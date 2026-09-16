using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// `EB-695`. WHAT A RELIC ANSWERED WITH, ON THE PATH THAT HAD NO RECEIPT.
///
/// THE FIND (Kokomi r30, lane 2, debrief 1). The Tamakushi Casket answers
/// "whenever you apply a debuff to an enemy" with a 2-damage Hydro strike from
/// the jellyfish. Inside a PLAN carry-out that strike is named --
/// "Inside the same beat: Tamakushi Casket 2 on Damp Cultist", the clause
/// `EB-453`/`EB-518` built -- because `KokomiPlan.NoteRider` is standing there
/// to catch it. Play the same debuff card FROM HAND and the same strike lands
/// with nothing anywhere naming it: the seat watched HP fall by more than the
/// card's number and subtracted the difference by hand on every such play.
///
/// THE ASYMMETRY WAS AN ACCIDENT OF WHERE THE RECEIPT LIVED. `NoteRider` files
/// a rider against the Plan being resolved RIGHT NOW and drops it where no
/// Plan is running -- which is correct for a Plan's own accounting and is
/// exactly the played-card path. So this is the same fact, kept where a played
/// card can reach it: a per-turn list the page prints.
///
/// IT IS `ReactionLog`'S SHAPE AND ITS WINDOW, deliberately, down to the
/// carry: a row is a printed name, a number and the body it landed on; the
/// wire keys ARE the contract; `Snapshot` hands primitives to
/// `vendor/STS2_MCP/gits/GitsReactionLog.cs` by reflection because that
/// assembly cannot reference this one; and a strike that lands after the
/// player ended their turn carries one turn rather than being dropped before a
/// page could print it (`EB-710`, whose argument is repeated in
/// <see cref="MarkTurnStart"/> because the failure is the same one).
///
/// ONE ROW PER STRIKE AND NOT PER CARD, because that is what a reader is
/// subtracting: `EB-518` is the whole reason the body is on the row -- three
/// entries reading "Tamakushi Casket 2" divide among three enemies more than
/// one way, and the beat that does not add up is the one that struck the same
/// body twice.
///
/// SHIPPED CODE, like `ReactionLog` and unlike the relic that feeds it: the
/// Casket is quarantined behind `PROTOTYPE_CARDS`, and a log that were
/// quarantined with it would make "no rows" mean two things to the bridge.
/// Empty is a fact; absent is a build with no klee mod.
/// </summary>
public static class RelicAnswerLog
{
    /// <summary>One answering hit, as the page prints it. `Carried` is
    /// `ReactionLog.Reacted`'s and means the same thing: the row resolved
    /// after the player ended their turn and no page has printed it.</summary>
    public readonly record struct Answered(
        string Source, int Amount, string Target, string CombatId,
        bool Carried = false);

    private static readonly List<Answered> Rows = new();

    /// <summary>Where the player stopped watching, or negative for "no mark
    /// was taken this turn". <see cref="ReactionLog.MarkPlayerTurnEnd"/>'s
    /// twin, and taken from the same broadcast.</summary>
    private static int _playerTurnEnd = -1;

    /// <summary>"The player's turn is ending here."</summary>
    public static void MarkPlayerTurnEnd() => _playerTurnEnd = Rows.Count;

    /// <summary>
    /// Open the turn's window, carrying the rows the player has not been
    /// shown. <see cref="ReactionLog.MarkTurnStart"/>'s argument, whole: this
    /// fires at the END OF THE ENEMY TURN, so a straight clear would drop
    /// every row logged since the player last had control -- and those are
    /// precisely the rows no page ever carried. Rows past the mark survive one
    /// turn, flagged; rows before it have been printed and go. NO MARK, NO
    /// CARRY, for the same conservative reason: a window whose end nothing
    /// announced is not a window anything can call unwatched.
    /// </summary>
    public static void MarkTurnStart()
    {
        var carried = new List<Answered>();
        for (var i = _playerTurnEnd; i >= 0 && i < Rows.Count; i++)
        {
            carried.Add(Rows[i] with { Carried = true });
        }
        Rows.Clear();
        Rows.AddRange(carried);
        _playerTurnEnd = -1;
    }

    /// <summary>
    /// "This relic answered, for this much, on this body."
    ///
    /// CALLED WHERE THE PLAN'S OWN RECEIPT DID NOT CATCH IT, which is what
    /// keeps the Casket's strike from being named twice on one screen: inside
    /// a carry-out the rider clause already prints it, and
    /// <see cref="Prototype.KokomiPlan.NoteRider"/> says whether it filed the
    /// row. The caller passes that answer in.
    ///
    /// A ZERO WRITES NOTHING. The number reported is the DELIVERED one
    /// (Vulnerable moves it), and a strike that delivered nothing is not a
    /// subtraction anybody is trying to account for.
    /// </summary>
    public static void Note(string source, int amount, Creature? target)
    {
        if (string.IsNullOrEmpty(source) || amount <= 0) return;
        Rows.Add(new Answered(source, amount, Named(target),
                              Safe(() => target?.CombatId.ToString())));
    }

    /// <summary>A printed title, or `""`, and never a throw --
    /// `ReactionLog.Named`'s bargain and its reason: a display read is a read
    /// of live game objects that a torn-down combat can leave half standing,
    /// and a LOG must never be the thing that ends a beat.</summary>
    private static string Named(Creature? creature) =>
        Safe(() => creature?.Monster?.Title.GetFormattedText()
                   ?? creature?.Name);

    private static string Safe(System.Func<string?> read)
    {
        try
        {
            return read() ?? string.Empty;
        }
        catch (System.Exception)
        {
            return string.Empty;
        }
    }

    /// <summary>
    /// THE WIRE'S VIEW. `ReactionLog.Snapshot`'s shape and contract: plain
    /// dictionaries of primitives, oldest first, read by reflection from the
    /// bridge. The key names here ARE the contract and
    /// `understudy/blindplay_board.relic_answers` reads them.
    /// </summary>
    public static List<Dictionary<string, object?>> Snapshot() =>
        Rows.ConvertAll(row => new Dictionary<string, object?>
        {
            ["source"] = row.Source,
            ["amount"] = row.Amount,
            ["target"] = row.Target,
            ["combat_id"] = row.CombatId,
            ["carried"] = row.Carried,
        });
}
