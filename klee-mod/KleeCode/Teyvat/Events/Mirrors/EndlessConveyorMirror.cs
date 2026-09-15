using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// ENDLESS CONVEYOR, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/EndlessConveyor.cs` and cross-checked
/// against the frozen harvest (Grab Something Off the Belt, Observe the Chef,
/// and the eight-dish table under them).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same six vars, the same 40 Mora a
/// plate with Golden Fysh free, the same weights (6 / 6 / 3 / 3 / 3 / 3 / 1),
/// the same three conditional dishes (Clam Roll only when hurt, Suspicious
/// Condiment only with a slot free, Golden Fysh only after the first grab),
/// the same forced Seapunk Salad on every fifth grab, the same no-repeat rule,
/// the same 120-Mora gate on every player, and the same single upgrade for
/// walking away.
///
/// THE GRAB OPTION'S KEY IS THE ROLLED DISH, AND THAT IS WHY THIS EVENT WAS
/// PARKED. There is no `GRAB_SOMETHING_OFF_THE_BELT` option key at all: the
/// option is built from `<see cref="Dish"/>.OptionKey`, one of eight, and each
/// dish also needs a `DISHES.&lt;id&gt;.title` row because `CalculateVars`
/// reads it into the `CurrentDishTitle` var. The face carries all eight inside
/// the one belt line, and the mirror ledger's `dish_table` is what splits them
/// out; the grab line itself pairs with the LOCKED twin, which is the same
/// option greyed out and the only key on that branch that is not a dish.
///
/// THE DISH IDS ARE NEVER SPELLED ALONE. A `Dish` carries the SUFFIXES of its
/// two keys rather than a bare id, and identity is compared on the option
/// suffix -- so the literals in this class are `ALL.options.CAVIAR` and
/// `DISHES.CAVIAR.title`, which are keys the shape has, rather than `CAVIAR`,
/// which would read to `A_mirrors_key_literals_are_exactly_its_shape` as a key
/// the shape does not.
/// </summary>
public abstract class EndlessConveyorMirror : TeyvatEventMirror
{
    /// <summary>One dish on the belt: the two loc-key suffixes it owns, what
    /// it does, what it shows on hover, and how often it comes round. A
    /// readonly struct for the base event's own reason -- it is copied into
    /// `CurrentDish` by value and nothing mutates it.</summary>
    private readonly struct Dish
    {
        public Dish(string optionKey, string titleKey, Func<Task> action,
                    IEnumerable<IHoverTip> hoverTips, float weight)
        {
            OptionKey = optionKey;
            TitleKey = titleKey;
            Action = action;
            HoverTips = hoverTips;
            Weight = weight;
        }

        /// <summary>The suffix under `pages.`, e.g.
        /// `ALL.options.CAVIAR`.</summary>
        public string OptionKey { get; }

        /// <summary>The suffix under the entry, e.g.
        /// `DISHES.CAVIAR.title`.</summary>
        public string TitleKey { get; }

        public Func<Task> Action { get; }

        public IEnumerable<IHoverTip> HoverTips { get; }

        public float Weight { get; }
    }

    private string _lastDishOptionKey = "";

    private int _numOfGrabs;

    private Dish _currentDish;

    private int NumOfGrabs
    {
        get => _numOfGrabs;
        set
        {
            AssertMutable();
            _numOfGrabs = value;
        }
    }

    private Dish CurrentDish
    {
        get => _currentDish;
        set
        {
            AssertMutable();
            _currentDish = value;
        }
    }

    /// <summary>`EndlessConveyor.cs:88-96`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(40),
            new GoldVar("GoldenFyshGold", 75),
            new HealVar("ClamRollHeal", 10m),
            new MaxHpVar("CaviarMaxHp", 4m),
            new StringVar("CurrentDishTitle"),
            new StringVar("LastDishTitle"),
        };

    /// <summary>The base event's gate: every player holding 120, which is
    /// three plates rather than one -- the room is a belt, not a purchase.
    /// </summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Gold >= 120);

    /// <summary>The first dish is rolled before the page is drawn, because the
    /// INITIAL description names it through the `CurrentDishTitle` var.
    /// </summary>
    public override void CalculateVars()
    {
        RollDish();
        ((StringVar)DynamicVars["CurrentDishTitle"]).StringValue = DishTitle(CurrentDish);
    }

    /// <summary>The dish's own name, off this DRESSING's `DISHES` row.</summary>
    private string DishTitle(Dish dish) =>
        new LocString("events", Id.Entry + "." + dish.TitleKey).GetFormattedText();

    /// <summary>Two options, in the base event's order: whatever the belt is
    /// carrying, and the way out.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            GenerateGrabSomethingOffTheBeltOption(),
            new EventOption(this, ObserveChef, InitialOptionKey("OBSERVE_CHEF")),
        };

    /// <summary>
    /// `GrabSomethingOffTheBelt`: pay unless it is the Golden Fysh, eat, roll
    /// the next plate, shift the two title vars along, and offer the belt
    /// again beside Leave.
    /// </summary>
    private async Task GrabSomethingOffTheBelt()
    {
        if (_currentDish.OptionKey != "ALL.options.GOLDEN_FYSH")
        {
            await PlayerCmd.LoseGold(DynamicVars.Gold.IntValue, Owner, GoldLossType.Spent);
        }

        await CurrentDish.Action();
        RollDish();
        ((StringVar)DynamicVars["LastDishTitle"]).StringValue =
            ((StringVar)DynamicVars["CurrentDishTitle"]).StringValue;
        ((StringVar)DynamicVars["CurrentDishTitle"]).StringValue = DishTitle(CurrentDish);
        SetEventState(L10NLookup(PageKey("GRAB_SOMETHING_OFF_THE_BELT.description")),
            new List<EventOption>
            {
                GenerateGrabSomethingOffTheBeltOption(),
                new EventOption(this, Leave,
                    PageKey("GRAB_SOMETHING_OFF_THE_BELT.options.LEAVE")),
            });
    }

    /// <summary>The belt option, or the locked twin when the purse is short.
    /// The twin is keyed on `pages.ALL`, like the dishes, and is the one key
    /// on this branch that is not a dish -- which is why it is the key the
    /// face's belt line pairs with.</summary>
    private EventOption GenerateGrabSomethingOffTheBeltOption()
    {
        if (Owner.Gold >= DynamicVars.Gold.IntValue)
        {
            return new EventOption(this, GrabSomethingOffTheBelt,
                PageKey(_currentDish.OptionKey), _currentDish.HoverTips);
        }

        return new EventOption(this, null, PageKey("ALL.options.LOCKED"));
    }

    private async Task ClamRoll()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars["ClamRollHeal"].IntValue);
    }

    private async Task Caviar()
    {
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars["CaviarMaxHp"].IntValue);
    }

    /// <summary>The base event's potion roll: the character's own pool and the
    /// shared one together, and a null answer left alone rather than
    /// offered.</summary>
    private async Task SuspiciousCondiment()
    {
        IEnumerable<PotionModel> items = Owner.Character.PotionPool
            .GetUnlockedPotions(Owner.UnlockState)
            .Concat(ModelDb.PotionPool<SharedPotionPool>().GetUnlockedPotions(Owner.UnlockState));

        PotionModel potion = Owner.PlayerRng.Rewards.NextItem(items);
        if (potion != null)
        {
            await RewardsCmd.OfferCustom(Owner, new List<Reward>(1)
            {
                new PotionReward(potion.ToMutable(), Owner),
            });
        }
    }

    /// <summary>One card off the deck, transformed -- and nothing at all when
    /// the grid comes back empty, which is the base event's own null
    /// check.</summary>
    private async Task JellyLiver()
    {
        CardModel card = (await CardSelectCmd.FromDeckForTransformation(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }
    }

    /// <summary>The forced plate: a Feeding Frenzy, made on the run rather
    /// than drawn from a pool.</summary>
    private async Task SeapunkSalad()
    {
        CardModel card = Owner.RunState.CreateCard<FeedingFrenzy>(Owner);
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 1.2f,
            CardPreviewStyle.EventLayout);
    }

    /// <summary>One colourless card at default odds -- the base event sets no
    /// creation flags here, so neither does this.</summary>
    private async Task FriedEel()
    {
        CardCreationOptions options = CardCreationOptions
            .ForNonCombatWithDefaultOdds(
                new List<CardPoolModel> { ModelDb.CardPool<ColorlessCardPool>() });
        CardModel card = CardFactory.CreateForReward(Owner, 1, options).First().Card;
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(card, PileType.Deck), 1.2f,
            CardPreviewStyle.EventLayout);
    }

    private async Task GoldenFysh()
    {
        await PlayerCmd.GainGold(DynamicVars["GoldenFyshGold"].BaseValue, Owner);
    }

    private Task SpicySnappy()
    {
        List<CardModel> upgradable = PileType.Deck.GetPile(Owner).Cards
            .Where((CardModel c) => c.IsUpgradable).ToList();
        if (upgradable.Count != 0)
        {
            CardModel card = Rng.NextItem(upgradable);
            CardCmd.Upgrade(card);
        }

        return Task.CompletedTask;
    }

    /// <summary>
    /// The base event's weighted roll, clause for clause. Every fifth grab is
    /// the Seapunk Salad and nothing else; otherwise the four unconditional
    /// dishes, plus Suspicious Condiment with a slot free, Clam Roll while
    /// hurt and Golden Fysh after the first grab, less whatever came round
    /// last.
    /// </summary>
    private void RollDish()
    {
        NumOfGrabs++;
        if (NumOfGrabs % 5 == 0)
        {
            _lastDishOptionKey = "ALL.options.SEAPUNK_SALAD";
            _currentDish = new Dish("ALL.options.SEAPUNK_SALAD", "DISHES.SEAPUNK_SALAD.title",
                SeapunkSalad, HoverTipFactory.FromCardWithCardHoverTips<FeedingFrenzy>(), 0f);
            return;
        }

        List<Dish> belt = new List<Dish>
        {
            new Dish("ALL.options.CAVIAR", "DISHES.CAVIAR.title",
                Caviar, Array.Empty<IHoverTip>(), 6f),
            new Dish("ALL.options.SPICY_SNAPPY", "DISHES.SPICY_SNAPPY.title",
                SpicySnappy, Array.Empty<IHoverTip>(), 3f),
            new Dish("ALL.options.JELLY_LIVER", "DISHES.JELLY_LIVER.title",
                JellyLiver, new List<IHoverTip> { HoverTipFactory.Static(StaticHoverTip.Transform) }, 3f),
            new Dish("ALL.options.FRIED_EEL", "DISHES.FRIED_EEL.title",
                FriedEel, Array.Empty<IHoverTip>(), 3f),
        };

        if (Owner.HasOpenPotionSlots)
        {
            belt.Add(new Dish("ALL.options.SUSPICIOUS_CONDIMENT",
                "DISHES.SUSPICIOUS_CONDIMENT.title",
                SuspiciousCondiment, Array.Empty<IHoverTip>(), 3f));
        }

        if (Owner.Creature.CurrentHp != Owner.Creature.MaxHp)
        {
            belt.Add(new Dish("ALL.options.CLAM_ROLL", "DISHES.CLAM_ROLL.title",
                ClamRoll, Array.Empty<IHoverTip>(), 6f));
        }

        if (NumOfGrabs > 1)
        {
            belt.Add(new Dish("ALL.options.GOLDEN_FYSH", "DISHES.GOLDEN_FYSH.title",
                GoldenFysh, Array.Empty<IHoverTip>(), 1f));
        }

        belt.RemoveAll((Dish d) => d.OptionKey == _lastDishOptionKey);

        float total = 0f;
        foreach (Dish dish in belt)
        {
            total += dish.Weight;
        }

        float roll = Rng.NextFloat() * total;
        float running = 0f;
        foreach (Dish dish in belt)
        {
            running += dish.Weight;
            if (roll < running)
            {
                _lastDishOptionKey = dish.OptionKey;
                _currentDish = dish;
                break;
            }
        }
    }

    /// <summary>`ObserveChef`: one random upgrade for not eating, and the end
    /// of it.</summary>
    private Task ObserveChef()
    {
        IEnumerable<CardModel> upgradable = Owner.Deck.Cards
            .Where((CardModel c) => c.IsUpgradable);
        IEnumerable<CardModel> materialised = (upgradable as CardModel[]) ?? upgradable.ToArray();
        if (materialised.Any())
        {
            CardCmd.Upgrade(Rng.NextItem(materialised));
        }

        SetEventFinished(L10NLookup(PageKey("OBSERVE_CHEF.description")));
        return Task.CompletedTask;
    }

    /// <summary>`Leave`: its own page, and nothing paid for it.</summary>
    private Task Leave()
    {
        SetEventFinished(L10NLookup(PageKey("LEAVE.description")));
        return Task.CompletedTask;
    }
}
