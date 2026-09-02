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
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE OVERHAUL'S BAKE-KURAGE (rules 1, 2 and 3 of the ruled brief's sec.4).
///
/// It is on the field for the whole combat, it holds <b>Tide</b>, the Tide
/// starts at 0 and NEVER resets on its own, her cards add to it, and a card
/// that says <i>Surge</i> makes it one Hydro hit for the whole number and then
/// the Tide is 0.
///
/// WHY THIS IS A SEPARATE POWER AND NOT A MODE ON <see cref="KurageSummonPower"/>.
/// The shipped jellyfish is a DURATION summon whose whole body is an automatic
/// end-of-turn pulse for <c>KuragePulseBase + KuragePulsePerCharge * Charge</c>,
/// and this arm retires both the Charge bank and that pulse. Teaching one type
/// to be both would put a runtime branch inside a hook that fires on every one
/// of her turns, in the file the Kurage's-memory arm is also live inside. A
/// second power costs one type and buys the acceptance condition outright:
/// under the flag no card summons a <see cref="KurageSummonPower"/>, so "no
/// Charge pulse of any kind" is a property of what is on the board rather than
/// of a branch somebody remembers. The shipped jellyfish is not edited by this
/// arm in any build.
///
/// THE AMOUNT IS A PRESENCE MARKER, NOT THE TIDE, and that is deliberate. A
/// <see cref="PowerStackType.Counter"/> at zero stacks is a power the game may
/// tear down, and rule 1 says the jellyfish is on the field for the WHOLE
/// combat -- including the opening turn, when the Tide is 0 and the badge must
/// still read "Tide 0". So <c>Amount</c> is pinned at 1 and the Tide lives in
/// <see cref="_tide"/>, surfaced through <see cref="DisplayAmount"/>. Same
/// split, and the same reason, as <c>ProtoBombPower</c>'s charge list.
///
/// IT ALSO HOSTS THE PLAN QUEUE'S RESOLUTION (rule 8), for a reason the Klee
/// arm could not use: <c>KleeOverhaulLedger</c>'s header explains that under
/// rule 7 there is no power guaranteed to be on Klee, so its turn boundary had
/// to roll on a round stamp. Here rule 1 GUARANTEES this power is on her for
/// every turn of every combat, so the turn-start hook the Plans need can hang
/// off it honestly. Which turn-start hook, and why it is not the one the slice
/// packet names, is on <see cref="AfterPlayerTurnStart"/>.
/// </summary>
public sealed class ProtoBakeKuragePower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// BaseLib's AddModelLoc keys off Id.Entry for any model implementing this
    /// interface, so the loc lives here and cannot drift from the id.
    ///
    /// THE BADGE IS THE TIDE (slice packet sec.5, last bullet: "Tide on the
    /// jellyfish"). Nothing new is drawn: this is the same
    /// <c>DisplayAmount</c> + <c>DynamicVar</c> rendering the shipped powers
    /// already use.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bake-Kurage"),
        ("description",
            "The jellyfish is on the field for the whole combat and holds "
          + "[gold]Tide[/gold]. Your cards add to it and it never resets on "
          + "its own. A card that says [gold]Surge[/gold] makes it deal the "
          + "whole [gold]Tide[/gold] as Hydro damage, and then the "
          + "[gold]Tide[/gold] is 0."),
        ("smartDescription",
            "[gold]Tide[/gold] {Tide}. A [gold]Surge[/gold] deals {Tide} Hydro "
          + "damage and leaves the [gold]Tide[/gold] at 0."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: the badge shows a number, not a countdown.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    private int _tide;

    /// <summary>The Tide this jellyfish is holding.</summary>
    public int Tide => _tide;

    /// <summary>The badge reads the Tide, which is what a Surge will deal --
    /// the shipped Bomb's ruling (2026-07-20) applied one character over: an
    /// on-field number reads as the damage it is about to become.</summary>
    public override int DisplayAmount => _tide;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new[] { new DynamicVar("Tide", 0m) };

    private void SyncDisplay()
    {
        var tide = DynamicVars["Tide"];
        tide.BaseValue = _tide;
        tide.ResetToBase();
        InvokeDisplayAmountChanged();
    }

    /// <summary>Rule 2, applied to this jellyfish. PURE.</summary>
    public void AddTide(int amount)
    {
        if (amount <= 0) return;
        _tide += amount;
        SyncDisplay();
    }

    /// <summary>
    /// Rule 3's first half: empty the Tide and hand back what it held. PURE,
    /// and take-then-resolve for the reason <c>ProtoBombPower.TakeAll</c> gives
    /// -- the number is off the power before anything that can kill runs, so a
    /// kill mid-hit cannot leave the badge showing a Tide that already went
    /// out.
    /// </summary>
    public int TakeTide()
    {
        var taken = _tide;
        _tide = 0;
        SyncDisplay();
        return taken;
    }

    /// <summary>
    /// RULE 8's resolution point: the Plans she wrote last turn happen at the
    /// START of this one.
    ///
    /// <c>AfterPlayerTurnStart</c>, AND NOT THE PRE-DRAW HOOK THE SLICE'S
    /// sec.5 ASKS FOR -- a reading, recorded here because the packet's own
    /// arithmetic is what settles it against its own wording.
    ///
    /// The game's turn-start order is fixed and written down
    /// (<c>tier0/tests/test_reaction_phase_parity.TURN_START_BROADCAST_ORDER</c>,
    /// read off the decompile): <c>BeforeSideTurnStart</c>, BLOCK CLEAR,
    /// <c>AfterBlockCleared</c>, ENERGY RESET, HAND DRAW,
    /// <c>AfterPlayerTurnStart</c>. There is NO broadcast between the energy
    /// reset and the draw. So a Plan resolved "before draw" resolves before the
    /// block clear and the energy reset too, and Read the Field's "Plan: gain 4
    /// Block" and Battle Plan's "Plan: gain 2 Energy" would both be wiped by
    /// the turn setup that follows them -- two of the eight Strategist cards,
    /// silently doing nothing.
    ///
    /// THE BRIEF'S OWN SCRIPTS REQUIRE THE LATER HOOK. Script C's turn 2
    /// "opens: Ambush fires (10 into a cultist), Battle Plan pays 2, Treatise
    /// draws 2. FIVE ENERGY, SEVEN CARDS" -- five is three plus the Plan's two,
    /// which is only true if the Plan lands after the reset; seven is five
    /// drawn plus Treatise's two, which is only true if the draw has happened.
    /// Sec.6.2 says the same thing in words: "before the hand is PLAYED".
    ///
    /// What the later hook costs is one turn's card ORDER: a Plan-drawn card
    /// arrives after the turn's five rather than before them. Nothing in the
    /// slice reads that difference.
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        await KokomiPlan.ResolveAll(choiceContext, Owner);
    }
}

/// <summary>
/// THE ARM'S FIVE VERBS, in one place: <b>Tide</b>, <b>Surge</b>, <b>Mend</b>,
/// <b>Exert</b>, and the jellyfish's own install.
///
/// EVERY CARD REACHES A RULE THROUGH EXACTLY ONE CALL HERE, which is the same
/// discipline <c>ProtoBombPower</c>'s static face keeps and for the same
/// reason: the rules live in one file, so a card cannot express a VARIANT of a
/// rule by being generated differently, and the entry-HP cap cannot be
/// forgotten at one call site out of four.
/// </summary>
public static class KokomiTide
{
    /// <summary>This creature's jellyfish, or null.</summary>
    public static ProtoBakeKuragePower? Kurage(Creature? kokomi) =>
        kokomi?.Powers.OfType<ProtoBakeKuragePower>().FirstOrDefault();

    /// <summary>The Tide she is holding. 0 with no jellyfish, which is the same
    /// answer and needs no special case.</summary>
    public static int Of(Creature? kokomi) => Kurage(kokomi)?.Tide ?? 0;

    /// <summary>
    /// RULE 1's install. Idempotent, and called from two places for the reason
    /// the Kurage's memory installs from two: the combat-start hook is the
    /// braces and the turn-start one is the belt, so a combat whose setup order
    /// ever moves still opens with a jellyfish rather than silently without
    /// one.
    /// </summary>
    public static async Task Install(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (Kurage(kokomi) != null) return;
        await PowerCmd.Apply<ProtoBakeKuragePower>(
            new ThrowingPlayerChoiceContext(), kokomi!, 1,
            applier: kokomi, cardSource: null, silent: true);
    }

    private static ICombatState? _combat;

    /// <summary>
    /// STASH ONLY, and it is the arrangement <c>KurageMemory.NoteCombat</c>
    /// already has for the same reason: <c>KokomiResourceHooks.Subscribe</c> is
    /// the one place the mod is handed a <c>CombatState</c>, but the game
    /// re-enumerates its hook listeners on EVERY hook broadcast, so that
    /// delegate is not a per-fight seam. The per-fight work is
    /// <see cref="InstallAll"/>'s, called from <c>BeforeCombatStart</c>.
    /// </summary>
    public static void NoteCombat(ICombatState? combat) => _combat = combat;

    /// <summary>Every seat in this combat opens with a jellyfish and a captured
    /// entry HP. Twin of <c>KurageMemory.InstallAll</c>, called from the same
    /// hook and for the same reason.</summary>
    public static async Task InstallAll()
    {
        var combat = _combat;
        if (combat == null) return;
        foreach (var player in combat.Players)
        {
            var creature = player.Creature;
            if (!KokomiOverhaul.LiveFor(creature)) continue;
            // ENTRY HP FIRST. The Mend cap is the HP she WALKED IN WITH
            // (brief sec.14), and this hook runs before the first turn opens,
            // so this is the only moment in the fight at which that number is
            // simply her current HP.
            KokomiOverhaulLedger.OpenCombat(creature!);
            await Install(creature);
        }
    }

    // ---- rule 2: Tide -----------------------------------------------------

    /// <summary>"Tide +N". Installs the jellyfish if it is somehow absent, so a
    /// feed card is never a dead draw.</summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature? kokomi, int amount)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || amount <= 0) return;
        await Install(kokomi);
        Kurage(kokomi)?.AddTide(amount);
    }

    /// <summary>
    /// RULE 7's landing site: Tide added from a SYNCHRONOUS chokepoint.
    ///
    /// <c>KokomiResourceHooks.TryModifyPowerAmountReceived</c> is the game's
    /// power-application hook and it is not async, so the Strength conversion
    /// cannot await an install. It does not need to: rule 1 puts the jellyfish
    /// on her before the first turn opens, so by the time any Strength can
    /// arrive there is always one to feed. With no jellyfish this is a no-op
    /// rather than a silent detour into some other bank -- the Strength is
    /// still refused either way, which is the half of rule 7 that must not
    /// depend on anything.
    /// </summary>
    public static void GainImmediate(Creature? kokomi, int amount)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || amount <= 0) return;
        Kurage(kokomi)?.AddTide(amount);
    }

    /// <summary>
    /// Deep Current's "Tide +1 per enemy hit", read off the play snapshot.
    ///
    /// THE SNAPSHOT AND NOT A LIVE COUNT, and the difference is the card: it
    /// deals its damage to EVERY enemy and then asks how many it hit, so an
    /// enemy the damage killed was still hit. <see cref="KokomiOverhaulLedger.BeginPlay"/>
    /// takes the count at the top of the body, before any effect resolves --
    /// the same place <c>KleeOverhaulLedger.BeginPlay</c> is emitted and for
    /// the same reason.
    /// </summary>
    public static async Task GainPerEnemyHit(
        PlayerChoiceContext choiceContext, Creature? kokomi, int per)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var hit = KokomiOverhaulLedger.For(kokomi!).EnemiesAtPlayStart;
        await Gain(choiceContext, kokomi, per * hit);
    }

    // ---- rule 3: Surge ----------------------------------------------------

    /// <summary>
    /// RULE 3. The jellyfish deals Hydro damage equal to the whole Tide to
    /// <paramref name="target"/>, and then the Tide is 0.
    ///
    /// TAKE-THEN-RESOLVE: the Tide leaves the jellyfish before the hit lands,
    /// so a reaction, a death or a listener firing inside the hit cannot spend
    /// it twice.
    ///
    /// THROUGH <see cref="ElementalHit"/>, which is what makes the Hydro half
    /// need no card text: the shared pipeline applies, refreshes or consumes
    /// the aura and pays out the reaction exactly as one of her Attacks would.
    /// A Surge on a 0 Tide is a legal, printed no-op -- it still counts as a
    /// Surge for rule 4, because the card said Surge and she chose to.
    /// </summary>
    public static async Task Surge(
        PlayerChoiceContext choiceContext, Creature? kokomi, Creature? target)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var kurage = Kurage(kokomi);
        if (kurage == null) return;

        var tide = kurage.TakeTide();
        // THE LATCH IS SET EVEN ON AN EMPTY SURGE. Rule 4 is "a turn in which
        // she did not Surge", not "a turn in which the Surge did something":
        // cashing nothing is still cashing, and the alternative would pay the
        // pulse for a wasted card.
        KokomiOverhaulLedger.For(kokomi!).NoteSurge(tide);
        if (tide <= 0 || target == null || target.IsDead) return;

        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro, tide, kokomi);
    }

    /// <summary>
    /// Undertow's second clause: "Gain Block equal to half the damage dealt."
    ///
    /// HALF THE TIDE THAT WENT OUT, rounded down. "The damage dealt" is the
    /// Surge's own printed quantity -- rule 3 says it deals damage EQUAL TO THE
    /// TIDE -- and it is read off the ledger because the jellyfish is empty by
    /// the time this clause asks. It deliberately does not read the number that
    /// finally landed on the enemy: that one has been through the shared
    /// elemental pipeline's amplifier and the target's own Vulnerable, and
    /// neither of those is a fact about her Tide.
    /// </summary>
    public static async Task BlockHalfSurge(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var block = KokomiOverhaulLedger.For(kokomi!).SurgeDamageThisPlay / 2;
        if (block <= 0) return;
        // Power-sourced Block is RAW (NC-11, R116): Unpowered, so neither
        // Frail nor Dexterity sees it. The same line the Garment's rider takes.
        await CreatureCmd.GainBlock(kokomi!, block, ValueProp.Unpowered, null);
    }

    /// <summary>Reading the Tide: "Draw 1 card per 5 Tide." A READ, not a
    /// spend -- the card says nothing about the Tide going down.</summary>
    public static async Task DrawPerTide(
        PlayerChoiceContext choiceContext, Creature? kokomi, int cards, int per)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || per <= 0) return;
        var player = kokomi!.Player;
        if (player == null) return;
        var draws = cards * (Of(kokomi) / per);
        if (draws <= 0) return;
        await CardPileCmd.Draw(choiceContext, draws, player);
    }

    // ---- rule 5: Exert ----------------------------------------------------

    /// <summary>
    /// RULE 5. "Lose N HP, taken from Block first."
    ///
    /// IT IS DAMAGE AND NOT AN HP LOSS, and that one word is the whole rule.
    /// The mod's shipped self-cost (<c>{op: damage, target: self}</c>, Hot
    /// Hands) is <c>Unblockable | Unpowered</c>, which is how the base game
    /// models an HP cost -- it walks past Block on purpose. Exert must NOT:
    /// the brief's contested thing is that "a Block card is worth two things
    /// and she picks which", so Block has to be able to eat it. Dropping
    /// <c>Unblockable</c> is what makes Block fuel.
    ///
    /// <c>Unpowered</c> stays. This is a cost she pays, not an attack anyone
    /// made, so no Strength, no Vulnerable and no attack hook sees it.
    ///
    /// IT CAN KILL HER, "the way Tackle can" (slice sec.5), and there is no
    /// guard here saying otherwise. That is a default for the Balance stage to
    /// revisit, named in the packet.
    /// </summary>
    public static async Task Exert(
        PlayerChoiceContext choiceContext, Creature? kokomi, int amount,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || amount <= 0) return;
        await CreatureCmd.Damage(
            choiceContext, kokomi!, amount, ValueProp.Unpowered,
            dealer: null, cardSource: cardSource, cardPlay: cardPlay);
    }

    // ---- the Mend rule ----------------------------------------------------

    /// <summary>
    /// MEND: heal, never above entry HP. Returns the HP that actually landed,
    /// which is what the pulse's per-combat budget is measured in.
    ///
    /// ONE FUNCTION, and every Mend in the arm goes through it -- the pulse,
    /// the Garment, three cards and a Plan -- because "never above entry HP" is
    /// the rule that makes the whole healing bound work (brief sec.10, the
    /// first named failure mode) and a second implementation of it is how the
    /// bound would eventually come off one of them.
    ///
    /// SANGO ISSHIN IS RESOLVED HERE for the same reason: it is the one Rare
    /// that touches the cap ("Mend that would go past your entry HP becomes
    /// Hydro damage to a random enemy"), so it has to sit exactly where the cap
    /// is applied or the two would eventually disagree about what "past" means.
    /// With the power absent the excess is simply lost, which is what the cap
    /// has always meant.
    /// </summary>
    public static async Task<int> Mend(
        PlayerChoiceContext choiceContext, Creature? kokomi, int amount)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || amount <= 0) return 0;

        var entry = KokomiOverhaulLedger.For(kokomi!).EntryHp;
        var room = entry - (int)kokomi!.CurrentHp;
        var landed = room > 0 ? System.Math.Min(amount, room) : 0;
        var excess = amount - landed;

        if (landed > 0)
        {
            await CreatureCmd.Heal(kokomi, landed);
        }

        if (excess > 0 && kokomi.Powers.OfType<SangoIsshinPower>().Any())
        {
            await SangoIsshinPower.Overflow(choiceContext, kokomi, excess);
        }

        return landed;
    }
}
