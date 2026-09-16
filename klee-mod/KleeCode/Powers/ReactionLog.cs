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
    /// <summary>One reaction, as the page prints it.</summary>
    public readonly record struct Reacted(
        string Reaction, string Source, string Target, string CombatId);

    private static readonly List<Reacted> Rows = new();

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

    /// <summary>Drop the turn's rows. Called from
    /// <see cref="ReactionEffects.MarkTurnStart"/> and its extra-turn twin, so
    /// the window is exactly the one every other per-turn reaction fact
    /// keeps.</summary>
    public static void MarkTurnStart() => Rows.Clear();

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
        });
}
