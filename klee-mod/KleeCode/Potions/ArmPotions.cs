using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.PotionPools;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod.Potions;

/// <summary>
/// KLEE'S AND FURINA'S OWN POTIONS
/// (<c>review/active/relics-potions-klee-furina-2026-09-27.md</c>, ruled
/// 2026-09-27; the two Rares raised by the ruling). The base game's shape:
/// one Common (a refill), one Uncommon (a burst), one Rare (one big
/// rule-bending turn) per character. Combat only, and aimed at a player as the
/// base game's character potions are, so in co-op one can be handed over.
///
/// QUARANTINED: the file is inside <c>#if PROTOTYPE_CARDS</c>, and the two
/// pools are what the characters' <c>PotionPool</c> answers only under their
/// arms (<c>Klee.PotionPool</c>, <c>Furina.PotionPool</c>). Arm off, both still
/// answer <c>SilentPotionPool</c> and none of these can be rolled.
/// </summary>
public static class ArmPotions
{
    public static readonly IReadOnlyList<Type> Klee = new[]
    {
        typeof(BottledSparks), typeof(BlastingPowder), typeof(JumpyJuice),
    };

    public static readonly IReadOnlyList<Type> Furina = new[]
    {
        typeof(BottledApplause),
    };

    internal static string Image(string character, string slug) =>
        character + "/potions/" + slug + ".png";
}

/// <summary>A character potion: combat only, aimed at a player, art from the
/// pck when it is there and the base game's missing-potion picture when not.
/// </summary>
public abstract class ArmPotion : CustomPotionModel
{
    protected ArmPotion() : base(autoAdd: false) { }

    public override PotionUsage Usage => PotionUsage.CombatOnly;

    public override TargetType TargetType => TargetType.AnyPlayer;

    /// <summary><c>klee/potions/x.png</c> or <c>furina/potions/x.png</c>.
    /// </summary>
    protected abstract string ArtPath { get; }

    public override string? CustomPackedImagePath => KleePck.Path(ArtPath);

    public override string? CustomLargeImagePath => KleePck.Path(ArtPath);
}

// ---- Klee (the Klee arm) --------------------------------------------------

/// <summary>Common. "Gain 3 Sparks."</summary>
public sealed class BottledSparks : ArmPotion
{
    public const int Sparks = 3;

    public override PotionRarity Rarity => PotionRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Sparks"),
        ("description", "Gain [blue]" + Sparks + "[/blue] [gold]Sparks[/gold]."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("klee", "bottled_sparks");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        await SparkPower.Gain(choiceContext, target!, Sparks, cardSource: null,
                              source: "potion:bottled_sparks");
    }
}

/// <summary>Uncommon. "Every Bomb on every enemy grows 6." The drinker's
/// Bombs: every charge on every enemy.</summary>
public sealed class BlastingPowder : ArmPotion
{
    public const int Growth = 6;

    public override PotionRarity Rarity => PotionRarity.Uncommon;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Blasting Powder"),
        ("description",
            "Every [gold]Bomb[/gold] on every enemy grows [blue]" + Growth
          + "[/blue]."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("klee", "blasting_powder");

    protected override Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        Use(target!);
        return Task.CompletedTask;
    }

    /// <summary>The whole effect: pure, so the tests run it.</summary>
    public static void Use(Creature klee)
    {
        if (klee.CombatState == null) return;
        foreach (var enemy in klee.CombatState.HittableEnemies.ToList())
        {
            ProtoBombPower.GrowOn(enemy, klee, Growth);
        }
    }
}

/// <summary>Rare, raised by the ruling. "Double every Bomb on every enemy."
/// Nothing goes off: rule 7 stands, and her Set off card still fires them.
/// </summary>
public sealed class JumpyJuice : ArmPotion
{
    public override PotionRarity Rarity => PotionRarity.Rare;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Jumpy Juice"),
        ("description", "Double every [gold]Bomb[/gold] on every enemy."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("klee", "jumpy_juice");

    protected override Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        Use(target!);
        return Task.CompletedTask;
    }

    public static void Use(Creature klee)
    {
        if (klee.CombatState == null) return;
        foreach (var enemy in klee.CombatState.HittableEnemies.ToList())
        {
            ProtoBombPower.DoubleOn(enemy, klee);
        }
    }
}

// ---- Furina (the Stage) ---------------------------------------------------

/// <summary>Common (sec.10): "Gain 6 Fanfare."</summary>
public sealed class BottledApplause : ArmPotion
{
    public const int Fanfare = 6;

    public override PotionRarity Rarity => PotionRarity.Common;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Bottled Applause"),
        ("description",
            "Gain [blue]" + Fanfare + "[/blue] [gold]Fanfare[/gold]."),
    };

    protected override string ArtPath =>
        ArmPotions.Image("furina", "bottled_applause");

    protected override async Task OnUse(
        PlayerChoiceContext choiceContext, Creature? target)
    {
        AssertValidForTargetedPotion(target);
        if (!FurinaStage.LiveFor(target)) return;
        using (FurinaStageLedger.For(target!).CausedBy("Bottled Applause"))
        {
            await FurinaStage.Gain(choiceContext, target, Fanfare,
                                   "Bottled Applause");
        }
    }
}

// ---- the pools -------------------------------------------------------------

/// <summary>Klee's potion pool under the Klee arm: her three, and nothing
/// borrowed. <c>Klee.PotionPool</c> answers it only with the arm on.</summary>
public sealed class KleePotionPool : PotionPoolModel
{
    public override string EnergyColorName => "ironclad";

    public override Color LabOutlineColor => new("E85A4F");

    protected override IEnumerable<PotionModel> GenerateAllPotions() => new PotionModel[]
    {
        ModelDb.Potion<BottledSparks>(),
        ModelDb.Potion<BlastingPowder>(),
        ModelDb.Potion<JumpyJuice>(),
    };
}

/// <summary>Furina's potion pool: Bottled Applause, and nothing borrowed
/// (the Salon's Tab, 2026-10-05: Curtain Water and Encore Elixir left with
/// Rehearsal and the performers).</summary>
public sealed class FurinaPotionPool : PotionPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("4AA6C8");

    protected override IEnumerable<PotionModel> GenerateAllPotions() => new PotionModel[]
    {
        ModelDb.Potion<BottledApplause>(),
    };
}
