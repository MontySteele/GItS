using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Cards.Kokomi.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE KURAGE'S MEMORY, v3 -- the C# half of the rule the sim carries behind
/// <c>tier0/constants.py C.KURAGE_MEMORY</c>. Spec:
/// <c>review/active/kokomi-kurage-memory-2026-08-29.md</c> §11, whose §11.1 is
/// [USER]'s words and IS the spec. Every behaviour here mirrors
/// <c>tier0/engine/effects.py</c>; no rule is re-derived C#-side.
///
/// THE QUARANTINE. This whole directory is <c>Compile Remove</c>d unless
/// <c>-p:PrototypeCards=true</c> (KleeCode.csproj), which is the same switch
/// that defines <c>PROTOTYPE_CARDS</c> and makes a dev deploy stamp
/// <c>+proto</c>. A release build contains no type from this file and every
/// seam that calls into it is itself inside <c>#if PROTOTYPE_CARDS</c>, so the
/// targeted revert is the flag and nothing else. The sim's own master flag,
/// <c>C.KURAGE_MEMORY</c>, is that compile switch's twin: default off, one
/// line to flip, nothing reachable behind it.
///
/// TWO ENTRY RULES, AND THEY ARE INDEPENDENT ([USER]: "Those should be
/// independent mechanics"). <see cref="NoteMuster"/> and
/// <see cref="NoteExhaust"/> never mention each other and neither reads what
/// the other did; what they SHARE is the refusal list, and that lives in the
/// one enrolment door <see cref="Enrol"/> so there is one list rather than two
/// that drift. One Muster whose recruit later Exhausts therefore yields TWO
/// entries, in order, and that is ruled intended.
///
/// SCOPE IS PER FIGHT. Everything below is keyed off the Player and cleared by
/// <see cref="ResetForCombat"/>, called from
/// <c>KokomiResourceHooks.Subscribe</c> -- the sim gets this for free because
/// <c>CombatState</c> is rebuilt by <c>run_fight</c>; the mod's hook models are
/// singletons and have to be told.
/// </summary>
public static class KurageMemory
{
    // ---------------------------------------------------------------- law --

    /// <summary>
    /// TRANSCRIPTION SURFACE, same rule as <see cref="KokomiConstants"/>:
    /// every number is copied from tier0 by value and none is re-derived here.
    /// <c>tools/lint_constant_parity.py</c> holds the numeric rows.
    ///
    /// | C# constant   | sim source                                  |
    /// |---------------|---------------------------------------------|
    /// | CostPerEnergy | constants.py KURAGE_MEMORY_COST_PER_ENERGY=3 |
    /// | PulseBlock    | constants.py KURAGE_MEMORY_PULSE_BLOCK = 5   |
    /// | QueueCap      | constants.py KURAGE_QUEUE_CAP = 0 (uncapped) |
    ///
    /// The string/bool rows below are MODE selectors, not balance numbers, and
    /// carry their sim spelling verbatim so a sweep is a one-word edit on both
    /// sides.
    /// </summary>
    public static class KurageMemoryLaw
    {
        /// <summary>[USER], §11.1: "cards cost Charge equal to 3x their Cost".</summary>
        public const int CostPerEnergy = 3;

        /// <summary>
        /// The SKILL branch of the pulse, RULED at 5 by [USER] 2026-08-29 on
        /// its own constant. NOT <see cref="KokomiConstants.KuragePulseBlock"/>,
        /// which ships at 0 and must stay reachable byte-for-byte with the
        /// flag off. The Oath's ward still stacks on top.
        /// </summary>
        public const int PulseBlock = 5;

        /// <summary>0 = UNCAPPED. [USER]: "I don't think we need to cap this."</summary>
        public const int QueueCap = 0;

        /// <summary>
        /// "remembered_face" is the ONE basis v3 keeps: the printed cost of the
        /// card that ENTERED, as that instance reads it. Permanent upgrade
        /// changes count; temporary combat discounts do not.
        /// </summary>
        public static readonly string CostBasis = "remembered_face";

        /// <summary>
        /// "random" (v3 default) leaves the game's own forced-random roll in
        /// charge -- <c>CardCmd.AutoPlay</c> rolls it when the target is null,
        /// which is exactly the sim's `None`. "most_hp" is v2's PICK E1
        /// fallback, implemented so the arm can be swept.
        /// </summary>
        public static readonly string TargetFallback = "random";

        /// <summary>[USER], §11.1: "At the start of Kokomi's turn". "turn_end"
        /// is implemented so the arm can be swept.</summary>
        public static readonly string FireTiming = "turn_start";

        /// <summary>
        /// The Power branch pays CHARGE, not Hydro ([USER]: "Sacrificing a
        /// power seems like a bigger deal than sacrificing anything else").
        /// The AMOUNT is DERIVED, not picked (R212): it is
        /// <see cref="KokomiConstants.ChargePerExhaust"/> -- a Power pulse is
        /// worth exactly one burnt card. "hydro" is v2's PICK C1, implemented.
        /// </summary>
        public static readonly string PowerPulse = "charge";

        /// <summary>
        /// NOT A [USER] PICK -- §11.6 item 2, a hole the build filled, and it
        /// goes back to [USER]. True: the acceleration keyword still needs a
        /// jellyfish on the field (one rule for what may act on the memory).
        ///
        /// SUPERSEDED IN SPIRIT by [USER]'s 2026-08-29 ruling that the
        /// Bake-Kurage becomes base kit and is ALWAYS on: when the jellyfish
        /// cannot be absent, this constant and every duration question stop
        /// having a case. Mirrored minimally as v3 has it and nothing new is
        /// built around it; the always-on swap is <see cref="SummonIsFielded"/>
        /// and nothing else.
        /// </summary>
        public static readonly bool KeywordNeedsSummon = true;

        /// <summary>
        /// v4 BASE KIT ([USER], 2026-08-29): "I think that we will want to
        /// make Bake-Kurage part of the base kit (always on) rather than a
        /// separate card. So yes, we could add one Muster card to the base
        /// deck to teach the pattern." Mirrors <c>C.KURAGE_ALWAYS_ON</c>, and
        /// is READ ONLY UNDER the memory quarantine, exactly as in the sim.
        ///
        /// True: the jellyfish is installed at the start of every one of her
        /// combats and holds the whole fight -- no duration, no expiry, no
        /// summon needed -- and her starter deck trades Bake-Kurage for one
        /// Muster ("To the Front!"), so RULE 1 is printed in fight 1 instead
        /// of drafted. False leaves the v3 arm reachable whole, which is why
        /// this is a separate switch and not an edit to the v3 code.
        ///
        /// A `bool` rather than an `int`, so `lint_constant_parity` does not
        /// scan it: it selects a shape, it is not a balance number. Its sim
        /// twin is named above and the two must move together.
        /// </summary>
        public static readonly bool AlwaysOn = true;
    }

    // -------------------------------------------------------------- state --

    /// <summary>ONE entry in the memory. Mirrors <c>state.KurageMemory</c>.</summary>
    public sealed class Entry
    {
        /// <summary>
        /// The remembered INSTANCE, kept rather than an id.
        ///
        /// DELIBERATE DIVERGENCE FROM THE SIM, and it is the more exact half:
        /// tier0 stores `card_id` and re-materialises through
        /// <c>loader.get_card</c> because a python Card is data. Here the
        /// instance already carries the upgrade level, the permanent cost and
        /// the keywords the face entered with, and
        /// <c>ICombatState.CloneCard</c> reproduces all three at fire time. An
        /// id round-trip would have to rebuild them from scratch and would
        /// lose a Muster recruit's discount.
        /// </summary>
        public required CardModel Card { get; init; }

        /// <summary>The printed title at entry -- what the strip draws.</summary>
        public required string Name { get; init; }

        /// <summary>The remembered face's own cost (permanent upgrades in,
        /// temporary discounts out).</summary>
        public required int Cost { get; init; }

        /// <summary>3 x <see cref="Cost"/>, computed ONCE at entry so the strip
        /// can show it for as long as the memory is queued.</summary>
        public required int Price { get; init; }

        /// <summary>The body the original was played against, or null. Null is
        /// the honest answer for a card that was never played -- a Muster's
        /// sacrifice, an Ethereal burn, a hand-Exhaust.</summary>
        public required Creature? Target { get; init; }

        /// <summary>The original did NOT print Exhaust. RECORDED AND
        /// BEHAVIOUR-FREE, exactly as in the sim: every copy is removed from
        /// combat, so there is no second lifecycle for this to select. Kept
        /// because it is what the strip must show and what a later ruling would
        /// attach behaviour to. §11.6 item 1: THIS GOES BACK TO [USER].</summary>
        public required bool Ephemeral { get; init; }

        /// <summary>"muster" or "exhaust" -- which rule filed it.</summary>
        public required string Rule { get; init; }
    }

    private static readonly Dictionary<Player, List<Entry>> Queues = new();
    private static readonly HashSet<CardModel> EnrolledCards = new();
    private static readonly HashSet<CardModel> MemoryCopies = new();
    private static readonly Dictionary<CardModel, Creature?> PlayTargets = new();
    private static readonly Dictionary<CardModel, int> MusterFaceCost = new();
    private static readonly Dictionary<Player, CardType> LastCardType = new();
    private static readonly HashSet<Player> PlayedAnything = new();
    private static readonly Dictionary<Player, Creature?> LastAttackTarget = new();
    private static readonly HashSet<Player> FiredThisTurn = new();

    /// <summary>True for exactly the duration of a jellyfish auto-play.
    /// RECURSION RULE 2 reads it: a replayed card is not "the last card Kokomi
    /// played", so a copy cannot key or overwrite the pulse.</summary>
    public static bool Autoplaying { get; private set; }

    /// <summary>
    /// Per-fight reset. The sim gets this free (CombatState is rebuilt); the
    /// mod's hook models are singletons, so the clear is explicit.
    /// </summary>
    public static void ResetForCombat()
    {
        Queues.Clear();
        EnrolledCards.Clear();
        MemoryCopies.Clear();
        PlayTargets.Clear();
        MusterFaceCost.Clear();
        LastCardType.Clear();
        PlayedAnything.Clear();
        LastAttackTarget.Clear();
        FiredThisTurn.Clear();
        Autoplaying = false;
    }

    /// <summary>The one gate: the player IS Kokomi. (The FLAG is the compile
    /// switch -- this file does not exist in a release build.)</summary>
    public static bool IsLive(Creature? creature) =>
        KokomiResources.IsKokomi(creature);

    /// <summary>
    /// THE ONE "is the jellyfish here" PREDICATE, and deliberately the only
    /// one: the fire, the keyword door and the strip all ask it, so [USER]'s
    /// 2026-08-29 ruling that the Bake-Kurage becomes base kit (always on) is
    /// a change to THIS METHOD and to nothing else -- not the rule body, not
    /// the strip. Today it is the shipped summon power's presence.
    /// </summary>
    public static bool SummonIsFielded(Creature? creature) =>
        creature?.Powers.OfType<KurageSummonPower>().Any() ?? false;

    /// <summary>
    /// sec.12.6 ITEMS 5 AND 6 -- THE STARTER SWAP, AND IT IS ONE SEAM.
    ///
    /// Slot 11 of her authored starting deck. With the base kit on it is
    /// "To the Front!"; otherwise it is Bake-Kurage, byte for byte what ships.
    ///
    /// [USER], 2026-08-29: "we could add one Muster card to the base deck to
    /// teach the pattern." A card that summons what is always on the field is
    /// a card that does nothing, so Bake-Kurage leaves; one Muster takes the
    /// slot, so RULE 1 -- the card you sacrifice to a Muster enters the
    /// memory, priced at three times its cost -- is something she meets in
    /// fight 1 rather than something she has to draft into. ONE CARD FOR ONE
    /// CARD: the deck is still twelve, which is what keeps this a substitution
    /// and not a starter rework.
    ///
    /// "To the Front!" and not one of the other three Musters: it is 0 energy
    /// with one Muster and nothing else printed, so what the player learns is
    /// the RULE and not a rider, and at 0 cost it can be played on any turn of
    /// any hand. sec.12.3 lists the three that lost and why.
    ///
    /// ITEM 6 -- THE PRINTED SHEET DOES NOT MOVE. `docs/kokomi-cards.yaml`
    /// still says Bake-Kurage and the generated card row is untouched; only
    /// this list moves, and only under the flag. Sim twin, and the same
    /// argument for the same reason: `loader._starter_ids`.
    ///
    /// ITEM 5's OTHER HALF -- the support-Companion roll still composes. That
    /// roll (`KleeStartingCompanionsPatch.ResolveKokomi`) replaces Sayu in
    /// slot 10 and never looks at slot 11, so the two are independent by
    /// construction rather than by ordering luck.
    /// </summary>
    public static CardModel StarterSlotEleven() =>
        KurageMemoryLaw.AlwaysOn
            ? ModelDb.Card<ToTheFront>()
            : ModelDb.Card<BakeKurage>();

    /// <summary>Is the BASE KIT live for this creature? The memory rule, plus
    /// v4's always-on switch, plus her identity.</summary>
    public static bool BaseKitLive(Creature? creature) =>
        KurageMemoryLaw.AlwaysOn && IsLive(creature);

    /// <summary>
    /// sec.12.6 ITEM 1 -- INSTALL THE JELLYFISH AT COMBAT START, not on a card.
    ///
    /// Mirror of the sim's `combat.run_fight`, which puts `kurage_summon` on
    /// the player beside the per-combat Charge reset because the two now have
    /// the same lifetime: one fight. It must be on the field before the first
    /// turn opens and it is never removed.
    ///
    /// ITEM 4 -- ITS OWN SIGNAL, NOT A SUMMON. This deliberately does NOT call
    /// <see cref="KurageSummon.Field"/>: nothing summoned it, no card paid for
    /// it, and a listener counting summons (the play telemetry, a future
    /// on-summon rider) must not see one. `PowerCmd.Apply` is the game's own
    /// application path and is what the field call would have reached anyway;
    /// what is skipped is the mod's summon WRAPPER and the meaning it carries.
    /// The sim's twin emits `kurage_base_kit`, not `summon_kurage`.
    ///
    /// ITEM 2 -- NEVER EXPIRES. Nothing here starts a countdown, and the
    /// memory branch of <see cref="KurageSummonPower.FirePulse"/> never
    /// reaches `TickDownDuration`. The amount is 1 because stacks ARE turns in
    /// the shipped grammar and one is all a thing that never ticks needs.
    ///
    /// IDEMPOTENT, and that is load-bearing: it is called from the
    /// creature-entered-combat hook AND, as a belt, at her turn start, so a
    /// combat whose setup order ever changes still opens with the jellyfish
    /// rather than silently without it.
    ///
    /// The context: `ThrowingPlayerChoiceContext` is the game's own "quite
    /// certain no player choice occurs deeper in this callstack" context --
    /// what `PowerCmd.Decrement` passes -- and applying a power with no
    /// applier opens none. If one ever did, the throw lands in the log, which
    /// is louder and more useful than a board silently missing a jellyfish.
    /// </summary>
    public static async Task Install(Creature? creature)
    {
        if (!BaseKitLive(creature)) return;
        if (SummonIsFielded(creature)) return;          // already installed
        await PowerCmd.Apply<KurageSummonPower>(
            new ThrowingPlayerChoiceContext(), creature!, 1,
            applier: creature, cardSource: null, silent: true);
    }

    /// <summary>Is this card instance a memory copy? Read by the exhaust
    /// funnel's belt clause, which must not mint Charge for a card that was
    /// never burned.</summary>
    public static bool IsCopy(CardModel card) => MemoryCopies.Contains(card);

    /// <summary>The queue, front first. Never null.</summary>
    public static IReadOnlyList<Entry> Queue(Player? player) =>
        player != null && Queues.TryGetValue(player, out var q)
            ? q
            : (IReadOnlyList<Entry>)System.Array.Empty<Entry>();

    // -------------------------------------------------------------- price --

    /// <summary>
    /// The remembered face's own cost. Permanent upgrade changes count;
    /// TEMPORARY combat discounts do not.
    ///
    /// <c>GetWithModifiers(CostModifiers.None)</c> is the exact reading:
    /// <c>CardEnergyCost._base</c>, which <c>UpgradeBy</c> moves and every
    /// discount (<c>SetThisTurn</c>, <c>AddThisCombat</c>, the global hook)
    /// leaves alone. The sim spells the same thing "read the CARD, never
    /// combat.card_cost".
    ///
    /// THE ONE EXCEPTION IS A MUSTER RECRUIT. tier0's <c>_op_conscript</c>
    /// writes <c>recruit.cost</c> permanently; the mod applies the same -1 as
    /// <c>EnergyCost.AddThisCombat</c>, because CardModel has no settable base
    /// cost. Rather than change the shipped Muster, the recruit's intended face
    /// cost is stamped at the transformation (<see cref="NoteMusterRecruit"/>)
    /// and read back here -- so §11.4's "a Muster's own -1 counts on the
    /// RECRUIT's own entry" holds on both engines.
    /// </summary>
    public static int FaceCost(CardModel card) =>
        MusterFaceCost.TryGetValue(card, out var stamped)
            ? stamped
            : card.EnergyCost.GetWithModifiers(CostModifiers.None);

    /// <summary>
    /// 3 x the face's cost, or null for a face that cannot be priced.
    ///
    /// X-COST IS INELIGIBLE FOR NOW (the advisor's rule statement, ratified as
    /// the design): "X" has no cost to multiply, and pricing it off the energy
    /// the original captured would make one memory's price depend on a turn
    /// that is over.
    /// </summary>
    public static int? Price(CardModel card)
    {
        if (card.EnergyCost.CostsX) return null;
        return System.Math.Max(0, FaceCost(card)) * KurageMemoryLaw.CostPerEnergy;
    }

    // ------------------------------------------------- the enrolment door --

    /// <summary>
    /// THE ONE WRITER OF THE QUEUE. Both entry rules end here.
    ///
    /// The rules themselves are independent and neither reads the other; what
    /// they SHARE is the set of things that can never enter:
    ///   * a card that has already enrolled (the general once-only guard, and
    ///     the only one v3 keeps);
    ///   * a MEMORY COPY, ever, by either rule (recursion rule 1);
    ///   * a Status or a Curse -- the rotation ruling that governs the Charge
    ///     funnel governs the memory too;
    ///   * an X-cost card, which has no price.
    /// </summary>
    private static bool Enrol(Player? owner, CardModel card, Creature? target,
                              string rule)
    {
        if (owner == null) return false;
        if (EnrolledCards.Contains(card) || MemoryCopies.Contains(card)) return false;
        if (KokomiResources.IsJunk(card)) return false;
        var price = Price(card);
        if (price == null) return false;                    // X-cost: refused

        var queue = Queues.TryGetValue(owner, out var existing)
            ? existing
            : Queues[owner] = new List<Entry>();
        if (KurageMemoryLaw.QueueCap > 0 && queue.Count >= KurageMemoryLaw.QueueCap) return false;

        EnrolledCards.Add(card);
        queue.Add(new Entry
        {
            Card = card,
            Name = SafeTitle(card),
            Cost = FaceCost(card),
            Price = price.Value,
            Target = target,
            // "the original did not print Exhaust" -- the instance-level
            // ExhaustOnNextPlay counts, which is how a Muster recruit reads as
            // an Exhaust card without printing the keyword.
            Ephemeral = !card.Keywords.Contains(CardKeyword.Exhaust)
                        && !card.ExhaustOnNextPlay,
            Rule = rule,
        });
        RefreshStrip(owner.Creature);
        return true;
    }

    private static string SafeTitle(CardModel card)
    {
        try { return card.Title; }
        catch { return card.Id.Entry; }
    }

    // ------------------------------------------------------------- rule 1 --

    /// <summary>
    /// RULE 1 -- MUSTER. Called from <c>KokomiConscript</c> with the
    /// SACRIFICED card, at the moment it is consumed.
    ///
    /// [USER], 2026-08-29: "We would be adding the card that was sacrificed for
    /// the Muster, not the new card - so the original face."
    ///
    /// It does not care what the Muster produced or what becomes of it. That is
    /// why this method does not mention Companions, Exhaust, or Rule 2. The
    /// sacrifice is usually one of her own NON-Companion cards, so the memory
    /// holds non-Companion cards under v3 and replays them by the same rules.
    /// It was never played, so it stores NO target.
    ///
    /// Create-mode conscription sacrifices nothing and never reaches here,
    /// which is the correct reading: no sacrifice, no memory.
    /// </summary>
    public static void NoteMuster(Player? owner, CardModel sacrificed)
    {
        if (!IsLive(owner?.Creature)) return;
        Enrol(owner, sacrificed, null, "muster");
    }

    /// <summary>
    /// The recruit's intended face cost, stamped at the transformation so
    /// <see cref="FaceCost"/> can read a permanent discount the mod applies as
    /// a combat modifier. See <see cref="FaceCost"/> for why this exists.
    /// Not an entry rule and not a queue write: bookkeeping only.
    /// </summary>
    public static void NoteMusterRecruit(Player? owner, CardModel recruit,
                                         int faceCost)
    {
        if (!IsLive(owner?.Creature)) return;
        MusterFaceCost[recruit] = System.Math.Max(0, faceCost);
    }

    // ------------------------------------------------------------- rule 2 --

    /// <summary>
    /// RULE 2 -- EXHAUST. Called from <c>KokomiResourceHooks.AfterCardExhausted</c>,
    /// the one funnel every exhaust route passes through -- which is what makes
    /// this structural rather than per-site discipline, the same argument that
    /// put the Charge accrual there.
    ///
    /// The advisor's rule statement, ratified by [USER] as the design: "When a
    /// Companion not originating from Memory Exhausts, remember it." HOWEVER IT
    /// CAME TO EXIST: drafted, Mustered or created. A Muster's recruit gains
    /// Exhaust, so it enrols here on its own face when it burns -- a SECOND
    /// memory from one Muster, and [USER] ruled that intended.
    ///
    /// A Companion that does NOT print Exhaust never reaches here on its own;
    /// the player has to burn it by hand (or by Ethereal), which is the synergy
    /// space [USER] named for the Exhaust and Ethereal tags.
    ///
    /// OUTSIDE THE RELIC GATE, deliberately, exactly as the sim has it: the
    /// memory belongs to the jellyfish, not to the Tamakushi Casket.
    /// </summary>
    public static void NoteExhaust(CardModel card)
    {
        var owner = card.Owner;
        if (!IsLive(owner?.Creature)) return;
        if (card is not ICompanionCard) return;
        PlayTargets.TryGetValue(card, out var target);
        Enrol(owner, card, target, "exhaust");
    }

    // --------------------------------------------------------------- play --

    /// <summary>
    /// The per-card target record. Written at the BIND -- before the card can
    /// reach the exhaust funnel -- so a card that enters the memory after a
    /// play carries the body it hit. tier0 writes the same dictionary in
    /// <c>effects.resolve_card</c>; the mod's earliest site carrying a
    /// resolved Target is <c>BeforeCardPlayed</c>, and it is strictly before
    /// the result-pile move that exhausts, which is what the sim's ordering
    /// guarantees too.
    /// </summary>
    public static void NoteBind(CardPlay cardPlay)
    {
        if (!IsLive(cardPlay.Card.Owner?.Creature)) return;
        PlayTargets[cardPlay.Card] = cardPlay.Target;
    }

    /// <summary>
    /// THE PULSE KEY. Set for EVERY card she plays, Companion or not: the
    /// branch is on card TYPE, and a Companion is a Skill like any other.
    ///
    /// RECURSION RULE 2 is the <see cref="Autoplaying"/> guard and not
    /// <c>cardPlay.IsAutoPlay</c>: Havoc and Cascade auto-play HER cards and
    /// those DO key the pulse in the sim (they run through the same
    /// <c>_finish_play</c>); only the jellyfish's own replay does not.
    /// </summary>
    public static void NotePlay(CardPlay cardPlay)
    {
        var owner = cardPlay.Card.Owner;
        if (owner == null || !IsLive(owner.Creature) || Autoplaying) return;
        LastCardType[owner] = cardPlay.Card.Type;
        PlayedAnything.Add(owner);
        if (cardPlay.Card.Type == CardType.Attack && cardPlay.Target != null)
        {
            LastAttackTarget[owner] = cardPlay.Target;
        }
    }

    // ---------------------------------------------------------------- aim --

    /// <summary>
    /// v3's targeting rule, [USER]'s sentence almost verbatim: "Cards must play
    /// against the same target the second time, unless that target no longer
    /// exists, in which case they play randomly against eligible targets."
    ///
    /// The stored body whenever it is still alive. Otherwise the fallback, and
    /// the default fallback is RANDOM -- expressed as null, which leaves
    /// <c>CardCmd.AutoPlay</c>'s own forced-random roll in charge rather than
    /// rolling a second stream here. A memory with NO stored target takes the
    /// fallback by the same line: absence and death are the same thing to a
    /// card that has to aim at something.
    /// </summary>
    private static Creature? Aim(ICombatState combat, Entry entry)
    {
        if (entry.Target is { IsAlive: true } stored
            && combat.HittableEnemies.Contains(stored))
        {
            return stored;
        }
        if (KurageMemoryLaw.TargetFallback == "most_hp")
        {
            return combat.HittableEnemies
                .OrderByDescending(e => e.CurrentHp)
                .FirstOrDefault();
        }
        return null;
    }

    /// <summary>
    /// The PULSE's aim, and v2's PICK E in its remaining job:
    /// <c>KURAGE_TARGET_RULE = "follow_her_last_attack"</c> aims at the enemy
    /// her own last attack was bound to, or, if that enemy is dead, the enemy
    /// with the MOST current HP. v3 took the REPLAY's aim away from this.
    /// </summary>
    private static Creature? PulseTarget(ICombatState combat, Player owner)
    {
        var living = combat.HittableEnemies;
        if (living.Count == 0) return null;
        if (LastAttackTarget.TryGetValue(owner, out var led)
            && led is { IsAlive: true } && living.Contains(led))
        {
            return led;
        }
        return living.OrderByDescending(e => e.CurrentHp).FirstOrDefault();
    }

    // --------------------------------------------------------------- fire --

    /// <summary>Clears the once-per-turn latch. Called at her turn start,
    /// before <see cref="Fire"/>.</summary>
    public static void OpenTurn(Player? player)
    {
        if (player != null) FiredThisTurn.Remove(player);
        if (player != null) PlayedAnything.Remove(player);
        if (player != null) LastCardType.Remove(player);
    }

    /// <summary>
    /// THE FIRE: the jellyfish plays the FRONT of its memory for 0 energy and
    /// the bank pays that memory's own price.
    ///
    /// [USER], §11.1: "At the start of Kokomi's turn, if she can afford the
    /// front Memory, spend its Charge cost and play it. Then remove that Memory
    /// from combat."
    ///
    /// THE BLOCK is [USER]'s own clause and the reason this returns before
    /// touching anything behind the front: "Sticking a card you can't afford
    /// into Memory blocks Memory until it's played." Nothing behind an
    /// unaffordable front fires, and the bank HOLDS -- it is not spent down on
    /// something cheaper and it is not lost. Distinct from an EMPTY memory,
    /// which also pays nothing but is not a block.
    ///
    /// ONE CARD PER TURN, MAXIMUM: "If you stack infinite Charge, then you
    /// still get only one play per turn." A TURN boundary, not a bank size.
    ///
    /// <paramref name="manual"/> is the acceleration keyword's door (the
    /// provisional keyword "Stir"). It neither reads nor sets the per-turn
    /// latch -- that is the whole point of an accelerator -- and it still pays
    /// the price, because the keyword buys RHYTHM and never the card.
    ///
    /// The play goes through <c>CardCmd.AutoPlay</c>, the game's own free-play
    /// door, so a copy fires the real card-played hooks and every ordinary
    /// "when you play a Companion" effect -- exactly as the rule statement
    /// requires. It is the twin of tier0's <c>combat.resolve_free_play</c>.
    /// </summary>
    public static async Task<bool> Fire(PlayerChoiceContext choiceContext,
                                        Player? player, bool manual = false)
    {
        var creature = player?.Creature;
        if (player == null || !IsLive(creature)) return false;
        if (!manual && FiredThisTurn.Contains(player)) return false;
        if ((!manual || KurageMemoryLaw.KeywordNeedsSummon) && !SummonIsFielded(creature))
        {
            // No jellyfish on the field, no memory to fire from. The queue
            // still FILLS without one: the memory is of what she burned, and
            // the summon is what acts on it.
            return false;
        }
        if (creature!.CombatState is not { } combat) return false;

        var queue = Queues.TryGetValue(player, out var q) ? q : null;
        // KURAGE_EMPTY_QUEUE "hold": nothing fires and NOTHING IS PAID. The
        // punishment for an empty memory is tempo, never deletion.
        if (queue == null || queue.Count == 0) return false;

        var entry = queue[0];
        // THE BLOCK.
        if (KokomiResources.GetCharge(creature) < entry.Price) return false;
        if (entry.Price > 0
            && !await KokomiResources.SpendCharge(
                choiceContext, creature, entry.Price, null))
        {
            return false;                 // cannot happen; the bank was checked
        }

        queue.RemoveAt(0);
        if (!manual) FiredThisTurn.Add(player);

        var copy = combat.CloneCard(entry.Card);
        MemoryCopies.Add(copy);
        // The copy is NOT AN EXHAUST EVENT (see the removal below): clearing
        // the flag here is what makes that true at the game's own pile rule
        // rather than by a special case inside the funnel. The sim writes
        // `token.exhaust = False` on the same line of reasoning.
        copy.ExhaustOnNextPlay = false;
        CardCmd.RemoveKeyword(copy, CardKeyword.Exhaust);

        var aim = Aim(combat, entry);
        var previous = Autoplaying;
        Autoplaying = true;
        try
        {
            await CardCmd.AutoPlay(choiceContext, copy, aim);
        }
        finally
        {
            Autoplaying = previous;
            // EVERY copy is removed from combat and reaches no pile. The rule
            // statement ends "Then remove that Memory from combat", and that is
            // taken literally for both kinds. The alternative for a copy whose
            // original DID print Exhaust is that it Exhausts again -- and an
            // Exhaust pays Charge, which the same statement forbids. One
            // removal rather than two lifecycles. `ephemeral` is recorded and
            // behaviour-free for exactly this reason (§11.6 item 1).
            await CardPileCmd.RemoveFromCombat(copy);
            MemoryCopies.Remove(copy);
            RefreshStrip(creature);
        }
        return true;
    }

    /// <summary>
    /// THE ACCELERATION KEYWORD'S HOOK -- provisional name "Stir" (R179: an
    /// ordinary word, cosmetic, renameable for free). NO CARD PRINTS IT. It
    /// exists so codegen has a door to emit against, the way the sim registers
    /// the <c>play_front_memory</c> op with no sheet row: [USER] and the
    /// advisor both prefer explicit Skills that say "Play the front Memory"
    /// over a passive rate Power.
    ///
    /// <paramref name="amount"/> fires the front that many times, stopping at
    /// the first refusal (an empty or blocked memory, or a bank that cannot pay
    /// the next front).
    /// </summary>
    public static async Task PlayFrontMemory(PlayerChoiceContext choiceContext,
                                             Player? player, int amount)
    {
        for (var i = 0; i < amount; i++)
        {
            if (!await Fire(choiceContext, player, manual: true)) return;
        }
    }

    // -------------------------------------------------------------- pulse --

    /// <summary>
    /// The rewritten turn-end pulse: keyed to the TYPE of the last card KOKOMI
    /// HERSELF played this turn, and reading the bank not at all. The
    /// per-Charge term is gone, and with it the multiplier the playtest named
    /// as the "100+ hit".
    ///
    /// NO CARD PLAYED -> NO PULSE ("a price on a wasted turn rather than a free
    /// tick").
    ///
    /// The summon is PERSISTENT under the flag, so this never ticks the
    /// duration down. ([USER] 2026-08-29 goes further -- the Bake-Kurage
    /// becomes base kit and is always on -- and that swap is
    /// <see cref="SummonIsFielded"/> alone.)
    /// </summary>
    public static async Task Pulse(PlayerChoiceContext choiceContext,
                                   KurageSummonPower summon)
    {
        var owner = summon.Owner;
        var player = owner?.Player;
        if (player == null || !IsLive(owner)) return;
        if (!PlayedAnything.Contains(player)) return;
        if (owner!.CombatState is not { } combat) return;

        var kind = LastCardType.TryGetValue(player, out var t) ? t : CardType.Skill;
        var target = PulseTarget(combat, player);

        if (kind == CardType.Attack)
        {
            if (target != null)
            {
                await ElementalHit.Deal(choiceContext, target, Element.Hydro,
                                        KokomiConstants.KuragePulseBase, owner);
            }
            return;
        }

        if (kind == CardType.Power)
        {
            if (KurageMemoryLaw.PowerPulse == "charge")
            {
                // [USER]: "Sacrificing a power seems like a bigger deal than
                // sacrificing anything else." The Power branch pays in the
                // currency the whole rule runs on. It lands with no board and
                // no target -- a bank does not need a body.
                KokomiResources.GainCharge(owner, KokomiConstants.ChargePerExhaust);
            }
            else if (target != null)
            {
                // v2's PICK C1, kept implemented: pure Hydro application, no
                // number. Nothing lands on an empty board -- an aura needs a
                // body.
                await ElementalHit.Deal(choiceContext, target, Element.Hydro, 0,
                                        owner);
            }
            return;
        }

        // Skill, and every other type.
        var block = KurageMemoryLaw.PulseBlock + KurageWardPower.WardAmount(owner);
        if (block > 0)
        {
            // NC-11 (R116): power-sourced block is RAW -- unpowered, not Move,
            // so neither Frail nor Dexterity sees it. Same line the shipped
            // pulse takes.
            await CreatureCmd.GainBlock(owner, block, ValueProp.Unpowered, null);
        }
    }

    private static void RefreshStrip(Creature? creature)
    {
        if (creature != null) Vfx.GaugeBridge.Refresh(creature);
    }

    // ------------------------------------------------------------- bridge --

    /// <summary>
    /// THE OBSERVED-BOARD PAYLOAD (`EB-181` rides here). A plain
    /// dictionary-of-primitives so the vendored bridge can lift it by
    /// reflection without referencing this assembly -- the same posture
    /// <c>gits/GitsResources.cs</c> takes toward BaseLib.
    ///
    /// Field names are the wire contract and are mirrored in
    /// <c>understudy/blindplay.py</c>:
    ///   bank          -- the Charge bank
    ///   front_price   -- the front memory's own price, or null on an empty queue
    ///   blocked       -- the front is unaffordable (distinct from empty)
    ///   fires_next    -- the front will fire at her next turn start
    ///   empty         -- the queue holds nothing
    ///   summon        -- a jellyfish is on the field
///   base_kit      -- it was installed at fight start, not summoned
    ///   pulse_kind    -- "attack" / "skill" / "power" / "none"
    ///   pulse_amount  -- what the pulse will move
    ///   pulse_unit    -- "damage" / "block" / "charge" / "hydro" / "none"
    ///   reading       -- the strip's one line, verbatim
    ///   queue         -- ordered, front first; each {name, price, cost,
    ///                    target, blocked, ephemeral, rule, affordable}
    ///
    /// READ-ONLY, and it never throws: a state read must not take the run down.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        var creature = player?.Creature;
        if (player == null || !IsLive(creature)) return snapshot;

        var queue = Queue(player);
        var bank = KokomiResources.GetCharge(creature);
        var front = queue.Count > 0 ? queue[0] : null;
        var blocked = front != null && bank < front.Price;

        snapshot["bank"] = bank;
        snapshot["front_price"] = front?.Price;
        snapshot["blocked"] = blocked;
        snapshot["fires_next"] = front != null && !blocked;
        snapshot["empty"] = front == null;
        snapshot["summon"] = SummonIsFielded(creature);
        // sec.12.6 ITEM 12: the install as a FIGHT-START FACT, so a blind
        // run can see the jellyfish before turn 1 rather than inferring it
        // from the first pulse. `summon` says it is on the field; this says
        // nobody had to summon it.
        snapshot["base_kit"] = KurageMemoryLaw.AlwaysOn;
        snapshot["pulse_kind"] = PulseKind(player);
        snapshot["pulse_amount"] = PulseAmount(player, creature);
        snapshot["pulse_unit"] = PulseUnit(player);
        snapshot["reading"] = Reading(player);

        var rows = new List<Dictionary<string, object?>>();
        foreach (var entry in queue)
        {
            rows.Add(new Dictionary<string, object?>
            {
                ["name"] = entry.Name,
                ["cost"] = entry.Cost,
                ["price"] = entry.Price,
                ["target"] = entry.Target is { IsAlive: true } t ? t.Name : null,
                ["blocked"] = entry == front && blocked,
                ["affordable"] = bank >= entry.Price,
                ["ephemeral"] = entry.Ephemeral,
                ["rule"] = entry.Rule,
            });
        }
        snapshot["queue"] = rows;
        return snapshot;
    }

    private static string PulseKind(Player player) =>
        !PlayedAnything.Contains(player) ? "none"
        : LastCardType.TryGetValue(player, out var t)
            ? t.ToString().ToLowerInvariant()
            : "skill";

    private static string PulseUnit(Player player) => PulseKind(player) switch
    {
        "none" => "none",
        "attack" => "damage",
        "power" => KurageMemoryLaw.PowerPulse == "charge" ? "charge" : "hydro",
        _ => "block",
    };

    private static int PulseAmount(Player player, Creature? owner) =>
        PulseKind(player) switch
        {
            "none" => 0,
            "attack" => KokomiConstants.KuragePulseBase,
            "power" => KurageMemoryLaw.PowerPulse == "charge"
                ? KokomiConstants.ChargePerExhaust : 0,
            _ => KurageMemoryLaw.PulseBlock + KurageWardPower.WardAmount(owner),
        };

    // ---------------------------------------------------------- the strip --

    /// <summary>
    /// THE STRIP'S ONE-LINE READING, §11.5, and the exact string the gauge
    /// draws and the bridge reports:
    ///
    ///     Charge 5 / 9 — Raiden blocked
    ///
    /// the bank, the front's price, and the front's state. When the front is
    /// affordable the same line reads as a forecast -- THIS FIRES NEXT TURN --
    /// and a 0-cost memory reads as free, because it is. An empty memory says
    /// so; it is not a block, and the strip must not let the two look alike.
    ///
    /// D4, in one sentence: everything that will fire next turn is readable
    /// this turn. The bank number, the front's price and the blocked state are
    /// the three facts the player must see before ending a turn.
    /// </summary>
    public static string Reading(Player? player)
    {
        var creature = player?.Creature;
        if (player == null || !IsLive(creature)) return string.Empty;
        var bank = KokomiResources.GetCharge(creature);
        var queue = Queue(player);
        if (queue.Count == 0) return $"Charge {bank} — memory empty";
        var front = queue[0];
        var state = bank < front.Price ? "blocked" : "fires next turn";
        return $"Charge {bank} / {front.Price} — {front.Name} {state}";
    }

    /// <summary>
    /// The whole strip as the lines the gauge label draws: the reading, then
    /// the queue in order, front first, each with its own price and the body it
    /// will hit. §11.5: under v2 every memory cost the same and the strip only
    /// had to draw ONE number; under v3 it must draw a price per card, and the
    /// block is a STATE it has to show rather than a number that happens to be
    /// too small.
    /// </summary>
    public static string StripText(Player? player)
    {
        var creature = player?.Creature;
        if (player == null || !IsLive(creature)) return string.Empty;
        var lines = new List<string> { Reading(player) };
        var bank = KokomiResources.GetCharge(creature);
        var queue = Queue(player);
        for (var i = 0; i < queue.Count; i++)
        {
            var e = queue[i];
            var aim = e.Target is { IsAlive: true } t ? t.Name : "random";
            var price = e.Price == 0 ? "free" : $"{e.Price} Charge";
            var mark = i == 0 && bank < e.Price ? "  (blocked)" : string.Empty;
            lines.Add($"{i + 1}. {e.Name} — {price} — {aim}{mark}");
        }
        return string.Join("\n", lines);
    }
}
