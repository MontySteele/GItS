#if PROTOTYPE_CARDS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Relics;

/// <summary>
/// VARKA'S OWN RELICS (<c>review/active/varka-expansion-2026-10-01.md</c>
/// sec.4, built at the paper's defaults while its picks are open). The base
/// game's shape, Klee's and Furina's: one Common, two Uncommons, three Rares
/// and one Shop relic beside Boreas's Fang. They, the Fang and Wolf's
/// Gravestone are his whole relic offer, and the Silent borrow goes (pick 1,
/// <see cref="KeepSilentBorrow"/>).
///
/// QUARANTINED for Salon Solitaire's reason: inside <c>#if PROTOTYPE_CARDS</c>
/// and under <c>Relics/</c>, so the titles stay in
/// <c>tools/lint_unique_names.py</c>'s namespace. Every effect asks
/// <see cref="VarkaPrototype.LiveFor"/>, so a relic held by anyone else, or
/// with the arm off, does nothing.
///
/// RELIC AND POTION APPLICATIONS GAIN NO OATH (sec.4, the kit paper's sec.3
/// terms) and switch no element: Dandelion Seeds' application runs inside
/// <see cref="VarkaOath.NoCredit"/>. Knight's Commission sets his element and
/// gains its 1 Oath because its face says so.
/// </summary>
public static class VarkaArmRelics
{
    /// <summary>
    /// Pick 1 of the expansion paper. False is its default (a): his own seven
    /// replace the Silent's six in the offer, and his three potions replace
    /// the Silent's. True is (b), the borrow kept beside them: the relic offer
    /// is every member and his potion pool appends the Silent's.
    /// </summary>
    public const bool KeepSilentBorrow = false;

    /// <summary>The seven, in the paper's table order. The pool reads this
    /// list and nothing else.</summary>
    public static readonly IReadOnlyList<Type> Types = new[]
    {
        typeof(KnightsCommission), typeof(WindblumeGarland),
        typeof(DandelionSeeds), typeof(BannerOfTheWestWind),
        typeof(StormterrorsScale), typeof(AndriussHowl),
        typeof(FavoniusDutyRoster),
    };

    /// <summary>How many copies of <typeparamref name="T"/> this Varka holds,
    /// with the arm live; 0 otherwise.</summary>
    internal static int Held<T>(Creature? varka) where T : RelicModel =>
        VarkaPrototype.LiveFor(varka) && varka!.Player is { } player
            ? player.Relics.OfType<T>().Count()
            : 0;

    /// <summary>Flash every copy of <typeparamref name="T"/> he holds.
    /// </summary>
    internal static void FlashAll<T>(Creature varka) where T : RelicModel
    {
        foreach (var relic in varka.Player?.Relics.OfType<T>().ToList()
                              ?? new List<T>())
        {
            relic.Flash();
        }
    }

    /// <summary>The turn-one gate Fresh Catch uses: his own first turn, the
    /// arm live.</summary>
    public static bool FirstTurnOf(RelicModel relic, Player player) =>
        player == relic.Owner
        && VarkaPrototype.LiveFor(player.Creature)
        && player.PlayerCombatState?.TurnNumber == 1
        && player.Creature is { IsDead: false };

    internal static string Icon(string slug) => "varka/relics/" + slug + ".png";

    /// <summary>
    /// His current element changed from <paramref name="from"/> to
    /// <paramref name="to"/> (<see cref="VarkaOath.SetCurrent"/>, the one
    /// place it moves). Banner of the West Wind first, so whatever reads the
    /// new element after the change reads the carried Oath; then Windblume
    /// Garland's Block.
    /// </summary>
    internal static async Task OnElementChanged(
        Creature varka, Element from, Element to)
    {
        if (BannerOfTheWestWind.Carry(varka, from, to) > 0)
        {
            FlashAll<BannerOfTheWestWind>(varka);
        }
        var block = WindblumeGarland.BlockFor(varka);
        if (block > 0)
        {
            FlashAll<WindblumeGarland>(varka);
            await CreatureCmd.GainBlock(varka, block, ValueProp.Unpowered, null,
                                        fast: true);
        }
    }
}

/// <summary>A relic of his: the Fang's fallback icon chain, his own file
/// when the art pass has put one in the pack.</summary>
public abstract class VarkaArmRelic : CustomRelicModel
{
    protected VarkaArmRelic() : base(autoAdd: false) { }

    /// <summary><c>varka/relics/&lt;slug&gt;.png</c>.</summary>
    protected abstract string Slug { get; }

    protected override string IconBaseName => "burning_blood";

    public override string PackedIconPath =>
        KleePck.Path(VarkaArmRelics.Icon(Slug)) ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path(VarkaArmRelics.Icon(Slug)) ?? base.BigIconPath;
}

/// <summary>Common. "At the start of each combat, your starting Knight's
/// element becomes your current element, with 1 Oath." On his first turn,
/// after the draw (Fresh Catch's hook), so the Fang's Ascension lands in the
/// opening hand (the paper: "intended"). The starting Knight is the one
/// starter-only Knight in his deck, the one the Fang rolled for the run; with
/// none left in the deck it does nothing.</summary>
public sealed class KnightsCommission : VarkaArmRelic
{
    public const int Oath = 1;

    protected override string Slug => "knights_commission";

    public override RelicRarity Rarity => RelicRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Knight's Commission"),
        ("description",
            "At the start of each combat, your starting Knight's element "
          + "becomes your [gold]current element[/gold], with [blue]" + Oath
          + "[/blue] [gold]Oath[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(
            ArmKeywordTips.ForOath(Array.Empty<IHoverTip>(), null), null);

    /// <summary>The element of the run's starting Knight: the first
    /// starter-only Knight in the deck, or None. PURE.</summary>
    public static Element StartingElement(IEnumerable<CardModel> deck) =>
        VarkaOath.KnightElement(deck.FirstOrDefault(VarkaRules.IsStarterKnight));

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!VarkaArmRelics.FirstTurnOf(this, player)) return;
        var element = StartingElement(player.Deck.Cards);
        if (element == Element.None) return;
        Flash();
        await VarkaOath.SetCurrent(choiceContext, player.Creature, element,
                                   knight: false);
        await VarkaOath.Gain(choiceContext, player.Creature, element, Oath);
    }
}

/// <summary>Uncommon. "Whenever your current element changes, gain 4 Block."
/// Paid by <see cref="VarkaArmRelics.OnElementChanged"/>; the first element
/// of a fight is a change, as Boreas Unbound counts it. Copies add.</summary>
public sealed class WindblumeGarland : VarkaArmRelic
{
    public const int Block = 4;

    protected override string Slug => "windblume_garland";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Windblume Garland"),
        ("description",
            "Whenever your [gold]current element[/gold] changes, gain [blue]"
          + Block + "[/blue] [gold]Block[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(Array.Empty<IHoverTip>(), null);

    /// <summary>The Block one change pays him: 4 a copy.</summary>
    public static int BlockFor(Creature? varka) =>
        Block * VarkaArmRelics.Held<WindblumeGarland>(varka);
}

/// <summary>Uncommon. "At the start of your turn, if no enemy has an aura,
/// apply your current element to a random enemy." A spent aura is an aura.
/// Nothing before his first element. The application gains no Oath and
/// switches nothing (<see cref="VarkaOath.NoCredit"/>). Late in the turn
/// start (Alice's Guidebook's hook), so it reads the board and the element
/// after Knight's Commission and his turn-start Powers have moved them.
/// </summary>
public sealed class DandelionSeeds : VarkaArmRelic
{
    protected override string Slug => "dandelion_seeds";

    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Dandelion Seeds"),
        ("description",
            "At the start of your turn, if no enemy has an aura, apply your "
          + "[gold]current element[/gold] to a random enemy."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(Array.Empty<IHoverTip>(), null);

    /// <summary>Does the board call for it: an element to apply, and not one
    /// enemy wearing an aura? PURE.</summary>
    public static bool Fires(Element current, IEnumerable<Creature> enemies) =>
        current != Element.None
        && enemies.All(e => e.IsDead || AuraCmd.Find(e) == null);

    public override async Task AfterPlayerTurnStartLate(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner || player.Creature is not { IsDead: false } varka) return;
        if (!VarkaPrototype.LiveFor(varka)) return;
        var combat = varka.CombatState;
        if (combat == null) return;
        var element = VarkaOath.Current(varka);
        var enemies = combat.HittableEnemies.ToList();
        if (!Fires(element, enemies)) return;
        var candidates = enemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var target = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (target == null) return;
        Flash();
        using (VarkaOath.NoCredit(varka))
        {
            await ElementalHit.ApplyOnly(choiceContext, target, element, varka);
        }
    }
}

/// <summary>Rare. "When your current element changes, the old element's Oath
/// moves to the new one." Bends sec.3 (the paper's pick 4). Paid by
/// <see cref="VarkaArmRelics.OnElementChanged"/> before anything reads the new
/// element. A move, not a gain: Dawn Wind's March and the Fang do not see it.
/// </summary>
public sealed class BannerOfTheWestWind : VarkaArmRelic
{
    protected override string Slug => "banner_of_the_west_wind";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Banner of the West Wind"),
        ("description",
            "When your [gold]current element[/gold] changes, the old "
          + "element's [gold]Oath[/gold] moves to the new one."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(
            ArmKeywordTips.ForOath(Array.Empty<IHoverTip>(), null), null);

    /// <summary>Move the Oath, if he holds the Banner. Returns how many
    /// points moved. A second copy has nothing left to move.</summary>
    public static int Carry(Creature varka, Element from, Element to) =>
        VarkaArmRelics.Held<BannerOfTheWestWind>(varka) > 0
            ? VarkaOathLedger.For(varka).MoveOath(from, to)
            : 0;
}

/// <summary>Rare. "Your Swirls pay twice." His current element's Swirl
/// payout (<see cref="VarkaOath.OnSwirl"/>) runs once more per copy; the
/// Swirl's own credit and its shared 2 damage are not doubled.</summary>
public sealed class StormterrorsScale : VarkaArmRelic
{
    protected override string Slug => "stormterrors_scale";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Stormterror's Scale"),
        ("description", "Your [gold]Swirls[/gold] pay twice."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(Array.Empty<IHoverTip>(), null);

    /// <summary>How many times one Swirl of his pays: 1, plus 1 a copy.
    /// PURE.</summary>
    public static int PayoutsFor(Creature? varka) =>
        1 + VarkaArmRelics.Held<StormterrorsScale>(varka);

    /// <summary><see cref="PayoutsFor"/>, flashing the Scale when it adds
    /// one. <see cref="VarkaOath.OnSwirl"/>'s call.</summary>
    internal static int TakePayouts(Creature varka)
    {
        var payouts = PayoutsFor(varka);
        if (payouts > 1) VarkaArmRelics.FlashAll<StormterrorsScale>(varka);
        return payouts;
    }
}

/// <summary>Rare. "Four Winds' Ascension returns to your hand at the start
/// of your turn after you play it." Each copy played is noted; at the start
/// of his next turn, after the draw, each noted copy still in his draw or
/// discard pile comes back to his hand, once per copy per turn. One drawn
/// already stays where it is; one exhausted does not come back.</summary>
public sealed class AndriussHowl : VarkaArmRelic
{
    /// <summary>Made on first use, never by the constructor: a mutable
    /// relic is a copy of the canonical one, and a set made there would be
    /// shared by every copy.</summary>
    private HashSet<CardModel>? _played;

    private HashSet<CardModel> Played => _played ??= new();

    protected override string Slug => "andriuss_howl";

    public override RelicRarity Rarity => RelicRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Andrius's Howl"),
        ("description",
            "[gold]Four Winds' Ascension[/gold] returns to your hand at the "
          + "start of your turn after you play it."),
    };

    /// <summary>The copies waiting to come back. Read by the tests.</summary>
    public IReadOnlyCollection<CardModel> Waiting => Played;

    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is ProtoVkFourWindsAscension ascension
            && ascension.Owner == Owner
            && VarkaPrototype.LiveFor(Owner?.Creature))
        {
            Played.Add(ascension);
        }
        return Task.CompletedTask;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner || !VarkaPrototype.LiveFor(player.Creature)) return;
        var back = Returning(player);
        Played.Clear();
        if (back.Count == 0) return;
        Flash();
        foreach (var card in back)
        {
            await CardPileCmd.Add(card, PileType.Hand);
        }
    }

    /// <summary>The noted copies in his draw or discard pile, in the order
    /// they were played.</summary>
    private List<CardModel> Returning(Player player)
    {
        var draw = PileType.Draw.GetPile(player).Cards;
        var discard = PileType.Discard.GetPile(player).Cards;
        return Played.Where(c => draw.Contains(c) || discard.Contains(c)).ToList();
    }

    public override Task AfterCombatEnd(CombatRoom room)
    {
        _played?.Clear();
        return Task.CompletedTask;
    }
}

/// <summary>Shop. "At the start of each combat, add a random Knight to your
/// hand. It costs 0 this turn." Knights' Roll Call's own add
/// (<see cref="VarkaRules.AddKnight"/>, unchosen): a pool Knight, never one
/// of the four starter-only ones, on his first turn after the draw so the
/// cost holds.</summary>
public sealed class FavoniusDutyRoster : VarkaArmRelic
{
    protected override string Slug => "favonius_duty_roster";

    public override RelicRarity Rarity => RelicRarity.Shop;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Favonius Duty Roster"),
        ("description",
            "At the start of each combat, add a random [gold]Knight[/gold] to "
          + "your hand. It costs 0 this turn."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForKnight(Array.Empty<IHoverTip>(), null);

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!VarkaArmRelics.FirstTurnOf(this, player)) return;
        Flash();
        await VarkaRules.AddKnight(choiceContext, player, choose: false);
    }
}
#endif
