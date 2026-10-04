using System.Linq;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// WHO A GUEST STAR CARD WILL MOVE, on its face (2026-10-04, the Furina v2
/// seat round: three times a summon onto a full stage sent a performer off
/// without the player noticing). Kept for the guests (the Salon's Tab,
/// 2026-10-05).
///
/// A Guest Star card's face ends in <c>{InCombat:{StageBow}|}</c>, the base
/// game's in-combat line, and the generated card fills <c>StageBow</c> in
/// <c>AddExtraArgsToDescription</c> from here. The line is empty when the
/// guest simply takes a free seat. The decision is
/// <see cref="StageDirector.GuestRoom"/>, the rule the summon itself runs,
/// so preview and outcome cannot drift.
/// </summary>
public static class FurinaStageBowPreview
{
    /// <summary>The description token the line rides on.</summary>
    public const string Token = "StageBow";

    /// <summary>A Guest Star card's line for its owner's stage as it stands;
    /// empty off a combat, on a canonical card, or for a seat that is not
    /// Furina's.</summary>
    public static string Guest(CardModel card, string member)
    {
        if (TipOwner.CreatureOf(card) is not { } owner
            || owner.CombatState == null || !FurinaStage.LiveFor(owner))
        {
            return "";
        }
        return Line(FurinaStageLedger.For(owner), FurinaStage.Parse(member));
    }

    /// <summary>The line for <paramref name="stage"/> (the pins'): "(Clorinde
    /// will act again)" for a guest already on stage, "(Charlotte will act
    /// and leave)" for the oldest guest on a full stage, else empty.</summary>
    public static string Line(FurinaStageLedger stage, StagePerformer who)
    {
        var room = StageDirector.GuestRoom(stage.Company.ToList(),
                                           stage.Capacity, who);
        return room.Kind switch
        {
            StageSummonResult.Repeat => $"\n({who} will act again)",
            StageSummonResult.Evict =>
                $"\n({stage.Seats[room.Index].Who} will act and leave)",
            _ => "",
        };
    }
}
