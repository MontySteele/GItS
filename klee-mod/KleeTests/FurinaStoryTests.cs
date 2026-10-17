using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Ancients;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;
using Doubt = MegaCrit.Sts2.Core.Models.Cards.Doubt;

namespace KleeMod.Tests;

/// <summary>
/// FURINA'S STORY IN THE RUN (<c>review/active/furina-story-2026-10-15.md</c>,
/// ruled 2026-10-15: "I like the Furina event PR! Approved!", all three picks
/// (a)).
///
/// The same headless boundary as <see cref="VarkaStoryTests"/> and
/// <see cref="StoryChainTests"/>: every string is held against the paper,
/// every routing decision runs through the pure function the game calls, and
/// Stage Fright is a story Curse on the shared clock.
/// </summary>
public class FurinaStoryTests
{
    private static readonly CharacterStory F = FurinaStory.Table;
    private static readonly Type FurinaType = typeof(global::KleeMod.Furina);

    private static string Paper() => File.ReadAllText(Path.Combine(
        RepoRoot(), "review", "active", "furina-story-2026-10-15.md")).Replace("\r\n", "\n");

    /// <summary>The paper with its prose line breaks joined.</summary>
    private static string Flat() => Paper().Replace("\n", " ");

    private static string ToPaper(string s) => s
        .Replace("[i]", "*").Replace("[/i]", "*")
        .Replace("[gold]", "**").Replace("[/gold]", "**");

    private static StoryEvent E(Type t) => F.Events.Single(e => e.EventType == t);

    private static readonly IReadOnlyList<StoryRecord> None = Array.Empty<StoryRecord>();

    private static StoryRecord R(int act, Type t, string? option = null) => new(act, t, option);

    // ---- The words are the paper's --------------------------------------------

    [Fact]
    public void She_has_a_table_in_the_registry()
    {
        Assert.Same(F, StoryRegistry.For(FurinaType));
        Assert.Contains(F, StoryRegistry.All);
    }

    [Fact]
    public void The_intro_is_the_papers_select_line()
    {
        Assert.Contains($"*{F.IntroTitle}* \"{F.IntroLine}\"", Flat());
        var intro = new global::KleeMod.Furina().Localization!.Single(r => r.Item1 == "description");
        Assert.Equal(F.Intro, intro.Item2);
    }

    [Fact]
    public void Every_Ancient_exchange_is_the_papers_word_for_word()
    {
        var paper = Paper();
        Assert.Equal(
            new[] { "NEOW", "OROBAS", "PAEL", "TEZCATARA", "NONUPEIPE", "TANX", "VAKUU", "DARV" },
            F.Ancients.Select(a => a.AncientEntry));
        foreach (var a in F.Ancients)
        {
            Assert.Contains($"| {a.Ancient} | {a.AncientLine} | {a.CharacterLine} |", paper);
            Assert.Equal(a.Ancient.ToUpperInvariant(), a.AncientEntry);
        }
    }

    [Fact]
    public void Every_combat_line_is_the_papers_word_for_word()
    {
        var flat = Flat();
        var l = F.Lines;
        Assert.Contains($"boss entry \"{l.BossEntry}\"", flat);
        Assert.Contains($"Low HP \"{l.LowHp}\"", flat);
        Assert.Contains($"(signature) \"{l.Signature}\"", flat);
        Assert.Contains($"Boss kill \"{l.BossKill}\"", flat);
        Assert.Contains($"Run loss \"{l.RunLoss}\"", flat);
        Assert.Contains($"Run win \"{l.RunWin}\"", flat);
    }

    [Fact]
    public void Every_pair_exchange_is_the_papers_in_the_papers_order()
    {
        var flat = Flat();
        Assert.Equal(new[] { typeof(Kokomi), typeof(Yae) }, F.Pairs.Select(p => p.Partner));
        var kokomi = F.Pairs[0];
        Assert.True(kokomi.OwnFirst);
        Assert.Contains(
            $"with Kokomi, Furina: \"{kokomi.OwnLine}\" Kokomi: \"{kokomi.PartnerLine}\"", flat);
        var yae = F.Pairs[1];
        Assert.False(yae.OwnFirst);
        Assert.Contains($"With Yae, Yae: \"{yae.PartnerLine}\" Furina: \"{yae.OwnLine}\"", flat);
        foreach (var p in F.Pairs) Assert.Equal(p.Partner.Name, p.PartnerName);
    }

    [Fact]
    public void Eight_events_in_three_threads()
    {
        Assert.Equal(8, F.Events.Count);
        Assert.Equal(8, F.Events.Select(e => e.EventType).Distinct().Count());
        Assert.Equal(new[] { 0, 0, 0, 1, 1, 1, 2, 2 }, F.Events.Select(e => e.ActIndex));
        var paper = Paper();
        foreach (var e in F.Events) Assert.Contains($"**Act {e.ActIndex + 1}. {e.Title}**", paper);
    }

    [Fact]
    public void Every_event_is_the_papers_page_options_and_results()
    {
        var paper = Paper();
        var flat = Flat();
        foreach (var e in F.Events)
        {
            // Act 1's pages are set in italics as page text; the later ones
            // follow "*Body:*".
            Assert.Contains(e.ActIndex == 0 ? $"*{ToPaper(e.Body)}*" : $"*Body:* {ToPaper(e.Body)}", flat);
            Assert.Equal(3, e.Options.Count);
            foreach (var o in e.Options)
            {
                // The effect cell may go on with the paper's own note ("*(a
                // jackpot)*", "Locked with ..."), which is the rule, not
                // player text.
                Assert.Contains($"| {o.Title} | {ToPaper(o.Description).TrimEnd('.')}", paper);
                Assert.Contains($" | {o.Result} |", paper);
            }
        }
    }

    [Fact]
    public void Every_opening_line_is_the_papers()
    {
        var flat = Flat();
        foreach (var e in F.Events)
        {
            foreach (var o in e.Openings)
            {
                var inPaper = "\"" + o.Line.Replace('"', '\'') + "\"";
                Assert.Contains(inPaper, flat);
            }
        }
    }

    [Fact]
    public void The_options_do_what_the_tables_say()
    {
        Steps(typeof(FurinaEmptyHouse), 0, (StoryEffectKind.LoseHp, 8, null), (StoryEffectKind.UpgradeRandomCards, 2, null));
        Steps(typeof(FurinaEmptyHouse), 1, (StoryEffectKind.Heal, 10, null));
        Steps(typeof(FurinaEmptyHouse), 2, (StoryEffectKind.GainRandomRelic, 0, null), (StoryEffectKind.AddCard, 0, typeof(StageFright)));
        Steps(typeof(FurinaRisingWater), 0, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.RemoveCard, 0, null));
        Steps(typeof(FurinaRisingWater), 1, (StoryEffectKind.AddCard, 0, typeof(Doubt)), (StoryEffectKind.UpgradeRandomCards, 3, null));
        Steps(typeof(FurinaRisingWater), 2, (StoryEffectKind.GainGold, 75, null), (StoryEffectKind.AddCard, 0, typeof(StageFright)));
        Steps(typeof(FurinaSteambirdClipping), 0, (StoryEffectKind.Heal, 12, null));
        Steps(typeof(FurinaSteambirdClipping), 1, (StoryEffectKind.ChooseFromPoolToDeck, 3, null));
        Steps(typeof(FurinaSteambirdClipping), 2, (StoryEffectKind.GainRandomPotions, 1, null));
        Steps(typeof(FurinaUnderstudy), 0, (StoryEffectKind.LoseHp, 6, null), (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoFsUnderstudysDebut)));
        Steps(typeof(FurinaUnderstudy), 1, (StoryEffectKind.RemoveCard, 0, null), (StoryEffectKind.AddCard, 0, typeof(StageFright)));
        Steps(typeof(FurinaUnderstudy), 2, (StoryEffectKind.GainGold, 50, null));
        Steps(typeof(FurinaOratricesEcho), 0, (StoryEffectKind.LoseHp, 12, null), (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(FurinaOratricesEcho), 1, (StoryEffectKind.Heal, 15, null), (StoryEffectKind.AddCard, 0, typeof(StageFright)));
        Steps(typeof(FurinaOratricesEcho), 2, (StoryEffectKind.LoseGold, 50, null), (StoryEffectKind.TransformCards, 2, null));
        Steps(typeof(FurinaLetterFromTheCourt), 0, (StoryEffectKind.UpgradeChosenCard, 0, null));
        Steps(typeof(FurinaLetterFromTheCourt), 1, (StoryEffectKind.LoseGold, 40, null), (StoryEffectKind.Heal, 25, null));
        Steps(typeof(FurinaLetterFromTheCourt), 2, (StoryEffectKind.AddCard, 0, typeof(ProtoFsTearfulMonologue)));
        Steps(typeof(FurinaCurtainCall), 0, (StoryEffectKind.LoseHp, 10, null), (StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoFsLetThePeopleRejoice)));
        Steps(typeof(FurinaCurtainCall), 1, (StoryEffectKind.Heal, 30, null));
        Steps(typeof(FurinaCurtainCall), 2, (StoryEffectKind.UpgradeRandomCards, 3, null), (StoryEffectKind.AddCard, 0, typeof(StageFright)));
        Steps(typeof(FurinaEmptyThrone), 0, (StoryEffectKind.LoseHp, 15, null), (StoryEffectKind.GainRandomRareRelic, 0, null));
        Steps(typeof(FurinaEmptyThrone), 1, (StoryEffectKind.Heal, 20, null));
        Steps(typeof(FurinaEmptyThrone), 2, (StoryEffectKind.LoseHp, 8, null), (StoryEffectKind.RemoveCard, 0, null), (StoryEffectKind.RemoveEvery, 0, typeof(Doubt)));

        // The cards are the paper's, under their own names.
        Assert.Equal("Understudy's Debut", Title(new ProtoFsUnderstudysDebut()));
        Assert.Equal("Let the People Rejoice", Title(new ProtoFsLetThePeopleRejoice()));
        Assert.Equal("Tearful Monologue", Title(new ProtoFsTearfulMonologue()));
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
    public void The_paper_ratio_holds_one_free_five_with_a_way_out_two_all_priced()
    {
        // Free: no HP, Gold or curse cost. A curse or Doubt is a price.
        static bool Priced(StoryOption o) => o.Effects.Any(s =>
            s.Kind is StoryEffectKind.LoseHp or StoryEffectKind.LoseGold
            || (s.Kind == StoryEffectKind.AddCard && (s.Card == typeof(StageFright) || s.Card == typeof(Doubt))));
        var allFree = F.Events.Where(e => e.Options.All(o => !Priced(o))).Select(e => e.EventType).ToList();
        var allPriced = F.Events.Where(e => e.Options.All(Priced)).Select(e => e.EventType).ToList();
        Assert.Equal(new[] { typeof(FurinaSteambirdClipping) }, allFree);
        Assert.Equal(new[] { typeof(FurinaRisingWater), typeof(FurinaOratricesEcho) }, allPriced);
    }

    [Fact]
    public void Guest_Stars_are_the_choice_pool_eleven_in_her_pool_order()
    {
        Assert.NotNull(F.ChoicePool);
        Assert.Equal(typeof(FurinaCards), F.ChoicePool!.Method.DeclaringType);
        Assert.Equal(nameof(FurinaCards.GuestStars), F.ChoicePool.Method.Name);
        var calls = Il.CallSequence(Il.Method(nameof(FurinaCards), nameof(FurinaCards.GuestStars)));
        Assert.Equal(11, calls.Count(c => c.Contains("ModelDb.Card")));
    }

    [Fact]
    public void Let_the_People_Rejoice_is_her_signature_once_a_combat()
    {
        Assert.True(StoryRules.IsSignaturePlay(F, typeof(ProtoFsLetThePeopleRejoice)));
        Assert.False(StoryRules.IsSignaturePlay(F, typeof(ProtoFsStandingOvation)));
        Assert.Single(F.SignatureCards);
    }

    // ---- Stage Fright: the story Curses' clock ---------------------------------

    [Fact]
    public void Stage_Fright_is_an_unplayable_removable_story_Curse()
    {
        var curse = new StageFright();
        Assert.IsAssignableFrom<StoryCurse>(curse);
        Assert.Equal(CardType.Curse, curse.Type);
        Assert.Equal(CardRarity.Curse, curse.Rarity);
        Assert.Contains(CardKeyword.Unplayable, curse.CanonicalKeywords);
        Assert.True(StoryEventModel.IsRemovableCurse(curse));
        Assert.Equal(0, curse.MaxUpgradeLevel);
        var loc = curse.Localization!;
        Assert.Equal("Stage Fright", loc.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("After 3 combats, remove this from your deck.", loc.Single(r => r.Item1 == "description").Item2);
        Assert.Contains("**Her story curse: Stage Fright.** Unplayable; removed after 3 combats", Flat());
    }

    // ---- The chain ------------------------------------------------------------

    [Fact]
    public void Act_1_draws_one_of_three_at_random_and_the_same_one_on_a_reload()
    {
        var act1 = F.Events.Where(e => e.ActIndex == 0).ToList();
        Assert.Equal(3, act1.Count);
        Assert.All(act1, e => Assert.Empty(e.Follows));
        var drawn = new HashSet<Type>();
        for (ulong seed = 0; seed < 200; seed++)
        {
            var e = StoryRules.Route(F, 0, None, seed)!;
            Assert.Same(e, StoryRules.Route(F, 0, None, seed));
            drawn.Add(e.EventType);
        }
        Assert.Equal(act1.Select(e => e.EventType).ToHashSet(), drawn);
    }

    [Theory]
    [InlineData(typeof(FurinaEmptyHouse), typeof(FurinaUnderstudy))]
    [InlineData(typeof(FurinaRisingWater), typeof(FurinaOratricesEcho))]
    [InlineData(typeof(FurinaSteambirdClipping), typeof(FurinaLetterFromTheCourt))]
    public void The_act_1_event_picks_act_2s(Type act1, Type act2) =>
        Assert.Equal(act2, StoryRules.Route(F, 1, new[] { R(0, act1, "X") }, 7UL)!.EventType);

    [Theory]
    [InlineData(typeof(FurinaUnderstudy), typeof(FurinaCurtainCall))]
    [InlineData(typeof(FurinaOratricesEcho), typeof(FurinaEmptyThrone))]
    [InlineData(typeof(FurinaLetterFromTheCourt), typeof(FurinaEmptyThrone))]
    public void The_act_2_event_picks_act_3s(Type act2, Type act3) =>
        Assert.Equal(act3, StoryRules.Route(F, 2, new[] { R(1, act2, "X") }, 7UL)!.EventType);

    [Fact]
    public void A_skipped_act_falls_back_to_the_home_thread()
    {
        Assert.Equal(typeof(FurinaLetterFromTheCourt), StoryRules.Route(F, 1, None, 7UL)!.EventType);
        foreach (var t in new[] { typeof(FurinaEmptyHouse), typeof(FurinaRisingWater), typeof(FurinaSteambirdClipping) })
        {
            Assert.Equal(typeof(FurinaEmptyThrone), StoryRules.Route(F, 2, new[] { R(0, t, "X") }, 7UL)!.EventType);
        }
        Assert.Equal(typeof(FurinaEmptyThrone), StoryRules.Route(F, 2, None, 7UL)!.EventType);
        Assert.Equal(1, F.Events.Count(e => e.Home && e.ActIndex == 1));
        Assert.Equal(1, F.Events.Count(e => e.Home && e.ActIndex == 2));
    }

    [Fact]
    public void At_most_one_fires_per_act()
    {
        for (var act = 0; act < 3; act++)
        {
            var fired = F.Events.First(e => e.ActIndex == act);
            Assert.Null(StoryRules.Route(F, act, new[] { R(act, fired.EventType) }, 7UL));
        }
        Assert.Null(StoryRules.Route(F, 3, None, 7UL));
    }

    private static string? Opening(Type evt, params StoryRecord[] records) =>
        StoryRules.OpeningFor(E(evt), records)?.Key;

    [Fact]
    public void Later_events_open_with_the_line_that_matches_what_she_did()
    {
        var house = typeof(FurinaEmptyHouse);
        Assert.Equal("PERFORMED", Opening(typeof(FurinaUnderstudy), R(0, house, "PERFORM_FOR_NO_ONE")));
        Assert.Equal("FRONT_ROW", Opening(typeof(FurinaUnderstudy), R(0, house, "SIT_IN_THE_FRONT_ROW")));
        Assert.Equal("COSTUME", Opening(typeof(FurinaUnderstudy), R(0, house, "TAKE_A_COSTUME")));

        var water = typeof(FurinaRisingWater);
        Assert.Equal("RAN", Opening(typeof(FurinaOratricesEcho), R(0, water, "RUN_FOR_THE_STAIRS")));
        Assert.Equal("STOOD", Opening(typeof(FurinaOratricesEcho), R(0, water, "STAND_IN_IT")));
        Assert.Equal("HUMMED", Opening(typeof(FurinaOratricesEcho), R(0, water, "HUM_THE_OVERTURE")));

        var clip = typeof(FurinaSteambirdClipping);
        Assert.Equal("READ", Opening(typeof(FurinaLetterFromTheCourt), R(0, clip, "READ_IT_ALOUD")));
        Assert.Equal("CAST", Opening(typeof(FurinaLetterFromTheCourt), R(0, clip, "CAST_THE_SEQUEL")));
        Assert.Equal("KEPT", Opening(typeof(FurinaLetterFromTheCourt), R(0, clip, "FOLD_IT_INTO_HER_GLOVE")));
        Assert.Null(Opening(typeof(FurinaLetterFromTheCourt)));

        var understudy = typeof(FurinaUnderstudy);
        Assert.Equal("TAUGHT", Opening(typeof(FurinaCurtainCall), R(1, understudy, "TEACH_HER_THE_ENDING")));
        Assert.Equal("TOOK_THE_ROLE", Opening(typeof(FurinaCurtainCall), R(1, understudy, "TAKE_THE_ROLE_BACK")));
        Assert.Equal("IMPROVISED", Opening(typeof(FurinaCurtainCall), R(1, understudy, "LET_HER_IMPROVISE")));

        var echo = typeof(FurinaOratricesEcho);
        Assert.Equal("GUILTY", Opening(typeof(FurinaEmptyThrone), R(1, echo, "PLEAD_GUILTY")));
        Assert.Equal("INNOCENT", Opening(typeof(FurinaEmptyThrone), R(1, echo, "PLEAD_INNOCENT")));
        Assert.Equal("PERFORMED", Opening(typeof(FurinaEmptyThrone), R(1, echo, "GIVE_IT_A_PERFORMANCE")));
        // "Any letter": every option of the Court's letter.
        foreach (var o in E(typeof(FurinaLetterFromTheCourt)).Options)
        {
            Assert.Equal("LETTER", Opening(typeof(FurinaEmptyThrone), R(1, typeof(FurinaLetterFromTheCourt), o.Key)));
        }
        Assert.Null(Opening(typeof(FurinaEmptyThrone)));
        Assert.Null(Opening(typeof(FurinaEmptyThrone), R(0, house, "PERFORM_FOR_NO_ONE")));
    }

    [Fact]
    public void A_price_she_cannot_pay_is_locked()
    {
        var performance = E(typeof(FurinaOratricesEcho)).Options[2];
        Assert.True(StoryRules.IsLocked(performance, new StoryDeckView(49, 10, 10, 0, 0)));
        Assert.False(StoryRules.IsLocked(performance, new StoryDeckView(50, 10, 10, 0, 0)));
        Assert.True(StoryRules.IsLocked(performance, new StoryDeckView(99, 10, 0, 0, 0)));
        var cake = E(typeof(FurinaLetterFromTheCourt)).Options[1];
        Assert.True(StoryRules.IsLocked(cake, new StoryDeckView(39, 10, 10, 0, 0)));
        Assert.False(StoryRules.IsLocked(cake, new StoryDeckView(40, 10, 10, 0, 0)));
        // "Remove every Doubt" with none is not a lock; the removal is.
        var breakIt = E(typeof(FurinaEmptyThrone)).Options[2];
        Assert.False(StoryRules.IsLocked(breakIt, new StoryDeckView(0, 10, 10, 0, 0)));
        Assert.True(StoryRules.IsLocked(breakIt, new StoryDeckView(0, 0, 10, 0, 0)));
    }

    [Fact]
    public void Only_Furina_takes_her_options()
    {
        foreach (var e in F.Events)
        {
            Assert.True(StoryRules.IsOwnersEvent(FurinaType, e.EventType));
            Assert.False(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Varka), e.EventType));
        }
    }

    [Fact]
    public void Every_option_and_page_has_its_loc_row()
    {
        var rows = StoryLoc.EventRows();
        foreach (var e in F.Events)
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

    // ---- The Ancients and her lines -------------------------------------------

    private const string FurinaEntry = "KLEEMOD-FURINA";

    private static AncientDialogueSet BaseSet() => new()
    {
        FirstVisitEverDialogue = null,
        CharacterDialogues = new Dictionary<string, IReadOnlyList<AncientDialogue>>(),
        AgnosticDialogues = new[]
        {
            new AncientDialogue("") { VisitIndex = 0 },
            new AncientDialogue("") { IsRepeating = true },
        },
    };

    [Fact]
    public void Every_Ancient_greets_her_with_her_exchange()
    {
        foreach (var a in F.Ancients)
        {
            var set = BaseSet();
            var added = StoryAncients.AddTo(set, a.AncientEntry, populate: false,
                entryOf: t => t == FurinaType ? FurinaEntry : "KLEEMOD-" + t.Name.ToUpperInvariant());
            Assert.Contains(FurinaEntry, added);
            Assert.True(set.CharacterDialogues[FurinaEntry].Single().IsRepeating);
        }
        var entry = StoryRegistry.EntryOf(FurinaType);
        var rows = StoryAncients.Rows(_ => "NEXT");
        foreach (var a in F.Ancients)
        {
            Assert.Equal(a.AncientLine, rows[$"{a.AncientEntry}.talk.{entry}.0-0.ancient"]);
            Assert.Equal(a.CharacterLine, rows[$"{a.AncientEntry}.talk.{entry}.0-1.char"]);
        }
    }

    [Fact]
    public void Her_line_rows_are_filed_under_her_entry()
    {
        var rows = StoryLoc.LineRows();
        var own = StoryRegistry.EntryOf(FurinaType);
        Assert.Equal(F.Lines.BossEntry, rows[StoryLines.Key(own, StoryLines.BossEntry)]);
        Assert.Equal(F.Lines.LowHp, rows[StoryLines.Key(own, StoryLines.LowHp)]);
        Assert.Equal(F.Lines.Signature, rows[StoryLines.Key(own, StoryLines.Signature)]);
        Assert.Equal(F.Lines.BossKill, rows[StoryLines.Key(own, StoryLines.BossKill)]);
        Assert.Equal(F.Lines.RunLoss, rows[StoryLines.Key(own, StoryLines.RunLoss)]);
        Assert.Equal(F.Lines.RunWin, rows[StoryLines.Key(own, StoryLines.RunWin)]);
    }

    [Fact]
    public void Who_speaks_at_a_boss_with_her_at_the_table()
    {
        var alone = Assert.Single(StoryRules.BossEntryPlan(new[] { FurinaType }));
        Assert.Same(F, alone.Story);
        Assert.Null(alone.Pair);

        // Her Kokomi pair: Furina opens.
        var kokomi = Assert.Single(StoryRules.BossEntryPlan(new[] { typeof(Kokomi), FurinaType }));
        Assert.Same(F, kokomi.Story);
        Assert.True(kokomi.Pair!.OwnFirst);
        var yae = Assert.Single(StoryRules.BossEntryPlan(new[] { FurinaType, typeof(Yae) }));
        Assert.Equal(typeof(Yae), yae.Pair!.Partner);

        // Klee's and Varka's pairs with her stay in their tables.
        foreach (var other in new[] { typeof(global::KleeMod.Klee), typeof(global::KleeMod.Varka) })
        {
            foreach (var seats in new[] { new[] { FurinaType, other }, new[] { other, FurinaType } })
            {
                var s = Assert.Single(StoryRules.BossEntryPlan(seats));
                Assert.Same(StoryRegistry.For(other), s.Story);
                Assert.Equal(FurinaType, s.Pair!.Partner);
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
