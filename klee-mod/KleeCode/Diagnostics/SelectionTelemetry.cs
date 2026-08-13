using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using HarmonyLib;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;

namespace KleeMod.Diagnostics;

/// <summary>
/// EB-14 — THE MOD-SIDE HOOK INTO THE SELECTION SCREENS.
///
/// The `selectors` channel (P1.5) was bot-feed only: the soak records a
/// selector answer because it POSTED it, while `PlayTelemetry` saw a card
/// leave a pile rather than an offer being taken from a list. This file is the
/// human-feed vantage. Rows land inside the open fight record, so they inherit
/// that record's `feed` and `source` labels and no second writer exists.
///
/// THE SWEEP, WHICH LAW REQUIRES BEFORE BUILDING INFRASTRUCTURE (precedent:
/// the "no combat-END hook" claim, retracted when `Hook.AfterCombatEnd` /
/// `AfterCombatVictory` turned out to be first-party). Swept 2026-08-12
/// against the pinned build — `sts2.dll` v0.107.1 (commit 59260271) and
/// BaseLib 3.3.7.0, both decompiled with ilspycmd 8.2.0:
///
///   * `AbstractModel` — the ~180 first-party virtuals the mod already rides
///     via `SubscribeForCombatStateHooks`. There is a hook for a card changing
///     PILES (`AfterCardChangedPiles`), for a reward being taken
///     (`AfterRewardTaken`), for a merchant purchase and for a rest-site
///     smith. There is NO hook for a card SELECTION: nothing reports the
///     offered list, and nothing fires when a selection screen resolves.
///   * `BaseLib.Hooks` — nine hook interfaces (`IAfterScryed`,
///     `IAfterCardDowngraded`, `IAfterSpendResource`, `IModifyScryAmount`,
///     `IMaxHandSizeModifier`, `IHealAmountModifier`, `ICardTypeTextModifier`,
///     `IModifyResourceCostInCombat`, `IHealthBarForecastSource`). None is
///     about selection. `BaseLib.Commands.MultiPileCardSelect` is an OPENER
///     (it shows a multi-pile grid), not an observer.
///   * `CardSelectCmd.ICardSelector` (`UseSelector` / `PushSelector`) — the
///     one thing that looks like an answer and is NOT one. It is the game's
///     automation seam ("used by tests, AutoSlay, and gameplay effects that
///     auto-play cards"), and a pushed selector BYPASSES the selection UI
///     entirely: installing one to watch a human choose would make the choice
///     FOR them. Measurement must never move the thing it measures, so this
///     file must never touch it — pinned by
///     `tier0/tests/test_eb14_selection_hook.py`.
///   * `CardSelectCmd.LogChoice(player, cards)` — the real first-party
///     convergence point: every one of the eleven `From*` entry points ends
///     there. It is `private static void` and writes a log line, so it is
///     reachable only by patch, and it carries the ANSWER without the OFFER.
///     A selector row whose offered list is missing cannot be read by the
///     consumers that exist (`understudy/replay.py` declines "Center Stage"
///     unless Guest Cast was demonstrably on the same list), so this is not
///     the seam either.
///
/// CONCLUSION: no first-party observation hook exists, so the seam is the
/// screens themselves, patched read-only. Each screen object holds BOTH halves
/// of the event — the list it was built with and the task it completes — which
/// is why patching them needs no pairing, no ambient state, and no ordering
/// assumption. Three surfaces cover every in-combat selection the roster can
/// raise:
///
///   1. `NCardGridSelectionScreen.CardsSelected()` — the abstract base of six
///      concrete grids (simple, combat-pile, deck, deck-upgrade,
///      deck-enchant, deck-transform). One patch, one implementation — but
///      NOT one offer reader: five of the six hold their offered list in
///      `_cards`, and `NCombatPileCardSelectScreen` does not (it assigns
///      `Array.Empty` once and keeps the real list in `_pile` + `_filter`).
///      The offer resolver is therefore per-type; see `OfferedFromPile`.
///      Note also that the four DECK grids essentially never open inside a
///      fight, and a row is only recorded against an open fight record, so
///      in-fight grid coverage is about half, not five-sixths.
///   2. `NChooseACardSelectionScreen.CardsSelected()` — a separate class, and
///      the load-bearing one: Furina's Ethereal Spotlight opens it every turn
///      (Center Stage / Guest Cast).
///   3. `NPlayerHand.SelectCards(...)` — hand selection, which never builds a
///      screen at all (Kokomi's exhaust cards, Klee's Crackle, Armaments).
///
/// THE SAME THREE RULES `PlayTelemetry` OBEYS APPLY HERE, and one more:
///
///   0. **Nothing here decides anything.** Every patch is a Prefix that reads
///      and a Postfix that attaches a continuation. No `SetResult`, no
///      selector push, no return-value edit — a measurement that can change a
///      choice is not a measurement.
///   1. It never touches game state and never consumes game RNG.
///   2. Every entry point is wrapped in try/catch, including the continuation
///      body: an exception escaping a task continuation is an unobserved
///      fault, and one thrown from a Prefix inside a lockstep co-op game is a
///      lost run.
///   3. It writes nothing itself. `PlayTelemetry` owns the file.
///
/// DECLARED LIMITS, surfaced rather than smuggled (`understudy/README.md`):
///   * **Local seat only.** A remote seat's answer arrives as indices through
///     `PlayerChoiceSynchronizer` and never opens a screen in this process, so
///     a co-op partner's row is absent, not empty.
///   * **In-fight only**, matching the bot feed exactly: a row is recorded
///     only against an OPEN fight record, so rest-site smiths and shop
///     removals are outside the channel on both feeds.
///   * **No bundle rows.** `NChooseABundleSelectionScreen` offers
///     `IReadOnlyList&lt;CardModel&gt;` bundles, and a bundle has no first-party
///     name. The bot feed's `bundle_select` row would have to be filled with
///     an invented one, and inventing is what schema discipline forbids.
///   * **An empty answer records nothing**, matching the bot feed: a skipped
///     screen produces no POST there and no row here.
/// </summary>
internal static class SelectionTelemetry
{
    /// <summary>
    /// One selection in flight: what was on the table, and who was asked.
    /// Carried through Harmony's `__state` so it is per-call — a screen opened
    /// from inside another screen cannot borrow its parent's offer.
    /// </summary>
    internal sealed class Pending
    {
        internal Pending(string screen, IReadOnlyList<CardModel> offered)
        {
            Screen = screen;
            Offered = offered;
        }

        internal string Screen { get; }

        internal IReadOnlyList<CardModel> Offered { get; }
    }

    /// <summary>
    /// `_cards` on the two screen families, resolved once and cached. Both are
    /// non-public, which is the whole reason this file exists — the offered
    /// list is not on any public surface.
    ///
    /// A DEAD LOOKUP RECORDS NOTHING RATHER THAN AN EMPTY OFFER. "Chosen from
    /// a list of zero" is a false statement about the game; absence is a true
    /// one about the instrument, and the warning below says which.
    /// </summary>
    private static readonly Dictionary<Type, FieldInfo?> OfferedFields = new();

    private static readonly HashSet<Type> Warned = new();

    /// <summary>The screen label written into the row: the concrete type name,
    /// lowercased. NOT a re-spelling of the bridge's `card_select` — that word
    /// is three screens wearing one name, and this side can tell them apart,
    /// which is the point of hooking here. The lowercasing matches the bot
    /// feed's own fallback spelling (`ncombatpilecardselectscreen`), so the two
    /// vocabularies overlap instead of colliding.</summary>
    private static string Label(object surface) =>
        surface.GetType().Name.ToLowerInvariant();

    /// <summary>`_pile` / `_filter` on `NCombatPileCardSelectScreen`, resolved
    /// once and cached — the one grid subclass whose offer is NOT in `_cards`.
    /// </summary>
    private static FieldInfo? _pileField;

    private static FieldInfo? _filterField;

    private static bool _pileFieldsResolved;

    /// <summary>The combat pile's offer, recomputed the way the screen itself
    /// recomputes it.
    ///
    /// WHY THIS EXISTS AND WHY A `_cards` READ CANNOT WORK HERE.
    /// `NCombatPileCardSelectScreen.Create` assigns
    /// `_cards = Array.Empty&lt;CardModel&gt;()` and never writes it again — one
    /// `_cards` reference in the whole class. The screen's real offer lives in
    /// `_pile` + `_filter` and is recomputed into `_grid.SetCards(...)` by
    /// `UpdatePileContents()` on every `_pile.ContentsChanged`. So the
    /// inherited `_cards` read succeeded, returned an empty list, and
    /// `Offer()` short-circuited — every combat-pile selection wrote no row,
    /// with no warning, while the boot report said ARMED. (Decompile read
    /// pinned to the build: `klee-mod/KleeTests/bin/Debug/sts2.dll`.)
    ///
    /// THE SNAPSHOT IS THE OFFER AS OPENED. `_pile.ContentsChanged` can fire
    /// mid-selection, so a Prefix-time read is the list the player was looking
    /// at when asked — which is the honest record and is what the bot feed's
    /// state dump captures.
    /// </summary>
    private static IReadOnlyList<CardModel>? OfferedFromPile(object screen)
    {
        if (!_pileFieldsResolved)
        {
            var t = typeof(NCombatPileCardSelectScreen);
            _pileField = AccessTools.Field(t, "_pile");
            _filterField = AccessTools.Field(t, "_filter");
            _pileFieldsResolved = true;
        }

        if (_pileField == null || _filterField == null)
        {
            if (Warned.Add(typeof(NCombatPileCardSelectScreen)))
            {
                Log.Warn($"[{KleeMod.ModId}] selection telemetry: "
                       + "NCombatPileCardSelectScreen._pile/_filter did not "
                       + "resolve, so the offered list is unreadable and NO "
                       + "selector rows are recorded for that screen. Every "
                       + "other telemetry channel is unaffected.");
            }

            return null;
        }

        if (_pileField.GetValue(screen) is not CardPile pile)
        {
            return null;
        }

        // A null filter is the screen's "everything in the pile" case; the
        // game always passes one, but reading a field is not a guarantee.
        var filter = _filterField.GetValue(screen) as Func<CardModel, bool>;
        return filter == null
            ? pile.Cards.ToList()
            : pile.Cards.Where(filter).ToList();
    }

    /// <summary>Reads a screen's offered list off its non-public `_cards`
    /// field. Returns null when the lookup is dead or the field is empty.
    /// </summary>
    private static IReadOnlyList<CardModel>? OfferedCards(object screen, Type declaring)
    {
        if (!OfferedFields.TryGetValue(declaring, out var field))
        {
            field = AccessTools.Field(declaring, "_cards");
            OfferedFields[declaring] = field;
        }

        if (field == null)
        {
            if (Warned.Add(declaring))
            {
                Log.Warn($"[{KleeMod.ModId}] selection telemetry: {declaring.Name}._cards "
                       + "did not resolve, so the offered list is unreadable and NO "
                       + "selector rows are recorded for that screen. Every other "
                       + "telemetry channel is unaffected.");
            }

            return null;
        }

        return field.GetValue(screen) as IReadOnlyList<CardModel>;
    }

    /// <summary>Prefix half: what is on the table, before anyone answers.
    /// </summary>
    internal static Pending? Offer(object screen, Type declaring)
    {
        try
        {
            // PER-TYPE RESOLVER, not another `_cards` read: one grid subclass
            // keeps its offer somewhere else entirely. See OfferedFromPile.
            var offered = screen is NCombatPileCardSelectScreen
                ? OfferedFromPile(screen)
                : OfferedCards(screen, declaring);
            return offered == null || offered.Count == 0
                ? null
                : new Pending(Label(screen), offered.ToList());
        }
        catch (Exception e)
        {
            Warn("Offer", e);
            return null;
        }
    }

    /// <summary>
    /// Postfix half: hand the answer to <see cref="PlayTelemetry"/> when the
    /// task the game is already awaiting completes.
    ///
    /// `ExecuteSynchronously` is deliberate and is a thread-safety decision,
    /// not a performance one. The screen calls `SetResult` from the UI, so
    /// running inline puts this read on the game's own thread; the default
    /// would queue it on the thread pool and read `CardModel.Title` off a
    /// background thread in a deterministic lockstep game.
    ///
    /// A cancelled or faulted task (the screen left the tree, the run ended)
    /// records nothing, and the continuation body catches everything so the
    /// task it returns can never fault unobserved.
    /// </summary>
    internal static void Answer(Pending? pending, Task<IEnumerable<CardModel>>? result)
    {
        try
        {
            if (pending == null || result == null) return;
            result.ContinueWith(
                task =>
                {
                    try
                    {
                        if (task.Status != TaskStatus.RanToCompletion) return;
                        var chosen = task.Result?.ToList();
                        if (chosen == null || chosen.Count == 0) return;
                        PlayTelemetry.SelectorAnswered(
                            pending.Screen, pending.Offered, chosen);
                    }
                    catch (Exception e)
                    {
                        Warn("Answer/continuation", e);
                    }
                },
                TaskContinuationOptions.ExecuteSynchronously);
        }
        catch (Exception e)
        {
            Warn("Answer", e);
        }
    }

    /// <summary>The hand has no screen and no `_cards`: the offer is the
    /// player's hand under the caller's filter, computed exactly the way
    /// `CardSelectCmd.FromHand` computes it. The seat is the local one by
    /// construction — `NPlayerHand.SelectCards` is only ever reached inside
    /// `ShouldSelectLocalCard`.</summary>
    internal static Pending? OfferFromHand(object hand, Func<CardModel, bool>? filter)
    {
        try
        {
            var combat = CombatManager.Instance?.DebugOnlyGetState();
            if (combat == null) return null;
            var me = LocalContext.GetMe(combat);
            var pile = me?.PlayerCombatState?.Hand;
            if (pile == null) return null;
            var offered = pile.Cards.Where(filter ?? (_ => true)).ToList();
            return offered.Count == 0 ? null : new Pending(Label(hand), offered);
        }
        catch (Exception e)
        {
            Warn("OfferFromHand", e);
            return null;
        }
    }

    private static void Warn(string where, Exception e) =>
        Log.Warn($"[{KleeMod.ModId}] selection telemetry {where} skipped "
               + $"({e.GetType().Name}: {e.Message})");
}

/// <summary>
/// Surface 1: the six grid screens, which share one inherited
/// <c>CardsSelected()</c> on their abstract base — so one patch covers the
/// simple grid, the combat pile, and the four deck screens. One PATCH, but
/// two offer readers: the combat pile keeps its list in <c>_pile</c> +
/// <c>_filter</c> rather than <c>_cards</c>, and reading <c>_cards</c> there
/// made this patch a silent no-op for the whole life of the channel.
/// </summary>
[HarmonyPatch(typeof(NCardGridSelectionScreen),
              nameof(NCardGridSelectionScreen.CardsSelected))]
internal static class NCardGridSelectionScreen_CardsSelected_Patch
{
    private static void Prefix(NCardGridSelectionScreen __instance,
                               out SelectionTelemetry.Pending? __state) =>
        __state = SelectionTelemetry.Offer(__instance,
                                           typeof(NCardGridSelectionScreen));

    private static void Postfix(Task<IEnumerable<CardModel>> __result,
                                SelectionTelemetry.Pending? __state) =>
        SelectionTelemetry.Answer(__state, __result);
}

/// <summary>
/// Surface 2: the choose-a-card screen. Not a grid subclass — its own class,
/// its own `_cards`, its own completion source. Furina's Ethereal Spotlight
/// opens it every turn, which is the whole reason the selector channel exists.
/// </summary>
[HarmonyPatch(typeof(NChooseACardSelectionScreen),
              nameof(NChooseACardSelectionScreen.CardsSelected))]
internal static class NChooseACardSelectionScreen_CardsSelected_Patch
{
    private static void Prefix(NChooseACardSelectionScreen __instance,
                               out SelectionTelemetry.Pending? __state) =>
        __state = SelectionTelemetry.Offer(__instance,
                                           typeof(NChooseACardSelectionScreen));

    private static void Postfix(Task<IEnumerable<CardModel>> __result,
                                SelectionTelemetry.Pending? __state) =>
        SelectionTelemetry.Answer(__state, __result);
}

/// <summary>
/// Surface 3: hand selection, which opens no screen — the hand itself enters a
/// select mode. `CardSelectCmd.FromHand` / `FromHandForDiscard` /
/// `FromHandForUpgrade` all land here.
/// </summary>
[HarmonyPatch(typeof(NPlayerHand), nameof(NPlayerHand.SelectCards))]
internal static class NPlayerHand_SelectCards_Patch
{
    private static void Prefix(NPlayerHand __instance,
                               Func<CardModel, bool>? filter,
                               out SelectionTelemetry.Pending? __state) =>
        __state = SelectionTelemetry.OfferFromHand(__instance, filter);

    private static void Postfix(Task<IEnumerable<CardModel>> __result,
                                SelectionTelemetry.Pending? __state) =>
        SelectionTelemetry.Answer(__state, __result);
}
