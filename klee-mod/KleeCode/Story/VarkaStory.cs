using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;

namespace KleeMod.Story;

/// <summary>
/// VARKA'S STORY TABLE. Every string here is the ruled paper's, word for word
/// (<c>review/active/varka-story-2026-10-13.md</c>: the intro, the eight
/// Ancients, Dispatch from Mondstadt, The Wolf of the North, The Long Way
/// Home, the combat and pair lines; ruled "Sounds good! Let's go with it.").
/// <c>VarkaStoryTests</c> holds each one against the paper. Nothing in this
/// file is authored here. His pair with Klee is in Klee's table (written with
/// her batch); <see cref="StoryRules.BossEntryPlan"/> finds it from either.
/// </summary>
public static class VarkaStory
{
    /// <summary>Varka's answer when one of the three steps out (sec.5).</summary>
    public const string HomeAnswer = "Good. Then we climb together, and we all go home.";

    /// <summary>Varka's line on the skip (sec.5, "Wave them back to the column.").</summary>
    public const string WaveBackLine = "Save it for the tavern. We've still got a Spire to finish.";

    private static string HomeResult(string knight, string line) =>
        knight + ": \"" + line + "\"\n" + "Varka: \"" + HomeAnswer + "\"";

    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Varka),
        Name = "Varka",

        IntroTitle = "The Grand Master of the Knights of Favonius.",
        IntroLine =
            "He marched most of the Knights north to fight the Abyss and left Jean the paperwork. The Spire is the expedition's next front.",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "A knight. A large one.",
                "Grand Master, if we're being formal. Let's not."),
            new AncientExchange("Orobas", "OROBAS",
                "Your trinket hums. Let me make it sing.",
                "Teach it a drinking song and we have a deal."),
            new AncientExchange("Pael", "PAEL",
                "You have bitten off more than you can chew.",
                "Every expedition starts that way."),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Warm yourself by my light.",
                "Gladly. It's been a long winter up north."),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "Two blades. One will.",
                "And Lord Barbatos behind them."),
            new AncientExchange("Tanx", "TANX",
                "Do you fight for glory?",
                "I fight so my knights get home. Glory can find its own way."),
            new AncientExchange("Vakuu", "VAKUU",
                "Trade with me.",
                "I have a stack of unsigned reports. I'll pay you to take them."),
            new AncientExchange("Darv", "DARV",
                "I collect what others leave behind.",
                "Then you'll want my desk. I left it to Jean."),
        },

        Lines = new CombatLines(
            BossEntry: "Knights, with me! ...Right. Just me, then.",
            LowHp: "Still standing. That's the job.",
            Signature: "By Lord Barbatos!",
            BossKill: "Someone write that down. Not me!",
            RunLoss: "Tell Jean... we're running a little late.",
            RunWin: "Knights of Favonius, we're going home!"),

        Pairs = new[]
        {
            new PairExchange(typeof(Kokomi), "Kokomi",
                "Only if you take the left flank.",
                "You've got your planning face on. Mind if I borrow it?",
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
                        new StoryEffect(StoryEffectKind.UpgradeRandomCards, 2)),
                    new StoryOption("SIGN_THEM_LATER", "Sign them later.",
                        "Gain 75 Gold. Add [gold]Overdue Reports[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.GainGoldAddCard, 75, typeof(OverdueReports))),
                    new StoryOption("REQUEST_REINFORCEMENTS", "Request reinforcements for the expedition.",
                        "Choose 1 of 3 random Knights to add to your deck.",
                        new StoryEffect(StoryEffectKind.ChooseFromPoolToDeck, 3)),
                },
                Portrait: () => KleeArt.CardPortrait("proto_vk_grand_masters_order"),
                FallbackPortraitPath: "res://images/events/potion_courier.png"),

            new StoryEvent(
                ActIndex: 1,
                EventType: typeof(VarkaWolfOfTheNorth),
                Title: "The Wolf of the North",
                Body:
                    "Frost creeps across the landing, and a great grey wolf pads out of it. "
                  + "Boreas, Varka's partner, a fragment of Andrius, the old Wolf of the North, "
                  + "has come to see whether the Knight of Boreas still deserves the name.\n\n"
                  + "[i]\"You've gone soft, Knight.\"[/i] — [i]\"Soft? Come over here and say that.\"[/i]",
                Options: new[]
                {
                    new StoryOption("SPAR", "Spar with him.",
                        "Lose 12 HP. Upgrade 3 random cards.",
                        new StoryEffect(StoryEffectKind.LoseHpUpgradeRandomCards, 3, HpLoss: 12)),
                    new StoryOption("REST", "Rest at his side.",
                        "Heal 20 HP.",
                        new StoryEffect(StoryEffectKind.Heal, 20)),
                    new StoryOption("ASK_AFTER_THE_PACK", "Ask after the pack.",
                        "Add an upgraded [gold]Razor: Awakening[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkRazorClawAndThunder))),
                },
                Portrait: () => KleeArt.CardPortrait("proto_vk_boreas_unbound"),
                FallbackPortraitPath: "res://images/events/punch_off.png"),

            new StoryEvent(
                ActIndex: 2,
                EventType: typeof(VarkaLongWayHome),
                Title: "The Long Way Home",
                Body:
                    "Campfires on the stairs below, and banners in Favonius blue. After five years "
                  + "away, most of the expedition has come the long way round to walk him home. "
                  + "Jean is at the head of the column. \"You owe me five years of reports, Grand "
                  + "Master.\" Three faces step out of the ranks behind her.",
                Options: new[]
                {
                    new StoryOption("EULA", "Eula",
                        "Add an upgraded [gold]Eula: Icetide Vortex[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkEulaIcetideVortex)),
                        HomeResult("Eula", "You still owe me a rematch. Don't you dare go easy.")),
                    new StoryOption("NOELLE", "Noelle",
                        "Add an upgraded [gold]Noelle: Steadfast Maid[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkNoelleSteadfastMaid)),
                        HomeResult("Noelle", "Welcome back, Grand Master! Please, let me take the front line.")),
                    new StoryOption("DILUC", "Diluc",
                        "Add an upgraded [gold]Diluc: Searing Onslaught[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoVkDilucSearingOnslaught)),
                        HomeResult("Diluc", "Angel's Share is holding your usual table. Don't keep it waiting.")),
                    new StoryOption("WAVE_THEM_BACK", "Wave them back to the column.",
                        "Nothing.",
                        new StoryEffect(StoryEffectKind.Nothing),
                        "Varka: \"" + WaveBackLine + "\""),
                },
                Portrait: () => KleeArt.CardPortrait("proto_vk_rally_to_the_banner"),
                FallbackPortraitPath: "res://images/events/the_legends_were_true.png"),
        },

        SignatureCard = typeof(ProtoVkFourWindsAscension),
        ChoicePool = VarkaRules.PoolKnights,
    };
}

/// <summary>Act 1, Varka only: Dispatch from Mondstadt.</summary>
public sealed class VarkaDispatchFromMondstadt : StoryEventModel
{
    protected override StoryEvent Data => VarkaStory.Table.Events[0];
}

/// <summary>Act 2, Varka only: The Wolf of the North.</summary>
public sealed class VarkaWolfOfTheNorth : StoryEventModel
{
    protected override StoryEvent Data => VarkaStory.Table.Events[1];
}

/// <summary>Act 3, Varka only: The Long Way Home.</summary>
public sealed class VarkaLongWayHome : StoryEventModel
{
    protected override StoryEvent Data => VarkaStory.Table.Events[2];
}
