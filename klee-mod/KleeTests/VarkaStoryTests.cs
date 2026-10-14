using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Story;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Ancients;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;
using MegaCrit.Sts2.Core.Saves.Runs;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// VARKA'S STORY IN THE RUN (<c>review/active/varka-story-2026-10-13.md</c>,
/// ruled "Sounds good! Let's go with it.").
///
/// The same headless boundary as <see cref="KleeStoryTests"/>: the words are
/// held against the paper, every decision runs through the pure function the
/// game calls, Overdue Reports' clock survives the game's own
/// <c>SavedProperties</c>, and what an option DOES against a live run is
/// pinned structurally on the commands it calls.
/// </summary>
public class VarkaStoryTests
{
    private static readonly CharacterStory V = VarkaStory.Table;
    private static readonly Type VarkaType = typeof(global::KleeMod.Varka);
    private static readonly Type KleeType = typeof(global::KleeMod.Klee);

    // ---- The words are the paper's --------------------------------------------

    private static string Paper() => File.ReadAllText(Path.Combine(
        RepoRoot(), "review", "active", "varka-story-2026-10-13.md"));

    /// <summary>The game's markup back to the paper's Markdown.</summary>
    private static string ToPaper(string s) => s
        .Replace("[i]", "*").Replace("[/i]", "*")
        .Replace("[gold]", "**").Replace("[/gold]", "**");

    [Fact]
    public void The_intro_is_the_papers_two_lines()
    {
        Assert.Contains($"> **{V.IntroTitle}** {V.IntroLine}", Paper());
        Assert.Equal(V.IntroTitle + "\n" + V.IntroLine, V.Intro);
        var intro = new global::KleeMod.Varka().Localization!.Single(r => r.Item1 == "description");
        Assert.Equal(V.Intro, intro.Item2);
    }

    [Fact]
    public void Every_Ancient_exchange_is_the_papers_word_for_word()
    {
        var paper = Paper();
        Assert.Equal(
            new[] { "NEOW", "OROBAS", "PAEL", "TEZCATARA", "NONUPEIPE", "TANX", "VAKUU", "DARV" },
            V.Ancients.Select(a => a.AncientEntry));
        foreach (var a in V.Ancients)
        {
            Assert.Contains(
                $"| {a.Ancient} | \"{ToPaper(a.AncientLine)}\" | \"{ToPaper(a.CharacterLine)}\" |",
                paper);
            Assert.Equal(a.Ancient.ToUpperInvariant(), a.AncientEntry);
        }
    }

    [Fact]
    public void Every_combat_line_is_the_papers_word_for_word()
    {
        var paper = Paper();
        var l = V.Lines;
        Assert.Contains($"| Entering a boss fight | \"{l.BossEntry}\" |", paper);
        Assert.Contains($"| Below a third of his HP | \"{l.LowHp}\" |", paper);
        Assert.Contains($"| Four Winds' Ascension | \"{l.Signature}\" |", paper);
        Assert.Contains($"| Killing a boss | \"{l.BossKill}\" |", paper);
        Assert.Contains($"| Losing the run | \"{l.RunLoss}\" |", paper);
        Assert.Contains($"| Winning the run | \"{l.RunWin}\" |", paper);
        // The signature moment is that card.
        Assert.Contains(typeof(ProtoVkFourWindsAscension), V.SignatureCards);
        Assert.Equal("Four Winds' Ascension", Title(new ProtoVkFourWindsAscension()));
    }

    [Fact]
    public void Every_pair_exchange_is_the_papers_word_for_word_in_the_papers_order()
    {
        var paper = Paper();
        Assert.Equal(new[] { typeof(Kokomi), typeof(Furina) }, V.Pairs.Select(p => p.Partner));
        foreach (var p in V.Pairs)
        {
            Assert.Equal(p.Partner.Name, p.PartnerName);
            var row = p.OwnFirst
                ? $"Varka: \"{p.OwnLine}\" {p.PartnerName}: \"{p.PartnerLine}\""
                : $"{p.PartnerName}: \"{p.PartnerLine}\" Varka: \"{p.OwnLine}\"";
            Assert.Contains($"| Varka and {p.PartnerName} | {row} |", paper);
        }
        Assert.True(V.Pairs.Single(p => p.Partner == typeof(Kokomi)).OwnFirst);
        Assert.False(V.Pairs.Single(p => p.Partner == typeof(Furina)).OwnFirst);

        // His pair with Klee is in her table, written with her batch, and is
        // the same words this paper quotes.
        var klee = KleeStory.Table.Pairs.Single(p => p.Partner == typeof(Varka));
        Assert.Contains(
            $"| Varka and Klee | (written with Klee's batch) Varka: \"{klee.PartnerLine}\" "
          + $"Klee: \"{klee.OwnLine}\" |",
            paper);
    }

    [Fact]
    public void Dispatch_from_Mondstadt_is_the_papers_page_and_table()
    {
        var paper = Paper();
        var e = V.Events[0];
        Assert.Contains($"## 3. Act 1: {e.Title}", paper);
        Assert.Contains($"> {e.Body}", paper);
        Assert.Equal(3, e.Options.Count);
        foreach (var o in e.Options)
        {
            Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} |", paper);
            Assert.Null(o.Result);
        }
        Assert.Contains(
            $"**{OverdueReports.TitleText}** is a Varka-only curse built like Klee's Confinement: "
          + $"\"Unplayable. {StoryCurse.DescriptionText}\"",
            paper);
    }

    [Fact]
    public void The_Wolf_of_the_North_is_the_papers_page_and_table()
    {
        var paper = Paper();
        var e = V.Events[1];
        Assert.Contains($"## 4. Act 2: {e.Title}", paper);
        var parts = e.Body.Split("\n\n");
        Assert.Equal(2, parts.Length);
        Assert.Contains($"> {parts[0]}\n>\n> {ToPaper(parts[1])}", paper);
        Assert.Equal(3, e.Options.Count);
        foreach (var o in e.Options)
        {
            Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} |", paper);
            Assert.Null(o.Result);
        }
    }

    [Fact]
    public void The_Long_Way_Home_is_the_papers_page_table_lines_and_answer()
    {
        var paper = Paper();
        var e = V.Events[2];
        Assert.Contains($"## 5. Act 3: {e.Title}", paper);
        Assert.Contains($"> {e.Body}", paper);
        Assert.Contains($"When one steps out, Varka answers: \"{VarkaStory.HomeAnswer}\"", paper);
        Assert.Equal(4, e.Options.Count);
        foreach (var o in e.Options.Take(3))
        {
            var lines = o.Result!.Split('\n');
            Assert.Equal(2, lines.Length);
            Assert.StartsWith(o.Title + ": \"", lines[0]);
            var line = lines[0][(o.Title.Length + 3)..^1];
            Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} | \"{line}\" |", paper);
            Assert.Equal($"Varka: \"{VarkaStory.HomeAnswer}\"", lines[1]);
        }
        var skip = e.Options[3];
        Assert.Contains(
            $"| **{skip.Title}** | {skip.Description} | \"{VarkaStory.WaveBackLine}\" |", paper);
        Assert.Equal($"Varka: \"{VarkaStory.WaveBackLine}\"", skip.Result);
    }

    [Fact]
    public void Each_effect_line_states_its_own_numbers_and_cards()
    {
        foreach (var o in V.Events.SelectMany(e => e.Options))
        {
            if (o.Effect.Amount > 0) Assert.Contains(o.Effect.Amount.ToString(), o.Description);
            if (o.Effect.HpLoss > 0) Assert.Contains($"Lose {o.Effect.HpLoss} HP", o.Description);
            if (o.Effect.Card != null && o.Effect.Card != typeof(OverdueReports))
            {
                var card = (BaseLib.Abstracts.CustomCardModel)Activator.CreateInstance(o.Effect.Card)!;
                Assert.Contains($"[gold]{Title(card)}[/gold]", o.Description);
            }
        }
        Assert.Equal("Razor: Awakening", Title(new ProtoVkRazorClawAndThunder()));
        Assert.Equal("Eula: Icetide Vortex", Title(new ProtoVkEulaIcetideVortex()));
        Assert.Equal("Noelle: Steadfast Maid", Title(new ProtoVkNoelleSteadfastMaid()));
        Assert.Equal("Diluc: Searing Onslaught", Title(new ProtoVkDilucSearingOnslaught()));
        // The paper's own card ids for act 3, and his Uncommons all three.
        var paper = Paper();
        foreach (var id in new[] { "proto_vk_eula_icetide_vortex", "proto_vk_noelle_steadfast_maid",
                                   "proto_vk_diluc_searing_onslaught" })
        {
            Assert.Contains($"`{id}`", paper);
        }
        foreach (var card in new CardModel[] { new ProtoVkEulaIcetideVortex(), new ProtoVkNoelleSteadfastMaid(),
                                               new ProtoVkDilucSearingOnslaught() })
        {
            Assert.Equal(CardRarity.Uncommon, card.Rarity);
        }
    }

    // ---- Each option's effect, as the paper's tables say ----------------------

    [Fact]
    public void The_options_do_what_the_tables_say()
    {
        Effect(0, 0, StoryEffectKind.UpgradeRandomCards, 2, null);
        Effect(0, 1, StoryEffectKind.GainGoldAddCard, 75, typeof(OverdueReports));
        Effect(0, 2, StoryEffectKind.ChooseFromPoolToDeck, 3, null);
        Effect(1, 0, StoryEffectKind.LoseHpUpgradeRandomCards, 3, null, hpLoss: 12);
        Effect(1, 1, StoryEffectKind.Heal, 20, null);
        Effect(1, 2, StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkRazorClawAndThunder));
        Effect(2, 0, StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkEulaIcetideVortex));
        Effect(2, 1, StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkNoelleSteadfastMaid));
        Effect(2, 2, StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkDilucSearingOnslaught));
        Effect(2, 3, StoryEffectKind.Nothing, 0, null);
    }

    private static void Effect(int evt, int option, StoryEffectKind kind, int amount, Type? card, int hpLoss = 0)
    {
        var e = V.Events[evt].Options[option].Effect;
        Assert.Equal(kind, e.Kind);
        Assert.Equal(amount, e.Amount);
        Assert.Equal(card, e.Card);
        Assert.Equal(hpLoss, e.HpLoss);
    }

    [Fact]
    public void The_new_effects_run_the_games_own_commands_structural()
    {
        // STRUCTURAL: an option's effect is a command against a live run.
        var apply = Il.Calls(Il.Method(nameof(StoryEventModel), "Apply"));
        Assert.Contains("CreatureCmd.Damage", apply);
        Assert.Contains("StoryEventModel.UpgradeRandom", apply);
        Assert.Contains("StoryEventModel.ChooseFromPool", apply);
        var upgrade = Il.Calls(Il.Method(nameof(StoryEventModel), "UpgradeRandom"));
        Assert.Contains("StoryRules.PickRandom", upgrade);
        Assert.Contains("CardCmd.Upgrade", upgrade);
        // Knights' Roll Call's pool, three distinct, on the game's add-to-deck grid.
        var choose = Il.Calls(Il.Method(nameof(StoryEventModel), "ChooseFromPool"));
        Assert.Contains("StoryRules.PickRandom", choose);
        Assert.Contains("EventModel.SelectCardsToAddToDeckFromGrid", choose);
        Assert.NotNull(V.ChoicePool);
        Assert.Equal(typeof(VarkaRules), V.ChoicePool!.Method.DeclaringType);
        Assert.Equal(nameof(VarkaRules.PoolKnights), V.ChoicePool.Method.Name);
        Assert.Equal(3, VarkaRules.OrderAnswersOptions);
    }

    [Fact]
    public void Upgrade_two_or_three_random_cards_takes_distinct_cards_or_all_there_are()
    {
        var deck = new[] { "a", "b", "c", "d" };
        Assert.Equal(3, StoryRules.PickRandom(deck, 3, _ => 0).Distinct().Count());
        Assert.Equal(new[] { "a", "b" }, StoryRules.PickRandom(new[] { "a", "b" }, 3, _ => 0));
        Assert.Empty(StoryRules.PickRandom(Array.Empty<string>(), 2, _ => 0));
    }

    // ---- Overdue Reports: Confinement's clock -----------------------------------

    [Fact]
    public void Overdue_Reports_is_an_unplayable_removable_story_Curse()
    {
        var curse = new OverdueReports();
        Assert.IsAssignableFrom<StoryCurse>(curse);
        Assert.Equal(CardType.Curse, curse.Type);
        Assert.Equal(CardRarity.Curse, curse.Rarity);
        Assert.Contains(CardKeyword.Unplayable, curse.CanonicalKeywords);
        Assert.True(StoryEventModel.IsRemovableCurse(curse));
        Assert.Equal(0, curse.MaxUpgradeLevel);
        var loc = curse.Localization!;
        Assert.Equal("Overdue Reports", loc.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("After 3 combats, remove this from your deck.", loc.Single(r => r.Item1 == "description").Item2);
        // Confinement's text is unchanged by the shared base.
        Assert.Equal("Confinement", new Confinement().Localization!.Single(r => r.Item1 == "title").Item2);
    }

    [Fact]
    public void Overdue_Reports_rides_the_story_Curse_clock_and_survives_a_save()
    {
        // Structural: the combat-end clock ticks every story Curse.
        var calls = Il.Calls(Il.Method(nameof(StoryLines), "ServeStoryCurses"));
        Assert.Contains("StoryCurse.set_CombatsServed", calls);
        Assert.Contains("CardPileCmd.RemoveFromDeck", calls);

        var prop = typeof(OverdueReports).GetProperty(nameof(StoryCurse.CombatsServed))!;
        Assert.NotNull(prop.GetCustomAttribute<SavedPropertyAttribute>());
        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(OverdueReports));
            initialized.SetValue(null, true);
            var card = Mutable(new OverdueReports());
            card.CombatsServed = 2;
            var props = SavedProperties.FromInternal(card, null);
            Assert.NotNull(props);
            var loaded = Mutable(new OverdueReports());
            props!.FillInternal(loaded);
            Assert.Equal(2, loaded.CombatsServed);
            loaded.CombatsServed += 1;
            Assert.True(StoryRules.StoryCurseServedOut(loaded.CombatsServed));
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    // ---- The events are his, act by act ----------------------------------------

    private static readonly Func<Type, bool> NothingSeen = _ => false;

    [Fact]
    public void Each_act_offers_Varka_his_own_event_and_no_one_else_any()
    {
        var solo = new[] { VarkaType };
        Assert.Equal(typeof(VarkaDispatchFromMondstadt), StoryRules.EventFor(solo, 0, NothingSeen)!.EventType);
        Assert.Equal(typeof(VarkaWolfOfTheNorth), StoryRules.EventFor(solo, 1, NothingSeen)!.EventType);
        Assert.Equal(typeof(VarkaLongWayHome), StoryRules.EventFor(solo, 2, NothingSeen)!.EventType);
        Assert.Null(StoryRules.EventFor(solo, 3, NothingSeen));
        Assert.Equal(new[] { 0, 1, 2 }, V.Events.Select(e => e.ActIndex));
        Assert.Null(StoryRules.EventFor(new[] { typeof(Kokomi), typeof(Furina) }, 0, NothingSeen));
    }

    [Fact]
    public void Varka_and_Klee_at_one_table_each_get_their_own_once()
    {
        var table = new[] { KleeType, VarkaType };
        Assert.Equal(typeof(KleeStarsnatchCliff), StoryRules.EventFor(table, 0, NothingSeen)!.EventType);
        Assert.Equal(typeof(VarkaDispatchFromMondstadt),
            StoryRules.EventFor(table, 0, t => t == typeof(KleeStarsnatchCliff))!.EventType);
        Assert.Null(StoryRules.EventFor(table, 0,
            t => t == typeof(KleeStarsnatchCliff) || t == typeof(VarkaDispatchFromMondstadt)));
    }

    [Fact]
    public void Only_Varka_takes_the_options()
    {
        Assert.True(StoryRules.IsOwnersEvent(VarkaType, typeof(VarkaDispatchFromMondstadt)));
        Assert.True(StoryRules.IsOwnersEvent(VarkaType, typeof(VarkaLongWayHome)));
        Assert.False(StoryRules.IsOwnersEvent(KleeType, typeof(VarkaWolfOfTheNorth)));
        Assert.False(StoryRules.IsOwnersEvent(VarkaType, typeof(KleeStarsnatchCliff)));
        Assert.False(StoryRules.IsOwnersEvent(null, typeof(VarkaDispatchFromMondstadt)));
    }

    [Fact]
    public void Every_option_and_page_has_its_loc_row()
    {
        var rows = StoryLoc.EventRows();
        foreach (var e in V.Events)
        {
            var local = StoryEventModel.Rows(e, "X");
            Assert.Equal(e.Title, local["X.title"]);
            Assert.Equal(e.Body, local["X.pages.INITIAL.description"]);
            foreach (var o in e.Options)
            {
                Assert.Equal(o.Title, local[$"X.pages.INITIAL.options.{o.Key}.title"]);
                Assert.Equal(o.Description, local[$"X.pages.INITIAL.options.{o.Key}.description"]);
                Assert.Equal(o.Result ?? e.Body, local[$"X.pages.{o.Key}.description"]);
            }
            var entry = StoryRegistry.EntryOf(e.EventType);
            Assert.Equal(e.Title, rows[entry + ".title"]);
        }
    }

    // ---- The Ancients greet him -----------------------------------------------

    private const string KleeEntry = "KLEEMOD-KLEE";
    private const string VarkaEntry = "KLEEMOD-VARKA";

    private static string EntryOf(Type t) => t == VarkaType ? VarkaEntry : KleeEntry;

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
    public void Every_Ancient_greets_him_with_his_exchange_on_every_visit()
    {
        foreach (var a in V.Ancients)
        {
            var set = BaseSet();
            var added = StoryAncients.AddTo(set, a.AncientEntry, populate: false, entryOf: EntryOf);
            Assert.Contains(VarkaEntry, added);
            var his = set.CharacterDialogues[VarkaEntry].Single();
            Assert.True(his.IsRepeating);
            foreach (var total in new[] { 1, 5, 40 })
            {
                Assert.Same(his, StoryAncients.StoryDialogueFor(set, VarkaEntry, total));
            }
        }
        var entry = StoryRegistry.EntryOf(VarkaType);
        var rows = StoryAncients.Rows(_ => "NEXT");
        foreach (var a in V.Ancients)
        {
            Assert.Equal(a.AncientLine, rows[$"{a.AncientEntry}.talk.{entry}.0-0.ancient"]);
            Assert.Equal(a.CharacterLine, rows[$"{a.AncientEntry}.talk.{entry}.0-1.char"]);
        }
    }

    // ---- Combat lines ---------------------------------------------------------

    [Fact]
    public void Dandelion_Gale_speaks_the_signature_line_too()
    {
        // Orobas's Archaic Tooth replaces the Ascension with the Gale; the
        // bark follows it (release fix, 2026-10-14).
        Assert.True(StoryRules.IsSignaturePlay(V, typeof(global::KleeMod.Cards.Varka.DandelionGale)));
        Assert.Equal(2, V.SignatureCards.Count);
        // Data on the table, not a special case in the rule.
        Assert.DoesNotContain(
            Il.Calls(Il.Method(nameof(StoryRules), nameof(StoryRules.IsSignaturePlay))),
            c => c.Contains("DandelionGale"));
    }

    [Fact]
    public void Four_Winds_Ascension_is_his_signature_once_a_combat()
    {
        Assert.True(StoryRules.IsSignaturePlay(V, typeof(ProtoVkFourWindsAscension)));
        Assert.False(StoryRules.IsSignaturePlay(V, typeof(ProtoVkKnightsRollCall)));
        Assert.False(StoryRules.IsSignaturePlay(V, null));
        // Klee's signature is her Bomb's, never a card play.
        Assert.False(StoryRules.IsSignaturePlay(KleeStory.Table, typeof(ProtoVkFourWindsAscension)));
        Assert.Empty(KleeStory.Table.SignatureCards);

        // Structural: the card-play hook asks the rule and speaks once a combat.
        var hook = Il.Calls(Il.Method(nameof(StoryCombatHooks), "AfterCardPlayed"));
        Assert.Contains("StoryRules.IsSignaturePlay", hook);
        Assert.Contains("StoryLines.SaySignature", hook);
        var say = Il.Calls(Il.Method(nameof(StoryLines), "SaySignature"));
        Assert.Contains("CombatLatch.TryTake", say);
        Assert.Contains("StoryLines.SaySignature",
            Il.Calls(Il.Method(nameof(StoryLines), "AfterBombWentOff")));
    }

    [Fact]
    public void His_line_rows_are_filed_under_his_entry()
    {
        var rows = StoryLoc.LineRows();
        var own = StoryRegistry.EntryOf(VarkaType);
        Assert.Equal(V.Lines.BossEntry, rows[StoryLines.Key(own, StoryLines.BossEntry)]);
        Assert.Equal(V.Lines.LowHp, rows[StoryLines.Key(own, StoryLines.LowHp)]);
        Assert.Equal(V.Lines.Signature, rows[StoryLines.Key(own, StoryLines.Signature)]);
        Assert.Equal(V.Lines.BossKill, rows[StoryLines.Key(own, StoryLines.BossKill)]);
        Assert.Equal(V.Lines.RunLoss, rows[StoryLines.Key(own, StoryLines.RunLoss)]);
        Assert.Equal(V.Lines.RunWin, rows[StoryLines.Key(own, StoryLines.RunWin)]);
        foreach (var p in V.Pairs)
        {
            var partner = StoryRegistry.EntryOf(p.Partner);
            Assert.Equal(p.PartnerLine, rows[StoryLines.PairKey(own, partner, true)]);
            Assert.Equal(p.OwnLine, rows[StoryLines.PairKey(own, partner, false)]);
        }
    }

    // ---- Who speaks at a boss -------------------------------------------------

    [Fact]
    public void Varka_alone_says_his_own_boss_line()
    {
        var plan = StoryRules.BossEntryPlan(new[] { VarkaType });
        var s = Assert.Single(plan);
        Assert.Same(V, s.Story);
        Assert.Null(s.Pair);
        Assert.Single(StoryRules.BossEntryPlan(new[] { VarkaType, typeof(MegaCrit.Sts2.Core.Models.Characters.Ironclad) }));
        Assert.Empty(StoryRules.BossEntryPlan(new[] { typeof(Kokomi), typeof(Furina) }));
    }

    [Theory]
    [InlineData(true)]
    [InlineData(false)]
    public void Varka_and_Klee_play_the_pair_from_her_table_and_nothing_else(bool varkaFirst)
    {
        var seats = varkaFirst ? new[] { VarkaType, KleeType } : new[] { KleeType, VarkaType };
        var plan = StoryRules.BossEntryPlan(seats);
        var s = Assert.Single(plan);
        Assert.Same(KleeStory.Table, s.Story);
        Assert.Equal(typeof(Varka), s.Pair!.Partner);
        Assert.Equal(KleeType, seats[s.OwnerSeat]);
        Assert.Equal(VarkaType, seats[s.PartnerSeat]);
        Assert.False(s.Pair.OwnFirst); // Varka (the partner) speaks first
    }

    [Fact]
    public void Varka_with_Kokomi_opens_and_with_Furina_answers()
    {
        var kokomi = Assert.Single(StoryRules.BossEntryPlan(new[] { typeof(Kokomi), VarkaType }));
        Assert.Same(V, kokomi.Story);
        Assert.Equal(1, kokomi.OwnerSeat);
        Assert.Equal(0, kokomi.PartnerSeat);
        Assert.True(kokomi.Pair!.OwnFirst);
        var furina = Assert.Single(StoryRules.BossEntryPlan(new[] { VarkaType, typeof(Furina) }));
        Assert.Same(V, furina.Story);
        Assert.Equal(typeof(Furina), furina.Pair!.Partner);
        Assert.False(furina.Pair.OwnFirst);

        // Structural: the entry block reads the plan.
        Assert.Contains("StoryRules.BossEntryPlan", Il.Calls(Il.Method(nameof(StoryLines), "BossEntered")));
    }

    [Fact]
    public void Three_story_characters_each_speak_once()
    {
        // Klee takes Kokomi (first in her table); Varka has no free partner.
        var plan = StoryRules.BossEntryPlan(new[] { KleeType, VarkaType, typeof(Kokomi) });
        Assert.Equal(2, plan.Count);
        Assert.Equal(typeof(Kokomi), plan[0].Pair!.Partner);
        Assert.Null(plan[1].Pair);
        Assert.Same(V, plan[1].Story);
    }

    // ---- Helpers ---------------------------------------------------------------

    private static string Title(BaseLib.Abstracts.CustomCardModel card) => card.Localization!.Single(r => r.Item1 == "title").Item2;

    private static T Mutable<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

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
