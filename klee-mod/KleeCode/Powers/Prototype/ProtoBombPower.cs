using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE OVERHAUL'S BOMB (rules 1, 2, 3 and 6 of the ruled brief's sec.3).
///
/// A numbered charge on an enemy that GROWS by
/// <see cref="KleeOverhaulLaw.BombGrowth"/> at the start of Klee's turn and
/// NEVER goes off by itself. Only a card that says <i>Set off</i> pops one, and
/// when it does, every Bomb on the target goes off ONE AT A TIME, each a Pyro
/// hit for its own size, BEFORE the rest of the card resolves. A Bomb whose
/// enemy dies JUMPS to a random living enemy at its current size. A MINE is a
/// Bomb that ALSO goes off when its enemy attacks a player, before the hit
/// lands (any player since 2026-09-25: see <see cref="BeforeDamageReceived"/>).
///
/// WHY THIS IS A SEPARATE POWER AND NOT A MODE ON <see cref="BombPower"/>.
/// Rule 7 is "nothing fires by itself", and the shipped Bomb's whole lifecycle
/// is two automatic detonations -- <c>BeforeSideTurnStart</c> and the
/// early pop in <c>AfterDamageReceived</c>. Teaching one type to be both would
/// put a runtime branch inside every one of those hooks, in the file whose
/// per-placer instancing, suppression arbiter and death-teardown compensation
/// are the mod's most load-bearing co-op work. A second power costs one type and
/// buys the acceptance condition outright: under the flag no card places a
/// <see cref="BombPower"/>, so "no automatic detonation of any kind" is a
/// property of what is on the board rather than of a branch somebody remembers.
/// The shipped Bomb is not edited by this arm in any build.
///
/// WHAT IS INHERITED FROM THE SHIPPED BOMB, DELIBERATELY, because these are its
/// decisions and not this arm's to re-take:
///   * <see cref="PowerInstanceType.InstancedPerApplier"/> -- R205, one pile
///     per placer, so two Klees never spend each other's charges or credit;
///   * <see cref="DeepCloneFields"/> -- <c>AbstractModel.MutableClone</c> is a
///     shallow <c>MemberwiseClone</c>, so an un-cloned list is a silent
///     cross-enemy corruption bug rather than a crash;
///   * TAKE-THEN-RESOLVE -- charges leave the power before any damage lands, so
///     a kill mid-payload can neither re-enter the pile nor lose what is owed
///     (EB-138), which is also exactly what rule 3's jump needs;
///   * <see cref="PowerType.Buff"/> -- Artifact coexists with an application
///     rather than eating it ([USER] 2026-08-23).
///
/// WHAT IS NOT INHERITED: the shipped Bomb's "first attack while Bombed deals
/// 25% less" suppression. It is not in the brief's seven rules, so under rule 7
/// it is not a rule -- it would be a card.
///
/// A BOMB CARRIES THE TARGET'S MODIFIERS ONLY (`EB-343`, ruled R248). A charge
/// is planted at its PRINTED size and nothing of Klee's changes it -- a printed
/// 6 is a Bomb 6 under minus 5 Strength and under Weak alike -- and what it
/// pays when it goes off is that size through the ENEMY's own terms: Vulnerable
/// and the enemy's per-hit cap. Weak has no target-side reading at all, because
/// the game's <c>WeakPower</c> reduces what its OWNER deals and never what its
/// owner takes.
///
/// WHY THE RULE MOVED. The badge is priced off the pile, so every dealer term
/// in the pipeline showed up on an enemy-side number that a player reads as
/// incoming damage: [USER] planted three Bombs of printed 6, 4 and 4 into
/// Tender's minus 5 Strength and read `Bomb -1`, and a Weak on Klee shrank a
/// banked stack at the badge without a card saying so. A charge already sitting
/// on an enemy is not a swing Klee is taking, and pricing it as one made the
/// character's central number unreadable in exactly the fights that are hard.
/// The badge's number folds the target's terms in; since the text pass of
/// 2026-09-25 the face names only the pending reaction beside it
/// (<see cref="Localization"/>), and the number is the whole of the rest.
/// </summary>
public sealed partial class ProtoBombPower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for any model implementing this
    /// interface, so the loc lives here and cannot drift from the id.
    ///
    /// THE BADGE IS THE WHOLE UI (slice packet sec.5, last bullet): the number
    /// under the enemy is what a Set off here would deal, and the fuse mark is
    /// the Mine count in the smart tooltip. Nothing new is drawn -- this is the
    /// same <c>DisplayAmount</c> + <c>DynamicVar</c> rendering the shipped Bomb
    /// already uses, which is what "reuse the existing badge" means here.
    /// <c>EB-270</c>: the badge and the <c>{Size}</c> below are ONE number,
    /// because two numbers on one pile is one too many -- see
    /// <see cref="DisplayAmount"/>.
    /// </summary>
    public List<(string, string)>? Localization
    {
        get
        {
            var rows = new List<(string, string)>
            {
                ("title", "Bomb"),
                // `EB-417`. THE BADGE'S OTHER NAME, and it is a row rather
                // than a conditional inside the one above for
                // <see cref="SmartDescriptionLocKey"/>'s reason: loc is
                // registered once at boot and the pile changes every turn, so
                // the LIVE choice is a key (<see cref="Title"/>) and both
                // spellings have to exist before it can be made.
                (MineTitleKey, "Mine"),
                // TEXT PASS 2026-09-25 (the owner: "the existing text is
                // often very verbose and unintuitive"). The static face is
                // what a reward shelf or the compendium shows, with no pile to
                // quote: what the Bombs are and the two rules a reader needs
                // first. The Bomb and Mine keyword tips carry the rest.
                ("description",
                    "Klee's Bombs. They deal their size in [gold]Pyro[/gold] "
                  + "damage when [gold]Set off[/gold] and grow at the start of "
                  + "her turn."),
            };
            // THE LIVE GRID. Rows and a key, not conditionals inside one row,
            // because loc is registered once at boot and a headless pin can
            // read a row and cannot run `LocManager`. Every key the selector
            // can compose has a row, because both walk the same four axes.
            foreach (var sparks in new[] { false, true })
            {
                foreach (var mines in new[] { false, true })
                {
                    foreach (var rider in new[] { false, true })
                    {
                        foreach (var reaction in new[] { ReactionKind.None,
                                     ReactionKind.Vaporize, ReactionKind.Melt })
                        {
                            rows.Add((SmartKey(sparks, mines, rider, reaction),
                                      Face(sparks, mines, rider, reaction)));
                        }
                    }
                }
            }
            return rows;
        }
    }

    /// <summary>
    /// The face the wire prints (<c>PowerModel.HoverTips</c> uses the SMART
    /// description for any mutable power that has one). At most three short
    /// sentences (text pass 2026-09-25): what a Set off here pays, the pile in
    /// set-off order, and the rider if one is riding.
    ///
    /// <c>{Size}</c> is the number the Set off will actually deal -- the
    /// target's Vulnerable, its HP cap and the pending reaction are already
    /// folded in (<see cref="PredictedSetOffDamage"/>), so the face names the
    /// reaction and nothing else. The growth, the jump and the Mine's timing
    /// are the keyword tips' (<c>ArmKeywordTips.ForBomb</c> and
    /// <c>ForMine</c>), and the old clauses for them left this face.
    ///
    /// EVERY PIECE IS A NAMED CONSTANT, because
    /// `tools/lint_text_conventions.py` reads the player's text off the
    /// SOURCE and rebuilds these faces from these names.
    /// </summary>
    private static string Face(bool sparks, bool mines, bool rider,
                              ReactionKind reaction) =>
        "[gold]Set off[/gold] here deals " + PyroTotal
      + ReactionClause(reaction)
      + (sparks ? SparksClause : string.Empty) + "."
      + Bombs + (mines ? MinesClause : string.Empty) + "."
      + (rider ? RiderSentence : string.Empty);

    /// <summary>The total, with no full stop: a reaction clause may follow.</summary>
    private const string PyroTotal = "[blue]{Size}[/blue] [gold]Pyro[/gold] damage";

    /// <summary>`EB-721`. The one term folded into the total that a reader
    /// cannot check against a badge on the enemy: the amplifying reaction the
    /// leading charge will cause. Pyro amplifies over Hydro and over Cryo and
    /// nothing else, so these are the only two.</summary>
    private const string VaporizeClause = " with [gold]Vaporize[/gold]";

    /// <summary>`EB-721`, the other amplifier.</summary>
    private const string MeltClause = " with [gold]Melt[/gold]";

    private static string ReactionClause(ReactionKind reaction) => reaction switch
    {
        ReactionKind.Vaporize => VaporizeClause,
        ReactionKind.Melt => MeltClause,
        _ => string.Empty,
    };

    /// <summary>`EB-514` / `EB-666`: what a Set off here MAKES, in Sparks --
    /// one per explosion, from Klee's starter relic
    /// (<see cref="SparksOnSetOff"/>). Printed only when it is more than
    /// none.</summary>
    private const string SparksClause =
        " and gives [blue]{Sparks}[/blue] [gold]Spark{Sparks:plural:|s}[/gold]";

    /// <summary>`EB-450` / `EB-536` / `EB-755`: the pile, in the order it
    /// goes off, each charge under its ordinal (<see cref="ChargeListVar"/>).
    /// </summary>
    private const string Bombs = " Bombs here, oldest first: [blue]{Charges}[/blue]";

    /// <summary>`EB-260`: how many of the pile are Mines, where any are.</summary>
    private const string MinesClause =
        ", including [blue]{Mines}[/blue] [gold]Mine{Mines:plural:|s}[/gold]";

    /// <summary>`EB-573`: the rider a merge keeps (Jumpy Dumpty's
    /// Mine-on-ALL), named where the pile is.</summary>
    private const string RiderSentence =
        " One drops [gold]Mine[/gold] [blue]{Payload}[/blue] on ALL enemies "
      + "when it goes off.";

    /// <summary>The row key <see cref="Face"/> is filed under, and the ONE
    /// place the axes are spelled into a key -- <see cref="Localization"/>
    /// writes the rows with it and <see cref="SmartDescriptionLocKey"/> reads
    /// one back, so a row and its selector cannot drift apart.</summary>
    private static string SmartKey(bool sparks, bool mines, bool rider,
                                  ReactionKind reaction) =>
        "smartDescription" + (sparks ? "Sparks" : string.Empty)
      + (mines ? "Mines" : string.Empty)
      + (rider ? "Rider" : string.Empty)
      + reaction switch
        {
            ReactionKind.Vaporize => "Vaporize",
            ReactionKind.Melt => "Melt",
            _ => string.Empty,
        };

    /// <summary>
    /// The selector. <c>PowerModel.SmartDescription</c> resolves this key on
    /// EVERY read of <c>HoverTips</c>, so the face follows the pile and the
    /// enemy under it.
    /// </summary>
    protected override string SmartDescriptionLocKey =>
        Id.Entry + "."
      + SmartKey(SparksOnSetOff() > 0, MineCount > 0, PayloadTotal > 0,
                 LiveReaction);

    /// <summary>The loc suffix <see cref="Title"/> selects when the pile is all
    /// Mines. `title` is the base game's own suffix and BaseLib registers every
    /// pair this model returns under `{Id.Entry}.{key}`, so a second name costs
    /// a row and nothing else.</summary>
    private const string MineTitleKey = "titleMine";

    /// <summary>The table a power's loc lives in, and the one
    /// <c>KleeSelfCheck</c> R8 walks.</summary>
    private const string PowersTable = "powers";

    /// <summary>
    /// `EB-417`. A MINE READS AS A MINE.
    ///
    /// THE DEFECT. The badge titled every pile `Bomb`, so a lone Mine under an
    /// enemy read `Bomb 4` and the one property the whole Mine trick turns on
    /// -- that it goes off BEFORE the enemy's hit lands -- was three lines down
    /// in the body text. The r11 Opus seat found the rule on Jumpy Dumpty's
    /// face instead and said so: "the enemy badge calls a Mine `Bomb 4` in the
    /// title and only discloses it is a Mine in the body text... Since the
    /// whole Mine trick is timing, the badge should lead with it."
    ///
    /// ALL OF THEM OR NONE, which is the honest test and not a cautious one. A
    /// pile is one badge and one number; naming it `Mine` while a plain Bomb
    /// sits in it would print a timing rule over a charge that does not have
    /// one. A MIXED pile keeps `Bomb` and discloses its Mines where it always
    /// has -- <see cref="MinesClause"/>'s "including {Mines} Mines", the
    /// fuse mark -- and the Mine count rides beside it either way, because
    /// <see cref="SmartDescriptionLocKey"/> switches on <c>MineCount > 0</c>
    /// and not on this.
    ///
    /// A CANONICAL COPY HAS NO CHARGES and therefore no Mines, so the
    /// compendium entry is titled `Bomb` exactly as it was: the guard is
    /// <c>MineCount > 0</c>, not <c>MineCount == _charges.Count</c> alone,
    /// which an empty pile satisfies vacuously.
    /// </summary>
    public override LocString Title =>
        TitledAsMine
            ? new LocString(PowersTable, Id.Entry + "." + MineTitleKey)
            : base.Title;

    /// <summary>Is this pile a Mine and nothing but? The decision
    /// <see cref="Title"/> makes, exposed for the pins the way the pure reads
    /// below are: a <c>LocString</c> cannot be resolved outside a booted game
    /// (KleeTests README, "The headless boundary"), so the branch has to be
    /// readable without formatting one.</summary>
    public bool TitledAsMine => MineCount > 0 && MineCount == _charges.Count;

    /// <summary>
    /// `EB-721`. The amplifying reaction the FIRST charge will cause, read off
    /// the target's aura alone -- the term <see cref="PredictedSetOffDamage"/>
    /// folds into <c>{Size}</c>. An empty pile or a canonical (compendium)
    /// copy answers none: <see cref="PowerModel.Owner"/>'s getter asserts
    /// mutability, and <c>HasSmartDescription</c> reads the key before the
    /// mutability check that gates the smart face.
    /// </summary>
    private ReactionKind LiveReaction
    {
        get
        {
            if (_charges.Count == 0 || !IsMutable) return ReactionKind.None;
            var target = Owner;
            if (target == null) return ReactionKind.None;
            return AuraCmd.Find(target)?.Element switch
            {
                Elements.Element.Hydro => ReactionKind.Vaporize,
                Elements.Element.Cryo => ReactionKind.Melt,
                _ => ReactionKind.None,
            };
        }
    }

    /// <summary>
    /// What a Set off here gives in Sparks: one per explosion
    /// (<see cref="KleeOverhaulLaw.SparkPerExplosion"/>) for each relic of the
    /// placer's that pays per explosion -- Pounding Surprise, or Dodoco Tales
    /// once Touch of Orobas has upgraded it. PURE, and 0 on a canonical copy,
    /// an empty pile, or a pile whose placer holds neither relic (a Companion
    /// card can plant one for another character), which is exactly when the
    /// face should say nothing about Sparks. `EB-666`: the face says "gives",
    /// never "for", because "for N" reads as a price.
    /// </summary>
    public int SparksOnSetOff()
    {
        if (_charges.Count == 0 || !IsMutable || !KleeOverhaul.Enabled) return 0;
        var player = Applier?.Player;
        if (player == null) return 0;
        var payers = player.Relics.Count(
            r => r is global::KleeMod.Relics.PoundingSurprise
                 or global::KleeMod.Relics.ExplosiveFrags);
        return _charges.Count * KleeOverhaulLaw.SparkPerExplosion * payers;
    }

    /// <summary>The amplifying reaction the leading charge will cause, or
    /// none. `EB-721`; see <see cref="VaporizeClause"/> for why the list is
    /// two long.</summary>
    private enum ReactionKind { None, Vaporize, Melt }

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: charges are spent by going off, not ticked by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>R205's ruling, inherited unchanged: one pile per placer.</summary>
    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

    /// <summary>
    /// ONE live charge.
    ///
    /// <c>Size</c> is rule 1's number -- what it grows and what it deals.
    /// <c>IsMine</c> is rule 6's flag, and it is a flag on a Bomb rather than a
    /// second power because the brief says so in as many words ("A Mine is a
    /// Bomb that ALSO goes off when...") and because Mines have to grow, merge
    /// and jump exactly like Bombs.
    /// <c>PayloadMineAll</c> is the Bomb payload the build list names: Jumpy
    /// Dumpty's charge, when it goes off, puts a Mine of this size on every
    /// enemy. 0 is "no payload", which is every other charge in the slice.
    /// </summary>
    public readonly record struct ProtoCharge(int Size, bool IsMine, int PayloadMineAll);

    /// <summary>Charges in placement order. MUST be deep-cloned: see
    /// <see cref="DeepCloneFields"/>.</summary>
    private List<ProtoCharge> _charges = new();

    protected override void DeepCloneFields()
    {
        base.DeepCloneFields();
        _charges = new List<ProtoCharge>(_charges);
    }

    // ---- the pure reads -----------------------------------------------

    /// <summary>Total size on this pile: what a Set off will deal here.</summary>
    public int TotalSize => _charges.Sum(c => c.Size);

    /// <summary>The single largest charge on this pile. `TotalSize`'s twin:
    /// the raw SUM every other rule inside the arm is priced in (growth,
    /// jumps, Sorry Jean's Block, a Set off) survives beside it
    /// untouched.</summary>
    public int LargestSize => _charges.Count == 0 ? 0 : _charges.Max(c => c.Size);

    /// <summary>How many of this pile's charges are Mines -- the fuse mark.</summary>
    public int MineCount => _charges.Count(c => c.IsMine);

    /// <summary>`EB-573`. The riders this pile is carrying, summed -- the same
    /// sum <see cref="MergeAllTo"/> builds and <see cref="Explode"/> pays out,
    /// so the badge's number and the board's are one read.</summary>
    public int PayloadTotal => _charges.Sum(c => c.PayloadMineAll);

    /// <summary>The charges, for the pins. Never handed out to a mutator.
    ///
    /// PUBLIC, like the pure mutators below and for the reason
    /// <c>Diagnostics.MeterLedger</c> gives one file over: KleeTests is a
    /// separate assembly, the arithmetic here is what every rule in the arm
    /// rests on, and the alternative was an <c>InternalsVisibleTo</c> nothing
    /// else in this mod needs or an IL-shape assertion standing in for the
    /// arithmetic itself.</summary>
    public IReadOnlyList<ProtoCharge> Charges => _charges;

    /// <summary>
    /// THE BADGE, AND IT IS THE SAME NUMBER THE TOOLTIP PRINTS -- <c>EB-270</c>.
    ///
    /// The badge shows an AMOUNT, not the count -- the shipped Bomb's ruling
    /// (2026-07-20), for its own reason: an enemy-side number reads as incoming
    /// damage, and a count hides what growing did. That much is unchanged. What
    /// changed is WHICH amount.
    ///
    /// It used to be <see cref="TotalSize"/>, the raw sum of the charges, while
    /// the face beside it printed <see cref="PredictedSetOffDamage"/> -- so
    /// under Weak the pile read "Bomb 17" in bold with "a Set off here deals 12
    /// Pyro damage in total, after Weak" underneath. The r2 Opus seat read the
    /// bold 17 first and called it "the wrong one", and the r3 Codex seat had
    /// to reason its way from one to the other. Two numbers on one pile is one
    /// number too many, and the survivor has to be the one the Set off actually
    /// PAYS.
    ///
    /// `EB-343` narrowed WHAT CAN MOVE IT rather than which number is shown:
    /// under R248 the two agree on an unmodified board and part company only
    /// over the ENEMY's Vulnerable and cap, never over anything of Klee's. The
    /// [USER]-reported board this closes is Tender's minus 5 Strength turning
    /// three Bombs of printed 6, 4 and 4 into a badge that read `Bomb -1`.
    ///
    /// So the badge, the tooltip's <c>{Size}</c> and Big Badda Boom's bonus
    /// line now all come off the same arithmetic: this getter and
    /// <c>SetOffDamageVar</c> both call <see cref="PredictedSetOffDamage"/>,
    /// and the ledger the bonus line reads is fed the number
    /// <c>ElementalHit.Deal</c> returned. <see cref="TotalSize"/> survives as
    /// the raw sum every rule inside the arm is priced in (growth, jumps, Sorry
    /// Jean's Block); it is simply not a number the player is shown any more.
    ///
    /// A canonical (compendium) copy has no owner, and
    /// <see cref="PredictedSetOffDamage"/> answers <see cref="TotalSize"/> for
    /// one -- so the compendium badge is unchanged by this.
    /// </summary>
    public override int DisplayAmount => PredictedSetOffDamage();

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[]
        {
            new SetOffDamageVar(),
            new DynamicVar("Mines", 0m),
            // `EB-289`: the live charge count. See `Bombs` above for why the
            // stack amount could not be it.
            new DynamicVar("Count", 0m),
            // `EB-450`: the charges themselves, oldest first.
            new ChargeListVar(),
            // `EB-573`: the rider the merge keeps, summed over the pile.
            new DynamicVar("Payload", 0m),
            // Text pass 2026-09-25: the Sparks a Set off here gives, read
            // live like `{Size}` (a relic can change under a pile that has
            // not moved).
            new SparksVar(),
        };

    /// <summary><c>{Sparks}</c>, read live off <see cref="SparksOnSetOff"/>
    /// at format time, the <see cref="SetOffDamageVar"/> construction.</summary>
    private sealed class SparksVar : DynamicVar
    {
        public SparksVar() : base("Sparks", 0m)
        {
        }

        private int Live =>
            (_owner as ProtoBombPower)?.SparksOnSetOff() ?? (int)BaseValue;

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// <c>{Charges}</c>, the pile's sizes in the order they will go off
    /// (`EB-450`), EACH UNDER ITS ORDINAL (`EB-755`).
    ///
    /// `EB-755`. "OLDEST FIRST" DOES NOT SAY WHICH OF TWO IS OLDER. The clause
    /// states the RULE and the list states the ORDER, and for two Bombs placed
    /// in the SAME turn a reader has no way to join the two: nothing on the
    /// board says which of them the game filed first, and only the leading
    /// charge takes the aura (`PredictedSetOffDamage`), so a seat planning a
    /// Vaporize could not tell which size the multiplier would ride. The D
    /// default is taken: print them in SET-OFF ORDER WITH ORDINALS, so the list
    /// names its own positions instead of leaving them to be counted.
    ///
    /// ONLY WHERE THERE ARE TWO OR MORE. A lone charge has no order to
    /// disambiguate and `1st 12` on a single Bomb is a numeral a reader has to
    /// discard -- the same argument `EB-536` made for the hit clause, which is
    /// a fact about a STACK and reads as noise on one Bomb.
    ///
    /// AND THE ORDINALS RIDE THE VALUE, not the face. The face constants are
    /// at their measured ceilings (<see cref="Bombs"/> is 125 of 125) and
    /// `tools/lint_text_conventions.py` measures the SOURCE, so a word added
    /// to the format string would cost the sentence a clause. This is the same
    /// live var the sizes already arrive through.
    ///
    /// A <see cref="SetOffDamageVar"/> SUBCLASSED THE SAME WAY AND FOR THE
    /// SAME REASON: the game hands the var itself to SmartFormat
    /// (<c>LocString.Add(DynamicVar)</c>) and formats it through
    /// <c>ToString()</c>, so a var can answer with something that is not one
    /// number -- and this one has to, because the whole finding is that ONE
    /// number was all the badge could say. Read LIVE off <c>_charges</c>, like
    /// every other figure on this face.
    ///
    /// <c>GetBaseValueForIConvertible</c> answers the COUNT, which is what a
    /// numeric formatter would have to be given if anybody ever wrote
    /// <c>{Charges:plural:|s}</c>; nothing does today, and answering the sum
    /// there would be a second name for <c>{Size}</c>.
    /// </summary>
    private sealed class ChargeListVar : DynamicVar
    {
        public ChargeListVar() : base("Charges", 0m)
        {
        }

        private ProtoBombPower? Pile => _owner as ProtoBombPower;

        protected override decimal GetBaseValueForIConvertible() =>
            Pile?._charges.Count ?? BaseValue;

        public override string ToString()
        {
            var pile = Pile;
            if (pile == null || pile._charges.Count == 0)
            {
                return "0";
            }

            var sizes = pile._charges.Select(
                c => c.Size.ToString(
                    System.Globalization.CultureInfo.InvariantCulture));
            if (pile._charges.Count == 1)
            {
                return string.Join(" / ", sizes);
            }

            return string.Join(" / ", sizes.Select(
                (size, index) => Ordinal(index + 1) + " " + size));
        }

        /// <summary>`1st`, `2nd`, `3rd`, `4th` ... -- the position of one
        /// charge in the set-off order (`EB-755`).
        ///
        /// The teens are the exception every ordinal table carries (11th,
        /// 12th, 13th, not 11st), and a pile CAN reach them: the r21 seat's
        /// merged stack was nine charges and Jumpy Dumpty's rider adds one per
        /// enemy per detonation.</summary>
        private static string Ordinal(int position)
        {
            var suffix = (position % 100) is >= 11 and <= 13
                ? "th"
                : (position % 10) switch
                {
                    1 => "st",
                    2 => "nd",
                    3 => "rd",
                    _ => "th",
                };
            return position.ToString(
                System.Globalization.CultureInfo.InvariantCulture) + suffix;
        }
    }

    /// <summary>
    /// <c>{Size}</c>, READ LIVE. <c>EB-265</c>.
    ///
    /// A plain <see cref="DynamicVar"/> is a stored number, written by
    /// <see cref="SyncDisplay"/> when the pile changes -- and a modifier does
    /// not change the pile. So an enemy that gained Vulnerable after the Bombs
    /// were planted would show a face that was right when it was written and
    /// wrong when it was read, which is the same defect one turn later. (Before
    /// <c>EB-343</c> the stale term was Klee's own Strength; the rule moved,
    /// the staleness problem did not.) This subclass
    /// asks the pile at FORMAT time instead: the game hands the var itself to
    /// SmartFormat (<c>LocString.Add(DynamicVar)</c>) and formats it through
    /// <c>ToString()</c>, converting through <c>IConvertible</c> only for the
    /// numeric formatters, so both are overridden and both answer the same
    /// number.
    ///
    /// The stored <c>BaseValue</c> is kept in step by <see cref="SyncDisplay"/>
    /// as the fallback, which is what a canonical (compendium) copy with no
    /// owner reads.
    /// </summary>
    private sealed class SetOffDamageVar : DynamicVar
    {
        public SetOffDamageVar() : base("Size", 0m)
        {
        }

        private int Live =>
            (_owner as ProtoBombPower)?.PredictedSetOffDamage() ?? (int)BaseValue;

        protected override decimal GetBaseValueForIConvertible() => Live;

        public override string ToString() =>
            Live.ToString(System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// WHAT A SET OFF HERE ACTUALLY DEALS, right now -- <c>EB-265</c>, and the
    /// arithmetic R248 re-ruled at <c>EB-343</c>.
    ///
    /// The face used to print <see cref="TotalSize"/>, the raw sum of the
    /// charges, while <see cref="Explode"/> sent every charge through a
    /// pipeline that moved it. With Strength 2 and two Bombs the face printed
    /// 10 and the set-off dealt 14, and the blind tester called it "the one
    /// number I learned not to trust" (`klee-overhaul-r1-opus`, fight 2). The
    /// answer then was to put the dealer's terms ON the face; R248's answer is
    /// to take them out of the RULE, and this number follows the rule.
    ///
    /// THE TARGET'S TERMS AND NOTHING OF KLEE'S. A Bomb is the enemy's burden:
    /// a printed 6 is a Bomb 6 whatever Klee's Strength and Weak are doing, and
    /// what a Set off pays is that size through the enemy's own Vulnerable and
    /// the enemy's own per-hit cap.
    ///
    /// SHARED, NOT RE-DERIVED: <c>SimDamagePipeline.ResolveOnTarget</c> is the
    /// same target-mods / one-truncation / cap chain the explosion takes --
    /// <c>ElementalHit.Deal</c> with <c>applyDealerMods: false</c>, then
    /// <c>CreatureCmd.Damage</c>'s own Cap phase -- called once per charge
    /// exactly as the explosion loop does, so per-charge truncation and the
    /// per-HIT cap are the pipeline's rather than a second copy of them here.
    ///
    /// THE PENDING REACTION IS FOLDED IN SINCE `EB-559`, and the clause that
    /// used to leave it out had the argument backwards. "With a Hydro aura up
    /// and Bomb 25 on the body it still printed 'Set off here deals 25 Pyro
    /// damage'; the real number was 39. I had to compute the Vaporize myself,
    /// and in fight 5 the difference between those two numbers was the
    /// difference between lethal and dying two short" (Klee r20 lane 2, (c) 2).
    ///
    /// "THERE IS NO ONE MULTIPLIER FOR THE PILE" IS TRUE AND IS NOT AN OBSTACLE:
    /// the FIRST charge is the one that meets the aura -- `EB-432`'s rule, which
    /// this file already prints on the `Set off` tip -- and every charge behind
    /// it lands into a bare body because the reaction consumed the aura. So the
    /// amplifier is a property of ONE charge, applied to the one the walk takes
    /// first, and the rest resolve at 1 exactly as they did. One multiplier for
    /// the PILE would have been wrong; one for the first charge is the board.
    ///
    /// PYRO, WHICH IS THE ELEMENT THE FACE PRINTS. The explosion asks
    /// <c>CompanionCovenBombs.ElementFor</c>, which is an async command call a
    /// tooltip may not make and which answers Pyro on every board but one --
    /// Prune's Hexhunter Chime, for ONE explosion, under the companion arm. A
    /// preview that is right on every other board and behind by one Chime is
    /// the trade; the face's own "Pyro damage" makes the same claim already.
    ///
    /// THE DEALER IS CONSULTED FOR THIS ONE TERM AND R248 IS NOT BREACHED.
    /// "Nothing of Klee's" is about her Strength and her Weak, which move a hit
    /// she deals and never a charge sitting on an enemy. The amplifier is not
    /// one of those: <c>ElementalHit.Deal</c> reads Vermillion Pact's boost off
    /// the APPLIER when the explosion lands, so a preview that ignored it would
    /// be predicting a number the board does not pay.
    ///
    /// ONE TERM IS STILL LEFT OUT, and it is one-shot rather than standing
    /// state: The Big One's DOUBLING, because reading it means
    /// <c>KleeOverhaulLedger.For</c>, which rolls per-turn counters, and a face
    /// is read on every state poll -- a tooltip may not have side effects.
    /// </summary>
    public int PredictedSetOffDamage()
    {
        if (_charges.Count == 0) return 0;
        // A canonical (compendium) copy has no owner and its getter asserts;
        // the stored BaseValue is what such a copy prints.
        if (!IsMutable) return TotalSize;
        var target = Owner;
        if (target == null) return TotalSize;

        var total = 0;
        // `EB-559`: the first charge through the funnel is the one that meets
        // the aura (`EB-432`, and `_charges` is placement order), so the
        // amplifier rides it and every charge behind it lands into a bare body.
        var amplifier = PendingReactionMultiplier(target);
        foreach (var charge in _charges)
        {
            total += SimDamagePipeline.ResolveOnTarget(
                target, charge.Size, amplifier);
            amplifier = 1m;
        }
        return total;
    }

    /// <summary>
    /// `EB-559`. What the FIRST explosion's reaction multiplies its charge by,
    /// or 1 where the target is bare, is already wearing Pyro, or wears an
    /// element Pyro does not amplify.
    ///
    /// PURE, which is the whole reason it is a method of its own: this is read
    /// on every state poll through <see cref="DisplayAmount"/> and
    /// <c>SetOffDamageVar</c>, so it may touch no command and roll no counter.
    /// <c>AuraCmd.Find</c>, <c>ReactionTable.Lookup</c> and
    /// <c>ReactionTable.AmplifierMultiplier</c> are all reads.
    /// </summary>
    private decimal PendingReactionMultiplier(Creature target)
    {
        var aura = AuraCmd.Find(target);
        if (aura == null || aura.Element == Elements.Element.Pyro) return 1m;
        var reaction = ReactionTable.Lookup(aura.Element,
                                            Elements.Element.Pyro);
        return ReactionTable.AmplifierMultiplier(reaction, Applier);
    }

    /// <summary>Called after EVERY mutation of <see cref="_charges"/>. The badge
    /// and the tooltip both derive from the list the explosions consume, so the
    /// number shown can never diverge from the number that will land.</summary>
    private void SyncDisplay()
    {
        var size = DynamicVars["Size"];
        size.BaseValue = PredictedSetOffDamage();
        size.ResetToBase();
        var mines = DynamicVars["Mines"];
        mines.BaseValue = MineCount;
        mines.ResetToBase();
        var count = DynamicVars["Count"];
        count.BaseValue = _charges.Count;
        count.ResetToBase();
        // `EB-573`: the rider total, kept in step with the list like the rest.
        var payload = DynamicVars["Payload"];
        payload.BaseValue = PayloadTotal;
        payload.ResetToBase();
        InvokeDisplayAmountChanged();
    }

    // ---- the pure mutations (no commands, nothing that can kill) -------

    /// <summary>Rule 1's growth, applied to this pile. PURE.</summary>
    public void GrowBy(int amount)
    {
        if (amount == 0 || _charges.Count == 0) return;
        for (var i = 0; i < _charges.Count; i++)
        {
            _charges[i] = _charges[i] with { Size = _charges[i].Size + amount };
        }
        SyncDisplay();
    }

    /// <summary>
    /// Grow the single largest charge ON THIS PILE by <paramref name="amount"/>,
    /// and report which index took it (-1 if the pile is empty). PURE.
    ///
    /// <see cref="GrowBy"/>'s one-charge twin, and the board-wide walk in
    /// <see cref="GrowLargestPerSpark"/> is what turns "largest here" into
    /// "largest anywhere". THE FIRST largest wins a tie, in place order, which
    /// is the tie-break <see cref="RemoveLargestForBlock"/> already takes: a
    /// card whose payout lands on a coin flip is one the player cannot plan
    /// around. Sim twin: <c>klee_overhaul.grow_largest_per_spark</c>'s inner
    /// walk.
    /// </summary>
    public int GrowLargestChargeBy(int amount)
    {
        if (_charges.Count == 0) return -1;
        var best = 0;
        for (var i = 1; i < _charges.Count; i++)
        {
            if (_charges[i].Size > _charges[best].Size) best = i;
        }
        if (amount == 0) return best;
        _charges[best] = _charges[best] with
        {
            Size = _charges[best].Size + amount,
        };
        SyncDisplay();
        return best;
    }

    /// <summary>Add one charge. PURE -- the APPLY that creates the pile is the
    /// caller's.</summary>
    /// <summary>Every charge here becomes a Mine (R276, Hair Trigger).</summary>
    public void MakeAllMines()
    {
        if (_charges.Count == 0) return;
        for (var i = 0; i < _charges.Count; i++)
        {
            _charges[i] = _charges[i] with { IsMine = true };
        }
        SyncDisplay();
    }

    public void AddCharge(ProtoCharge charge)
    {
        _charges.Add(charge);
        SyncDisplay();
    }

    /// <summary>
    /// Empty this pile and hand back what it carried, null if it was already
    /// empty. PURE, and that is the point: the charges are off the power before
    /// anything that can kill runs, so a kill mid-payload cannot re-enter the
    /// pile (the shipped Bomb's EB-138 discipline, and rule 3's jump needs the
    /// same guarantee for the same reason).
    /// </summary>
    public List<ProtoCharge>? TakeAll()
    {
        if (_charges.Count == 0) return null;
        var taken = new List<ProtoCharge>(_charges);
        _charges.Clear();
        SyncDisplay();
        return taken;
    }

    /// <summary>Empty only the MINES, leaving plain Bombs where they are.
    /// Rule 6: an attack on a player pops the Mines and nothing else.
    /// PURE.</summary>
    public List<ProtoCharge>? TakeMines()
    {
        var mines = _charges.Where(c => c.IsMine).ToList();
        if (mines.Count == 0) return null;
        _charges.RemoveAll(c => c.IsMine);
        SyncDisplay();
        return mines;
    }

    /// <summary>The index of this pile's single largest charge, the OLDEST
    /// (first in placement order) on a tie, or -1 on an empty pile. Pocket
    /// Match's pick (<see cref="SetOffLargest"/>); the same first-found
    /// tie-break <see cref="GrowLargestChargeBy"/> takes. PURE. Sim twin:
    /// <c>klee_overhaul.largest_index</c>.</summary>
    public int LargestIndex()
    {
        if (_charges.Count == 0) return -1;
        var best = 0;
        for (var i = 1; i < _charges.Count; i++)
        {
            if (_charges[i].Size > _charges[best].Size) best = i;
        }
        return best;
    }

    /// <summary>Remove ONE charge by index and hand it back. Sorry, Jean...'s
    /// primitive. PURE.</summary>
    public ProtoCharge? TakeAt(int index)
    {
        if (index < 0 || index >= _charges.Count) return null;
        var charge = _charges[index];
        _charges.RemoveAt(index);
        SyncDisplay();
        return charge;
    }

    /// <summary>
    /// Rule 1's growth NUMBER for one Klee, right now. PURE: the base
    /// <see cref="KleeOverhaulLaw.BombGrowth"/>, MULTIPLIED by
    /// <see cref="KleeOverhaulLaw.AliceMultiplier"/> while Alice's Recipe is up
    /// ("your Bombs grow twice each turn"). The brief's own gloss on Alice is
    /// "Breaks rule 1".
    /// </summary>
    public static int GrowthFor(Creature? klee)
    {
        if (klee == null) return KleeOverhaulLaw.BombGrowth;
        return klee.Powers.OfType<AlicesRecipePower>().Any()
            ? KleeOverhaulLaw.BombGrowth * KleeOverhaulLaw.AliceMultiplier
            : KleeOverhaulLaw.BombGrowth;
    }

    // ---- rule 1: growth at the start of Klee's turn ---------------------

    /// <summary>
    /// RULE 1's growth, and rule 7's whole point: this hook GROWS and does not
    /// detonate. The shipped Bomb's identical hook is what fires its start-of-
    /// turn payload; under this arm there is nothing to fire, because nothing
    /// fires by itself.
    ///
    /// <c>BeforeSideTurnStart</c> for the same reason the shipped Bomb uses it:
    /// it is the turn-start hook that carries a <c>PlayerChoiceContext</c>, and
    /// the corpse sweep below can place a Bomb.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;

        // Jumps first: a Bomb owed a jump is a Bomb that should GROW on its new
        // enemy this turn, not next. See SweepJumps for why a sweep exists.
        await SweepJumps(choiceContext, combatState);
        GrowBy(GrowthFor(Applier));
    }

    // ---- rule 2: Set off, and the four card-facing spellings of it -------

    /// <summary>
    /// "Set off. Deal N." on an AIMED card (Kaboom!, Ka-pow!, Big Badda Boom,
    /// The Big One, Bang Bang!, Quick Fuse, Sizzle, Perfect Timing).
    ///
    /// THE ORDER IS THE RULE: the Bombs go off first, one at a time, and the
    /// card's own damage lands after. That is rule 2's second half, and it is
    /// held HERE rather than by the order two emitted statements happen to sit
    /// in, so a card cannot get it wrong by being generated differently.
    /// <paramref name="damage"/> of 0 is a Set off with no Attack behind it.
    ///
    /// <c>EB-280</c>: <paramref name="damage"/> is a <c>decimal</c> because the
    /// generated card hands in <c>DynamicVars.Damage.BaseValue</c> -- the very
    /// var its face renders -- rather than a literal. The Strength and
    /// Vulnerable arithmetic still happens where it always did, inside
    /// <c>DamageCmd.Attack</c>; what changed is that the number entering that
    /// pipeline is now the printed one, so the face and the hit cannot drift.
    /// </summary>
    public static async Task SetOffAimed(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage)
    {
        // ONCE MORE!'s NOTE (`EB-732`), taken HERE and above every early
        // return below: "the last Set off card you played this combat" is a
        // fact about the CARD, so a Set off played into an empty board still
        // counts. The three card-facing entry points take it and
        // <see cref="SetOff"/> itself does not, because a Mine reaches that
        // one with no card at all. Sim twin: `klee_overhaul.note_set_off_card`
        // at the head of `effects._op_set_off`.
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        // BOOM BADGE (playtest 2026-09-24), spent beside the note and for its
        // reason: the doubling belongs to the next Set off CARD, so it is
        // taken once per entry point and handed to every pile it reaches.
        var badge = await BoomBadgePower.Spend(applier);
        if (target == null) return;
        await SetOff(choiceContext, target, applier, cardSource, badge: badge);
        await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
    }

    /// <summary>
    /// POCKET MATCH (playtest 2026-09-24): "Set off only your largest Bomb on
    /// the enemy. Deal N damage." <see cref="SetOffAimed"/> with ONE charge
    /// taken instead of the pile (<see cref="SetOffLargest"/>); the card's own
    /// hit lands after it, and the note and the Boom Badge are taken the same
    /// way, so it is a Set off card to every reader. Sim twin: the
    /// `charge: largest` arm of <c>effects._op_set_off</c>.
    /// </summary>
    public static async Task SetOffLargestAimed(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage)
    {
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        var badge = await BoomBadgePower.Spend(applier);
        if (target == null) return;
        await SetOffLargest(choiceContext, target, applier, cardSource, badge);
        await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
    }

    /// <summary>
    /// Pocket Match's rule: this placer's SINGLE LARGEST charge on
    /// <paramref name="target"/> -- the OLDEST on a tie -- leaves the pile and
    /// goes off; every other charge stays where it is and keeps growing.
    /// Returns 1 if a charge went off.
    ///
    /// THE SHAPE OF A MINE ANSWERING AN ATTACK (<see cref="BeforeDamageReceived"/>):
    /// a PURE take of part of the pile, then the one <see cref="Explode"/> every
    /// rule is priced in -- so it pays its Spark, answers Explosive Frags and
    /// Second Surprise if the charge was a Mine, and a kill leaves the charges
    /// behind it to <see cref="SweepJumps"/>. Unlike the Mine it is a card's Set
    /// off, so it SPENDS The Big One's multiplier (and Boom Badge's
    /// <paramref name="badge"/>, multiplied in) rather than peeking it.
    ///
    /// A charge aimed at a body that is already dead jumps instead, the rule
    /// <see cref="SetOff"/> keeps for a corpse. Sim twin:
    /// <c>klee_overhaul.set_off_largest</c>.
    /// </summary>
    public static async Task<int> SetOffLargest(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel? cardSource, int badge = 1)
    {
        if (target == null) return 0;

        ProtoBombPower? bestPile = null;
        var bestIndex = -1;
        var bestSize = 0;
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier != applier) continue;   // R205: your pile only
            var index = pile.LargestIndex();
            if (index < 0) continue;
            var size = pile._charges[index].Size;
            if (bestPile != null && size <= bestSize) continue;
            bestPile = pile;
            bestIndex = index;
            bestSize = size;
        }
        if (bestPile == null || bestPile.TakeAt(bestIndex) is not { } charge)
        {
            return 0;
        }
        if (bestPile._charges.Count == 0) await PowerCmd.Remove(bestPile);

        var multiplier = KleeOverhaulLedger.For(applier).TakeMultiplier() * badge;
        var exploded = 0;
        if (target.IsDead)
        {
            await JumpCharges(choiceContext, target, new[] { charge }, applier,
                              cardSource);
        }
        else
        {
            await Explode(choiceContext, target, charge, applier, cardSource,
                          multiplier);
            exploded = 1;
        }
        await SweepJumps(choiceContext, applier.CombatState);
        return exploded;
    }

    /// <summary>
    /// "Set off each enemy that has a non-Pyro aura" (Flame Dance), and the
    /// unfiltered all-enemies form beside it.
    ///
    /// The aura filter reads the board as it stands when the card resolves, so
    /// an enemy whose aura an earlier explosion in the same play consumed is
    /// no longer eligible -- which is what "each enemy that HAS" says.
    /// </summary>
    /// <summary>
    /// R276, BIG BOUNCE: the aimed Set off, with the explosions' damage past
    /// the target's HP summed and dealt as ONE plain Pyro hit to a random
    /// OTHER living enemy.
    ///
    /// THE BOUNCE IS NOT A SET OFF AND DOES NOT BOUNCE AGAIN: it is one
    /// <see cref="ElementalHit.Deal"/> with neither Klee's terms nor the
    /// destination's Vulnerable (both were settled at the source, where the
    /// overflow was measured). A Bomb that jumps off the dead target is rule
    /// 3's and untouched; the two do not overlap, because a jump moves a charge
    /// that did NOT go off. Sim twin: <c>klee_overhaul.bounce_overflow</c>.
    /// </summary>
    public static async Task SetOffAimedBouncing(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage)
    {
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        var badge = await BoomBadgePower.Spend(applier);
        if (target == null) return;
        var overflow = new List<int>();
        await SetOff(choiceContext, target, applier, cardSource, overflow, badge);
        await BounceOverflow(choiceContext, target, applier, overflow.Sum());
        await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
    }

    /// <summary>Big Bounce's second half: <paramref name="amount"/> as one
    /// plain Pyro hit on a random living enemy other than
    /// <paramref name="from"/>. Nothing to do with no overflow or no other
    /// enemy.</summary>
    public static async Task BounceOverflow(
        PlayerChoiceContext choiceContext, Creature from, Creature applier,
        int amount)
    {
        if (amount <= 0) return;
        var combat = applier.CombatState;
        if (combat == null) return;
        var candidates = combat.HittableEnemies
            .Where(e => e != from && !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (dest == null) return;
        KleeOverhaulLedger.For(applier).NoteLine(
            amount + " damage bounced to " + NameOf(dest));
        await ElementalHit.Deal(choiceContext, dest, Element.Pyro, amount,
                                applier, ignoreBlock: false, powered: false,
                                targetMods: false);
        await SweepJumps(choiceContext, combat);
    }

    public static async Task SetOffAll(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage,
        bool nonPyroAuraOnly)
    {
        // ONCE MORE!'s NOTE (`EB-732`), taken HERE and above every early
        // return below: "the last Set off card you played this combat" is a
        // fact about the CARD, so a Set off played into an empty board still
        // counts. The three card-facing entry points take it and
        // <see cref="SetOff"/> itself does not, because a Mine reaches that
        // one with no card at all. Sim twin: `klee_overhaul.note_set_off_card`
        // at the head of `effects._op_set_off`.
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        var badge = await BoomBadgePower.Spend(applier);
        var combat = applier.CombatState;
        if (combat == null) return;

        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            if (nonPyroAuraOnly)
            {
                var aura = AuraCmd.Find(enemy);
                if (aura == null || aura.Element == Element.Pyro) continue;
            }
            await SetOff(choiceContext, enemy, applier, cardSource, badge: badge);
            await DealCardDamage(choiceContext, enemy, damage, cardSource, cardPlay);
        }
    }

    /// <summary>
    /// "Set off and deal N, to a random enemy", <paramref name="times"/> times
    /// (Fwoosh!, Tinder Toss, Rapid Fire).
    ///
    /// RULE 2's LAST SENTENCE: "For random-target Attacks, per target hit." So
    /// the roll happens once per hit and each rolled enemy's Bombs go off
    /// before that hit lands -- four rolls is four Set offs, not one Set off
    /// and four hits. The candidates are re-read each time, so a hit that
    /// killed its target cannot be rolled again.
    ///
    /// `EB-516`, THE AIM (Klee r18, packet sec.4 item 2). The roll is drawn
    /// from the enemies CARRYING one of her charges, and falls back to every
    /// living enemy only when none does. Tinder Toss and Rapid Fire share one
    /// fault and one rule fixes both: a random Set off landing on a Bomb-less
    /// body breaks the arm's only economic loop -- a Spark-priced Set off into
    /// a bombed body costs nothing net -- and the r17 and r18 seats named those
    /// two rows the least-wanted cards in the pool. The NUMBERS are untouched:
    /// the same rolls, the same hits, a narrower bag to draw from. The bag is
    /// re-read per hit like the wider one, so a body whose last charge this hit
    /// spent is out of it for the next roll. Sim twin: the `random_enemy` arm
    /// of <c>effects._op_set_off</c>.
    /// </summary>
    public static async Task SetOffRandom(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage, int times)
    {
        // ONCE MORE!'s NOTE (`EB-732`), taken HERE and above every early
        // return below: "the last Set off card you played this combat" is a
        // fact about the CARD, so a Set off played into an empty board still
        // counts. The three card-facing entry points take it and
        // <see cref="SetOff"/> itself does not, because a Mine reaches that
        // one with no card at all. Sim twin: `klee_overhaul.note_set_off_card`
        // at the head of `effects._op_set_off`.
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        var badge = await BoomBadgePower.Spend(applier);
        var combat = applier.CombatState;
        if (combat == null) return;

        for (var i = 0; i < times; i++)
        {
            var living = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
            if (living.Count == 0) return;
            var candidates = BombedFirst(living, applier);
            var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target == null) return;

            await SetOff(choiceContext, target, applier, cardSource, badge: badge);
            await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
        }
    }

    /// <summary>
    /// `EB-516`'s BAG: the bodies a random Set off draws from. The enemies
    /// carrying one of <paramref name="applier"/>'s charges, or all of
    /// <paramref name="living"/> when none does.
    ///
    /// PURE, AND A NAMED METHOD FOR THAT REASON: the roll around it needs a
    /// live combat and cannot be reached headlessly, and this decision -- which
    /// is the whole of the rule -- can. Sim twin: the `bombed or living` line
    /// in <c>effects._op_set_off</c>.
    /// </summary>
    public static IReadOnlyList<Creature> BombedFirst(
        IReadOnlyList<Creature> living, Creature applier)
    {
        var bombed = living.Where(e => HoldsChargeFrom(e, applier)).ToList();
        return bombed.Count > 0 ? bombed : living;
    }

    /// <summary>The card's OWN hit, after its explosions. A powered Attack from
    /// Klee, so it applies Pyro through her cadence exactly as any other Attack
    /// of hers does; the explosions above went through the elemental pipeline
    /// directly, because they are not card damage.</summary>
    private static async Task DealCardDamage(
        PlayerChoiceContext choiceContext, Creature target, decimal damage,
        CardModel cardSource, CardPlay cardPlay)
    {
        if (damage <= 0 || target.IsDead) return;
        await DamageCmd.Attack(damage)
            .FromCard(cardSource, cardPlay)
            .Targeting(target)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
    }

    /// <summary>
    /// Big Badda Boom's second clause: "Then hit again for the damage the
    /// Bombs dealt." Read off the ledger, because by now the pile is gone --
    /// which is exactly why the number is remembered rather than recomputed.
    /// `EB-270`: the ledger banks what each explosion LANDED for, so this is
    /// the card's printed promise and not the raw charge sum it used to be.
    /// </summary>
    public static async Task DealSetOffTotal(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay)
    {
        if (target == null) return;
        var total = KleeOverhaulLedger.For(applier).DamageSetOffThisPlay;
        await DealCardDamage(choiceContext, target, total, cardSource, cardPlay);
    }

    /// <summary>Ammo Scavenging: "Draw a card for each of your Bombs that went
    /// off this turn." Rule 7's first counter, spent.</summary>
    public static async Task DrawPerSetOff(
        PlayerChoiceContext choiceContext, Player player)
    {
        var creature = player.Creature;
        if (creature == null) return;
        var count = KleeOverhaulLedger.For(creature).SetOffThisTurn;
        if (count <= 0) return;
        await CardPileCmd.Draw(choiceContext, count, player);
    }

    /// <summary>
    /// RULE 2. Every Bomb on <paramref name="target"/> goes off, ONE AT A TIME,
    /// each a Pyro hit for its own size -- and the caller's own damage has not
    /// run yet, because the generated card body emits this ahead of it.
    /// Returns how many charges went off.
    ///
    /// THE ORDER IS THE RULE, not an implementation detail: "one at a time"
    /// is what makes a three-Bomb pile three separate Pyro hits, so three
    /// separate reactions, three separate Sparks, and a kill on the second one
    /// leaves the third to jump rather than to fizzle (rule 3, the brief's own
    /// worked example).
    ///
    /// TAKE-THEN-RESOLVE: the whole pile leaves the power first (EB-138's
    /// discipline), so the loop below owns charges that no teardown can take.
    ///
    /// <paramref name="badge"/> is Boom Badge's factor
    /// (<see cref="BoomBadgePower.Spend"/>), taken ONCE by the card-facing
    /// entry point and handed to every pile that clause reaches. It MULTIPLIES
    /// The Big One's armed multiplier, so x4 and x2 meet at x8.
    /// </summary>
    public static async Task<int> SetOff(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel? cardSource, List<int>? overflow = null, int badge = 1)
    {
        if (target == null) return 0;

        var taken = new List<ProtoCharge>();
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier != applier) continue;   // R205: your pile only
            if (pile.TakeAll() is { } charges) taken.AddRange(charges);
        }
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier == applier && pile.TotalSize == 0)
            {
                await PowerCmd.Remove(pile);
            }
        }
        if (taken.Count == 0) return 0;

        var ledger = KleeOverhaulLedger.For(applier);
        var multiplier = ledger.TakeMultiplier() * badge;
        var exploded = 0;

        for (var i = 0; i < taken.Count; i++)
        {
            // RULE 3, the brief's worked example: "The second of three Bombs
            // killed the enemy: the third jumps." The test is read per charge
            // and BEFORE the charge resolves, so the Bomb that lands the kill
            // still goes off on a live enemy and every Bomb behind it jumps.
            if (target.IsDead)
            {
                await JumpCharges(choiceContext, target, taken.Skip(i).ToList(),
                                  applier, cardSource);
                break;
            }
            await Explode(choiceContext, target, taken[i], applier, cardSource,
                          multiplier, overflow);
            exploded++;
        }

        await SweepJumps(choiceContext, applier.CombatState);
        return exploded;
    }

    /// <summary>
    /// ONE explosion, which is the unit every other rule is priced in: one Pyro
    /// hit for the charge's size, one Spark, one payload, one entry in both of
    /// rule 7's counters.
    ///
    /// PYRO, THROUGH <see cref="ElementalHit"/>, is rule 5 and it is why the
    /// reaction half needs no card text at all: the shared pipeline resolves
    /// the aura, the amplifier and the reaction, so a cooked Bomb Vaporizes
    /// exactly as one of Klee's Attacks would. The reaction is DETECTED by
    /// diffing <c>ReactionEffects.TotalResolved</c> across the hit, because
    /// that counter is the one place every reaction in the mod passes through.
    /// </summary>
    private static async Task Explode(
        PlayerChoiceContext choiceContext, Creature target, ProtoCharge charge,
        Creature applier, CardModel? cardSource, int multiplier,
        List<int>? overflow = null)
    {
        var ledger = KleeOverhaulLedger.For(applier);
        var size = charge.Size * multiplier;

        Vfx.KleeCombatVfx.SpawnBombLob(applier, target);

        var reactionsBefore = ReactionEffects.TotalResolved;
        // `EB-450`: which reaction this explosion is about to cause, read
        // before the hit consumes the aura that decides it.
        var pendingAura = AuraCmd.Find(target);
        var pending = pendingAura == null
            ? Elements.Reaction.None
            : ReactionTable.Lookup(pendingAura.Element, Element.Pyro);
        // `EB-270`: the number the hit LANDED for, straight off the funnel that
        // computed it. Big Badda Boom's second clause reads this through the
        // ledger and its face says "the damage the Bombs dealt", so the two
        // have to be one number -- `size` is the charge, not the damage, and
        // under the target's Vulnerable they are different.
        // PYRO, UNLESS A COVEN PERSONAL SAYS OTHERWISE (R236). Prune's
        // Hexhunter Chime is the one thing in either engine that moves rule 5's
        // element, and it moves it for ONE explosion; the call answers Pyro on
        // every other board and with the companion arm off. Sim twin:
        // `companion_coven.bomb_element`, read at `klee_overhaul._explode`.
        var element = await CompanionCovenBombs.ElementFor(choiceContext, applier);
        // THE VERMILLION PACT'S ONE READ, taken BEFORE the funnel runs because
        // the funnel is what consumes it: the aura this explosion is about to
        // eat is the aura the Pact hands back. Null on an aura-less enemy and
        // on every board with no Pact, and the whole of what the Rare knows.
        var auraBefore = VermillionPactPower.AuraToRestore(applier, cardSource,
                                                           target);
        // `EB-343` / R248: THIS DOOR IS THE WHOLE OF "a Bomb carries the
        // target's modifiers only". The charge enters the funnel at its printed
        // size -- Klee's Strength and Weak are hers and never travelled to a
        // charge sitting on an enemy -- and everything the funnel does after
        // that is the target's: the aura, the reaction, the Vulnerable and the
        // per-hit cap. Sparks 'n' Splash's echo takes the same door
        // (2026-09-25): it pays a Bomb's size on a Bomb's terms.
        // R276 (Big Bounce): what stood between this hit and the kill, read
        // BEFORE the hit spends it. Only a caller that passes `overflow` reads
        // it, and every other Set off is byte-identical.
        var standingBefore = target.CurrentHp + target.Block;
        var dealt = await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, element, size, applier);
        var reacted = ReactionEffects.TotalResolved > reactionsBefore;
        // THE OVERFLOW IS THE HIT PAST THE KILL, after the target's own terms
        // (Vulnerable is already in `dealt`), so the bounce carries it without
        // applying them a second time. A hit that did not kill has none.
        if (overflow != null && target.IsDead && dealt > standingBefore)
        {
            overflow.Add(dealt - standingBefore);
        }

        ledger.NoteExplosion(reacted, dealt);
        // `EB-450`, the log half. The badge printed 7 and 12 landed, with the
        // reaction named nowhere, because a Mine fires on the ENEMY's turn
        // where no card is in front of the player to price it. The reaction is
        // NAMED rather than flagged: `pending` is the same lookup
        // `PendingReactionMultiplier` makes for the badge, taken BEFORE the
        // funnel because the funnel consumes the aura, so the line and the
        // preview cannot disagree about which reaction this was.
        ledger.NoteLine(
            (charge.IsMine ? "Mine " : "Bomb ") + size + " went off on "
          + NameOf(target) + " for " + dealt
          + (reacted && pending != Elements.Reaction.None
                ? " (" + pending + ")"
                : reacted ? " (a reaction)" : string.Empty));
        // THE VERMILLION PACT (the pool pass, `EB-491`). The Rare's whole rule
        // is that the aura the explosion CONSUMED is still standing when the
        // Attack behind it lands, so the Attack reacts too -- re-applied HERE,
        // between the explosion and `DealCardDamage`, which is the ordering the
        // face states. It fires only on a reaction the card's own Set off
        // caused and only for an ATTACK: a Mine answering an intent and a
        // Skill's Set off carry no hit behind them for the aura to feed.
        await VermillionPactPower.Restore(choiceContext, applier, target,
                                          auraBefore, reacted);
        // R276, EXPLOSIVE FRAGS: a Mine that went off leaves Vulnerable on its
        // enemy, AFTER its own hit (the face's order), whatever set it off --
        // the enemy's attack or a card's Set off. Sim twin:
        // `klee_overhaul._explode`'s `MINE_FRAGS` read.
        if (charge.IsMine)
        {
            await MineFragsPower.OnMineWentOff(choiceContext, applier, target);
        }
        // THE COMPANION STAND-INS' two this-turn watchers (QUARANTINED,
        // COMPANION_OVERHAUL): Diona's Bomb and Noelle's Mine. Here rather than
        // on `NotifyExplosionListeners` below, because that bus carries no Mine
        // flag and widening this arm's own interface for one companion card
        // would put that arm's rule inside this one. A no-op with it off.
        await CompanionStandIns.OnExplosion(choiceContext, applier, charge.IsMine);

        // THE BOMB PAYLOAD (Jumpy Dumpty). It rides the explosion rather than
        // the card, which is the whole of what makes the starter's promise
        // legible: the Mines arrive when the big Bomb finally goes off, not
        // when it was planted.
        //
        // `EB-457`: THE CORPSE GUARD, and this sweep was the ONE placement
        // walk in the file without it -- <see cref="PlaceOnAll"/>,
        // <see cref="PlaceOnRandom"/>, <see cref="SetOffAll"/> and
        // <see cref="JumpCharges"/> all filter the dead. A Set off kills, and
        // this loop runs BETWEEN the explosions of one pile, so a body that
        // the charge before this one killed is still in `HittableEnemies` when
        // the rider sweeps it. The Mine that lands there is real -- the
        // register holds it and `SweepJumps` will walk it to a survivor at the
        // next beat -- and it prints on no status block in between, which is
        // exactly the shape the r14 seat reported. `isMine: true` and
        // `payloadMineAll: 0` are what make the rider's Mine the same charge a
        // Mine Toss places, so the pile it lands in prints the Mine face and
        // never the rider one.
        if (charge.PayloadMineAll > 0 && applier.CombatState != null)
        {
            var landed = 0;
            foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
            {
                if (enemy.IsDead) continue;
                await Place(choiceContext, enemy, charge.PayloadMineAll,
                            isMine: true, payloadMineAll: 0, applier, cardSource);
                landed++;
            }
            // `EB-318`: THE RIDER SAYS IT FIRED. One detonation of Jumpy
            // Dumpty put a Mine on every enemy and the round-7 seat could
            // confirm it had happened only by watching a Spark tick over --
            // the rule is on the card, the result is on the badges, and
            // nothing joined the two at the moment it happened. The COUNT is
            // in the line because the count is what the seat was trying to
            // read: one Mine per living enemy per detonation, said out loud.
            if (landed > 0)
            {
                ledger.NoteLine(
                    "Its rider placed Mine " + charge.PayloadMineAll + " on "
                  + landed + (landed == 1 ? " enemy" : " enemies"));
            }
        }

        await NotifyExplosionListeners(choiceContext, applier, target, size, reacted);
        // R276, THE CHARGE-AWARE DOOR, after the bus so rule 4's Spark has
        // landed first. Look Out! and Second Surprise need to know this was a
        // MINE, Aftershock needs the charge's own size, and Wait For It...
        // closes its one-shot window here -- none of which the bus carries.
        await KleeExpansion.AfterChargeExploded(
            choiceContext, applier, target, charge, reacted);
    }

    /// <summary>The body a log line names. `Monster.Title` is what the seat's
    /// own screen calls it, and a `LocString` cannot be resolved outside a
    /// booted game -- so a headless read falls back to the type's name rather
    /// than throwing inside a log call.</summary>
    private static string NameOf(Creature creature)
    {
        try
        {
            var title = creature.Monster?.Title.GetFormattedText();
            return string.IsNullOrEmpty(title) ? "the enemy" : title!;
        }
        catch (System.Exception)
        {
            return "the enemy";
        }
    }

    /// <summary>
    /// The explosion bus, once PER EXPLOSION. Same shape and same reason as the
    /// shipped Bomb's detonation bus: subscribers are the applying player's
    /// relics and creature powers, discovered by interface test so a listener
    /// cannot be forgotten at wire-up. Rule 4's Spark arrives here, through
    /// Pounding Surprise, which is the brief's own arrangement -- the relic IS
    /// the Spark rule (sec.8).
    /// </summary>
    private static async Task NotifyExplosionListeners(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        var player = applier.Player;
        if (player == null) return;

        foreach (var relic in player.Relics.ToList())
        {
            if (relic is IProtoExplosionListener listener)
            {
                await listener.OnBombExploded(
                    choiceContext, applier, target, size, reacted);
            }
        }
        foreach (var power in applier.Powers.ToList())
        {
            if (power is IProtoExplosionListener listener)
            {
                await listener.OnBombExploded(
                    choiceContext, applier, target, size, reacted);
            }
        }
    }

    // ---- rule 3: Jump ---------------------------------------------------

    /// <summary>
    /// RULE 3, for charges already in hand: each moves to a random LIVING enemy
    /// at its current size. Nothing is lost and nothing grows -- a jump is a
    /// move, so the size, the Mine flag and the payload all travel.
    ///
    /// Each charge rolls its own destination (the shipped Bomb's per-bomb
    /// target pick, same stream), so three jumping Bombs can land on three
    /// different enemies. With no living enemy left there is nowhere to go and
    /// the charges are dropped, which is the only answer available: the fight
    /// is over.
    /// </summary>
    private static async Task JumpCharges(
        PlayerChoiceContext choiceContext, Creature from,
        IReadOnlyList<ProtoCharge> charges, Creature applier,
        CardModel? cardSource)
    {
        var combat = applier.CombatState;
        if (combat == null) return;

        foreach (var charge in charges)
        {
            var candidates = combat.HittableEnemies
                .Where(e => e != from && !e.IsDead).ToList();
            if (candidates.Count == 0) return;
            var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (dest == null) return;
            await Place(choiceContext, dest, charge.Size, charge.IsMine,
                        charge.PayloadMineAll, applier, cardSource);
        }
    }

    /// <summary>
    /// RULE 3 for the death this arm did NOT cause: "A partner or a poison
    /// killed the enemy: all of them jump."
    ///
    /// WHY A SWEEP AND NOT A DEATH HOOK. The base game does not broadcast
    /// <c>AfterDamageReceived</c> for a blow that killed
    /// (<c>CreatureCmd.Damage</c>: <c>if (!WasTargetKilled || !target.IsDead)</c>,
    /// the same fact <c>BombPower</c> records), and the kill runs INLINE inside
    /// the damage command, detaching the corpse and stripping its powers before
    /// control returns. There is no hook on the dying enemy's own power that
    /// can be trusted to fire. What survives a teardown is the POWER OBJECT and
    /// the charge list on it, so the arm keeps a per-combat register of live
    /// piles and sweeps it: any pile whose enemy is dead or gone hands its
    /// charges to <see cref="JumpCharges"/>.
    ///
    /// WHEN IT RUNS, and the brief does not say, so this is the arm's default
    /// and it is the earliest set of moments that need no new machinery: at the
    /// start of Klee's turn (before growth, so a jumped Bomb grows on its new
    /// enemy this turn), at the end of every Set off, and after a Mine fires.
    /// A jump is therefore always observed before the player's next decision.
    ///
    /// THE EMPTIED PILE LEAVES THE BODY TOO (2026-09-25). A corpse whose
    /// powers the game KEEPS -- an Illusion (<c>IllusionPower</c>: "Illusions
    /// keep their buffs after dying", and this power is a Buff) stays in the
    /// combat and revives -- used to keep the pile this sweep had emptied, and
    /// the revived Eye with Teeth printed "Bomb 0" over a Bomb that was not
    /// there. So every claimed pile still on its body is removed, charged or
    /// not; an empty one jumps nothing (<see cref="Register.Claimed"/>).
    /// </summary>
    public static async Task SweepJumps(
        PlayerChoiceContext choiceContext, ICombatState? combatState)
    {
        if (combatState == null) return;
        foreach (var pile in Register.Claim(combatState))
        {
            if (pile.StillOnBody) await PowerCmd.Remove(pile.Pile);
            if (pile.Applier == null || pile.Charges.Count == 0) continue;
            await JumpCharges(choiceContext, pile.Owner, pile.Charges,
                              pile.Applier, cardSource: null);
        }
    }

    // ---- rule 6: the Mine ----------------------------------------------

    /// <summary>
    /// RULE 6. When this enemy's attack is about to land on ANY PLAYER, every
    /// Mine here goes off first; plain Bombs stay put.
    ///
    /// ANY PLAYER, NOT ONLY HER (the owner, 2026-09-25, "Mines in co-op, pick
    /// a": "a Mine goes off just before ITS enemy's attack lands on ANY player,
    /// not only on the Klee who placed it"). The co-op clause this replaced was
    /// <c>target != Applier</c>, so in the 2026-09-24 co-op run an enemy that
    /// swung at Furina walked through Hair Trigger's Mines untouched. What is
    /// still HERS is everything after the trigger: the explosion is dealt by
    /// the placing Klee (<see cref="Explode"/> with the pile's
    /// <c>Applier</c>), so its Spark, Look Out!'s Block, Explosive Frags and
    /// every other reader pay the Klee who placed it -- and it is still THIS
    /// enemy's hit (<c>dealer == Owner</c>), and still a powered attack.
    ///
    /// "A PLAYER" IS <c>Creature.IsPlayer</c>, the base game's own reading:
    /// an enemy move only ever sees <c>CombatState.PlayerCreatures</c>, which
    /// is <c>Where(c =&gt; c.IsPlayer)</c>. A pet is never the target of an
    /// enemy's attack -- Furina's performers ABSORB a hit aimed at Furina in
    /// her own damage pipeline (<c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c>),
    /// which runs AFTER this hook, so the target here is Furina and the Mine
    /// goes off before her lead performer takes anything.
    ///
    /// <c>BeforeDamageReceived</c> is the hook because it is the one that fires
    /// before the hit lands AND carries a <c>PlayerChoiceContext</c> -- an
    /// explosion deals damage, and dealing damage needs one. The hook is fanned
    /// to every model in the combat (<c>Hook.IterateCombatHookListeners</c>),
    /// which is what lets a power on the ENEMY see the enemy's own outgoing
    /// damage; <c>CompanionPowers</c> reads it from the other side the same way.
    ///
    /// NO PER-ACTION LATCH IS NEEDED, unlike the shipped Bomb's suppression:
    /// the Mines are CONSUMED, so the second hit of a multi-hit intent finds
    /// none. The rule is self-limiting.
    ///
    /// R205 STILL HOLDS FOR THE PILE: it belongs to one Klee, and only her
    /// charges answer here; another Klee's Mines on the same enemy answer the
    /// same attack from their own pile, each paying its own placer.
    ///
    /// <c>EB-336</c>: A LETHAL MINE PRE-EMPTS ITS OWN HIT. See
    /// <see cref="Preempted"/> for the whole of why the kill alone was not
    /// enough, and <c>KleeOverhaulSweepHooks.ModifyHpLostBeforeOsty</c> for
    /// where the pre-emption is spent.
    /// </summary>
    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (!AnswersAttack(Owner, Applier, target, dealer, props)) return;
        if (Applier == null) return;

        var mines = TakeMines();
        if (mines == null) return;
        if (_charges.Count == 0) await PowerCmd.Remove(this);

        var ledger = KleeOverhaulLedger.For(Applier);
        var multiplier = ledger.PeekMultiplier();
        var enemy = Owner;
        for (var i = 0; i < mines.Count; i++)
        {
            if (enemy.IsDead)
            {
                await JumpCharges(choiceContext, enemy, mines.Skip(i).ToList(),
                                  Applier, cardSource: null);
                break;
            }
            await Explode(choiceContext, enemy, mines[i], Applier,
                          cardSource: null, multiplier);
        }
        // `EB-336`. The attacker died to its own Mines, so the hit that
        // triggered them is owed nothing. NOTED HERE and not acted on here:
        // this hook cannot change `modifiedAmount`, which the caller already
        // holds (`CreatureCmd.Damage`).
        if (enemy.IsDead) Preempted.Note(target, enemy);
        await SweepJumps(choiceContext, Applier.CombatState);
    }

    /// <summary>
    /// RULE 6's TRIGGER, the whole of it and PURE, so a headless pin can ask
    /// it: a Mine on <paramref name="enemy"/>, placed by
    /// <paramref name="applier"/>, answers a hit on <paramref name="target"/>
    /// from <paramref name="dealer"/> when the hit is THIS enemy's own powered
    /// attack and lands on a PLAYER -- any player, the placing Klee or an ally
    /// (the owner, 2026-09-25, "Mines in co-op, pick a").
    /// </summary>
    public static bool AnswersAttack(
        Creature enemy, Creature? applier, Creature target, Creature? dealer,
        ValueProp props) =>
        applier != null
        && ReferenceEquals(dealer, enemy)
        && target.IsPlayer
        && props.IsPoweredAttack();

    // ---- EB-336: the hit a lethal Mine pre-empts -------------------------

    /// <summary>
    /// THE ONE HIT A LETHAL MINE HAS ALREADY ANSWERED.
    ///
    /// WHAT THE SEAT SAW (`klee round 7b, opus-act2b.md`,
    /// finding 3). A Chomper on 4 HP under a `Mine 4` swung `8x2`. The Mine
    /// fired, killed it, and the SECOND hit never landed -- and the FIRST one
    /// did, for its full 8. The tip promises "before the hit lands", and what
    /// that promises a player is that the enemy dies before hurting them.
    ///
    /// WHY THE KILL IS NOT ENOUGH BY ITSELF. `CreatureCmd.Damage` reads
    /// `dealer.IsDead` ONCE, at the top of the whole call, and
    /// `AttackCommand.Execute` reads `Attacker.IsDead` once per hit BEFORE it
    /// issues that call. So a dealer that dies DURING a hit -- which is
    /// exactly what a Mine does, from inside `Hook.BeforeDamageReceived` --
    /// is caught for every LATER hit and never for the one in flight. That is
    /// the whole defect, and it is why the second hit of the `8x2` was already
    /// correct.
    ///
    /// WHERE IT IS SPENT, AND WHY NOT HERE. The hook has `amount` by value and
    /// the caller keeps its own `modifiedAmount`; the first hook after this one
    /// that can move the number is `Hook.ModifyHpLost(..., BeforeOsty)`, one
    /// line further down `CreatureCmd.Damage`. So the pre-emption is NOTED
    /// here and READ there, purely, by <c>KleeOverhaulSweepHooks</c> -- which
    /// has to be the reader, because by then this pile is gone: the kill runs
    /// inline and `RemoveAllPowersAfterDeath` strips the corpse's powers before
    /// control returns, so the dead enemy's own power is no longer a hook
    /// listener. That is the same fact `SweepJumps` is built on.
    ///
    /// BLOCK IS STILL SPENT, said plainly rather than hidden: `DamageBlockInternal`
    /// runs between the two hooks and there is nothing between them to stop it.
    /// The rule the row asks for, and the one both engines now keep, is that a
    /// Mine whose explosion kills the attacker costs Klee no HP. The sim reaches
    /// the stronger form for free -- `combat._enemy_turn` breaks out of the hit
    /// loop before Block -- and that difference is Block, never HP.
    ///
    /// NO LATCH TO CLEAR, for the same reason rule 6 needs none: the predicate
    /// requires the dealer to be DEAD, and a dead dealer never deals again --
    /// `CreatureCmd.Damage` returns early for one. The note is dropped with the
    /// rest of the arm's per-combat state when <see cref="Register.Rebase"/>
    /// sees a new combat.
    /// </summary>
    public static class Preempted
    {
        private static Creature? _victim;
        private static Creature? _attacker;

        /// <summary>PUBLIC, like the pure mutators above and for the same
        /// reason: KleeTests is a separate assembly and this rule's whole
        /// arithmetic is three references, so the alternative was an
        /// <c>InternalsVisibleTo</c> nothing else in this mod needs.</summary>
        public static void Note(Creature victim, Creature attacker)
        {
            _victim = victim;
            _attacker = attacker;
        }

        public static void Clear()
        {
            _victim = null;
            _attacker = null;
        }

        /// <summary>Is THIS hit -- this victim, this dealer -- the one a Mine
        /// already answered? PURE: a modifier hook may not mutate (the Vigil's
        /// note in <c>KuragePowers.cs</c>), and this reads three references and
        /// one flag.</summary>
        public static bool Covers(Creature? victim, Creature? dealer) =>
            _victim != null && _attacker != null
            && ReferenceEquals(_victim, victim)
            && ReferenceEquals(_attacker, dealer)
            && dealer.IsDead;
    }

    // ---- placement, and the card verbs -----------------------------------

    /// <summary>
    /// Plant one charge on <paramref name="target"/>, stacking into this
    /// placer's own pile (R205). The single entry point for every source:
    /// a card's <c>plant_bomb</c>, a jump's landing, a payload's Mines and
    /// Chained Reactions' re-bomb all arrive here, so the register below cannot
    /// miss a pile.
    /// </summary>
    public static async Task Place(
        PlayerChoiceContext choiceContext, Creature target, int size,
        bool isMine, int payloadMineAll, Creature applier, CardModel? cardSource)
    {
        var power = await PowerCmd.Apply<ProtoBombPower>(
            choiceContext, target, 1, applier: applier, cardSource: cardSource);

        if (power is ProtoBombPower bomb)
        {
            bomb.AddCharge(new ProtoCharge(size, isMine, payloadMineAll));
            Register.Note(bomb);
        }
        else
        {
            Log.Warn($"[{KleeMod.ModId}] ProtoBombPower.Place: could not resolve "
                   + "the applied power instance; the charge was not recorded.");
        }
    }

    /// <summary>Mine Toss: one charge on EVERY enemy. A snapshot, so a payload
    /// firing mid-sweep cannot change who is swept.</summary>
    public static async Task PlaceOnAll(
        PlayerChoiceContext choiceContext, Creature applier, int size,
        bool isMine, int payloadMineAll, CardModel? cardSource)
    {
        var combat = applier.CombatState;
        if (combat == null) return;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            await Place(choiceContext, enemy, size, isMine, payloadMineAll,
                        applier, cardSource);
        }
    }

    /// <summary>Jumpy Dumpty: one charge on a random living enemy.</summary>
    public static async Task PlaceOnRandom(
        PlayerChoiceContext choiceContext, Creature applier, int size,
        bool isMine, int payloadMineAll, CardModel? cardSource)
    {
        var combat = applier.CombatState;
        if (combat == null) return;
        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (target == null) return;
        await Place(choiceContext, target, size, isMine, payloadMineAll,
                    applier, cardSource);
    }

    /// <summary>
    /// Does ANY living enemy hold a charge this Klee placed? <c>EB-261</c>.
    ///
    /// The gate behind a card whose whole body is a Set off. <i>Quick Fuse</i>
    /// ("Spend 1 [Spark]. Set off target enemy's Bombs.") was playable on a
    /// Bomb-less board: it spent the Spark and did nothing, and the Codex
    /// tester had to INFER that from the result rather than read it off the
    /// card (`klee-overhaul-r1-codex-b`, fight 3). <c>CardModel.IsPlayable</c>
    /// is the extension point the base game documents for exactly this shape
    /// (Grand Finale's empty draw pile), and it is the one the Spark price
    /// already uses, so a card that cannot do anything refuses in the same
    /// place and the same way as one that cannot pay.
    ///
    /// BOARD-WIDE, not per-target, because <c>IsPlayable</c> is asked without
    /// a target -- the same question the acceptance asks ("unplayable on a
    /// Bomb-less board, playable once any enemy holds one"). Aiming at the
    /// wrong enemy stays the player's to get right.
    ///
    /// R205's per-placer rule applies here as everywhere: another Klee's pile
    /// is not one this seat can set off, so it does not make her card playable.
    ///
    /// <c>Enemies</c> AND NOT <c>HittableEnemies</c>, unlike the sweeps above,
    /// and deliberately: those ACT on every enemy, while this only asks what is
    /// on the board, and <see cref="SetOff"/> -- the thing the card actually
    /// does -- takes an aimed target and never consults hittability either. A
    /// Bomb on a living enemy a hook is currently shielding is still a Bomb
    /// this card can set off, so it still makes the card playable.
    /// </summary>
    public static bool AnyPlacedBy(Creature? applier)
    {
        var combat = applier?.CombatState;
        if (applier == null || combat == null) return false;

        foreach (var enemy in combat.Enemies)
        {
            if (enemy.IsDead) continue;
            if (HoldsChargeFrom(enemy, applier)) return true;
        }
        return false;
    }

    /// <summary>Does <paramref name="enemy"/> hold a live charge that
    /// <paramref name="applier"/> placed? The per-enemy half of
    /// <see cref="AnyPlacedBy"/>, pure and R205-scoped.</summary>
    public static bool HoldsChargeFrom(Creature enemy, Creature applier)
    {
        foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier == applier && pile._charges.Count > 0) return true;
        }
        return false;
    }

    /// <summary>
    /// What this placer's charges on <paramref name="enemy"/> add up to, RAW.
    /// (Sparks 'n' Splash read it until R250; since 2026-09-25 the echo reads
    /// <see cref="LargestBombFor"/>.)
    ///
    /// PURE, and R205-scoped like every other read here: another Klee's pile
    /// is not hers to read.
    /// </summary>
    public static int TotalPlacedBy(Creature? enemy, Creature? applier)
    {
        if (enemy == null || applier == null) return 0;
        var total = 0;
        foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier == applier) total += pile.TotalSize;
        }
        return total;
    }

    /// <summary>
    /// This placer's SINGLE LARGEST charge on <paramref name="enemy"/>, RAW.
    /// Sparks 'n' Splash's per-enemy read from R250 until 2026-09-25, when the
    /// echo moved to the board-wide <see cref="LargestBombFor"/>; Careful Now
    /// and its sibling still read it.
    ///
    /// <see cref="TotalPlacedBy"/> survives unchanged and unremoved: growth,
    /// jumps and Sorry Jean's Block are still priced in the raw SUM, and a
    /// Set off still pays every charge.
    ///
    /// R205-scoped like every other read here: another Klee's pile is not
    /// hers to echo.
    /// </summary>
    public static int LargestPlacedBy(Creature? enemy, Creature? applier)
    {
        if (enemy == null || applier == null) return 0;
        var largest = 0;
        foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier != applier) continue;
            if (pile.LargestSize > largest) largest = pile.LargestSize;
        }
        return largest;
    }

    /// <summary>
    /// Chain Fuse: every Bomb on ONE enemy grows by <paramref name="amount"/>.
    /// This placer's piles only, for the same reason Set off reads only hers.
    /// </summary>
    public static void GrowOn(Creature? target, Creature applier, int amount)
    {
        if (target == null) return;
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier == applier) pile.GrowBy(amount);
        }
    }

    /// <summary>
    /// Careful Arrangement: move ALL of this placer's Bombs onto one enemy AS
    /// ONE Bomb, which then grows by <paramref name="growth"/>.
    ///
    /// TWO THINGS THE CARD TEXT DOES NOT SAY, chosen as the simplest reading
    /// that loses nothing (and reported as defaults):
    ///   * the merged Bomb is a MINE if any merged charge was one -- merging
    ///     must not silently delete the defence the player set up;
    ///   * it carries the payloads of every merged charge, summed, for the same
    ///     reason: a merge is a move, and a move loses nothing.
    /// </summary>
    /// <summary>
    /// R276, HAIR TRIGGER: every charge of <paramref name="applier"/>'s on
    /// <paramref name="target"/> becomes a Mine at its own size. Pure, like
    /// <see cref="GrowOn"/>: no charge moves, merges or goes off, so the pile
    /// keeps its order and its riders. Sim twin: <c>klee_overhaul.mine_all_on</c>.
    /// </summary>
    public static void MineAllOn(Creature? target, Creature applier)
    {
        if (target == null) return;
        foreach (var pile in target.Powers.OfType<ProtoBombPower>().ToList())
        {
            if (pile.Applier == applier) pile.MakeAllMines();
        }
    }

    public static async Task MergeAllTo(
        PlayerChoiceContext choiceContext, Creature? dest, Creature applier,
        int growth, CardModel? cardSource)
    {
        if (dest == null || applier.CombatState == null) return;

        var size = 0;
        var isMine = false;
        var payload = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>().ToList())
            {
                if (pile.Applier != applier) continue;
                if (pile.TakeAll() is not { } charges) continue;
                foreach (var charge in charges)
                {
                    size += charge.Size;
                    isMine |= charge.IsMine;
                    payload += charge.PayloadMineAll;
                }
                await PowerCmd.Remove(pile);
            }
        }
        if (size == 0) return;
        await Place(choiceContext, dest, size + growth, isMine, payload,
                    applier, cardSource);
    }

    /// <summary>
    /// Sorry, Jean...: remove ONE of your Bombs and gain Block equal to its
    /// size. Returns the size removed, 0 if there was nothing to remove.
    ///
    /// WHICH Bomb, the card does not say. THE LARGEST, which is the simplest
    /// deterministic answer and the only one a player can plan around: an
    /// emergency exit whose size is a coin flip is not an exit.
    /// </summary>
    public static async Task<int> RemoveLargestForBlock(
        PlayerChoiceContext choiceContext, Creature applier)
    {
        if (applier.CombatState == null) return 0;

        ProtoBombPower? best = null;
        var bestIndex = -1;
        var bestSize = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
            {
                if (pile.Applier != applier) continue;
                for (var i = 0; i < pile._charges.Count; i++)
                {
                    if (pile._charges[i].Size <= bestSize) continue;
                    best = pile;
                    bestIndex = i;
                    bestSize = pile._charges[i].Size;
                }
            }
        }
        if (best == null || best.TakeAt(bestIndex) is not { } removed) return 0;
        if (best.TotalSize == 0 && best.Charges.Count == 0)
        {
            await PowerCmd.Remove(best);
        }
        return removed.Size;
    }

    /// <summary>Sorry, Jean..., whole: remove the largest Bomb and gain Block
    /// equal to its size. ONE call, so the number removed and the number gained
    /// are the same number by construction and no printed value can drift from
    /// either.
    ///
    /// `EB-390`: <c>ValueProp.Move</c>, WHICH IS THE CARD-BLOCK PIPELINE, and
    /// the row's own "one rule" default. Under Dexterity 2 the r10 run-2 seat
    /// watched Dig In go 8 to 10 and Barbara's 5 to 7 while this card paid 13
    /// for a Bomb 13 -- and its face says "gain Block", which is the sentence
    /// Dexterity's own face is about ("Block gained from cards"). The other
    /// reading was available (print that the size is paid raw) and it costs a
    /// card its verb, so the rule moves instead of the words:
    /// <c>DexterityPower.ModifyBlockAdditive</c> and <c>FrailPower</c>'s
    /// multiplicative hook share one predicate,
    /// <c>props.IsPoweredCardOrMonsterMoveBlock()</c>, so this is one switch
    /// and both terms arrive with it.
    ///
    /// <see cref="BlockForLargestBomb"/> TAKES THE SAME SWITCH, because it is
    /// the same rule on the other card: two Bomb-sized Blocks that disagree
    /// about Dexterity is the defect this row is about, one card later. What
    /// stays <c>Unpowered</c> is Block no card printed -- a power's or a
    /// relic's -- which is the line the engine's own predicate draws. Sim
    /// twin: <c>klee_overhaul.remove_largest_for_block</c>, through
    /// <c>powers.modify_block_gained</c>.</summary>
    public static async Task RemoveLargestForBlockAndGain(
        PlayerChoiceContext choiceContext, Creature applier,
        int multiplier = 1)
    {
        var size = await RemoveLargestForBlock(choiceContext, applier);
        if (size <= 0) return;
        // R276 (Favonius Escort): "Gain Block equal to twice its size". The
        // multiplier is the row's; Sorry, Jean... passes none and gains the
        // size itself, exactly as before.
        size = BlockForRemoved(size, multiplier);
        await CreatureCmd.GainBlock(applier, size, ValueProp.Move, null);
    }

    /// <summary>R276. The Block a removed Bomb of <paramref name="size"/>
    /// pays at <paramref name="multiplier"/> -- PURE, the half of
    /// <see cref="RemoveLargestForBlockAndGain"/> a headless pin can read.
    /// A multiplier below 1 reads as 1: the card can print no smaller one.
    /// </summary>
    public static int BlockForRemoved(int size, int multiplier) =>
        size <= 0 ? 0 : size * System.Math.Max(1, multiplier);

    /// <summary>
    /// Careful Now (<c>R252</c>): gain Block equal to your largest Bomb, up to
    /// <paramref name="cap"/>. Returns the Block granted.
    ///
    /// IT READS THE PILE AND SPENDS NOTHING, which is the whole of what
    /// separates it from <see cref="RemoveLargestForBlockAndGain"/> above.
    /// Sorry, Jean... is an emergency exit that costs the Bomb; this is the
    /// cook's own posture -- the bigger the charge she is standing over, the
    /// more carefully she stands -- and afterwards every Bomb is still there
    /// and still growing.
    ///
    /// THE LARGEST SINGLE CHARGE, BOARD-WIDE, and both halves are the printed
    /// face's ("your largest Bomb"). Per enemy it is
    /// <see cref="LargestPlacedBy"/>, the Splash's own reader since R250;
    /// across the board it is the largest of those, which is the same walk
    /// Sorry, Jean... makes one charge at a time. The card takes no target, so
    /// "the enemy" could only ever have meant the board.
    ///
    /// THE CAP IS THE ROW'S, never a law constant: it is a printed number the
    /// upgrade moves (<c>upgrade: {cap: +3}</c>), and it is what keeps the row
    /// from turning Grounded's cook turn into a stall.
    ///
    /// `EB-390`: <c>ValueProp.Move</c>, THE CARD-BLOCK PIPELINE, for the
    /// reason <see cref="RemoveLargestForBlockAndGain"/> gives at length. It
    /// used to be <c>Unpowered</c> on the reading that a Bomb-sized Block is a
    /// rule's Block rather than a card's; the row's finding is that a face
    /// saying "gain Block" is what Dexterity's own face is about, and two
    /// Bomb-sized Blocks disagreeing about it is the same defect twice. Sim
    /// twin: <c>klee_overhaul.block_for_largest_bomb</c>, through
    /// <c>powers.modify_block_gained</c>.
    /// </summary>
    public static async Task<int> BlockForLargestBomb(
        PlayerChoiceContext choiceContext, Creature applier, int cap)
    {
        if (applier.CombatState == null || cap <= 0) return 0;

        var largest = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            var here = LargestPlacedBy(enemy, applier);
            if (here > largest) largest = here;
        }
        var amount = largest < cap ? largest : cap;
        if (amount <= 0) return 0;
        await CreatureCmd.GainBlock(applier, amount, ValueProp.Move, null);
        return amount;
    }

    /// <summary>
    /// THE CO-OP SET, <i>Hide Here!</i>: "Another player gains Block equal to
    /// your largest Bomb, up to 12." Careful Now's read (<see
    /// cref="LargestBombBlock"/>, board-wide, nothing removed) paid to the
    /// player the card was aimed at instead of to Klee. The play is attached,
    /// so it is the CARD's Block and KLEE's Dexterity folds into it -- the
    /// base game's Lift, which gives an ally Block through the same door.
    /// </summary>
    public static async Task<int> BlockAllyForLargestBomb(
        PlayerChoiceContext choiceContext, Creature applier, int cap,
        Creature? ally, CardPlay? cardPlay)
    {
        if (ally is not { IsAlive: true }) return 0;
        var amount = LargestBombBlock(applier, cap);
        if (amount <= 0) return 0;
        await CreatureCmd.GainBlock(ally, amount, ValueProp.Move, cardPlay);
        return amount;
    }

    /// <summary>The Block <see cref="BlockAllyForLargestBomb"/> pays: the
    /// largest single charge <paramref name="applier"/> has on any living
    /// enemy, capped at <paramref name="cap"/> -- <see
    /// cref="BlockForLargestBomb"/>'s own walk, word for word. PURE, so a
    /// headless pin can ask it.</summary>
    public static int LargestBombBlock(Creature applier, int cap)
    {
        if (applier.CombatState == null || cap <= 0) return 0;

        var largest = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            var here = LargestPlacedBy(enemy, applier);
            if (here > largest) largest = here;
        }
        return largest < cap ? largest : cap;
    }

    /// <summary>
    /// Stoke the Fuse (the round-11 pool pass): the SINGLE largest Bomb on the
    /// board grows by <paramref name="perSpark"/> for every Spark this card
    /// spent. Returns the growth applied, 0 if nothing grew.
    ///
    /// <paramref name="sparksSpent"/> IS HANDED IN, not read here, and that is
    /// the whole ordering rule. <c>SparkPower.Spend</c> debits the bank where
    /// it is called, so the generated body captures
    /// <c>SparkPower.SparksAtPlay</c> BEFORE the price is paid and passes the
    /// number down -- reading the bank after the spend would read zero. The
    /// sim answers the same question off <c>state.sparks_at_play</c>, the
    /// documented twin of that accessor, and the op is legal only behind an
    /// all-in Spark price so the two readings are the same number.
    ///
    /// THE LARGEST SINGLE CHARGE, BOARD-WIDE -- <see cref="BlockForLargestBomb"/>'s
    /// walk one rule over, with <see cref="GrowLargestChargeBy"/>'s tie-break
    /// inside each pile. ONE CHARGE AND NOT THE PILE is the row's decision:
    /// <see cref="GrowOn"/> spreads growth across an enemy's charges, and this
    /// pours the bank into the one she is already cooking.
    ///
    /// IT SETS NOTHING OFF. Sim twin:
    /// <c>klee_overhaul.grow_largest_per_spark</c>.
    /// </summary>
    public static int GrowLargestPerSpark(
        Creature applier, int perSpark, int sparksSpent)
    {
        if (applier.CombatState == null) return 0;
        if (perSpark <= 0 || sparksSpent <= 0) return 0;

        ProtoBombPower? bestPile = null;
        var bestSize = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
            {
                if (pile.Applier != applier) continue;
                if (pile.LargestSize > bestSize)
                {
                    bestPile = pile;
                    bestSize = pile.LargestSize;
                }
            }
        }
        if (bestPile == null) return 0;

        var amount = perSpark * sparksSpent;
        bestPile.GrowLargestChargeBy(amount);
        return amount;
    }

    /// <summary>
    /// THE POOL PASS's one shared read (`EB-491`): the SINGLE largest charge
    /// this Klee holds anywhere on the living board, as the pile that carries
    /// it and its index inside that pile.
    ///
    /// The walk <see cref="RemoveLargestForBlock"/> makes one charge at a time
    /// and <see cref="GrowLargestPerSpark"/> makes one pile at a time, named
    /// once so All of My Treasures! and Split Charge cannot
    /// disagree about which Bomb "your largest Bomb" is. THE TIE-BREAK IS THE
    /// FIRST ONE FOUND -- living enemies in order, each pile in place order --
    /// which is Sorry, Jean...'s rule and the only one a player can plan
    /// around. Sim twin: <c>klee_overhaul.largest_charge</c>.
    /// </summary>
    private static (ProtoBombPower? Pile, int Index, int Size) LargestCharge(
        Creature applier)
    {
        if (applier.CombatState == null) return (null, -1, 0);

        ProtoBombPower? best = null;
        var bestIndex = -1;
        var bestSize = 0;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
            {
                if (pile.Applier != applier) continue;
                for (var i = 0; i < pile._charges.Count; i++)
                {
                    if (pile._charges[i].Size <= bestSize) continue;
                    best = pile;
                    bestIndex = i;
                    bestSize = pile._charges[i].Size;
                }
            }
        }
        return (best, bestIndex, bestSize);
    }

    /// <summary>
    /// All of My Treasures! (the pool pass, `EB-491`): "Place a Bomb on the
    /// enemy equal to your largest Bomb." A COPY and not a move -- the pile it
    /// was measured against is untouched and still growing, which is what makes
    /// the card a cook decision (play it on a 12, or wait for a 16) rather than
    /// a second Careful Arrangement.
    ///
    /// THE COPY IS A PLAIN BOMB. A Mine's defence is not doubled by a card that
    /// prints "Bomb", and the copy carries no payload: Jumpy Dumpty's Mines are
    /// the charge's own promise, not its size.
    ///
    /// IT GROWS ON ITS OWN SCHEDULE from here (rule 9, each Bomb grows
    /// separately), which is the whole of what "equal to" means -- equal WHEN
    /// PLACED. Nothing happens on a board with no Bomb on it. Sim twin:
    /// <c>klee_overhaul.place_copy_of_largest</c>.
    /// </summary>
    public static async Task PlaceCopyOfLargest(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel? cardSource)
    {
        if (target == null) return;
        var size = LargestCharge(applier).Size;
        if (size <= 0) return;
        await Place(choiceContext, target, size, isMine: false,
                    payloadMineAll: 0, applier, cardSource);
    }

    /// <summary>
    /// Split Charge (the pool pass, `EB-491`): "Split your largest Bomb into
    /// two halves on random enemies." Careful Arrangement's opposite, and the
    /// arm's one bridge from Cook to Spray -- a pile cooked on one body becomes
    /// two fuses wherever they land.
    ///
    /// THE HALVES ARE <c>n/2</c> AND <c>n - n/2</c>, so an odd Bomb loses
    /// nothing and the bigger half is the second one; each then grows by
    /// <paramref name="growth"/>, which is 0 until the upgrade buys it.
    ///
    /// EACH HALF ROLLS ITS OWN DESTINATION, independently, which is
    /// <see cref="JumpCharges"/>'s rule and means both halves can land on one
    /// enemy -- on a single-enemy board they always do, which is the row's
    /// printed losing line (two piles growing 4 apiece where one grew 4, into
    /// Block, for a card and an energy).
    ///
    /// A MINE'S HALVES ARE PLAIN BOMBS. The Mine is one fuse and splitting it
    /// does not make two; the defence is spent, which is the price of the
    /// bridge.
    ///
    /// A LARGEST BOMB OF 1 DOES NOTHING: there is no split of 1 that leaves two
    /// Bombs, and halving it to 0 and 1 would silently delete a charge. Sim
    /// twin: <c>klee_overhaul.split_largest</c>.
    /// </summary>
    public static async Task SplitLargest(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel? cardSource, int growth)
    {
        var combat = applier.CombatState;
        if (combat == null) return;

        var (pile, index, size) = LargestCharge(applier);
        if (pile == null || size <= 1) return;
        if (pile.TakeAt(index) is not { } removed) return;
        if (pile.TotalSize == 0 && pile.Charges.Count == 0)
        {
            await PowerCmd.Remove(pile);
        }

        var halves = new[] { removed.Size / 2, removed.Size - removed.Size / 2 };
        foreach (var half in halves)
        {
            var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
            if (candidates.Count == 0) return;
            var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (dest == null) return;
            await Place(choiceContext, dest, half + growth, isMine: false,
                        payloadMineAll: 0, applier, cardSource);
        }
    }

    /// <summary>Big Badda Boom's second clause reads this: the damage this
    /// play's explosions have already dealt. Kept on the ledger, not here,
    /// because the card asks about the PLAY and a pile is gone by the time it
    /// asks.</summary>
    public static int DamageSetOffThisPlay(Creature applier) =>
        KleeOverhaulLedger.For(applier).DamageSetOffThisPlay;

    // ---- the per-combat register of live piles ---------------------------

    /// <summary>
    /// Every pile this combat has seen, so a JUMP can still find the charges of
    /// an enemy the game has already torn down. See <see cref="SweepJumps"/>
    /// for why a register is the only shape available.
    ///
    /// NOT A SECOND COPY OF THE STATE, which is the trap here: it holds power
    /// REFERENCES, so the charges it reaches are the same list the badge shows
    /// and the same list an explosion consumes. Cleared whenever the combat
    /// instance changes, so it holds at most this combat's piles.
    /// </summary>
    public static class Register
    {
        private static ICombatState? _combat;
        private static readonly List<ProtoBombPower> _piles = new();

        public static void Note(ProtoBombPower pile)
        {
            Rebase(pile.CombatState);
            if (!_piles.Contains(pile)) _piles.Add(pile);
        }

        /// <summary>Piles whose enemy is dead or gone: what a jump owes, and
        /// the pile the sweep then takes off the body. An already-empty pile is
        /// claimed too (2026-09-25), with no charges, so it is removed rather
        /// than left to badge "Bomb 0" on a body the game keeps. Emptied as it
        /// is claimed, so a second sweep in the same beat finds
        /// nothing.</summary>
        public static List<Claimed> Claim(ICombatState combatState)
        {
            Rebase(combatState);
            var owed = new List<Claimed>();
            foreach (var pile in _piles.ToList())
            {
                var owner = pile.Owner;
                var alive = owner is { IsDead: false }
                            && combatState.HittableEnemies.Contains(owner);
                if (alive) continue;
                _piles.Remove(pile);
                var charges = pile.TakeAll() ?? new List<ProtoCharge>();
                owed.Add(new Claimed(owner, pile.Applier, charges, pile));
            }
            return owed;
        }

        public static void Rebase(ICombatState? combatState)
        {
            if (ReferenceEquals(_combat, combatState)) return;
            _combat = combatState;
            _piles.Clear();
            // `EB-336`: the pre-empted hit is per-combat state too, and this is
            // the one place the arm already notices a new combat.
            Preempted.Clear();
        }

        /// <summary>Charges taken off a pile whose enemy is gone, and the
        /// pile itself.</summary>
        public readonly record struct Claimed(
            Creature Owner, Creature? Applier, IReadOnlyList<ProtoCharge> Charges,
            ProtoBombPower Pile)
        {
            /// <summary>Is the emptied pile still attached to its body? True
            /// on a corpse the game keeps (an Illusion); false once the game
            /// has stripped the corpse's powers. PURE.</summary>
            public bool StillOnBody =>
                Owner != null && Owner.Powers.Contains(Pile);
        }
    }
}

/// <summary>
/// The explosion event bus (rule 4's carrier, and Chained Reactions'). Once
/// PER EXPLOSION, so a three-Bomb Set off is three
/// events -- which is what makes "1 Spark per explosion" a rule about
/// explosions rather than about cards.
///
/// <paramref name="reacted"/> is the half the React loop is built on: it says
/// whether THIS explosion consumed an off-element aura, which no listener could
/// work out for itself after the fact.
/// </summary>
public interface IProtoExplosionListener
{
    /// <param name="choiceContext">Live context; a listener may deal damage.</param>
    /// <param name="applier">The Klee whose card planted the Bomb.</param>
    /// <param name="target">The enemy it went off on.</param>
    /// <param name="size">What that single explosion dealt, doubling included.</param>
    /// <param name="reacted">Did this explosion trigger an Elemental Reaction?</param>
    Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted);
}
