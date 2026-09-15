using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// WELCOME TO WONGO'S, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/WelcomeToWongos.cs` and cross-checked
/// against the harvest (4 options: Bargain Bin, Featured Item, Mystery Box,
/// Leave).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same nine vars, the same
/// act-2-and-100-gold gate, the featured Rare pulled off the FRONT of the run's
/// relic queue when the options are built (so the option can name it and carry
/// its tips), the same three `_LOCKED` twins, the same three purchases at 100 /
/// 200 / 300 with their 32 / 8 / 16 Wongo Points, and the same Leave that
/// downgrades one upgraded card at random.
///
/// THE WONGO POINTS ARE META-PROGRESSION, NOT RUN STATE.
/// `CheckObtainWongoBadge` reads `SaveManager.Instance.Progress.WongoPoints`,
/// works out the position inside the current 2000-point badge, and picks ONE
/// of three pages accordingly -- the badge page when the purchase crosses 2000,
/// the counter page when a badge has been earned before, the plain page
/// otherwise. A dressing writes all three rows and changes none of that: the
/// points are the player's across runs and across arms, and the arm must not
/// fork them.
///
/// THE PAGE IS CHOSEN BY THE HANDLER, NOT BY THE OPTION -- all three purchases
/// end on `SetEventFinished(await CheckObtainWongoBadge(n))`, which is why the
/// three AFTER_BUY pages have no option of their own and the mirror's spec
/// points all three at the Bargain Bin line.
///
/// THE FEATURED RELIC IS FILTERED BY `IsAllowedInShops`, and so is the Bargain
/// Bin's Common. Both are `PullNextRelicFromFront` with a rarity and that
/// filter, which is what keeps a non-shop relic out of a stall.
///
/// `ExtraFields.WongoPoints` IS SET ON THE PLAYER as well, which is what the
/// run summary reads. The base event's line, kept.
/// </summary>
public abstract class WelcomeToWongosMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names. Its 2000-point badge
    /// threshold is inlined at its use sites, as every other mirror's
    /// base-game numbers are.</summary>
    private const string BargainBinCostKey = "BargainBinCost";

    private const string FeaturedItemCostKey = "FeaturedItemCost";

    private const string MysteryBoxCostKey = "MysteryBoxCost";

    private const string MysteryBoxRelicCountKey = "MysteryBoxRelicCount";

    private const string MysteryBoxCombatCountKey = "MysteryBoxCombatCount";

    private const string WongoPointAmountKey = "WongoPointAmount";

    private const string RemainingWongoPointAmountKey = "RemainingWongoPointAmount";

    private const string TotalWongoBadgeAmountKey = "TotalWongoBadgeAmount";

    private const string RandomRelicKey = "RandomRelic";

    private RelicModel _featuredItem;

    /// <summary>The Rare the stall is showing, pulled once when the options are
    /// built so the option can NAME it.</summary>
    private RelicModel FeaturedItem
    {
        get => _featuredItem;
        set
        {
            AssertMutable();
            _featuredItem = value;
        }
    }

    /// <summary>`WelcomeToWongos.cs:52-63`, value for value and in its
    /// order.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar(BargainBinCostKey, 100m),
            new DynamicVar(MysteryBoxCostKey, 300m),
            new DynamicVar(FeaturedItemCostKey, 200m),
            new DynamicVar(MysteryBoxRelicCountKey, 3m),
            new DynamicVar(MysteryBoxCombatCountKey, 5m),
            new DynamicVar(WongoPointAmountKey, 0m),
            new DynamicVar(RemainingWongoPointAmountKey, 0m),
            new DynamicVar(TotalWongoBadgeAmountKey, 0m),
            new StringVar(RandomRelicKey),
        };

    /// <summary>The base event's gate: act 2, and every player at 100 gold or
    /// more.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex == 1)
        {
            return runState.Players.All((Player p) => p.Gold >= 100);
        }

        return false;
    }

    /// <summary>Four options, in the base event's order; the first three fall
    /// back to their own `_LOCKED` twin when the purse is short.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        Player owner = Owner;
        FeaturedItem = RelicFactory.PullNextRelicFromFront(
            owner, RelicRarity.Rare, (RelicModel r) => r.IsAllowedInShops);
        ((StringVar)DynamicVars[RandomRelicKey]).StringValue =
            FeaturedItem.Title.GetFormattedText();

        List<EventOption> options = new List<EventOption>();
        options.Add((decimal)owner.Gold >= DynamicVars[BargainBinCostKey].BaseValue
            ? new EventOption(this, BuyBargainBin, InitialOptionKey("BARGAIN_BIN"))
            : new EventOption(this, null, InitialOptionKey("BARGAIN_BIN_LOCKED")));
        options.Add((decimal)owner.Gold >= DynamicVars[FeaturedItemCostKey].BaseValue
            ? new EventOption(this, BuyFeaturedItem, InitialOptionKey("FEATURED_ITEM"),
                FeaturedItem.HoverTips)
            : new EventOption(this, null, InitialOptionKey("FEATURED_ITEM_LOCKED")));
        options.Add((decimal)owner.Gold >= DynamicVars[MysteryBoxCostKey].BaseValue
            ? new EventOption(this, BuyMysteryBox, InitialOptionKey("MYSTERY_BOX"))
            : new EventOption(this, null, InitialOptionKey("MYSTERY_BOX_LOCKED")));
        options.Add(new EventOption(this, Leave, InitialOptionKey("LEAVE")));
        return options;
    }

    /// <summary>The base event's badge arithmetic, and the three pages it
    /// chooses between.</summary>
    private async Task<LocString> CheckObtainWongoBadge(int pointsEarned)
    {
        int banked = SaveManager.Instance.Progress.WongoPoints;
        int intoBadge = banked % 2000;
        int afterPurchase = intoBadge + pointsEarned;
        int total = banked + pointsEarned;
        DynamicVars[WongoPointAmountKey].BaseValue = afterPurchase;
        DynamicVars[RemainingWongoPointAmountKey].BaseValue = 2000 - afterPurchase;
        DynamicVars[TotalWongoBadgeAmountKey].BaseValue = total / 2000;
        Owner.ExtraFields.WongoPoints = pointsEarned;
        if (afterPurchase >= 2000)
        {
            await RelicCmd.Obtain<WongoCustomerAppreciationBadge>(Owner);
            return L10NLookup(PageKey("AFTER_BUY_RECEIVE_BADGE.description"));
        }

        if (DynamicVars[TotalWongoBadgeAmountKey].BaseValue > 0m)
        {
            return L10NLookup(PageKey("AFTER_BUY_BADGE_COUNTER.description"));
        }

        return L10NLookup(PageKey("AFTER_BUY.description"));
    }

    /// <summary>100 gold, one shop-legal Common, 32 points.</summary>
    private async Task BuyBargainBin()
    {
        await PlayerCmd.LoseGold(
            DynamicVars[BargainBinCostKey].BaseValue, Owner, GoldLossType.Spent);
        RelicModel relic = RelicFactory.PullNextRelicFromFront(
            Owner, RelicRarity.Common, (RelicModel r) => r.IsAllowedInShops).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        SetEventFinished(await CheckObtainWongoBadge(32));
    }

    /// <summary>300 gold, the ticket that pays out later, 8 points.</summary>
    private async Task BuyMysteryBox()
    {
        await PlayerCmd.LoseGold(
            DynamicVars[MysteryBoxCostKey].BaseValue, Owner, GoldLossType.Spent);
        await RelicCmd.Obtain<WongosMysteryTicket>(Owner);
        SetEventFinished(await CheckObtainWongoBadge(8));
    }

    /// <summary>200 gold, the Rare the stall named, 16 points.</summary>
    private async Task BuyFeaturedItem()
    {
        await PlayerCmd.LoseGold(
            DynamicVars[FeaturedItemCostKey].BaseValue, Owner, GoldLossType.Spent);
        await RelicCmd.Obtain(FeaturedItem.ToMutable(), Owner);
        SetEventFinished(await CheckObtainWongoBadge(16));
    }

    /// <summary>Leave: one UPGRADED card downgraded at random, or nothing at
    /// all if the deck holds none.</summary>
    private async Task Leave()
    {
        Player owner = Owner;
        CardModel card = Rng.NextItem(owner.Deck.Cards.Where((CardModel c) => c.IsUpgraded));
        if (card != null)
        {
            CardCmd.Downgrade(card);
            CardCmd.Preview(card);
            await Cmd.CustomScaledWait(0.5f, 1.2f);
        }

        SetEventFinished(L10NLookup(PageKey("LEAVE.description")));
    }
}
