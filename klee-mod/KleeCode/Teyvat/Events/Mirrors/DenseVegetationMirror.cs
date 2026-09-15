using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx.Utilities;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// DENSE VEGETATION, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/DenseVegetation.cs` and cross-checked
/// against the harvest (2 options: Trudge On, Rest).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `IsShared`, the same three
/// vars, the same `Rng.NextInt(61, 100)` gold roll and rest-site heal amount
/// in `CalculateVars`, the same multiplayer HP gate, the same three slash
/// VFX and sounds before the 8 unblockable unpowered damage, and the same
/// `MimicRestSiteHeal` into a SECOND PAGE that offers one option: the fight.
///
/// THE SECOND PAGE IS WHY THIS MIRROR HAS AN `extra_options` ROW. `Rest`
/// calls `SetEventState` rather than `SetEventFinished`, and the option it
/// puts on that page -- `pages.REST.options.FIGHT` -- is an option KEY, so
/// the engine asks the loc table for its `.title` and its `.description`
/// exactly as it does for an INITIAL one. It has no face line of its own;
/// it takes the Rest line's, because it is the Rest branch continued.
///
/// THE ENCOUNTER IS THE BASE GAME'S. `DenseVegetationEventEncounter` is a
/// global model with global monster rows; the dressing renames the
/// WRIGGLERS through `Patches/MonsterNamePatch`'s dressed-key lookup and not
/// here, which is the same seam every dressed monster name goes through.
/// </summary>
public abstract class DenseVegetationMirror : TeyvatEventMirror
{
    /// <summary>The base event's own: a shared event, so every player is in
    /// the same room and `IsDeterministic` falls false with it.</summary>
    public override bool IsShared => true;

    /// <summary>`DenseVegetation.cs:29-34`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(0),
            new HealVar(0m),
            new HpLossVar(8m),
        };

    /// <summary>The base event's rolls: gold in 61-99 (`NextInt` is exclusive
    /// at the top) and the heal the rest site itself would have given.</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue = Rng.NextInt(61, 100);
        DynamicVars.Heal.BaseValue = (Owner != null) ? HealRestSiteOption.GetHealAmount(Owner) : 0m;
    }

    /// <summary>
    /// The base event's gate: a solo run always; a co-op run only while every
    /// player can survive the Trudge On price. The loop and its early return
    /// are the base event's shape, not a rewrite of it.
    /// </summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.Players.Count == 1)
        {
            return true;
        }

        foreach (Player player in runState.Players)
        {
            if ((decimal)player.Creature.CurrentHp <= DynamicVars.HpLoss.BaseValue)
            {
                return false;
            }
        }

        return true;
    }

    /// <summary>Two options, in the base event's order, under its names, with
    /// the damage annotation on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, TrudgeOn, InitialOptionKey("TRUDGE_ON"))
                .ThatDoesDamage(DynamicVars.HpLoss.BaseValue),
            new EventOption(this, Rest, InitialOptionKey("REST")),
        };

    /// <summary>
    /// `TrudgeOn`. Three slashes at randomised offsets and rotations, each
    /// with the base event's own sound and wait, then the damage and the
    /// gold. The VFX is inside `LocalContext.IsMe` for the base event's
    /// reason: in co-op only the acting player's client plays it.
    /// </summary>
    private async Task TrudgeOn()
    {
        Control container = NEventRoom.Instance?.VfxContainer;
        if (LocalContext.IsMe(Owner) && container != null)
        {
            for (int i = 0; i < 3; i++)
            {
                Vector2 centre = new Vector2(container.Size.X * 0.25f, container.Size.Y * 0.6f);
                Vector2 jitter = new Vector2(
                    MegaCrit.Sts2.Core.Random.Rng.Chaotic.NextFloat(-100f, 100f),
                    MegaCrit.Sts2.Core.Random.Rng.Chaotic.NextFloat(-200f, 200f));
                Node2D slash = VfxCmd.PlayNonCombatVfx(container, centre + jitter, "vfx/vfx_attack_slash");
                Node2D slice = VfxCmd.PlayNonCombatVfx(container, centre + jitter, "vfx/events/dense_vegetation_slice_vfx");
                NDebugAudioManager.Instance.Play("slash_attack.mp3", 0.8f, PitchVariance.Medium);
                slash.RotationDegrees = -MegaCrit.Sts2.Core.Random.Rng.Chaotic.NextFloat() * 180f;
                slice.RotationDegrees = -MegaCrit.Sts2.Core.Random.Rng.Chaotic.NextFloat() * 180f;
                await Cmd.CustomScaledWait(0.2f, 0.4f);
            }
        }

        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.HpLoss.BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        await PlayerCmd.GainGold(DynamicVars.Gold.BaseValue, Owner);
        SetEventFinished(L10NLookup(PageKey("TRUDGE_ON.description")));
    }

    /// <summary>
    /// `Rest`. The rest-site heal with the rest site's SFX suppressed, the
    /// sleep-then-hiss the base event plays instead, and then the second page
    /// with its single Fight option.
    /// </summary>
    private async Task Rest()
    {
        await PlayerCmd.MimicRestSiteHeal(Owner, playSfx: false);
        if (LocalContext.IsMe(Owner))
        {
            int restHandle = NDebugAudioManager.Instance.Play("sleep.tres", 0.8f);
            await Cmd.CustomScaledWait(0.7f, 1.5f);
            NDebugAudioManager.Instance.Stop(restHandle);
            NDebugAudioManager.Instance.Play("hiss.mp3", 0.8f, PitchVariance.Large);
            NGame.Instance.ScreenRumble(ShakeStrength.Medium, ShakeDuration.Normal, RumbleStyle.Rumble);
        }

        SetEventState(L10NLookup(PageKey("REST.description")), new List<EventOption>
        {
            new EventOption(this, Fight, PageKey("REST.options.FIGHT")),
        });
    }

    /// <summary>`Fight`: the base event's encounter, with no extra rewards and
    /// no resume -- the event is over whichever way the fight goes.</summary>
    private Task Fight()
    {
        EnterCombatWithoutExitingEvent<DenseVegetationEventEncounter>(
            Array.Empty<Reward>(), shouldResumeAfterCombat: false);
        return Task.CompletedTask;
    }
}
