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
        "Klee knew you'd come! ...Klee's still not going home until the top, though.";

    private static string KnightsResult(string knight, string line) =>
        knight + ": \"" + line + "\"\n" + "Klee: \"" + KnightsAnswer + "\"";

    public static readonly CharacterStory Table = new()
    {
        Character = typeof(Klee),
        Name = "Klee",

        IntroTitle = "The Spark Knight of Mondstadt.",
        IntroLine =
            "Mom says the best treasure is at the top of the tallest place. Klee brought bombs for anything in the way.",

        Ancients = new[]
        {
            new AncientExchange("Neow", "NEOW",
                "A child. Carrying... fire.",
                "It's not fire yet! Klee hasn't lit it."),
            new AncientExchange("Orobas", "OROBAS",
                "Your trinket hums. Let me make it sing.",
                "Can it go [i]boom[/i] louder?"),
            new AncientExchange("Pael", "PAEL",
                "You have bitten off more than you can chew, little one.",
                "Klee only bites cookies. Bombs are for throwing."),
            new AncientExchange("Tezcatara", "TEZCATARA",
                "Warm yourself by my light.",
                "Klee makes her own light. Want to see?"),
            new AncientExchange("Nonupeipe", "NONUPEIPE",
                "Small hands. Many sparks.",
                "Mom says a good bomb needs small hands."),
            new AncientExchange("Tanx", "TANX",
                "Do you fight for glory?",
                "Klee fights so Jean doesn't find out she left."),
            new AncientExchange("Vakuu", "VAKUU",
                "Trade with me.",
                "Klee has... three pebbles and a Dodoco."),
            new AncientExchange("Darv", "DARV",
                "I collect what others leave behind.",
                "Klee leaves craters. Do you want one?"),
        },

        Lines = new CombatLines(
            BossEntry: "Klee's never blown up anything that big!",
            LowHp: "Owie... Klee's okay. Klee's [i]fine[/i].",
            Signature: "KABOOM!",
            BossKill: "Klee's gonna need a bigger backpack.",
            RunLoss: "Klee... wants to go home now.",
            RunWin: "Wait till Jean hears! ...Actually, maybe don't tell Jean."),

        Pairs = new[]
        {
            new PairExchange(typeof(Kokomi), "Kokomi",
                "Stay behind the jellyfish, Klee.",
                "Can the jellyfish carry bombs?"),
            new PairExchange(typeof(Furina), "Furina",
                "A little explosion would make a fine finale.",
                "Klee does [i]big[/i] explosions!"),
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
                    "A Favonius pigeon lands on Klee's backpack with a letter tied to its leg. "
                  + "It is in Jean's handwriting.\n\n"
                  + "[i]\"Klee — Albedo told me where you went. I am not angry. (I am a little "
                  + "angry.) Eat proper meals, stay close to your friends, and do not, under any "
                  + "circumstances, blow up anything that is holding the Spire up. — Jean, Acting "
                  + "Grand Master\"[/i]",
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
                    "Footsteps on the stairs below. Three familiar voices argue about who gets to "
                  + "bring Klee home. When they see her, they stop arguing.",
                Options: new[]
                {
                    new StoryOption("KAEYA", "Kaeya",
                        "Add an upgraded [gold]Kaeya — Glacial Waltz[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcKaeyaGlacialWaltz)),
                        KnightsResult("Kaeya", "Shh. I won't tell Jean if you don't.")),
                    new StoryOption("NOELLE", "Noelle",
                        "Add an upgraded [gold]Noelle — Breastplate[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcNoelleBreastplate)),
                        KnightsResult("Noelle", "I brought snacks. And a shield. Mostly the shield.")),
                    new StoryOption("ALBEDO", "Albedo",
                        "Add an upgraded [gold]Albedo — Solar Isotoma[/gold] to your deck.",
                        new StoryEffect(StoryEffectKind.AddUpgradedCard, 0, typeof(ProtoMcAlbedoSolarIsotoma)),
                        KnightsResult("Albedo", "I'll take notes. You do the exploding.")),
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
