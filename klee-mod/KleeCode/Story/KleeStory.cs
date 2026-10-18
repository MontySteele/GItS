using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;

namespace KleeMod.Story;

/// <summary>
/// KLEE'S STORY TABLE. Every string here is the ruled paper's, word for word:
/// batch 1 (<c>review/ruled/klee-story-batch-1-2026-10-12.md</c>: the intro,
/// the eight Ancients, Starsnatch Cliff, the combat and pair lines) and batch
/// 2 (<c>review/active/klee-story-batch-2-2026-10-12.md</c>: A Letter from
/// Jean, The Knights Come Looking) and the story chains
/// (<c>review/active/klee-varka-story-chains-2026-10-14.md</c>, ruled
/// 2026-10-15: five new events, Starsnatch Cliff as a memory, every result
/// line and opening line). <c>KleeStoryTests</c> holds each one
/// against the paper. Nothing in this file is authored here.
/// </summary>
public static class KleeStory
{
    /// <summary>Klee's answer to whichever knight she picks (batch 2, act 3).</summary>
    public const string KnightsAnswer =
        "You found me! Can we see what's at the top before we go home? Please?";

    private static string KnightsResult(string knight, string line) =>
        knight + ": \"" + line + "\"\n" + "Klee: \"" + KnightsAnswer + "\"";

    /// <summary>Found You!: "Every option ends with Dodoco back, and removes
    /// Doubt if Klee has it."</summary>
    private static readonly StoryEffect[] DodocoHome =
    {
        new(StoryEffectKind.RemoveEvery, 0, typeof(MegaCrit.Sts2.Core.Models.Cards.Doubt)),
    };

    /// <summary>Mom's Last Note: "Saved the cache" (Alice's Cache, Save it
    /// for a real emergency).</summary>
    private static readonly StoryCondition SavedTheCache = new(typeof(KleeAlicesCache), "SAVE_IT");

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
                    "A still pool in the Spire's stone is full of fat, silver fish. It looks just like the "
                  + "pond below Starsnatch Cliff, back home. Klee has three bombs left and nobody is "
                  + "watching. She remembers Jean's face the last time.",
                Options: new[]
                {
                    new StoryOption("BLAST_THE_POND", "Blast the pond!",
                        "Gain 75 Gold. Add [gold]Confinement[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGoldAddCard, 75, typeof(Confinement)),
                        "KABOOM! Fish everywhere. Klee hopes the Spire doesn't tell Jean."),
                    new StoryOption("JUST_ONE_LITTLE_BOMB", "Just one little bomb.",
                        "Add [gold]Fish Blasting[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddCard, 0, typeof(ProtoKoFishBlasting)),
                        "Just a little one. Klee keeps the biggest fish for Dodoco."),
                    new StoryOption("LEAVE_THEM_BE", "Leave them be.",
                        "Remove a card from your deck.",
                        new StoryEffect(StoryEffectKind.RemoveCard),
                        "Klee puts the fuse away and watches the fish swim past."),
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_starsnatch_cliff"),
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
                        new StoryEffect(StoryEffectKind.Heal, 15),
                        "Klee reads it twice, then a third time. She tucks it in next to Dodoco."),
                    new StoryOption("WRITE_BACK", "Write back with a promise.",
                        "Remove a Curse from your deck. If you have none, gain 50 Gold.",
                        new StoryEffect(StoryEffectKind.RemoveCurseElseGold, 50),
                        "Dear Jean, I will be good. Mostly. Love, Klee."),
                    new StoryOption("PAPER_BOMB", "Fold it into a paper bomb.",
                        "Upgrade 2 random cards that place a Bomb.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomBombCards, 2),
                        "It folds into a perfect little bomb. Jean won't mind. Probably."),
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_letter_from_jean"),
                FallbackPortraitPath: "res://images/events/self_help_book.png")
            {
                Follows = new[] { typeof(KleeStarsnatchCliff) },
                Home = true,
            },

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
                    new StoryOption("EVERYONE_CAN_COME", "Everyone can come!",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "Klee: \"You can all come! Dodoco, make room!\" Three knights fall in behind her, "
                      + "trying very hard to look like they were planning to anyway."),
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_knights_come_looking"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(KleeLetterFromJean), typeof(KleeFoundYou) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("DODOCO_THREAD",
                        new StoryCondition(Fired: typeof(KleeFoundYou)),
                        "Dodoco rides on Klee's shoulder the whole way."),
                    new StoryOpening("DODOCO_FOUND",
                        new StoryCondition(Fired: typeof(KleeDodocoGoesMissing), NoEventInAct: 1),
                        "A knight holds out something small and a little sticky. \"Found this on the "
                      + "stairs below. Is it yours?\" It's Dodoco.",
                        RemovesOnOpen: typeof(MegaCrit.Sts2.Core.Models.Cards.Doubt)),
                },
            },

            // ---- The story chains (review/active/klee-varka-story-chains-2026-10-14.md)

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KleeDodocoGoesMissing),
                Title: "Dodoco Goes Missing",
                Body:
                    "Klee wakes up from a nap on the landing. Her backpack is open, and Dodoco is gone. "
                  + "Small sticky footprints lead away up the stairs, past a trail of Klee's snack crumbs.",
                Options: new[]
                {
                    new StoryOption("CHASE_IT", "Chase it right now!",
                        "Lose 10 HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "Klee trips twice and lands on somebody's lost treasure. The thief gets away, "
                      + "but Klee knows which way it went.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic) },
                    },
                    new StoryOption("LEAVE_MORA_AS_BAIT", "Leave Mora out as bait.",
                        "Lose 50 Gold. Remove a card.",
                        new StoryEffect(StoryEffectKind.LoseGold, 50),
                        "By morning the Mora is gone, and so is a bit of junk from her bag. The sticky "
                      + "footprints go up.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.RemoveCard) },
                    },
                    new StoryOption("WAIT_HERE", "Wait here in case Dodoco comes back.",
                        "Heal 15 HP. Add [gold]Doubt[/gold].",
                        new StoryEffect(StoryEffectKind.Heal, 15),
                        "Klee waits and waits. Dodoco doesn't come back. She worries all the way up.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(MegaCrit.Sts2.Core.Models.Cards.Doubt)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_dodoco_goes_missing"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KleeFoundYou),
                Title: "Found You!",
                Body:
                    "The sticky footprints end at a nest of stolen things: buttons, a boot, half a "
                  + "sandwich. On top sits Dodoco. A small round creature with far too many eyes is "
                  + "hugging it.",
                Options: new[]
                {
                    new StoryOption("ASK_NICELY", "Ask nicely for Dodoco back.",
                        "Add an upgraded [gold]Dodoco Tag[/gold].",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKoDodocoTag)),
                        "Klee trades it her last snack. Dodoco is a little sticky, but fine.")
                    {
                        Then = DodocoHome,
                    },
                    new StoryOption("GRAB_AND_RUN", "Grab Dodoco and some treasure, and run!",
                        "Lose 8 HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 8),
                        "It bites. Klee doesn't let go of either.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic), DodocoHome[0] },
                    },
                    new StoryOption("SWAP_HER_BEST_BOMB", "Swap her best bomb for Dodoco.",
                        "Transform a card.",
                        new StoryEffect(StoryEffectKind.TransformCards, 1),
                        "It gives her a rock in return. Klee keeps the rock.")
                    {
                        Then = DodocoHome,
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_found_you"),
                FallbackPortraitPath: "res://images/events/self_help_book.png")
            {
                Follows = new[] { typeof(KleeDodocoGoesMissing) },
                Openings = new[]
                {
                    new StoryOpening("CHASED",
                        new StoryCondition(typeof(KleeDodocoGoesMissing), "CHASE_IT"),
                        "Klee knows this trail. She ran most of it."),
                    new StoryOpening("BAIT",
                        new StoryCondition(typeof(KleeDodocoGoesMissing), "LEAVE_MORA_AS_BAIT"),
                        "Klee's Mora is in the nest too."),
                    new StoryOpening("WAITED",
                        new StoryCondition(typeof(KleeDodocoGoesMissing), "WAIT_HERE"),
                        "Klee has been worried the whole way up."),
                },
            },

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KleeMomsMarks),
                Title: "Mom's Marks",
                Body:
                    "Scratched into a pillar, at exactly Klee's height: a little bomb, a star, and "
                  + "\"Alice was here! ♪\". More marks lead upward, and beside them a recipe.",
                Options: new[]
                {
                    new StoryOption("FOLLOW_THE_MARKS", "Follow Mom's marks.",
                        "Gain 75 Gold.",
                        new StoryEffect(StoryEffectKind.GainGold, 75),
                        "The marks lead to a little pouch of Mora. Mom always leaves snack money."),
                    new StoryOption("TRY_THE_RECIPE", "Try the recipe right now.",
                        "Lose 10 HP. Add [gold]Alice's Recipe[/gold].",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "It works! Klee's eyebrows will grow back.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(ProtoKoAlicesRecipe)) },
                    },
                    new StoryOption("ADD_A_MARK", "Add a mark of her own.",
                        "Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2),
                        "A bomb, a star, and \"Klee was here too!\""),
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_moms_marks"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KleeAlicesCache),
                Title: "Alice's Cache",
                Body:
                    "At the end of Mom's marks is a little chest with a note: \"For my darling Klee. "
                  + "Open in an emergency only! It's a bit lively, so stand back. And don't tell Jean. ♪\" "
                  + "The chest is ticking.",
                Options: new[]
                {
                    new StoryOption("OPEN_IT", "It's an emergency! Open it!",
                        "Lose 15 HP. Gain a random Rare relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 15),
                        "KABOOM. Mom wasn't joking about lively. Inside, wrapped in fireproof cloth, is "
                      + "something wonderful.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRareRelic) },
                    },
                    new StoryOption("SAVE_IT", "Save it for a real emergency.",
                        "Lose 5 HP. Gain a random potion.",
                        new StoryEffect(StoryEffectKind.LoseHp, 5),
                        "The chest sputters at her the whole way up. Klee carries it very, very carefully.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomPotions, 1) },
                    },
                    new StoryOption("LEAVE_IT", "Leave it for the next adventurer.",
                        "Lose 50 Gold. Transform 2 cards.",
                        new StoryEffect(StoryEffectKind.LoseGold, 50),
                        "Klee swaps in two of her own bombs, and some Mora for luck. Fair's fair.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.TransformCards, 2) },
                    },
                    new StoryOption("BACK_AWAY", "Back away from the ticking.",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "Klee tiptoes backwards all the way to the stairs. Dodoco keeps watch."),
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_alices_cache"),
                FallbackPortraitPath: "res://images/events/self_help_book.png")
            {
                Follows = new[] { typeof(KleeMomsMarks) },
            },

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(KleeMomsLastNote),
                Title: "Mom's Last Note",
                Body:
                    "Pinned to the last landing with a tiny bomb-shaped pin is one more note in Mom's handwriting.",
                Options: new[]
                {
                    new StoryOption("READ_IT_OUT_LOUD", "Read it out loud to Dodoco.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20),
                        "\"...and I'll see you in Mondstadt. Love, Mom.\" Klee reads it twice."),
                    new StoryOption("TRY_THE_TRICK", "Try the trick on the back.",
                        "Lose 10 HP. Add an upgraded [gold]Alice's Introduction Magic[/gold].",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "On the fifth try, it works. \"I did it, Dodoco! Let's do it again!\"")
                    {
                        Then = new[]
                        {
                            new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoKoAlicesIntroductionMagic)),
                        },
                    },
                    new StoryOption("OPEN_THE_CHEST", "Open the chest at last.",
                        "Gain a random Rare relic.",
                        new StoryEffect(StoryEffectKind.GainRandomRareRelic),
                        "Klee sets the chest down and opens it at arm's length, just like Mom said.")
                    {
                        ShownIf = SavedTheCache,
                    },
                    new StoryOption("FOLD_INTO_A_FUSE", "Fold the note into a fuse.",
                        "Upgrade 3 random cards that place a Bomb.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomBombCards, 3),
                        "The ink burns blue. Klee saves a scrap for later.")
                    {
                        ShownIf = SavedTheCache with { Not = true },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_klee_moms_last_note"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(KleeAlicesCache) },
                Openings = new[]
                {
                    new StoryOpening("OPENED",
                        new StoryCondition(typeof(KleeAlicesCache), "OPEN_IT"),
                        "\"You opened it, didn't you? Of course you did. Was it a real emergency? (It always is.)\""),
                    new StoryOpening("SAVED",
                        new StoryCondition(typeof(KleeAlicesCache), "SAVE_IT"),
                        "\"You didn't open it? My sensible little spark! Go on, open it now. You've earned it.\""),
                    new StoryOpening("LEFT",
                        new StoryCondition(typeof(KleeAlicesCache), "LEAVE_IT"),
                        "\"You left it for someone else? You're kinder than I ever was. ♪\""),
                    new StoryOpening("NO_CACHE",
                        new StoryCondition(),
                        "\"I knew you'd make it this far.\""),
                },
            },
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
public sealed class KleeStarsnatchCliff : StoryEventModel { }

/// <summary>Act 2, Klee only: A Letter from Jean (the home thread).</summary>
public sealed class KleeLetterFromJean : StoryEventModel { }

/// <summary>Act 3, Klee only: The Knights Come Looking (the home finale).</summary>
public sealed class KleeKnightsComeLooking : StoryEventModel { }

/// <summary>Act 1, Klee only: Dodoco Goes Missing.</summary>
public sealed class KleeDodocoGoesMissing : StoryEventModel { }

/// <summary>Act 2, Klee only: Found You!</summary>
public sealed class KleeFoundYou : StoryEventModel { }

/// <summary>Act 1, Klee only: Mom's Marks.</summary>
public sealed class KleeMomsMarks : StoryEventModel { }

/// <summary>Act 2, Klee only: Alice's Cache.</summary>
public sealed class KleeAlicesCache : StoryEventModel { }

/// <summary>Act 3, Klee only: Mom's Last Note.</summary>
public sealed class KleeMomsLastNote : StoryEventModel { }
