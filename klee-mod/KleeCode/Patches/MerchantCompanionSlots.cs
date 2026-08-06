using System;
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
    /// SLOT 1's Uncommon share: tier0 RARITY_ODDS CONDITIONED on
    /// >= Uncommon -- Uncommon 0.35 and Rare 0.05 renormalize to 0.875 /
    /// 0.125. NC-10 (R116) respecified slot 1 as "Uncommon or higher from the
    /// home region", so the floor's odds are this slot's now; it used to be
    /// slot 2's, and slot 1 was hard-wired to Uncommon with no roll at all.
    ///
    /// THE ALTERNATIVE READING, surfaced and NOT chosen, because R116 said
    /// so in as many words ("a renormalization chosen by an implementer is a
    /// balance value chosen by an implementer"): the floor could carry a
    /// STATED SPLIT instead -- odds designed for the premium slot rather
    /// than inherited from the reward table. Conditioning is the reading that
    /// introduces no new number, so it is the one implemented; the split is a
    /// [USER] call. See tier0/constants.py, same note.
    /// </summary>
    private const float SlotOneUncommonOdds = 0.875f;

    /// <summary>
    /// SLOT 2's table: tier0 RARITY_ODDS itself, UNCONDITIONED. "Any
    /// companion card" (R116) is the absence of a filter, and the absence of
    /// a filter is the reward table with nothing cut out of it -- so this
    /// slot can offer a Common, at the Common band, which it could not
    /// before. Pricing needs no new number here: MerchantCardEntry.GetCost
    /// already carries 50/75/150 by rarity.
    /// </summary>
    private const float SlotTwoCommonOdds = 0.60f;

    /// <summary>Slot 2's Uncommon share of tier0 RARITY_ODDS.</summary>
    private const float SlotTwoUncommonOdds = 0.35f;

    /// <summary>
    /// The bands each slot may fall back through when its drawn corner is
    /// empty, IN TABLE ORDER -- slot 1 keeps its floor even on the fallback
    /// rung, slot 2 has none to keep. Mirrors the odds dicts tier05/shop.py
    /// walks for the same rung.
    /// </summary>
    private static readonly CardRarity[] SlotOneRarities =
        { CardRarity.Uncommon, CardRarity.Rare };

    private static readonly CardRarity[] SlotTwoRarities =
        { CardRarity.Common, CardRarity.Uncommon, CardRarity.Rare };

    /// <summary>
    /// F2. This was a bare `AccessTools.FieldRefAccess<...>("_colorlessCardEntries")`
    /// in a static field initializer, and FieldRefAccess THROWS on a name that
    /// no longer resolves. A throw in a static initializer becomes a
    /// TypeInitializationException on first use -- and first use is inside this
    /// Prefix, which runs when the player walks into a shop. So a renamed
    /// private field turned into a black-screened shop, hours into a run: the
    /// exact softlock class this patch's neighbours exist to prevent, produced
    /// by the guard itself.
    ///
    /// Resolved through a method with its own catch so the static ctor cannot
    /// throw, and left nullable so the Prefix can decide. That is the
    /// CreatureFacing pattern (a null degrades to no facing, not to an
    /// exception) applied where the cost of the alternative is a lost run.
    /// </summary>
    private static readonly AccessTools.FieldRef<MerchantInventory, List<MerchantCardEntry>>?
        ColorlessEntries = ResolveColorlessEntries();

    private static AccessTools.FieldRef<MerchantInventory, List<MerchantCardEntry>>?
        ResolveColorlessEntries()
    {
        try
        {
            return AccessTools.FieldRefAccess<MerchantInventory, List<MerchantCardEntry>>(
                "_colorlessCardEntries");
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] MerchantInventory._colorlessCardEntries did not "
                    + $"resolve ({e.GetType().Name}). The companion shop channel (R60/S4.7) "
                    + "is OFF this session; shops fall back to the base colourless fill. "
                    + "Shops still work -- the premium slot is simply absent.");
            return null;
        }
    }

    private static bool _warnedNoColorlessField;

    [HarmonyPrefix]
    public static bool Prefix(MerchantInventory __instance)
    {
        var player = __instance.Player;
        // Base-game characters get a completely unmodified shop.
        if (!CompanionPool.HostsCompanions(player)) return true;

        if (ColorlessEntries is not { } colorlessEntries)
        {
            // Degrade to the base game's colorless fill rather than throwing
            // into MerchantRoom.EnterInternal's async continuation, which is
            // the thing that black-screens instead of crashing.
            if (!_warnedNoColorlessField)
            {
                _warnedNoColorlessField = true;
                Log.Warn($"[{KleeMod.ModId}] companion shop slots skipped: the entries field "
                       + "never resolved (see the boot error). Base colourless fill runs.");
            }

            return true;
        }

        var entries = colorlessEntries(__instance);

        // --- Slot 1: home region, UNCOMMON OR HIGHER (NC-10 / R116). The
        // targeted "buy your dream support" slot (§4.7). It used to be
        // hard-wired to Uncommon and therefore could never offer a Rare at
        // all -- the flagship example of the semantic-parity gap S14 was
        // chartered to find, because the constant the parity lint compares
        // matched on both sides while the behaviour did not. ---
        var slotOneRarity = player.PlayerRng.Shops.NextFloat() < SlotOneUncommonOdds
            ? CardRarity.Uncommon
            : CardRarity.Rare;
        AddSlot(__instance, player, entries,
            slotOneRarity, CompanionPool.HomeNation(player), slot: 1,
            fallbackRarities: SlotOneRarities);

        // --- Slot 2: ANY COMPANION CARD (NC-10 / R116). No nation, no floor,
        // full reward odds -- so this slot offers Commons now, priced at the
        // Common band. R59 read the floor as covering both slots on the
        // argument that a ~60%-Common wildcard is worse than the guaranteed
        // Rare it replaces; R116 heard that argument and specified the slot
        // anyway. ---
        var slotTwoRoll = player.PlayerRng.Shops.NextFloat();
        var slotTwoRarity = slotTwoRoll < SlotTwoCommonOdds
            ? CardRarity.Common
            : slotTwoRoll < SlotTwoCommonOdds + SlotTwoUncommonOdds
                ? CardRarity.Uncommon
                : CardRarity.Rare;
        AddSlot(__instance, player, entries, slotTwoRarity, nation: null, slot: 2,
            fallbackRarities: SlotTwoRarities);

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
        List<MerchantCardEntry> entries, CardRarity rarity, string? nation, int slot,
        IReadOnlyList<CardRarity>? fallbackRarities = null)
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

        fallbackRarities ??= new[] { CardRarity.Uncommon, CardRarity.Rare };

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
            // The rarity rung, generalized for NC-10: slot 2's table has
            // three entries now, not two. Walk the SLOT'S OWN rarities in
            // the table's order -- picking a "best" fallback would be a
            // balance choice hiding in an error path -- and mirror
            // tier05/shop.py, which walks its odds dict the same way.
            foreach (var other in fallbackRarities)
            {
                if (other == rarity) continue;
                candidates = Draw(other, null);
                if (candidates.Count == 0) continue;
                chosenRarity = other;
                Log.Warn($"[{KleeMod.ModId}] shop slot {slot} found no {rarity} "
                       + $"companion at any nation; dropping to {other}. This "
                       + "crosses the slot's rarity band and should be treated "
                       + "as a roster gap, not as intended behaviour.");
                break;
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
            // chosenRarity, not rarity. Every other reader of this ladder
            // prices off chosenRarity -- the slot's ACTUAL rarity -- and this
            // one rung read the requested rarity instead. Today the two are
            // provably equal here (chosenRarity only moves on a rung that
            // found candidates, and reaching this branch means none did), so
            // this is a correctness repair rather than a behaviour change:
            // add one more rung above that downgrades and succeeds partially,
            // and the old line would silently price a downgraded card at the
            // original rarity. Fixed 2026-07-29.
            var baseEntry = new MerchantCardEntry(player, inventory, basePool, chosenRarity);
            baseEntry.Populate();
            entries.Add(baseEntry);
            return;
        }

        var entry = new MerchantCardEntry(player, inventory, candidates, chosenRarity);
        entry.Populate();
        entries.Add(entry);
    }
}
