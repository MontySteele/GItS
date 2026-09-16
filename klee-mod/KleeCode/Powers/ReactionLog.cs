using System.Collections.Generic;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// `EB-681`. WHAT REACTED THIS TURN, BY NAME, IN ORDER.
///
/// THE FIND (Kokomi r27). Lane 2, fight 4: Slack Water put Hydro on a body,
/// Shinobu's Thundergrust hit it with Electro, and the panel showed "Poison 8,
/// not the 4 the Electro-Charged rule prints". The eight was two
/// Electro-Charged procs -- the Tamakushi Casket answered the Weak with a 2
/// Hydro hit, which landed on the fresh Electro aura and reacted a second time
/// -- and the seat reconstructed the whole beat from a doubled number, saying
/// so: "the player has to reconstruct a double proc from a number that is
/// simply twice what the keyword says. I only trusted my reading because it
/// reproduced four times." Lane 1, (c) 2, is the same hole from the other
/// side: "Gorou+'s Crystallize did not visibly fire in fight 5 turn 2", and
/// nothing on any screen could settle whether it had.
///
/// NO NUMBER, AND THAT IS DELIBERATE. What a reaction DELIVERS is already on
/// the board and on the panel; what no surface carried is that it HAPPENED,
/// how many times, and off what. So a row is the reaction's printed name, the
/// body it landed on, and the source that triggered it -- three facts the
/// funnel already holds, none of them derived and none of them a measurement.
/// `R101b` is untouched: this is the beat a sighted player watched, not an
/// instrument's ledger.
///
/// THE SINGLE FUNNEL IS <see cref="ReactionEffects.Resolve"/>, which says so
/// itself ("this is the single site a reaction resolves in the mod"), so a
/// reaction cannot happen off this list -- which is the row's acceptance.
///
/// SHIPPED CODE AND NOT QUARANTINED, unlike the Plan queue beside it: every
/// arm reacts, and a Klee lane's Overloaded is as unnamed as a Kokomi lane's
/// Electro-Charged was. Read onto the wire by
/// `vendor/STS2_MCP/gits/GitsReactionLog.cs` and printed by
/// `understudy/blindplay_render`.
///
/// BOARD-GLOBAL, one list, which is <see cref="ReactionEffects.TotalResolved"/>'s
/// own scoping and red-pen R1's rule: a Reaction is a fact about the board. In
/// co-op both seats are shown the same beats, which is what both watched.
/// </summary>
public static class ReactionLog
{
    /// <summary>One reaction, as the page prints it.
    ///
    /// `EB-710` ADDS <paramref name="Carried"/>: true for a row the player
    /// page has not had a chance to print yet, because it resolved after they
    /// ended their turn. See <see cref="MarkTurnStart"/>.
    /// </summary>
    public readonly record struct Reacted(
        string Reaction, string Source, string Target, string CombatId,
        bool Carried = false);

    private static readonly List<Reacted> Rows = new();

    /// <summary>
    /// Where the player's own turn stopped and the unwatched half began: the
    /// count of rows at the moment their turn began to end. `EB-710`.
    ///
    /// NEGATIVE MEANS NO MARK WAS TAKEN THIS TURN, and then
    /// <see cref="MarkTurnStart"/> drops everything exactly as it always did.
    /// That is the conservative direction rather than an oversight: a window
    /// whose end was never announced is a window nothing can say was unwatched,
    /// and a log that carried on a missing mark would carry forever.
    /// </summary>
    private static int _playerTurnEnd = -1;

    /// <summary>The printed word for each reaction.
    ///
    /// A MAP AND NOT <c>ToString()</c>, because two of them differ: the enum
    /// spells <c>Overload</c> and <c>ElectroCharged</c> where every player
    /// surface prints "Overloaded" and "Electro-Charged". The page's own
    /// glossary (`blindplay_notes.REACTION_KEYWORDS`) is keyed by these
    /// strings, so a row and its definition on one screen cannot disagree.
    /// </summary>
    public static string PrintedName(Reaction reaction) => reaction switch
    {
        Reaction.Overload => "Overloaded",
        Reaction.ElectroCharged => "Electro-Charged",
        _ => reaction.ToString(),
    };

    /// <summary>
    /// "The player's turn is ending here." Called from
    /// <c>ElementalApplication.BeforeSideTurnEnd(Player)</c> -- `EB-710`.
    ///
    /// WHY THIS MARK EXISTS AT ALL. Every row noted from here on resolved on a
    /// board the player is no longer acting on: their end-of-turn effects, and
    /// then the whole enemy side. Nothing renders a player page in that
    /// window, so those rows were written and dropped without a screen ever
    /// carrying them.
    ///
    /// AND WHY IT IS <c>BeforeSideTurnEnd</c> rather than the After twin one
    /// hook later: the end-of-turn tenants that DEAL the elements deal them in
    /// <c>AfterSideTurnEnd(Player)</c> (Durin's Pyro consume) and in the
    /// <c>TurnEndSequencer</c>'s own fixed order, so a mark taken after them
    /// would file exactly the rows this row is about on the wrong side of the
    /// line. `KleeElementalHooks` is the FIRST listener in `KleeMod`'s
    /// subscribe chain, so this broadcast reaches here before the tenants'.
    /// </summary>
    public static void MarkPlayerTurnEnd() => _playerTurnEnd = Rows.Count;

    /// <summary>Open the turn's window. Called from
    /// <see cref="ReactionEffects.MarkTurnStart"/> and its extra-turn twin, so
    /// the window is exactly the one every other per-turn reaction fact
    /// keeps.
    ///
    /// `EB-710`: IT NO LONGER DROPS WHAT NO PAGE HAS PRINTED. Klee r26 and a
    /// Kokomi run met the heading saying "Nothing reacted this turn" through
    /// runs where reactions plainly happened: six Electro-Charged off Shinobu's
    /// Ring at END of turn, two Melts and an Overloaded off a played Set off.
    /// This method fires at the END OF THE ENEMY TURN
    /// (<c>ElementalApplication.AfterSideTurnEnd(Enemy)</c>), which is the
    /// opening of the player's next turn -- so a straight
    /// <c>Rows.Clear()</c> threw away every row logged since the player last
    /// had control, and those rows are precisely the ones no page ever showed.
    /// The log was cleared on the wrong window.
    ///
    /// SO THE UNWATCHED HALF SURVIVES EXACTLY ONE TURN. Rows from before
    /// <see cref="MarkPlayerTurnEnd"/> were on a page the player read while
    /// they were acting and go; rows from after it carry, marked, into the
    /// turn whose first page will print them. Next time round they sit BEFORE
    /// the new mark and are dropped in their turn, so a row prints once and a
    /// long enemy side cannot pile up.
    ///
    /// NO SECOND LIST AND NO TIMESTAMP, because neither is needed: the mark is
    /// an index into the one list and the carry is a slice of it.
    ///
    /// NO MARK, NO CARRY. Where <see cref="MarkPlayerTurnEnd"/> never fired --
    /// a combat opening, a window whose end nothing announced -- this drops
    /// everything, which is what it has always done.
    /// </summary>
    public static void MarkTurnStart()
    {
        var carried = new List<Reacted>();
        for (var i = _playerTurnEnd; i >= 0 && i < Rows.Count; i++)
        {
            carried.Add(Rows[i] with { Carried = true });
        }
        Rows.Clear();
        Rows.AddRange(carried);
        _playerTurnEnd = -1;
    }

    /// <summary>
    /// `EB-697`. THE SOURCE A HIT CANNOT NAME FOR ITSELF.
    ///
    /// THE FIND (Kokomi r30 lane 1 (c)). A Vaporize row named the
    /// <c>Bake-Kurage</c> as its source in a fight with no Plan written in it
    /// at all, and the hit was the Tamakushi Casket's answer to a Vulnerable.
    /// The resolution below is right for every hit that carries a card or is
    /// thrown by a creature acting for itself; it is wrong for the relic,
    /// because the relic's ping has NO card and its dealer is the pet
    /// (<see cref="KleeMod.Relics.TamakushiCasket.Strike"/> hands the pet in
    /// deliberately, so the number and the lunge land on the jellyfish). So
    /// the pet's name was the true dealer and the false SOURCE, and a seat
    /// reading the panel was told a Plan had fired.
    ///
    /// A SCOPE AND NOT A PARAMETER. <c>ElementalHit.Deal</c> is between the
    /// relic and this log and carries no source name; threading one through
    /// would put a relic's word on every elemental hit in the mod. The scope
    /// is the same shape <c>KokomiOverhaulKit.Answer</c> already uses one file
    /// over -- set, do the beat, restore -- and the game loop is single
    /// threaded, so it covers exactly the hit it wraps. It NESTS (the previous
    /// value is restored, not cleared), so a relic answering inside a relic
    /// leaves the outer name standing.
    /// </summary>
    public static Attribution Attribute(string source) => new(source);

    /// <summary>The scope <see cref="Attribute"/> opens. A struct, so the
    /// common path allocates nothing.</summary>
    public readonly struct Attribution : System.IDisposable
    {
        private readonly string? _previous;

        internal Attribution(string source)
        {
            _previous = _attributed;
            _attributed = source;
        }

        public void Dispose() => _attributed = _previous;
    }

    /// <summary>The name an open <see cref="Attribution"/> puts on the rows
    /// written inside it, or null.</summary>
    private static string? _attributed;

    /// <summary>"This reaction happened, on this body, off this source."
    ///
    /// THE SOURCE IS THE OPEN ATTRIBUTION where one is open (`EB-697`), the
    /// CARD where there is one, and the dealer otherwise -- which is what
    /// separates the two procs of the r27 beat: Thundergrust names itself,
    /// and the Casket's answering ping has no card and arrives under the
    /// creature that threw it. An empty string is the honest answer for a
    /// beat with none of the three -- a bomb detonating on nobody's turn --
    /// and the page prints the row without a source rather than inventing one.
    /// </summary>
    public static void Note(Reaction reaction, Creature? target,
                            Creature? dealer, CardModel? cardSource)
    {
        if (reaction == Reaction.None) return;
        Rows.Add(new Reacted(
            PrintedName(reaction),
            _attributed is { Length: > 0 } named ? named
                : Named(cardSource) is { Length: > 0 } card ? card
                : Named(dealer),
            Named(target),
            Safe(() => target?.CombatId.ToString())));
    }

    /// <summary>A printed title, or `""`, and never a throw.
    ///
    /// `KokomiPlan.EnemyName`'s bargain and its reason: a display read is a
    /// read of live game objects that a torn-down combat can leave half
    /// standing, and a LOG must never be the thing that ends a beat.
    /// </summary>
    private static string Named(Creature? creature) =>
        Safe(() => creature?.Monster?.Title.GetFormattedText()
                   ?? creature?.Name);

    private static string Named(CardModel? card) =>
        Safe(() => card?.Title.ToString());

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
    /// THE WIRE'S VIEW, `KokomiPlan.Snapshot`'s shape and contract: a list of
    /// plain dictionaries of primitives, reached by REFLECTION from the bridge
    /// because that assembly cannot reference this one. The key names here ARE
    /// the contract and `understudy/blindplay_board.reaction_log` reads them.
    ///
    /// PRESENT AND EMPTY ON A TURN NOTHING REACTED, which is a fact and not a
    /// hole: the page says "nothing reacted this turn" rather than going
    /// silent, and an ABSENT key is a build with no log at all.
    /// </summary>
    public static List<Dictionary<string, object?>> Snapshot() =>
        Rows.ConvertAll(row => new Dictionary<string, object?>
        {
            ["reaction"] = row.Reaction,
            ["source"] = row.Source,
            ["target"] = row.Target,
            ["combat_id"] = row.CombatId,
            // `EB-710`. WHICH SIDE OF THE PLAYER'S LAST END-TURN THIS ROW IS
            // ON. A carried row is true and the page says so on the line
            // rather than filing it under "this turn", because the heading
            // names a window and a row that happened outside it would make the
            // heading the second false thing on the screen.
            ["carried"] = row.Carried,
        });
}
