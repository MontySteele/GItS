using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE STATUS BATCH (2026-10-01, ruled): the bodies of the four Plan clauses
/// that read the hand just drawn. Paper
/// <c>review/active/kokomi-status-batch-2026-10-01.md</c> sec.2; readings in
/// <c>docs/notes/prototype-surface-provenance.md</c>, "Kokomi status batch,
/// 2026-10-01".
///
/// Rule 2 resolves a Plan after the next turn's draw, so "in your hand" on a
/// Plan is that hand, before she acts, and Plans carried out earlier in the
/// same morning have already changed it (a card one drew is seen by the
/// next). Each body reads the hand at the moment its clause runs.
///
/// BASE-GAME MACHINERY WHERE IT EXISTS: the transform is Defect's Compact's
/// (<c>CardCmd.Transform</c> over <c>IsTransformable</c> cards), the
/// discard-and-draw is Gambler's Brew's (<c>CardSelectCmd.FromHandForDiscard</c>
/// then <c>CardCmd.DiscardAndDraw</c>), and the status test is the card's own
/// <c>CardType.Status</c> / <c>CardType.Curse</c>. Sim twins:
/// <c>tier0/engine/kokomi_plan</c>, the same names.
/// </summary>
public static class KokomiStatusBatch
{
    /// <summary>A status or a curse, by the card's own type.</summary>
    public static bool IsStatusOrCurse(CardModel? card) =>
        card != null
        && (card.Type == CardType.Status || card.Type == CardType.Curse);

    private static List<CardModel> HandStatuses(Player? player)
    {
        if (player == null) return new List<CardModel>();
        var hand = PileType.Hand.GetPile(player);
        return hand?.Cards.Where(IsStatusOrCurse).ToList()
            ?? new List<CardModel>();
    }

    /// <summary>How many statuses and curses are in her hand right now.</summary>
    public static int StatusesInHand(Player? player) =>
        HandStatuses(player).Count;

    /// <summary>Tidecleanse's "up to N": every one when she holds N or
    /// fewer; a choice of N when she holds more. Pure, for the pins.</summary>
    public static int ExhaustCount(int held, int cap) =>
        held <= 0 || cap <= 0 ? 0 : System.Math.Min(held, cap);

    /// <summary>Kelp Wall: "plus 3 for each status or curse in your hand".
    /// Powered Block, rule 3's reading of every planned Block. A hand with
    /// none pays nothing.</summary>
    public static async Task<int?> BlockPerStatus(Creature kokomi, int rate)
    {
        var n = StatusesInHand(kokomi.Player);
        if (n <= 0 || rate <= 0) return 0;
        return (int)await CreatureCmd.GainBlock(
            kokomi, rate * n, ValueProp.Move, null);
    }

    /// <summary>Tidecleanse: "Exhaust up to 2 [3] statuses or curses in
    /// your hand." The number on the beat is the cards exhausted.</summary>
    public static async Task<int?> ExhaustStatuses(
        PlayerChoiceContext choiceContext, Player player, int cap,
        CardModel? source)
    {
        var held = HandStatuses(player);
        var n = ExhaustCount(held.Count, cap);
        if (n <= 0) return 0;
        IEnumerable<CardModel> victims = held;
        if (held.Count > n && source != null)
        {
            victims = await CardSelectCmd.FromHand(
                choiceContext, player,
                new CardSelectorPrefs(new LocString("cards", ExhaustPromptKey),
                                      n),
                IsStatusOrCurse, source);
        }
        var done = 0;
        foreach (var card in victims.Take(n).ToList())
        {
            await CardCmd.Exhaust(choiceContext, card);
            done++;
        }
        return done;
    }

    /// <summary>Sea Glass Harvest: "Transform every status and curse in your
    /// hand into Sea Glass [Sea Glass+]." Compact's body with curses added;
    /// a curse the game will not transform stays.</summary>
    public static async Task<int?> TransformStatuses(Player player,
                                                     bool upgraded)
    {
        var combat = player.Creature?.CombatState;
        if (combat == null) return 0;
        var targets = HandStatuses(player)
            .Where(c => c.IsTransformable).ToList();
        if (targets.Count == 0) return 0;
        var swaps = new List<CardTransformation>();
        foreach (var card in targets)
        {
            var glass = combat.CreateCard<Cards.Prototype.SeaGlass>(player);
            if (upgraded) CardCmd.Upgrade(glass);
            swaps.Add(new CardTransformation(card, glass));
        }
        await CardCmd.Transform(swaps, null);
        return targets.Count;
    }

    /// <summary>Turning Tide: "Discard any number of cards, then draw that
    /// many." Gambler's Brew's screen and call, none included.</summary>
    public static async Task<int?> DiscardAndDraw(
        PlayerChoiceContext choiceContext, Player player, CardModel? source)
    {
        if (source == null) return 0;
        var picked = (await CardSelectCmd.FromHandForDiscard(
            choiceContext, player,
            new CardSelectorPrefs(new LocString("cards", DiscardPromptKey),
                                  0, 999999999),
            null, source)).ToList();
        if (picked.Count == 0) return 0;
        await CardCmd.DiscardAndDraw(choiceContext, picked, picked.Count);
        return picked.Count;
    }

    /// <summary>Tidecleanse's screen, merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>.</summary>
    public const string ExhaustPromptKey =
        "KLEEMOD-KOKOMI_EXHAUST_STATUSES.selectionScreenPrompt";

    public const string ExhaustPromptText =
        "Choose statuses or curses to Exhaust.";

    /// <summary>Turning Tide's screen.</summary>
    public const string DiscardPromptKey =
        "KLEEMOD-KOKOMI_DISCARD_AND_DRAW.selectionScreenPrompt";

    public const string DiscardPromptText =
        "Choose any number of cards to discard. Draw that many.";
}

/// <summary>
/// Abyssal Salvage (the status batch, 2026-10-01): "Whenever a status or
/// curse is exhausted, the Casket gains 1." Any of HER statuses and curses,
/// by any route (a played Slimed, a Dazed at turn end, Tidecleanse). The
/// count is the ledger's, as every Casket card's. Sim twin:
/// <c>refpowers.after_card_exhausted</c>'s <c>kk_abyssal_salvage</c> read.
/// </summary>
public sealed class AbyssalSalvagePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Abyssal Salvage"),
        ("description",
            "Whenever a status or curse is exhausted, the "
          + "[gold]Casket[/gold] gains [blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        if (Owner == null || Amount <= 0) return Task.CompletedTask;
        if (card?.Owner?.Creature != Owner) return Task.CompletedTask;
        if (!KokomiStatusBatch.IsStatusOrCurse(card)) return Task.CompletedTask;
        if (!KokomiOverhaul.LiveFor(Owner)) return Task.CompletedTask;
        KokomiOverhaulKit.GainCasket(Owner, Amount);
        return Task.CompletedTask;
    }
}

/// <summary>
/// Abyssal Salvage upgraded: "the Casket gains 1 and you gain 2 Block". The
/// upgraded card installs this Power in place of
/// <see cref="AbyssalSalvagePower"/> (`upgraded_power`, The Long Game's
/// shape). Each stack is 1 Casket and 2 Block per exhaust. Powered Block,
/// the planned Block's reading. Sim twin: <c>kk_abyssal_salvage_plus</c>.
/// </summary>
public sealed class AbyssalSalvagePlusPower : PowerModel, ILocalizationProvider
{
    /// <summary>The Block per stack per exhausted status or curse.</summary>
    public const int BlockPerStack = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Abyssal Salvage+"),
        ("description",
            "Whenever a status or curse is exhausted, the "
          + "[gold]Casket[/gold] gains [blue]{Amount}[/blue] and you gain "
          + "2 [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card, bool causedByEthereal)
    {
        if (Owner == null || Amount <= 0) return;
        if (card?.Owner?.Creature != Owner) return;
        if (!KokomiStatusBatch.IsStatusOrCurse(card)) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        KokomiOverhaulKit.GainCasket(Owner, Amount);
        await CreatureCmd.GainBlock(Owner, BlockPerStack * Amount,
                                    ValueProp.Move, null);
    }
}
