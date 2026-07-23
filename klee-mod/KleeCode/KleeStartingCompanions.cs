using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod;

/// <summary>
/// Resolves Klee's two randomized starter slots once the run seed is known.
///
/// Player.CreateForNewRun populates Character.StartingDeck before a RunState
/// (and therefore before seeded RNG) exists. RunState.CreateForNewRun is the
/// first safe seam: the deck is populated but its cards have not yet been
/// registered with the run. A dedicated seed-derived stream keeps multiplayer
/// peers and save replays deterministic without consuming any native RNG.
/// </summary>
[HarmonyPatch(typeof(RunState), nameof(RunState.CreateForNewRun))]
internal static class KleeStartingCompanionsPatch
{
    [HarmonyPrefix]
    public static void Prefix(IReadOnlyList<Player> players, string seed)
    {
        for (var slot = 0; slot < players.Count; slot++)
        {
            var player = players[slot];
            if (player.Character is Klee)
            {
                ResolveKlee(player, seed, slot);
            }
            else if (player.Character is Furina)
            {
                ResolveFurina(player, seed, slot);
            }
        }
    }

    private static void ResolveKlee(Player player, string seed, int slot)
    {
        var playerSeed = unchecked(
            (uint)(StringHelper.GetDeterministicHashCode(seed) + slot));
        var rng = new Rng(playerSeed, "klee_starting_companions");

        CardModel attack = rng.NextBool()
            ? ModelDb.Card<DahliaSacramentalShower>()
            : ModelDb.Card<KaeyaFrostgnaw>();
        CardModel support = rng.NextBool()
            ? ModelDb.Card<BarbaraMelody>()
            : ModelDb.Card<PruneWitchHunt>();

        var attackOk = ReplaceFirst<Kaboom>(player, attack);
        var supportOk = ReplaceFirst<DuckAndCover>(player, support);
        if (!attackOk || !supportOk)
        {
            Log.Error($"[{KleeMod.ModId}] could not resolve Klee's "
                    + "randomized starter Companion slots; keeping any "
                    + "unreplaced basics.");
        }
    }

    private static void ResolveFurina(Player player, string seed, int slot)
    {
        var playerSeed = unchecked(
            (uint)(StringHelper.GetDeterministicHashCode(seed) + slot));
        var rng = new Rng(playerSeed, "furina_starting_companions");

        CardModel attack = rng.NextBool()
            ? ModelDb.Card<ChevreuseInterdictionFire>()
            : ModelDb.Card<FreminetPersDeploy>();
        CardModel support = rng.NextBool()
            ? ModelDb.Card<CharlotteEnduringFrosthelm>()
            : ModelDb.Card<LynetteEnigmaticFeint>();

        var attackOk = ReplaceFirst<SoloistsSolicitation>(player, attack);
        var supportOk = ReplaceFirst<StagePresence>(player, support);
        if (!attackOk || !supportOk)
        {
            Log.Error($"[{KleeMod.ModId}] could not resolve Furina's "
                    + "randomized starter Companion slots; keeping any "
                    + "unreplaced basics.");
        }
    }

    private static bool ReplaceFirst<TBasic>(Player player,
                                              CardModel canonicalReplacement)
        where TBasic : CardModel
    {
        var old = player.Deck.Cards.FirstOrDefault(card => card is TBasic);
        if (old == null)
        {
            return false;
        }

        var index = player.Deck.Cards.ToList().IndexOf(old);
        player.Deck.RemoveInternal(old, silent: true);

        var replacement = canonicalReplacement.ToMutable();
        replacement.FloorAddedToDeck = 1;
        player.Deck.AddInternal(replacement, index, silent: true);
        return true;
    }
}
