using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Entities.Cards;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S TWO CLOCKS: the lead regenerates at the start of her turn
/// (rule 4) and the performers act at the end of it (rule 10).
///
/// ITS OWN LISTENER, and the argument is <c>CompanionOverhaulTurnEnd</c>'s one
/// arm over. The shipped end-of-turn work is <c>TurnEndSequencer</c>'s, which
/// walks <c>TurnEndAttribution.Order</c> -- a SHIPPED table, pinned by
/// <c>test_the_turn_end_sequence_is_the_sims_order</c>, whose whole point is
/// that the docket cannot name its four sources in an order they are not
/// fired in. Adding an arm's fifth source to that table would move a shipped
/// display under a flag. So the stage keeps its own subscription, is
/// concatenated behind the one <c>SubscribeForCombatStateHooks</c> call like
/// every other tenant, and is a walk over nothing on a board with no stage.
///
/// AFTER the sequencer, in the same broadcast, and deliberately: the shipped
/// end-of-turn tenants are what a shipped Furina's docket accounts for, and an
/// act that resolved before them would change a number the docket had already
/// drawn. Position in the concat list is the whole of that ordering, which is
/// why it is stated here rather than left to the reader of KleeMod.cs.
///
/// QUARANTINED AND ARM-GATED. The file is not compiled into a release build,
/// and every method's first line asks <see cref="FurinaStage.LiveFor"/>, so on
/// a Klee seat, a Kokomi seat or a flag-off Furina it is three early returns.
/// </summary>
public sealed class FurinaStageHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaStageHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaStageHooks>(
            ModelDb.GetId<FurinaStageHooks>());
        yield return _instance;
    }

    /// <summary>
    /// RULE 4. The site is the retired reframe's opening grant's and its
    /// argument carries over whole: this engine's turn-start effects fire on
    /// <c>AfterPlayerTurnStart</c>, after the block clear, the energy reset and
    /// the draw -- the moment the sim's <c>_player_turn</c> fires its own, and
    /// the moment the blind-play page renders its first line of the turn.
    /// </summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        await FurinaStage.InstallBadge(player.Creature);
        await FurinaStage.RegenLead(player.Creature);
        // 2026-09-26: the cues go up for the turn they forecast.
        Vfx.FurinaStageCues.CurtainUp(player.Creature);
    }

    /// <summary>
    /// RULE 10. <c>BeforeSideTurnEnd</c> rather than <c>AfterSideTurnEnd</c>,
    /// because that is the broadcast the shipped end-of-turn work already runs
    /// in and the one that still precedes the discard flush: an act that
    /// resolved after the flush would land on a board the player had stopped
    /// looking at.
    /// </summary>
    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants.ToList())
        {
            if (!FurinaStage.LiveFor(creature)) continue;
            // `EB-735`. THE LOG'S TURN BOUNDARY, and it is HERE rather than at
            // her turn start on purpose. The window a seat cannot watch is the
            // TURN BREAK -- this sweep, and then what the enemies' attacks
            // take off the lead -- so a clear at turn start would wipe both a
            // moment before the only screen that could print them. That is
            // `SALON_ARRIVAL_NOTE`'s defect one arm over, where an arrival
            // that had performed reached the page as an empty list. Cleared
            // immediately BEFORE the sweep, so the log the next screen carries
            // opens with the sweep it is about.
            FurinaStageLedger.For(creature).ClearBeats();
            // 2026-09-26: the cues forecast "the end of this turn", and it is
            // here: they come down as the acts begin, the way an enemy's
            // intent clears as it acts, and stay down until her next turn.
            Vfx.FurinaStageCues.CurtainDown(creature);
            await FurinaStage.EndOfTurnActs(choiceContext, creature);
        }
    }

    /// <summary>
    /// RULE 1's second sentence, "pets live one combat", needs no teardown
    /// here and that absence is deliberate. The LEDGER clears itself by combat
    /// identity (<c>FurinaStageLedger.For</c>), the BODIES are pets and leave
    /// with the combat, and the STRIP is a creature-tracked gauge inside the
    /// room's own vfx container rather than a HUD Control -- so it dies with
    /// the room. `EB-640`'s finding (a lethal beat leaving the Salon panel
    /// drawn behind the loot dialog) was about a Control that outlived its
    /// room, and it does not reach a gauge.
    /// </summary>
    /// <summary>
    /// `EB-747`. A FRESH PER-PLAY SPEND RECORD, at the start of every card
    /// play.
    ///
    /// <c>FurinaStage.BeginPlay</c> existed and NOTHING CALLED IT, which was
    /// invisible while the readers printed a rule instead of a number: each
    /// spending op writes <c>SpentThisPlay</c> itself, so the record was right
    /// during a play and stale between two. It is a forecast now
    /// (<see cref="FurinaStage.SpentOrBackFanfare"/>), and a forecast read off
    /// a record the last card left is the wrong number on the face.
    /// </summary>
    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        FurinaStage.BeginPlay(cardPlay.Card?.Owner?.Creature);
        return Task.CompletedTask;
    }

    /// <summary>
    /// ROUND THREE, sec.4: <i>Let the People Rejoice</i> printed "Deal 2 damage
    /// to ALL" with the stage reading Usher 12 -- an earlier card's spend, read
    /// off a record that was opened at <see cref="BeforeCardPlayed"/> and never
    /// closed. The forecast is only a forecast while a play is in flight, so
    /// the record CLOSES here and the face falls back to the bars.
    /// </summary>
    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        FurinaStage.EndPlay(cardPlay.Card?.Owner?.Creature);
        Vfx.FurinaStageCues.Refresh(cardPlay.Card?.Owner?.Creature);
        return Task.CompletedTask;
    }

    /// <summary>
    /// Rule 7 (2026-09-25): THE HIT THAT KILLS FURINA EARNS NO BOW. A lead
    /// emptied by a hit queues its Bow for the flush after the hit, and the
    /// engine skips that flush for a target the hit killed. Dropped here, so a
    /// revived Furina's next hit cannot pay a Bow left over from this one.
    /// </summary>
    public override Task AfterDeath(
        PlayerChoiceContext choiceContext, Creature creature,
        bool wasRemovalPrevented, float deathAnimLength)
    {
        if (FurinaStage.LiveFor(creature))
        {
            FurinaStageLedger.For(creature).TakePendingHitBows();
        }
        return Task.CompletedTask;
    }
}
