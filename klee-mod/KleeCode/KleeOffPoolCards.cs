using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Klee cards that BELONG to her pool but must never be GENERATED from it:
/// the companion roster (the 4th reward slot is their only door), the kit
/// Burst card (granted by KitGrant), and the token statuses (created at play).
///
/// WHY THIS SHAPE (playtest 2026-07-21, two attempts).
///
/// Every card must resolve <c>CardModel.Pool</c>, which walks
/// ModelDb.AllCardPools and, finding nothing, probes MockCardPool -- whose
/// generator throws InvalidOperationException("You monster!") in a shipped
/// build. Pool is read by NCard.Reload, so a poolless card crashes when a card
/// NODE is built: on DRAW and on PREVIEW, never on play. Symptoms were a
/// softlocked combat, a reward button that did nothing, an empty deck screen,
/// and cards rendering with the engine's own "If you can read this, there is a
/// bug." placeholder -- Reload throws at the Pool read BEFORE it populates the
/// description label, so the scene's default text survives.
///
/// ATTEMPT 1 (wrong): a second CardPoolModel to hold them. It could never
/// work. ModelDb.AllCardPools is
/// <c>AllCharacters.Select(c =&gt; c.CardPool)</c> concatenated with a HARDCODED
/// array of 7 shared pools. There is no registration hook: a mod pool that is
/// not some character's CardPool is invisible to the very lookup it was
/// created to satisfy. The lint added alongside it passed, because the lint
/// checked source membership -- not that the engine could see the pool.
///
/// ATTEMPT 2 (this): the cards go into KleeCardPool, which IS visible (Klee is
/// a character, so her pool is in AllCharacterCardPools), and KleeCardPool
/// overrides <c>FilterThroughEpochs</c> to strip them from
/// <c>GetUnlockedCards</c>. That split is the engine's own idiom, not a trick:
/// AllCards means "belongs to this pool" and backs the Pool lookup, while
/// GetUnlockedCards means "may be generated" and is the sole path into BOTH
/// reward rolls (CardCreationOptions.GetPossibleCards) and card transforms
/// (CardFactory, line 174). Nothing else generates from a pool.
///
/// So: Pool resolves, and no generator can reach them. The design constraint
/// -- companions arrive only through the companion slot -- is unchanged.
/// </summary>
public static class KleeOffPoolCards
{
    private static List<CardModel>? _all;

    /// <summary>The never-generated cards, in KleeCardPool but not in rolls.</summary>
    public static IReadOnlyList<CardModel> All => _all ??= BuildAll();

    private static List<CardModel> BuildAll()
    {
        // Companions: the reward slot (CompanionSlot.Roll) is their only door.
        var cards = new List<CardModel>(CompanionRoster.All)
        {
            // Kit Burst card: granted to hand by KitGrant when the meter
            // fills, never draftable or transformable.
            ModelDb.Card<SparksNSplash>(),

            // Token status: created at play time by Fish Blasting.
            ModelDb.Card<Confiscated>(),
        };
        return cards;
    }

    private static HashSet<ModelId>? _ids;

    /// <summary>Id set for the pool's generation filter.</summary>
    public static HashSet<ModelId> Ids =>
        _ids ??= All.Select(c => c.Id).ToHashSet();
}
