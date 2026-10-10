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

    /// <summary>The line for <paramref name="stage"/> (the pins'; the pool to
    /// 75's rule): "(Clorinde moves to the newest seat)" for a guest already
    /// on stage, "(Charlotte will leave)" for the oldest guest on a full
    /// stage, else empty.</summary>
    public static string Line(FurinaStageLedger stage, StagePerformer who)
    {
        var room = StageDirector.GuestRoom(stage.Company.ToList(),
                                           stage.Capacity, who);
        return room.Kind switch
        {
            StageSummonResult.Repeat => $"\n({who} moves to the newest seat)",
            StageSummonResult.Evict =>
                $"\n({stage.Seats[room.Index].Who} will leave)",
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
/// THE DRAIN LINE. Since the Drain line rule (2026-10-09) a Drain may go
/// past the line, so the card says so in hand, before the play: "(Past your
/// Drain line of 59 HP)" while the Drain would take her past it. The one
/// refusal left -- a Drain to 0 HP -- reads "(Not enough HP)", because the
/// game's chooser has no greyed option
/// (<see cref="ModalChoice.SelectAffordableMode"/>). The gate is
/// <see cref="FurinaStage.CanDrain"/>, the one the play and the chooser
/// ask.
///
/// THE REPAY. A Repay with nothing drained did nothing and said nothing; the
/// face prints what it would return now, the clamp
/// <see cref="FurinaStageLedger.RepayRoom"/> applies, without moving it.
/// </summary>
public static class FurinaStageFacePreview
{
    /// <summary>"(Not enough HP)" while a Drain of <paramref name="amount"/>
    /// would take her to 0 HP; "(Past your Drain line of 59 HP)" while it
    /// would take her past the line; empty otherwise, and off a combat or a
    /// Furina board.</summary>
    public static string DrainLine(CardModel card, int amount)
    {
        if (Owner(card) is not { } owner) return "";
        if (!FurinaStage.CanDrain(owner, amount)) return NotEnoughHp;
        var ledger = FurinaStageLedger.For(owner);
        if (!ledger.PastLine(amount, (int)owner.CurrentHp)) return "";
        // The Spend round (2026-10-10): with A Five-Century Act in play the
        // HP drained past the line returns at the curtain call too, so the
        // tag says that instead of naming a line that costs nothing.
        return ledger.Mods.FiveCenturyAct > 0
            ? PastLineReturns
            : PastLine(FurinaStage.LineOf(owner));
    }

    /// <summary>The tag under A Five-Century Act: the HP drained past the
    /// line returns after combat.</summary>
    public const string PastLineReturns =
        "\n(Past your Drain line: returns after combat)";

    /// <summary>The refusal's words: a Drain cannot take her to 0 HP.
    /// </summary>
    public const string NotEnoughHp = "\n(Not enough HP)";

    /// <summary>The warning's words, for the pins: the HP drained past the
    /// line is lost unless Repaid.</summary>
    public static string PastLine(int line) =>
        $"\n(Past your Drain line of {line} HP)";

    /// <summary>The Drain tip's in-combat sentence (the pool-75 round,
    /// 2026-10-09: every record missed where the line sat): "Your Drain line
    /// is 30: the HP you started this fight with, minus 1/4 of your Max HP."
    /// Empty off a combat or a Furina board.</summary>
    public static string LineNow(CardModel card)
    {
        if (Owner(card) is not { } owner) return "";
        var ledger = FurinaStageLedger.For(owner);
        return LineNowWords(ledger.Line, ledger.LineWhy);
    }

    /// <summary>The sentence's words, for the pins.</summary>
    public static string LineNowWords(int line, string why) =>
        $"\nYour Drain line is {line}: {why}."
        // The Spend round 2 (2026-10-10): a line of 0 explains itself.
      + (line <= 0 ? " " + Capitalised(FurinaStageLaw.LineZeroReturns) + "."
                   : "");

    private static string Capitalised(string words) =>
        words.Length == 0 ? words
                          : char.ToUpperInvariant(words[0]) + words.Substring(1);

    /// <summary>"(Repays N)": what a Repay of <paramref name="amount"/>
    /// would return now. Empty off a combat or a Furina board. A card with a
    /// Repay floor names its <paramref name="payout"/> ("Block", "Vigor",
    /// "damage") whenever the Repay would return less than its full amount:
    /// "(Repays 0, +3 Block)" (the drain-line round, 2026-10-09).</summary>
    public static string Repay(CardModel card, int amount,
                               string payout = "") =>
        Owner(card) is { } owner
            ? Line(Room(owner, amount), amount, payout)
            : "";

    /// <summary>The Repay floor's payout words, as the faces print them.
    /// </summary>
    public const string PayBlock = "Block";

    /// <summary>Pneuma Tides' payout.</summary>
    public const string PayVigor = "Vigor";

    /// <summary>Surging Waters', Hydro Lance's and Cleansing Torrent's
    /// payout.</summary>
    public const string PayDamage = "damage";

    /// <summary>Singer of Many Waters: "Repay all your drained HP."</summary>
    public static string RepayAll(CardModel card) =>
        Owner(card) is { } owner
            ? Line(Room(owner, FurinaStage.DrainedOf(owner)))
            : "";

    /// <summary>The line's words, for the pins.</summary>
    public static string Line(int repays) => $"\n(Repays {repays})";

    /// <summary>The line with the Repay floor's payout: "(Repays 1, +2
    /// Block)" when a Repay of <paramref name="amount"/> returns only
    /// <paramref name="repays"/>; the plain line when it returns all of it
    /// or the card has no <paramref name="payout"/>.</summary>
    public static string Line(int repays, int amount, string payout) =>
        string.IsNullOrEmpty(payout) || repays >= amount
            ? Line(repays)
            : $"\n(Repays {repays}, +{amount - repays} {payout})";

    /// <summary>"(Repays N)" for a card that Drains
    /// <paramref name="drainFirst"/> before it Repays (Riptide Lunge): the
    /// Repay reads the board after the card's own Drain.</summary>
    public static string RepayAfterDrain(CardModel card, int amount,
                                         int drainFirst) =>
        Owner(card) is { } owner ? Line(Room(owner, amount, drainFirst)) : "";

    /// <summary>What a Repay of <paramref name="amount"/> returns at this
    /// HP: never more than she drained, never past Max HP. A read; the
    /// ledger is not clamped here. <paramref name="drainFirst"/> is a Drain
    /// the same card pays before its Repay.</summary>
    public static int Room(MegaCrit.Sts2.Core.Entities.Creatures.Creature owner,
                           int amount, int drainFirst = 0)
    {
        var drained = System.Math.Min(
            FurinaStage.DrainedOf(owner) + drainFirst,
            System.Math.Max(0,
                (int)owner.MaxHp - ((int)owner.CurrentHp - drainFirst)));
        return System.Math.Max(0, System.Math.Min(amount, drained));
    }

    private static MegaCrit.Sts2.Core.Entities.Creatures.Creature? Owner(
        CardModel card) =>
        TipOwner.CreatureOf(card) is { } owner
        && owner.CombatState != null && FurinaStage.LiveFor(owner)
            ? owner
            : null;
}
