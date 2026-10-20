using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
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
/// KLEE'S STORY IN THE RUN, batches 1 and 2
/// (<c>review/ruled/klee-story-batch-1-2026-10-12.md</c>,
/// <c>review/active/klee-story-batch-2-2026-10-12.md</c>).
///
/// THE HEADLESS BOUNDARY (README.md): no ModelDb, no event room, no live
/// combat, no loc tables. So the words are held against the papers, every
/// decision is run through the pure function the game calls
/// (<see cref="StoryRules"/>, <see cref="StoryAncients.AddTo"/>), the
/// dialogue lookup is the game's own <c>AncientDialogueSet</c>, Confinement's
/// clock survives the game's own <c>SavedProperties</c>, and what an option
/// DOES (a command against a live run) is pinned structurally on the
/// commands it calls. What only a live run shows is listed in the PR.
/// </summary>
public class KleeStoryTests
{
    private static readonly CharacterStory Klee = KleeStory.Table;

    // ---- The words are the papers' -------------------------------------------

    private static string Paper(int batch) => File.ReadAllText(Path.Combine(
        RepoRoot(), "review", batch == 1 ? "ruled" : "active",
        $"klee-story-batch-{batch}-2026-10-12.md"));

    /// <summary>The game's markup back to the paper's Markdown.</summary>
    private static string ToPaper(string s) => s
        .Replace("[i]", "*").Replace("[/i]", "*")
        .Replace("[gold]", "**").Replace("[/gold]", "**");

    [Fact]
    public void The_intro_is_the_papers_two_lines()
    {
        Assert.Contains($"> **{Klee.IntroTitle}** {Klee.IntroLine}", Paper(1));
        Assert.Equal(Klee.IntroTitle + "\n" + Klee.IntroLine, Klee.Intro);
        var intro = new global::KleeMod.Klee().Localization!.Single(r => r.Item1 == "description");
        Assert.Equal(Klee.Intro, intro.Item2);
    }

    [Fact]
    public void Every_Ancient_exchange_is_the_papers_word_for_word()
    {
        var paper = Paper(1);
        Assert.Equal(
            new[] { "NEOW", "OROBAS", "PAEL", "TEZCATARA", "NONUPEIPE", "TANX", "VAKUU", "DARV" },
            Klee.Ancients.Select(a => a.AncientEntry));
        foreach (var a in Klee.Ancients)
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
        var paper = Paper(1);
        var l = Klee.Lines;
        Assert.Contains($"| Entering a boss fight | \"{ToPaper(l.BossEntry)}\" |", paper);
        Assert.Contains($"| Below a third of her HP | \"{ToPaper(l.LowHp)}\" |", paper);
        Assert.Contains($"| Her biggest Bomb (30 or more damage at once) | \"{ToPaper(l.Signature)}\" |", paper);
        Assert.Contains($"| Killing a boss | \"{ToPaper(l.BossKill)}\" |", paper);
        Assert.Contains($"| Losing the run | \"{ToPaper(l.RunLoss)}\" |", paper);
        Assert.Contains($"| Winning the run | \"{ToPaper(l.RunWin)}\" |", paper);
        Assert.Equal(30, StoryRules.BigBombDamage);
    }

    [Fact]
    public void Every_pair_exchange_is_the_papers_word_for_word()
    {
        var paper = Paper(1);
        Assert.Equal(new[] { typeof(Kokomi), typeof(Furina), typeof(Varka) },
                     Klee.Pairs.Select(p => p.Partner));
        foreach (var p in Klee.Pairs)
        {
            Assert.Equal(p.Partner.Name, p.PartnerName);
            Assert.Contains(
                $"| Klee and {p.PartnerName} | {p.PartnerName}: \"{ToPaper(p.PartnerLine)}\" "
              + $"Klee: \"{ToPaper(p.OwnLine)}\" |",
                paper);
        }
    }

    [Fact]
    public void Starsnatch_Cliff_is_the_papers_page_and_table()
    {
        // Its options and effects are batch 1's; its page (now a memory) and
        // its result lines are the story chains'.
        var paper = Paper(1);
        var chains = StoryChainTests.Paper();
        var e = Klee.Events[0];
        Assert.Contains($"## 3. Act 1's story event: {e.Title}", paper);
        Assert.Contains($"> {e.Body}", chains);
        Assert.Equal(3, e.Options.Count);
        foreach (var o in e.Options)
        {
            // "Just one little bomb" was repriced by the story rewards pass
            // (2026-10-19): its effect is the chains paper's now.
            if (o.Key == "JUST_ONE_LITTLE_BOMB")
                Assert.Contains($"| {o.Title} | {ToPaper(o.Description)} |", chains);
            else
                Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} |", paper);
            Assert.Contains($"| {o.Title} | ", chains);
            Assert.Contains($" | {o.Result} |", chains);
        }
        Assert.Contains(
            $"**{Confinement.TitleText}** is a Klee-only curse: \"Unplayable. {Confinement.DescriptionText}\"",
            paper);
    }

    [Fact]
    public void A_Letter_from_Jean_is_the_papers_page_and_table()
    {
        var paper = Paper(2);
        var e = Klee.Events[1];
        Assert.Contains($"## Act 2: {e.Title}", paper);
        var parts = e.Body.Split("\n\n");
        Assert.Equal(2, parts.Length);
        Assert.Contains($"> {parts[0]}\n>\n> {ToPaper(parts[1])}", paper);
        foreach (var o in e.Options)
        {
            Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} |", paper);
        }
        // The story chains give it result lines.
        foreach (var o in e.Options)
        {
            Assert.Contains("\"" + o.Result + "\"", StoryChainTests.Flat());
        }
    }

    [Fact]
    public void The_Knights_Come_Looking_is_the_papers_page_table_and_answer()
    {
        var paper = Paper(2);
        var e = Klee.Events[2];
        Assert.Contains($"## Act 3: {e.Title}", paper);
        Assert.Contains($"> {e.Body}", paper);
        Assert.Contains($"Klee answers whichever knight she picks: \"{KleeStory.KnightsAnswer}\"", paper);
        Assert.Equal(4, e.Options.Count);
        foreach (var o in e.Options.Take(3))
        {
            var lines = o.Result!.Split('\n');
            Assert.Equal(2, lines.Length);
            Assert.StartsWith(o.Title + ": \"", lines[0]);
            var knightLine = lines[0][(o.Title.Length + 3)..^1];
            Assert.Contains($"| **{o.Title}** | {ToPaper(o.Description)} | \"{knightLine}\" |", paper);
            Assert.Equal($"Klee: \"{KleeStory.KnightsAnswer}\"", lines[1]);
        }
    }

    [Fact]
    public void Each_effect_line_states_its_own_number_and_card()
    {
        foreach (var o in Klee.Events.SelectMany(e => e.Options))
        {
            foreach (var step in o.Effects)
            {
                // "Transform a card", "Gain a random potion": one is "a".
                if (step.Amount > 1) Assert.Contains(step.Amount.ToString(), o.Description);
            }
        }
        Assert.Equal("Fish Blasting", new ProtoKoFishBlasting().Localization!.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("Kaeya — Glacial Waltz", new ProtoMcKaeyaGlacialWaltz().Localization!.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("Noelle — Breastplate", new ProtoMcNoelleBreastplate().Localization!.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("Albedo — Solar Isotoma", new ProtoMcAlbedoSolarIsotoma().Localization!.Single(r => r.Item1 == "title").Item2);
    }

    // ---- Each option's effect, as the paper's tables say ----------------------

    [Fact]
    public void The_options_do_what_the_tables_say()
    {
        Effect(0, 0, StoryEffectKind.GainGoldAddCard, 75, typeof(Confinement));
        Effect(0, 1, StoryEffectKind.ChooseOfferToDeck, 3, null);
        Effect(0, 2, StoryEffectKind.RemoveCard, 0, null);
        Effect(1, 0, StoryEffectKind.Heal, 15, null);
        Effect(1, 1, StoryEffectKind.RemoveCurseElseGold, 50, null);
        Effect(1, 2, StoryEffectKind.UpgradeRandomBombCards, 2, null);
        // The story rewards pass: each knight's scene offers Companions.
        Effect(2, 0, StoryEffectKind.LoseHp, 6, null);
        Effect(2, 1, StoryEffectKind.ChooseOfferToDeck, 3, null);
        Effect(2, 2, StoryEffectKind.LoseHp, 12, null);
    }

    private static void Effect(int evt, int option, StoryEffectKind kind, int amount, Type? card)
    {
        var e = Klee.Events[evt].Options[option].Effect;
        Assert.Equal(kind, e.Kind);
        Assert.Equal(amount, e.Amount);
        Assert.Equal(card, e.Card);
    }

    [Fact]
    public void Each_effect_kind_runs_the_games_own_command_structural()
    {
        // STRUCTURAL: an option's effect is a command against a live run.
        var calls = Il.Calls(Il.Method(nameof(StoryEventModel), "Apply"));
        Assert.Contains("PlayerCmd.GainGold", calls);
        Assert.Contains("CreatureCmd.Heal", calls);
        // The random upgrades (Paper bomb's, and Varka's) share one helper;
        // Paper bomb's filter is the table's PlacesBomb (a closure, so it is
        // pinned by behaviour below, not by IL).
        Assert.Contains("StoryEventModel.UpgradeRandom", calls);
        var upgrade = Il.Calls(Il.Method(nameof(StoryEventModel), "UpgradeRandom"));
        Assert.Contains("CardCmd.Upgrade", upgrade);
        Assert.Contains("StoryRules.PickRandom", upgrade);
        var add = Il.Calls(Il.Method(nameof(StoryEventModel), "AddToDeck"));
        Assert.Contains("CardPileCmd.Add", add);
        Assert.Contains("CardCmd.Upgrade", add);
        var remove = Il.Calls(Il.Method(nameof(StoryEventModel), "RemoveChosen"));
        Assert.Contains("CardSelectCmd.FromDeckForRemoval", remove);
        Assert.Contains("CardPileCmd.RemoveFromDeck", remove);
    }

    [Fact]
    public void Paper_bomb_upgrades_two_random_Bomb_cards_or_all_there_are()
    {
        var deck = new[] { "a", "b", "c", "d" };
        var picks = StoryRules.PickRandom(deck, 2, n => n - 1);
        Assert.Equal(new[] { "d", "c" }, picks);
        Assert.Equal(new[] { "a" }, StoryRules.PickRandom(new[] { "a" }, 2, _ => 0));
        Assert.Empty(StoryRules.PickRandom(Array.Empty<string>(), 2, _ => 0));
        // Distinct: never the same card twice.
        var many = StoryRules.PickRandom(deck, 2, _ => 0);
        Assert.Equal(2, many.Distinct().Count());

        Assert.True(StoryRules.PlacesBomb(Klee, "KLEEMOD-PROTO_KO_POP"));
        Assert.True(StoryRules.PlacesBomb(Klee, "KLEEMOD-PROTO_KO_JUMPY_DUMPTY"));
        // Mk.III's hits place Bombs; the Archaic Tooth Ancient Mk.Omega is
        // not a sheet row but places a Bomb on ALL enemies and upgrades.
        Assert.True(StoryRules.PlacesBomb(Klee, "KLEEMOD-PROTO_KO_JUMPY_DUMPTY_MK_III"));
        var omega = new JumpyDumptyMkOmega();
        Assert.True(StoryRules.PlacesBomb(Klee, omega.Id.Entry));
        Assert.True(omega.IsUpgradable);
        Assert.False(StoryRules.PlacesBomb(Klee, "KLEEMOD-PROTO_KO_MINE_TOSS"));
        Assert.False(StoryRules.PlacesBomb(Klee, "STRIKE_IRONCLAD"));
        Assert.Equal("proto_ko_pop", StoryRules.SheetIdOf("KLEEMOD-PROTO_KO_POP"));
    }

    [Fact]
    public void Write_back_removes_a_Curse_and_Confinement_is_one()
    {
        var curse = new Confinement();
        Assert.Equal(CardType.Curse, curse.Type);
        Assert.Equal(CardRarity.Curse, curse.Rarity);
        Assert.True(StoryEventModel.IsRemovableCurse(curse));
        Assert.False(StoryEventModel.IsRemovableCurse(new ProtoKoFishBlasting()));
        Assert.Contains(CardKeyword.Unplayable, curse.CanonicalKeywords);
    }

    // ---- The event is Klee's, act by act ---------------------------------------

    private static readonly IReadOnlyList<StoryRecord> Nothing = Array.Empty<StoryRecord>();

    private static (Type, IReadOnlyList<StoryRecord>)[] Seats(params Type[] characters) =>
        characters.Select(c => (c, Nothing)).ToArray();

    [Fact]
    public void Each_act_offers_Klee_her_own_event_and_no_one_else_any()
    {
        var klee = Seats(typeof(global::KleeMod.Klee));
        Assert.Equal(0, StoryRules.EventFor(klee, 0, 7UL)!.ActIndex);
        Assert.Equal(typeof(KleeLetterFromJean), StoryRules.EventFor(klee, 1, 7UL)!.EventType);
        Assert.Equal(typeof(KleeKnightsComeLooking), StoryRules.EventFor(klee, 2, 7UL)!.EventType);
        Assert.Null(StoryRules.EventFor(klee, 3, 7UL));
        for (var act = 0; act < 4; act++)
        {
            Assert.Null(StoryRules.EventFor(Seats(typeof(MegaCrit.Sts2.Core.Models.Characters.Ironclad), typeof(Yae)), act, 7UL));
            Assert.Null(StoryRules.EventFor(Seats(typeof(MegaCrit.Sts2.Core.Models.Characters.Ironclad)), act, 7UL));
            Assert.Null(StoryRules.EventFor(Seats(), act, 7UL));
        }
        Assert.Equal(new[] { 0, 1, 2, 0, 1, 0, 1, 2 }, Klee.Events.Select(e => e.ActIndex));
    }

    [Fact]
    public void Klee_at_a_co_op_table_still_gets_hers_and_only_once()
    {
        var first = StoryRules.EventFor(Seats(typeof(Yae), typeof(global::KleeMod.Klee)), 0, 7UL)!;
        Assert.Contains(first, Klee.Events);
        var fired = new[] { new StoryRecord(0, first.EventType, null) };
        Assert.Null(StoryRules.EventFor(
            new (Type, IReadOnlyList<StoryRecord>)[] { (typeof(Yae), Nothing), (typeof(global::KleeMod.Klee), fired) },
            0, 7UL));
    }

    [Fact]
    public void Only_Klee_takes_the_options_everyone_else_gets_Proceed()
    {
        Assert.True(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Klee), typeof(KleeStarsnatchCliff)));
        Assert.True(StoryRules.IsOwnersEvent(typeof(global::KleeMod.Klee), typeof(KleeKnightsComeLooking)));
        Assert.False(StoryRules.IsOwnersEvent(typeof(Kokomi), typeof(KleeStarsnatchCliff)));
        Assert.False(StoryRules.IsOwnersEvent(null, typeof(KleeStarsnatchCliff)));
        Assert.Contains("SetEventFinished",
            string.Join(" ", Il.Calls(Il.Method(nameof(StoryEventModel), "SetInitialEventState"))));
    }

    [Fact]
    public void The_events_are_in_no_act_pool_they_arrive_by_substitution()
    {
        // Structural: the one seam that puts a story event on the map is the
        // game's ModifyNextEvent, and it asks the pure rule.
        var patch = typeof(StoryEventModel).Assembly.GetTypes()
            .Single(t => t.Name == "Hook_ModifyNextEvent_Story_Patch");
        var calls = Il.Calls(patch.GetMethod("Postfix", HeadlessGame.All)!);
        Assert.Contains("StoryRules.StoryRoomEventFor", calls);
        Assert.Contains("StoryHistory.EventRoomsThisAct", calls);
        Assert.Contains("StoryRules.RoomEventFor",
            Il.Calls(typeof(StoryRules).GetMethod(nameof(StoryRules.StoryRoomEventFor))!));
        Assert.Contains("StoryRules.EventFor",
            Il.Calls(typeof(StoryRules).GetMethod(nameof(StoryRules.RoomEventFor))!));
        // No act class in the mod names a story event.
        foreach (var t in typeof(StoryEventModel).Assembly.GetTypes()
                     .Where(t => typeof(ActModel).IsAssignableFrom(t)))
        {
            foreach (var m in t.GetMethods(HeadlessGame.All).Where(m => m.DeclaringType == t && m.GetMethodBody() != null))
            {
                Assert.DoesNotContain(Il.Calls(m), c => c.Contains("Klee") && c.Contains("Cliff"));
            }
        }
    }

    [Fact]
    public void Every_option_and_page_has_its_loc_row()
    {
        foreach (var e in Klee.Events)
        {
            var rows = StoryEventModel.Rows(e, "X");
            Assert.Equal(e.Title, rows["X.title"]);
            Assert.Equal(e.Body, rows["X.pages.INITIAL.description"]);
            foreach (var o in e.Options)
            {
                Assert.Equal(o.Title, rows[$"X.pages.INITIAL.options.{o.Key}.title"]);
                Assert.Equal(o.Description, rows[$"X.pages.INITIAL.options.{o.Key}.description"]);
                Assert.Equal(o.Result ?? e.Body, rows[$"X.pages.{o.Key}.description"]);
            }
        }
    }

    // ---- The Ancients: Klee's set for Klee, the agnostic set for anyone else ---

    private static AncientDialogueSet BaseSet() => new()
    {
        FirstVisitEverDialogue = null,
        CharacterDialogues = new Dictionary<string, IReadOnlyList<AncientDialogue>>
        {
            ["IRONCLAD"] = new[] { new AncientDialogue("") { VisitIndex = 0 } },
        },
        AgnosticDialogues = new[]
        {
            new AncientDialogue("") { VisitIndex = 0 },
            new AncientDialogue("") { IsRepeating = true },
        },
    };

    private const string KleeEntry = "KLEEMOD-KLEE";

    private static ModelId Character(string entry) => new("CHARACTER", entry);

    [Fact]
    public void The_lookup_returns_Klees_exchange_for_Klee_on_every_visit()
    {
        var set = BaseSet();
        var added = StoryAncients.AddTo(set, "NEOW", populate: false, entryOf: _ => KleeEntry);
        Assert.Equal(new[] { KleeEntry }, added);
        var hers = set.CharacterDialogues[KleeEntry][0];
        Assert.Equal(2, hers.Lines.Count);
        Assert.True(hers.IsRepeating);
        Assert.Null(hers.VisitIndex);

        // What the GetValidDialogues prefix answers: hers, visit after visit.
        foreach (var total in new[] { 1, 5, 40 })
        {
            Assert.Same(hers, StoryAncients.StoryDialogueFor(set, KleeEntry, total));
        }
        // And the game's own pools would still include it (repeating).
        Assert.Contains(hers, set.GetValidDialogues(Character(KleeEntry), 7, 9, true));

        // Structural: the prefix asks the pure function and short-circuits.
        var patch = typeof(StoryAncients).Assembly.GetTypes()
            .Single(t => t.Name == "Ancient_GetValidDialogues_Story_Patch");
        Assert.Contains("StoryAncients.StoryDialogueFor",
            Il.Calls(patch.GetMethod("Prefix", HeadlessGame.All)!));
    }

    [Fact]
    public void BaseLibs_entry_registered_first_is_replaced_and_hers_repeats()
    {
        // The live order: BaseLib's PopulateLocKeys prefix (AddAncientDialogues)
        // finds our NEOW.talk.KLEEMOD-KLEE.0-* rows and registers the entry
        // first, the way AncientDialogueUtil.GetDialoguesForKey builds it:
        // VisitIndex 0, not repeating. Our DialogueSet postfix runs after.
        var set = BaseSet();
        var baseLibs = new AncientDialogue("", "") { VisitIndex = 0 };
        set.CharacterDialogues[KleeEntry] = new[] { baseLibs };

        // The bug as seen on 0.2.5073: past her first visit the game gives the
        // stock repeating line, never hers.
        Assert.Same(set.AgnosticDialogues[1],
                    set.GetValidDialogues(Character(KleeEntry), 3, 9, true).Single());

        var added = StoryAncients.AddTo(set, "NEOW", populate: false, entryOf: _ => KleeEntry);
        Assert.Equal(new[] { KleeEntry }, added);
        var hers = set.CharacterDialogues[KleeEntry].Single();
        Assert.NotSame(baseLibs, hers);
        Assert.True(hers.IsRepeating);
        Assert.Null(hers.VisitIndex);
        foreach (var total in new[] { 1, 2, 5, 40 })
        {
            Assert.Same(hers, StoryAncients.StoryDialogueFor(set, KleeEntry, total));
        }
        // And the game's own repeating pool holds hers (BaseLib's never was).
        Assert.Contains(hers, set.GetValidDialogues(Character(KleeEntry), 3, 9, true));

        // A second pass over the same set leaves hers in place.
        Assert.Empty(StoryAncients.AddTo(set, "NEOW", populate: false, entryOf: _ => KleeEntry));
        Assert.Same(hers, set.CharacterDialogues[KleeEntry].Single());
    }

    [Fact]
    public void The_games_once_ever_introduction_still_comes_first()
    {
        var set = BaseSet();
        var intro = new AncientDialogue("");
        var withIntro = new AncientDialogueSet
        {
            FirstVisitEverDialogue = intro,
            CharacterDialogues = set.CharacterDialogues,
            AgnosticDialogues = set.AgnosticDialogues,
        };
        StoryAncients.AddTo(withIntro, "NEOW", populate: false, entryOf: _ => KleeEntry);
        Assert.Null(StoryAncients.StoryDialogueFor(withIntro, KleeEntry, totalVisits: 0));
        Assert.Same(intro, withIntro.GetValidDialogues(Character(KleeEntry), 0, 0, true).Single());
        Assert.NotNull(StoryAncients.StoryDialogueFor(withIntro, KleeEntry, totalVisits: 1));
    }

    [Fact]
    public void The_lookup_returns_the_agnostic_set_for_everyone_else()
    {
        var set = BaseSet();
        StoryAncients.AddTo(set, "NEOW", populate: false, entryOf: _ => KleeEntry);
        foreach (var other in new[] { "KLEEMOD-KOKOMI", "KLEEMOD-FURINA", "KLEEMOD-VARKA" })
        {
            Assert.Null(StoryAncients.StoryDialogueFor(set, other, 5));
            var valid = set.GetValidDialogues(Character(other), 0, 5, true).ToList();
            Assert.Single(valid);
            Assert.Same(set.AgnosticDialogues[0], valid[0]);
        }
        // A base character keeps its own, and its lines are never taken for hers.
        Assert.Null(StoryAncients.StoryDialogueFor(set, "IRONCLAD", 5));
        Assert.Same(set.CharacterDialogues["IRONCLAD"][0],
                    set.GetValidDialogues(Character("IRONCLAD"), 0, 5, true).Single());
    }

    [Fact]
    public void Every_Ancient_has_her_exchange_and_the_Architect_is_left_alone()
    {
        foreach (var a in Klee.Ancients)
        {
            var s = BaseSet();
            Assert.Single(StoryAncients.AddTo(s, a.AncientEntry, populate: false, entryOf: _ => KleeEntry));
        }
        var architect = BaseSet();
        Assert.Empty(StoryAncients.AddTo(architect, "THE_ARCHITECT", populate: false, entryOf: _ => KleeEntry));
        Assert.False(architect.CharacterDialogues.ContainsKey(KleeEntry));
        Assert.Null(StoryAncients.StoryDialogueFor(architect, KleeEntry, 5));
    }

    [Fact]
    public void The_Ancient_rows_are_the_lines_under_the_games_own_keys()
    {
        var entry = StoryRegistry.EntryOf(typeof(global::KleeMod.Klee));
        var rows = StoryAncients.Rows(_ => "NEXT");
        Assert.Equal(StoryRegistry.All.Sum(s => s.Ancients.Count) * 3, rows.Count);
        foreach (var a in Klee.Ancients)
        {
            Assert.Equal(a.AncientLine, rows[$"{a.AncientEntry}.talk.{entry}.0-0.ancient"]);
            Assert.Equal(a.CharacterLine, rows[$"{a.AncientEntry}.talk.{entry}.0-1.char"]);
            Assert.Equal("NEXT", rows[$"{a.AncientEntry}.talk.{entry}.0-0.next"]);
        }
    }

    // ---- Confinement: three combats, and a save between them -------------------

    [Fact]
    public void Confinement_is_removed_after_exactly_three_combats()
    {
        Assert.Equal(3, StoryRules.StoryCurseCombats);
        var served = 0;
        var removedAfter = -1;
        for (var combat = 1; combat <= 5 && removedAfter < 0; combat++)
        {
            served++;
            if (StoryRules.StoryCurseServedOut(served)) removedAfter = combat;
        }
        Assert.Equal(3, removedAfter);
        Assert.False(StoryRules.StoryCurseServedOut(2));

        // Structural: the combat-end hook ticks every Confinement in every
        // deck and removes the served ones through the game's own command.
        var calls = Il.Calls(Il.Method(nameof(StoryLines), "ServeStoryCurses"));
        Assert.Contains("StoryCurse.set_CombatsServed", calls);
        Assert.Contains("StoryRules.StoryCurseServedOut", calls);
        Assert.Contains("CardPileCmd.RemoveFromDeck", calls);
        Assert.Contains("StoryLines.ServeStoryCurses",
            Il.Calls(Il.Method(nameof(StoryCombatHooks), "AfterCombatEnd")));
    }

    [Fact]
    public void Confinement_count_survives_the_games_own_save_and_reload()
    {
        var prop = typeof(Confinement).GetProperty(nameof(Confinement.CombatsServed))!;
        Assert.NotNull(prop.GetCustomAttribute<SavedPropertyAttribute>());

        var initialized = typeof(ModelIdSerializationCache)
            .GetField("_initialized", BindingFlags.Static | BindingFlags.NonPublic);
        Assert.NotNull(initialized);
        var was = (bool)initialized!.GetValue(null)!;
        try
        {
            ModelIdSerializationCache.CacheSavedPropertiesForTypeDebug(typeof(Confinement));
            initialized.SetValue(null, true);

            var card = Mutable(new Confinement());
            card.CombatsServed = 2;
            var props = SavedProperties.FromInternal(card, null);
            Assert.NotNull(props);
            var loaded = Mutable(new Confinement());
            props!.FillInternal(loaded);
            Assert.Equal(2, loaded.CombatsServed);

            // One more combat after the reload is the third.
            loaded.CombatsServed += 1;
            Assert.True(StoryRules.StoryCurseServedOut(loaded.CombatsServed));
        }
        finally
        {
            initialized.SetValue(null, was);
        }
    }

    // ---- Trigger guards --------------------------------------------------------

    [Fact]
    public void A_once_a_combat_line_fires_once_a_combat()
    {
        var combat = new object();
        var klee = new object();
        var latch = StoryLines.LatchFor(combat);
        Assert.True(latch.TryTake(klee, StoryLines.Signature));
        Assert.False(latch.TryTake(klee, StoryLines.Signature));
        Assert.False(StoryLines.LatchFor(combat).TryTake(klee, StoryLines.Signature));
        // Another line, or another Klee, is its own latch.
        Assert.True(latch.TryTake(klee, StoryLines.LowHp));
        Assert.True(latch.TryTake(new object(), StoryLines.Signature));
        // The next combat starts fresh.
        Assert.True(StoryLines.LatchFor(new object()).TryTake(klee, StoryLines.Signature));
    }

    [Fact]
    public void Below_a_third_fires_on_the_drop_only()
    {
        Assert.True(StoryRules.CrossedBelowThird(30, 20, 70));   // 30*3=90 >= 70, 20*3=60 < 70
        Assert.False(StoryRules.CrossedBelowThird(60, 30, 70));  // still at a third or more
        Assert.False(StoryRules.CrossedBelowThird(20, 15, 70));  // already below: no drop
        Assert.False(StoryRules.CrossedBelowThird(30, 0, 70));   // dead says nothing
        Assert.True(StoryRules.CrossedBelowThird(24, 23, 70));   // 24 is a third (72 >= 70), 23 is not
        Assert.False(StoryRules.CrossedBelowThird(10, 5, 0));
    }

    [Fact]
    public void KABOOM_needs_one_Bomb_of_30_or_more()
    {
        Assert.True(StoryRules.IsBigBomb(isMine: false, dealt: 30));
        Assert.True(StoryRules.IsBigBomb(false, 75));
        Assert.False(StoryRules.IsBigBomb(false, 29));
        Assert.False(StoryRules.IsBigBomb(isMine: true, dealt: 40));
        Assert.Contains("StoryLines.AfterBombWentOff",
            Il.Calls(Il.Method("ProtoBombPower", "Explode")));
    }

    [Fact]
    public void Pair_lines_need_both_characters_at_the_table()
    {
        Assert.Equal(typeof(Kokomi), StoryRules.PairFor(Klee, new[] { typeof(Kokomi) })!.Partner);
        Assert.Equal(typeof(Furina), StoryRules.PairFor(Klee, new[] { typeof(Furina) })!.Partner);
        Assert.Equal(typeof(Varka), StoryRules.PairFor(Klee, new[] { typeof(Varka) })!.Partner);
        Assert.Null(StoryRules.PairFor(Klee, Array.Empty<Type>()));
        Assert.Null(StoryRules.PairFor(Klee, new[] { typeof(MegaCrit.Sts2.Core.Models.Characters.Ironclad) }));
        Assert.Null(StoryRules.PairFor(Klee, new[] { typeof(global::KleeMod.Klee) }));
        // Two partners: the first in her table speaks.
        Assert.Equal(typeof(Kokomi), StoryRules.PairFor(Klee, new[] { typeof(Varka), typeof(Kokomi) })!.Partner);
    }

    [Fact]
    public void The_line_rows_cover_every_line_and_pair()
    {
        var rows = StoryLoc.LineRows();
        var own = StoryRegistry.EntryOf(typeof(global::KleeMod.Klee));
        Assert.Equal(StoryRegistry.All.Sum(s => (s.Lines == null ? 0 : 6) + 2 * s.Pairs.Count), rows.Count);
        Assert.Equal(Klee.Lines.Signature, rows[StoryLines.Key(own, StoryLines.Signature)]);
        foreach (var p in Klee.Pairs)
        {
            var partner = StoryRegistry.EntryOf(p.Partner);
            Assert.Equal(p.PartnerLine, rows[StoryLines.PairKey(own, partner, true)]);
            Assert.Equal(p.OwnLine, rows[StoryLines.PairKey(own, partner, false)]);
        }
    }

    // ---- A page change mid-exchange closes the dialogue -------------------------

    [Fact]
    public void A_clear_mid_exchange_closes_the_dialogue_and_a_last_line_clear_is_untouched()
    {
        // The game's IsDialogueOnLastLine is `current >= count - 1`.
        Assert.True(AncientDialogueClose.MidExchange(0, 2));   // greeting on line 0: close
        Assert.False(AncientDialogueClose.MidExchange(1, 2));  // last line: the base path
        Assert.False(AncientDialogueClose.MidExchange(0, 1));  // a one-line dialogue
        Assert.False(AncientDialogueClose.MidExchange(0, 0));  // nothing set

        // Every private field the patch reads resolves on the real layout.
        foreach (var f in new[]
                 {
                     AncientDialogueClose.DialogueField, AncientDialogueClose.CurrentLineField,
                     AncientDialogueClose.HitboxField, AncientDialogueClose.FakeNextField,
                     AncientDialogueClose.ContentContainerField, AncientDialogueClose.OriginalHeightField,
                 })
        {
            Assert.NotNull(f);
        }
        Assert.Equal(typeof(int), AncientDialogueClose.CurrentLineField!.FieldType);
        Assert.Equal(typeof(float), AncientDialogueClose.OriginalHeightField!.FieldType);
        Assert.True(typeof(MegaCrit.Sts2.Core.Nodes.GodotExtensions.NClickableControl)
            .IsAssignableFrom(AncientDialogueClose.HitboxField!.FieldType));

        // Structural: a prefix that reads the state and a postfix that closes.
        var patch = typeof(AncientDialogueClose).Assembly.GetTypes()
            .Single(t => t.Name == "NAncientEventLayout_ClearDialogue_Close_Patch");
        var info = patch.GetCustomAttribute<HarmonyLib.HarmonyPatch>()!.info;
        Assert.Equal(typeof(MegaCrit.Sts2.Core.Nodes.Events.NAncientEventLayout), info.declaringType);
        Assert.Equal("ClearDialogue", info.methodName);
        Assert.Contains("AncientDialogueClose.IsMidExchange",
            Il.Calls(patch.GetMethod("Prefix", HeadlessGame.All)!));
        Assert.Contains("AncientDialogueClose.Close",
            Il.Calls(patch.GetMethod("Postfix", HeadlessGame.All)!));
    }

    // ---- Helpers ---------------------------------------------------------------

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
