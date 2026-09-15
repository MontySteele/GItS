using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Nodes.Vfx.Utilities;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// PUNCH OFF, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/PunchOff.cs` and cross-checked against
/// the harvest (2 options: Nab, I Can Take Them).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same combat LAYOUT and canonical
/// encounter, the same `IsShared`, the same floor-6 gate, the same
/// `Rng.NextInt(91, 99)` gold roll, the same Injury-then-relic-reward on the
/// first option, and the same cancel-the-punching-then-offer-the-fight on the
/// second, with the same two extra rewards on the fight itself.
///
/// THIS IS THE ONLY MIRROR WITH A BACKGROUND LOOP. `AfterEventStarted`
/// subscribes to `RunManager.RoomExited` and starts `PunchEachOther` under a
/// `CancellationTokenSource`; the loop reads the two enemies straight off
/// `_combatSynchronizer`, mirrors the left one horizontally, and trades
/// blows until cancelled. Both the option and the room exit cancel it, and
/// the unsubscribe is in the same handler the base event puts it in -- a
/// mirror that dropped either would leave a task swinging in a room the
/// player has left.
///
/// `_combatSynchronizer` IS REACHABLE WITHOUT REFLECTION, which is worth
/// saying because it is the one thing in this surface that looked like it
/// would not be: it is `protected` on `EventModel` (`EventModel.cs:36`), not
/// private, so the mirror reads it as the base event does and no
/// `TeyvatEventMirror` accessor or reverse patch is needed.
///
/// THE ENCOUNTER AND THE CURSE ARE THE BASE GAME'S. `PunchOffEventEncounter`
/// and `Injury` carry global rows; the constructs' NAMES are dressed through
/// `Patches/MonsterNamePatch`, which is the seam every dressed monster name
/// goes through, and not here.
/// </summary>
public abstract class PunchOffMirror : TeyvatEventMirror
{
    /// <summary>The base event's cancel handle for the punching loop.</summary>
    private CancellationTokenSource _punchCts;

    /// <summary>The base event's own: this event draws the combat room.</summary>
    public override EventLayoutType LayoutType => EventLayoutType.Combat;

    /// <summary>The base event's own: the encounter the layout shows, and the
    /// one the fight enters.</summary>
    public override EncounterModel CanonicalEncounter => ModelDb.Encounter<PunchOffEventEncounter>();

    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>`PunchOff.cs:41`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new GoldVar(0) };

    /// <summary>The base event's gate: floor 6 or later.</summary>
    public override bool IsAllowed(IRunState runState) => runState.TotalFloor >= 6;

    /// <summary>Two options, in the base event's order, under its names, with
    /// Injury's card hover tip on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Nab, InitialOptionKey("NAB"),
                HoverTipFactory.FromCardWithCardHoverTips<Injury>()),
            new EventOption(this, TakeThem, InitialOptionKey("I_CAN_TAKE_THEM")),
        };

    /// <summary>The base event's start hook: watch for the room exit, then
    /// start the punching.</summary>
    public override Task AfterEventStarted()
    {
        RunManager.Instance.RoomExited += OnRoomExited;
        _punchCts = new CancellationTokenSource();
        TaskHelper.RunSafely(PunchEachOther());
        return Task.CompletedTask;
    }

    /// <summary>
    /// The base event's loop, beat for beat: the left enemy is flipped by
    /// negating its X scale, each blow is anim-then-VFX-then-hit-spark-then-
    /// hit-anim with the base event's own waits, and the cancellation is
    /// checked between the two halves as well as at the top. The scale is put
    /// back only if the node is still valid, which is the base event's guard
    /// against a room torn down mid-swing.
    /// </summary>
    private async Task PunchEachOther()
    {
        Creature leftEnemy = _combatSynchronizer.CombatStateForLayout.Enemies[0];
        Creature rightEnemy = _combatSynchronizer.CombatStateForLayout.Enemies[1];
        NCreature leftEnemyNode = NCombatRoom.Instance?.GetCreatureNode(leftEnemy);
        if (leftEnemyNode == null)
        {
            return;
        }

        Vector2 originalScale = leftEnemyNode.Scale;
        leftEnemyNode.Scale = new Vector2(-originalScale.X, originalScale.Y);
        Control vfxContainer = NCombatRoom.Instance?.CombatVfxContainer;

        while (!_punchCts.IsCancellationRequested)
        {
            await CreatureCmd.TriggerAnim(leftEnemy, "Attack", 0f);
            await Cmd.Wait(0.1f);
            VfxCmd.PlayOnCreatureCenter(rightEnemy, "vfx/vfx_attack_blunt");
            vfxContainer?.AddChildSafely(NHitSparkVfx.Create(rightEnemy, requireInteractable: false));
            await CreatureCmd.TriggerAnim(rightEnemy, "Hit", 0f);
            await Cmd.Wait(1.2f);

            if (_punchCts.IsCancellationRequested)
            {
                break;
            }

            await CreatureCmd.TriggerAnim(rightEnemy, "Attack", 0f);
            await Cmd.Wait(0.1f);
            VfxCmd.PlayOnCreatureCenter(leftEnemy, "vfx/vfx_attack_blunt");
            vfxContainer?.AddChildSafely(NHitSparkVfx.Create(leftEnemy, requireInteractable: false));
            await CreatureCmd.TriggerAnim(leftEnemy, "Hit", 0f);
            await Cmd.Wait(1.2f);
        }

        _punchCts = null;
        if (leftEnemyNode.IsValid())
        {
            leftEnemyNode.Scale = originalScale;
        }
    }

    /// <summary>The base event's roll: 91-98 (`NextInt` is exclusive at the
    /// top).</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue = Rng.NextInt(91, 99);
    }

    /// <summary>`Nab`: the curse, the shake and the thud, a beat, then one
    /// relic reward.</summary>
    private async Task Nab()
    {
        await CardPileCmd.AddCurseToDeck<Injury>(Owner);
        NGame.Instance.ScreenShakeTrauma(ShakeStrength.Strong);
        NDebugAudioManager.Instance?.Play("blunt_attack.mp3");
        await Cmd.CustomScaledWait(0.25f, 0.5f);
        await RewardsCmd.OfferCustom(Owner, new List<Reward>(1) { new RelicReward(Owner) });
        SetEventFinished(L10NLookup(PageKey("NAB.description")));
    }

    /// <summary>`TakeThem`: the punching stops and the second page offers the
    /// fight.</summary>
    private Task TakeThem()
    {
        _punchCts?.Cancel();
        SetEventState(L10NLookup(PageKey("I_CAN_TAKE_THEM.description")), new List<EventOption>
        {
            new EventOption(this, Fight, PageKey("I_CAN_TAKE_THEM.options.FIGHT")),
        });
        return Task.CompletedTask;
    }

    /// <summary>`Fight`: the encounter, with a relic and a potion ON TOP of
    /// the standard combat reward, and no resume.</summary>
    private Task Fight()
    {
        List<Reward> extraRewards = new List<Reward>
        {
            new RelicReward(Owner),
            new PotionReward(Owner),
        };
        EnterCombatWithoutExitingEvent<PunchOffEventEncounter>(extraRewards, shouldResumeAfterCombat: false);
        return Task.CompletedTask;
    }

    /// <summary>The base event's teardown: unsubscribe, then cancel.</summary>
    private void OnRoomExited()
    {
        RunManager.Instance.RoomExited -= OnRoomExited;
        _punchCts?.Cancel();
    }
}
