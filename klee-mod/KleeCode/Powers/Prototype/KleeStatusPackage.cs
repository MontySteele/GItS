using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE KLEE STATUS PACKAGE (2026-10-01, ruled). Paper
/// <c>review/active/klee-status-package-2026-10-01.md</c>; readings in
/// <c>docs/notes/prototype-surface-provenance.md</c>, "Klee status package,
/// 2026-10-01".
///
/// The two taxes are ordinary <c>add_card</c> rows (the base game's
/// <c>Dazed</c>, and her <see cref="Confiscated"/>); this file is the cards
/// that READ them. A STATUS is a card of <c>CardType.Status</c> or of
/// <c>CardRarity.Status</c>: the second is what makes Confiscated one (a
/// 1-cost Skill at Status rarity). Curses are not statuses. Sim twins:
/// <c>tier0/engine/klee_overhaul.py</c>, the status-package block.
/// </summary>
public static class KleeStatusPackage
{
    /// <summary>Is <paramref name="card"/> a status? PURE.</summary>
    public static bool IsStatus(CardModel? card) =>
        card != null
        && (card.Type == CardType.Status || card.Rarity == CardRarity.Status);

    /// <summary>Is <paramref name="card"/> her Confiscated? PURE.</summary>
    public static bool IsConfiscated(CardModel? card) => card is Confiscated;

    private static List<CardModel> HandStatuses(Player? player)
    {
        if (player == null) return new List<CardModel>();
        var hand = PileType.Hand.GetPile(player);
        return hand?.Cards.Where(IsStatus).ToList() ?? new List<CardModel>();
    }

    /// <summary>How many statuses are in the hand of
    /// <paramref name="owner"/>'s player. PURE: the count Kitchen Alchemy's
    /// <see cref="ExhaustStatuses"/> would exhaust (curses are not
    /// statuses).</summary>
    public static int StatusesInHand(Creature? owner) =>
        HandStatuses(owner?.Player).Count;

    /// <summary>Kitchen Alchemy (reworked 2026-10-02): "Exhaust every status
    /// in your hand." Returns how many went; none held, nothing happens and
    /// the card still plays. Dust of Purification's exhaust, shared. Sim
    /// twin: <c>klee_overhaul.exhaust_statuses</c>.</summary>
    public static async Task<int> ExhaustStatuses(
        PlayerChoiceContext choiceContext, Player player)
    {
        var victims = HandStatuses(player);
        foreach (var card in victims)
        {
            await CardCmd.Exhaust(choiceContext, card);
        }
        return victims.Count;
    }

    /// <summary>Kitchen Alchemy: "ALL enemies lose 1 [2] Strength. Exhaust
    /// every status in your hand; they lose 1 more for each." The printed
    /// base plus <paramref name="per"/> for each status exhausted, applied
    /// once as one total. PURE.</summary>
    public static int LossWithStatuses(int printed, int per, int exhausted) =>
        printed + per * (exhausted > 0 ? exhausted : 0);

    /// <summary>Klee Can Explain!: "Transform every status in your hand into
    /// Pop!." Defect's Compact body (<c>CardCmd.Transform</c> over
    /// <c>IsTransformable</c> cards), the made card unupgraded.</summary>
    public static async Task<int> TransformStatusesInto<T>(Player player)
        where T : CardModel
    {
        var combat = player.Creature?.CombatState;
        if (combat == null) return 0;
        var targets = HandStatuses(player).Where(c => c.IsTransformable)
            .ToList();
        if (targets.Count == 0) return 0;
        var swaps = new List<CardTransformation>();
        foreach (var card in targets)
        {
            swaps.Add(new CardTransformation(card, combat.CreateCard<T>(player)));
        }
        await CardCmd.Transform(swaps, null);
        return targets.Count;
    }

    /// <summary>Albedo -- Dust of Purification: "Exhaust every status in your
    /// hand. Your largest Bomb grows by 6 [8] for each." The exhausts first,
    /// then ONE growth of <paramref name="per"/> times the count; with no
    /// Bomb out the exhausts still happen.</summary>
    public static async Task<int> ExhaustStatusesGrowLargest(
        PlayerChoiceContext choiceContext, Player player, int per)
    {
        var n = await ExhaustStatuses(choiceContext, player);
        if (n > 0 && per > 0 && player.Creature != null)
        {
            ProtoBombPower.GrowLargest(player.Creature, per * n);
        }
        return n;
    }

    /// <summary>The card a transform makes, previewed as a hover tip (the base
    /// game's Compact / Fuel shape). Appended after
    /// <paramref name="tips"/>.</summary>
    public static IEnumerable<IHoverTip> WithPreview<T>(
        IEnumerable<IHoverTip> tips) where T : CardModel
    {
        foreach (var tip in tips) yield return tip;
        yield return HoverTipFactory.FromCard<T>(false);
    }
}

/// <summary>
/// Finders Keepers: "Whenever you play a Confiscated, place a Bomb 5 [7] on a
/// random enemy." Party Poppers' shape, one trigger over: the stack is the
/// Bomb size. Sim twin: <c>klee_overhaul.finders_keepers</c>.
/// </summary>
public sealed class FindersKeepersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Finders Keepers"),
        ("description",
            "Whenever you play a [gold]Confiscated[/gold], place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!KleeStatusPackage.IsConfiscated(cardPlay.Card)) return;
        await ProtoBombPower.PlaceOnRandom(choiceContext, Owner, Amount,
                                           isMine: false, payloadMineAll: 0,
                                           cardSource: null);
    }
}

/// <summary>
/// Damage Report: "Whenever you draw a status, deal 5 [7] damage to ALL
/// enemies." Per card drawn, any status (a Dazed too). Spark Knight's hit:
/// unelemented, through <see cref="ElementalHit.DealUnelemented"/>. Sim
/// twin: <c>klee_overhaul.damage_report</c>, read at
/// <c>refpowers.after_card_drawn</c>.
/// </summary>
public sealed class DamageReportPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Damage Report"),
        ("description",
            "Whenever you draw a status, deal [blue]{Amount}[/blue] damage to "
          + "ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardDrawn(
        PlayerChoiceContext choiceContext, CardModel card, bool fromHandDraw)
    {
        if (Owner == null || Amount <= 0) return;
        if (card?.Owner?.Creature != Owner) return;
        if (!KleeStatusPackage.IsStatus(card)) return;
        var combat = Owner.CombatState;
        if (combat == null) return;
        foreach (var target in combat.HittableEnemies
                     .Where(e => !e.IsDead).ToList())
        {
            if (target.IsDead) continue;
            await ElementalHit.DealUnelemented(choiceContext, target, Amount,
                                               Owner);
        }
    }
}

/// <summary>
/// Solitary Confinement: "Your Confiscated cost 0. [Innate.]" Playdate's
/// cost seam (<c>TryModifyEnergyCostInCombat</c>), for every Confiscated of
/// hers for the rest of combat. Sim twin:
/// <c>klee_overhaul.solitary_confinement_frees</c>.
/// </summary>
public sealed class SolitaryConfinementPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Solitary Confinement"),
        ("description", "Your [gold]Confiscated[/gold] cost 0."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (!KleeStatusPackage.IsConfiscated(card)) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = 0m;
        return true;
    }
}
