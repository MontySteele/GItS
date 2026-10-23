using System;
using System.Collections.Generic;
using KleeMod.Cards;
using CardRarity = MegaCrit.Sts2.Core.Entities.Cards.CardRarity;
using CardType = MegaCrit.Sts2.Core.Entities.Cards.CardType;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using Doubt = MegaCrit.Sts2.Core.Models.Cards.Doubt;

namespace KleeMod.Story;

/// <summary>
/// KOKOMI'S STORY TABLE. Every string here is the ruled paper's, word for
/// word (<c>review/active/kokomi-story-2026-10-16.md</c>, ruled 2026-10-16:
/// "I reviewed it myself and I still think it looks a bit stilted at parts,
/// but nothing that blocks it from a beta launch. ... Approved!", and "That is
/// for the story events, not the new gaps."): picks 1 (a) and 2 (a), her
/// eight events in three threads and the Public Address story curse; and
/// pick 3 (a), "Ok, I'm good to approve the full Kokomi paper as-is. The
/// dialogue looks good!": the select intro, the eight Ancients and the
/// combat lines (the Architect is <c>tools/build_pck.ps1</c>'s, the utility
/// rows <c>Kokomi.cs</c>'s). The
/// chain's shape is the story chains' (<c>review/active/klee-varka-story-chains-2026-10-14.md</c>).
/// <c>KokomiStoryTests</c> holds each one against the paper. Nothing in this
/// file is authored here.
///
/// Her pairs with Klee, Varka and Furina stay in their tables ("The three
/// co-op exchanges (Klee, Varka, Furina) stay as they are").
///
/// THE PAPER'S MARKUP. Every page is set in italics in the paper as page
/// text, not emphasis, so it carries none here; an italic word inside a
/// result ("*urgent*") is <c>[i]</c>.
/// </summary>
public static class KokomiStory
{
    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Kokomi),
        Name = "Kokomi",

        IntroTitle = "The Pearl of Wisdom.",
        IntroLine =
            "Watatsumi's priestess and strategist. She would rather solve a hard problem quietly than give a speech, and the Spire is the hardest one yet.",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "A strategist. Your mind is very busy.",
                "It usually is. You're welcome to the quiet parts, if you find any."),
            new AncientExchange("Orobas", "OROBAS",
                "Give me what you carry. I will make it stranger.",
                "Stranger is fine. Tell me what it does first."),
            new AncientExchange("Pael", "PAEL",
                "You are smaller than your ambitions.",
                "Most generals are. That's why we bring friends."),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Warm yourself by my light.",
                "Thank you. It's been a long climb, and I'll take the warmth."),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "You carry a whole island on your back.",
                "Only some days. Today it's mostly a satchel."),
            new AncientExchange("Tanx", "TANX",
                "Do you lead from the front?",
                "When I must. I'd rather stand where I can see everything."),
            new AncientExchange("Vakuu", "VAKUU",
                "Trade with me.",
                "Gladly. Show me the terms, then the small print."),
            new AncientExchange("Darv", "DARV",
                "I collect what others leave behind.",
                "Then you'd get on with quartermasters. We never throw anything away."),
        },

        Lines = new CombatLines(
            BossEntry: "So this is what holds the floor. Let's watch how it moves first.",
            LowHp: "I'm all right. Hold on a little longer.",
            Signature: "Watatsumi, rise with me.",
            BossKill: "There. I can breathe again.",
            RunLoss: "I misjudged it. I hope whoever climbs next finds my notes.",
            RunWin: "Done. Now I would very much like a quiet afternoon."),

        // "The three co-op exchanges (Klee, Varka, Furina) stay as they are",
        // in their own tables.
        Pairs = Array.Empty<PairExchange>(),

        Events = new[]
        {
            // ---- Act 1, drawn at random: one starts each thread.

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KokomiSandTable),
                Title: "The Sand Table",
                Body:
                    "A low table on the landing holds a sand map of the Spire, floor by floor, with a "
                  + "carved piece for everything that lives here. One piece is a little jellyfish. It is "
                  + "standing exactly where Kokomi is standing.",
                Options: new[]
                {
                    new StoryOption("PLAY_IT_OUT", "Play it out until the candles go out.",
                        "Lose 7 HP. Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.LoseHp, 7),
                        "She plays the next three floors four different ways and loses twice. By the end "
                      + "the candles are stubs, and she is smiling.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2) },
                    },
                    new StoryOption("MOVE_HER_PIECE", "Move her piece up one floor.",
                        "Remove a card.",
                        new StoryEffect(StoryEffectKind.RemoveCard),
                        "She moves it gently, as if it might be watching. Something in her pack feels "
                      + "lighter."),
                    new StoryOption("POCKET_THE_GENERAL", "Pocket the enemy's general.",
                        "Gain a random potion.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 1),
                        "It is a very small piece, and nobody said she couldn't."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_sand_table"),
                FallbackPortraitPath: "res://images/events/punch_off.png"),

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KokomiCoralLight),
                Title: "Coral Light",
                Body:
                    "Pale coral glows in a crack in the stone, the color of the reefs off Watatsumi. On "
                  + "afternoons the shrine let her keep for herself, she used to swim out to coral like "
                  + "this and stay until someone came looking.",
                Options: new[]
                {
                    new StoryOption("REACH_IN", "Reach in for a piece.",
                        "Lose 10 HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "The coral cuts, as coral does. She would have done it at ten as well.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic) },
                    },
                    new StoryOption("SAY_THE_SEA_PRAYER", "Kneel at the water and pray.",
                        "Lose 6 HP. Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.LoseHp, 6),
                        "The water is cold to the knee. She says the old island words softly, as fishing "
                      + "families say them before a voyage.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2) },
                    },
                    // "Locked under 50 Gold": a Gold price locks itself
                    // (StoryRules.IsLocked).
                    new StoryOption("LEAVE_A_PEARL", "Leave a pearl for it.",
                        "Lose 50 Gold. Remove a card.",
                        new StoryEffect(StoryEffectKind.LoseGold, 50),
                        "On Watatsumi you pay the sea back. She picks her best pearl.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.RemoveCard) },
                    },
                    new StoryOption("LEAVE_IT", "Leave the coral undisturbed.",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "She watches it glow for a while, then climbs on."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_coral_light"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(KokomiEmptyRoom),
                Title: "A Room with No One in It",
                Body:
                    "Behind a door with nothing written on it is a small room: one cushion, one lamp, a "
                  + "stack of unread books. Kokomi closes the door behind her. For the first time since "
                  + "the Spire began, nobody needs her to decide anything.",
                Options: new[]
                {
                    new StoryOption("TAKE_AN_HOUR", "Take an hour to herself.",
                        "Heal 15 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 15),
                        "She does nothing at all, carefully, for a whole hour."),
                    new StoryOption("READ_THE_TOP_BOOK", "Read the top book.",
                        "Choose 1 of 3 random Uncommon Powers to add to your deck.",
                        StoryEffect.Choose(CardRarity.Uncommon, CardType.Power),
                        "A treatise on naval supply. On page forty the author is wrong about tides, and "
                      + "she fills three margins explaining why."),
                    new StoryOption("PLAN_A_HOLIDAY", "Plan a holiday.",
                        "Gain a random potion.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 1),
                        "Three days off, two fallbacks, one beach. She files it under [i]urgent[/i]."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_room_with_no_one"),
                FallbackPortraitPath: "res://images/events/self_help_book.png"),

            // ---- Act 2.

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KokomiOtherCommander),
                Title: "The Other Commander",
                Body:
                    "Across another sand table sits a figure in grey with no face, its pieces in a "
                  + "patient line. It opens a hand: your move.",
                Options: new[]
                {
                    new StoryOption("PLAY_THE_FULL_GAME", "Play the full game.",
                        "Lose 12 HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 12),
                        "It takes every piece she offers, even the bad ones. She wins by one piece, hours "
                      + "later.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic) },
                    },
                    new StoryOption("OFFER_A_DRAW", "Offer a draw.",
                        "Transform a card.",
                        new StoryEffect(StoryEffectKind.TransformCards, 1),
                        "It agrees only once she offers it a piece to keep. It cannot leave a piece on "
                      + "the table."),
                    new StoryOption("CONCEDE", "Concede and study its opening.",
                        "Add [gold]Doubt[/gold] to your deck. Choose 1 of 3 random Rare cards to add to your deck.",
                        new StoryEffect(StoryEffectKind.AddCard, 0, typeof(Doubt)),
                        "She plays its first ten moves against herself until she sees it: it takes every "
                      + "piece left in reach.")
                    {
                        Then = new[] { StoryEffect.Choose(CardRarity.Rare) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_other_commander"),
                FallbackPortraitPath: "res://images/events/punch_off.png")
            {
                Follows = new[] { typeof(KokomiSandTable) },
                Openings = new[]
                {
                    new StoryOpening("PLAYED",
                        new StoryCondition(typeof(KokomiSandTable), "PLAY_IT_OUT"),
                        "She knows this floor. She has already lost on it twice, in sand."),
                    new StoryOpening("MOVED",
                        new StoryCondition(typeof(KokomiSandTable), "MOVE_HER_PIECE"),
                        "Her piece is already here. She did not move it this far."),
                    new StoryOpening("POCKETED",
                        new StoryCondition(typeof(KokomiSandTable), "POCKET_THE_GENERAL"),
                        "The general in her pocket has gone warm."),
                },
            },

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KokomiSerpentsBones),
                Title: "The Serpent's Bones",
                Body:
                    "A great curved bone is set into the wall, long as a boat, faintly purple. Every "
                  + "child on Watatsumi knows that shape: Orobashi, who brought his people up to the "
                  + "surface and later died fighting the Shogun. His remains have poisoned people before.",
                Options: new[]
                {
                    new StoryOption("LAY_A_HAND", "Lay a hand on it, through her sleeve.",
                        "Lose 8 Max HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseMaxHp, 8),
                        "She wraps her hand first and keeps the touch short; she knows what his remains "
                      + "did to Inazuma. For a moment she can feel the island he gave her people. The cold stays "
                      + "in her fingers.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic) },
                    },
                    new StoryOption("GATHER_THE_OFFERINGS", "Gather the offerings at its foot.",
                        "Gain 100 Gold. Add [gold]Doubt[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGold, 100),
                        "Someone has been leaving Mora here for a very long time. She takes it home for "
                      + "the shrine's poor box. The bone whispers to her all the way up.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(Doubt)) },
                    },
                    new StoryOption("PROMISE_A_RITE", "Promise him a rite at home.",
                        "Remove a card. Add [gold]Public Address[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.RemoveCard),
                        "A proper one, on Watatsumi, with the whole shrine there. She means every word, "
                      + "and she is already dreading the speech.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(PublicAddress)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_serpents_bones"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(KokomiCoralLight) },
                Openings = new[]
                {
                    new StoryOpening("REACHED",
                        new StoryCondition(typeof(KokomiCoralLight), "REACH_IN"),
                        "Her palm still stings where the coral cut it."),
                    new StoryOpening("PRAYED",
                        new StoryCondition(typeof(KokomiCoralLight), "SAY_THE_SEA_PRAYER"),
                        "The sea prayer is still in her mouth."),
                    new StoryOpening("PAID",
                        new StoryCondition(typeof(KokomiCoralLight), "LEAVE_A_PEARL"),
                        "She has one pearl left. She is glad she kept it."),
                },
            },

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(KokomiReportFromGorou),
                Title: "A Report from Gorou",
                Body:
                    "A Watatsumi scout is waiting on the stair, soaked to the knee, with a satchel and a "
                  + "wrapped box. \"From the General, Your Excellency. He said to wait for your answer.\" "
                  + "The letter reads: \"Drills on schedule. Fishing boats out. Bourou Village sends "
                  + "sushi. Requesting permission to send reinforcements. —Gorou. P.S. Please eat "
                  + "properly.\"",
                Options: new[]
                {
                    new StoryOption("SEND_FOR_REINFORCEMENTS", "Send for reinforcements.",
                        "Choose 1 of 3 random Uncommon Companions to add to your deck.",
                        StoryEffect.ChooseCompanion(CardRarity.Uncommon),
                        "The scout runs down the stairs with her orders. An hour later there are paw "
                      + "prints on the landing and a familiar voice calling drill."),
                    new StoryOption("WRITE_BACK", "Write back with new orders.",
                        "Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2),
                        "Three pages of orders, and a fourth telling him to rest too. The scout salutes "
                      + "and goes."),
                    new StoryOption("EAT_THE_SUSHI", "Eat the sushi while it is fresh.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20),
                        "Bird egg sushi, her favorite. Gorou remembered. She eats every piece and sends "
                      + "the box back with a thank-you."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_report_from_gorou"),
                FallbackPortraitPath: "res://images/events/potion_courier.png")
            {
                Follows = new[] { typeof(KokomiEmptyRoom) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("RESTED",
                        new StoryCondition(typeof(KokomiEmptyRoom)),
                        "Rested, she reads it properly this time."),
                },
            },

            // ---- Act 3.

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(KokomiEndgame),
                Title: "Endgame",
                Body:
                    "The faceless commander waits at the top of the stairs without its board. It has "
                  + "one piece left. So does she. The step between them is split down the middle, like "
                  + "the fold in a game board.",
                Options: new[]
                {
                    new StoryOption("OFFER_HER_LAST_PIECE", "Offer it her last piece.",
                        "Lose 18 HP. Gain a random Rare relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 18),
                        "She sets her piece on the split step. It takes the piece, as it always does, and "
                      + "the stair folds shut over it like a closing board. The jolt throws her hard "
                      + "against the wall.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRareRelic) },
                    },
                    // "Locked under 100 Gold": a Gold price locks itself.
                    new StoryOption("PAY_ITS_STAKE", "Pay its stake and trade pieces.",
                        "Lose 100 Gold. Transform 2 cards.",
                        new StoryEffect(StoryEffectKind.LoseGold, 100),
                        "It will not trade for nothing. She counts out its stake in Mora, and they trade "
                      + "their last pieces.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.TransformCards, 2) },
                    },
                    new StoryOption("BOW_AND_WALK_PAST", "Bow and walk past.",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "A commander's bow, one to another. She takes the stairs, and it does not follow."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_endgame"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(KokomiOtherCommander) },
                Openings = new[]
                {
                    new StoryOpening("PLAYED",
                        new StoryCondition(typeof(KokomiOtherCommander), "PLAY_THE_FULL_GAME"),
                        "She beat it once, by a single piece."),
                    new StoryOpening("DREW",
                        new StoryCondition(typeof(KokomiOtherCommander), "OFFER_A_DRAW"),
                        "Their game is still unfinished."),
                    new StoryOpening("CONCEDED",
                        new StoryCondition(typeof(KokomiOtherCommander), "CONCEDE"),
                        "She knows its opening by heart now."),
                },
            },

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(KokomiTideComesIn),
                Title: "The Tide Comes In",
                Body:
                    "Water rises up the stairs: real sea water, salt and cold. Kokomi feels the same "
                  + "pull she uses to shape her Bake-Kurage, and the water answers her.",
                Options: new[]
                {
                    new StoryOption("SHAPE_A_SHOAL", "Shape a whole shoal.",
                        "Lose 6 HP. Choose 1 of 3 random upgraded Uncommon Powers to add to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 6),
                        "A dozen Bake-Kurage, more than she has ever held at once. The whole stairwell "
                      + "turns blue with their light.")
                    {
                        Then = new[]
                        {
                            StoryEffect.Choose(CardRarity.Uncommon, CardType.Power, upgraded: true),
                        },
                    },
                    new StoryOption("RIDE_THE_TIDE", "Ride the tide up.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20),
                        "She lets the water carry her a floor and a half, eyes closed, like floating off "
                      + "the reef at home."),
                    new StoryOption("SEND_THE_WATER_HOME", "Send the water home to the sea.",
                        "Remove a card.",
                        new StoryEffect(StoryEffectKind.RemoveCard),
                        "She sends it down toward the sea, with a message folded into the current for "
                      + "whoever on Watatsumi is listening."),
                },
                Portrait: () => KleeArt.CardPortrait("event_kokomi_tide_comes_in"),
                FallbackPortraitPath: "res://images/events/wellspring.png")
            {
                Follows = new[] { typeof(KokomiSerpentsBones), typeof(KokomiReportFromGorou) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("BONES",
                        new StoryCondition(typeof(KokomiSerpentsBones)),
                        "The water smells of salt and incense, like the shrine on festival days."),
                    new StoryOpening("REINFORCEMENTS",
                        new StoryCondition(typeof(KokomiReportFromGorou), "SEND_FOR_REINFORCEMENTS"),
                        "Somewhere below, she can hear Gorou's soldiers singing."),
                    new StoryOpening("OTHERWISE",
                        new StoryCondition(),
                        "The water moves when she does."),
                },
            },
        },

        // "Her signature card is Nereid's Ascension", once a combat.
        SignatureCards = new[] { typeof(ProtoKkNereidsAscension) },
    };
}

/// <summary>Act 1, Kokomi only: The Sand Table (the strategist's thread).</summary>
public sealed class KokomiSandTable : StoryEventModel { }

/// <summary>Act 1, Kokomi only: Coral Light (Watatsumi's thread, a memory).</summary>
public sealed class KokomiCoralLight : StoryEventModel { }

/// <summary>Act 1, Kokomi only: A Room with No One in It (her friends' thread).</summary>
public sealed class KokomiEmptyRoom : StoryEventModel { }

/// <summary>Act 2, Kokomi only: The Other Commander.</summary>
public sealed class KokomiOtherCommander : StoryEventModel { }

/// <summary>Act 2, Kokomi only: The Serpent's Bones.</summary>
public sealed class KokomiSerpentsBones : StoryEventModel { }

/// <summary>Act 2, Kokomi only: A Report from Gorou (the home thread).</summary>
public sealed class KokomiReportFromGorou : StoryEventModel { }

/// <summary>Act 3, Kokomi only: Endgame.</summary>
public sealed class KokomiEndgame : StoryEventModel { }

/// <summary>Act 3, Kokomi only: The Tide Comes In (the home finale).</summary>
public sealed class KokomiTideComesIn : StoryEventModel { }
