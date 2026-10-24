using System;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;
using Doubt = MegaCrit.Sts2.Core.Models.Cards.Doubt;

namespace KleeMod.Tests;

/// <summary>
/// THE STORY REWARDS PASS (<c>review/active/story-rewards-pass-2026-10-19.md</c>,
/// ruled all (a) 2026-10-19: "I like the new draft - agreed all around!").
/// Named cards became rarity offers, relics and transforms were repriced, and
/// the kept exceptions stayed. Each changed row of the paper's table is held
/// here against the table that ships; the words are held against the story
/// papers by each character's own suite.
/// </summary>
public class StoryRewardsTests
{
    private static StoryEvent E(Type t) =>
        StoryRegistry.All.SelectMany(s => s.Events).Single(e => e.EventType == t);

    private static StoryOption O(Type evt, string key) => E(evt).Options.Single(o => o.Key == key);

    private static StoryEffect OfferOf(StoryOption o) =>
        o.Effects.Single(s => s.Kind == StoryEffectKind.ChooseOfferToDeck);

    // (event, option, rarity, type, upgraded, companions, HP paid)
    public static readonly TheoryData<Type, string, CardRarity, CardType?, bool, bool, int> Offers = new()
    {
        { typeof(KleeStarsnatchCliff), "JUST_ONE_LITTLE_BOMB", CardRarity.Common, CardType.Attack, false, false, 0 },
        { typeof(KleeMomsMarks), "TRY_THE_RECIPE", CardRarity.Rare, null, false, false, 10 },
        { typeof(KleeFoundYou), "ASK_NICELY", CardRarity.Uncommon, CardType.Attack, false, false, 0 },
        { typeof(KleeKnightsComeLooking), "NOELLE", CardRarity.Common, null, true, true, 0 },
        { typeof(KleeKnightsComeLooking), "KAEYA", CardRarity.Uncommon, null, true, true, 6 },
        { typeof(KleeKnightsComeLooking), "ALBEDO", CardRarity.Rare, null, true, true, 12 },
        { typeof(KleeMomsLastNote), "TRY_THE_TRICK", CardRarity.Rare, null, true, false, 10 },
        { typeof(VarkaDispatchFromMondstadt), "REQUEST_REINFORCEMENTS", CardRarity.Uncommon, null, false, true, 0 },
        { typeof(VarkaRearguard), "TAKE_THE_REAR", CardRarity.Rare, null, false, false, 10 },
        { typeof(VarkaWolfOfTheNorth), "ASK_AFTER_THE_PACK", CardRarity.Uncommon, CardType.Attack, false, false, 0 },
        { typeof(VarkaActingGrandMaster), "LET_HER_LEAD", CardRarity.Rare, null, true, true, 10 },
        { typeof(VarkaLongWayHome), "EULA", CardRarity.Uncommon, CardType.Attack, true, false, 0 },
        { typeof(VarkaLongWayHome), "NOELLE", CardRarity.Uncommon, CardType.Skill, true, false, 0 },
        { typeof(VarkaLongWayHome), "DILUC", CardRarity.Uncommon, CardType.Power, true, false, 0 },
        { typeof(FurinaUnderstudy), "TEACH_HER_THE_ENDING", CardRarity.Uncommon, null, true, false, 6 },
        { typeof(FurinaLetterFromTheCourt), "KEEP_IT", CardRarity.Common, CardType.Skill, false, false, 0 },
        { typeof(FurinaCurtainCall), "GIVE_THEM_THE_FINALE", CardRarity.Rare, null, true, false, 10 },
        { typeof(KokomiEmptyRoom), "READ_THE_TOP_BOOK", CardRarity.Uncommon, CardType.Power, false, false, 0 },
        { typeof(KokomiReportFromGorou), "SEND_FOR_REINFORCEMENTS", CardRarity.Uncommon, null, false, true, 0 },
        { typeof(KokomiTideComesIn), "SHAPE_A_SHOAL", CardRarity.Uncommon, CardType.Power, true, false, 6 },
        // Kept: The Other Commander's offer was already a rarity offer.
        { typeof(KokomiOtherCommander), "CONCEDE", CardRarity.Rare, null, false, false, 0 },
    };

    [Theory]
    [MemberData(nameof(Offers))]
    public void A_named_card_became_a_rarity_offer_of_three(
        Type evt, string key, CardRarity rarity, CardType? type, bool upgraded, bool companions, int hp)
    {
        var o = O(evt, key);
        var offer = OfferOf(o);
        Assert.Equal(3, offer.Amount);
        Assert.Equal(new StoryOffer(rarity, type, upgraded, companions), offer.Offer);
        Assert.Equal(hp, o.HpCost);
        // No named card is left in the option.
        Assert.DoesNotContain(o.Effects, s => s.Kind is StoryEffectKind.AddCard or StoryEffectKind.AddUpgradedCard
            && s.Card != typeof(Doubt));
        // The line is the base templates': "Lose 10 HP. Choose 1 of 3 random
        // upgraded Rare cards to add to your deck."
        var line = offer.Offer!.Text(3);
        Assert.Contains(line, o.Description);
        if (hp > 0) Assert.StartsWith($"Lose {hp} HP. ", o.Description);
    }

    [Fact]
    public void Every_offer_in_every_table_says_what_it_offers()
    {
        var offers = StoryRegistry.All.SelectMany(s => s.Events).SelectMany(e => e.Options)
            .Where(o => o.Effects.Any(s => s.Kind == StoryEffectKind.ChooseOfferToDeck))
            .ToList();
        Assert.Equal(Offers.Count(), offers.Count);
        foreach (var o in offers)
        {
            var e = OfferOf(o);
            Assert.NotNull(e.Offer);
            Assert.Contains(e.Offer!.Text(e.Amount), o.Description);
        }
    }

    [Fact]
    public void The_offer_line_is_the_base_templates()
    {
        Assert.Equal("Choose 1 of 3 random Uncommon Attacks to add to your deck.",
            new StoryOffer(CardRarity.Uncommon, CardType.Attack).Text(3));
        Assert.Equal("Choose 1 of 3 random upgraded Rare cards to add to your deck.",
            new StoryOffer(CardRarity.Rare, Upgraded: true).Text(3));
        Assert.Equal("Choose 1 of 3 random upgraded Common Companions to add to your deck.",
            new StoryOffer(CardRarity.Common, Upgraded: true, Companions: true).Text(3));
        Assert.Equal("Choose 1 of 3 random Common Skills to add to your deck.",
            new StoryOffer(CardRarity.Common, CardType.Skill).Text(3));
        Assert.Equal("Choose 1 of 3 random Uncommon Powers to add to your deck.",
            new StoryOffer(CardRarity.Uncommon, CardType.Power).Text(3));
    }

    [Fact]
    public void An_offer_admits_its_rarity_and_type_only()
    {
        var attacks = new StoryOffer(CardRarity.Uncommon, CardType.Attack);
        Assert.True(attacks.Admits(CardRarity.Uncommon, CardType.Attack));
        Assert.False(attacks.Admits(CardRarity.Uncommon, CardType.Skill));
        Assert.False(attacks.Admits(CardRarity.Rare, CardType.Attack));
        Assert.False(attacks.Admits(CardRarity.Common, CardType.Attack));
        var rares = new StoryOffer(CardRarity.Rare);
        Assert.True(rares.Admits(CardRarity.Rare, CardType.Attack));
        Assert.True(rares.Admits(CardRarity.Rare, CardType.Power));
        Assert.False(rares.Admits(CardRarity.Uncommon, CardType.Power));
        Assert.False(rares.Admits(CardRarity.Basic, CardType.Attack));
    }

    [Fact]
    public void The_offer_draws_from_her_pool_or_her_Companions_structural()
    {
        // STRUCTURAL: her card pool's unlocked cards (what her rewards roll
        // from) or the Companions she can be offered (the reward slot's and
        // the shop's rule), filtered by the offer; three distinct on the
        // event's own Rng; upgraded when the offer says so.
        var pool = Il.Calls(Il.Method(nameof(StoryEventModel), "OfferPool"));
        Assert.Contains("CardPoolModel.GetUnlockedCards", pool);
        Assert.Contains("CompanionPool.Eligible", pool);
        Assert.Contains("StoryEventModel.OfferPool", Il.Calls(Il.Method(nameof(StoryEventModel), "Apply")));
        var choose = typeof(StoryEventModel).GetNestedTypes(HeadlessGame.All)
            .SelectMany(t => t.GetMethods(HeadlessGame.All))
            .Append(Il.Method(nameof(StoryEventModel), "ChooseFromPool"))
            .Where(m => m.GetMethodBody() != null)
            .SelectMany(m => Il.Calls(m))
            .ToList();
        Assert.Contains("CardCmd.Upgrade", choose);
        var direct = Il.Calls(Il.Method(nameof(StoryEventModel), "ChooseFromPool"));
        Assert.Contains("StoryRules.PickRandom", direct);
        Assert.Contains("EventModel.SelectCardsToAddToDeckFromGrid", direct);
        // The story telemetry logs the cards offered and the card taken
        // (StoryChoiceRecord's lists, filled here for every offer).
        Assert.Contains("List`1.AddRange", direct);
        // What the lock counts is the same offer.
        Assert.Contains("StoryEventModel.OfferPool", Il.Calls(Il.Method(nameof(StoryEventModel), "OfferSize")));
    }

    [Fact]
    public void An_offer_with_nothing_to_show_is_locked_and_fewer_than_three_is_not()
    {
        var o = O(typeof(VarkaWolfOfTheNorth), "ASK_AFTER_THE_PACK");
        StoryDeckView Deck(int n) => new(999, 10, 10, 0, 0, OfferSize: _ => n);
        Assert.True(StoryRules.IsLocked(o, Deck(0)));
        Assert.False(StoryRules.IsLocked(o, Deck(1)));
        Assert.False(StoryRules.IsLocked(o, Deck(3)));
        // Not asked: never a lock.
        Assert.False(StoryRules.IsLocked(o, new StoryDeckView(0, 0, 0, 0, 0)));
        // A paid offer locks the same way.
        Assert.True(StoryRules.IsLocked(O(typeof(KleeKnightsComeLooking), "ALBEDO"), Deck(0)));
        // Fewer than three are offered as they are: the draw takes those there are.
        Assert.Equal(new[] { "a", "b" }, StoryRules.PickRandom(new[] { "a", "b" }, 3, n => 0));
    }

    // ---- Relics, transforms, curses ----------------------------------------------

    private static void Steps(Type evt, string key, params (StoryEffectKind Kind, int Amount)[] steps)
    {
        var o = O(evt, key);
        Assert.Equal(steps, o.Effects.Select(s => (s.Kind, s.Amount)).ToArray());
    }

    [Fact]
    public void Relics_are_repriced()
    {
        Steps(typeof(KleeFoundYou), "GRAB_AND_RUN",
            (StoryEffectKind.LoseHp, 11), (StoryEffectKind.GainRandomRelic, 0), (StoryEffectKind.RemoveEvery, 0));
        Steps(typeof(KleeAlicesCache), "OPEN_IT", (StoryEffectKind.LoseHp, 12), (StoryEffectKind.GainRandomRelic, 0));
        Steps(typeof(FurinaOratricesEcho), "PLEAD_GUILTY", (StoryEffectKind.LoseHp, 12), (StoryEffectKind.GainRandomRelic, 0));
        Steps(typeof(FurinaEmptyThrone), "SIT_IN_IT", (StoryEffectKind.LoseHp, 18), (StoryEffectKind.GainRandomRareRelic, 0));
        Steps(typeof(KokomiEndgame), "OFFER_HER_LAST_PIECE", (StoryEffectKind.LoseHp, 18), (StoryEffectKind.GainRandomRareRelic, 0));
        var bones = O(typeof(KokomiSerpentsBones), "LAY_A_HAND");
        Steps(typeof(KokomiSerpentsBones), "LAY_A_HAND", (StoryEffectKind.LoseMaxHp, 8), (StoryEffectKind.GainRandomRelic, 0));
        Assert.Equal("Lose 8 Max HP. Gain a random relic.", bones.Description);
        Assert.Equal(8, bones.MaxHpCost);
        Assert.Equal(0, bones.HpCost);
    }

    [Fact]
    public void A_relic_takes_a_curse_that_stays()
    {
        var o = O(typeof(FurinaEmptyHouse), "TAKE_A_COSTUME");
        Assert.Equal("Gain a random relic. Add [gold]Doubt[/gold] to your deck.", o.Description);
        Assert.Equal(StoryEffectKind.GainRandomRelic, o.Effect.Kind);
        Assert.Equal(typeof(Doubt), o.Then.Single().Card);
    }

    [Theory]
    [InlineData(typeof(KleeAlicesCache), "LEAVE_IT")]
    [InlineData(typeof(FurinaOratricesEcho), "GIVE_IT_A_PERFORMANCE")]
    [InlineData(typeof(KokomiEndgame), "PAY_ITS_STAKE")]
    public void Two_transforms_cost_100_Gold_and_lock_under_it(Type evt, string key)
    {
        var o = O(evt, key);
        Assert.Equal("Lose 100 Gold. Transform 2 cards.", o.Description);
        Steps(evt, key, (StoryEffectKind.LoseGold, 100), (StoryEffectKind.TransformCards, 2));
        Assert.True(StoryRules.IsLocked(o, new StoryDeckView(99, 10, 10, 0, 0)));
        Assert.False(StoryRules.IsLocked(o, new StoryDeckView(100, 10, 10, 0, 0)));
    }

    [Fact]
    public void A_full_report_costs_50_Gold_a_Curse()
    {
        var o = O(typeof(VarkaActingGrandMaster), "PROMISE_A_FULL_REPORT");
        Assert.Equal("Remove every Curse. Lose 50 Gold for each.", o.Description);
        Steps(typeof(VarkaActingGrandMaster), "PROMISE_A_FULL_REPORT", (StoryEffectKind.RemoveEveryCurseLoseGoldEach, 50));
        Assert.True(StoryRules.IsLocked(o, new StoryDeckView(149, 10, 10, 3, 0)));
        Assert.False(StoryRules.IsLocked(o, new StoryDeckView(150, 10, 10, 3, 0)));
    }

    [Fact]
    public void Saving_the_cache_says_the_chest_waits()
    {
        var o = O(typeof(KleeAlicesCache), "SAVE_IT");
        Assert.Equal("Lose 5 HP. Gain a random potion. Klee takes Mom's chest with her.", o.Description);
        Steps(typeof(KleeAlicesCache), "SAVE_IT", (StoryEffectKind.LoseHp, 5), (StoryEffectKind.GainRandomPotions, 1));
    }

    // ---- Kept on purpose -------------------------------------------------------

    [Fact]
    public void The_kept_exceptions_are_unchanged()
    {
        // The First Exam's upgraded Four Winds' Ascension (his Basic).
        var exam = O(typeof(VarkaFirstExam), "KNOCK_THEM_ALL_DOWN");
        Assert.Equal(typeof(ProtoVkFourWindsAscension), exam.Then.Single().Card);
        Assert.Equal(StoryEffectKind.AddUpgradedCard, exam.Then.Single().Kind);
        Assert.Equal(8, exam.HpCost);
        // Mom's Last Note's free Rare relic.
        Steps(typeof(KleeMomsLastNote), "OPEN_THE_CHEST", (StoryEffectKind.GainRandomRareRelic, 0));
        // The Second Satchel's Overdue Reports removal.
        Assert.Contains(O(typeof(VarkaSecondSatchel), "SIGN_BY_LAMPLIGHT").Effects,
            s => s.Kind == StoryEffectKind.RemoveEvery && s.Card == typeof(OverdueReports));
        // Pick 3 (a): Cast the sequel keeps 3 random Guest Stars.
        var sequel = O(typeof(FurinaSteambirdClipping), "CAST_THE_SEQUEL");
        Assert.Equal("Choose 1 of 3 random Guest Stars to add to your deck.", sequel.Description);
        Steps(typeof(FurinaSteambirdClipping), "CAST_THE_SEQUEL", (StoryEffectKind.ChooseFromPoolToDeck, 3));
    }
}
