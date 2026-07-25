using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Merchant;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;

namespace KleeMod.Patches;

/// <summary>
/// §4.7 Track B: the shop's two colorless slots carry COMPANIONS.
///
/// THE SURFACE. MerchantInventory.PopulateColorlessCardEntries builds exactly
/// two MerchantCardEntry objects from ModelDb.CardPool&lt;ColorlessCardPool&gt;()
/// at a hardcoded [Uncommon, Rare]. An entry holds its card list and its
/// rarity for the whole shop visit and re-rolls from them on restock, so
/// substituting the LIST at populate time is the whole job: pricing, the
/// duplicate-suppression Except(), the upgrade roll and restock all stay
/// native. That is why this is a prefix that rebuilds both entries rather than
/// a postfix that rewrites their results.
///
/// WHY NOT THE SANCTIONED HOOK. CardFactory.CreateForMerchant calls
/// Hook.ModifyMerchantCardPool and Hook.ModifyMerchantCardRarity, which are
/// first-class AbstractModel overrides and would need no Harmony at all. They
/// were rejected on discrimination, not taste: both fire for the FIVE
/// character-card entries as well, the pool hook fires BEFORE the rarity hook
/// (so it cannot know which colorless slot it is serving), and neither is told
/// which entry is being populated. Slot 1 differs from slot 2 only by the
/// nation filter, so a surface that cannot tell the slots apart cannot
/// implement §4.7. Patching Populate's caller gives us both slots in order,
/// once, with the inventory in hand.
///
/// R60 PHASE 1: this REDIRECTS the shop and nothing else. ColorlessCardPool
/// stays populated for its six non-shop consumers, including all three
/// GetDistinctForCombat sites -- emptying it is the empty-draw softlock class
/// that Dusty Tome already cost us once.
///
/// PRICING IS NATIVE, WITH ONE DELIBERATE LOSS. MerchantCardEntry.GetCost is
/// 50/75/150 by rarity, then x1.15 iff `card.Pool is ColorlessCardPool`.
/// Companions resolve Pool to their character's pool (see CompanionPool for
/// why they are not a pool of their own), so they are priced at the BASE
/// bands and do not collect the colorless surcharge. That matches §4.7 as
/// written -- "base shop-card gold bands by drawn rarity" -- but it does mean
/// the mod's premium channel is ~15% cheaper than the one it replaces, and
/// pricing is supposed to be the balance governor. Flagged at close-out; the
/// tier 0.5 channel (Track C) prices the same way, so sim and mod agree.
/// </summary>
[HarmonyPatch(typeof(MerchantInventory), "PopulateColorlessCardEntries")]
internal static class MerchantInventory_CompanionColorlessSlots_Patch
{
    /// <summary>
    /// tier0 RARITY_ODDS renormalized onto {Uncommon, Rare} -- R59's floor.
    /// Uncommon 0.35 and Rare 0.05 renormalize to 0.875 / 0.125.
    /// </summary>
    private const float SlotTwoUncommonOdds = 0.875f;

    private static readonly AccessTools.FieldRef<MerchantInventory, List<MerchantCardEntry>>
        ColorlessEntries = AccessTools.FieldRefAccess<MerchantInventory, List<MerchantCardEntry>>(
            "_colorlessCardEntries");

    [HarmonyPrefix]
    public static bool Prefix(MerchantInventory __instance)
    {
        var player = __instance.Player;
        // Base-game characters get a completely unmodified shop.
        if (!CompanionPool.HostsCompanions(player)) return true;

        var entries = ColorlessEntries(__instance);

        // --- Slot 1: home region, Uncommon floor. The targeted "buy your
        // dream support" slot (§4.7). ---
        AddSlot(__instance, player, entries,
            CardRarity.Uncommon, CompanionPool.HomeNation(player), slot: 1);

        // --- Slot 2: wildcard nation, Uncommon floor at renormalized odds
        // (R59). The floor is the ruling: a wildcard at full reward odds would
        // be ~60% Common, which is WORSE than the guaranteed Rare it replaces,
        // at the one slot whose entire argument is that it is premium. ---
        var slotTwoRarity = player.PlayerRng.Shops.NextFloat() < SlotTwoUncommonOdds
            ? CardRarity.Uncommon
            : CardRarity.Rare;
        AddSlot(__instance, player, entries, slotTwoRarity, nation: null, slot: 2);

        return false;   // both slots stocked; skip the base colorless fill
    }

    /// <summary>
    /// Stock one slot, falling back rather than crashing when the requested
    /// (nation x rarity) corner is empty.
    ///
    /// AN EMPTY SHOP SLOT MUST BE A DECISION, NEVER A CRASH (Track D). The
    /// merchant's slot layout is load-bearing UI -- Populate has no "no card"
    /// path, and CreateForMerchant ends in Rng.NextItem over the filtered
    /// list, which has nothing to return from an empty sequence. This is the
    /// same failure shape as finding 24 (a Power-less pool soft locking every
    /// shop), so it gets the same treatment: substitute, log loudly, and stop
    /// substituting the moment the roster covers the corner.
    ///
    /// The ladder is deliberate. Widen the NATION before dropping the RARITY,
    /// because R59 ratified the floor and §4.7 only ever described slot 1's
    /// nation as falling through. The last rung is a single base colorless
    /// entry for THIS SLOT ONLY -- a bounded, shop-scoped read of the pool
    /// R60 keeps populated, so the shop degrades to base rather than to
    /// nothing.
    ///
    /// Live corner today: Fontaine designs ZERO Rare companions, so Furina's
    /// slot 1 can never roll one. That is exactly the brittleness R59 cites
    /// and it is why the floor is Uncommon rather than a guaranteed Rare.
    /// </summary>
    private static void AddSlot(
        MerchantInventory inventory, Player player,
        List<MerchantCardEntry> entries, CardRarity rarity, string? nation, int slot)
    {
        // Cards already stocked elsewhere in this inventory are excluded by
        // MerchantCardEntry.Populate itself; count them here too so the
        // fallback ladder measures what is ACTUALLY still drawable rather than
        // what exists on paper.
        var stocked = inventory.CardEntries
            .Select(e => e.CreationResult?.Card.CanonicalInstance)
            .OfType<CardModel>()
            .ToHashSet();

        List<CardModel> Draw(CardRarity r, string? n) =>
            CompanionPool.Eligible(player, r, n).Where(c => !stocked.Contains(c)).ToList();

        var candidates = Draw(rarity, nation);
        var chosenRarity = rarity;

        if (candidates.Count == 0 && nation != null)
        {
            candidates = Draw(rarity, null);
            if (candidates.Count > 0)
            {
                Log.Warn($"[{KleeMod.ModId}] shop slot {slot} wanted a {rarity} "
                       + $"companion from {nation} and the roster has none left; "
                       + "widening to every nation. Stops happening once that "
                       + "nation designs one.");
            }
        }

        if (candidates.Count == 0)
        {
            var other = rarity == CardRarity.Uncommon ? CardRarity.Rare : CardRarity.Uncommon;
            candidates = Draw(other, null);
            if (candidates.Count > 0)
            {
                chosenRarity = other;
                Log.Warn($"[{KleeMod.ModId}] shop slot {slot} found no {rarity} "
                       + $"companion at any nation; dropping to {other}. This "
                       + "crosses the R59 rarity floor and should be treated as "
                       + "a roster gap, not as intended behaviour.");
            }
        }

        if (candidates.Count == 0)
        {
            // Last rung: one base colorless entry, this slot only (R60 keeps
            // that pool populated precisely so this rung exists).
            Log.Warn($"[{KleeMod.ModId}] shop slot {slot} has NO drawable "
                   + "companion at any nation or rarity; falling back to a base "
                   + "colorless card for this slot. The companion roster cannot "
                   + "fill the shop -- this is a content bug, not a shop bug.");
            var basePool = ModelDb.CardPool<ColorlessCardPool>()
                .GetUnlockedCards(player.UnlockState, player.RunState.CardMultiplayerConstraint)
                .ToList();
            var baseEntry = new MerchantCardEntry(player, inventory, basePool, rarity);
            baseEntry.Populate();
            entries.Add(baseEntry);
            return;
        }

        var entry = new MerchantCardEntry(player, inventory, candidates, chosenRarity);
        entry.Populate();
        entries.Add(entry);
    }
}
