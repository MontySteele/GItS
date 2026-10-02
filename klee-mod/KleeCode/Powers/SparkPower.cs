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
/// below on its hover tip. UNDER THE ARM the bank is drawn instead as a
/// dedicated resource counter beside the energy orb, glyph and number
/// (`EB-621`, <c>Vfx.SparkCounter</c>; the overhead gauge `EB-281` put over her
/// head was deleted by the 2026-09-24 playtest), and the badge is suppressed at
/// the one container that makes it (<c>Vfx.SparkGauge</c>).
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
    /// <summary>The counter's face: a resource cards charge for. The
    /// shipped free-Attack rule (3 Sparks) went with the shipped kits.</summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Spark"),
        ("description",
            "A resource. Cards that print a [gold]Spark[/gold] price "
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
        // R276, SPARK KNIGHT, and it rides this chokepoint for the ledger's
        // reason: every Spark any source grants passes here, so "whenever you
        // gain a Spark" has one door. The Sparks that LANDED, not the ask.
        await SparkKnightPower.AfterSparksGained(
            choiceContext, player, Bank(player) - before);
    }

    /// <summary>
    /// Redraw the Spark display (`EB-281`, now the energy-area counter
    /// `EB-621` alone). Called from every funnel that MOVES
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
        Vfx.SparkGauge.Refresh(player);
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
    /// yet. LEDGER READS ONLY -- <see cref="SparksAtPlay"/> is the accessor a
    /// RULE reads, and it is spelled separately on purpose.</summary>
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
    /// </summary>
    public static bool CanSpend(Creature owner, int amount) =>
        amount > 0 && SparksAtPlay(owner) >= amount;

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
    ///
    /// `EB-512`: THE PAYMENT IS VERIFIED AND NOT ASSUMED, which is the whole
    /// of that row. The r18 seat played Stoke the Fuse at Spark 2, watched the
    /// Mine grow 4 to 10 -- both Sparks counted -- and read `Spark 2` on the
    /// very next screen: "the effect billed me and the counter did not". This
    /// method used to `return true` the moment the command was awaited, and
    /// <c>PowerCmd.ModifyAmount</c> returns having touched nothing on two of
    /// its own guards (the combat is ending; the power's owner has no combat
    /// state) before its hook chain can resize the offset at all. So the bank
    /// stayed whole, the caller was told it had paid, and the X-price row's
    /// payout -- read off <see cref="SparksAtPlay"/> BEFORE the call -- was
    /// handed over in full. The bank is now read back and the answer is what
    /// the bank actually did, so a caller can refuse its own payout; the
    /// generated X-price body does exactly that
    /// (<c>gen_klee_cards._stmt_spend_spark</c>).
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
        int paid = before - power.Amount;
        SyncGauge(player);

        // `EB-512`. A COMMAND THAT MOVED NOTHING IS NOT A PAYMENT. Same
        // `EB-216` rule as the two refusals above, one step later: the row is
        // written only when the bank actually moved, so "paid 0" stays a thing
        // the ledger cannot say.
        if (paid <= 0)
        {
            return false;
        }
        Diagnostics.MeterLedger.Note(Diagnostics.MeterLedger.Spark,
            source ?? SourceOf(cardSource), power.Amount - before, before);
        return paid >= amount;
    }

    /// <summary>
    /// The Spark bank as it stood when the card was played -- tier0
    /// state.sparks_at_play (R39). Nothing spends Sparks between the play and
    /// the card's resolution, so this is the plain read.
    /// </summary>
    public static int SparksAtPlay(Creature owner) =>
        owner.Powers.OfType<SparkPower>().FirstOrDefault()?.Amount ?? 0;
}
