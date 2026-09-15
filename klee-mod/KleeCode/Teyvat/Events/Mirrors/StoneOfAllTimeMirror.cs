using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE STONE OF ALL TIME, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/StoneOfAllTime.cs` and cross-checked
/// against the harvest (2 options: Lift, Push).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same four vars, the same ACT-2-ONLY
/// gate with its every-player-holds-a-potion clause, the same potions lock
/// while the page is open, the same `_LOCKED` twins on BOTH options, the same
/// discard-then-10-max-HP on Lift, and the same 6-unblockable-then-enchant-with-
/// Vigorous-8 on Push.
///
/// THE POTION IS ROLLED WHEN THE OPTIONS ARE BUILT, NOT WHEN LIFT IS TAKEN.
/// `GenerateInitialOptions` picks it, stores it on the event and writes its
/// title into the `DrinkRandomPotion` var, so the option can name the potion
/// it will take and the hover tip can show it. That is why the potion is a
/// FIELD here, and why the potions lock exists: a player who could re-order or
/// drink their belt between the page drawing and the click would make the
/// named potion wrong.
///
/// THE TWO `Rng.NextInt(100)` CALLS ARE NOT DEAD CODE -- they are the base
/// event's RNG-stream advances, one at the end of each handler, and dropping
/// either would desync the event's own stream against a replay. They are kept
/// with their result discarded exactly as the base event discards it.
///
/// THE GATE IS `CurrentActIndex == 1` -- act 2 ONLY, not act 2 or later. So
/// this event is the Hive faces' and never Glory's, and never act 1's.
///
/// `PUSH` ENCHANTS WITH AN AMOUNT TWICE: `FromDeckForEnchantment` is given the
/// amount so the grid previews the right number, and `CardCmd.Enchant` is given
/// it again as the applied value. Both are `PushVigorousAmount`, and both are
/// the base event's.
/// </summary>
public abstract class StoneOfAllTimeMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names.</summary>
    private const string DrinkRandomPotionKey = "DrinkRandomPotion";

    private const string DrinkMaxHpGainKey = "DrinkMaxHpGain";

    private const string PushHpLossKey = "PushHpLoss";

    private const string PushVigorousAmountKey = "PushVigorousAmount";

    private PotionModel _drinkAndLiftPotion;

    /// <summary>The potion Lift will take, rolled when the options are built.
    /// Mutable-guarded as the base event guards it.</summary>
    private PotionModel DrinkAndLiftPotion
    {
        get => _drinkAndLiftPotion;
        set
        {
            AssertMutable();
            _drinkAndLiftPotion = value;
        }
    }

    /// <summary>`StoneOfAllTime.cs:43-48`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar(DrinkRandomPotionKey),
            new DynamicVar(DrinkMaxHpGainKey, 10m),
            new DynamicVar(PushHpLossKey, 6m),
            new DynamicVar(PushVigorousAmountKey, 8m),
        };

    /// <summary>The base event's gate: act 2 ONLY, and every player holding at
    /// least one potion.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex == 1)
        {
            return runState.Players.All((Player player) => player.Potions.Any());
        }

        return false;
    }

    /// <summary>The base event's lock: the belt cannot be touched while the
    /// page names a potion off it.</summary>
    protected override Task BeforeEventStarted(bool isPreFinished)
    {
        Owner.CanUseOrRemovePotions = false;
        return Task.CompletedTask;
    }

    /// <summary>And the base event's unlock.</summary>
    protected override void OnEventFinished()
    {
        Owner.CanUseOrRemovePotions = true;
    }

    /// <summary>Two options, in the base event's order, each replaced by its
    /// own `_LOCKED` twin when it cannot be taken.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        DrinkAndLiftPotion = Rng.NextItem(Owner.Potions);
        EventOption lift;
        if (DrinkAndLiftPotion != null)
        {
            StringVar named = (StringVar)DynamicVars[DrinkRandomPotionKey];
            named.StringValue = DrinkAndLiftPotion.Title.GetFormattedText();
            lift = new EventOption(this, Lift, InitialOptionKey("LIFT"),
                HoverTipFactory.FromPotion(DrinkAndLiftPotion));
        }
        else
        {
            lift = new EventOption(this, null, InitialOptionKey("LIFT_LOCKED"));
        }

        EventOption push =
            CardPile.Get(PileType.Deck, Owner).Cards
                .Count((CardModel c) => ModelDb.Enchantment<Vigorous>().CanEnchant(c)) < 1
            ? new EventOption(this, null, InitialOptionKey("PUSH_LOCKED"))
            : new EventOption(this, Push, InitialOptionKey("PUSH"),
                HoverTipFactory.FromEnchantment<Vigorous>(
                    DynamicVars[PushVigorousAmountKey].IntValue))
                .ThatDoesDamage(DynamicVars[PushHpLossKey].BaseValue);

        return new List<EventOption> { lift, push };
    }

    /// <summary>`Lift`: the named potion is discarded, 10 max HP, the stream
    /// advance, then the page with the potion's name added to it.</summary>
    private async Task Lift()
    {
        await PotionCmd.Discard(DrinkAndLiftPotion);
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars[DrinkMaxHpGainKey].BaseValue);
        Rng.NextInt(100);
        LocString page = L10NLookup(PageKey("LIFT.description"));
        page.Add(DynamicVars[DrinkRandomPotionKey]);
        SetEventFinished(page);
    }

    /// <summary>`Push`: the 6 FIRST, then the enchant grid, then the stream
    /// advance.</summary>
    private async Task Push()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            DynamicVars[PushHpLossKey].BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        CardSelectorPrefs prefs = new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1);
        Vigorous vigorous = ModelDb.Enchantment<Vigorous>();
        foreach (CardModel card in await CardSelectCmd.FromDeckForEnchantment(
            Owner, vigorous, DynamicVars[PushVigorousAmountKey].IntValue, prefs))
        {
            CardCmd.Enchant(vigorous.ToMutable(), card, DynamicVars[PushVigorousAmountKey].BaseValue);
            CardCmd.Preview(card);
        }

        Rng.NextInt(100);
        SetEventFinished(L10NLookup(PageKey("PUSH.description")));
    }
}
