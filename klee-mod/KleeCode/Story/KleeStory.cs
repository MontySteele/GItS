using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;

namespace KleeMod.Story;

/// <summary>
/// KLEE'S STORY TABLE. Every string here is the ruled paper's, word for word:
/// batch 1 (<c>review/ruled/klee-story-batch-1-2026-10-12.md</c>: the intro,
/// the eight Ancients, Starsnatch Cliff, the combat and pair lines) and batch
/// 2 (<c>review/active/klee-story-batch-2-2026-10-12.md</c>: A Letter from
/// Jean, The Knights Come Looking). <c>KleeStoryTests</c> holds each one
/// against the paper. Nothing in this file is authored here.
/// </summary>
public static class KleeStory
{
    /// <summary>Klee's answer to whichever knight she picks (batch 2, act 3).</summary>
    public const string KnightsAnswer =
        "You found me! Can we see what's at the top before we go home? Please?";

    private static string KnightsResult(string knight, string line) =>
        knight + ": \"" + line + "\"\n" + "Klee: \"" + KnightsAnswer + "\"";

    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Klee),
        Name = "Klee",

        IntroTitle = "The Spark Knight of Mondstadt.",
        IntroLine =
            "Mom says there's treasure up there! Klee packed Dodoco, some snacks, and lots of bombs. We're going all the way to the top!",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "A child. Carrying... fire.",
                "Don't worry! I haven't lit the fuse yet."),
            new AncientExchange("Orobas", "OROBAS",
                "Your trinket hums. Let me make it sing.",
                "Ooh! Can you make it go [i]boom[/i] louder?"),
            new AncientExchange("Pael", "PAEL",
                "You have bitten off more than you can chew, little one.",
                "But I haven't eaten anything! Do you have snacks?"),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Warm yourself by my light.",
                "It's so warm! Dodoco, come closer!"),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "Small hands. Many sparks.",
                "I made these myself! Mom showed me how."),
            new AncientExchange("Tanx", "TANX",
                "Do you fight for glory?",
                "I'm looking for treasure! I'll bring some back for everyone."),
            new AncientExchange("Vakuu", "VAKUU",
                "Trade with me.",
                "You can have this shiny pebble! But Dodoco stays with me."),
            new AncientExchange("Darv", "DARV",
                "I collect what others leave behind.",
                "Oh! Have you seen any little round bombs? I dropped one..."),
        },

        Lines = new CombatLines(
            BossEntry: "Whoa, look how big it is! Stand back, Dodoco!",
            LowHp: "Ow... Can we rest for a little bit?",
            Signature: "KABOOM!",
            BossKill: "We did it! Did you see, Dodoco?",
            RunLoss: "Jean... can you come get me?",
            RunWin: "I made it all the way up! Mom's gonna be so proud!"),

        Pairs = new[]
        {
            new PairExchange(typeof(Kokomi), "Kokomi",
                "Stay behind the jellyfish, Klee.",
                "Can the jellyfish carry bombs?"),
            new PairExchange(typeof(Furina), "Furina",
                "A little explosion would make a fine finale.",
                "How big? I brought lots!"),
            new PairExchange(typeof(Varka), "Varka",
                "Spark Knight. Same orders as always.",
                "No bombs indoors. ...Is this indoors?"),
        },

        Events = new[]
        {
            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KleeStarsnatchCliff),
                Title: "Starsnatch Cliff",
                Body:
                    "The pond at the foot of the cliff is full of fat, silver fish. Klee has "
                  + "three bombs left and nobody is watching. She remembers Jean's face the "
                  + "last time.",
                Options: new[]
                {
                    new StoryOption("BLAST_THE_POND", "Blast the pond!",
                        "Gain 75 Gold. Add [gold]Confinement[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGoldAddCard, 75, typeof(Confinement))),
                    new StoryOption("JUST_ONE_LITTLE_BOMB", "Just one little bomb.",
                        "Add [gold]Fish Blasting[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddCard, 0, typeof(ProtoKoFishBlasting))),
                    new StoryOption("LEAVE_THEM_BE", "Leave them be.",
                        "Remove a card from your deck.",
                        new StoryEffect(StoryEffectKind.RemoveCard)),
                },
                Portrait: () => KleeArt.CardPortrait("proto_ko_fish_fry"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KleeLetterFromJean),
                Title: "A Letter from Jean",
                Body:
                    "A Favonius pigeon lands on Klee's backpack with a letter tied to its leg. It is in Jean's "
                  + "handwriting.\n\n[i]\"Klee — Albedo told me where you went. We are coming to find you. Until "
                  + "then, stay with your friends and remember to eat. Keep your bombs away from the stairs "
                  + "and pillars. I want you home safely. — Jean, Acting Grand Master\"[/i]",
                Options: new[]
                {
                    new StoryOption("READ_IT_TWICE", "Read it twice.",
                        "Heal 15 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 15)),
                    new StoryOption("WRITE_BACK", "Write back with a promise.",
                        "Remove a Curse from your deck. If you have none, gain 50 Gold.",
                        new StoryEffect(StoryEffectKind.RemoveCurseElseGold, 50)),
                    new StoryOption("PAPER_BOMB", "Fold it into a paper bomb.",
                        "Upgrade 2 random cards that place a Bomb.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomBombCards, 2)),
                },
                Portrait: () => KleeArt.CardPortrait("proto_ko_behind_jeans_desk"),
                FallbackPortraitPath: "res://images/events/self_help_book.png"),

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(KleeKnightsComeLooking),
                Title: "The Knights Come Looking",
                Body:
                    "Klee hears her name from the stairs below. Kaeya spots her first and waves. Noelle hurries up beside him, and Albedo lets out a quiet sigh of relief.",
                Options: new[]
                {
                    new StoryOption("KAEYA", "Kaeya",
                        "Add an upgraded [gold]Kaeya — Glacial Waltz[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcKaeyaGlacialWaltz)),
                        KnightsResult("Kaeya", "There you are! Shall we finish your adventure together? Jean's waiting for us.")),
                    new StoryOption("NOELLE", "Noelle",
                        "Add an upgraded [gold]Noelle — Breastplate[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcNoelleBreastplate)),
                        KnightsResult("Noelle", "Are you hurt, Klee? Here, have something to eat. I'll stay with you.")),
                    new StoryOption("ALBEDO", "Albedo",
                        "Add an upgraded [gold]Albedo — Solar Isotoma[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcAlbedoSolarIsotoma)),
                        KnightsResult("Albedo", "I'm glad you're safe. Show me where you're going, and we'll find a way up.")),
                },
                Portrait: () => KleeArt.CardPortrait("proto_ko_favonius_escort"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png"),
        },

        BombPlacers = new HashSet<string>
        {
            "proto_ko_jumpy_dumpty",
            "proto_ko_pop",
            "proto_ko_bang_bang",
            "proto_ko_ammo_scavenging",
            "proto_ko_coven_errand",
            "proto_ko_all_of_my_treasures",
            "proto_ko_bombs_away",
            "proto_ko_witchs_homework_next",
            "proto_ko_windblume_fireworks",
            "proto_ko_fire_fire",
            "proto_ko_blasting_spree",
        },
    };
}

/// <summary>Act 1, Klee only: Starsnatch Cliff.</summary>
public sealed class KleeStarsnatchCliff : StoryEventModel
{
    protected override StoryEvent Data => KleeStory.Table.Events[0];
}

/// <summary>Act 2, Klee only: A Letter from Jean.</summary>
public sealed class KleeLetterFromJean : StoryEventModel
{
    protected override StoryEvent Data => KleeStory.Table.Events[1];
}

/// <summary>Act 3, Klee only: The Knights Come Looking.</summary>
public sealed class KleeKnightsComeLooking : StoryEventModel
{
    protected override StoryEvent Data => KleeStory.Table.Events[2];
}
