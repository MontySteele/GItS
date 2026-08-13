// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// EB-52: A DEV-ONLY DOOR FOR PUTTING A CHOSEN CARD IN A DECK.
//
// WHY THIS EXISTS. EB-52(a) still owes one evidence shape: a Power being played
// and the Fanfare floor rising because of it, on one of three RARE
// `gain_fanfare_floor` Powers. The instrument has been confirmed present twice
// -- `KLEEMOD_FANFARE`, `KLEEMOD_FANFARE_FLOOR` and `KLEEMOD_FANFARE_CAP_BONUS`
// ride on every singleplayer GET (gits/GitsResources.cs) -- so the read is one
// request either side of the play. What is missing is ACQUISITION, and the row
// wrote the arithmetic down so nobody re-derives it: six rare draws across
// three runs hit none of the three targets, P(0 hits) = 0.842^6 = 36%, an
// ordinary miss. The acquisition cost is bounded below by run survival under
// the bot policy, and that is the real obstacle. This route removes the
// obstacle for a SMOKE. It removes nothing else.
//
// THE DESIGN CONSTRAINT, WHICH IS GitsSeed'S AND IS INHERITED VERBATIM.
// GitsSeed.cs earns its place by SELECTING which run the game's own generators
// produce, and by changing no generator, constant, reward table or pilot. This
// file is held to the same line: it selects a card the game's own card pools
// already contain and hands it to the game's own acquisition machinery. It
// never mints a card object of its own.
//
//   canonical  =  ModelDb.AllCards, matched on Id.Entry
//                 -- the same registry McpMod.Wiki.cs enumerates, which is
//                    also where mod-injected cards arrive by construction
//   instance   =  <scope>.CreateCard(canonical, player)
//                 -- the game's own instantiation: ToMutable, AddCard(owner),
//                    AfterCreated. Not `new`, not a clone we assembled.
//                    THE SCOPE IS THE PILE'S (see below).
//   handover   =  CardPileCmd.Add(card, PileType.Deck)                (deck)
//                 CardPileCmd.AddGeneratedCardToCombat(card, pile, player)
//                                                                  (in combat)
//
// Those are the same two lines a card reward runs (`CardReward.OnSelected` ->
// `CardPileCmd.Add(obtainedCard, PileType.Deck)`) and the same pair the game's
// own curse grant runs (`CardPileCmd.AddCursesToDeck` -> `RunState.CreateCard`
// then `Add`). Every hook, history entry, relic trigger and save-state effect
// those paths fire, this fires, because it IS those paths.
//
// EB-91: THE SCOPE IS PART OF THE PATH, AND GETTING IT WRONG WEDGES THE FIGHT.
// A card belongs to the `ICardScope` that created it, and the RunState and the
// CombatState are two different scopes. The first cut of this file created
// every card in the RUN scope and then handed the combat ones to
// `AddGeneratedCardToCombat`. The card arrived in hand and read back on the
// wire, so the grant looked fine -- and then playing it threw
// `... must be added to a CombatState before playing it` out of
// `CardPileCmd.AddDuringManualCardPlay`, whose guard is
// `card.Owner.Creature.CombatState.ContainsCard(card)`. The action queue never
// drained afterwards and the run ended `no_progress`: an unrecoverable fight,
// from a grant that answered `ok`.
//
// The game's own generation path never had this problem because it never
// crosses the scopes. Every in-combat generator reads the same two lines --
// `CollisionCourse` is the shortest of them:
//
//     await CardPileCmd.AddGeneratedCardToCombat(
//         base.CombatState.CreateCard<Debris>(base.Owner),
//         PileType.Hand, base.Owner);
//
// and `CardFactory.GetForCombat` / `GetDistinctForCombat` (the attack potion
// and Discovery route, which is the closest analogue to what this endpoint
// does -- an arbitrary canonical card handed into a live combat) do exactly
// the same with `player.Creature.CombatState.CreateCard(canonical, player)`.
// So this file now picks the scope from the pile:
//
//     PileType.Deck      -> player.RunState                (a run acquisition)
//     any combat pile    -> player.Creature.CombatState    (a generated card)
//
// which is the deck route unchanged -- it is what EB-52(a)'s evidence was
// taken through -- and the combat route finally being the path it always
// claimed to be. A combat-scoped card is not in the deck and does not outlive
// the fight, which is what a generated card IS; `pile: "deck"` remains the
// route for a grant that should persist.
//
// One filter the game applies and this route deliberately does not:
// `CardFactory.FilterForCombat` drops cards with `CanBeGeneratedInCombat`
// false and Basic/Ancient/Event rarities. That filter exists to keep the
// game's own RANDOM generators away from cards nobody designed for it, and
// this endpoint is not a generator -- it hands over a card the caller named.
// The refusal list below is the whole of what it declines.
//
// WHAT A RUN THAT USED THIS IS, AND IS NOT.
// It is no longer a run the generators produced. Its deck contains a card no
// draft, shop or event offered, so nothing about it -- not a winrate, not a
// floor reached, not an HP curve -- is comparable to any other run, and it is
// not a measurement of anything at all. The response says so in a `guardrail`
// field on EVERY successful grant, and `understudy/bridge.py` stamps the same
// sentence on the harness log, because a caveat that lives only in a comment
// is a caveat that is not in the record. Guardrail-7 is unchanged and this
// route cannot weaken it: a bot cannot see the screen either way.
//
// REFUSALS, AND WHY EACH ONE IS HERE.
//   * no run in progress          -- there is no deck to add to.
//   * multiplayer                 -- the pile add would not go through the
//                                    action-queue synchronizer, so peers would
//                                    diverge. Upstream hard-blocks SP/MP
//                                    mismatch at dispatch for the same reason;
//                                    this route sits outside that dispatcher
//                                    (like speed and seed) so it checks itself.
//   * unknown card id             -- refused with the id echoed. No fuzzy
//                                    match: `/api/v1/wiki?query=` is the
//                                    search surface and it already exists.
//   * a combat pile out of combat -- `AddGeneratedCardsToCombat` returns an
//                                    empty list when no combat is in progress,
//                                    which would be a silent no-op wearing an
//                                    `ok`.
//
//   GET  /api/v1/gits/give_card
//        -> { status, message, guardrail, run_in_progress, piles }
//   POST /api/v1/gits/give_card
//        { "card_id": "UNHEARD_CONFESSION", "count": 1,
//          "upgraded": false, "pile": "deck" }
//        -> { status, message, guardrail, card_id, card_name, count, pile }
//
// The grant is QUEUED, not awaited: `CardPileCmd.Add` is an async command that
// runs pile visuals, and blocking the main thread on it from inside the frame
// drain is a deadlock. Same shape as upstream's `play_card`, which enqueues a
// `PlayCardAction` and answers immediately. The caller confirms by reading the
// next state, which is what a harness does anyway.
//
// PIN NOTE. This adds one `else if` arm to `McpMod.HandleRequest` -- the third,
// after speed (W2) and seed (P1.5) -- marked in-file with `GItS LOCAL EDIT`.
// Routed from McpMod.HandleRequest; recorded in PROVENANCE.md, which also
// carries what it means for a pin refresh.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text.Json;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Runs;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The sentence every successful grant carries. It is a field on
    /// the wire and not a comment for the same reason the feed label is part of
    /// a telemetry record rather than part of its filename: a caveat that lives
    /// outside the record is a caveat that is lost the moment two records are
    /// concatenated.</summary>
    private const string GitsGiveCardGuardrail =
        "DEV ROUTE. This run's deck now contains a card no draft, shop or event "
        + "offered, so the run is no longer one the generators produced and "
        + "nothing measured on it is comparable to any other run. Use it for a "
        + "smoke, never for a number.";

    private static readonly Dictionary<string, PileType> GitsGiveCardPiles =
        new(StringComparer.OrdinalIgnoreCase)
        {
            ["deck"] = PileType.Deck,
            ["hand"] = PileType.Hand,
            ["draw"] = PileType.Draw,
            ["discard"] = PileType.Discard,
        };

    private const int GitsGiveCardMaxCount = 10;

    private static CardModel? GitsGiveCardFind(string cardId)
    {
        CardModel? byTitle = null;
        foreach (var card in ModelDb.AllCards)
        {
            var id = SafeGetText(() => card.Id.Entry);
            if (!string.IsNullOrWhiteSpace(id)
                && string.Equals(id, cardId, StringComparison.OrdinalIgnoreCase))
            {
                return card;
            }
            // The TITLE is a fallback and only an exact one. An id is the thing
            // itself; a title is loc data that moves with a wording pass, and a
            // fuzzy title match would hand back a card nobody asked for. The
            // search surface is /api/v1/wiki, which already exists.
            if (byTitle == null)
            {
                var title = SafeGetText(() => card.Title);
                if (!string.IsNullOrWhiteSpace(title)
                    && string.Equals(title, cardId,
                                     StringComparison.OrdinalIgnoreCase))
                {
                    byTitle = card;
                }
            }
        }
        return byTitle;
    }

    /// <summary>The route label a grant reports, and the ONE place the two
    /// branches are named. EB-91 found the response reporting the static
    /// string `card_pile_cmd` for both, which made the wire unable to tell a
    /// reader which path had run — on the night the combat path was broken,
    /// that is precisely the field that would have said so.</summary>
    private static string GitsGiveCardRoute(PileType pile) =>
        pile == PileType.Deck
            ? "run_state_create+card_pile_add"
            : "combat_state_create+add_generated_to_combat";

    /// <summary>The scope a granted card is created in, chosen by its
    /// destination pile (EB-91). A card belongs to the scope that made it,
    /// and `CardPileCmd.AddDuringManualCardPlay` checks membership of the
    /// COMBAT scope before it will play one.</summary>
    private static ICardScope? GitsGiveCardScope(Player player, PileType pile)
    {
        if (pile == PileType.Deck)
            return player.RunState;
        // Not CombatManager's state directly: the generators all reach it
        // through the owner's own creature, and a card must be created in the
        // combat state its owner is actually in.
        //
        // `as` and not a cast: `ICombatState` declares `CreateCard` itself and
        // does NOT derive from `ICardScope` (`CombatState` implements both
        // separately), so a state that is not also a card scope is a real
        // possibility to the compiler. It becomes the refusal above rather
        // than an InvalidCastException inside a fire-and-forget task.
        return player.Creature?.CombatState as ICardScope;
    }

    private static async Task GitsGiveCardGrant(
        CardModel canonical, Player player, PileType pile, int count,
        bool upgraded)
    {
        var scope = GitsGiveCardScope(player, pile);
        if (scope == null)
        {
            // Refused rather than created in the wrong scope. The apply path
            // already checked `CombatManager.Instance.IsInProgress`, so this
            // is the narrow race where the combat ended between the check and
            // the queued grant -- and a card minted into the run scope and
            // pushed at a dead combat is exactly the EB-91 shape.
            GD.PrintErr("[STS2 MCP][GItS] give_card: no card scope for pile "
                        + $"{pile}; grant dropped rather than mis-scoped.");
            return;
        }

        for (int i = 0; i < count; i++)
        {
            // The game's own instantiation. Never `new`, never a hand-built
            // clone: CreateCard is ToMutable + AddCard(owner) + AfterCreated,
            // and AfterCreated is where a card gets to set itself up.
            var card = scope.CreateCard(canonical, player);
            if (upgraded)
            {
                // The game's own upgrade command, which is what a rest-site
                // smith and an upgrade reward both call.
                CardCmd.Upgrade(card);
            }

            if (pile == PileType.Deck)
            {
                await CardPileCmd.Add(card, PileType.Deck);
            }
            else
            {
                // The generated-into-combat path, which additionally writes the
                // combat-history entry that "this card was generated" -- the
                // same route a Shiv or an attack potion takes. Using the plain
                // Add here would put the card in the pile with no history row,
                // which is a difference a later reader would have no way to see.
                await CardPileCmd.AddGeneratedCardToCombat(card, pile, player);
            }

            GD.Print($"[STS2 MCP][GItS] give_card: granted "
                     + $"{SafeGetText(() => card.Id.Entry)} to {pile} "
                     + $"via {GitsGiveCardRoute(pile)}");
        }
    }

    private static Dictionary<string, object?> GitsGiveCardApply(
        string cardId, int count, bool upgraded, string pileName)
    {
        if (!RunManager.Instance.IsInProgress)
            return Error("No run in progress; there is no deck to add to.");

        if (IsMultiplayerRun())
            return Error("give_card is refused in multiplayer: the pile add "
                         + "does not go through the action-queue synchronizer, "
                         + "so peers would diverge.");

        if (!GitsGiveCardPiles.TryGetValue(pileName, out var pile))
            return Error($"Unknown pile '{pileName}'. One of: "
                         + string.Join(", ", GitsGiveCardPiles.Keys) + ".");

        if (pile != PileType.Deck && !CombatManager.Instance.IsInProgress)
            return Error($"pile '{pileName}' is a combat pile and no combat is "
                         + "in progress; the add would silently do nothing.");

        var runState = RunManager.Instance.DebugOnlyGetState();
        if (runState == null)
            return Error("No run state");

        var player = LocalContext.GetMe(runState);
        if (player == null)
            return Error("Could not find local player");

        var canonical = GitsGiveCardFind(cardId);
        if (canonical == null)
            return Error($"No card with id or exact title '{cardId}'. Search "
                         + "with GET /api/v1/wiki?query=<text>&type=card.");

        // Fire and forget through the game's own no-await helper. Awaiting here
        // would block the frame drain on a command that runs pile visuals,
        // which is a deadlock; upstream's `play_card` answers the same way.
        TaskHelper.RunSafely(
            GitsGiveCardGrant(canonical, player, pile, count, upgraded));

        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = $"queued {count}x '{SafeGetText(() => canonical.Title)}'"
                          + $" into {pileName}"
                          + (upgraded ? " (upgraded)" : "")
                          + "; read the next state to confirm",
            ["guardrail"] = GitsGiveCardGuardrail,
            ["card_id"] = SafeGetText(() => canonical.Id.Entry),
            ["card_name"] = SafeGetText(() => canonical.Title),
            ["count"] = count,
            ["upgraded"] = upgraded,
            ["pile"] = pileName,
            ["route"] = GitsGiveCardRoute(pile),
            ["scope"] = pile == PileType.Deck ? "run" : "combat"
        };
    }

    private static Dictionary<string, object?> GitsGiveCardDescribe()
    {
        bool inRun;
        try { inRun = RunManager.Instance.IsInProgress; }
        catch { inRun = false; }
        return new Dictionary<string, object?>
        {
            ["status"] = "ok",
            ["message"] = "POST { card_id, count?, upgraded?, pile? } to grant "
                          + "a card through the game's own acquisition path.",
            ["guardrail"] = GitsGiveCardGuardrail,
            ["run_in_progress"] = inRun,
            ["piles"] = GitsGiveCardPiles.Keys.ToList(),
            ["max_count"] = GitsGiveCardMaxCount
        };
    }

    private static void HandleGitsGiveCard(
        HttpListenerRequest request, HttpListenerResponse response)
    {
        try
        {
            if (request.HttpMethod == "GET")
            {
                var readTask = RunOnMainThread(GitsGiveCardDescribe);
                SendJson(response, readTask.GetAwaiter().GetResult());
                return;
            }

            if (request.HttpMethod != "POST")
            {
                SendError(response, 405, "Method not allowed");
                return;
            }

            string body;
            using (var reader = new StreamReader(request.InputStream,
                                                 request.ContentEncoding))
                body = reader.ReadToEnd();

            Dictionary<string, JsonElement>? parsed;
            try
            {
                parsed = JsonSerializer
                    .Deserialize<Dictionary<string, JsonElement>>(body);
            }
            catch
            {
                SendError(response, 400, "Invalid JSON");
                return;
            }

            if (parsed == null)
            {
                SendError(response, 400, "Missing body");
                return;
            }

            string? cardId = null;
            if (parsed.TryGetValue("card_id", out var idElem)
                && idElem.ValueKind == JsonValueKind.String)
                cardId = idElem.GetString();
            if (string.IsNullOrWhiteSpace(cardId))
            {
                SendError(response, 400, "Missing 'card_id'");
                return;
            }

            int count = 1;
            if (parsed.TryGetValue("count", out var countElem)
                && countElem.ValueKind == JsonValueKind.Number
                && countElem.TryGetInt32(out var parsedCount))
                count = parsedCount;
            // Clamped rather than refused: the bound exists so a typo cannot
            // stuff a deck, and the honest answer to "give me 500" is "here is
            // the most this route hands out", not a 400 nobody reads.
            count = Math.Clamp(count, 1, GitsGiveCardMaxCount);

            bool upgraded = parsed.TryGetValue("upgraded", out var upElem)
                            && upElem.ValueKind == JsonValueKind.True;

            string pileName = "deck";
            if (parsed.TryGetValue("pile", out var pileElem)
                && pileElem.ValueKind == JsonValueKind.String)
                pileName = pileElem.GetString() ?? "deck";

            var applyTask = RunOnMainThread(
                () => GitsGiveCardApply(cardId!.Trim(), count, upgraded,
                                        pileName.Trim()));
            SendJson(response, applyTask.GetAwaiter().GetResult());
        }
        catch (Exception ex)
        {
            GD.PrintErr($"[STS2 MCP][GItS] give_card endpoint failed: {ex}");
            try { SendError(response, 500, $"give_card failed: {ex.Message}"); }
            catch { /* response may already be closed */ }
        }
    }
}
