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
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Settings;

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
/// THE ONE DEVIATION FROM THE BASE EVENT IS `EB-769`, AND IT IS NOT
/// MECHANICAL: EVERY PER-SWING ALLOCATION IN THE LOOP IS BOUNDED, and the
/// loop itself stops swinging under `FastModeType.Instant`.
///
/// The base loop is paced by `Cmd.Wait`, and `Cmd.Wait` IS A NO-OP UNDER
/// `Instant` (`Cmd.cs`: the `SceneTreeTimer` is never created when
/// `PrefsSave.FastMode == FastModeType.Instant`), as is
/// `Cmd.CustomScaledWait` inside `CreatureCmd.TriggerAnim(.., 0f)`. So under
/// the soak harness the `while` has no awaited suspension left in it at all:
/// it is a tight loop that both never yields and allocates a Godot node on
/// every pass. Three guards, one per thing a pass costs:
///
/// * the decorative `NHitSparkVfx` node -- skipped under `Instant`, capped at
///   `MaxHitSparksPerVisit` otherwise (the half of this that shipped in #528);
/// * the `vfx/vfx_attack_blunt` scene, which `VfxCmd.PlayOnCreatureCenter`
///   reaches through `PlayVfx` -> `PackedScene.Instantiate` -- skipped under
///   `Instant`, capped at `MaxBluntVfxPerVisit` otherwise. This is the one
///   proofs-6 caught: with the sparks capped and absent from every log, the
///   top backtrace frame moved to `Godot.PackedScene.Instantiate_Patch1`
///   under `PunchEachOther`;
/// * the swing itself -- under `Instant` the loop stops after
///   `MaxSwingsUnderInstant`, so no per-pass cost of ANY kind, named here or
///   not, is left unbounded.
///
/// `CreatureCmd.TriggerAnim` allocates nothing per swing for these two: it
/// sets an animation trigger on the existing `NCreature` node, and its SFX
/// arm is `creature.IsPlayer` only. It is left exactly as the base event has
/// it. NOTHING ELSE MOVES: the same anims, the same waits, the same options,
/// the same rewards, and at the player's own speed (`Normal` / `Fast`) the
/// punching runs on forever as it always did.
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

    /// <summary>
    /// `EB-769`. HOW MANY HIT SPARKS ONE VISIT MAY SPAWN.
    ///
    /// THE LOOP IS PACED BY A WAIT, NOT BY A BUDGET. Each swing adds an
    /// `NHitSparkVfx` node to the combat VFX container and then waits 1.2 s,
    /// so at the game's own speed a player sees under one spark a second and
    /// the engine reclaims them as fast as they arrive. Under the harness's
    /// `FastMode = Instant` with `Engine.TimeScale = 3` the waits collapse and
    /// the spawn rate is bounded by nothing at all: proofs-5 measured 34,501
    /// `Element limit reached. at: _allocate_rid` and 613,190
    /// `Parameter "particles" is null`, every one of them under
    /// `NHitSparkVfx.Create` called from this loop, with the process
    /// unresponsive and a 2.56 GB `godot.log` (the 2026-09-15 deploy proofs,
    /// item 2: `git show
    /// d47d9fcc:review/records/teyvat-proofs-5-2026-09-15.md`).
    ///
    /// 24 IS HALF A MINUTE OF THE INTENDED PACING and far short of the
    /// allocator's ceiling. Past it the punching CONTINUES -- the anims and
    /// `vfx_attack_blunt` are the event's mechanics and its picture, and
    /// nothing here touches either -- but the extra spark node is not spawned.
    /// </summary>
    internal const int MaxHitSparksPerVisit = 24;

    /// <summary>Hit sparks spawned by THIS visit's loop.</summary>
    private int _hitSparks;

    /// <summary>
    /// `EB-769`. May this swing spawn its hit spark?
    ///
    /// Pure and `internal` so the judgment is pinned off a headless test:
    /// `SaveManager` and `Engine.TimeScale` are outside that boundary, this
    /// decision is not.
    ///
    /// TWO GUARDS, AND THE FIRST IS THE ONE THAT MATTERS. `FastModeType.Instant`
    /// is exactly what the soak harness sets --
    /// `vendor/STS2_MCP/gits/GitsSpeed.cs` assigns
    /// `SaveManager.Instance.PrefsSave.FastMode = FastModeType.Instant`
    /// alongside `Engine.TimeScale` -- so under the harness no spark is
    /// spawned at all and the room stays drivable. The count is the backstop
    /// for any other way a machine can outrun a 1.2 s wait.
    /// </summary>
    internal static bool ShouldSpawnHitSpark(FastModeType fastMode, int spawned)
        => fastMode != FastModeType.Instant && spawned < MaxHitSparksPerVisit;

    /// <summary>
    /// `EB-769`. HOW MANY BLUNT-IMPACT SCENES ONE VISIT MAY INSTANTIATE.
    ///
    /// A SIBLING OF `MaxHitSparksPerVisit`, AND FOR THE SAME REASON: each
    /// swing's `VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_attack_blunt")`
    /// runs `PreloadManager.Cache.GetScene(path).Instantiate<Node2D>(..)` and
    /// adds the node to the combat VFX container (`VfxCmd.PlayVfx`), so it is
    /// exactly as unbounded as the spark was once the 1.2 s wait collapses.
    /// #528 capped the spark and left this one, and proofs-6 read the result:
    /// no `NHitSparkVfx` in any log, the process still dead under
    /// `FastMode = Instant` / `TimeScale 3`, and the top backtrace frame now
    /// `Godot.PackedScene.Instantiate_Patch1` under `PunchEachOther`
    /// (`review/records/teyvat-proofs-6-2026-09-16.md`, item 3).
    ///
    /// ITS OWN CONSTANT RATHER THAN A SHARED ONE, because the two are
    /// separate pictures with separate budgets: the blunt impact is the blow
    /// the player reads and the spark is decoration on top of it, and a later
    /// ruling that moves one should not silently move the other. They start
    /// at the same value because the same half-minute of the loop's intended
    /// pacing is the right budget for both.
    /// </summary>
    internal const int MaxBluntVfxPerVisit = 24;

    /// <summary>
    /// `EB-769`. HOW MANY SWINGS THE LOOP TAKES WHEN THE WAITS ARE GONE.
    ///
    /// THE BOUND OF LAST RESORT, and the only guard here that is about the
    /// loop rather than about one allocation in it. Under `Instant` neither
    /// `Cmd.Wait` nor `Cmd.CustomScaledWait` creates a timer, so every
    /// `await` in the body completes synchronously and the `while` becomes a
    /// tight loop that never returns to the scene tree. Capping the two known
    /// spawns makes each pass cheap; it does not make a spinning loop stop.
    /// This does, and it bounds anything a future engine version starts
    /// allocating in a pass that nobody has audited yet.
    ///
    /// ONLY UNDER `Instant`. At `Normal` and `Fast` the waits are real, the
    /// loop yields, and the constructs punch until the player leaves the room
    /// exactly as they do in the base event -- nothing a person sees at their
    /// own speed is changed by this beyond the two caps above.
    /// </summary>
    internal const int MaxSwingsUnderInstant = 24;

    /// <summary>Blunt-impact scenes instantiated by THIS visit's loop.</summary>
    private int _bluntVfx;

    /// <summary>Swings taken by THIS visit's loop, counting each blow.</summary>
    private int _swings;

    /// <summary>
    /// `EB-769`. May this swing play its `vfx_attack_blunt`?
    ///
    /// Pure and `internal` for the same reason `ShouldSpawnHitSpark` is: the
    /// scene cache and the node tree are outside the headless boundary, this
    /// judgment is not.
    /// </summary>
    internal static bool ShouldPlayBluntVfx(FastModeType fastMode, int played)
        => fastMode != FastModeType.Instant && played < MaxBluntVfxPerVisit;

    /// <summary>
    /// `EB-769`. May the loop take another swing?
    ///
    /// `true` at every speed a person plays at, whatever the count -- the
    /// base event's loop is endless and stays endless. Under `Instant` it
    /// stops at `MaxSwingsUnderInstant`, which is what turns the tight
    /// no-yield loop into a bounded one.
    /// </summary>
    internal static bool ShouldKeepPunching(FastModeType fastMode, int swings)
        => fastMode != FastModeType.Instant || swings < MaxSwingsUnderInstant;

    /// <summary>
    /// The player's animation-pacing setting, or `Normal` when it cannot be
    /// read. NEVER THROWS: this is consulted inside a background loop in a
    /// room the player is standing in, and an exception here would leave the
    /// constructs frozen mid-swing.
    /// </summary>
    private static FastModeType CurrentFastMode()
    {
        try
        {
            return SaveManager.Instance?.PrefsSave?.FastMode ?? FastModeType.Normal;
        }
        catch
        {
            return FastModeType.Normal;
        }
    }

    /// <summary>
    /// `EB-769`. One swing's hit spark, spawned only when the budget and the
    /// speed setting both allow it.
    /// </summary>
    private void SpawnHitSpark(Control vfxContainer, Creature target)
    {
        if (!ShouldSpawnHitSpark(CurrentFastMode(), _hitSparks))
        {
            return;
        }

        _hitSparks++;
        vfxContainer?.AddChildSafely(NHitSparkVfx.Create(target, requireInteractable: false));
    }

    /// <summary>
    /// `EB-769`. One swing's blunt impact, played only when the budget and
    /// the speed setting both allow it. The call itself is the base event's,
    /// argument for argument.
    /// </summary>
    private void PlayBluntVfx(Creature target)
    {
        if (!ShouldPlayBluntVfx(CurrentFastMode(), _bluntVfx))
        {
            return;
        }

        _bluntVfx++;
        VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_attack_blunt");
    }

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
        // `EB-769`: every budget here is PER VISIT, so they are zeroed where
        // the visit starts rather than where the model is constructed -- an
        // event model outlives the room it was shown in.
        _hitSparks = 0;
        _bluntVfx = 0;
        _swings = 0;
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
    ///
    /// `EB-769` adds only the swing bound beside each of those two cancel
    /// checks, and routes the blunt impact and the hit spark through their
    /// guards. Leaving by the bound takes the base event's own exit path --
    /// the handle is cleared and the scale is put back -- so a room exit
    /// after it is the same no-op it is after a cancel.
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

        // `EB-769`: the base event's `while (!cancelled)` with the swing bound
        // beside the cancel check. The bound is `true` at every speed a person
        // plays at, so this is the base event's condition unchanged there.
        while (!_punchCts.IsCancellationRequested
               && ShouldKeepPunching(CurrentFastMode(), _swings))
        {
            _swings++;
            await CreatureCmd.TriggerAnim(leftEnemy, "Attack", 0f);
            await Cmd.Wait(0.1f);
            PlayBluntVfx(rightEnemy);
            SpawnHitSpark(vfxContainer, rightEnemy);
            await CreatureCmd.TriggerAnim(rightEnemy, "Hit", 0f);
            await Cmd.Wait(1.2f);

            if (_punchCts.IsCancellationRequested
                || !ShouldKeepPunching(CurrentFastMode(), _swings))
            {
                break;
            }

            _swings++;
            await CreatureCmd.TriggerAnim(rightEnemy, "Attack", 0f);
            await Cmd.Wait(0.1f);
            PlayBluntVfx(leftEnemy);
            SpawnHitSpark(vfxContainer, leftEnemy);
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
