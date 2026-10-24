using KleeMod.Cards;
using CardRarity = MegaCrit.Sts2.Core.Entities.Cards.CardRarity;
using CardType = MegaCrit.Sts2.Core.Entities.Cards.CardType;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using Doubt = MegaCrit.Sts2.Core.Models.Cards.Doubt;

namespace KleeMod.Story;

/// <summary>
/// FURINA'S STORY TABLE. Every string here is the ruled paper's, word for
/// word (<c>review/active/furina-story-2026-10-15.md</c>, ruled 2026-10-15:
/// "I like the Furina event PR! Approved!", all three picks (a) with both
/// voice passes): the select intro, the eight Ancients, her eight events in
/// three threads, the combat and pair lines. The chain's shape is the story
/// chains' (<c>review/active/klee-varka-story-chains-2026-10-14.md</c>).
/// <c>FurinaStoryTests</c> holds each one against the paper. Nothing in this
/// file is authored here. Her pairs with Klee and Varka are in their tables
/// (<see cref="StoryRules.BossEntryPlan"/> finds them from either).
///
/// THE PAPER'S MARKUP. A whole act-1 page is set in italics in the paper as
/// page text, not emphasis, so it carries none here; an italic phrase inside
/// a page (the Oratrice's plate) is <c>[i]</c>. A narrated opening that
/// quotes speech in single quotes in the paper speaks it in double quotes
/// here, the chains' convention.
/// </summary>
public static class FurinaStory
{
    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Furina),
        Name = "Furina",

        IntroTitle = "The Regina of All Waters.",
        IntroLine =
            "She played a god for five hundred years and was very good at it. Now she chooses her own roles, and the Spire is the biggest stage she has ever seen.",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "A performer. How bright you burn.",
                "Oh! Well. Thank you. Do you say that to everyone?"),
            new AncientExchange("Orobas", "OROBAS",
                "Your trinket hums. Let me make it sing.",
                "As long as it's in tune. I'll know if it isn't."),
            new AncientExchange("Pael", "PAEL",
                "You have bitten off more than you can chew.",
                "Did anyone ask you? No. I didn't think so."),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Warm yourself by my light.",
                "That's... actually very kind. Thank you."),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "You wear a crown you set down.",
                "I set it down on purpose. My neck is much happier."),
            new AncientExchange("Tanx", "TANX",
                "Do you fight for glory?",
                "Glory? Please. Have you read my reviews?"),
            new AncientExchange("Vakuu", "VAKUU",
                "Trade with me.",
                "Show me what you have. And don't tell me it's priceless; everyone says that."),
            new AncientExchange("Darv", "DARV",
                "I collect what others leave behind.",
                "You'd have loved the Palais's lost property office."),
        },

        Lines = new CombatLines(
            BossEntry: "So you're the headliner? Fine. Let's see who they came to see.",
            LowHp: "I'm fine! I'm... fine. Keep going.",
            Signature: "Let the people rejoice!",
            BossKill: "Ha! Did you see that? Tell me someone saw that.",
            RunLoss: "So that's the ending. I really thought there'd be another act.",
            RunWin: "Curtain! Now, who's writing the review?"),

        Pairs = new[]
        {
            new PairExchange(typeof(Kokomi), "Kokomi",
                "Only one, please. On my signal.",
                "A strategist! Do you need a dramatic entrance? I have several.",
                OwnFirst: true),
            new PairExchange(typeof(Yae), "Yae",
                "Smile for the readers, Furina. You're in next month's issue.",
                "Only if I get the cover."),
        },

        Events = new[]
        {
            // ---- Act 1, drawn at random: one starts each thread.

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(FurinaEmptyHouse),
                Title: "An Empty House",
                Body:
                    "A theater stands on this landing, impossibly: red velvet rows and not one seat taken. "
                  + "As Furina walks in, the stage lights come up, as if they had been waiting for her. "
                  + "She straightens before she can stop herself.",
                Options: new[]
                {
                    new StoryOption("PERFORM_FOR_NO_ONE", "Perform for no one.",
                        "Lose 8 HP. Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.LoseHp, 8),
                        "She plays every part and finally lands the high note in the second act. Nobody "
                      + "claps. She bows anyway, and makes a note about the lighting.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2) },
                    },
                    new StoryOption("SIT_IN_THE_FRONT_ROW", "Sit in the front row.",
                        "Heal 10 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 10),
                        "She has never actually sat out here. The seats are softer than she thought. She "
                      + "stays until her feet stop aching."),
                    new StoryOption("TAKE_A_COSTUME", "Take a costume from the rack.",
                        "Gain a random relic. Add [gold]Doubt[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainRandomRelic),
                        "It fits perfectly. She would very much like to know who took her measurements.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(Doubt)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_empty_house"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png"),

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(FurinaRisingWater),
                Title: "Rising Water",
                Body:
                    "Water is creeping up the stairs, ankle-deep and rising. Furina stops dead. For five "
                  + "hundred years she waited for exactly this, and smiled at everyone the whole time.",
                Options: new[]
                {
                    new StoryOption("RUN_FOR_THE_STAIRS", "Run for the stairs.",
                        "Lose 10 HP. Remove a card.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "She takes the stairs two at a time until they are dry and she can't breathe. "
                      + "Whatever she dropped on the way, she doesn't go back for it.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.RemoveCard) },
                    },
                    new StoryOption("STAND_IN_IT", "Stand in it until it stops.",
                        "Add [gold]Doubt[/gold] to your deck. Upgrade 3 random cards.",
                        new StoryEffect(StoryEffectKind.AddCard, 0, typeof(Doubt)),
                        "\"It's over. It's been over for ages,\" she tells the water. It stops at her knees. "
                      + "She waits a long time anyway, to be sure.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.UpgradeRandomCards, 3) },
                    },
                    new StoryOption("HUM_THE_OVERTURE", "Hum the overture and wade on.",
                        "Gain 75 Gold. Add [gold]Stage Fright[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGold, 75),
                        "She hums all the way across, loudly. There are coins in the water, like at the "
                      + "Fountain of Lucine, and she takes a handful for luck. Her hands shake for an hour.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(StageFright)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_rising_water"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(FurinaSteambirdClipping),
                Title: "A Steambird Clipping",
                Body:
                    "An envelope is tucked under a stone on the landing, addressed in Charlotte's hand. "
                  + "Inside is a page of The Steambird, folded to the reviews, one circled in red: \"Former "
                  + "Archon Steals the Show.\" In the margin: \"Sequel when? And I'm still waiting on that "
                  + "interview! —C.\"",
                Options: new[]
                {
                    new StoryOption("READ_IT_ALOUD", "Read it aloud, twice.",
                        "Heal 12 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 12),
                        "She does all the voices, Charlotte's included. On the second reading she adds the "
                      + "exclamation marks Charlotte left out."),
                    new StoryOption("CAST_THE_SEQUEL", "Cast the sequel in the margin.",
                        "Choose 1 of 3 random Guest Stars to add to your deck.",
                        new StoryEffect(StoryEffectKind.ChooseFromPoolToDeck, 3),
                        "Lead: Furina. Then a part for everyone she can think of. Charlotte gets a cameo, "
                      + "as a reporter, which serves her right."),
                    new StoryOption("FOLD_IT_INTO_HER_GLOVE", "Fold it into her glove.",
                        "Gain a random potion.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 1),
                        "Folded along the old creases. She'll want it for the next person who doubts her."),
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_steambird_clipping"),
                FallbackPortraitPath: "res://images/events/self_help_book.png"),

            // ---- Act 2.

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(FurinaUnderstudy),
                Title: "The Understudy",
                Body:
                    "A smaller stage, and someone on it: a girl in a copy of Furina's old costume, saying "
                  + "the lines a beat late. She sees Furina and freezes. \"I'm only the understudy. Nobody "
                  + "told me how it ends.\"",
                Options: new[]
                {
                    new StoryOption("TEACH_HER_THE_ENDING", "Teach her the ending.",
                        "Lose 6 HP. Choose 1 of 3 random upgraded Uncommon cards to add to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 6),
                        "\"You bow on the last note, not after. Chin up. Hands where they can see them. No, "
                      + "like this.\" By the fifth try the girl has it. \"Are you ever scared?\" \"Again. "
                      + "From the top.\"")
                    {
                        Then = new[]
                        {
                            StoryEffect.Choose(CardRarity.Uncommon, upgraded: true),
                        },
                    },
                    new StoryOption("TAKE_THE_ROLE_BACK", "Take the role back.",
                        "Remove a card. Add [gold]Stage Fright[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.RemoveCard),
                        "The girl hurries off, relieved. Furina takes her mark. She knows every line, and "
                      + "the first one still comes out a beat late.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(StageFright)) },
                    },
                    new StoryOption("LET_HER_IMPROVISE", "Let her improvise.",
                        "Gain 50 Gold.",
                        new StoryEffect(StoryEffectKind.GainGold, 50),
                        "Her ending is completely wrong and the empty seats love it. Furina laughs so hard "
                      + "she has to sit down."),
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_understudy"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(FurinaEmptyHouse) },
                Openings = new[]
                {
                    new StoryOpening("PERFORMED",
                        new StoryCondition(typeof(FurinaEmptyHouse), "PERFORM_FOR_NO_ONE"),
                        "Her voice is still a little hoarse from the empty theater."),
                    new StoryOpening("FRONT_ROW",
                        new StoryCondition(typeof(FurinaEmptyHouse), "SIT_IN_THE_FRONT_ROW"),
                        "She still remembers how soft those seats were."),
                    new StoryOpening("COSTUME",
                        new StoryCondition(typeof(FurinaEmptyHouse), "TAKE_A_COSTUME"),
                        "The costume still fits. She still wishes it didn't."),
                },
            },

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(FurinaOratricesEcho),
                Title: "The Oratrice's Echo",
                Body:
                    "A machine of brass and glass hangs over the landing, its scale swinging. It isn't the "
                  + "Oratrice. It only looks like it, the way a bad dream looks like a room you know. A "
                  + "plate reads: [i]State your case.[/i]",
                Options: new[]
                {
                    new StoryOption("PLEAD_GUILTY", "Plead guilty.",
                        "Lose 12 HP. Gain a random relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 12),
                        "\"I lied to everyone for five hundred years.\" A pause. \"And it kept them alive.\" "
                      + "The scale tips, and something drops into the tray.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRelic) },
                    },
                    new StoryOption("PLEAD_INNOCENT", "Plead innocent.",
                        "Heal 15 HP. Add [gold]Stage Fright[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.Heal, 15),
                        "\"I did what I had to, and it worked.\" The scale doesn't move. \"Well? Say "
                      + "something.\" This copy never could decide anything by itself.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(StageFright)) },
                    },
                    new StoryOption("GIVE_IT_A_PERFORMANCE", "Give it a performance.",
                        "Lose 100 Gold. Transform 2 cards.",
                        new StoryEffect(StoryEffectKind.LoseGold, 100),
                        "There is a slot for an admission fee. She pays, under protest, then gives it the "
                      + "old monologue from the top. It's still good. The machine hands back something new.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.TransformCards, 2) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_oratrices_echo"),
                FallbackPortraitPath: "res://images/events/punch_off.png")
            {
                Follows = new[] { typeof(FurinaRisingWater) },
                Openings = new[]
                {
                    new StoryOpening("RAN",
                        new StoryCondition(typeof(FurinaRisingWater), "RUN_FOR_THE_STAIRS"),
                        "Her lungs still ache from the stairs."),
                    new StoryOpening("STOOD",
                        new StoryCondition(typeof(FurinaRisingWater), "STAND_IN_IT"),
                        "Her shoes are still wet."),
                    new StoryOpening("HUMMED",
                        new StoryCondition(typeof(FurinaRisingWater), "HUM_THE_OVERTURE"),
                        "The overture is stuck in her head."),
                },
            },

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(FurinaLetterFromTheCourt),
                Title: "A Letter from the Court",
                Body:
                    "A Melusine in a Palais courier's cap is waiting on the step, holding a very neatly "
                  + "addressed letter. \"I'm to wait for your reply, Miss Furina.\" The letter reads: "
                  + "\"Miss Furina. The Court notes your absence. The Court also notes that Café Lutèce has "
                  + "not sold a single La Lettre à Focalors in some weeks, and is concerned. N.\"",
                Options: new[]
                {
                    new StoryOption("WRITE_BACK_AT_LENGTH", "Write back at length.",
                        "Upgrade a card.",
                        new StoryEffect(StoryEffectKind.UpgradeChosenCard),
                        "Four pages: the stairs (too many), the lighting (dreadful), a very rude Ancient, "
                      + "and the cake situation, which she considers urgent. The courier tucks it away "
                      + "carefully."),
                    new StoryOption("ORDER_THE_CAKE", "Order the cake anyway.",
                        "Lose 40 Gold. Heal 25 HP.",
                        new StoryEffect(StoryEffectKind.LoseGold, 40),
                        "She sends the courier off with the Mora and an order. On the next landing a box "
                      + "from Café Lutèce is waiting, still cold. She eats the whole thing on the stairs.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.Heal, 25) },
                    },
                    new StoryOption("KEEP_IT", "Keep it for a hard night.",
                        "Choose 1 of 3 random Common Skills to add to your deck.",
                        StoryEffect.Choose(CardRarity.Common, CardType.Skill),
                        "\"Tell him I'll write.\" She reads it again on every landing."),
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_letter_from_the_court"),
                FallbackPortraitPath: "res://images/events/potion_courier.png")
            {
                Follows = new[] { typeof(FurinaSteambirdClipping) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("READ",
                        new StoryCondition(typeof(FurinaSteambirdClipping), "READ_IT_ALOUD"),
                        "She is still doing Charlotte's voice under her breath."),
                    new StoryOpening("CAST",
                        new StoryCondition(typeof(FurinaSteambirdClipping), "CAST_THE_SEQUEL"),
                        "The cast list in the margin keeps growing."),
                    new StoryOpening("KEPT",
                        new StoryCondition(typeof(FurinaSteambirdClipping), "FOLD_IT_INTO_HER_GLOVE"),
                        "The clipping is still in her glove."),
                },
            },

            // ---- Act 3.

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(FurinaCurtainCall),
                Title: "Curtain Call",
                Body:
                    "The last stage. Every seat is full, and every face is someone she knew in Fontaine, "
                  + "or nearly. They have been waiting for her a long time.",
                Options: new[]
                {
                    new StoryOption("GIVE_THEM_THE_FINALE", "Give them the finale.",
                        "Lose 10 HP. Choose 1 of 3 random upgraded Rare cards to add to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "Halfway through she changes the ending, because she has a better one. The "
                      + "orchestra, somehow, follows her.")
                    {
                        Then = new[]
                        {
                            StoryEffect.Choose(CardRarity.Rare, upgraded: true),
                        },
                    },
                    new StoryOption("BOW_AND_LEAVE", "Bow and leave them wanting more.",
                        "Heal 30 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 30),
                        "One proper bow, and off while they're still clapping. Someone in the wings is "
                      + "grinning at her."),
                    new StoryOption("ASK_FOR_AN_ENCORE", "Ask them to stay for an encore.",
                        "Upgrade 3 random cards. Add [gold]Stage Fright[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 3),
                        "They stay. Her heart is pounding. She sends the orchestra back to the top twice, "
                      + "because the tempo is wrong.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(StageFright)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_curtain_call"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(FurinaUnderstudy) },
                Openings = new[]
                {
                    new StoryOpening("TAUGHT",
                        new StoryCondition(typeof(FurinaUnderstudy), "TEACH_HER_THE_ENDING"),
                        "A note from the understudy: \"I bowed on the last note!\""),
                    new StoryOpening("TOOK_THE_ROLE",
                        new StoryCondition(typeof(FurinaUnderstudy), "TAKE_THE_ROLE_BACK"),
                        "She knows the role by heart now, the understudy's lines too."),
                    new StoryOpening("IMPROVISED",
                        new StoryCondition(typeof(FurinaUnderstudy), "LET_HER_IMPROVISE"),
                        "She still laughs about that ending."),
                },
            },

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(FurinaEmptyThrone),
                Title: "An Empty Throne",
                Body:
                    "At the top of the stairs is a throne over still water: the one from the prophecy, "
                  + "where the Archon was to sit weeping after everyone else was gone. It is empty. A seat "
                  + "for one.",
                Options: new[]
                {
                    new StoryOption("SIT_IN_IT", "Sit in it one last time.",
                        "Lose 18 HP. Gain a random Rare relic.",
                        new StoryEffect(StoryEffectKind.LoseHp, 18),
                        "Just as cold as she remembers. She tells herself she won't cry, and then she does.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.GainRandomRareRelic) },
                    },
                    new StoryOption("WALK_PAST_IT", "Walk past it.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20),
                        "\"No, thank you,\" she says, as if it had offered, and keeps climbing."),
                    new StoryOption("BREAK_IT", "Break it.",
                        "Lose 8 HP. Remove a card. Remove every [gold]Doubt[/gold].",
                        new StoryEffect(StoryEffectKind.LoseHp, 8),
                        "It shatters like a stage prop, because that's all this one is.")
                    {
                        Then = new[]
                        {
                            new StoryEffect(StoryEffectKind.RemoveCard),
                            new StoryEffect(StoryEffectKind.RemoveEvery, 0, typeof(Doubt)),
                        },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_furina_empty_throne"),
                FallbackPortraitPath: "res://images/events/wellspring.png")
            {
                Follows = new[] { typeof(FurinaOratricesEcho), typeof(FurinaLetterFromTheCourt) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("GUILTY",
                        new StoryCondition(typeof(FurinaOratricesEcho), "PLEAD_GUILTY"),
                        "She has said it out loud once now."),
                    new StoryOpening("INNOCENT",
                        new StoryCondition(typeof(FurinaOratricesEcho), "PLEAD_INNOCENT"),
                        "She is still annoyed with that scale."),
                    new StoryOpening("PERFORMED",
                        new StoryCondition(typeof(FurinaOratricesEcho), "GIVE_IT_A_PERFORMANCE"),
                        "She has run out of old monologues."),
                    new StoryOpening("LETTER",
                        new StoryCondition(typeof(FurinaLetterFromTheCourt)),
                        "The letter is in her glove."),
                },
            },
        },

        // "Her full Spend": Let the People Rejoice, the card her Burst line
        // is named for, once a combat.
        SignatureCards = new[] { typeof(ProtoFsLetThePeopleRejoice) },
        ChoicePool = FurinaCards.GuestStars,
    };
}

/// <summary>Act 1, Furina only: An Empty House (the stage thread).</summary>
public sealed class FurinaEmptyHouse : StoryEventModel { }

/// <summary>Act 1, Furina only: Rising Water (the prophecy thread, a memory).</summary>
public sealed class FurinaRisingWater : StoryEventModel { }

/// <summary>Act 1, Furina only: A Steambird Clipping (her friends' thread).</summary>
public sealed class FurinaSteambirdClipping : StoryEventModel { }

/// <summary>Act 2, Furina only: The Understudy.</summary>
public sealed class FurinaUnderstudy : StoryEventModel { }

/// <summary>Act 2, Furina only: The Oratrice's Echo.</summary>
public sealed class FurinaOratricesEcho : StoryEventModel { }

/// <summary>Act 2, Furina only: A Letter from the Court (the home thread).</summary>
public sealed class FurinaLetterFromTheCourt : StoryEventModel { }

/// <summary>Act 3, Furina only: Curtain Call.</summary>
public sealed class FurinaCurtainCall : StoryEventModel { }

/// <summary>Act 3, Furina only: An Empty Throne (the home finale).</summary>
public sealed class FurinaEmptyThrone : StoryEventModel { }
