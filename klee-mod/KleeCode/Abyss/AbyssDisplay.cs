using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Relics;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod.Abyss;

/// <summary>
/// THE IN-RUN DISPLAY of the Spiral Abyss (2026-10-12): the relics that show
/// each player what was taken, and the badges that show each enemy (or, for
/// a Shadow that acts on the player, each player) what it carries. DISPLAY ONLY -- nothing here changes a number. The effects are
/// the <see cref="SpiralAbyss"/> modifier's hooks and stay there.
///
/// Every decision is a pure planner (<see cref="BlessingsToGrant"/>,
/// <see cref="NeedsShadowsRelic"/>, <see cref="ShadowsToShow"/>) over what the
/// run recorded and what the player or creature already holds, so a second
/// call -- the other copy of a shared event, a reload, a summon -- adds
/// nothing that is already there.
/// </summary>
public static class AbyssDisplay
{
    /// <summary>The one pool the display relics belong to: the base game's
    /// <c>DeprecatedRelicPool</c>, which nothing rolls from.</summary>
    public static readonly Type PoolType = typeof(DeprecatedRelicPool);

    public static IReadOnlyList<Type> RelicTypes { get; } = new[]
    {
        typeof(AbyssLeyLineRelic), typeof(AbyssAbyssalMoonRelic),
        typeof(AbyssMoonlitRestRelic), typeof(AbyssFirstStrikeRelic),
        typeof(AbyssElementalBurstRelic), typeof(AbyssResonanceRelic),
        typeof(AbyssCrystallizeRelic), typeof(AbyssFatefulFortuneRelic),
        typeof(AbyssOverflowRelic), typeof(AbyssVigorOfTheAbyssRelic),
        typeof(AbyssMoonlitSpringRelic), typeof(AbyssBattleRhythmRelic),
        typeof(AbyssWaveringMoonRelic), typeof(AbyssStarfellDraftRelic),
        typeof(AbyssShadowsRelic),
    };

    public static IReadOnlyList<Type> PowerTypes { get; } = new[]
    {
        typeof(AbyssClockShadowPower), typeof(AbyssMageShieldShadowPower),
        typeof(AbyssSheerColdShadowPower), typeof(AbyssElementalMarkShadowPower),
        typeof(AbyssHeraldShadowPower), typeof(AbyssRallyShadowPower),
        typeof(AbyssRiptideShadowPower), typeof(AbyssFatuiSkirmishersShadowPower),
        typeof(AbyssThornyGroundShadowPower), typeof(AbyssBulwarkShadowPower),
        typeof(AbyssFrenzyShadowPower), typeof(AbyssWitheringShadowPower),
    };

    /// <summary>Called once from <c>KleeMod.Initialize</c>, before the game
    /// builds its pools. <c>RelicModel.Pool</c> throws for a poolless relic,
    /// and this is the only pool these join.</summary>
    internal static void RegisterPool()
    {
        foreach (var type in RelicTypes)
        {
            try
            {
                ModHelper.AddModelToPool(PoolType, type);
            }
            catch (Exception e)
            {
                Log.Error($"[{KleeMod.ModId}] Spiral Abyss relic {type.Name} could not join its pool: {e}");
            }
        }
    }

    // ---- The planners (pure) ---------------------------------------------

    /// <summary>The Blessings the run has taken that this player does not yet
    /// show a relic for, in the order taken.</summary>
    public static IReadOnlyList<AbyssBlessing> BlessingsToGrant(
        IEnumerable<AbyssBlessing> taken, IEnumerable<RelicModel> held)
    {
        var shown = held.OfType<AbyssBlessingRelic>().Select(r => r.Blessing).ToHashSet();
        return taken.Where(b => b != AbyssBlessing.None && shown.Add(b)).ToList();
    }

    /// <summary>The Blessing relics this player holds whose Blessing is no
    /// longer in force: a This act Blessing once its act has ended
    /// (<c>review/ruled/abyss-pools-2-2026-10-12.md</c>, pick 1 (a)).</summary>
    public static IReadOnlyList<AbyssBlessingRelic> BlessingRelicsToRemove(
        IEnumerable<AbyssBlessing> inForce, IEnumerable<RelicModel> held)
    {
        var live = inForce.ToHashSet();
        return held.OfType<AbyssBlessingRelic>().Where(r => !live.Contains(r.Blessing)).ToList();
    }

    /// <summary>Whether this player still needs the Abyss Shadows relic: the
    /// run has a Shadow, and the player holds no copy.</summary>
    public static bool NeedsShadowsRelic(IEnumerable<AbyssShadow> applied, IEnumerable<RelicModel> held) =>
        applied.Any(s => s != AbyssShadow.None) && !held.OfType<AbyssShadowsRelic>().Any();

    /// <summary>The Shadow badges this creature still lacks, one per Shadow in
    /// force, on the side the Shadow acts on. The two that act on the player
    /// (<see cref="AbyssRules.ActsOnPlayer"/>: Withering, Sheer Cold) are worn
    /// by each player, the rest by each enemy (2026-10-18: seats read the
    /// player-side ones on the enemies as enemy effects). A creature that is
    /// neither -- a pet, a summon on the player's side -- wears none.</summary>
    public static IReadOnlyList<AbyssShadow> ShadowsToShow(
        bool isEnemy, bool isPlayer, IEnumerable<AbyssShadow> applied, IEnumerable<PowerModel> worn)
    {
        if (!isEnemy && !isPlayer) return Array.Empty<AbyssShadow>();
        var shown = worn.OfType<AbyssShadowPower>().Select(p => p.Shadow).ToHashSet();
        return applied.Where(s => s != AbyssShadow.None
                                  && AbyssRules.ActsOnPlayer(s) == !isEnemy
                                  && shown.Add(s)).ToList();
    }

    /// <summary>The Abyss Shadows relic's list: each Shadow with the act it
    /// was taken in, whose numbers its text prints.</summary>
    public static string ShadowsText(IEnumerable<(AbyssShadow Shadow, int Act)> shadows, int? elementAct = null)
    {
        var lines = shadows.Where(e => e.Shadow != AbyssShadow.None)
            .Select(e => CodeText.Format(AbyssOverlayText.ShadowLine, CodeText.Vars(
                ("Name", AbyssText.Name(e.Shadow)),
                ("Text", AbyssText.Text(e.Shadow, e.Act, elementAct ?? AbyssText.NoAct)))))
            .ToList();
        return lines.Count == 0 ? CodeText.Format(AbyssOverlayText.NoShadows) : string.Join("\n", lines);
    }

    // ---- The models ---------------------------------------------------------

    public static Type RelicTypeFor(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine => typeof(AbyssLeyLineRelic),
        AbyssBlessing.AbyssalMoon => typeof(AbyssAbyssalMoonRelic),
        AbyssBlessing.MoonlitRest => typeof(AbyssMoonlitRestRelic),
        AbyssBlessing.FirstStrike => typeof(AbyssFirstStrikeRelic),
        AbyssBlessing.ElementalBurst => typeof(AbyssElementalBurstRelic),
        AbyssBlessing.Resonance => typeof(AbyssResonanceRelic),
        AbyssBlessing.Crystallize => typeof(AbyssCrystallizeRelic),
        AbyssBlessing.FatefulFortune => typeof(AbyssFatefulFortuneRelic),
        AbyssBlessing.Overflow => typeof(AbyssOverflowRelic),
        AbyssBlessing.VigorOfTheAbyss => typeof(AbyssVigorOfTheAbyssRelic),
        AbyssBlessing.MoonlitSpring => typeof(AbyssMoonlitSpringRelic),
        AbyssBlessing.BattleRhythm => typeof(AbyssBattleRhythmRelic),
        AbyssBlessing.WaveringMoon => typeof(AbyssWaveringMoonRelic),
        AbyssBlessing.StarfellDraft => typeof(AbyssStarfellDraftRelic),
        _ => throw new ArgumentOutOfRangeException(nameof(b)),
    };

    public static Type PowerTypeFor(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock => typeof(AbyssClockShadowPower),
        AbyssShadow.MageShield => typeof(AbyssMageShieldShadowPower),
        AbyssShadow.SheerCold => typeof(AbyssSheerColdShadowPower),
        AbyssShadow.ElementalMark => typeof(AbyssElementalMarkShadowPower),
        AbyssShadow.Herald => typeof(AbyssHeraldShadowPower),
        AbyssShadow.Rally => typeof(AbyssRallyShadowPower),
        AbyssShadow.Riptide => typeof(AbyssRiptideShadowPower),
        AbyssShadow.FatuiSkirmishers => typeof(AbyssFatuiSkirmishersShadowPower),
        AbyssShadow.ThornyGround => typeof(AbyssThornyGroundShadowPower),
        AbyssShadow.Bulwark => typeof(AbyssBulwarkShadowPower),
        AbyssShadow.Frenzy => typeof(AbyssFrenzyShadowPower),
        AbyssShadow.Withering => typeof(AbyssWitheringShadowPower),
        _ => throw new ArgumentOutOfRangeException(nameof(s)),
    };

    private static RelicModel BlessingRelic(AbyssBlessing b) => b switch
    {
        AbyssBlessing.LeyLine => ModelDb.Relic<AbyssLeyLineRelic>(),
        AbyssBlessing.AbyssalMoon => ModelDb.Relic<AbyssAbyssalMoonRelic>(),
        AbyssBlessing.MoonlitRest => ModelDb.Relic<AbyssMoonlitRestRelic>(),
        AbyssBlessing.FirstStrike => ModelDb.Relic<AbyssFirstStrikeRelic>(),
        AbyssBlessing.ElementalBurst => ModelDb.Relic<AbyssElementalBurstRelic>(),
        AbyssBlessing.Resonance => ModelDb.Relic<AbyssResonanceRelic>(),
        AbyssBlessing.Crystallize => ModelDb.Relic<AbyssCrystallizeRelic>(),
        AbyssBlessing.FatefulFortune => ModelDb.Relic<AbyssFatefulFortuneRelic>(),
        AbyssBlessing.Overflow => ModelDb.Relic<AbyssOverflowRelic>(),
        AbyssBlessing.VigorOfTheAbyss => ModelDb.Relic<AbyssVigorOfTheAbyssRelic>(),
        AbyssBlessing.MoonlitSpring => ModelDb.Relic<AbyssMoonlitSpringRelic>(),
        AbyssBlessing.BattleRhythm => ModelDb.Relic<AbyssBattleRhythmRelic>(),
        AbyssBlessing.WaveringMoon => ModelDb.Relic<AbyssWaveringMoonRelic>(),
        AbyssBlessing.StarfellDraft => ModelDb.Relic<AbyssStarfellDraftRelic>(),
        _ => throw new ArgumentOutOfRangeException(nameof(b)),
    };

    private static PowerModel ShadowPower(AbyssShadow s) => s switch
    {
        AbyssShadow.Clock => ModelDb.Power<AbyssClockShadowPower>(),
        AbyssShadow.MageShield => ModelDb.Power<AbyssMageShieldShadowPower>(),
        AbyssShadow.SheerCold => ModelDb.Power<AbyssSheerColdShadowPower>(),
        AbyssShadow.ElementalMark => ModelDb.Power<AbyssElementalMarkShadowPower>(),
        AbyssShadow.Herald => ModelDb.Power<AbyssHeraldShadowPower>(),
        AbyssShadow.Rally => ModelDb.Power<AbyssRallyShadowPower>(),
        AbyssShadow.Riptide => ModelDb.Power<AbyssRiptideShadowPower>(),
        AbyssShadow.FatuiSkirmishers => ModelDb.Power<AbyssFatuiSkirmishersShadowPower>(),
        AbyssShadow.ThornyGround => ModelDb.Power<AbyssThornyGroundShadowPower>(),
        AbyssShadow.Bulwark => ModelDb.Power<AbyssBulwarkShadowPower>(),
        AbyssShadow.Frenzy => ModelDb.Power<AbyssFrenzyShadowPower>(),
        AbyssShadow.Withering => ModelDb.Power<AbyssWitheringShadowPower>(),
        _ => throw new ArgumentOutOfRangeException(nameof(s)),
    };

    // ---- The doers ------------------------------------------------------------

    /// <summary>
    /// Bring one player's relics up to what is in force in act
    /// <paramref name="act"/>: a relic for each Blessing in force that the
    /// player lacks, none for a This act Blessing whose act has ended (its
    /// relic goes), the Abyss Shadows relic once the run has a Shadow, and
    /// that relic's list redrawn to the Shadows in force. Called from the
    /// choice page for each player's copy of the shared event, so in co-op
    /// every player gets their own, and from the act-change hook; idempotent,
    /// so a second call changes nothing.
    /// </summary>
    public static async Task GrantTo(Player player, AbyssRecord record, int act)
    {
        var blessings = record.BlessingsInForce(act);
        var shadows = record.ShadowsInForce(act);

        foreach (var expired in BlessingRelicsToRemove(blessings, player.Relics))
        {
            await RelicCmd.Remove(expired);
        }

        foreach (var blessing in BlessingsToGrant(blessings, player.Relics))
        {
            await RelicCmd.Obtain(BlessingRelic(blessing).ToMutable(), player);
        }

        // The Shadows relic comes with the run's first Shadow and stays (an
        // empty list reads "None yet."), so a run whose only Shadow expired
        // keeps the relic it was shown.
        if (NeedsShadowsRelic(record.Shadows, player.Relics))
        {
            var relic = (AbyssShadowsRelic)ModelDb.Relic<AbyssShadowsRelic>().ToMutable();
            relic.SetShadows(shadows, record, act);
            await RelicCmd.Obtain(relic, player);
        }

        foreach (var shown in player.Relics.OfType<AbyssShadowsRelic>())
        {
            shown.SetShadows(shadows, record, act);
        }

        RefreshTexts(player, record, act);
    }

    /// <summary>
    /// NUMBERS BY ACT (<c>review/active/abyss-act-scaling-2026-10-18.md</c>):
    /// put the act each entry was taken in back on this player's Abyss relics,
    /// so each prints the number its effect uses. Display only, idempotent. A
    /// relic loaded from a save comes back with act 1's text (the act lives in
    /// the run's record, not the relic), so the modifier also calls this on
    /// every room, not only after a pick.
    /// </summary>
    public static void RefreshTexts(Player player, AbyssRecord record, int? currentAct = null)
    {
        foreach (var relic in player.Relics.OfType<AbyssBlessingRelic>())
        {
            relic.ShowAct(record.ActTaken(relic.Blessing), currentAct);
        }
        foreach (var shown in player.Relics.OfType<AbyssShadowsRelic>())
        {
            shown.SetShadows(shown.Shadows.ToList(), record, currentAct);
        }
    }

    /// <summary>
    /// Put a badge on <paramref name="creature"/> for each Shadow in force it
    /// does not yet wear: an enemy wears the enemy-side Shadows, a player the
    /// player-side ones (<see cref="ShadowsToShow"/>). Attached through
    /// <c>PowerModel.ApplyInternal</c> (see <see cref="AbyssShadowPower"/>),
    /// so no hook hears it.
    /// </summary>
    public static void ShowShadows(Creature creature, IEnumerable<AbyssShadow> inForce, AbyssRecord record,
                                   int? currentAct = null)
    {
        if (!creature.IsAlive || !creature.CanReceivePowers) return;
        var missing = ShadowsToShow(creature.Side == CombatSide.Enemy, creature.IsPlayer, inForce, creature.Powers);
        foreach (var shadow in missing)
        {
            // The badge prints the number of the act the Shadow was taken in.
            var badge = (AbyssShadowPower)ShadowPower(shadow).ToMutable();
            badge.ShowAct(record.ActTaken(shadow), currentAct);
            badge.ApplyInternal(creature, 1m, silent: true);
        }
    }
}
