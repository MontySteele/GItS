using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// WHO A SUMMON CARD WILL BOW, on its face (2026-10-04, the Furina v2 seat
/// round: three times a summon onto a full stage Bowed Usher off without the
/// player noticing, once on a boss's big attack turn).
///
/// A summon card's face ends in <c>{InCombat:{StageBow}|}</c>, the base
/// game's in-combat line, and the generated card fills <c>StageBow</c> in
/// <c>AddExtraArgsToDescription</c> from here. The line is empty when nobody
/// will Bow. The decision is <see cref="StageDirector.PlanSummons"/>, the
/// rule the summons themselves run (<see cref="StageDirector.SalonRoom"/>,
/// <see cref="StageDirector.GuestRoom"/>), so preview and outcome cannot
/// drift.
/// </summary>
public static class FurinaStageBowPreview
{
    /// <summary>The description token the line rides on.</summary>
    public const string Token = "StageBow";

    /// <summary>A card that summons these Salon members in order (a sheet
    /// name, or <c>"random"</c>).</summary>
    public static string Salon(CardModel card, params string[] members) =>
        For(card, members
            .Select(m => StageSummonStep.Salon(
                m == "random" ? null : FurinaStage.Parse(m)))
            .ToList());

    /// <summary>A Guest Star card.</summary>
    public static string Guest(CardModel card, string member) =>
        For(card, new[] { StageSummonStep.GuestStar(FurinaStage.Parse(member)) });

    /// <summary>The line for this card's owner's stage as it stands; empty
    /// off a combat, on a canonical card, or for a seat with no stage.
    /// </summary>
    public static string For(CardModel card,
                             IReadOnlyList<StageSummonStep> steps)
    {
        if (TipOwner.CreatureOf(card) is not { } owner
            || owner.CombatState == null || !FurinaStage.LiveFor(owner))
        {
            return "";
        }
        return For(FurinaStageLedger.For(owner), steps);
    }

    /// <summary>The line for <paramref name="stage"/> (the pins').</summary>
    public static string For(FurinaStageLedger stage,
                             IReadOnlyList<StageSummonStep> steps) =>
        Line(StageDirector.PlanSummons(stage, steps));

    /// <summary>The words, on a line of their own: "(Usher will Bow)",
    /// "(Clorinde will Bow and stay)", "(Walk-on: acts once and Bows)",
    /// "(Usher and Chevalmarin will Bow)". Empty when nobody Bows.</summary>
    public static string Line(IReadOnlyList<StagePlannedBow> bows)
    {
        if (bows.Count == 0) return "";
        if (bows.All(b => b.Kind == StageSummonResult.WalkOn))
        {
            return bows.Count == 1
                ? "\n(Walk-on: acts once and Bows)"
                : "\n(Walk-on: each acts once and Bows)";
        }
        if (bows.Count == 1 && bows[0].Kind == StageSummonResult.Repeat)
        {
            return $"\n({Name(bows[0].Who)} will Bow and stay)";
        }
        var names = bows.Select(b => Name(b.Who)).ToList();
        var list = names.Count == 1
            ? names[0]
            : string.Join(", ", names.Take(names.Count - 1))
              + " and " + names[^1];
        return $"\n({list} will Bow)";
    }

    private static string Name(StagePerformer? who) =>
        who?.ToString() ?? "a Salon member";
}
