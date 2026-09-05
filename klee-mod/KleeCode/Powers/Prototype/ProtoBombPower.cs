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
/// Bomb that ALSO goes off when its enemy attacks Klee, before the hit lands.
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
/// The costs of the reading are the two things a player CAN see: the badge and
/// the tooltip now name every modifier folded into them
/// (<see cref="Localization"/>), rather than the one that used to be named.
/// </summary>
public sealed class ProtoBombPower : PowerModel, ILocalizationProvider
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
                // FOUR SENTENCES, which is the ceiling, so `EB-343`'s clause
                // is paid for by merging the first two rather than added to
                // them. NO SEMICOLON, and that is not a style note:
                // `tools/lint_text_conventions.py` reads these literals out of
                // the SOURCE with a regex that stops at one, so a semicolon
                // makes a player-facing string invisible to its own ceiling.
                ("description",
                    "A charge on this enemy that grows at the start of your "
                  + "turn. Every [gold]Bomb[/gold] here goes off as Pyro "
                  + "damage when [gold]Set off[/gold], never by itself. The "
                  + "hit is not an Attack, so only this enemy's "
                  + "[gold]Vulnerable[/gold] and a damage cap move it, never a "
                  + "debuff that answers Attacks and never anything of yours."
                  + MineClause),
            };
            // EB-260, EB-287 and `EB-343`. ROWS, not one row with conditionals
            // in it, for the reason <see cref="SmartDescriptionLocKey"/> gives:
            // a headless pin can read a row and cannot run `LocManager`. TWO
            // axes, and the second one GREW: the live Mine count (EB-260 -- a
            // player must never read "never goes off by itself" over a pile
            // that answers the enemy's next attack) and which of the target's
            // modifiers the printed total has folded in (EB-287 asked for one
            // of them by name and R248 asks for all of them).
            //
            // GENERATED RATHER THAN TYPED, which is what keeps the grid honest
            // now that it is a grid: every key the selector below can compose
            // has a row, because both come off <see cref="FoldedMods.All"/>. A
            // key with no row behind it falls back to the static description
            // (`PowerModel.HasSmartDescription` is a `LocString.Exists` probe),
            // so a hole here is a silently blank face rather than a crash.
            // `EB-536` ADDED THE THIRD AXIS: whether the pile holds ONE
            // charge or several. The hit clause is a fact about a STACK and
            // reads as noise on a single Bomb, where the total and the hit are
            // the same number.
            foreach (var single in new[] { false, true })
            {
                foreach (var mines in new[] { false, true })
                {
                    foreach (var mods in FoldedMods.All)
                    {
                        rows.Add((SmartKey(single, mines, mods),
                                  Face(single, mines, mods)));
                    }
                }
            }
            return rows;
        }
    }

    /// <summary>
    /// Rule 6, in the words the static face already used. ONE sentence, two
    /// surfaces: the tooltip carried it and the smart face did not, which is
    /// the whole of <c>EB-260</c> -- the Codex tester read the contradiction
    /// twice and called it the most confusing thing on the screen
    /// (`klee-overhaul-r1-codex-b`, fights 4 and 5).
    /// </summary>
    /// <summary>`EB-436` PUT THE HIT IN THE SENTENCE. The clause said WHEN
    /// and nothing about the attack, and the r12 act-1 seat read mitigation
    /// into it: three Mines left armed against an elite, five went off,
    /// "every hit landed in full, 36 to 18 HP". The only thing a Mine does to
    /// the attack is stop it happening, by killing the attacker -- `EB-336`'s
    /// rule, <see cref="Preempted"/> -- so the badge says that and stops.
    /// Same sentence, same two surfaces the clause has had since
    /// <c>EB-260</c>.</summary>
    private const string MineClause =
        " A [gold]Mine[/gold] also goes off before this enemy's hit, which "
      + "lands in full unless the Mine kills.";

    // `EB-343`'s sentence is written INTO the static description above rather
    // than pulled out as a constant beside `MineClause`, and the reason is the
    // measuring rule: `tools/lint_text_conventions.py` counts a bare
    // identifier in a concatenation as ONE numeral, so a named constant would
    // hide 65 characters of player-facing text from its own ceiling.
    //
    // `EB-373` REWROTE THAT SENTENCE ON BOTH SURFACES, because it was not the
    // rule this file implements. `FoldedMods` reads exactly two things off the
    // target -- its `VulnerablePower`, and whichever power returns the lowest
    // `ModifyDamageCap` -- and "the enemy's debuffs" claimed the rest. The r9
    // seat lost two reads to it: a Slow 50 enemy took 48 from a pile printing
    // 46, and a Flutter 5 enemy took a 27 Bomb whole while a printed 8 Attack
    // landed 4. Both of those say "from Attacks" on their own faces, and the
    // reason they miss is the one both surfaces now lead with -- the hit is not
    // an Attack. The keyword tip says it in its own shorter words ("Not an
    // Attack: only their Vulnerable and a cap move it",
    // `ArmKeywordTips.ForBomb`), while this face, read on the enemy where the
    // modifiers actually are, names the cap and both exclusions outright. Same
    // rule, two surfaces, the arrangement `MineClause` already has.

    /// <summary>
    /// The face the wire prints (<c>PowerModel.HoverTips</c> uses the SMART
    /// description for any mutable power that has one). <c>{Size}</c> is the
    /// number the Set off will actually deal -- see
    /// <see cref="PredictedSetOffDamage"/>, <c>EB-265</c> and <c>EB-343</c>.
    ///
    /// EB-287: IT IS PROSE NOW. The r3 Opus seat read the old parenthetical
    /// -- "(2 Bombs, 0 of them Mines)" -- as a debug string, and the r3 Codex
    /// seat had to REASON OUT that the total was the Weak-adjusted one
    /// ("I inferred [it] was the Weak-adjusted amount but had to reason
    /// through"). So the count is a sentence, the Mine clause appears only
    /// when there is a Mine to talk about, and each modifier term says its own
    /// name.
    ///
    /// EB-361: FOUR SENTENCES IS THE CEILING AND RULE 3 IS THE FIFTH FACT, so
    /// the growth sentence is a clause on the count rather than a sentence of
    /// its own. Rule 3 -- a Bomb whose enemy dies moves to a survivor -- was on
    /// no card, badge or tip, and three round-10 seats met it as a surprise:
    /// one read `Bomb 36 / Bombs here: 3` on an enemy it had planted 11 on and
    /// filed it as the screen contradicting itself. The badge is where a player
    /// meets the survivor's stack, so it is where the rule is printed.
    /// </summary>
    private static string Face(bool single, bool mines, FoldedMods mods) =>
        "[gold]Set off[/gold] here deals " + PyroTotal + mods.Clause
      + (single ? string.Empty : HitCount) + "."
      + (mines ? BombsWithMines : Bombs)
      + (mines ? MineClause : NoSelfSentence) + JumpSentence;

    /// <summary>
    /// `EB-514`: THE HIT COUNT, IN THE HEADLINE.
    ///
    /// THE DEFECT (Klee r18 lane 2 (c) 4). "`Mine 7 -- Set off here deals 7
    /// Pyro damage. Bombs here: 4 / 3, including 2 Mines`. Reading only the
    /// headline I would have budgeted one Spark of refund and one hit; it is
    /// actually two hits and two Sparks, which matters enormously for whether
    /// a Set off is free. The information is in the second sentence but the
    /// number I plan against is in the first."
    ///
    /// AND THAT IS EXACTLY RIGHT: <see cref="PyroTotal"/> is a SUM over the
    /// charges, so a stack prints one number where the board will produce
    /// several hits -- several reactions, several Sparks, several chances for
    /// one to land on a corpse. The queue was already on the face
    /// (<c>EB-450</c>'s <c>{Charges}</c>) and the seat still planned against
    /// the headline, which is the reading this clause is about: the count goes
    /// where the total is, not one sentence later.
    ///
    /// SPARKS ARE NAMED RATHER THAN LEFT TO RULE 4. One Spark per explosion is
    /// printed on the Spark tip, and the seat had read it -- the miss was that
    /// "deals 7" hid how many explosions "7" was. "For as many Sparks" is the
    /// same rule said where the arithmetic is, which is the whole of the row.
    ///
    /// <c>{Count}</c> IS `EB-289`'s VAR, off the charge list rather than off
    /// the stack, so a Mine that has already self-popped is not counted; it
    /// left <see cref="Bombs"/> at `EB-450` because the list said the count
    /// more plainly there, and it comes back HERE because the headline is a
    /// different sentence with a different job. Both faces are over the power
    /// ceiling for it and both are excepted by name in
    /// `tools/lint_text_conventions.py`.
    /// </summary>
    ///
    /// `EB-536` CUT IT OFF THE SINGLE-CHARGE FACE AND SPELLED THE SPARKS OUT.
    /// "In 1 hit for as many Sparks", printed on every Bomb block, "was never
    /// comprehensible" (Klee r19 lane 2) -- and on a pile of one it is saying
    /// nothing: the total IS the hit, and "as many" is a comparison to a
    /// number the sentence has already spent. So the clause is a property of a
    /// STACK, it appears only on a stack, and it names the Spark count instead
    /// of pointing back at the hit count. The plural goes with it: this face
    /// is only ever chosen for two charges or more.
    private const string HitCount =
        ", in [blue]{Count}[/blue] hits for [blue]{Count}[/blue] "
      + "[gold]Sparks[/gold]";

    /// <summary>The total, with no full stop: a modifier clause may follow it.
    ///
    /// EVERY PIECE OF THE GRID IS A NAMED CONSTANT, this one included, and it
    /// is not decoration. `tools/lint_text_conventions.py` reads the player's
    /// whole text off the SOURCE -- it cannot run `LocManager` any more than a
    /// headless pin can -- and rebuilds these faces from these names. A clause
    /// spelled inline would be text the ceilings never measured.</summary>
    private const string PyroTotal = "[blue]{Size}[/blue] Pyro damage";

    /// <summary>`EB-343`'s four clauses, one per term the total can pass
    /// through. See <see cref="FoldedMods.Clause"/> for how they compose.
    /// </summary>
    private const string VulnerableClause = " after [gold]Vulnerable[/gold]";

    private const string HardToKillClause =
        " capped by [gold]Hard To Kill[/gold]";

    private const string IntangibleClause =
        " capped by [gold]Intangible[/gold]";

    /// <summary>A cap this build does not know the name of. See
    /// <see cref="CapKind"/> for why it is worth a clause at all.</summary>
    private const string UnnamedCapClause = " capped by this enemy";

    /// <summary>The row key <see cref="Face"/> is filed under, and the ONE
    /// place the two axes are spelled into a key -- <see cref="Localization"/>
    /// writes the rows with it and <see cref="SmartDescriptionLocKey"/> reads
    /// one back, so a row and its selector cannot drift apart.</summary>
    private static string SmartKey(bool single, bool mines, FoldedMods mods) =>
        "smartDescription" + (single ? "One" : string.Empty)
      + (mines ? "Mines" : string.Empty) + mods.KeySuffix;

    /// <summary>
    /// `EB-289`. <c>{Count}</c> AND NOT <c>{Amount}</c>, and the difference is
    /// the whole defect.
    ///
    /// <c>PowerModel</c> binds <c>{Amount}</c> to its own stack amount
    /// (<c>locString.Add("Amount", Amount)</c>), and this power's stack is
    /// raised once per <see cref="Place"/> and never lowered: the charge list
    /// is emptied by <see cref="TakeAll"/>, <see cref="TakeMines"/> and
    /// <see cref="TakeAt"/>, which are PURE by design -- they run inside a
    /// damage hook where no command may -- so none of them can move a stack.
    /// A pile whose Mine had already gone off therefore kept printing the Mine
    /// in its count.
    ///
    /// The r4 Opus seat read exactly that and worked out why unaided: "Bomb 8
    /// ... Bombs here: 2", a Set off that dealt 8 and paid ONE Spark, and
    /// "its Mine had already self-popped on the previous enemy turn, so only
    /// one bomb should have remained". The SPARK was right -- rule 4 pays one
    /// per explosion and one Bomb went off -- and the COUNT was the lie.
    ///
    /// So the count joins <c>{Size}</c> and <c>{Mines}</c> as a var read off
    /// the charge list itself in <see cref="SyncDisplay"/>. Every number on
    /// this face now comes from the list the explosions consume, and the stack
    /// amount is left to be what the engine uses it for.
    /// </summary>
    /// `EB-361` FOLDED RULE 1'S GROWTH INTO THIS SENTENCE, and the reason is
    /// the sentence ceiling rather than taste: rule 3's jump is a fifth fact on
    /// a face that may print four sentences, so the growth clause rides the
    /// count it is about. "growing each turn" is the phrasing the Bomb keyword
    /// tip already uses for the same rule ("grows {BombGrowth} a turn"), which
    /// is also where the RATE is printed -- the badge has never carried it.
    /// `EB-450` REPLACED THE COUNT WITH THE LIST, and the count is still in
    /// it: `Bombs here: 5, 8, 20, 12` says four as plainly as `4` did and adds
    /// the one fact the badge withheld.
    ///
    /// THE DEFECT. The badge printed a SUM and a count -- `Bomb 45 (4 bombs)`
    /// -- while `EB-432`'s Set off tip says the charges go off oldest first
    /// and the FIRST one takes the aura. So on a bombed body wearing Cryo,
    /// which charge Melts was a fact the player had to remember placing rather
    /// than read, and the r13 seat carried it in its head for a whole fight.
    /// Two surfaces, one rule, and only one of them could name the charge.
    ///
    /// OLDEST FIRST IS THE ORDER `SetOff` WALKS -- `_charges` is placement
    /// order and every taker walks it front to back -- so the list is printed
    /// in the list's own order and no second definition of "oldest" exists.
    ///
    /// `{Count}` STAYS A VAR (`EB-289` is why it is not `{Amount}`) and leaves
    /// this text: `5 / 8 / 20 / 12` says four as plainly as `4` did, and
    /// printing both would put two number groups in one sentence for no fact.
    ///
    /// THE WORDS "OLDEST FIRST" ARE NOT HERE AND THAT IS THE CEILING, said out
    /// loud rather than left to be discovered. This face was 125 of its
    /// 125-character power ceiling (`tools/lint_text_conventions.py`, and it
    /// bites) until `EB-514` put the hit count in the headline and took it
    /// over, so the clause has no room without rewriting `PyroTotal`,
    /// `NoSelfSentence` or `JumpSentence` -- three ruled sentences, to restate
    /// a rule the reader already has: `EB-432` put "oldest first" on the
    /// `Set off` tip, which is printed on the card that will spend this pile.
    /// The tip says the ORDER and the badge now shows the QUEUE, which is the
    /// pairing the r13 seat was doing in its head.
    ///
    /// `EB-536` (widened, Klee r20) MADE THE LABEL SAY WHAT THE NUMBERS ARE.
    /// "Bombs here: 3, including 1 Mine" reads as a COUNT and is a list of
    /// SIZES, and on a pile of one the two readings are indistinguishable: the
    /// natural-lane seat read `Bombs here: 3` as three Bombs and "was
    /// genuinely confused for a fight and a half", getting it only when a
    /// later pile printed `Bomb 21 ... Bombs here: 9 / 12` and the arithmetic
    /// refused the count reading. `EB-450` had already replaced the count with
    /// the list and the label was the half it left behind. Six characters, on
    /// two faces that are excepted from the power ceiling by name, and the
    /// count is not lost with it -- a list of sizes says how many there are as
    /// plainly as a number did.
    ///
    /// SLASHES AND NOT COMMAS inside the list, for one reason: the sentence
    /// around it is comma-separated, and `Bombs here: 5, 8, 20, 12, growing
    /// each turn` hides where the pile stops. It costs nothing at the ceiling
    /// -- the lint renders a hole as one character however it is filled.
    private const string Bombs =
        " Bomb sizes here: [blue]{Charges}[/blue], growing each turn.";

    /// <summary>
    /// `EB-471`. WHICH SIDE OF THE GROWTH TICK A MINE LANDS ON, and it is on
    /// THIS face rather than on <see cref="Bombs"/> because this is the face a
    /// pile with a Mine in it prints and <see cref="Bombs"/> is at 125 of 125.
    ///
    /// THE FIND (Klee r15 run 2 (c) 3). "A Mine fires at its base size on the
    /// enemy's turn, before the growth tick, and nothing printed says which
    /// side of the tick it lands on: Jumpy Dumpty's Mine 3 paid 3, not 7, and
    /// I reverse-engineered it from HP." The row offered "Mines do not grow"
    /// as the sentence to print and that sentence is FALSE here:
    /// <see cref="GrowBy"/> walks every charge and a Mine is a charge, so a
    /// Mine that lives to the next turn start is 7. What is true, and what the
    /// seat actually lacked, is WHEN the growth happens -- and paired with
    /// <see cref="MineClause"/>'s "goes off before this enemy's hit" it says
    /// the Mine pays the size it has now.
    /// </summary>
    private const string BombsWithMines =
        " Bomb sizes here: [blue]{Charges}[/blue], including [blue]{Mines}[/blue] "
      + "[gold]Mine{Mines:plural:|s}[/gold], growing at your turn's start.";

    /// <summary>Rule 3, `EB-361`. A Bomb whose enemy dies moves to a random
    /// LIVING enemy at its size -- see <see cref="JumpCharges"/>, which is what
    /// this sentence describes: every charge travels, Mines included, so the
    /// word is "a survivor" and not "the next enemy". Printed on both branches,
    /// because a Mine jumps exactly as a plain Bomb does.</summary>
    private const string JumpSentence = " A kill moves them to a survivor.";

    /// <summary>Rule 7 on a pile with no Mine in it. A pile holding a Mine
    /// prints <see cref="MineClause"/> INSTEAD, because "none goes off by
    /// itself" over a pile that answers the enemy's next attack is the exact
    /// contradiction <c>EB-260</c> was filed on.</summary>
    private const string NoSelfSentence = " None goes off by itself.";

    /// <summary>
    /// EB-260, EB-287 and `EB-343`, the selector.
    /// <c>PowerModel.SmartDescription</c> resolves this key on EVERY read of
    /// <c>HoverTips</c>, so the face follows the pile AND the enemy under it:
    /// the moment a Mine lands here the printed text gains rule 6's sentence
    /// and the moment the last one fires it loses it again, and the total
    /// names each of the enemy's modifiers exactly while that modifier is
    /// moving it. Rows and a key, rather than conditionals inside one row,
    /// because a headless pin can read a row and cannot run <c>LocManager</c>
    /// (KleeTests README, "The headless boundary").
    /// </summary>
    protected override string SmartDescriptionLocKey =>
        Id.Entry + "."
      + SmartKey(_charges.Count == 1, MineCount > 0, LiveMods);

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
    /// has -- <see cref="BombsWithMines"/>'s "including {Mines} Mines", the
    /// fuse mark -- and rule 6's sentence rides beside it either way, because
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
    /// WHICH OF THE TARGET'S MODIFIERS THE PRINTED TOTAL HAS FOLDED IN, right
    /// now. EB-287's half, widened by R248 from "Weak, and Vulnerable in
    /// silence" to every term the number passed through.
    ///
    /// The guards are <see cref="PredictedSetOffDamage"/>'s own, in its own
    /// order and for its own reasons: an empty pile prints 0 and no modifier
    /// touches it, and a canonical (compendium) copy prints the stored
    /// <c>TotalSize</c> because <see cref="PowerModel.Owner"/>'s getter
    /// asserts mutability -- and <c>HasSmartDescription</c> reads this key
    /// BEFORE the mutability check that gates the smart face, so the read has
    /// to survive one.
    ///
    /// <c>Applier</c> IS NO LONGER CONSULTED, and that is the rule: a Bomb is
    /// the enemy's burden, so nothing about Klee is in this number to name.
    /// </summary>
    private FoldedMods LiveMods
    {
        get
        {
            if (_charges.Count == 0 || !IsMutable) return FoldedMods.None;
            var target = Owner;
            return target == null ? FoldedMods.None : FoldedMods.For(target);
        }
    }

    /// <summary>
    /// The modifiers one Set off here passes through, as a value the face and
    /// the selector both read. `EB-343`.
    ///
    /// TWO AXES AND NOT A LIST, because the printed sentence is a sentence:
    /// Vulnerable multiplies and a cap clamps, in that order, and the clause
    /// below reads in that order too.
    ///
    /// PRESENCE, NOT EFFECT. A modifier is named while it is ON the enemy and
    /// applies to this hit -- not only when it happened to change the total.
    /// "Name what the number went through" is a rule a player can check against
    /// the enemy's own badges; "name what moved it" would make the sentence
    /// blink out on the boards where two modifiers happen to cancel, which is
    /// exactly when a player most wants to know both are there.
    /// </summary>
    private readonly record struct FoldedMods(bool Vulnerable, CapKind Cap)
    {
        internal static readonly FoldedMods None = new(false, CapKind.None);

        /// <summary>Every combination the selector can produce, so
        /// <see cref="Localization"/> can emit a row for each.</summary>
        internal static IEnumerable<FoldedMods> All =>
            from vulnerable in new[] { false, true }
            from cap in new[] { CapKind.None, CapKind.HardToKill,
                                CapKind.Intangible, CapKind.Other }
            select new FoldedMods(vulnerable, cap);

        /// <summary>What is standing on <paramref name="target"/> right now.
        /// The Vulnerable read is <c>SimDamagePipeline.TargetMods</c>' own, and
        /// the cap is whichever power SET the minimum
        /// <c>SimDamagePipeline.TargetCap</c> returns -- found by the same scan,
        /// so the named power is the one whose number the face is printing.
        /// </summary>
        internal static FoldedMods For(Creature target)
        {
            var vulnerable =
                (target.Powers.OfType<VulnerablePower>()
                    .FirstOrDefault()?.Amount ?? 0) > 0;

            var best = decimal.MaxValue;
            var cap = CapKind.None;
            foreach (var power in target.Powers)
            {
                var one = power.ModifyDamageCap(
                    target, ValueProp.Unpowered, dealer: null,
                    cardSource: null, cardPlay: null);
                if (one >= best) continue;
                best = one;
                cap = power switch
                {
                    IntangiblePower => CapKind.Intangible,
                    HardToKillPower => CapKind.HardToKill,
                    _ => CapKind.Other,
                };
            }
            return new FoldedMods(vulnerable, cap);
        }

        internal string KeySuffix =>
            (Vulnerable ? "Vulnerable" : string.Empty) + Cap switch
            {
                CapKind.HardToKill => "HardToKill",
                CapKind.Intangible => "Intangible",
                CapKind.Other => "Capped",
                _ => string.Empty,
            };

        /// <summary>The clause that goes after <see cref="PyroTotal"/>, empty
        /// on an unmodified enemy, and in PIPELINE ORDER: Vulnerable
        /// multiplies, then the cap clamps, so the sentence reads that way
        /// too.</summary>
        internal string Clause
        {
            get
            {
                var capped = Cap switch
                {
                    CapKind.HardToKill => HardToKillClause,
                    CapKind.Intangible => IntangibleClause,
                    CapKind.Other => UnnamedCapClause,
                    _ => string.Empty,
                };
                if (!Vulnerable) return capped;
                return VulnerableClause
                     + (capped.Length > 0 ? "," + capped : string.Empty);
            }
        }
    }

    /// <summary>
    /// Which power is doing the capping, because the face has to say its name.
    ///
    /// The 0.111.0 decompile carries exactly two <c>ModifyDamageCap</c>
    /// overrides -- <c>HardToKillPower</c> (Exoskeleton) and
    /// <c>IntangiblePower</c> (Soul Fysh, Test Subject, Nemesis) -- and
    /// <see cref="CapKind.Other"/> is for a cap this build does not know about.
    /// It is not dead weight and it is not a guess: an unrecognised cap would
    /// otherwise be folded into the printed number in SILENCE, which is the
    /// exact defect R248 is fixing, so it gets a clause that claims no name.
    /// </summary>
    private enum CapKind { None, HardToKill, Intangible, Other }

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

    /// <summary>The single largest charge on this pile -- what Sparks 'n'
    /// Splash's echo pays here (R250). `TotalSize`'s twin: the raw SUM every
    /// other rule inside the arm is priced in (growth, jumps, Sorry Jean's
    /// Block, a Set off) survives beside it untouched.</summary>
    public int LargestSize => _charges.Count == 0 ? 0 : _charges.Max(c => c.Size);

    /// <summary>How many of this pile's charges are Mines -- the fuse mark.</summary>
    public int MineCount => _charges.Count(c => c.IsMine);

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
        };

    /// <summary>
    /// <c>{Charges}</c>, the pile's sizes in the order they will go off
    /// (`EB-450`).
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

            return string.Join(" / ", pile._charges.Select(
                c => c.Size.ToString(
                    System.Globalization.CultureInfo.InvariantCulture)));
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
    /// Rule 6: an attack on Klee pops the Mines and nothing else. PURE.</summary>
    public List<ProtoCharge>? TakeMines()
    {
        var mines = _charges.Where(c => c.IsMine).ToList();
        if (mines.Count == 0) return null;
        _charges.RemoveAll(c => c.IsMine);
        SyncDisplay();
        return mines;
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
    /// Rule 1's growth NUMBER for one Klee, right now. PURE, and it is one
    /// function because the two modifiers compose in one printed way:
    /// Explosives Workshop ADDS <see cref="KleeOverhaulLaw.WorkshopGrowth"/>
    /// per stack ("your Bombs grow by 1 more"), Alice's Recipe MULTIPLIES what
    /// is left by <see cref="KleeOverhaulLaw.AliceMultiplier"/> ("your Bombs
    /// grow twice each turn").
    ///
    /// ADD-THEN-MULTIPLY, and it is the only reading that leaves both faces
    /// true: "twice" is twice the growth the turn would otherwise have had,
    /// Workshop's +1 included, so one Workshop and the Recipe is
    /// (3 + 1) x 2 = 8. The other order would make the Rare read "twice the
    /// base and the Workshop once", which neither card says. The brief's own
    /// gloss on Alice is still "Breaks rule 1".
    /// </summary>
    public static int GrowthFor(Creature? klee)
    {
        if (klee == null) return KleeOverhaulLaw.BombGrowth;
        var workshop = klee.Powers.OfType<ExplosivesWorkshopGrowthPower>()
            .Sum(p => p.Amount) * KleeOverhaulLaw.WorkshopGrowth;
        var growth = KleeOverhaulLaw.BombGrowth + workshop;
        return klee.Powers.OfType<AlicesRecipePower>().Any()
            ? growth * KleeOverhaulLaw.AliceMultiplier
            : growth;
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
        if (target == null) return;
        await SetOff(choiceContext, target, applier, cardSource);
        await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
    }

    /// <summary>
    /// "Set off each enemy that has a non-Pyro aura" (Flame Dance), and the
    /// unfiltered all-enemies form beside it.
    ///
    /// The aura filter reads the board as it stands when the card resolves, so
    /// an enemy whose aura an earlier explosion in the same play consumed is
    /// no longer eligible -- which is what "each enemy that HAS" says.
    /// </summary>
    public static async Task SetOffAll(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage,
        bool nonPyroAuraOnly)
    {
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
            await SetOff(choiceContext, enemy, applier, cardSource);
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
        var combat = applier.CombatState;
        if (combat == null) return;

        for (var i = 0; i < times; i++)
        {
            var living = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
            if (living.Count == 0) return;
            var candidates = BombedFirst(living, applier);
            var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target == null) return;

            await SetOff(choiceContext, target, applier, cardSource);
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
    /// </summary>
    public static async Task<int> SetOff(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel? cardSource)
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
        var multiplier = ledger.TakeMultiplier();
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
                          multiplier);
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
        Creature applier, CardModel? cardSource, int multiplier)
    {
        var ledger = KleeOverhaulLedger.For(applier);
        var size = charge.Size * multiplier;

        Vfx.KleeCombatVfx.SpawnBombLob(applier, target);

        var reactionsBefore = ReactionEffects.TotalResolved;
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
        // per-hit cap. It is the ONE caller of this entry point; the echo two
        // files over is a card's own damage and keeps hers.
        var dealt = await ElementalHit.DealWithoutDealerMods(
            choiceContext, target, element, size, applier);
        var reacted = ReactionEffects.TotalResolved > reactionsBefore;

        ledger.NoteExplosion(reacted, dealt);
        // THE VERMILLION PACT (the pool pass, `EB-491`). The Rare's whole rule
        // is that the aura the explosion CONSUMED is still standing when the
        // Attack behind it lands, so the Attack reacts too -- re-applied HERE,
        // between the explosion and `DealCardDamage`, which is the ordering the
        // face states. It fires only on a reaction the card's own Set off
        // caused and only for an ATTACK: a Mine answering an intent and a
        // Skill's Set off carry no hit behind them for the aura to feed.
        await VermillionPactPower.Restore(choiceContext, applier, target,
                                          auraBefore, reacted);
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
        if (charge.PayloadMineAll > 0 && applier.CombatState != null)
        {
            foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
            {
                await Place(choiceContext, enemy, charge.PayloadMineAll,
                            isMine: true, payloadMineAll: 0, applier, cardSource);
            }
        }

        await NotifyExplosionListeners(choiceContext, applier, target, size, reacted);
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
    /// </summary>
    public static async Task SweepJumps(
        PlayerChoiceContext choiceContext, ICombatState? combatState)
    {
        if (combatState == null) return;
        foreach (var pile in Register.Claim(combatState))
        {
            if (pile.Applier == null) continue;
            await JumpCharges(choiceContext, pile.Owner, pile.Charges,
                              pile.Applier, cardSource: null);
        }
    }

    // ---- rule 6: the Mine ----------------------------------------------

    /// <summary>
    /// RULE 6. When this enemy's attack is about to land on the Klee who placed
    /// the Mine, every Mine here goes off first; plain Bombs stay put.
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
    /// <c>target != Applier</c> is the co-op clause and it falls out of R205:
    /// this pile belongs to one Klee, and it is her attack to answer.
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
        if (dealer != Owner || target != Applier) return;
        if (!props.IsPoweredAttack()) return;
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
    /// Sparks 'n' Splash's echo reads it ("damage equal to the Bombs on it")
    /// and hands it to the same <c>ElementalHit.Deal</c> an explosion hands a
    /// charge's size to, and the raw sum is what enters that pipeline in both
    /// cases.
    ///
    /// THE ECHO KEEPS KLEE'S OWN TERMS AND AN EXPLOSION NO LONGER DOES
    /// (<c>EB-343</c>), which is not an inconsistency: the echo is the CARD's
    /// damage, sized off the pile, dealt by Klee at the end of her turn -- the
    /// pile is read and not spent, no Bomb goes off, no Spark is paid and
    /// neither of rule 7's counters moves. R248 is a rule about Bombs going
    /// off. What the echo shares with an explosion is the element and the
    /// reaction, not the dealer.
    ///
    /// PURE, and R205-scoped like every other read here: another Klee's pile
    /// is not hers to echo.
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
    /// This placer's SINGLE LARGEST charge on <paramref name="enemy"/>, RAW --
    /// what Sparks 'n' Splash's echo pays here since <c>R250</c>
    /// (<c>klee-overhaul-round-8-2026-09-04.md</c> sec.6 pick 1 default (1)),
    /// replacing <see cref="TotalPlacedBy"/> at that one call site. Round 8's
    /// seats found the sum made banking always right and every Set off card
    /// "deletes my engine"; the largest charge keeps hold-or-cash a decision
    /// after the Power lands, and a Set off (<c>SetOff</c>) still cashes the
    /// whole pile.
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
    /// either.</summary>
    public static async Task RemoveLargestForBlockAndGain(
        PlayerChoiceContext choiceContext, Creature applier)
    {
        var size = await RemoveLargestForBlock(choiceContext, applier);
        if (size <= 0) return;
        await CreatureCmd.GainBlock(applier, size, ValueProp.Unpowered, null);
    }

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
    /// UNPOWERED (<c>ValueProp.Unpowered</c>), like every other rule-sourced
    /// Block on this arm: no Dexterity feeds it and no Frail bites it, because
    /// it is a RULE's Block and not a card's printed Block. Sim twin:
    /// <c>klee_overhaul.block_for_largest_bomb</c>.
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
        await CreatureCmd.GainBlock(applier, amount, ValueProp.Unpowered, null);
        return amount;
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
    /// once so All of My Treasures!, Split Charge and Kindling's floor cannot
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
    /// Kindling (the pool pass, `EB-491`): "Each Bomb on an enemy whose aura is
    /// not Pyro grows by <paramref name="amount"/>. If there is none, your
    /// largest Bomb grows by <paramref name="floor"/>."
    ///
    /// THE FLOOR IS WHAT MAKES IT A REACT ROW WITH A LOSING LINE RATHER THAN A
    /// DEAD CARD. Catalytic Converter is dead in a mono-Pyro deck by its own
    /// printed admission (R244 pick 2's shape); this one still buys 2 growth
    /// when no applier went first, and buys 4 per Bomb on every foreign aura
    /// when one did.
    ///
    /// "AURA IS NOT PYRO" IS THE ENEMY'S CARRIED AURA and no aura does not
    /// count -- <see cref="SetOffAll"/>'s <c>nonPyroAuraOnly</c> filter, read
    /// the same way for the same reason (Flame Dance and this row must not
    /// disagree about which enemies are "off-element"). The board is read as it
    /// stands; nothing here consumes an aura, so no order matters inside it.
    ///
    /// AN ENEMY WITH THE AURA AND NO BOMB IS NOT A MATCH: the face counts
    /// BOMBS, not enemies, so a board of aura'd but Bomb-less enemies takes the
    /// floor. Sim twin: <c>klee_overhaul.grow_bombs_off_aura</c>.
    /// </summary>
    public static void GrowOffAura(Creature applier, int amount, int floor)
    {
        if (applier.CombatState == null) return;

        var grew = false;
        foreach (var enemy in applier.CombatState.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            var aura = AuraCmd.Find(enemy);
            if (aura == null || aura.Element == Element.Pyro) continue;
            if (!HoldsChargeFrom(enemy, applier)) continue;
            GrowOn(enemy, applier, amount);
            grew = true;
        }
        if (grew || floor <= 0) return;

        var pile = LargestCharge(applier).Pile;
        // The board's largest charge is by construction its own pile's largest,
        // and both walks break a tie the same way (first found, place order) --
        // so this is `LargestCharge`'s index, reached through the pure mutation
        // that already owns it.
        pile?.GrowLargestChargeBy(floor);
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

        /// <summary>Piles whose enemy is dead or gone AND that still carry
        /// charges: what a jump owes. Emptied as it is claimed, so a second
        /// sweep in the same beat finds nothing.</summary>
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
                if (pile.TakeAll() is { } charges)
                {
                    owed.Add(new Claimed(owner, pile.Applier, charges));
                }
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

        /// <summary>Charges taken off a pile whose enemy is gone.</summary>
        public readonly record struct Claimed(
            Creature Owner, Creature? Applier, IReadOnlyList<ProtoCharge> Charges);
    }
}

/// <summary>
/// The explosion event bus (rule 4's carrier, and Chained Reactions' and
/// Catalytic Converter's). Once PER EXPLOSION, so a three-Bomb Set off is three
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
