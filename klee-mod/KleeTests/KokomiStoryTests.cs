using System;
using System.Collections.Generic;
using System.IO;
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
/// KOKOMI'S STORY IN THE RUN (<c>review/active/kokomi-story-2026-10-16.md</c>,
/// ruled 2026-10-16: "I reviewed it myself and I still think it looks a bit
/// stilted at parts, but nothing that blocks it from a beta launch. ...
/// Approved!", picks 1 (a) and 2 (a); pick 3 (a), her lines: "Ok, I'm good
/// to approve the full Kokomi paper as-is. The dialogue looks good!").
///
/// The same headless boundary as <see cref="FurinaStoryTests"/>: every string
/// is held against the paper, every routing decision runs through the pure
/// function the game calls, and Public Address is a story Curse on the shared
/// clock.
/// </summary>
public class KokomiStoryTests
{
    private static readonly CharacterStory K = KokomiStory.Table;
    private static readonly Type KokomiType = typeof(global::KleeMod.Kokomi);

    private static string Paper() => File.ReadAllText(Path.Combine(
        RepoRoot(), "review", "active", "kokomi-story-2026-10-16.md")).Replace("\r\n", "\n");

    /// <summary>The paper with its prose line breaks joined.</summary>
    private static string Flat() => Paper().Replace("\n", " ");

    private static string ToPaper(string s) => s
        .Replace("[i]", "*").Replace("[/i]", "*")
        .Replace("[gold]", "**").Replace("[/gold]", "**");

    private static StoryEvent E(Type t) => K.Events.Single(e => e.EventType == t);

    private static readonly IReadOnlyList<StoryRecord> None = Array.Empty<StoryRecord>();

    private static StoryRecord R(int act, Type t, string? option = null) => new(act, t, option);

    // ---- The words are the paper's --------------------------------------------

    [Fact]
    public void She_has_a_table_in_the_registry()
    {
        Assert.Same(K, StoryRegistry.For(KokomiType));
        Assert.Contains(K, StoryRegistry.All);
    }

    [Fact]
    public void Eight_events_in_three_threads()
    {
        Assert.Equal(8, K.Events.Count);
        Assert.Equal(8, K.Events.Select(e => e.EventType).Distinct().Count());
        Assert.Equal(new[] { 0, 0, 0, 1, 1, 1, 2, 2 }, K.Events.Select(e => e.ActIndex));
        var paper = Paper();
        foreach (var e in K.Events) Assert.Contains($"**Act {e.ActIndex + 1}. {e.Title}**", paper);
    }

    [Fact]
    public void Every_event_is_the_papers_page_options_and_results()
    {
        var paper = Paper();
        var flat = Flat();
        foreach (var e in K.Events)
        {
            // Every page is set in italics in the paper, as page text.
            Assert.Contains($"*{ToPaper(e.Body)}*", flat);
            Assert.Equal(e.EventType == typeof(KokomiCoralLight) ? 4 : 3, e.Options.Count);
            foreach (var o in e.Options)
            {
                // The effect cell may go on with the paper's own note
                // ("Locked under 50 Gold."), which is the rule, not player text.
                Assert.Contains($"| {o.Title} | {ToPaper(o.Description).TrimEnd('.')}", paper);
                Assert.Contains($" | {ToPaper(o.Result!)} |", paper);
            }
        }
    }

    [Fact]
    public void Every_opening_line_is_the_papers()
    {
        var flat = Flat();
        var count = 0;
        foreach (var e in K.Events)
        {
            foreach (var o in e.Openings)
            {
                Assert.Contains("\"" + o.Line + "\"", flat);
                count++;
            }
        }
        // Three each for the commander, the bones and the endgame; one for
        // Gorou's report; three for the tide.
        Assert.Equal(13, count);
    }

    [Fact]
    public void The_options_do_what_the_tables_say()
    {
        Steps(typeof(KokomiSandTable), 0, (StoryEffectKind.LoseHp, 7, null), (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(KokomiSandTable), 1, (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(KokomiSandTable), 2, (StoryEffectKind.GainRandomPotions, 1, null));
        Steps(typeof(KokomiCoralLight), 0, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.GainRandomRelic, 0, null));
        Steps(typeof(KokomiCoralLight), 1, (StoryEffectKind.LoseHp, 6, null), (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(KokomiCoralLight), 2, (StoryEffectKind.LoseGold, 50, null), (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(KokomiCoralLight), 3, (StoryEffectKind.Nothing, 0, null));
        Steps(typeof(KokomiEmptyRoom), 0, (StoryEffectKind.Heal, 15, null));
        Steps(typeof(KokomiEmptyRoom), 1, (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKkTreatise)));
        Steps(typeof(KokomiEmptyRoom), 2, (StoryEffectKind.GainRandomPotions, 1, null));
        Steps(typeof(KokomiOtherCommander), 0, (StoryEffectKind.LoseHp, 12, null), (StoryEffectKind.GainRandomRelic, 0, null));
        Steps(typeof(KokomiOtherCommander), 1, (StoryEffectKind.TransformCards, 1, null));
        Steps(typeof(KokomiOtherCommander), 2, (StoryEffectKind.AddCard, 0, typeof(Doubt)), (StoryEffectKind.ChooseRareCardToDeck, 3, null));
        Steps(typeof(KokomiSerpentsBones), 0, (StoryEffectKind.LoseMaxHp, 4, null), (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(KokomiSerpentsBones), 1, (StoryEffectKind.GainGold, 100, null), (StoryEffectKind.AddCard, 0, typeof(Doubt)));
        Steps(typeof(KokomiSerpentsBones), 2, (StoryEffectKind.RemoveCard, 0, null), (StoryEffectKind.AddCard, 0, typeof(PublicAddress)));
        Steps(typeof(KokomiReportFromGorou), 0, (StoryEffectKind.ChooseFromPoolToDeck, 3, null));
        Steps(typeof(KokomiReportFromGorou), 1, (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(KokomiReportFromGorou), 2, (StoryEffectKind.Heal, 20, null));
        Steps(typeof(KokomiEndgame), 0, (StoryEffectKind.LoseHp, 15, null), (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(KokomiEndgame), 1, (StoryEffectKind.LoseGold, 50, null), (StoryEffectKind.TransformCards, 2, null));
        Steps(typeof(KokomiEndgame), 2, (StoryEffectKind.Nothing, 0, null));
        Steps(typeof(KokomiTideComesIn), 0, (StoryEffectKind.LoseHp, 6, null), (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKkKurageCanopy)));
        Steps(typeof(KokomiTideComesIn), 1, (StoryEffectKind.Heal, 20, null));
        Steps(typeof(KokomiTideComesIn), 2, (StoryEffectKind.RemoveCard, 0, null));

        // The cards are the paper's, under their own names.
        Assert.Equal("Treatise", Title(new ProtoKkTreatise()));
        Assert.Equal("Kurage Canopy", Title(new ProtoKkKurageCanopy()));
        Assert.Equal(4, E(typeof(KokomiSerpentsBones)).Options[0].Effects[0].Amount);
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

    private static bool Priced(StoryOption o) => o.Effects.Any(s =>
        s.Kind is StoryEffectKind.LoseHp or StoryEffectKind.LoseGold or StoryEffectKind.LoseMaxHp
        || (s.Kind == StoryEffectKind.AddCard && (s.Card == typeof(PublicAddress) || s.Card == typeof(Doubt))));

    [Fact]
    public void The_paper_ratio_holds_two_free_five_with_a_way_out_one_all_priced()
    {
        var allFree = K.Events.Where(e => e.Options.All(o => !Priced(o))).Select(e => e.EventType).ToList();
        var allPriced = K.Events.Where(e => e.Options.All(Priced)).Select(e => e.EventType).ToList();
        Assert.Equal(new[] { typeof(KokomiEmptyRoom), typeof(KokomiReportFromGorou) }, allFree);
        Assert.Equal(new[] { typeof(KokomiSerpentsBones) }, allPriced);
        Assert.Contains("| These eight | 2 (25%) | 5 (63%) | 1 (13%) |", Paper());
    }

    [Fact]
    public void Promise_him_a_rite_removes_before_it_adds_the_curse()
    {
        // The removal screen opens on the deck as it was, so the new
        // Public Address cannot remove itself; the text reads in that order.
        var o = E(typeof(KokomiSerpentsBones)).Options.Single(x => x.Key == "PROMISE_A_RITE");
        Assert.Equal(StoryEffectKind.RemoveCard, o.Effects[0].Kind);
        Assert.Equal(StoryEffectKind.AddCard, o.Effects[1].Kind);
        Assert.Equal(typeof(PublicAddress), o.Effects[1].Card);
        Assert.Equal("Remove a card. Add [gold]Public Address[/gold].", o.Description);
    }

    [Fact]
    public void A_Max_HP_cost_carries_the_games_lethal_warning()
    {
        // Lay a hand on it costs 4 Max HP: the option flashes red, the base
        // game's way (Vakuu's ThatDecreasesMaxHp), when it would kill.
        var bones = E(typeof(KokomiSerpentsBones));
        Assert.Equal(4, bones.Options[0].MaxHpCost);
        Assert.Equal(0, bones.Options[1].MaxHpCost);
        Assert.Equal(0, bones.Options[2].MaxHpCost);
        // STRUCTURAL: the option builder (a closure in GenerateInitialOptions)
        // calls the game's own warnings.
        const System.Reflection.BindingFlags All = System.Reflection.BindingFlags.Public
            | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance
            | System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.DeclaredOnly;
        var calls = typeof(StoryEventModel).GetNestedTypes(All)
            .SelectMany(t => t.GetMethods(All))
            .Concat(typeof(StoryEventModel).GetMethods(All))
            .SelectMany(m => Il.Calls(m))
            .ToList();
        Assert.Contains("EventOption.ThatDecreasesMaxHp", calls);
        Assert.Contains("EventOption.ThatDoesDamage", calls);
    }

    [Fact]
    public void No_event_forces_a_lethal_choice()
    {
        // "Every event has an option that costs no HP and needs no Gold",
        // except The Serpent's Bones, whose prices are Max HP, Doubt and the
        // curse: none of them can kill.
        foreach (var e in K.Events)
        {
            Assert.Contains(e.Options, o => o.HpCost == 0
                && o.Effects.All(s => s.Kind != StoryEffectKind.LoseGold));
        }
    }

    [Fact]
    public void Gorous_four_are_the_choice_pool_in_her_pool_order()
    {
        Assert.NotNull(K.ChoicePool);
        Assert.Equal(typeof(KokomiStory), K.ChoicePool!.Method.DeclaringType);
        Assert.Equal(nameof(KokomiStory.GorouCards), K.ChoicePool.Method.Name);
        var calls = Il.CallSequence(Il.Method(nameof(KokomiStory), nameof(KokomiStory.GorouCards)));
        Assert.Equal(4, calls.Count(c => c.Contains("ModelDb.Card")));
    }

    [Fact]
    public void The_Rare_choice_draws_from_her_offer()
    {
        Assert.Contains("CardPoolModel.GetUnlockedCards",
            Il.Calls(Il.Method(nameof(StoryEventModel), "RareOffer")));
        Assert.Contains("StoryEventModel.RareOffer",
            Il.Calls(Il.Method(nameof(StoryEventModel), "Apply")));
        Assert.Contains("CreatureCmd.LoseMaxHp",
            Il.Calls(Il.Method(nameof(StoryEventModel), "Apply")));
    }

    // ---- Public Address: the story Curses' clock ------------------------------

    [Fact]
    public void Public_Address_is_an_unplayable_removable_story_Curse()
    {
        var curse = new PublicAddress();
        Assert.IsAssignableFrom<StoryCurse>(curse);
        Assert.Equal(CardType.Curse, curse.Type);
        Assert.Equal(CardRarity.Curse, curse.Rarity);
        Assert.Contains(CardKeyword.Unplayable, curse.CanonicalKeywords);
        Assert.True(StoryEventModel.IsRemovableCurse(curse));
        Assert.Equal(0, curse.MaxUpgradeLevel);
        var loc = curse.Localization!;
        Assert.Equal("Public Address", loc.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("She has promised a speech when she gets home.\nAfter 3 combats, remove this from your deck.",
            loc.Single(r => r.Item1 == "description").Item2);
        var flat = Flat();
        Assert.Contains("**Her story curse: Public Address.** It is Unplayable and leaves after 3 combats.", flat);
        Assert.Contains($"Its text: *\"{PublicAddress.Text}\"*", flat);
        // The other story Curses keep the clock's sentence alone.
        Assert.Equal("After 3 combats, remove this from your deck.",
            new StageFright().Localization!.Single(r => r.Item1 == "description").Item2);
    }

    [Fact]
    public void Only_the_promised_rite_gives_Public_Address()
    {
        var givers = K.Events.SelectMany(e => e.Options)
            .Where(o => o.Effects.Any(s => s.Card == typeof(PublicAddress)))
            .Select(o => o.Key).ToList();
        Assert.Equal(new[] { "PROMISE_A_RITE" }, givers);
    }

    // ---- The chain ------------------------------------------------------------

    [Fact]
    public void Act_1_draws_one_of_three_at_random_and_the_same_one_on_a_reload()
    {
        var act1 = K.Events.Where(e => e.ActIndex == 0).ToList();
        Assert.Equal(3, act1.Count);
        Assert.All(act1, e => Assert.Empty(e.Follows));
        var drawn = new HashSet<Type>();
        for (ulong seed = 0; seed < 200; seed++)
        {
            var e = StoryRules.Route(K, 0, None, seed)!;
            Assert.Same(e, StoryRules.Route(K, 0, None, seed));
            drawn.Add(e.EventType);
        }
        Assert.Equal(act1.Select(e => e.EventType).ToHashSet(), drawn);
    }

    [Theory]
    [InlineData(typeof(KokomiSandTable), typeof(KokomiOtherCommander))]
    [InlineData(typeof(KokomiCoralLight), typeof(KokomiSerpentsBones))]
    [InlineData(typeof(KokomiEmptyRoom), typeof(KokomiReportFromGorou))]
    public void The_act_1_event_picks_act_2s(Type act1, Type act2) =>
        Assert.Equal(act2, StoryRules.Route(K, 1, new[] { R(0, act1, "X") }, 7UL)!.EventType);

    [Theory]
    [InlineData(typeof(KokomiOtherCommander), typeof(KokomiEndgame))]
    [InlineData(typeof(KokomiSerpentsBones), typeof(KokomiTideComesIn))]
    [InlineData(typeof(KokomiReportFromGorou), typeof(KokomiTideComesIn))]
    public void The_act_2_event_picks_act_3s(Type act2, Type act3) =>
        Assert.Equal(act3, StoryRules.Route(K, 2, new[] { R(1, act2, "X") }, 7UL)!.EventType);

    [Fact]
    public void A_skipped_act_falls_back_to_the_home_thread()
    {
        Assert.Equal(typeof(KokomiReportFromGorou), StoryRules.Route(K, 1, None, 7UL)!.EventType);
        foreach (var t in new[] { typeof(KokomiSandTable), typeof(KokomiCoralLight), typeof(KokomiEmptyRoom) })
        {
            Assert.Equal(typeof(KokomiTideComesIn), StoryRules.Route(K, 2, new[] { R(0, t, "X") }, 7UL)!.EventType);
        }
        Assert.Equal(typeof(KokomiTideComesIn), StoryRules.Route(K, 2, None, 7UL)!.EventType);
        Assert.Equal(1, K.Events.Count(e => e.Home && e.ActIndex == 1));
        Assert.Equal(1, K.Events.Count(e => e.Home && e.ActIndex == 2));
    }

    [Fact]
    public void At_most_one_fires_per_act()
    {
        for (var act = 0; act < 3; act++)
        {
            var fired = K.Events.First(e => e.ActIndex == act);
            Assert.Null(StoryRules.Route(K, act, new[] { R(act, fired.EventType) }, 7UL));
        }
        Assert.Null(StoryRules.Route(K, 3, None, 7UL));
    }

    private static string? Opening(Type evt, params StoryRecord[] records) =>
        StoryRules.OpeningFor(E(evt), records)?.Key;

    [Fact]
    public void Later_events_open_with_the_line_that_matches_what_she_did()
    {
        var sand = typeof(KokomiSandTable);
        Assert.Equal("PLAYED", Opening(typeof(KokomiOtherCommander), R(0, sand, "PLAY_IT_OUT")));
        Assert.Equal("MOVED", Opening(typeof(KokomiOtherCommander), R(0, sand, "MOVE_HER_PIECE")));
        Assert.Equal("POCKETED", Opening(typeof(KokomiOtherCommander), R(0, sand, "POCKET_THE_GENERAL")));

        var coral = typeof(KokomiCoralLight);
        Assert.Equal("REACHED", Opening(typeof(KokomiSerpentsBones), R(0, coral, "REACH_IN")));
        Assert.Equal("PRAYED", Opening(typeof(KokomiSerpentsBones), R(0, coral, "SAY_THE_SEA_PRAYER")));
        Assert.Equal("PAID", Opening(typeof(KokomiSerpentsBones), R(0, coral, "LEAVE_A_PEARL")));
        // The paper gives the free way out no opening.
        Assert.Null(Opening(typeof(KokomiSerpentsBones), R(0, coral, "LEAVE_IT")));

        // "When it follows the room, it opens: Rested, she reads it twice."
        foreach (var o in E(typeof(KokomiEmptyRoom)).Options)
        {
            Assert.Equal("RESTED", Opening(typeof(KokomiReportFromGorou), R(0, typeof(KokomiEmptyRoom), o.Key)));
        }
        Assert.Null(Opening(typeof(KokomiReportFromGorou)));

        var commander = typeof(KokomiOtherCommander);
        Assert.Equal("PLAYED", Opening(typeof(KokomiEndgame), R(1, commander, "PLAY_THE_FULL_GAME")));
        Assert.Equal("DREW", Opening(typeof(KokomiEndgame), R(1, commander, "OFFER_A_DRAW")));
        Assert.Equal("CONCEDED", Opening(typeof(KokomiEndgame), R(1, commander, "CONCEDE")));

        // The tide: the bones (any choice), Gorou's reinforcements, otherwise.
        foreach (var o in E(typeof(KokomiSerpentsBones)).Options)
        {
            Assert.Equal("BONES", Opening(typeof(KokomiTideComesIn), R(1, typeof(KokomiSerpentsBones), o.Key)));
        }
        var gorou = typeof(KokomiReportFromGorou);
        Assert.Equal("REINFORCEMENTS", Opening(typeof(KokomiTideComesIn), R(1, gorou, "SEND_FOR_REINFORCEMENTS")));
        Assert.Equal("OTHERWISE", Opening(typeof(KokomiTideComesIn), R(1, gorou, "WRITE_BACK")));
        Assert.Equal("OTHERWISE", Opening(typeof(KokomiTideComesIn), R(1, gorou, "EAT_THE_SUSHI")));
        Assert.Equal("OTHERWISE", Opening(typeof(KokomiTideComesIn)));
    }

    [Fact]
    public void A_price_she_cannot_pay_is_locked()
    {
        var pearl = E(typeof(KokomiCoralLight)).Options[2];
        Assert.True(StoryRules.IsLocked(pearl, new StoryDeckView(49, 10, 10, 0, 0)));
        Assert.False(StoryRules.IsLocked(pearl, new StoryDeckView(50, 10, 10, 0, 0)));
        Assert.True(StoryRules.IsLocked(pearl, new StoryDeckView(99, 0, 10, 0, 0)));
        var stake = E(typeof(KokomiEndgame)).Options[1];
        Assert.True(StoryRules.IsLocked(stake, new StoryDeckView(49, 10, 10, 0, 0)));
        Assert.False(StoryRules.IsLocked(stake, new StoryDeckView(50, 10, 10, 0, 0)));
        Assert.True(StoryRules.IsLocked(stake, new StoryDeckView(99, 10, 0, 0, 0)));
        // The free ways out never lock.
        var broke = new StoryDeckView(0, 0, 0, 0, 0);
        Assert.False(StoryRules.IsLocked(E(typeof(KokomiCoralLight)).Options[3], broke));
        Assert.False(StoryRules.IsLocked(E(typeof(KokomiEndgame)).Options[2], broke));
    }

    [Fact]
    public void Only_Kokomi_takes_her_options()
    {
        foreach (var e in K.Events)
        {
            Assert.True(StoryRules.IsOwnersEvent(KokomiType, e.EventType));
            Assert.False(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Furina), e.EventType));
        }
    }

    [Fact]
    public void Every_option_and_page_has_its_loc_row()
    {
        var rows = StoryLoc.EventRows();
        foreach (var e in K.Events)
        {
            var entry = StoryRegistry.EntryOf(e.EventType);
            Assert.Equal(e.Title, rows[entry + ".title"]);
            Assert.Equal(e.Body, rows[entry + ".pages.INITIAL.description"]);
            foreach (var o in e.Options)
            {
                Assert.Equal(o.Title, rows[StoryEventModel.OptionTitleKey(entry, o)]);
                Assert.Equal(o.Description, rows[StoryEventModel.OptionDescriptionKey(entry, o)]);
                Assert.Equal(o.Result, rows[StoryEventModel.ResultKey(entry, o)]);
            }
            foreach (var o in e.Openings)
            {
                Assert.Equal(StoryEventModel.OpeningPage(e, o), rows[StoryEventModel.OpeningKey(entry, o)]);
            }
        }
    }

    // ---- Her lines (pick 3 (a)) ---------------------------------------------

    [Fact]
    public void Her_lines_are_the_papers_word_for_word()
    {
        var flat = Flat();
        Assert.Equal("The Pearl of Wisdom.", K.IntroTitle);
        Assert.Contains(K.IntroLine, flat);
        var description = new global::KleeMod.Kokomi().Localization!.Single(r => r.Item1 == "description").Item2;
        Assert.Equal(K.Intro, description);

        Assert.Equal(
            new[] { "NEOW", "OROBAS", "PAEL", "TEZCATARA", "NONUPEIPE", "TANX", "VAKUU", "DARV" },
            K.Ancients.Select(a => a.AncientEntry));
        foreach (var a in K.Ancients)
        {
            Assert.Contains(a.AncientLine, flat);
            Assert.Contains(a.CharacterLine, flat);
            Assert.Equal(a.Ancient.ToUpperInvariant(), a.AncientEntry);
        }

        var l = K.Lines!;
        foreach (var line in new[] { l.BossEntry, l.LowHp, l.Signature, l.BossKill, l.RunLoss, l.RunWin })
        {
            Assert.Contains(line, flat);
        }
        Assert.Single(K.SignatureCards);
        Assert.Empty(K.Pairs);
    }

    [Fact]
    public void Who_speaks_at_a_boss_with_her_at_the_table()
    {
        // Alone, or with a character who has no pair with her: her own line.
        foreach (var seats in new[] { new[] { KokomiType }, new[] { KokomiType, typeof(global::KleeMod.Yae) } })
        {
            var s = Assert.Single(StoryRules.BossEntryPlan(seats));
            Assert.Same(K, s.Story);
            Assert.Null(s.Pair);
        }
        // Klee's, Varka's and Furina's pairs with her stay in their tables.
        foreach (var other in new[] { typeof(global::KleeMod.Klee), typeof(global::KleeMod.Varka), typeof(global::KleeMod.Furina) })
        {
            foreach (var seats in new[] { new[] { KokomiType, other }, new[] { other, KokomiType } })
            {
                var s = Assert.Single(StoryRules.BossEntryPlan(seats));
                Assert.Same(StoryRegistry.For(other), s.Story);
                Assert.Equal(KokomiType, s.Pair!.Partner);
            }
        }
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
