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
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bomb"),
        ("description",
            "A charge on this enemy. It grows at the start of your turn. "
          + "Every [gold]Bomb[/gold] here goes off as Pyro damage when "
          + "[gold]Set off[/gold], never by itself." + MineClause),
        // EB-260 and EB-287. FOUR ROWS, not one row with conditionals in it,
        // for the reason <see cref="SmartDescriptionLocKey"/> gives: a headless
        // pin can read a row and cannot run `LocManager`. The two axes are the
        // live Mine count (EB-260 -- a player must never read "never goes off
        // by itself" over a pile that answers the enemy's next attack) and
        // whether the total above is the Weak-reduced one (EB-287).
        ("smartDescription", Face(mines: false, weak: false)),
        ("smartDescriptionWeak", Face(mines: false, weak: true)),
        ("smartDescriptionMines", Face(mines: true, weak: false)),
        ("smartDescriptionMinesWeak", Face(mines: true, weak: true)),
    };

    /// <summary>
    /// Rule 6, in the words the static face already used. ONE sentence, two
    /// surfaces: the tooltip carried it and the smart face did not, which is
    /// the whole of <c>EB-260</c> -- the Codex tester read the contradiction
    /// twice and called it the most confusing thing on the screen
    /// (`klee-overhaul-r1-codex-b`, fights 4 and 5).
    /// </summary>
    private const string MineClause =
        " A [gold]Mine[/gold] also goes off when this enemy attacks you, "
      + "before the hit lands.";

    /// <summary>
    /// The face the wire prints (<c>PowerModel.HoverTips</c> uses the SMART
    /// description for any mutable power that has one). <c>{Size}</c> is the
    /// number the Set off will actually deal, Strength and Weak included --
    /// see <see cref="PredictedSetOffDamage"/>, <c>EB-265</c>.
    ///
    /// EB-287: IT IS PROSE NOW. The r3 Opus seat read the old parenthetical
    /// -- "(2 Bombs, 0 of them Mines)" -- as a debug string, and the r3 Codex
    /// seat had to REASON OUT that the total was the Weak-adjusted one
    /// ("I inferred [it] was the Weak-adjusted amount but had to reason
    /// through"). So the count is a sentence, the Mine clause appears only
    /// when there is a Mine to talk about, and the Weak term says its own
    /// name.
    /// </summary>
    private static string Face(bool mines, bool weak) =>
        "[gold]Set off[/gold] here deals " + (weak ? WeakTotal : PlainTotal)
      + (mines ? BombsWithMines : Bombs) + GrowthSentence
      + (mines ? MineClause : NoSelfSentence);

    /// <summary>The total, and the one term a player cannot see in it. The
    /// clause is chosen off <see cref="TotalIsAfterWeak"/>, which reads the
    /// same pile state <see cref="PredictedSetOffDamage"/> reads, so the
    /// sentence and the number can never disagree.</summary>
    private const string PlainTotal = "[blue]{Size}[/blue] Pyro damage.";

    private const string WeakTotal =
        "[blue]{Size}[/blue] Pyro damage after [gold]Weak[/gold].";

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
    private const string Bombs = " Bombs here: [blue]{Count}[/blue].";

    private const string BombsWithMines =
        " Bombs here: [blue]{Count}[/blue], including [blue]{Mines}[/blue] "
      + "[gold]Mine{Mines:plural:|s}[/gold].";

    private const string GrowthSentence =
        " Each grows at the start of your turn.";

    /// <summary>Rule 7 on a pile with no Mine in it. A pile holding a Mine
    /// prints <see cref="MineClause"/> INSTEAD, because "none goes off by
    /// itself" over a pile that answers the enemy's next attack is the exact
    /// contradiction <c>EB-260</c> was filed on.</summary>
    private const string NoSelfSentence = " None goes off by itself.";

    /// <summary>
    /// EB-260 and EB-287, the selector. <c>PowerModel.SmartDescription</c>
    /// resolves this key on EVERY read of <c>HoverTips</c>, so the face
    /// follows the pile: the moment a Mine lands here the printed text gains
    /// rule 6's sentence and the moment the last one fires it loses it again,
    /// and the total names Weak exactly while Weak is what is shrinking it.
    /// Rows and a key, rather than conditionals inside one row, because a
    /// headless pin can read a row and cannot run <c>LocManager</c> (KleeTests
    /// README, "The headless boundary").
    /// </summary>
    protected override string SmartDescriptionLocKey =>
        Id.Entry + ".smartDescription"
      + (MineCount > 0 ? "Mines" : string.Empty)
      + (TotalIsAfterWeak ? "Weak" : string.Empty);

    /// <summary>
    /// Is the printed total the Weak-REDUCED one? EB-287's second half.
    ///
    /// The guards are <see cref="PredictedSetOffDamage"/>'s own, in its own
    /// order and for its own reasons: an empty pile prints 0 and no modifier
    /// touches it, and a canonical (compendium) copy prints the stored
    /// <c>TotalSize</c> because <see cref="PowerModel.Owner"/>'s getter
    /// asserts mutability. <c>Applier</c>'s getter does not assert, so it is
    /// safe on either copy -- and <c>HasSmartDescription</c> reads this key
    /// BEFORE the mutability check that gates the smart face, so it has to be.
    /// </summary>
    private bool TotalIsAfterWeak =>
        _charges.Count > 0 && IsMutable && Owner != null
        && (Applier?.Powers.OfType<WeakPower>().FirstOrDefault()?.Amount ?? 0) > 0;

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
        };

    /// <summary>
    /// <c>{Size}</c>, READ LIVE. <c>EB-265</c>.
    ///
    /// A plain <see cref="DynamicVar"/> is a stored number, written by
    /// <see cref="SyncDisplay"/> when the pile changes -- and Strength does not
    /// change the pile. So a Klee who gained Strength after her Bombs were
    /// planted would read a face that was right when it was written and wrong
    /// when she read it, which is the same defect one turn later. This subclass
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
    /// WHAT A SET OFF HERE ACTUALLY DEALS, right now -- <c>EB-265</c>.
    ///
    /// The face used to print <see cref="TotalSize"/>, the raw sum of the
    /// charges, while <see cref="Explode"/> sends every charge through
    /// <c>ElementalHit.Deal</c>, which adds Strength PER HIT. With Strength 2
    /// and two Bombs the face printed 10 and the set-off dealt 14, and the
    /// blind tester called it "the one number I learned not to trust"
    /// (`klee-overhaul-r1-opus`, fight 2).
    ///
    /// SHARED, NOT RE-DERIVED: <c>SimDamagePipeline.Resolve</c> is the same
    /// dealer-mods / amplifier / one-truncation chain <c>ElementalHit.Deal</c>
    /// runs, called once per charge exactly as the explosion loop does -- so
    /// per-charge truncation and per-charge Strength are the pipeline's, not a
    /// second copy of them here.
    ///
    /// TWO TERMS ARE DELIBERATELY LEFT OUT, and both are one-shot rather than
    /// standing state:
    ///   * the REACTION amplifier, because the first explosion of a Set off
    ///     consumes the aura the rest would have reacted with -- there is no
    ///     one multiplier for the pile;
    ///   * The Big One's DOUBLING, because reading it means
    ///     <c>KleeOverhaulLedger.For</c>, which rolls per-turn counters, and a
    ///     face is read on every state poll -- a tooltip may not have side
    ///     effects.
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
        foreach (var charge in _charges)
        {
            total += SimDamagePipeline.Resolve(Applier, target, charge.Size, 1m);
        }
        return total;
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
    /// </summary>
    public static async Task SetOffRandom(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage, int times)
    {
        var combat = applier.CombatState;
        if (combat == null) return;

        for (var i = 0; i < times; i++)
        {
            var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
            if (candidates.Count == 0) return;
            var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target == null) return;

            await SetOff(choiceContext, target, applier, cardSource);
            await DealCardDamage(choiceContext, target, damage, cardSource, cardPlay);
        }
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
        // under Weak (or Strength, or Vulnerable) they are different.
        // PYRO, UNLESS A COVEN PERSONAL SAYS OTHERWISE (R236). Prune's
        // Hexhunter Chime is the one thing in either engine that moves rule 5's
        // element, and it moves it for ONE explosion; the call answers Pyro on
        // every other board and with the companion arm off. Sim twin:
        // `companion_coven.bomb_element`, read at `klee_overhaul._explode`.
        var element = await CompanionCovenBombs.ElementFor(choiceContext, applier);
        var dealt = await ElementalHit.Deal(
            choiceContext, target, element, size, applier);
        var reacted = ReactionEffects.TotalResolved > reactionsBefore;

        ledger.NoteExplosion(reacted, dealt);
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
        await SweepJumps(choiceContext, Applier.CombatState);
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
    /// charge's size to -- so Strength, Weak and the reaction all land on the
    /// echo exactly as they land on a Bomb going off, and the raw sum is what
    /// enters that pipeline in both cases.
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
