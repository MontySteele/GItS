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
/// THE STATUS BATCH (2026-10-01, ruled): the bodies of the clauses that read
/// the hand -- Kelp Wall's and Sea Glass Harvest's Plans, and since the
/// re-founding (2026-10-12) Tidecleanse's now-line Exhaust. (Turning Tide's
/// discard-and-draw and Abyssal Salvage left with their cards.) Paper
/// <c>review/active/kokomi-status-batch-2026-10-01.md</c> sec.2; readings in
/// <c>docs/notes/prototype-surface-provenance.md</c>, "Kokomi status batch,
/// 2026-10-01".
///
/// THE KOKOMI ROUND-1 FIXES (2026-10-12): the two Plan bodies used to read
/// the hand at carry-out, and seats found it empty of the statuses they wrote
/// the Plan for (an Ethereal one exhausted, the rest discarded with the hand).
/// Kelp Wall now pays the count stamped when the Plan was WRITTEN
/// (<c>KokomiPlan.Planned.WrittenCount</c>) and Sea Glass Harvest transforms
/// the statuses and curses in the DRAW PILE, the dead draws still to come.
///
/// BASE-GAME MACHINERY WHERE IT EXISTS: the transform is Defect's Compact's
/// (<c>CardCmd.Transform</c> over <c>IsTransformable</c> cards), and the status
/// test is the card's own
/// <c>CardType.Status</c> / <c>CardType.Curse</c>. Sim twins:
/// <c>tier0/engine/kokomi_plan</c>, the same names.
/// </summary>
public static class KokomiStatusBatch
{
    /// <summary>A status or a curse, by the card's own type.</summary>
    public static bool IsStatusOrCurse(CardModel? card) =>
        card != null
        && (card.Type == CardType.Status || card.Type == CardType.Curse);

    private static List<CardModel> HandStatuses(Player? player) =>
        PileStatuses(player, PileType.Hand);

    private static List<CardModel> PileStatuses(Player? player, PileType type)
    {
        if (player == null) return new List<CardModel>();
        var pile = type.GetPile(player);
        return pile?.Cards.Where(IsStatusOrCurse).ToList()
            ?? new List<CardModel>();
    }

    /// <summary>How many statuses and curses are in her hand right now.</summary>
    public static int StatusesInHand(Player? player) =>
        HandStatuses(player).Count;

    /// <summary>Tidecleanse's "up to N": every one when she holds N or
    /// fewer; a choice of N when she holds more. Pure, for the pins.</summary>
    public static int ExhaustCount(int held, int cap) =>
        held <= 0 || cap <= 0 ? 0 : System.Math.Min(held, cap);

    /// <summary>Kelp Wall: "plus 3 for each status or curse in your hand
    /// when written". Powered Block, rule 3's reading of every planned Block.
    /// <paramref name="writtenCount"/> is the count stamped when the Plan was
    /// written; null (no writer stamped it) reads the hand. None pays
    /// nothing.</summary>
    public static async Task<int?> BlockPerStatus(Creature kokomi, int rate,
                                                  int? writtenCount = null)
    {
        var n = writtenCount ?? StatusesInHand(kokomi.Player);
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
    /// draw pile into Sea Glass [Sea Glass+]." Compact's body with curses
    /// added, over the draw pile since the Kokomi round-1 fixes (2026-10-12);
    /// a curse the game will not transform stays.</summary>
    public static async Task<int?> TransformStatuses(Player player,
                                                     bool upgraded)
    {
        var combat = player.Creature?.CombatState;
        if (combat == null) return 0;
        var targets = PileStatuses(player, PileType.Draw)
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

    /// <summary>Tidecleanse's screen, merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>.</summary>
    public const string ExhaustPromptKey =
        "KLEEMOD-KOKOMI_EXHAUST_STATUSES.selectionScreenPrompt";

    public const string ExhaustPromptText =
        "Choose statuses or curses to Exhaust.";
}
