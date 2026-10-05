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

/// <summary>
/// THE OTHER TWO IN-COMBAT STAGE LINES (the Salon's Tab seat round,
/// 2026-10-05), filled the way <see cref="FurinaStageBowPreview"/> fills a
/// Guest Star's: the generated card ends its face in
/// <c>{InCombat:{StageDrainLine}|}</c> or <c>{InCombat:{StageRepay}|}</c> and
/// adds the token in <c>AddExtraArgsToDescription</c>.
///
/// THE DRAIN LINE. Below the line a Drain mode left the chooser with no word
/// said, and the game's chooser has no greyed option
/// (<see cref="ModalChoice.SelectAffordableMode"/>), so the card says it in
/// hand, before the play. The gate is <see cref="FurinaStage.CanDrain"/>, the
/// one the play and the chooser ask.
///
/// THE REPAY. A Repay with nothing drained did nothing and said nothing; the
/// face prints what it would return now, the clamp
/// <see cref="FurinaStageLedger.RepayRoom"/> applies, without moving it.
/// </summary>
public static class FurinaStageFacePreview
{
    /// <summary>"(Too close to your Drain line)" while a Drain of
    /// <paramref name="amount"/> cannot be paid; empty otherwise, and off a
    /// combat or a Furina board.</summary>
    public static string DrainLine(CardModel card, int amount) =>
        Owner(card) is { } owner && !FurinaStage.CanDrain(owner, amount)
            ? "\n(Too close to your Drain line)"
            : "";

    /// <summary>"(Repays N)": what a Repay of <paramref name="amount"/>
    /// would return now. Empty off a combat or a Furina board.</summary>
    public static string Repay(CardModel card, int amount) =>
        Owner(card) is { } owner ? Line(Room(owner, amount)) : "";

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public static string RepayAll(CardModel card) =>
        Owner(card) is { } owner
            ? Line(Room(owner, FurinaStage.DrainedOf(owner)))
            : "";

    /// <summary>The line's words, for the pins.</summary>
    public static string Line(int repays) => $"\n(Repays {repays})";

    /// <summary>What a Repay of <paramref name="amount"/> returns at this
    /// HP: never more than she drained, never past Max HP. A read; the
    /// ledger is not clamped here.</summary>
    public static int Room(MegaCrit.Sts2.Core.Entities.Creatures.Creature owner,
                           int amount)
    {
        var drained = System.Math.Min(
            FurinaStage.DrainedOf(owner),
            System.Math.Max(0, (int)owner.MaxHp - (int)owner.CurrentHp));
        return System.Math.Max(0, System.Math.Min(amount, drained));
    }

    private static MegaCrit.Sts2.Core.Entities.Creatures.Creature? Owner(
        CardModel card) =>
        TipOwner.CreatureOf(card) is { } owner
        && owner.CombatState != null && FurinaStage.LiveFor(owner)
            ? owner
            : null;
}
