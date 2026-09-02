using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Klee's CharacterModel. Same reason Furina and Kokomi have one,
/// arrived at from the other end: a prototype patch runs on EVERY seat at the
/// table under the single <c>PROTOTYPE_CARDS</c> switch, so one arm's UI change
/// can take down a run belonging to a different character
/// (<c>EB-194</c>, <c>EB-221</c>), and <c>tools/lint_prototype_patch_scope.py</c>
/// requires every such patch to say whose creature it is about in an identity
/// idiom the mod owns. Klee was the last of the three without one -- she is the
/// compatibility baseline and every shipped site tests <c>is Klee</c> directly
/// -- and the lint's allowlist has been holding <c>IKleeCharacter</c>'s two
/// spellings open since it was written.
///
/// EMPTY, AND NOTHING SHIPPED READS IT YET. The shipped identity tests are
/// deliberately left as they are: this arrives for `EB-281`, whose acceptance
/// condition is that a flag-off build behaves exactly as it did.
/// </summary>
public interface IKleeCharacter
{
}

/// <summary>
/// Klee's Spark counter (spec C2.3; reference implementation
/// tier0/engine/combat.py card_cost/play_card, constants.py
/// SPARKS_FOR_FREE_ATTACK).
///
/// Canonical rules:
///   - Sparks accumulate on the player, unbounded, for the rest of the combat.
///   - While at THRESHOLD or more, the player's Attacks cost 0.
///   - Playing an Attack whose PRINTED cost is nonzero while at threshold
///     consumes THRESHOLD Sparks. Printed-0 attacks never consume (the sim's
///     `card.cost != 0` guard) -- a free attack should not eat the charge.
///
/// The cost side rides Hook.ModifyEnergyCostInCombat, which CardEnergyCost
/// consults for BOTH display and payment (GetWithModifiers -> the hook), so
/// the card visibly reads 0 in hand the moment the third Spark lands -- no UI
/// patch needed. The spend DECISION is snapshotted in BeforeCardPlayed
/// (pre-resolution, the sim's timing); the consume executes in
/// AfterCardPlayed. See the method comments for the Snap finding that
/// forced the split.
///
/// DISPLAY. This power IS the bank on every build, and off the Klee overhaul
/// arm it is also its own display -- the status-strip badge, with the rule text
/// below on its hover tip. UNDER THE ARM (`EB-281`) the bank is drawn instead as
/// a dedicated resource gauge over Klee's head, glyph and number, and the badge
/// is suppressed at the one container that makes it (<c>Vfx.SparkGauge</c>).
/// Nothing about the resource moves: the model stays visible -- which is what
/// keeps it on the understudy wire under the name "Spark" -- and every rule,
/// price, refusal and ledger row below still reads and moves this power.
///
/// X-cost attacks are EXEMPT from both sides, deliberately: zeroing an X-card
/// sets X = 0 and makes the card do nothing, which converts the buff into a
/// trap. Since R34 the sim exempts them identically (combat.py returns
/// before the spark branch on X; the spend guard checks cost != "X"), so
/// the divergence DECISIONS finding 26 recorded no longer exists --
/// behaviour matches on both sides.
/// </summary>
public sealed class SparkPower : PowerModel, ILocalizationProvider
{
    /// <summary>
    /// THE ALTERNATIVE-COST FLAG, C# side (review/ruled/klee-sparks-2026-08-29.md
    /// sec.10.1, PICK 6 option 1). Twin of tier0's
    /// <c>C.SPARK_ALT_COST_ENABLED</c>, and it is the SAME switch that
    /// quarantines the prototype surface: <c>-p:PrototypeCards=true</c> defines
    /// <c>PROTOTYPE_CARDS</c>, compiles <c>Cards/Prototype/**</c> and
    /// <c>Powers/Prototype/**</c>, and stamps a deploy <c>+proto</c>. One flag,
    /// one revert.
    ///
    /// FALSE means the base rule is RETIRED: at no bank do Attacks cost 0 and
    /// nothing is consumed automatically. It is a const rather than a
    /// <c>#if</c> at each site so the retirement reads as one fact with three
    /// call sites, and so the bite-check can assert the fact itself.
    ///
    /// NOTHING BELOW IS DELETED, which is deliberate and is tier0's own posture
    /// (<c>combat.spark_threshold</c> carries the identical RETIRED-UNDER-FLAG
    /// note): the two economies are meant to be runnable as two arms, and an
    /// OFF arm needs the shipped rule byte for byte.
    /// </summary>
#if PROTOTYPE_CARDS
    public const bool BaseRuleActive = false;
#else
    public const bool BaseRuleActive = true;
#endif

    /// <summary>Mirrors tier0 constants.py SPARKS_FOR_FREE_ATTACK = 3.</summary>
    public const int Threshold = 3;

    /// <summary>
    /// The live threshold: True Spark Knight lowers it, floored at 1 (sim:
    /// combat.py spark_threshold, `max(1, 3 - spark_threshold_down)`). Used
    /// for BOTH the cost gate and the spend, so they can never disagree --
    /// the sim reads spark_threshold(state) at both sites too.
    /// </summary>
    private int CurrentThreshold => System.Math.Max(
        1, Threshold
           - (Owner?.Powers.OfType<SparkThresholdDownPower>()
                  .FirstOrDefault()?.Amount ?? 0));

    /// <summary>
    /// The counter's face. Under the flag the base rule's sentence is a lie --
    /// nothing costs 0 and nothing is consumed -- and D4 makes a power that
    /// prints a rule it does not run a defect, not a cosmetic loose end. So the
    /// text retires with the rule it describes and the bank says only what it
    /// is: a resource cards charge for.
    /// </summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Spark"),
        ("description",
            BaseRuleActive
                ? "At 3 [gold]Sparks[/gold], your Attacks cost 0. "
                  + "Playing one consumes 3 [gold]Sparks[/gold]."
                : "A resource. Cards that print a [gold]Spark[/gold] price "
                  + "spend it."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter: sparks are spent, not ticked down by time.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// Grants sparks to <paramref name="player"/>. The single entry point for
    /// every future source (gain_spark codegen op, Pounding Surprise, Crackle
    /// per M8 ruling R10) so the gain path stays one line to instrument.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource, string? source = null)
    {
        // `EB-216`. THE LEDGER RIDES THE CHOKEPOINT, which is the whole reason
        // this method's doc comment above promised "one line to instrument".
        // The bank is read either side of the mutation, so what is recorded is
        // the delta that LANDED and not the delta that was asked for -- the
        // game's ModifyPowerAmountGiven chain can resize a grant, and a ledger
        // recording the request would not add up against the bank the wire
        // reports.
        int before = Bank(player);
        await PowerCmd.Apply<SparkPower>(
            choiceContext, player, amount, applier: player, cardSource: cardSource);
        Diagnostics.MeterLedger.Note(Diagnostics.MeterLedger.Spark,
            source ?? SourceOf(cardSource), Bank(player) - before, before);
        SyncGauge(player);
    }

    /// <summary>
    /// Redraw the Spark gauge (`EB-281`). Called from every funnel that MOVES
    /// the bank -- the same three chokepoints the <c>spark</c> meter ledger
    /// rides, and nothing else -- so the number on screen and the number in the
    /// ledger cannot come from different reads. The fourth call site is
    /// <see cref="AfterPowerAmountChanged"/>, which is not a funnel but a net.
    ///
    /// NO CATCH-UP SITE, unlike <c>KleeBurstResource.SyncGauge</c>, and the
    /// difference is real rather than an omission: Burst needs one because
    /// BaseLib's cost machinery spends that meter outside the mod's funnels
    /// entirely. Nothing outside this file moves a Spark bank -- every gain is
    /// <see cref="Gain"/> and every spend is <see cref="Spend"/> or the
    /// threshold consume below -- so there is nothing for an after-every-play
    /// sync to catch. <see cref="AfterPowerAmountChanged"/> covers the one
    /// exception, a bank moved by something that is not this mod at all.
    ///
    /// EMPTY IN A RELEASE BUILD. The gauge lives in <c>Vfx/Prototype/</c>, which
    /// is <c>Compile Remove</c>d without <c>-p:PrototypeCards=true</c>, so the
    /// seam is guarded here once instead of at each call site -- the same shape
    /// <c>KleeBurstResource.Find</c> uses for the arm read it needs.
    /// </summary>
    private static void SyncGauge(Creature? player)
    {
#if PROTOTYPE_CARDS
        Vfx.SparkGauge.Refresh(player);
#endif
    }

    /// <summary>
    /// The bank moved by something that is not this mod (`EB-281`): the
    /// understudy's <c>set_power</c> door is the one that exists today, and it
    /// applies through the game's own mutators rather than through
    /// <see cref="Gain"/>. <c>Hook.AfterPowerAmountChanged</c> fans to every
    /// model in the combat and fires on both <c>PowerCmd</c> paths, so the
    /// display cannot be left stale by a mutator nobody here knows about.
    ///
    /// The guard is <c>power == this</c> and not a type test: the hook is fanned
    /// to the OTHER seat's powers too (<c>Hook.IterateCombatHookListeners</c>),
    /// and it is also what keeps a canonical model from reaching
    /// <c>Owner</c>'s mutability assert.
    ///
    /// Redundant with the funnels for every ordinary gain and spend, which is
    /// deliberate: a redraw writes the same value twice and costs nothing, and
    /// the funnels stay the sites a reader can point at.
    /// </summary>
    public override Task AfterPowerAmountChanged(
        PlayerChoiceContext choiceContext, PowerModel power, decimal amount,
        Creature? applier, CardModel? cardSource)
    {
        if (power == this)
        {
            SyncGauge(Owner);
        }

        return Task.CompletedTask;
    }

    /// <summary>The bank right now, 0 when the counter is not on the creature
    /// yet. LEDGER READS ONLY -- <see cref="SparksAtPlay"/> and
    /// <see cref="SparksAsResolved"/> are the accessors a RULE reads, and they
    /// are spelled separately on purpose.</summary>
    private static int Bank(Creature owner) =>
        owner.Powers.OfType<SparkPower>().FirstOrDefault()?.Amount ?? 0;

    /// <summary>
    /// The ledger label for a site that did not name itself: the card that
    /// caused the change. Every GENERATED card reaches the ledger through
    /// this, which is why no generated file needed editing; the handful of
    /// powers, relics and kit responses that are not a card rider pass their
    /// own label. `unknown` is deliberately not spelled `card:` -- a source
    /// nobody named must not read as one that did.
    /// </summary>
    internal static string SourceOf(CardModel? card)
    {
        try
        {
            return card == null ? "unknown" : "card:" + card.Id.Entry;
        }
        catch (System.Exception)
        {
            return "unknown";
        }
    }

    /// <summary>
    /// Can this creature pay a Spark price of <paramref name="amount"/> right
    /// now? (EB-118 §4.5, the Spark sink; sim mirror:
    /// tier0/engine/combat.py <c>spark_cost</c> read by <c>card_playable</c>.)
    ///
    /// This is the GATE half of the cost line. A generated sink overrides
    /// <c>CardModel.IsPlayable</c> with this call -- the extension point the
    /// game documents for exactly this ("Grand Finale is only playable if
    /// your draw pile is empty"), consulted by <c>CanPlay</c> before any
    /// energy is committed -- so a short bank shows as an unplayable card
    /// rather than as a play that quietly does nothing.
    ///
    /// Reads <see cref="SparksAsResolved"/> and not the raw Amount, for the
    /// reason that accessor exists: the sim spends the threshold charge
    /// before a card's effects resolve while our consume runs after, so a
    /// mid-play read must subtract the pending spend or it sees a bank the
    /// sim never shows. Out of hand (the playability read) the two agree.
    /// </summary>
    public static bool CanSpend(Creature owner, int amount) =>
        amount > 0 && SparksAsResolved(owner) >= amount;

    /// <summary>
    /// Spend Sparks as a COST, the sink's payment half (sim mirror:
    /// effects.py <c>spend_sparks</c>). ALL OR NOTHING -- returns whether the
    /// bank paid, and mutates nothing when it did not.
    ///
    /// No overdraw: the shortfall-drains-HP grammar belongs to Furina's
    /// Encore alone, and a PARTIAL spend would leave the caller believing it
    /// was paid. The gate above is what a player sees; this refusal is the
    /// backstop for a spend the gate cannot see (one nested in a branch),
    /// and it is the same all-or-nothing rule on both sides.
    ///
    /// Dropping the bank below <see cref="CurrentThreshold"/> is a legal and
    /// deliberate outcome: under True Spark Knight (threshold 2) a spend of 2
    /// forfeits the free Attack. Nothing caches the bar -- <c>AppliesTo</c>
    /// re-reads Amount for the cost hook and for the consume decision -- so
    /// the forfeit takes effect on the very next read, as in the sim.
    ///
    /// applier: null, and for the same reason the threshold consume passes
    /// null -- a spend is bookkeeping, not a power "given" by anyone, and
    /// keeping it out of the ModifyPowerAmountGiven chain means nothing can
    /// inflate or shrink the exact price.
    /// </summary>
    public static async Task<bool> Spend(
        PlayerChoiceContext choiceContext, Creature player, int amount,
        CardModel? cardSource, string? source = null)
    {
        if (!CanSpend(player, amount))
        {
            return false;
        }

        var power = player.Powers.OfType<SparkPower>().FirstOrDefault();
        if (power == null)
        {
            return false;
        }

        // `EB-216`. A REFUSED spend writes nothing at all -- the two returns
        // above mutate nothing, and a ledger row saying "paid 0" would read as
        // a free play rather than as a play that never happened.
        int before = power.Amount;
        await PowerCmd.ModifyAmount(
            choiceContext, power, -amount, applier: null, cardSource: cardSource);
        Diagnostics.MeterLedger.Note(Diagnostics.MeterLedger.Spark,
            source ?? SourceOf(cardSource), power.Amount - before, before);
        SyncGauge(player);
        return true;
    }

    /// <summary>
    /// The base rule's predicate. RETIRED-UNDER-FLAG: the first clause is the
    /// flag itself, so the zeroing hook, the spend DECISION and the consume all
    /// stand down together and cannot be retired by halves. Kept rather than
    /// deleted for the reason on <see cref="BaseRuleActive"/>.
    /// </summary>
    private bool AppliesTo(CardModel card) =>
        BaseRuleActive
        && Amount >= CurrentThreshold
        && card.Type == CardType.Attack
        && !card.EnergyCost.CostsX
        && card.Owner?.Creature == Owner;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (originalCost <= 0m || !AppliesTo(card))
        {
            return false;
        }

        modifiedCost = 0m;
        return true;
    }

    /// <summary>
    /// The spend DECISION, snapshotted at play start (playtest finding
    /// 2026-07-20, the Snap bug): the sim's play_card evaluates
    /// `sparks >= threshold` BEFORE the card's effects resolve, so a card
    /// whose own rider pushes the bank to threshold mid-resolution must NOT
    /// eat the charge -- the player paid energy for that play. Deciding in
    /// AfterCardPlayed (the old shape) read the post-rider bank: Snap at 2
    /// Sparks cost 1 energy, granted the 3rd Spark, then wrongly consumed
    /// all 3. Printed cost is read off EnergyCost.Canonical -- the sim's
    /// guard is `card.cost != 0` (a printed-0 attack never consumes).
    ///
    /// IsFirstInSeries reproduces "once per play_card call" across replays,
    /// same as the burst grant in KleeElementalHooks. The threshold is
    /// snapshotted with the decision (sim: `p.sparks -= spark_threshold(state)`
    /// reads the state at play time).
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (cardPlay.IsFirstInSeries
            && AppliesTo(cardPlay.Card)
            && cardPlay.Card.EnergyCost.Canonical != 0)
        {
            _pendingSpendPlay = cardPlay;
            _pendingSpendAmount = CurrentThreshold;
        }
        return Task.CompletedTask;
    }

    /// <summary>
    /// Transient decision state; only ever set between a BeforeCardPlayed and
    /// its AfterCardPlayed (one card resolves at a time). Not cloned
    /// meaningfully by MutableClone -- a stale reference on a clone can never
    /// equal a live CardPlay, so the worst case is a no-op.
    /// </summary>
    private CardPlay? _pendingSpendPlay;
    private int _pendingSpendAmount;

    /// <summary>
    /// The Spark bank as the sim sees it DURING a card's resolution. The
    /// sim's play_card spends BEFORE resolve_card, but our consume executes
    /// in AfterCardPlayed (payment-ordering safety, above) -- so mid-play
    /// readers must subtract the pending spend, or they read a pre-spend bank
    /// the sim never shows. This is the caveat recorded with the Snap fix.
    ///
    /// R39 NARROWED ITS SCOPE (2026-07-21): the only reader that ever needed
    /// this was Gleeful Barrage's hit count, and that card now deliberately
    /// reads the PRE-spend bank instead (SparksAtPlay). Spark spend fires on
    /// attacks only, and both has_spark cards are skills, so no current
    /// reader can observe a pending spend at all. Kept because the accessor
    /// is the correct one for any FUTURE attack that reads the bank mid-play
    /// and wants the sim's post-spend view.
    /// </summary>
    public static int SparksAsResolved(Creature owner)
    {
        var power = owner.Powers.OfType<SparkPower>().FirstOrDefault();
        if (power == null) return 0;
        return power._pendingSpendPlay == null
            ? power.Amount
            : power.Amount - power._pendingSpendAmount;
    }

    /// <summary>
    /// The Spark bank as it stood when the card was played, BEFORE that
    /// card's own spark spend -- tier0 state.sparks_at_play (R39).
    ///
    /// Our consume runs in AfterCardPlayed, so during OnPlay the power's
    /// Amount IS still the pre-spend bank; the pending spend is a decision
    /// that has not been executed. That makes this the plain read, and it is
    /// spelled out as its own accessor so the intent is legible at the call
    /// site rather than looking like someone forgot SparksAsResolved.
    /// </summary>
    public static int SparksAtPlay(Creature owner) =>
        owner.Powers.OfType<SparkPower>().FirstOrDefault()?.Amount ?? 0;

    /// <summary>
    /// The consume, executing the play-time decision. Kept AFTER resolution:
    /// mutating the bank in BeforeCardPlayed could drop Amount below
    /// threshold before the payment machinery reads the (zeroed) cost --
    /// that ordering has no decompile evidence, so the safe side wins. The
    /// sim spends pre-resolution, which only differs observably for cards
    /// that READ the bank mid-play (formula cards; none are shipped --
    /// revisit with evidence when formula codegen lands).
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay != _pendingSpendPlay)
        {
            return;
        }
        _pendingSpendPlay = null;

        // applier: null -- the spend is bookkeeping, not a power "given" by
        // anyone; keeping it out of the ModifyPowerAmountGiven hook chain
        // means nothing can inflate or shrink the exact spend.
        int before = Amount;
        await PowerCmd.ModifyAmount(
            choiceContext, this, -_pendingSpendAmount, applier: null,
            cardSource: cardPlay.Card);
        // `EB-216`. NAMED AS THE RULE AND NOT AS THE CARD: the base free-Attack
        // consume is charged by the threshold rule, not printed on the card
        // that triggered it, and a grader reading `card:` here would count a
        // printed price the face never showed.
        Diagnostics.MeterLedger.Note(Diagnostics.MeterLedger.Spark,
            "rule:threshold_consume", Amount - before, before);
        // The third funnel. UNREACHABLE under the overhaul arm -- the base rule
        // is retired wherever the gauge compiles (BaseRuleActive is false under
        // PROTOTYPE_CARDS) -- and refreshed anyway, so "every funnel that moves
        // the bank redraws it" stays one fact rather than two-thirds of one.
        SyncGauge(Owner);

        // Sparks-spend VFX (sprint plan E3); concurrency-capped in the
        // spawner so burst turns cannot particle-storm the screen.
        Vfx.KleeCombatVfx.SpawnDodocoPop(Owner);
    }
}
