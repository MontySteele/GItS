using KleeMod.Cards;
using CardRarity = MegaCrit.Sts2.Core.Entities.Cards.CardRarity;
using CardType = MegaCrit.Sts2.Core.Entities.Cards.CardType;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;

namespace KleeMod.Story;

/// <summary>
/// VARKA'S STORY TABLE. Every string here is the ruled paper's, word for word
/// (<c>review/active/varka-story-2026-10-13.md</c>: the intro, the eight
/// Ancients, Dispatch from Mondstadt, The Wolf of the North, The Long Way
/// Home, the combat and pair lines; ruled "Sounds good! Let's go with it.")
/// and the story chains (<c>review/active/klee-varka-story-chains-2026-10-14.md</c>,
/// ruled 2026-10-15: five new events, every result line, opening line and
/// reunion reply).
/// <c>VarkaStoryTests</c> holds each one against the paper. Nothing in this
/// file is authored here. His pair with Klee is in Klee's table (written with
/// her batch); <see cref="StoryRules.BossEntryPlan"/> finds it from either.
/// </summary>
public static class VarkaStory
{
    /// <summary>His reply to each knight who steps out (the story chains:
    /// "The Long Way Home's reunion replies become one per knight").</summary>
    public const string EulaAnswer = "Tomorrow. After I've slept. I won't go easy.";

    public const string NoelleAnswer = "It's yours. I'll be right behind you.";

    public const string DilucAnswer = "Tell them to bring up the good bottle. The one you hide.";

    /// <summary>Varka's line on the skip (sec.5, "Wave them back to the column.").</summary>
    public const string WaveBackLine = "Stay with the others. I'll meet you all at the foot of the stairs.";

    private static string HomeResult(string knight, string line, string answer) =>
        knight + ": \"" + line + "\"\n" + "Varka: \"" + answer + "\"";

    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Varka),
        Name = "Varka",

        IntroTitle = "The Grand Master of the Knights of Favonius.",
        IntroLine =
            "He led the Knights north against the Abyss, leaving Mondstadt in Jean's care. The Abyss's trail runs up the Spire, so up he goes.",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "[sine]...knight...\n..will you go... ..up...?[/sine]",
                "Up, then home. My people are waiting."),
            new AncientExchange("Orobas", "OROBAS",
                "Big knight! Big pack! What inside? Show!!",
                "Rations, mostly. And a few things worth more than they look."),
            new AncientExchange("Pael", "PAEL",
                "[thinky_dots]So many walk behind you...\nLet my strength carry some of them...[/thinky_dots]",
                "I'll take it. They're heavier than they look."),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Such a big strong boy! Eat something. Can't climb on an empty stomach!",
                "Now that's an order I can follow."),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "That armor has seen better days. Come forth, knight, and be made splendid.",
                "Splendid's fine. Sturdy's better."),
            new AncientExchange("Tanx", "TANX",
                "TWO SWORDS! NOW THAT IS MORE LIKE IT!!",
                "Ha! I knew you'd approve."),
            new AncientExchange("Vakuu", "VAKUU",
                "You realize your knights may [sine]never[/sine] see home?",
                "They will. Name your price, and keep it honest."),
            new AncientExchange("Darv", "DARV",
                "Grand Master! Got just the thing for ya... somewhere in here...",
                "Got a whetstone in there? Mine's about worn through."),
        },

        Lines = new CombatLines(
            BossEntry: "Well, you're a big one! Let's make some room.",
            LowHp: "Easy now. I've got another round in me.",
            Signature: "By Lord Barbatos!",
            BossKill: "Someone write that down. Not me!",
            RunLoss: "Tell Jean... we're running a little late.",
            RunWin: "Knights of Favonius, we're going home!"),

        Pairs = new[]
        {
            new PairExchange(typeof(Kokomi), "Kokomi",
                "I see it. Go ahead; I'll cover you.",
                "See that gap on the left? Bet I can get us through.",
                OwnFirst: true),
            new PairExchange(typeof(Furina), "Furina",
                "The Grand Master himself! Do try not to upstage me.",
                "Wouldn't dream of it."),
        },

        Events = new[]
        {
            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(VarkaDispatchFromMondstadt),
                Title: "Dispatch from Mondstadt",
                Body:
                    "A Favonius courier catches up with Varka on the stairs, out of breath, a "
                  + "satchel of reports under one arm. \"From the Acting Grand Master, sir. She "
                  + "says you'll know which ones.\"",
                Options: new[]
                {
                    new StoryOption("SIGN_EVERY_ONE", "Stop to sign every one of them.",
                        "Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2),
                        "He sorts out the ones that can't wait and signs them against the wall. The "
                      + "courier finally gets to sit down."),
                    new StoryOption("SIGN_THEM_LATER", "Sign them later.",
                        "Gain 75 Gold. Add [gold]Overdue Reports[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGoldAddCard, 75, typeof(OverdueReports)),
                        "\"Tell her they're in good hands.\" He tucks the satchel, and the expedition "
                      + "funds packed with it, under his cloak."),
                    new StoryOption("REQUEST_REINFORCEMENTS", "Request reinforcements for the expedition.",
                        "Choose 1 of 3 random Uncommon Companions to add to your deck.",
                        StoryEffect.ChooseCompanion(CardRarity.Uncommon),
                        "\"And not the new recruits. Send the ones who complain. They're usually right.\""),
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_dispatch_from_mondstadt"),
                FallbackPortraitPath: "res://images/events/potion_courier.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(VarkaWolfOfTheNorth),
                Title: "The Wolf of the North",
                Body:
                    "Frost spreads across the landing. Andrius takes shape beside Varka, stretches, and bares "
                  + "his teeth. The Wolf of the North gave him his title, and Varka knows that look "
                  + "well enough: his old partner wants a spar.\n\n[i]\"You've gone soft, Knight.\"[/i] — "
                  + "[i]\"Soft? Come over here and say that.\"[/i]",
                Options: new[]
                {
                    new StoryOption("SPAR", "Spar with him.",
                        "Lose 12 HP. Upgrade 3 random cards.",
                        new StoryEffect(StoryEffectKind.LoseHpUpgradeRandomCards, 3, HpLoss: 12),
                        "They wreck half the landing. Boreas looks pleased with himself."),
                    new StoryOption("REST", "Rest at his side.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20),
                        "He sleeps with his back against the wolf's flank, the way he did on the northern watch."),
                    new StoryOption("ASK_AFTER_THE_PACK", "Ask after the pack.",
                        "Choose 1 of 3 random Uncommon Attacks to add to your deck.",
                        StoryEffect.Choose(CardRarity.Uncommon, CardType.Attack),
                        "Boreas shows him Razor running with the wolves, fast and grinning. Varka watches "
                      + "until it fades."),
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_wolf_of_the_north"),
                FallbackPortraitPath: "res://images/events/punch_off.png")
            {
                Follows = new[] { typeof(VarkaRearguard) },
                Home = true,
            },

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(VarkaLongWayHome),
                Title: "The Long Way Home",
                Body:
                    "Favonius banners come into view on the stairs below. His expedition has caught up, with "
                  + "familiar faces from Mondstadt among them. After five years away, Varka has quite a "
                  + "welcome waiting. Jean folds her arms. \"You owe me five years of reports, Grand Master.\" "
                  + "Eula, Noelle, and Diluc step forward.",
                Options: new[]
                {
                    new StoryOption("EULA", "Eula",
                        "Choose 1 of 3 random upgraded Uncommon Attacks to add to your deck.",
                        StoryEffect.Choose(CardRarity.Uncommon, CardType.Attack, upgraded: true),
                        HomeResult("Eula", "You still owe me a rematch. Don't you dare go easy.", EulaAnswer)),
                    new StoryOption("NOELLE", "Noelle",
                        "Choose 1 of 3 random upgraded Uncommon Skills to add to your deck.",
                        StoryEffect.Choose(CardRarity.Uncommon, CardType.Skill, upgraded: true),
                        HomeResult("Noelle", "Welcome back, Grand Master! Please, let me take the front line.", NoelleAnswer)),
                    new StoryOption("DILUC", "Diluc",
                        "Choose 1 of 3 random upgraded Uncommon Powers to add to your deck.",
                        StoryEffect.Choose(CardRarity.Uncommon, CardType.Power, upgraded: true),
                        HomeResult("Diluc", "There's a bottle at Angel's Share with your name on it. You're paying.", DilucAnswer)),
                    new StoryOption("WAVE_THEM_BACK", "Wave them back to the column.",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "Varka: \"" + WaveBackLine + "\""),
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_long_way_home"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(VarkaWolfOfTheNorth), typeof(VarkaFirstExam) },
                Home = true,
                Openings = new[]
                {
                    new StoryOpening("TOOK_THE_REAR",
                        new StoryCondition(typeof(VarkaRearguard), "TAKE_THE_REAR"),
                        "The three from the rearguard march at the front of the column, grinning."),
                    new StoryOpening("SUPPLIES",
                        new StoryCondition(typeof(VarkaRearguard), "LEAVE_SUPPLIES"),
                        "The three from the rearguard are waiting at the top of the stairs, fed and "
                      + "rested. They saved him a loaf."),
                    new StoryOpening("SENT_DOWN",
                        new StoryCondition(typeof(VarkaRearguard), "SEND_THEM_DOWN"),
                        "Halfway home, three knights climb back up to meet him. \"Message delivered, sir. "
                      + "Jean says hurry up.\""),
                },
            },

            // ---- The story chains (review/active/klee-varka-story-chains-2026-10-14.md)

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(VarkaSecondSatchel),
                Title: "The Second Satchel",
                Body:
                    "Another courier, another satchel, heavier than the first. \"The Acting Grand Master "
                  + "says these are the urgent ones, sir. She underlined [i]urgent[/i].\"",
                Options: new[]
                {
                    new StoryOption("SIGN_BY_LAMPLIGHT", "Sign them by lamplight.",
                        "Lose 8 HP. Upgrade 2 random cards. Remove all [gold]Overdue Reports[/gold] from your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 8),
                        "He reads every name on the casualty lists before he signs the last page. The lamp "
                      + "burns out at dawn.")
                    {
                        Then = new[]
                        {
                            new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2),
                            new StoryEffect(StoryEffectKind.RemoveEvery, 0, typeof(OverdueReports)),
                        },
                    },
                    new StoryOption("HAND_TO_THE_COURIER", "Hand them to the courier.",
                        "Lose 75 Gold. Remove a card.",
                        new StoryEffect(StoryEffectKind.LoseGold, 75),
                        "\"Consider it a promotion. And a raise.\"")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.RemoveCard) },
                    },
                    new StoryOption("LOSE_THEM_ON_THE_STAIRS", "Lose them on the stairs.",
                        "Gain 2 random potions. Add [gold]Overdue Reports[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 2),
                        "The reports go astray somewhere on the stairs. The potions packed under them don't.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(OverdueReports)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_second_satchel"),
                FallbackPortraitPath: "res://images/events/potion_courier.png")
            {
                Follows = new[] { typeof(VarkaDispatchFromMondstadt) },
                Openings = new[]
                {
                    new StoryOpening("SIGNED",
                        new StoryCondition(typeof(VarkaDispatchFromMondstadt), "SIGN_EVERY_ONE"),
                        "\"You signed the last lot so fast, sir, she sent twice as many.\""),
                    new StoryOpening("LATER",
                        new StoryCondition(typeof(VarkaDispatchFromMondstadt), "SIGN_THEM_LATER"),
                        "\"Your overdue reports are now very overdue.\""),
                    new StoryOpening("REINFORCEMENTS",
                        new StoryCondition(typeof(VarkaDispatchFromMondstadt), "REQUEST_REINFORCEMENTS"),
                        "\"The reinforcements came with forms.\""),
                },
            },

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(VarkaActingGrandMaster),
                Title: "The Acting Grand Master",
                Body:
                    "Jean is waiting on the landing, alone, a ledger under her arm. \"Five years, Grand "
                  + "Master. I came up to collect.\" She almost manages not to smile. Then, quieter: \"The "
                  + "reports from the Spire stopped. I had to see for myself that you were all still standing.\"",
                Options: new[]
                {
                    new StoryOption("LET_HER_LEAD", "Let her lead the last stretch.",
                        "Lose 10 HP. Choose 1 of 3 random upgraded Rare Companions to add to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "\"Lead on, Acting Grand Master.\" \"Then keep up, Grand Master.\"")
                    {
                        Then = new[] { StoryEffect.ChooseCompanion(CardRarity.Rare, upgraded: true) },
                    },
                    new StoryOption("PROMISE_A_FULL_REPORT", "Promise a full report at Angel's Share.",
                        "Remove every Curse. Lose 50 Gold for each.",
                        new StoryEffect(StoryEffectKind.RemoveEveryCurseLoseGoldEach, 50),
                        "\"Every word. I'm buying.\""),
                    new StoryOption("CARRY_HER_LEDGER", "Carry her ledger the rest of the way.",
                        "Upgrade 3 random cards. Add [gold]Overdue Reports[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 3),
                        "He reads it on the way. Supply routes, a budget, and one page of complaints about him.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(OverdueReports)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_acting_grand_master"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png")
            {
                Follows = new[] { typeof(VarkaSecondSatchel) },
            },

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(VarkaRearguard),
                Title: "The Rearguard",
                Body:
                    "Three Favonius knights sit against the wall of the landing, bandaged and gray with "
                  + "dust. They straighten when they see him. \"Grand Master. We fell behind. We can still "
                  + "fight, sir.\"",
                Options: new[]
                {
                    new StoryOption("TAKE_THE_REAR", "Take the rear yourself.",
                        "Lose 10 HP. Choose 1 of 3 random Rare cards to add to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 10),
                        "\"You lot walk in front. I'll keep the stairs behind us.\"")
                    {
                        Then = new[] { StoryEffect.Choose(CardRarity.Rare) },
                    },
                    new StoryOption("LEAVE_SUPPLIES", "Leave them your supplies.",
                        "Lose 75 Gold. Remove a card.",
                        new StoryEffect(StoryEffectKind.LoseGold, 75),
                        "He leaves his own pack and travels light. \"Eat. That's an order.\"")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.RemoveCard) },
                    },
                    new StoryOption("SEND_THEM_DOWN", "Send them down with a message.",
                        "Gain 2 random potions. Add [gold]Overdue Reports[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 2),
                        "\"Tell Jean we're fine.\" They press their potions on him, and their paperwork.")
                    {
                        Then = new[] { new StoryEffect(StoryEffectKind.AddCard, 0, typeof(OverdueReports)) },
                    },
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_rearguard"),
                FallbackPortraitPath: "res://images/events/punch_off.png"),

            new StoryEvent(
                ActIndex: 0,
                EventType: typeof(VarkaSongOnTheWind),
                Title: "A Song on the Wind",
                Body:
                    "The wind on this landing carries an old Mondstadt tune: a young man knocks out every "
                  + "examiner, is rejected anyway, then ambushes the Grand Master on his way home from the "
                  + "tavern to make a point. Varka knows the song. He was the young man.",
                Options: new[]
                {
                    new StoryOption("HUM_ALONG", "Hum along.",
                        "Heal 12 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 12),
                        "He gets the second verse wrong. He always does."),
                    new StoryOption("TOAST_ABSENT_FRIENDS", "Toast absent friends.",
                        "Gain a random potion.",
                        new StoryEffect(StoryEffectKind.GainRandomPotions, 1),
                        "He raises a cup of the good wine to Valentine."),
                    new StoryOption("REMEMBER_VALENTINES_ADVICE", "Remember Valentine's advice.",
                        "Upgrade a card.",
                        new StoryEffect(StoryEffectKind.UpgradeChosenCard),
                        "\"Find a reason of your own.\" He did, eventually. It was home."),
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_song_on_the_wind"),
                FallbackPortraitPath: "res://images/events/wellspring.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(VarkaFirstExam),
                Title: "The First Exam",
                Body:
                    "Training dummies stand in a ring on this landing, as if someone set up a knight's exam "
                  + "inside the Spire. Varka cracks his knuckles. He has taken this exam before.",
                Options: new[]
                {
                    new StoryOption("KNOCK_THEM_ALL_DOWN", "Knock them all down again.",
                        "Lose 8 HP. Add an upgraded [gold]Four Winds' Ascension[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.LoseHp, 8),
                        "Every dummy down in one pass. Nobody here to reject him.")
                    {
                        Then = new[]
                        {
                            new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkFourWindsAscension)),
                        },
                    },
                    new StoryOption("DO_IT_PROPERLY", "Do it properly this time.",
                        "Upgrade 2 random cards.",
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2),
                        "One at a time, by the book. Valentine would laugh at him."),
                    new StoryOption("WALK_PAST", "Walk past.",
                        "Heal 15 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 15),
                        "He pats the nearest dummy on the way by."),
                },
                Portrait: () => KleeArt.CardPortrait("event_varka_first_exam"),
                FallbackPortraitPath: "res://images/events/punch_off.png")
            {
                Follows = new[] { typeof(VarkaSongOnTheWind) },
            },
        },

        // Orobas's Archaic Tooth replaces the Ascension with Dandelion Gale,
        // which speaks the same line.
        SignatureCards = new[]
        {
            typeof(ProtoVkFourWindsAscension),
            typeof(global::KleeMod.Cards.Varka.DandelionGale),
        },
    };
}

/// <summary>Act 1, Varka only: Dispatch from Mondstadt.</summary>
public sealed class VarkaDispatchFromMondstadt : StoryEventModel { }

/// <summary>Act 2, Varka only: The Wolf of the North (the home thread).</summary>
public sealed class VarkaWolfOfTheNorth : StoryEventModel { }

/// <summary>Act 3, Varka only: The Long Way Home (the home finale).</summary>
public sealed class VarkaLongWayHome : StoryEventModel { }

/// <summary>Act 2, Varka only: The Second Satchel.</summary>
public sealed class VarkaSecondSatchel : StoryEventModel { }

/// <summary>Act 3, Varka only: The Acting Grand Master.</summary>
public sealed class VarkaActingGrandMaster : StoryEventModel { }

/// <summary>Act 1, Varka only: The Rearguard.</summary>
public sealed class VarkaRearguard : StoryEventModel { }

/// <summary>Act 1, Varka only: A Song on the Wind.</summary>
public sealed class VarkaSongOnTheWind : StoryEventModel { }

/// <summary>Act 2, Varka only: The First Exam.</summary>
public sealed class VarkaFirstExam : StoryEventModel { }
