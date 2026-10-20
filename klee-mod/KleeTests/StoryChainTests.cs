using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization.Metadata;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Runs.History;
using Xunit;
using Doubt = MegaCrit.Sts2.Core.Models.Cards.Doubt;

namespace KleeMod.Tests;

/// <summary>
/// THE STORY CHAINS (<c>review/active/klee-varka-story-chains-2026-10-14.md</c>,
/// ruled 2026-10-15: "we can ship the event branch; looks good to me!").
///
/// The same headless boundary as <see cref="KleeStoryTests"/>: every string is
/// held against the paper, every routing decision runs through the pure
/// function the game calls (<see cref="StoryRules.Route"/>,
/// <see cref="StoryRules.Records"/>, <see cref="StoryRules.IsLocked"/>), the
/// saved story survives the game's own JSON for the run history, and what an
/// option DOES against a live run is pinned structurally on the commands it
/// calls.
/// </summary>
public class StoryChainTests
{
    private static readonly CharacterStory K = KleeStory.Table;
    private static readonly CharacterStory V = VarkaStory.Table;

    internal static string Paper() => File.ReadAllText(Path.Combine(
        RepoRoot(), "review", "active", "klee-varka-story-chains-2026-10-14.md")).Replace("\r\n", "\n");

    /// <summary>The paper with its prose line breaks joined, so a sentence
    /// wrapped across two lines is found whole.</summary>
    internal static string Flat() => Paper().Replace("\n", " ");

    private static string ToPaper(string s) => s
        .Replace("[i]", "*").Replace("[/i]", "*")
        .Replace("[gold]", "**").Replace("[/gold]", "**");

    private static StoryEvent E(Type t) =>
        K.Events.Concat(V.Events).Single(e => e.EventType == t);

    private static readonly Type[] NewEvents =
    {
        typeof(KleeDodocoGoesMissing), typeof(KleeFoundYou), typeof(KleeMomsMarks),
        typeof(KleeAlicesCache), typeof(KleeMomsLastNote),
        typeof(VarkaSecondSatchel), typeof(VarkaActingGrandMaster), typeof(VarkaRearguard),
        typeof(VarkaSongOnTheWind), typeof(VarkaFirstExam),
    };

    // ---- The words are the paper's --------------------------------------------

    [Fact]
    public void Each_character_has_eight_events_three_old_and_five_new()
    {
        Assert.Equal(8, K.Events.Count);
        Assert.Equal(8, V.Events.Count);
        Assert.Equal(16, K.Events.Concat(V.Events).Select(e => e.EventType).Distinct().Count());
        var paper = Paper();
        foreach (var e in K.Events.Concat(V.Events))
        {
            Assert.Contains($"**{e.Title}", paper);
        }
    }

    [Fact]
    public void Every_new_event_is_the_papers_page_options_and_results()
    {
        var paper = Paper();
        foreach (var t in NewEvents.Append(typeof(KleeStarsnatchCliff)))
        {
            var e = E(t);
            Assert.Contains($"> {ToPaper(e.Body)}", paper);
            if (t == typeof(KleeStarsnatchCliff)) continue; // its effects are batch 1's
            foreach (var o in e.Options)
            {
                // The effect cell may go on with the paper's own note ("(a
                // Rare)", "*(a jackpot)*", "Locked with ..."), which is the
                // rule, not player text.
                var effect = ToPaper(o.Description).TrimEnd('.').Replace("Jean — ", "Jean: ");
                Assert.Contains($"{o.Title} | {effect}", paper);
                Assert.Contains($" | {ToPaper(o.Result!)} |", paper);
            }
        }
    }

    [Fact]
    public void The_Knights_Come_Looking_gains_Everyone_can_come()
    {
        var o = E(typeof(KleeKnightsComeLooking)).Options[3];
        Assert.Contains($"| {o.Title} | {o.Description} | {o.Result} |", Paper());
        Assert.Equal(StoryEffectKind.Nothing, o.Effect.Kind);
        Assert.Empty(o.Then);
    }

    [Fact]
    public void Every_opening_line_is_the_papers()
    {
        var flat = Flat();
        foreach (var e in K.Events.Concat(V.Events))
        {
            foreach (var o in e.Openings)
            {
                // A spoken opening keeps its quotes; a narrated one was quoted
                // in the paper, with its inner speech in single quotes.
                var inPaper = o.Line.StartsWith('"') ? o.Line : "\"" + o.Line.Replace('"', '\'') + "\"";
                Assert.Contains(inPaper, flat);
            }
        }
    }

    [Fact]
    public void The_options_do_what_the_tables_say()
    {
        Steps(typeof(KleeDodocoGoesMissing), 0, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.GainRandomRelic, 0, null));
        Steps(typeof(KleeDodocoGoesMissing), 1, (StoryEffectKind.LoseGold, 50, null), (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(KleeDodocoGoesMissing), 2, (StoryEffectKind.Heal, 15, null), (StoryEffectKind.AddCard, 0, typeof(Doubt)));
        Steps(typeof(KleeFoundYou), 0, (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKoDodocoTag)), (StoryEffectKind.RemoveEvery, 0, typeof(Doubt)));
        Steps(typeof(KleeFoundYou), 1, (StoryEffectKind.LoseHp, 8, null), (StoryEffectKind.GainRandomRelic, 0, null), (StoryEffectKind.RemoveEvery, 0, typeof(Doubt)));
        Steps(typeof(KleeFoundYou), 2, (StoryEffectKind.TransformCards, 1, null), (StoryEffectKind.RemoveEvery, 0, typeof(Doubt)));
        // Every option removes Doubt, and every option's line says so.
        Assert.All(E(typeof(KleeFoundYou)).Options,
            o => Assert.EndsWith(" Remove every [gold]Doubt[/gold].", o.Description));
        Steps(typeof(KleeMomsMarks), 0, (StoryEffectKind.GainGold, 75, null));
        Steps(typeof(KleeMomsMarks), 1, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.AddCard, 0, typeof(ProtoKoAlicesRecipe)));
        Steps(typeof(KleeMomsMarks), 2, (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(KleeAlicesCache), 0, (StoryEffectKind.LoseHp, 15, null), (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(KleeAlicesCache), 1, (StoryEffectKind.LoseHp, 5, null), (StoryEffectKind.GainRandomPotions, 1, null));
        Steps(typeof(KleeAlicesCache), 2, (StoryEffectKind.LoseGold, 50, null), (StoryEffectKind.TransformCards, 2, null));
        Steps(typeof(KleeAlicesCache), 3, (StoryEffectKind.Nothing, 0, null));
        Steps(typeof(KleeMomsLastNote), 0, (StoryEffectKind.Heal, 20, null));
        Steps(typeof(KleeMomsLastNote), 1, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKoAlicesIntroductionMagic)));
        Steps(typeof(KleeMomsLastNote), 2, (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(KleeMomsLastNote), 3, (StoryEffectKind.UpgradeRandomBombCards, 3, null));

        Steps(typeof(VarkaSecondSatchel), 0, (StoryEffectKind.LoseHp, 8, null), (StoryEffectKind.UpgradeRandomCards, 2, null), (StoryEffectKind.RemoveEvery, 0, typeof(OverdueReports)));
        Steps(typeof(VarkaSecondSatchel), 1, (StoryEffectKind.LoseGold, 75, null), (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(VarkaSecondSatchel), 2, (StoryEffectKind.GainRandomPotions, 2, null), (StoryEffectKind.AddCard, 0, typeof(OverdueReports)));
        Steps(typeof(VarkaActingGrandMaster), 0, (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcJeanDandelionBreeze)));
        Steps(typeof(VarkaActingGrandMaster), 1, (StoryEffectKind.RemoveEveryCurseLoseGoldEach, 25, null));
        Steps(typeof(VarkaActingGrandMaster), 2, (StoryEffectKind.UpgradeRandomCards, 3, null), (StoryEffectKind.AddCard, 0, typeof(OverdueReports)));
        Steps(typeof(VarkaRearguard), 0, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.ChooseFromPoolToDeck, 3, null));
        Steps(typeof(VarkaRearguard), 1, (StoryEffectKind.LoseGold, 75, null), (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(VarkaRearguard), 2, (StoryEffectKind.GainRandomPotions, 2, null), (StoryEffectKind.AddCard, 0, typeof(OverdueReports)));
        Steps(typeof(VarkaSongOnTheWind), 0, (StoryEffectKind.Heal, 12, null));
        Steps(typeof(VarkaSongOnTheWind), 1, (StoryEffectKind.GainRandomPotions, 1, null));
        Steps(typeof(VarkaSongOnTheWind), 2, (StoryEffectKind.UpgradeChosenCard, 0, null));
        Steps(typeof(VarkaFirstExam), 0, (StoryEffectKind.LoseHp, 8, null), (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkFourWindsAscension)));
        Steps(typeof(VarkaFirstExam), 1, (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(VarkaFirstExam), 2, (StoryEffectKind.Heal, 15, null));

        // The cards are the paper's, under their own names.
        Assert.Equal("Dodoco Tag", Title(new ProtoKoDodocoTag()));
        Assert.Equal("Alice's Recipe", Title(new ProtoKoAlicesRecipe()));
        Assert.Equal("Alice's Introduction Magic", Title(new ProtoKoAlicesIntroductionMagic()));
        Assert.Equal("Four Winds' Ascension", Title(new ProtoVkFourWindsAscension()));
        Assert.Equal("Jean — Dandelion Breeze", Title(new ProtoMcJeanDandelionBreeze()));
    }

    private static void Steps(Type evt, int option, params (StoryEffectKind Kind, int Amount, Type? Card)[] steps)
    {
        var o = E(evt).Options[option];
        Assert.Equal(steps.Length, o.Effects.Count);
        for (var i = 0; i < steps.Length; i++)
        {
            Assert.Equal(steps[i].Kind, o.Effects[i].Kind);
            Assert.Equal(steps[i].Amount, o.Effects[i].Amount);
            Assert.Equal(steps[i].Card, o.Effects[i].Card);
        }
    }

    [Fact]
    public void An_option_warns_of_every_HP_it_costs()
    {
        Assert.Equal(10, E(typeof(KleeDodocoGoesMissing)).Options[0].HpCost);
        Assert.Equal(15, E(typeof(KleeAlicesCache)).Options[0].HpCost);
        Assert.Equal(12, E(typeof(VarkaWolfOfTheNorth)).Options[0].HpCost);
        Assert.Equal(0, E(typeof(KleeAlicesCache)).Options[3].HpCost);
    }

    [Fact]
    public void The_new_effects_run_the_games_own_commands_structural()
    {
        var apply = Il.Calls(Il.Method(nameof(StoryEventModel), "Apply"));
        Assert.Contains("PlayerCmd.LoseGold", apply);
        Assert.Contains("RelicFactory.PullNextRelicFromFront", apply);
        Assert.Contains("RelicCmd.Obtain", apply);
        Assert.Contains("CardSelectCmd.FromDeckForUpgrade", apply);
        Assert.Contains("CardPileCmd.RemoveFromDeck", apply);
        var potions = Il.Calls(Il.Method(nameof(StoryEventModel), "OfferRandomPotions"));
        Assert.Contains("RewardsCmd.OfferCustom", potions);
        var transform = Il.Calls(Il.Method(nameof(StoryEventModel), "TransformChosen"));
        Assert.Contains("CardSelectCmd.FromDeckForTransformation", transform);
        Assert.Contains("CardCmd.TransformToRandom", transform);
        var every = Il.Calls(Il.Method(nameof(StoryEventModel), "RemoveEvery"));
        Assert.Contains("CardPileCmd.RemoveFromDeck", every);
        // The opening's removal happens as the event begins, for its owner.
        Assert.Contains("StoryEventModel.RemoveEvery",
            Il.Calls(Il.Method(nameof(StoryEventModel), "BeforeEventStarted")));
    }

    // ---- The chain ------------------------------------------------------------

    private static readonly IReadOnlyList<StoryRecord> None = Array.Empty<StoryRecord>();

    private static StoryRecord R(int act, Type t, string? option = null) => new(act, t, option);

    [Fact]
    public void Act_1_draws_one_of_three_at_random_and_the_same_one_on_a_reload()
    {
        foreach (var story in new[] { K, V })
        {
            var act1 = story.Events.Where(e => e.ActIndex == 0).ToList();
            Assert.Equal(3, act1.Count);
            Assert.All(act1, e => Assert.Empty(e.Follows));
            var drawn = new HashSet<Type>();
            for (ulong seed = 0; seed < 200; seed++)
            {
                var e = StoryRules.Route(story, 0, None, seed)!;
                Assert.Equal(0, e.ActIndex);
                Assert.Same(e, StoryRules.Route(story, 0, None, seed));
                drawn.Add(e.EventType);
            }
            Assert.Equal(act1.Select(e => e.EventType).ToHashSet(), drawn);
        }
    }

    [Theory]
    [InlineData(typeof(KleeStarsnatchCliff), typeof(KleeLetterFromJean))]
    [InlineData(typeof(KleeDodocoGoesMissing), typeof(KleeFoundYou))]
    [InlineData(typeof(KleeMomsMarks), typeof(KleeAlicesCache))]
    [InlineData(typeof(VarkaDispatchFromMondstadt), typeof(VarkaSecondSatchel))]
    [InlineData(typeof(VarkaRearguard), typeof(VarkaWolfOfTheNorth))]
    [InlineData(typeof(VarkaSongOnTheWind), typeof(VarkaFirstExam))]
    public void The_act_1_event_picks_act_2s(Type act1, Type act2)
    {
        var story = act1.Name.StartsWith("Klee") ? K : V;
        Assert.Equal(act2, StoryRules.Route(story, 1, new[] { R(0, act1, "X") }, 7UL)!.EventType);
    }

    [Theory]
    [InlineData(typeof(KleeLetterFromJean), typeof(KleeKnightsComeLooking))]
    [InlineData(typeof(KleeFoundYou), typeof(KleeKnightsComeLooking))]
    [InlineData(typeof(KleeAlicesCache), typeof(KleeMomsLastNote))]
    [InlineData(typeof(VarkaSecondSatchel), typeof(VarkaActingGrandMaster))]
    [InlineData(typeof(VarkaWolfOfTheNorth), typeof(VarkaLongWayHome))]
    [InlineData(typeof(VarkaFirstExam), typeof(VarkaLongWayHome))]
    public void The_act_2_event_picks_act_3s(Type act2, Type act3)
    {
        var story = act2.Name.StartsWith("Klee") ? K : V;
        Assert.Equal(act3, StoryRules.Route(story, 2, new[] { R(1, act2, "X") }, 7UL)!.EventType);
    }

    [Fact]
    public void A_skipped_act_falls_back_to_the_home_thread()
    {
        // No act-1 event: act 2 is the home thread.
        Assert.Equal(typeof(KleeLetterFromJean), StoryRules.Route(K, 1, None, 7UL)!.EventType);
        Assert.Equal(typeof(VarkaWolfOfTheNorth), StoryRules.Route(V, 1, None, 7UL)!.EventType);
        // No act-2 event: act 3 is the home finale, whatever act 1 started.
        foreach (var t in new[] { typeof(KleeMomsMarks), typeof(KleeDodocoGoesMissing), typeof(KleeStarsnatchCliff) })
        {
            Assert.Equal(typeof(KleeKnightsComeLooking), StoryRules.Route(K, 2, new[] { R(0, t, "X") }, 7UL)!.EventType);
        }
        foreach (var t in new[] { typeof(VarkaDispatchFromMondstadt), typeof(VarkaSongOnTheWind) })
        {
            Assert.Equal(typeof(VarkaLongWayHome), StoryRules.Route(V, 2, new[] { R(0, t, "X") }, 7UL)!.EventType);
        }
        Assert.Equal(typeof(KleeKnightsComeLooking), StoryRules.Route(K, 2, None, 7UL)!.EventType);
        Assert.Equal(1, K.Events.Count(e => e.Home && e.ActIndex == 1));
        Assert.Equal(1, K.Events.Count(e => e.Home && e.ActIndex == 2));
        Assert.Equal(1, V.Events.Count(e => e.Home && e.ActIndex == 1));
        Assert.Equal(1, V.Events.Count(e => e.Home && e.ActIndex == 2));
    }

    [Fact]
    public void At_most_one_fires_per_act()
    {
        for (var act = 0; act < 3; act++)
        {
            foreach (var story in new[] { K, V })
            {
                var fired = story.Events.First(e => e.ActIndex == act);
                Assert.Null(StoryRules.Route(story, act, new[] { R(act, fired.EventType) }, 7UL));
                // Still open (no option chosen yet, as after a save mid-event): still fired.
                Assert.Null(StoryRules.EventFor(
                    new (Type, IReadOnlyList<StoryRecord>)[] { (story.Character, new[] { R(act, fired.EventType) }) },
                    act, 7UL));
            }
        }
        Assert.Null(StoryRules.Route(K, 3, None, 7UL));
    }

    [Fact]
    public void In_co_op_each_characters_event_goes_only_to_its_owner()
    {
        foreach (var e in K.Events)
        {
            Assert.True(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Klee), e.EventType));
            Assert.False(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Varka), e.EventType));
        }
        foreach (var e in V.Events)
        {
            Assert.True(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Varka), e.EventType));
            Assert.False(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Klee), e.EventType));
        }
    }

    // ---- Openings and the option that depends on act 2 ------------------------

    private static string? Opening(Type evt, params StoryRecord[] records) =>
        StoryRules.OpeningFor(E(evt), records)?.Key;

    [Fact]
    public void Later_events_open_with_the_line_that_matches_what_you_did()
    {
        var dodoco = typeof(KleeDodocoGoesMissing);
        Assert.Equal("CHASED", Opening(typeof(KleeFoundYou), R(0, dodoco, "CHASE_IT")));
        Assert.Equal("BAIT", Opening(typeof(KleeFoundYou), R(0, dodoco, "LEAVE_MORA_AS_BAIT")));
        Assert.Equal("WAITED", Opening(typeof(KleeFoundYou), R(0, dodoco, "WAIT_HERE")));

        var cache = typeof(KleeAlicesCache);
        Assert.Equal("OPENED", Opening(typeof(KleeMomsLastNote), R(1, cache, "OPEN_IT")));
        Assert.Equal("SAVED", Opening(typeof(KleeMomsLastNote), R(1, cache, "SAVE_IT")));
        Assert.Equal("LEFT", Opening(typeof(KleeMomsLastNote), R(1, cache, "LEAVE_IT")));
        Assert.Equal("NO_CACHE", Opening(typeof(KleeMomsLastNote), R(1, cache, "BACK_AWAY")));
        Assert.Equal("NO_CACHE", Opening(typeof(KleeMomsLastNote)));

        var dispatch = typeof(VarkaDispatchFromMondstadt);
        Assert.Equal("SIGNED", Opening(typeof(VarkaSecondSatchel), R(0, dispatch, "SIGN_EVERY_ONE")));
        Assert.Equal("LATER", Opening(typeof(VarkaSecondSatchel), R(0, dispatch, "SIGN_THEM_LATER")));
        Assert.Equal("REINFORCEMENTS", Opening(typeof(VarkaSecondSatchel), R(0, dispatch, "REQUEST_REINFORCEMENTS")));

        var rear = typeof(VarkaRearguard);
        Assert.Equal("TOOK_THE_REAR", Opening(typeof(VarkaLongWayHome), R(0, rear, "TAKE_THE_REAR"), R(1, typeof(VarkaWolfOfTheNorth), "REST")));
        Assert.Equal("SUPPLIES", Opening(typeof(VarkaLongWayHome), R(0, rear, "LEAVE_SUPPLIES")));
        Assert.Equal("SENT_DOWN", Opening(typeof(VarkaLongWayHome), R(0, rear, "SEND_THEM_DOWN")));
        Assert.Null(Opening(typeof(VarkaLongWayHome), R(0, typeof(VarkaSongOnTheWind), "HUM_ALONG")));
    }

    [Fact]
    public void Dodoco_comes_home_by_the_knights_when_act_2_brought_no_event()
    {
        var knights = typeof(KleeKnightsComeLooking);
        var missing = R(0, typeof(KleeDodocoGoesMissing), "WAIT_HERE");
        // The Dodoco thread: Found You! fired in act 2.
        Assert.Equal("DODOCO_THREAD", Opening(knights, missing, R(1, typeof(KleeFoundYou), "ASK_NICELY")));
        // Missing in act 1, nothing in act 2: a knight brings Dodoco, and
        // Doubt is removed as the event opens.
        Assert.Equal("DODOCO_FOUND", Opening(knights, missing));
        var found = E(knights).Openings.Single(o => o.Key == "DODOCO_FOUND");
        Assert.Equal(typeof(Doubt), found.RemovesOnOpen);
        // Any other road: the page as it was.
        Assert.Null(Opening(knights, R(0, typeof(KleeStarsnatchCliff), "LEAVE_THEM_BE"), R(1, typeof(KleeLetterFromJean), "READ_IT_TWICE")));
        Assert.Null(Opening(knights, R(0, typeof(KleeMomsMarks), "ADD_A_MARK")));
        Assert.Null(Opening(knights));
        // Found You! itself takes Doubt away on every option.
        Assert.All(E(typeof(KleeFoundYou)).Options, o =>
            Assert.Contains(o.Effects, s => s.Kind == StoryEffectKind.RemoveEvery && s.Card == typeof(Doubt)));
    }

    [Fact]
    public void Moms_Last_Note_offers_the_chest_only_if_it_was_saved()
    {
        var note = E(typeof(KleeMomsLastNote));
        var saved = StoryRules.OptionsFor(note, new[] { R(1, typeof(KleeAlicesCache), "SAVE_IT") });
        Assert.Equal(new[] { "READ_IT_OUT_LOUD", "TRY_THE_TRICK", "OPEN_THE_CHEST" }, saved.Select(o => o.Key));
        foreach (var other in new[] { "OPEN_IT", "LEAVE_IT", "BACK_AWAY" })
        {
            var shown = StoryRules.OptionsFor(note, new[] { R(1, typeof(KleeAlicesCache), other) });
            Assert.Equal(new[] { "READ_IT_OUT_LOUD", "TRY_THE_TRICK", "FOLD_INTO_A_FUSE" }, shown.Select(o => o.Key));
        }
        Assert.Equal(3, StoryRules.OptionsFor(note, None).Count);
        // Every other event shows all its options.
        foreach (var e in K.Events.Concat(V.Events).Where(e => e != note))
        {
            Assert.Equal(e.Options.Count, StoryRules.OptionsFor(e, None).Count);
        }
    }

    [Fact]
    public void Every_opening_has_its_page_row_and_the_page_opens_with_it()
    {
        foreach (var e in K.Events.Concat(V.Events))
        {
            var rows = StoryEventModel.Rows(e, "X");
            foreach (var o in e.Openings)
            {
                Assert.Equal(o.Line + "\n\n" + e.Body, rows[$"X.pages.INITIAL_{o.Key}.description"]);
            }
            foreach (var o in e.Options)
            {
                Assert.Equal(o.Result, rows[$"X.pages.{o.Key}.description"]);
            }
        }
        var entries = StoryLoc.EventRows();
        foreach (var e in K.Events.Concat(V.Events))
        {
            Assert.Equal(e.Title, entries[StoryRegistry.EntryOf(e.EventType) + ".title"]);
        }
    }

    // ---- Locks ------------------------------------------------------------------

    private static StoryDeckView Deck(int gold = 999, int removable = 10, int transformable = 10,
        int curses = 1, int bombs = 5) => new(gold, removable, transformable, curses, bombs);

    private static bool Locked(Type evt, string key, StoryDeckView deck) =>
        StoryRules.IsLocked(E(evt).Options.Single(o => o.Key == key), deck);

    [Fact]
    public void A_Gold_price_above_your_Gold_is_locked()
    {
        Assert.True(Locked(typeof(KleeAlicesCache), "LEAVE_IT", Deck(gold: 49)));
        Assert.False(Locked(typeof(KleeAlicesCache), "LEAVE_IT", Deck(gold: 50)));
        Assert.True(Locked(typeof(KleeDodocoGoesMissing), "LEAVE_MORA_AS_BAIT", Deck(gold: 0)));
        Assert.True(Locked(typeof(VarkaSecondSatchel), "HAND_TO_THE_COURIER", Deck(gold: 74)));
        Assert.True(Locked(typeof(VarkaRearguard), "LEAVE_SUPPLIES", Deck(gold: 74)));
        Assert.False(Locked(typeof(VarkaRearguard), "LEAVE_SUPPLIES", Deck(gold: 75)));
        // The free way out never locks.
        Assert.False(Locked(typeof(KleeAlicesCache), "BACK_AWAY", Deck(gold: 0, removable: 0, transformable: 0, curses: 0, bombs: 0)));
    }

    [Fact]
    public void Remove_every_Curse_locks_with_no_Curse_or_short_of_25_each()
    {
        Assert.True(Locked(typeof(VarkaActingGrandMaster), "PROMISE_A_FULL_REPORT", Deck(curses: 0)));
        Assert.False(Locked(typeof(VarkaActingGrandMaster), "PROMISE_A_FULL_REPORT", Deck(gold: 50, curses: 2)));
        Assert.True(Locked(typeof(VarkaActingGrandMaster), "PROMISE_A_FULL_REPORT", Deck(gold: 49, curses: 2)));
    }

    [Fact]
    public void Remove_or_Transform_with_no_eligible_card_is_locked()
    {
        Assert.True(Locked(typeof(KleeDodocoGoesMissing), "LEAVE_MORA_AS_BAIT", Deck(removable: 0)));
        Assert.True(Locked(typeof(KleeStarsnatchCliff), "LEAVE_THEM_BE", Deck(removable: 0)));
        Assert.True(Locked(typeof(KleeFoundYou), "SWAP_HER_BEST_BOMB", Deck(transformable: 0)));
        Assert.False(Locked(typeof(KleeFoundYou), "SWAP_HER_BEST_BOMB", Deck(transformable: 1)));
        Assert.True(Locked(typeof(KleeAlicesCache), "LEAVE_IT", Deck(transformable: 0)));
        // Fewer than two: the game transforms those there are.
        Assert.False(Locked(typeof(KleeAlicesCache), "LEAVE_IT", Deck(transformable: 1)));
    }

    [Fact]
    public void Upgrade_N_Bomb_cards_upgrades_those_there_are_and_locks_with_none()
    {
        Assert.True(Locked(typeof(KleeMomsLastNote), "FOLD_INTO_A_FUSE", Deck(bombs: 0)));
        Assert.False(Locked(typeof(KleeMomsLastNote), "FOLD_INTO_A_FUSE", Deck(bombs: 1)));
        Assert.True(Locked(typeof(KleeLetterFromJean), "PAPER_BOMB", Deck(bombs: 0)));
    }

    [Fact]
    public void Remove_every_Overdue_Reports_or_Doubt_with_none_is_not_a_lock()
    {
        var empty = Deck(gold: 0, removable: 0, transformable: 0, curses: 0, bombs: 0);
        Assert.False(Locked(typeof(VarkaSecondSatchel), "SIGN_BY_LAMPLIGHT", empty));
        foreach (var o in E(typeof(KleeFoundYou)).Options.Where(o => o.Key != "SWAP_HER_BEST_BOMB"))
        {
            Assert.False(StoryRules.IsLocked(o, empty));
        }
        // The lock is the base game's: an option with no action, keyed _LOCKED.
        var methods = typeof(StoryEventModel).GetNestedTypes(HeadlessGame.All)
            .SelectMany(t => t.GetMethods(HeadlessGame.All))
            .Append(Il.Method(nameof(StoryEventModel), "GenerateInitialOptions"))
            .Where(m => m.GetMethodBody() != null);
        Assert.Contains(methods, m => Il.Strings(m).Contains("_LOCKED"));
    }

    // ---- The saved story -------------------------------------------------------

    private static string Choice(Type evt, string key) =>
        $"{StoryRegistry.EntryOf(evt)}.pages.INITIAL.options.{key}.title";

    [Fact]
    public void The_saved_story_is_read_from_visited_events_and_chosen_options()
    {
        var visited = new HashSet<Type> { typeof(KleeMomsMarks), typeof(KleeAlicesCache) };
        var keys = new[]
        {
            "NEOW.pages.INITIAL.options.SOMETHING.title",
            Choice(typeof(KleeMomsMarks), "ADD_A_MARK"),
            null,
            Choice(typeof(KleeAlicesCache), "SAVE_IT"),
            Choice(typeof(VarkaRearguard), "TAKE_THE_REAR"), // another character's: ignored
        };
        var records = StoryRules.Records(K, visited.Contains, keys, StoryRegistry.EntryOf);
        Assert.Equal(2, records.Count);
        Assert.Contains(new StoryRecord(0, typeof(KleeMomsMarks), "ADD_A_MARK"), records);
        Assert.Contains(new StoryRecord(1, typeof(KleeAlicesCache), "SAVE_IT"), records);
        Assert.Equal(typeof(KleeMomsLastNote), StoryRules.Route(K, 2, records, 7UL)!.EventType);
        Assert.Equal("SAVED", StoryRules.OpeningFor(E(typeof(KleeMomsLastNote)), records)!.Key);

        // Visited with no choice yet (saved mid-event): fired, option unknown.
        var open = StoryRules.Records(K, t => t == typeof(KleeMomsMarks), Array.Empty<string?>(), StoryRegistry.EntryOf);
        Assert.Equal(new StoryRecord(0, typeof(KleeMomsMarks), null), Assert.Single(open));
        Assert.Null(StoryRules.Route(K, 0, open, 7UL));
    }

    [Fact]
    public void The_saved_story_survives_the_games_own_save_and_reload()
    {
        // The routing state is the run history the game already saves: a
        // player's event choices on each map point, serialized with the run.
        // Round-trip one through the game's own JSON context and read the
        // story back.
        var before = new MapPointHistoryEntry();
        before.PlayerStats.Add(new PlayerMapPointHistoryEntry
        {
            PlayerId = 42,
            EventChoices = new List<EventOptionHistoryEntry>
            {
                new() { Title = new LocString("events", Choice(typeof(VarkaRearguard), "LEAVE_SUPPLIES")) },
            },
        });
        // The game's source-generated context is internal; reach its
        // MapPointHistoryEntry type info the way the save code does.
        var context = typeof(MapPointHistoryEntry).Assembly.GetType("MegaCrit.Sts2.Core.Saves.MegaCritSerializerContext")!;
        var defaultContext = context.GetProperty("Default", HeadlessGame.All)!.GetValue(null)!;
        var info = (JsonTypeInfo<MapPointHistoryEntry>)context
            .GetProperty("MapPointHistoryEntry", HeadlessGame.All)!.GetValue(defaultContext)!;
        var json = JsonSerializer.Serialize(before, info);
        Assert.Contains("LEAVE_SUPPLIES", json);
        var after = JsonSerializer.Deserialize(json, info)!;

        var history = new[] { new[] { after } };
        var keys = StoryHistory.ChoiceKeys(history, 42).ToList();
        Assert.Equal(new[] { Choice(typeof(VarkaRearguard), "LEAVE_SUPPLIES") }, keys);
        Assert.Empty(StoryHistory.ChoiceKeys(history, 7));

        var records = StoryRules.Records(V, t => t == typeof(VarkaRearguard), keys, StoryRegistry.EntryOf);
        Assert.Equal(typeof(VarkaWolfOfTheNorth), StoryRules.Route(V, 1, records, 7UL)!.EventType);
        Assert.Equal("SUPPLIES", StoryRules.OpeningFor(E(typeof(VarkaLongWayHome)), records)!.Key);

        // Structural: the live substitution reads that history for each player.
        var patch = typeof(StoryEventModel).Assembly.GetTypes()
            .Single(t => t.Name == "Hook_ModifyNextEvent_Story_Patch");
        Assert.Contains("StoryHistory.RecordsFor", Il.Calls(patch.GetMethod("Postfix", HeadlessGame.All)!));
        Assert.Contains("StoryRules.Records",
            Il.Calls(typeof(StoryHistory).GetMethod(nameof(StoryHistory.RecordsFor))!));
    }

    // ---- Helpers ---------------------------------------------------------------

    private static string Title(BaseLib.Abstracts.CustomCardModel card) =>
        card.Localization!.Single(r => r.Item1 == "title").Item2;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "review")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName ?? throw new InvalidOperationException("repo root not found");
    }
}
