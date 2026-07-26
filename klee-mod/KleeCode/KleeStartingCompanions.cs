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
            else if (player.Character is Kokomi)
            {
                ResolveKokomi(player, seed, slot);
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

    /// <summary>
    /// Kokomi's slot is ONE, not two, and it is a different shape from the
    /// other two characters'.
    ///
    /// Klee and Furina each roll two Companions IN PLACE OF two basics. Her
    /// companions are ADDITIONS -- the 11th and 12th cards of a 12-card deck
    /// -- so Gorou sits in the authored StartingDeck directly and is not
    /// rolled at all: the adjutant ALWAYS enlists, for lore reasons (R52 N3).
    /// Only the support seat rolls, Sayu or Shinobu.
    ///
    /// The asymmetry against Klee and Furina's 2x2 is intended, not an
    /// oversight: the starter-reserved Inazuma trio is THREE characters
    /// across a two-slot convention, and Gorou is the only attack-slot name
    /// on the shortlist.
    ///
    /// The roll still burns its own Rng instance off the same seed+slot
    /// derivation, so peers and replays agree and no native stream is
    /// consumed. It draws ONE bool where the others draw two -- that is
    /// fine, the stream is hers alone.
    /// </summary>
    private static void ResolveKokomi(Player player, string seed, int slot)
    {
        var playerSeed = unchecked(
            (uint)(StringHelper.GetDeterministicHashCode(seed) + slot));
        var rng = new Rng(playerSeed, "kokomi_starting_companions");

        CardModel support = rng.NextBool()
            ? ModelDb.Card<SayuDarumaGift>()
            : ModelDb.Card<ShinobuGrassRingBond>();

        // Sayu is in the authored deck, so the "replacement" is a no-op half
        // the time -- deliberately still routed through ReplaceFirst so the
        // deck INDEX is identical on both arms. A conditional skip would put
        // Shinobu at a different position than Sayu, and card order is
        // visible in the deck view.
        if (!ReplaceFirst<SayuDarumaGift>(player, support))
        {
            Log.Error($"[{KleeMod.ModId}] could not resolve Kokomi's "
                    + "randomized starter Companion slot; keeping the "
                    + "authored Sayu.");
        }
    }

    /// <summary>
    /// Swap the first authored <typeparamref name="TBasic"/> out of the
    /// starting deck for <paramref name="canonicalReplacement"/>, in place.
    ///
    /// C1: the match is EXACT (`GetType() == typeof(TBasic)`), not `is`.
    /// `is` matches any subclass, and this method's whole contract is "find the
    /// authored basic I put in the starting deck". No card derives from these
    /// five types today, so this changes nothing now -- it is the shape that is
    /// wrong. The day an upgraded or reskinned variant is modelled as a
    /// subclass of its basic (the obvious way to model it), `is` would start
    /// silently eating that variant out of the starting deck instead, and the
    /// symptom would be a missing card in a run nobody could reproduce.
    /// Exact-match costs nothing and says what is meant.
    /// </summary>
    private static bool ReplaceFirst<TBasic>(Player player,
                                              CardModel canonicalReplacement)
        where TBasic : CardModel
    {
        var old = player.Deck.Cards
            .FirstOrDefault(card => card.GetType() == typeof(TBasic));
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
