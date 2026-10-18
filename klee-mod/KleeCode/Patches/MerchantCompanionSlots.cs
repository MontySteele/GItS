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
    /// THE BASE GAME'S SHAPE ([USER] 2026-10-18, legacy review pick 2:
    /// "Agreed on all 6 legacy picks"). Base <c>PopulateColorlessCardEntries</c>
    /// stocks a fixed Uncommon and a fixed Rare, and so do these two slots now:
    /// slot 1 (home nation) is an Uncommon, slot 2 (any nation) a Rare. No
    /// rarity is rolled. The 0.875 / 0.125 conditioned roll both slots used to
    /// take is gone.
    ///
    /// Each array is the slot's rarity FIRST, then the band it falls back to
    /// when no companion of that rarity can be offered at any nation. Slot 2
    /// falling back to Uncommon is the ruling's own wording; slot 1 keeps Rare
    /// as its roster-gap rung, so a slot is omitted only when neither band has
    /// a drawable companion. Mirrors <c>C.SHOP_COMPANION_SLOT_RARITIES</c>
    /// (tier05/shop.py walks the same ladders).
    /// </summary>
    private static readonly CardRarity[] SlotOneRarities =
        { CardRarity.Uncommon, CardRarity.Rare };

    private static readonly CardRarity[] SlotTwoRarities =
        { CardRarity.Rare, CardRarity.Uncommon };

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

        // --- Slot 1: home region, a fixed UNCOMMON. The targeted "buy your
        // dream support" slot (§4.7), in base slot 1's shape. ---
        AddSlot(__instance, player, entries,
            SlotOneRarities[0], CompanionPool.HomeNation(player), slot: 1,
            fallbackRarities: SlotOneRarities);

        // --- Slot 2: ANY NATION, a fixed RARE, in base slot 2's shape;
        // Uncommon when no Rare companion can be offered. ---
        AddSlot(__instance, player, entries, SlotTwoRarities[0], nation: null, slot: 2,
            fallbackRarities: SlotTwoRarities);

        // Skip the base colorless fill. Both slots are normally stocked; a
        // slot whose ladder ran out is OMITTED (see AddSlot), which leaves
        // the merchant with fewer colorless entries rather than with a base
        // card the sim never models. Falling through to the base fill instead
        // is not the alternative -- that would restock BOTH slots from the
        // colorless pool, including the one that filled fine.
        return false;
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
    /// nation as falling through.
    ///
    /// THE LAST RUNG IS OMISSION, AND OMISSION HAPPENS UPSTREAM OF Populate
    /// ([USER] 2026-08-10). It used to be a single base colorless entry for
    /// this slot, which is where the mod and tier05/shop.py disagreed: the
    /// sim models no base colorless pool, so it drops the slot. Two engines
    /// with two different last rungs is two different games on paper even
    /// when the rung is unreachable, so the divergence was ruled shut in the
    /// SIM'S favour -- the mod omits the slot too.
    ///
    /// WHY THIS DOES NOT REOPEN THE SOFTLOCK. The hard constraint above is
    /// about Populate: it has no "no card" path, and CreateForMerchant ends
    /// in Rng.NextItem over a filtered list that must not be empty. This
    /// method only ever reaches `new MerchantCardEntry(...)` / `Populate()`
    /// on a `candidates` list it has just checked is non-empty; the omission
    /// branch RETURNS BEFORE constructing anything, so no entry exists to
    /// populate, no null is handed to Populate, and nothing is added to
    /// `entries`. The slot is not created rather than created empty. The
    /// merchant's entry list is built by iteration, so a shorter list is a
    /// shorter shelf -- the same shape the base game produces when a pool
    /// runs thin -- and never an entry in an unpopulated state.
    ///
    /// Reaching the omission rung needs the roster to supply no drawable
    /// companion at ANY nation in EITHER band, which
    /// `tools/lint_companion_shop_coverage.py` fails the build over.
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

        List<CardModel> Draw(CardRarity r, string? n)
        {
            IEnumerable<CardModel> drawn = CompanionPool.Eligible(player, r, n);
            return drawn.Where(c => !stocked.Contains(c)).ToList();
        }

        fallbackRarities ??= new[] { rarity };

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
            // The rarity rung. Walk the SLOT'S OWN ladder in order -- picking
            // a "best" fallback would be a balance choice hiding in an error
            // path -- and mirror tier05/shop.py, which walks the same ladder.
            foreach (var other in fallbackRarities)
            {
                if (other == rarity) continue;
                candidates = Draw(other, null);
                if (candidates.Count == 0) continue;
                chosenRarity = other;
                Log.Warn($"[{KleeMod.ModId}] shop slot {slot} found no {rarity} "
                       + $"companion at any nation; falling back to {other}.");
                break;
            }
        }

        if (candidates.Count == 0)
        {
            // LAST RUNG: OMIT THE SLOT ([USER] 2026-08-10). Return before any
            // MerchantCardEntry is constructed -- see the reachability
            // argument in this method's doc comment. Populate is never
            // reached on this path because there is nothing to populate; the
            // slot simply does not exist this visit, which is what
            // tier05/shop.py has always done and is now what both engines do.
            //
            // This replaces a base-colorless fallback entry (R60 kept
            // ColorlessCardPool populated partly for that rung; its six
            // non-shop consumers, including all three GetDistinctForCombat
            // sites, are untouched by this and R60's no-emptying rule still
            // stands).
            Log.Warn($"[{KleeMod.ModId}] shop slot {slot} has NO drawable "
                   + "companion at any nation or rarity; the slot is OMITTED "
                   + "this visit. The companion roster cannot fill the shop -- "
                   + "this is a content bug, not a shop bug, and "
                   + "lint_companion_shop_coverage should have failed the "
                   + "build before a player ever saw it.");
            return;
        }

        var entry = new MerchantCardEntry(player, inventory, candidates, chosenRarity);
        entry.Populate();
        entries.Add(entry);
    }
}
