using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// JUNGLE MAZE ADVENTURE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/JungleMazeAdventure.cs` and
/// cross-checked against the harvest (2 options: Solo Quest, Join Forces).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `IsShared`, the same three
/// vars (150 solo gold, 18 unblockable unpowered solo HP, 50 joined gold),
/// the same +/-15 float jitter on BOTH gold bands in `CalculateVars`, the
/// same multiplayer HP gate, the same three shuffled attack VFX with their
/// sounds and waits on the solo branch, and the same "hey" and short wait on
/// the joined one.
///
/// THE JITTER IS A FLOAT AND STAYS A FLOAT. `Rng.NextFloat(-15f, 15f)` cast
/// to decimal is what makes the harvest's bands read 135-165 and 35-65; a
/// tidier `NextInt(-15, 16)` would have been a different distribution and a
/// different number of rng draws.
///
/// THE VFX TABLE IS A STATIC FIELD, as it is in the base event, so the three
/// pairs are allocated once. It carries no loc key and no number a player
/// sees.
/// </summary>
public abstract class JungleMazeAdventureMirror : TeyvatEventMirror
{
    /// <summary>The base event's three VFX-and-sound pairs, shuffled per
    /// choice.</summary>
    private static readonly List<(string, string)> _fx = new List<(string, string)>
    {
        ("vfx/vfx_attack_blunt", "blunt_attack.mp3"),
        ("vfx/vfx_attack_slash", "slash_attack.mp3"),
        ("vfx/vfx_heavy_blunt", "heavy_attack.mp3"),
    };

    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>`JungleMazeAdventure.cs:32-37`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("SoloGold", 150m),
            new DamageVar("SoloHp", 18m, ValueProp.Unblockable | ValueProp.Unpowered),
            new DynamicVar("JoinForcesGold", 50m),
        };

    /// <summary>The base event's gate: solo always; co-op only while every
    /// player can survive the solo price.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.Players.Count == 1)
        {
            return true;
        }

        foreach (Player player in runState.Players)
        {
            if ((decimal)player.Creature.CurrentHp <= DynamicVars["SoloHp"].BaseValue)
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
            new EventOption(this, DontNeedHelp, InitialOptionKey("SOLO_QUEST"))
                .ThatDoesDamage(DynamicVars["SoloHp"].BaseValue),
            new EventOption(this, SafetyInNumbers, InitialOptionKey("JOIN_FORCES")),
        };

    /// <summary>The base event's rolls, both off the event's own rng and both
    /// as floats.</summary>
    public override void CalculateVars()
    {
        DynamicVars["SoloGold"].BaseValue += (decimal)Rng.NextFloat(-15f, 15f);
        DynamicVars["JoinForcesGold"].BaseValue += (decimal)Rng.NextFloat(-15f, 15f);
    }

    /// <summary>
    /// `DontNeedHelp`. Three VFX from the shuffled table -- the shuffle is
    /// `StableShuffle` off the EVENT's rng, so it is the same three in the
    /// same order for every client -- with a wait between the first two and
    /// none after the third, then the damage and the gold.
    /// </summary>
    private async Task DontNeedHelp()
    {
        List<(string, string)> shuffledFx = _fx.ToList().StableShuffle(Rng);
        for (int i = 0; i < 3; i++)
        {
            Control container = NEventRoom.Instance?.VfxContainer;
            if (LocalContext.IsMe(Owner) && container != null)
            {
                VfxCmd.PlayNonCombatVfx(
                    container,
                    new Vector2(container.Size.X * 0.25f, container.Size.Y * 0.5f),
                    shuffledFx[i].Item1);
                NDebugAudioManager.Instance.Play(shuffledFx[i].Item2);
            }

            if (i < 2)
            {
                await Cmd.CustomScaledWait(0.25f, 0.5f);
            }
        }

        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars["SoloHp"].BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        await PlayerCmd.GainGold(DynamicVars["SoloGold"].BaseValue, Owner);
        SetEventFinished(L10NLookup(PageKey("SOLO_QUEST.description")));
    }

    /// <summary>`SafetyInNumbers`: the hail, a beat, and the smaller
    /// purse.</summary>
    private async Task SafetyInNumbers()
    {
        NDebugAudioManager.Instance.Play("hey.mp3");
        await Cmd.CustomScaledWait(0f, 0.2f);
        await PlayerCmd.GainGold(DynamicVars["JoinForcesGold"].BaseValue, Owner);
        SetEventFinished(L10NLookup(PageKey("JOIN_FORCES.description")));
    }
}
