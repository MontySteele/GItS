using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// DRAFT 6's ONE RULE: <b>Plan</b>. A card with a Plan line can be played on
/// the Bake-Kurage instead of where it would normally go; its cost is paid now,
/// and at the start of her next turn the jellyfish carries out the Plan line.
///
/// THE QUEUE IS TYPED, NOT A CLOSURE, and that is still the load-bearing
/// decision in this file. A Plan has to survive the play that wrote it, cross a
/// turn boundary and then resolve with a live <c>PlayerChoiceContext</c> it did
/// not have when it was written -- so a captured lambda over the writing card's
/// context would be a use-after-free waiting to happen. Instead every Plan is a
/// <see cref="Entry"/>: the card that wrote it, plus the <see cref="Planned"/>
/// clauses off its own <see cref="IPlannedCard.PlanClauses"/>. The
/// <see cref="Kind"/>s below are exactly the clauses draft 6 prints; a body the
/// emitter does not understand is a build failure, never an approximation.
///
/// ONE ENTRY IS ONE PLAN, and that is the unit everything downstream counts in:
/// the pending badge, the strip on the jellyfish, Change of Plans' "your front
/// Plan", Nereid's Ascension's "carries out every Plan twice" and the
/// whenever-a-Plan-is-carried-out payoffs (Treatise, Song of Pearls). War
/// Council prints two clauses and is ONE Plan, which is what its face says --
/// "Deal 4 damage to every enemy AND apply 1 Weak to each" is one sentence.
///
/// IN ORDER, and the order is the writing order (slice sec.2 rule 3: "Plans are
/// carried out in the order they were written").
/// <see cref="ProtoBakeKuragePower.AfterPlayerTurnStart"/> is the resolution
/// point and its header says why that hook and not the one the packet's prose
/// names.
///
/// THE JELLYFISH IS THE DEALER, KOKOMI IS THE APPLIER (`EB-334`, R246 pick 1).
/// The slice's sec.5 gave a planned hit her Strength and her Weak; round four-c
/// watched a Strategic enemy's Weak shrink two banked Plans while the enemy's
/// own Vulnerable raised none, which is the wrong way round if the Bake-Kurage
/// is the one hitting. So a planned hit goes out through
/// <see cref="ElementalHit"/> UNPOWERED -- no Strength, no Weak, no attack buff
/// of hers -- while the APPLIER stays her, which keeps the aura, the reaction
/// and the debuffs a reaction applies exactly where rule 3 put them. The whole
/// argument, both halves, is on <see cref="Hit"/>.
///
/// PER PLAYER, for the reason every other per-seat table in this mod is per
/// player (R205): in co-op the other seat's plans are not hers.
///
/// THE BADGE IS <see cref="PendingPlansPower"/>, a plain Counter power carrying
/// the queue's length, kept in step by <see cref="Sync"/> -- the existing badge
/// rendering, nothing new drawn.
/// </summary>
public static class KokomiPlan
{
    /// <summary>
    /// The clauses draft 6's Plan lines print, and nothing else.
    ///
    /// Stolen Chapter draws, Battle Plan pays energy and draws, Read the Field
    /// blocks, The Moon (A Ship O'er the Seas) Mends, Feint and Ambush and
    /// Kurage's Oath and War Council hit, Sango Isshin hits for a quarter of
    /// her Max HP, Chain of Command hits per Companion she played last turn,
    /// Slack Water and Exposed Flank and Vanguard and Coral Bulwark debuff,
    /// and Moon's Reflection replays a card out of the exhaust pile that had
    /// no Plan line of its own.
    ///
    /// NEREID'S ASCENSION IS OFF THIS LIST (`EB-492`). The Rare used to print
    /// "Plan: for 2 turns, the jellyfish carries out every Plan twice" and so
    /// spent the very morning it was meant to pay for; it is a POWER now
    /// (<see cref="NereidsAscensionPower"/>), and the `PlanTwice` clause is
    /// RETIRED rather than left standing unreachable -- a clause no row can
    /// spell is a rule nothing enforces.
    /// </summary>
    public enum Kind
    {
        Draw,
        Energy,
        Block,
        Mend,
        Damage,
        DamageQuarterMaxHp,
        DamagePerCompanionLastTurn,
        ApplyWeak,
        ApplyVulnerable,
        ReplayExhausted,
        // R236, Gorou's Crystal Collapse (the Inazuma workshop's one
        // Personal): "Plan: play a copy of the last other Companion card you
        // played this turn." The card it holds is captured when the Plan is
        // WRITTEN -- see <see cref="Schedule"/> -- and a copy of it is played
        // for free at the morning.
        PlayCopyOfCompanion,
        // `EB-335`, R246 pick 2. Tide Wall: "Plan: Gain 3 Block for each Plan
        // the Bake-Kurage carries out this morning." The count is the whole
        // morning's depth, taken once at the drain
        // (<see cref="KokomiOverhaulLedger.PlansThisMorning"/>), so a Tide Wall
        // written first, second or last in the queue pays the same number.
        BlockPerPlanThisMorning,
    }

    /// <summary>
    /// Where a clause lands. Rule 3: "A planned hit lands on the front enemy
    /// (leftmost alive) unless the line says every enemy." A self-facing clause
    /// (draw, energy, block, Mend, the doubling) takes <see cref="Self"/> and
    /// prints no target at all.
    ///
    /// NO STORED CREATURE, deliberately, and that is the difference from draft
    /// 2's queue: a Plan written last turn cannot hold a reference to an enemy
    /// that may be dead, escaped or replaced by the time it resolves, so the
    /// target is a RULE resolved at carry-out rather than a pointer captured at
    /// writing. It also makes the strip honest -- what it draws is what will
    /// happen, not what was true when the card was played.
    ///
    /// <see cref="EnemiesIntendingAttack"/> IS THE ONE AIM THAT LOOKS BACK, and
    /// it looks at IDs rather than at creatures (`EB-492`, Flank). "Each enemy
    /// that intends to attack" is a fact about the intents ON SCREEN WHEN THE
    /// PLAN WAS WRITTEN -- that is what a player is reading when they choose to
    /// write it, and re-asking the board at carry-out would answer about NEXT
    /// turn's intents instead. So the SET is fixed at writing and stored on the
    /// clause as <see cref="Planned.Targets"/>, a list of
    /// <c>Creature.CombatId</c>s: an enemy whose intent later changes is still
    /// hit, and one that died is simply not on the board to resolve. Ids and
    /// not references keeps the rule above intact -- nothing here holds a
    /// creature the game has torn down.
    /// </summary>
    public enum Aim
    {
        Self,
        FrontEnemy,
        AllEnemies,
        EnemiesIntendingAttack,
    }

    /// <summary>
    /// One scheduled clause. <paramref name="Card"/> is set for
    /// <see cref="Kind.ReplayExhausted"/> (Moon's Reflection's chosen card)
    /// and for <see cref="Kind.PlayCopyOfCompanion"/> (Crystal Collapse's
    /// captured Companion), and is the one place a Plan holds an object rather
    /// than a number. Both are filled in when the Plan is written, never read
    /// off the board at carry-out.
    ///
    /// <paramref name="Times"/> IS HOW MANY SEPARATE HITS THE CLAUSE IS
    /// (`EB-492`, Pincer). "Deal 3 damage three times" is three Hydro hits in
    /// sequence and not one hit of nine: each one goes out through
    /// <see cref="Hit"/> on its own, so each is absorbed by Block on its own,
    /// each reacts on its own, and the aim is re-read between them. One is the
    /// default and every clause the sheet wrote before this key existed keeps
    /// its old shape exactly.
    ///
    /// <paramref name="Targets"/> IS <see cref="Aim.EnemiesIntendingAttack"/>'s
    /// CAPTURED SET, by <c>Creature.CombatId</c>, filled in by
    /// <see cref="Schedule"/> at the moment the Plan is written and read by
    /// <see cref="Aimed"/> at carry-out. Empty is a real answer -- a Flank
    /// written into a board of Defends is written and carries out nothing --
    /// and null is "this clause does not aim that way".
    /// </summary>
    public readonly record struct Planned(
        Kind Kind, int Amount, Aim Aim, CardModel? Card = null,
        int Times = 1, IReadOnlyList<string>? Targets = null);

    /// <summary>
    /// ONE PLAN: the card that wrote it and the clauses it wrote. The card is
    /// kept for the DISPLAY -- the strip draws pending Plans face up, in order,
    /// on the jellyfish -- and for nothing else; the clauses are the whole of
    /// what will happen.
    /// </summary>
    public sealed record Entry(CardModel? Source, IReadOnlyList<Planned> Clauses,
                              string? Label = null)
    {
        /// <summary>What the strip prints for this Plan.
        ///
        /// <paramref name="Label"/> WINS WHERE ONE IS SET, and only a Plan
        /// that HOLDS a card sets one (R236): Crystal Collapse's face means a
        /// different thing every time it is written, so the strip has to say
        /// which card it caught -- "Crystal Collapse: Gorou &#8212; Juuga",
        /// or "Crystal Collapse: nothing" for a turn with no other Companion
        /// in it. Every other Plan is its own card's name, unchanged.</summary>
        public string Title => Label ?? Source?.Title.ToString() ?? "Plan";
    }

    /// <summary>
    /// ONE PLAN THAT HAS BEEN CARRIED OUT, as the screen said it (`EB-317`).
    ///
    /// THREE FIELDS AND ONE OF THEM IS THE OTHER TWO. <paramref name="Card"/>
    /// and <paramref name="Number"/> are the row's own shape -- the card that
    /// was carried out and the number its clause produced, null when the
    /// clause produced none. <paramref name="Line"/> is the string the
    /// jellyfish actually SAID, built by <c>Vfx.KurageBeat.Line</c>, and it
    /// rides the wire because the blind page's contract is that it prints the
    /// ON-SCREEN TEXT rather than a second composition of the same parts. Two
    /// composers in two languages is exactly how a page and a screen come to
    /// disagree about words; there is one, and it is C#.
    /// </summary>
    /// <paramref name="Kind"/> AND <paramref name="Asked"/> ARE `EB-426`, AND
    /// THEY SAY WHAT THE FIGURE IS. `Bake-Kurage: Cleansing Wave, 7` puts a
    /// bare 7 in the slot every other line uses for damage and then reports
    /// "no enemy lost HP"; the 7 was BLOCK, cut from the clause's 10 by Frail,
    /// and the r11 seat had to derive both halves. Neither is derivable from
    /// the wire: the line is one string and <paramref name="Number"/> is one
    /// integer, so the clause's own kind and the amount it asked for ride
    /// beside them. Both are the FIRST numbered clause's, which is the clause
    /// <paramref name="Number"/> already belongs to.
    ///
    /// WHICH MODIFIER MOVED IT IS NOT HERE, and that is a limit rather than an
    /// omission: <c>CreatureCmd.GainBlock</c> reports a landed amount and no
    /// attribution, so the honest pair is what was asked and what landed. The
    /// screen's own status rows name the power that sits between them.
    public readonly record struct CarriedOutPlan(
        string Card, int? Number, string Line,
        IReadOnlyList<MovedOn>? Moved, bool OnPlay,
        string? Kind = null, int? Asked = null,
        IReadOnlyList<Rider>? Riders = null, bool Unfinished = false);

    /// <summary>
    /// SOMETHING ELSE THAT LANDED INSIDE ONE PLAN'S WINDOW, by name and by
    /// the number it delivered (`EB-453`).
    ///
    /// THE GAP. <see cref="MovedOn"/> is MEASURED -- HP before the clauses and
    /// HP after -- which is what makes it honest and also what makes it
    /// anonymous: the r13 seat read `War Council, 7 (the 7 is damage)` beside
    /// a body that had lost 9, and the missing 2 was the Tamakushi Casket
    /// answering the Weak the same Plan had just applied. Both numbers were
    /// right and the page could not say why they differed.
    ///
    /// SO THE RIDER NAMES ITSELF. Nothing is re-derived and nothing is
    /// subtracted: a source that lands inside the window says what it is and
    /// what it dealt, at the one line that already knows both
    /// (<c>TamakushiCasket.Strike</c>), and the page prints the delivered
    /// total with that name beside it. A future rider that says nothing here
    /// leaves the page exactly as it was.
    ///
    /// AND WHICH BODY IT LANDED ON (`EB-518`). `EB-453`'s row named the source
    /// and the number and not the target, so a beat that struck ONE body twice
    /// and another once printed three identical entries -- "Tamakushi Casket
    /// 2, Tamakushi Casket 2, Tamakushi Casket 2" -- with nothing to say how
    /// they divided. The r18 seat had predicted 5 + 2 for each of three bodies,
    /// read 1 / 9 / 7 off the board, and concluded a FOURTH strike had gone
    /// unlisted: two of the three had in fact landed on the same body, because
    /// <c>ElementalHit.Deal</c> resolves the reaction BEFORE the hit lands, so
    /// the Plan's own Hydro froze that body and the Casket answered the Frozen
    /// as well as the Weak. Three entries, four events' worth of arithmetic,
    /// and no way to check it.
    ///
    /// <paramref name="CombatId"/> IS THE HANDLE AND <paramref name="Target"/>
    /// IS THE FALLBACK, which is <see cref="MovedOn"/>'s split verbatim and
    /// for its reasons: the page owns the numbered names, and a body the beat
    /// KILLED is off the next board and keeps the title recorded here.
    /// </summary>
    public readonly record struct Rider(string Source, int Amount,
                                        string Target, string CombatId);

    /// <summary>
    /// HOW MUCH THE BOARD ACTUALLY MOVED, on one creature, during one Plan
    /// (`EB-329`).
    ///
    /// <see cref="CarriedOutPlan.Number"/> IS NOT THIS NUMBER AND WAS NEVER
    /// MEANT TO BE. It is what the Plan's FIRST clause produced -- the right
    /// thing for the bubble over the jellyfish, which has room for one word
    /// and one figure -- and three seats read it as the board. On a Plan that
    /// applies a debuff the two are simply different quantities: round-5's
    /// `Exposed Flank, 2` is TWO STACKS OF VULNERABLE, and the HP that moved
    /// on that beat was the Tamakushi Casket's answering strike, 2 raw and 3
    /// against the Vulnerable it had just applied. `Feint+, 19` agreed with
    /// the board only because a damage clause's own landed number happens to
    /// be the damage.
    ///
    /// SO THIS IS MEASURED, NOT COMPUTED. The HP of every enemy is read
    /// before the Plan's clauses run and again after, and the difference is
    /// what a player watched happen -- which folds in the Casket's procs, an
    /// aura's reaction, the target's Vulnerable and anything a future card
    /// adds to the same beat, without this file knowing about any of them.
    /// `EB-317`'s own header said the missing numbers were "still on screen
    /// over its own enemy, drawn by the engine"; a blind page has no screen,
    /// so it gets the subtraction instead.
    ///
    /// <paramref name="CombatId"/> IS THE HANDLE AND <paramref name="Target"/>
    /// IS THE FALLBACK. The page numbers repeated enemies itself and keeps
    /// those numbers for the fight (`blindplay_faces._enemy_names`), so it
    /// resolves the id to the name a reader has been using; a body that DIED
    /// on this beat is off the board the next screen sends and keeps the name
    /// recorded here.
    ///
    /// <paramref name="Absorbed"/> IS `EB-440`, AND IT IS THE OTHER HALF OF
    /// THE SUBTRACTION. HP is not the only bar a Plan moves: the r12 seat
    /// carried `Kurage's Oath+` out into a Defend intent, watched HP go 35 to
    /// 35, saw the aura land, and read the beat as having worked. Every row
    /// above measures HP, so the receipt for that beat was the empty list --
    /// "no enemy lost HP" -- which is true and reads as "nothing happened".
    /// The enemy's BLOCK is read at the same two moments as its HP, so a
    /// morning that spent itself on Block says so with the number it spent.
    /// </summary>
    public readonly record struct MovedOn(
        string Target, string CombatId, int Amount, bool Dead, int Absorbed);

    private static object? _combat;
    private static readonly Dictionary<Player, List<Entry>> _queues = new();

    /// <summary>
    /// The riders landing inside the Plan being resolved RIGHT NOW, or null
    /// between Plans (`EB-453`).
    ///
    /// ONE LIST AND NOT A DICTIONARY PER SEAT, deliberately: a Plan resolves
    /// inside one synchronous beat of one seat's turn, which is the same
    /// window `before` is measured across, and a rider that arrives while no
    /// Plan is running belongs to no Plan and is dropped. `ResolveEntry` saves
    /// and restores the previous value around its own, because a clause can
    /// play a card that resolves a second Plan (Moon's Reflection's replay),
    /// and the inner Plan's riders are the inner Plan's.
    /// </summary>
    private static List<Rider>? _riders;

    /// <summary>
    /// "I landed inside this Plan, I am called X, and I delivered N."
    ///
    /// Called by the rider itself rather than inferred here: this file knows
    /// what the BOARD did (<see cref="MovedOn"/>) and cannot know what caused
    /// any part of it, which is exactly the gap `EB-453` is. Safe to call at
    /// any time -- outside a Plan it does nothing, which is what makes it a
    /// call a rider can make unconditionally.
    ///
    /// `EB-518` ADDS THE BODY, for the reason on <see cref="Rider"/>: three
    /// identical entries cannot be divided among three enemies by a reader,
    /// and the one that struck twice is exactly the one whose arithmetic does
    /// not close. The target is read the way <see cref="MovedOn"/> reads it --
    /// <see cref="EnemyName"/> for the title, <c>CombatId</c> for the handle --
    /// so the page resolves both rows through one lookup.
    /// </summary>
    public static void NoteRider(string source, int amount,
                                 Creature? target = null)
    {
        if (_riders == null || amount <= 0) return;
        _riders.Add(new Rider(source, amount, EnemyName(target),
                              target?.CombatId.ToString() ?? string.Empty));
    }

    /// <summary>
    /// WHAT THE STRIP SHOWS WHILE A MORNING IS RUNNING, and it exists only so
    /// the strip can empty ONE ENTRY AT A TIME IN VIEW (`EB-317`).
    ///
    /// THE QUEUE ITSELF STILL DRAINS IN ONE MOVE, which is the point of doing
    /// it this way rather than popping the real queue per entry. Two rules
    /// depend on the queue being empty for the whole drain -- a Plan written
    /// DURING resolution waits for the next turn, and Change of Plans reached
    /// through Moon's Reflection finds nothing to pull forward -- and the
    /// meter ledger's morning row is ONE note of the whole depth
    /// (`KokomiPlanLedgerTests`). Popping the real queue per entry would move
    /// both. So the DISPLAY gets its own list, and it is display-only:
    /// nothing reads it but <c>Vfx.KokomiPlanStrip</c> through
    /// <see cref="Showing"/>.
    /// </summary>
    private static readonly Dictionary<Player, List<Entry>> _showing = new();

    /// <summary>This turn's carry-out lines, in the order they were said.
    /// Cleared at the top of every morning, so a page never shows yesterday's.
    /// </summary>
    private static readonly
        Dictionary<Player, List<CarriedOutPlan>> _carriedOut = new();

    /// <summary>
    /// TIDE CHART'S PROMISE, per seat (`EB-478`, R257): what the next morning
    /// owes, as a rate per Plan carried out and a flat number beside it.
    ///
    /// TWO NUMBERS AND NOT A LIST OF CARDS, because the promise is arithmetic.
    /// Every copy played this turn adds its own `per` and its own flat, and the
    /// morning after pays <c>Flat + Per * PlansThisMorning</c> in one draw --
    /// so two base copies pay twice the depth, and an upgraded copy beside a
    /// base one adds its extra card once. A list of sources would let two
    /// copies read different counts on one morning, which is a rule nothing
    /// printed. Sim twin: `state.kk_tide_chart_per` / `kk_tide_chart_flat`.
    /// </summary>
    private static readonly Dictionary<Player, (int Per, int Flat)>
        _tideCharts = new();

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
        _tideCharts.Clear();
    }

    private static void Rebase(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (ReferenceEquals(_combat, combat)) return;
        _combat = combat;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
        // A promise is a fact about ONE combat, like the queue above it: a
        // Tide Chart played on the last turn of a fight owes nothing to the
        // next one.
        _tideCharts.Clear();
    }

    /// <summary>This seat's queue, front first. Never null.</summary>
    public static IReadOnlyList<Entry> Pending(Player? player) =>
        player != null && _queues.TryGetValue(player, out var q)
            ? q
            : (IReadOnlyList<Entry>)System.Array.Empty<Entry>();

    /// <summary>
    /// HOW MANY PLANS THE JELLYFISH HOLDS RIGHT NOW -- Tide Chart's count
    /// (the tempo shelf, round 9 pick 1): "draw 1 card for each Plan the
    /// Bake-Kurage holds".
    ///
    /// THE PENDING QUEUE, NOT THE MORNING. "Holds" is what has been WRITTEN
    /// and not yet carried out, which is <see cref="Pending"/>. The morning's
    /// own depth is <c>KokomiOverhaulLedger.PlansThisMorning</c> -- the number
    /// Tide Wall reads -- and it keeps yesterday's value until the next drain,
    /// so a Tide Chart played after the drain would pay for Plans the
    /// jellyfish no longer holds. Sim twin: `effects._runtime_count`'s
    /// `plans_held`, `len(state.kk_plan_queue)` read at the same moment and
    /// for the same reason.
    ///
    /// A CREATURE OVERLOAD because the generated card has a creature at the
    /// call site, and co-op means the seat matters: this is THIS Kokomi's
    /// queue and never the other seat's.
    /// </summary>
    public static int PlansHeld(Creature? kokomi) =>
        Pending(kokomi?.Player).Count;

    /// <summary>
    /// WHAT TO DRAW ON THE JELLYFISH RIGHT NOW: the morning's remaining Plans
    /// while one is running, and the pending queue every other moment.
    ///
    /// The badge is deliberately NOT switched over: `PendingPlansPower` says
    /// "carries out N Plans at the start of your NEXT turn", and during the
    /// drain that number really is zero. The strip says what is happening now.
    /// </summary>
    public static IReadOnlyList<Entry> Showing(Player? player) =>
        player != null && _showing.TryGetValue(player, out var drain)
            ? drain
            : Pending(player);

    /// <summary>This turn's carry-out lines. Never null.</summary>
    public static IReadOnlyList<CarriedOutPlan> CarriedOut(Player? player) =>
        player != null && _carriedOut.TryGetValue(player, out var said)
            ? said
            : (IReadOnlyList<CarriedOutPlan>)
              System.Array.Empty<CarriedOutPlan>();

    /// <summary>
    /// WAS THIS PLAY AIMED AT THE JELLYFISH? The one question the generated
    /// branch asks, and the decompile read is what makes it one line: the play
    /// pipeline hands <c>OnPlay</c> the <c>Creature</c> that was targeted
    /// (<c>CardPlay.Target</c>), so "played on the Bake-Kurage" is a property
    /// of the play rather than of a mode, a keyword or a second card.
    /// </summary>
    public static bool PlayedOnPet(CardPlay cardPlay) =>
        BakeKuragePet.Is(cardPlay.Target);

    /// <summary>
    /// Write one Plan down: rule 2's whole engine side.
    ///
    /// THE MOON OVERLOOKS THE WATERS IS RESOLVED HERE, and "also" is taken at
    /// its word: the Rare's face is "Plans also happen now", so the Plan
    /// happens NOW and is STILL queued for the start of her next turn. Reading
    /// it as "instead" would delete rule 2 rather than break it.
    /// </summary>
    public static async Task Schedule(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? source,
        IReadOnlyList<Planned> clauses)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null || clauses.Count == 0) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue))
        {
            queue = new List<Entry>();
            _queues[player] = queue;
        }
        // R236, CRYSTAL COLLAPSE CAPTURES AT WRITING TIME. "The last other
        // Companion card you played THIS TURN" is a fact about the turn the
        // Plan was written on, and the Plan resolves on the next one -- so
        // asking at carry-out would read a turn the face never named and, on
        // the usual morning, find nothing at all.
        //
        // "OTHER" IS FREE HERE and is asserted anyway. This runs inside
        // `OnPlay`, and the ledger's own recorder is an `AfterCardPlayed`
        // listener, so the card writing the Plan has not been recorded yet;
        // the identity test below says so out loud rather than resting on
        // listener order, and it is the same guard the sim needs for real
        // (there the play is recorded BEFORE the body resolves).
        var body = clauses.ToList();
        string? label = null;
        CardModel? held = null;
        if (body.Any(c => c.Kind == Kind.PlayCopyOfCompanion))
        {
            held = KokomiOverhaulLedger.For(kokomi)
                                       .LastCompanionPlayedThisTurn;
            if (held == source) held = null;
            for (var i = 0; i < body.Count; i++)
            {
                if (body[i].Kind == Kind.PlayCopyOfCompanion)
                {
                    body[i] = body[i] with { Card = held };
                }
            }
            label = Label(source, held);
        }
        // `EB-492`, FLANK CAPTURES ITS SET AT WRITING TIME, and the argument is
        // Crystal Collapse's above with one word changed: "each enemy that
        // intends to attack" is a fact about the intents ON SCREEN NOW, which
        // is what the player is reading when they decide to write the Plan.
        // Asking again at carry-out would answer about the NEXT turn's intents
        // -- a different question, and one the face never asked.
        //
        // AN EMPTY SET IS WRITTEN DOWN rather than refused, exactly as an empty
        // Crystal Collapse capture is: the Plan is real, the strip has to show
        // it, and what it carries out is nothing.
        if (body.Any(c => c.Aim == Aim.EnemiesIntendingAttack))
        {
            var caught = IntendingAttack(kokomi);
            for (var i = 0; i < body.Count; i++)
            {
                if (body[i].Aim == Aim.EnemiesIntendingAttack)
                {
                    body[i] = body[i] with
                    {
                        Targets = caught.Select(e => e.CombatId.ToString())
                                        .ToList(),
                    };
                }
            }
            label = AimedLabel(source, caught);
        }
        var entry = new Entry(source, body, label);
        int before = queue.Count;
        queue.Add(entry);
        await Sync(choiceContext, kokomi,
            SparkPower.SourceOf(source), before);

        // `EB-570`: A PLAN IS ONLY EVER QUEUED HERE. The Moon Overlooks the
        // Waters used to carry the entry out on the spot as well -- "Plans
        // also happen now" -- and that Rare deleted the kit's one question
        // rather than answering it: rule 2 IS the delay, and Battle Plan's
        // Plan line is double its play line, so any now-copy took the price
        // off waiting. The row is withdrawn under R213 B's deletion rule and
        // this door is the writing alone; <see cref="ResolveAll"/> and
        // <see cref="ResolveFront"/> are the two that carry a Plan out.
    }

    /// <summary>
    /// Moon's Reflection: "Choose a card in your exhaust pile: Plan: the
    /// jellyfish carries out its Plan line, or the card itself if it has none."
    ///
    /// TWO CLAUSE SHAPES OUT OF ONE SCREEN, and the card's own face is what
    /// splits them: a chosen card that HAS a Plan line contributes that line
    /// verbatim -- the same typed clauses it would have written itself -- and
    /// one that has none is replayed whole through the game's own free-play
    /// door as a single <see cref="Kind.ReplayExhausted"/> clause. Nothing is
    /// re-derived: an <see cref="IPlannedCard"/> is asked for its own list.
    ///
    /// AN EMPTY EXHAUST PILE IS A NO-OP and not a screen. A selection over
    /// nothing is a click the player cannot answer.
    /// </summary>
    public static async Task ScheduleFromExhaust(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source)
    {
        if (owner == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var pile = CardPile.Get(PileType.Exhaust, owner);
        if (pile == null || pile.Cards.Count == 0) return;

        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(ReflectionPrompt, 1))).FirstOrDefault();
        if (pick == null) return;

        var clauses = pick is IPlannedCard { PlanClauses.Count: > 0 } planned
            ? planned.PlanClauses
            : new[] { new Planned(Kind.ReplayExhausted, 1, Aim.Self, pick) };
        await Schedule(choiceContext, owner.Creature, pick, clauses);
    }

    /// <summary>
    /// What the strip prints for a Plan that HOLDS a card (R236).
    ///
    /// THE SHORT NAME IS THE HALF AFTER THE EM DASH. A companion row is named
    /// "&lt;Character&gt; &#8212; &lt;Card&gt;", so the line reads "Crystal
    /// Collapse: ..." rather than repeating Gorou twice inside one strip
    /// entry. The HELD card keeps its whole name, because that is the card the
    /// player will watch resolve. <c>kokomi_plan.plan_label</c> is the twin.
    /// </summary>
    private static string Label(CardModel? source, CardModel? held)
    {
        var name = source?.Title.ToString() ?? "Plan";
        var cut = name.LastIndexOf('—');
        var shortName = cut >= 0 ? name.Substring(cut + 1).Trim() : name;
        if (shortName.Length == 0) shortName = name;
        var what = held?.Title.ToString() ?? "nothing";
        return $"{shortName}: {what}";
    }

    /// <summary>
    /// THE ENEMIES TELEGRAPHING AN ATTACK RIGHT NOW (`EB-492`, Flank).
    ///
    /// ONE DEFINITION, AND IT IS THE ARM'S EXISTING ONE.
    /// <c>CurtainCallHooks.IntendsAttack</c> is the predicate the Furina arm
    /// already reads for "is any enemy telegraphing an attack" and the sim
    /// already twins (`effects._predicate("enemy_intends_attack")`); a second
    /// intent test written here is exactly how two cards on one board come to
    /// disagree about what an attack was.
    ///
    /// LIVING AND HITTABLE, the same list every other aim resolves over.
    /// </summary>
    private static List<Creature> IntendingAttack(Creature? kokomi) =>
        kokomi?.CombatState?.HittableEnemies
            .Where(IsAlive)
            .Where(CurtainCallHooks.IntendsAttack)
            .ToList() ?? new List<Creature>();

    /// <summary>
    /// What the strip prints for a Plan that CAUGHT A SET (`EB-492`).
    ///
    /// THE SAME ARGUMENT <see cref="Label"/> MAKES, one aim over: a Plan whose
    /// targets were decided when it was written means a different thing every
    /// time it is written, and a player who cannot see which bodies it caught
    /// cannot plan around it. "Flank: nothing" is the honest line for a Plan
    /// written into a board of Defends -- it is queued, it will fire, and it
    /// will hit no one.
    /// </summary>
    private static string AimedLabel(CardModel? source,
                                     IReadOnlyList<Creature> caught)
    {
        var name = source?.Title.ToString() ?? "Plan";
        if (caught.Count == 0) return $"{name}: nothing";
        var names = caught.Select(EnemyName)
                          .Where(n => n.Length > 0)
                          .ToList();
        return names.Count == 0
            ? $"{name}: {caught.Count}"
            : $"{name}: {string.Join(", ", names)}";
    }

    /// <summary>Keyed on the VERB, the way Rally's search screen was: one
    /// screen, one string, however many carriers eventually print it.</summary>
    public const string ReflectionPromptKey =
        "KLEEMOD-KOKOMI_EXHAUST_PLAN.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source.</summary>
    public const string ReflectionPromptText =
        "Choose a card. The Bake-Kurage carries out its Plan line, or the "
      + "card if it has none.";

    private static LocString ReflectionPrompt =>
        new LocString("cards", ReflectionPromptKey);

    /// <summary>
    /// The start of her turn: every Plan she wrote resolves, in order, and the
    /// queue is empty afterwards.
    ///
    /// THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS. A Plan whose body
    /// schedules another Plan would otherwise resolve its own child in the same
    /// turn, which is a rule nothing printed; taking the list first means a
    /// Plan written DURING resolution waits for the next turn like every other.
    /// (Moon's Reflection's replay can reach a card that writes one, so this is
    /// no longer only a discipline.)
    ///
    /// NEREID'S ASCENSION IS READ PER ENTRY, not once for the morning, and it
    /// stays that way now the Rare is a Power (`EB-492`): a Plan carried out
    /// this morning can play a card -- Moon's Reflection's replay reaches one
    /// -- and if that card is the Ascension, the Plans after it in the same
    /// drain are doubled and the ones already carried out are not. Reading the
    /// power once for the morning would have to pick one of those answers in
    /// advance; reading it per entry says what is true when each Plan happens,
    /// which is what "the jellyfish carries out every Plan twice" says.
    /// </summary>
    public static async Task ResolveAll(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;

        Rebase(kokomi);
        // `EB-317`: the morning's own record starts empty, and it starts empty
        // whether or not anything is due -- otherwise a turn with no Plans
        // would leave yesterday's lines on the blind page as if the jellyfish
        // had just said them.
        _carriedOut.Remove(player);
        if (!_queues.TryGetValue(player, out var queue) || queue.Count == 0)
        {
            return;
        }
        var due = new List<Entry>(queue);
        queue.Clear();
        // `EB-335`. THE MORNING'S DEPTH, recorded on the line the queue is
        // drained on and before the first clause runs -- Tide Wall's "for each
        // Plan the Bake-Kurage carries out this morning". Written once rather
        // than counted up inside the loop, so the answer does not depend on
        // where in the queue the Tide Wall sits. `kokomi_plan.resolve_all`
        // records the same number in the same place.
        //
        // `EB-501`. THE DEPTH IS CARRY-OUTS AND NOT ENTRIES. All three readers
        // say "carried out this morning" on their own faces -- Tide Wall, Well
        // Laid and Tide Chart -- and under Nereid's Ascension a one-Plan
        // morning is carried out twice. The r17 seat wrote its Plans under the
        // Ascension and Well Laid paid the written count.
        //
        // STILL READ ONCE, AT THE DRAIN, for the reason above: the answer must
        // not depend on where in the queue the reader sits. The one state it
        // cannot see is an Ascension that ARRIVES mid-morning off a Plan of its
        // own, which the loop below would honour and this number would not.
        // That is the price of order-independence and it is deliberate.
        // `kokomi_plan.resolve_all` multiplies by the same term in the same
        // place.
        KokomiOverhaulLedger.For(kokomi).NoteMorning(
            due.Count * CarryOutTimes(kokomi));
        // The display list is handed over BEFORE the sync, because `Sync`
        // refreshes the strip and the strip reads `Showing`: the badge goes
        // away in the same beat the column stays up, which is the true
        // statement (nothing is pending; four things are happening).
        _showing[player] = new List<Entry>(due);
        await Sync(choiceContext, kokomi, "rule:morning_drain", due.Count);

        try
        {
            foreach (var entry in due)
            {
                var times = CarryOutTimes(kokomi);
                for (var i = 0; i < times; i++)
                {
                    await ResolveEntry(choiceContext, kokomi, entry);
                }
                // ONE THUMBNAIL LEAVES, AFTER ITS PLAN HAS HAPPENED. Front
                // first, so the column shortens from the top in the order the
                // Plans were written -- the order the page prints.
                if (_showing.TryGetValue(player, out var shown)
                    && shown.Count > 0)
                {
                    shown.RemoveAt(0);
                }
                Vfx.KokomiPlanStrip.Refresh(kokomi);
            }
        }
        finally
        {
            // `EB-453`: WHAT THE FIGHT CUT OFF, recorded before the display
            // list that holds it is torn down. On the ordinary path this loop
            // is empty -- every Plan that resolved has already removed its own
            // thumbnail -- so a normal morning's page is unchanged.
            if (_showing.TryGetValue(player, out var left))
            {
                foreach (var entry in left) NoteUnfinished(kokomi, entry);
            }
            // A throw inside a Plan must not leave the strip drawing a morning
            // that is over; the display list is torn down on every path.
            _showing.Remove(player);
            Vfx.KokomiPlanStrip.Refresh(kokomi);
        }
    }

    /// <summary>
    /// TIDE CHART IS PLAYED: the draw is OWED, and paid next morning
    /// (`EB-478`, R257).
    ///
    /// NOTHING IS DRAWN HERE, which is the whole redesign. The old row read
    /// the queue at PLAY time -- "draw 1 card for each Plan the Bake-Kurage
    /// holds" -- and drew zero on three plays out of four, because a seat
    /// plays its cheap cards before it writes its Plans (Kokomi r15). The
    /// promise is written down instead and read after the carry-outs, when
    /// the number it multiplies is a fact rather than a guess.
    ///
    /// <paramref name="flat"/> IS THE UPGRADE'S HALF, folded in by the card
    /// as an <c>IsUpgraded</c> literal rather than carried here as a flag:
    /// this file holds what is owed, and which card owed it is the card's own
    /// business. Sim twin: `kokomi_plan.promise_tide_chart`.
    /// </summary>
    /// <summary>The card's printed title, said once (`EB-503`): the morning's
    /// draw line names the card that promised it, and the page's own naming
    /// rule is "by printed title" (`FurinaReframeLedger`'s replay list makes
    /// the same choice). Sim twin: the `tide_chart_paid` row's own name.
    /// </summary>
    private const string TideChartTitle = "Tide Chart";

    public static void PromiseDraw(Creature? kokomi, int flat, int per)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;
        Rebase(kokomi);
        var owed = _tideCharts.TryGetValue(player, out var had)
            ? had
            : (Per: 0, Flat: 0);
        _tideCharts[player] = (owed.Per + per, owed.Flat + flat);
    }

    /// <summary>
    /// WHAT THIS MORNING OWES: <c>Flat + Per * PlansThisMorning</c>, and zero
    /// when nothing is promised (`EB-478`, R257).
    ///
    /// A PURE READ, split out of the payment for the reason the arithmetic in
    /// <c>KokomiPlanLedgerTests</c> is split out of <c>Sync</c>: a draw needs a
    /// live <c>CombatState</c> and the headless boundary does not reach one,
    /// so the number is checkable here and the DRAW is pinned structurally.
    ///
    /// THE COUNT IS THE MORNING'S DEPTH, <c>PlansThisMorning</c> -- the same
    /// number Tide Wall reads, written at the drain and cleared by the
    /// ledger's own roll, so a morning with no Plans reads an honest zero
    /// rather than yesterday's.
    /// </summary>
    public static int PromisedDraw(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return 0;
        var player = kokomi!.Player;
        if (player == null) return 0;
        if (!_tideCharts.TryGetValue(player, out var owed)) return 0;
        return owed.Flat
             + owed.Per * KokomiOverhaulLedger.For(kokomi).PlansThisMorning;
    }

    /// <summary>
    /// THE MORNING AFTER: every Tide Chart promise is paid, in one draw.
    ///
    /// CALLED ONE LINE AFTER <see cref="ResolveAll"/>, from
    /// <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c>, which is what the
    /// face says -- "after the Bake-Kurage carries out its Plans". Called
    /// unconditionally, because <see cref="ResolveAll"/> returns early on an
    /// empty queue and a promise made on a turn that banked nothing still pays
    /// its flat: the upgraded row draws 1 on an empty morning and the base row
    /// draws 0, which is the ruled reading.
    ///
    /// THE COUNT IS THE MORNING'S DEPTH, <c>PlansThisMorning</c> -- the same
    /// number Tide Wall reads, written at the drain and cleared by the
    /// ledger's own roll, so a morning with no Plans reads an honest zero
    /// rather than yesterday's. Sim twin: `kokomi_plan.pay_tide_charts`.
    /// </summary>
    public static async Task PayPromisedDraws(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;

        Rebase(kokomi);
        var cards = PromisedDraw(kokomi);
        // CLEARED BEFORE THE DRAW, not after: a promise that survived its own
        // payment would pay twice on the next morning, and clearing first is
        // the shape that cannot.
        _tideCharts.Remove(player);
        if (cards <= 0) return;
        await CardPileCmd.Draw(choiceContext, cards, player);
        // `EB-503`. THE ONE PLAN CARD THE BAKE-KURAGE BLOCK NEVER REPORTED ON.
        // The r17 seat had two carry-outs pending, watched one extra card
        // arrive, and found "no line anywhere" -- the draw happens inside the
        // morning, after the jellyfish has finished speaking, and nothing said
        // it was the Tide Chart's.
        //
        // A ROW AND NOT A BEAT, which is `NoteUnfinished`'s split and taken
        // for a second reason here: `KurageBeat.Say` builds an
        // `NSpeechBubbleVfx`, which needs a live scene tree, and this method
        // is one of the few on this class the headless suite can reach
        // (`KokomiOverhaulRuleTests` calls it directly). It still goes through
        // `Record`, the one writer, so the draw files into the same list every
        // carry-out lands in and the page needs to learn nothing --
        // `KurageBeat.Line` gives it the ruled format ("Bake-Kurage: Tide
        // Chart, 3") and `Kind.Draw`'s word the rest ("3 cards drawn").
        //
        // AFTER THE DRAW, not before, because the number the seat is owed is
        // what arrived: this is the one site that knows both that a promise
        // existed and what it came to.
        //
        // `onPlay: false` -- a morning event, so it files with the morning's
        // carry-outs and not with the on-play doors.
        Record(kokomi, new CarriedOutPlan(
            TideChartTitle, cards, Vfx.KurageBeat.Line(TideChartTitle, cards),
            null, false, NumberKind(Kind.Draw), cards, null));
    }

    /// <summary>
    /// How many times ONE Plan is carried out right now: two while Nereid's
    /// Ascension is on her, one otherwise.
    ///
    /// A NAMED READ rather than an inline predicate, because WHERE it is asked
    /// is the rule: <see cref="ResolveAll"/> calls it inside the drain loop,
    /// before each entry, so a Plan written in the same morning the Rare was
    /// played is doubled too -- the power is on her by then.
    ///
    /// A POWER AND NO LONGER A WINDOW (`EB-492`). The Rare is a Power costing
    /// 2 and lasting the fight; there is nothing to tick down, and "every Plan
    /// twice" is read here at the one place the number of carry-outs is
    /// decided.
    /// </summary>
    private static int CarryOutTimes(Creature kokomi) =>
        kokomi.Powers.OfType<NereidsAscensionPower>().Any() ? 2 : 1;

    /// <summary>
    /// Change of Plans: "The jellyfish carries out your front Plan now."
    ///
    /// IT LEAVES THE QUEUE, which is what "carries out" means everywhere else
    /// in the arm -- one resolution moved forward, not a copy. An empty queue
    /// is a printed no-op, the way a Surge on an empty Tide was.
    /// </summary>
    public static async Task ResolveFront(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue) || queue.Count == 0)
        {
            return;
        }
        var front = queue[0];
        int before = queue.Count;
        queue.RemoveAt(0);
        await Sync(choiceContext, kokomi, "rule:carried_out_now", before);
        // `EB-329`: Change of Plans is one of the two mid-turn doors, and its
        // card says so in as many words -- "carries out your front Plan NOW".
        await ResolveNow(choiceContext, kokomi, front);
    }

    /// <summary>
    /// A PLAN CARRIED OUT IN THE MIDDLE OF A TURN (`EB-329`).
    ///
    /// A NAMED METHOD FOR A SINGLE ARGUMENT, and the reason is that the
    /// argument is the whole distinction: the mid-turn door -- Change of
    /// Plans, and since `EB-570` withdrew The Moon Overlooks the Waters it is
    /// the only one -- is the one the page must not file under "at the start
    /// of this turn", and a bare `true` at the call site is a fact no
    /// structural pin can see. Every caller of THIS is on-play by
    /// construction and <see cref="ResolveAll"/> calls
    /// <see cref="ResolveEntry"/> straight, so the split is readable from the
    /// call graph.
    /// </summary>
    private static Task ResolveNow(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry) =>
        ResolveEntry(choiceContext, kokomi, entry, onPlay: true);

    /// <summary>
    /// ONE PLAN CARRIED OUT, which is the unit Treatise and Song of Pearls are
    /// priced in: "Whenever the jellyfish carries out a Plan" is once per
    /// ENTRY, and the notify at the bottom is the only place that fires -- so
    /// Change of Plans' early resolution pays them exactly as the morning's
    /// does.
    ///
    /// <paramref name="onPlay"/> IS WHICH OF THE TWO DOORS THIS CAME
    /// THROUGH (`EB-329`). The morning queue is one and Change of Plans is
    /// the other, which happens in the middle of a turn, so filing both under
    /// "carried these out at the start of this turn" is a false sentence
    /// about WHEN. The round-4c seat read a Plan that fired mid-turn and was
    /// told, on the same screen, both that it had already resolved this
    /// morning and that it was still queued; both were true and neither was
    /// legible. The flag rides the record so the page can head the two apart.
    ///
    /// THE ARGUMENT FOR A PARAMETER RATHER THAN A READ: no power on the
    /// board answers this. `ResolveFront` fires one Plan early off its own
    /// card's face, and nothing about the state it leaves behind says the
    /// MORNING's Plans were on-play. The caller is the only thing that knows,
    /// so the caller says.
    /// </summary>
    private static async Task ResolveEntry(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry,
        bool onPlay = false)
    {
        // `EB-317`, the first half of the beat: THE JELLYFISH ACTS BEFORE THE
        // PLAN LANDS. Awaited, so the clause's damage number arrives after the
        // lunge rather than inside it -- the same argument the casket's strike
        // makes one file over.
        await Vfx.KurageBeat.Act(BakeKuragePet.Of(kokomi));

        // `EB-329`: THE BOARD BEFORE. Read here rather than inside the clause
        // loop because the unit the page prints is ONE PLAN -- War Council is
        // a hit and a Weak and the Casket's answer to the Weak, and a reader
        // asking "what did War Council do" wants the whole beat.
        var before = BoardHp(kokomi);

        // THE NUMBER ON THE LINE IS THE FIRST ONE THE PLAN PRODUCED, and
        // "first" is a reading of a card face: War Council prints "Deal 4
        // damage to ALL enemies and apply 1 Weak to each" and is ONE Plan, so
        // the number a player is watching for is the hit, which is also the
        // clause the sheet wrote first. A Plan whose clauses produce nothing at
        // all (Moon's Reflection's replay, Crystal Collapse's copy) says its
        // name and no number, which is what the row asks for.
        int? number = null;
        // `EB-426`: the first numbered clause's KIND and the amount it asked
        // for, taken beside the number they belong to. `asked` is read BEFORE
        // the clause runs, because two of the three scaled kinds read a ledger
        // the clause itself moves.
        string? kind = null;
        int? asked = null;
        // `EB-453`: the window a rider can name itself in, opened here beside
        // `before` because it closes where `before` is read back. The outer
        // value is saved rather than assumed null: a clause may play a card
        // that resolves a second Plan, and that Plan's riders are its own.
        var outerRiders = _riders;
        var riders = new List<Rider>();
        _riders = riders;
        try
        {
            foreach (var clause in entry.Clauses)
            {
                var wanted = AskedFor(kokomi, clause);
                var produced = await ResolveOne(choiceContext, kokomi, clause);
                if (number == null && produced != null)
                {
                    number = produced;
                    kind = NumberKind(clause.Kind);
                    asked = wanted;
                }
            }
        }
        finally
        {
            // `EB-329`, THE OTHER HALF OF THE ROW: A LINE EVEN WHEN THE PLAN'S
            // KILL ENDS THE FIGHT. The round-5 act-1 seat banked two Plans for
            // an exactly-lethal morning, and "the next screen was the reward
            // screen" -- the beat it had spent a turn setting up was the one
            // beat of the run it never got a receipt for. A combat that ends
            // inside a clause unwinds this method, so the announcement is on
            // the unwind path and not after it. Every number the board already
            // moved is still measured; the clauses that never ran moved
            // nothing, which is the honest reading.
            _riders = outerRiders;
            Announce(kokomi, entry.Title, number, Moved(before, kokomi),
                     onPlay, kind, asked, riders);
        }

        // SANGO ISSHIN's condition, written HERE because this is the one place
        // a Plan is carried out: the morning queue and Change of Plans' early
        // resolution both pass through, and both are the card's printed
        // "carried out a Plan this turn".
        KokomiOverhaulLedger.For(kokomi).NotePlanCarriedOut();

        foreach (var power in kokomi.Powers.ToList())
        {
            if (power is IKokomiPlanListener listener)
            {
                await listener.OnPlanResolved(choiceContext, kokomi);
            }
        }
    }

    /// <summary>
    /// `EB-317`'s second half: SAY WHAT JUST HAPPENED, AND RECORD IT.
    ///
    /// ONE STRING, TWO SURFACES. <c>Vfx.KurageBeat.Line</c> builds the ruled
    /// format once; the bubble over the jellyfish shows it and the wire
    /// carries the same characters to the blind page. The pet says it when
    /// there is a pet -- and Kokomi says it when there is not, the same honest
    /// degradation the casket's dealer takes.
    ///
    /// NOT ON THE LEDGER, and that is `R101b` rather than an oversight: the
    /// meter ledger stays off the page, so what a seat is shown here is the
    /// on-screen line and nothing else.
    /// </summary>
    private static void Announce(Creature kokomi, string card, int? number,
                                 IReadOnlyList<MovedOn>? moved, bool onPlay,
                                 string? kind = null, int? asked = null,
                                 IReadOnlyList<Rider>? riders = null)
    {
        var line = Vfx.KurageBeat.Line(card, number);
        Vfx.KurageBeat.Say(BakeKuragePet.Of(kokomi) ?? kokomi, line);
        Record(kokomi, new CarriedOutPlan(card, number, line, moved, onPlay,
                                          kind, asked, riders));
    }

    /// <summary>
    /// A PLAN THAT NEVER HAPPENED, filed in the order it would have (`EB-453`).
    ///
    /// THE GAP. `ResolveAll` drains the queue in one move and then resolves
    /// the entries one at a time; a kill inside the FIRST one unwinds the loop
    /// and the rest never run. The r13 seat wrote two Plans, was shown one,
    /// and had nothing on the page to say what became of the other -- the
    /// queue is already empty by then and `_showing` is torn down on the way
    /// out, so no surface carried it at all.
    ///
    /// NO BUBBLE, because nothing was said: this is a page row and not a beat.
    /// `Number` is null and `Moved` is null for the same reason -- the board
    /// was not measured across a Plan that did not run, and an empty list here
    /// would read as "measured, and nothing moved".
    /// </summary>
    private static void NoteUnfinished(Creature kokomi, Entry entry) =>
        Record(kokomi, new CarriedOutPlan(
            entry.Title, null, Vfx.KurageBeat.Line(entry.Title, null),
            null, false, null, null, null, Unfinished: true));

    /// <summary>The one writer of the turn's carry-out list, so a beat and a
    /// Plan the fight cut off arrive in one order and by one door.</summary>
    private static void Record(Creature kokomi, CarriedOutPlan row)
    {
        var player = kokomi.Player;
        if (player == null) return;
        if (!_carriedOut.TryGetValue(player, out var said))
        {
            said = new List<CarriedOutPlan>();
            _carriedOut[player] = said;
        }
        said.Add(row);
    }

    /// <summary>
    /// EVERY ENEMY'S HP RIGHT NOW, by combat id, with the name to fall back on
    /// (`EB-329`).
    ///
    /// NULL MEANS "COULD NOT ASK", AND EMPTY MEANS "NO ENEMIES", and the two
    /// are as different here as an absent wire key is from an empty one. A
    /// combat torn down between the two reads would otherwise subtract the
    /// whole board from itself and report every enemy dead of the Plan --
    /// a fabricated receipt, and the worst outcome this row could have.
    ///
    /// `HittableEnemies` AND NOT `Enemies`, and the dead are kept rather than
    /// filtered: a body that dies inside the Plan has to be in the BEFORE map
    /// or its death is a hit nothing recorded, and one already dead when the
    /// Plan starts simply moves zero and drops out of the difference on its
    /// own. Nothing here throws -- a state read never does.
    /// </summary>
    private static Dictionary<string, (string Name, int Hp, int Block)>?
        BoardHp(Creature? kokomi)
    {
        var combat = kokomi?.CombatState;
        if (combat == null) return null;
        var board = new Dictionary<string, (string, int, int)>();
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy == null) continue;
            var id = enemy.CombatId.ToString();
            if (string.IsNullOrEmpty(id)) continue;
            // `EB-440`: BLOCK BESIDE HP, read at the same moment and by the
            // same rule. A Plan that spent itself on a Defend intent moved a
            // bar; which bar is the reader's question and not this method's.
            board[id!] = (EnemyName(enemy), (int)enemy.CurrentHp,
                          (int)enemy.Block);
        }
        return board;
    }

    /// <summary>
    /// THE SUBTRACTION: what each enemy lost between the two reads, or NULL
    /// where either read could not be taken.
    ///
    /// ONLY THE ROWS THAT MOVED. An enemy the Plan never touched is not a
    /// fact about the Plan, and a morning of four Plans against four
    /// Gardeners would otherwise print sixteen rows to say twelve times that
    /// nothing happened. An empty LIST is therefore a real answer -- the Plan
    /// drew cards, or gave Block, and moved no enemy's HP -- which is exactly
    /// what a morning has to say for its arithmetic to close.
    ///
    /// A NEGATIVE DELTA IS DROPPED rather than printed as a heal. Nothing in
    /// the arm heals an enemy today; if something does, "the board moved -3"
    /// is a sentence this row has not been ruled on and inventing one here
    /// would be worse than the silence the seat already reported.
    ///
    /// AND DEATH IS A FIELD. The page cannot infer it -- an enemy at 0 is off
    /// the next board entirely, so "not in the enemy list" is as true of a
    /// creature that died to this Plan as of one that died three turns ago.
    /// </summary>
    private static IReadOnlyList<MovedOn>? Moved(
        Dictionary<string, (string Name, int Hp, int Block)>? before,
        Creature? kokomi)
    {
        var after = BoardHp(kokomi);
        if (before == null || after == null) return null;
        var rows = new List<MovedOn>();
        foreach (var pair in before)
        {
            var was = pair.Value.Hp;
            // A creature MISSING from the after-read has left the board, and
            // the honest reading of that is "it took everything it had left".
            var standing = after.TryGetValue(pair.Key, out var seen);
            var now = standing ? seen.Hp : 0;
            var lost = was - now;
            // `EB-440`: THE BLOCK THE BEAT ATE. A body off the board has no
            // Block left either, and Block a Plan somehow GAVE an enemy is not
            // a thing this row has been ruled on -- the negative delta drops,
            // exactly as a negative HP delta does one line up.
            var absorbed = pair.Value.Block - (standing ? seen.Block : 0);
            if (absorbed < 0) absorbed = 0;
            // A row is now "this Plan moved something on this body", and Block
            // is something: the empty list still means the morning moved no
            // bar at all, which is what a Draw Plan's receipt has to say.
            if (lost <= 0 && absorbed <= 0) continue;
            rows.Add(new MovedOn(pair.Value.Name, pair.Key,
                                 lost > 0 ? lost : 0, now <= 0, absorbed));
        }
        return rows;
    }

    /// <summary>The enemy's printed title, or an empty string where the game
    /// will not answer. A state read must never throw
    /// (<c>Diagnostics.PlayTelemetry.NameOf</c> takes the same posture), and
    /// the page has the combat id to name the creature with anyway.
    ///
    /// `EB-542`: `GetFormattedText` AND NOT `ToString`. A `LocString`'s
    /// `ToString` is its DEBUG form -- "LocString table monsters entry
    /// CORPSE_SLUG.name" -- and that string reached the player-facing
    /// carry-out log on Flank's set line, twice in one fight and again on
    /// floor 5 with `CALCIFIED_CULTIST` and `DAMP_CULTIST` (Kokomi r19 lane 1).
    ///
    /// IT IS THE LOOKUP THE ENEMY LIST ALREADY USES, which is why only this
    /// line showed it: the bridge names every body through
    /// `SafeGetText`, which resolves a `LocString` with `GetFormattedText`, and
    /// every OTHER row this class emits carries a `CombatId` the page renames
    /// from its own fight memory (`MovedOn`, `Rider`). <see cref="AimedLabel"/>
    /// bakes its names into a string with no id on it, so it is the one place
    /// an unresolved title could survive to the screen.
    ///
    /// THE GUARD IS THE SAME GUARD, one call further in: `GetFormattedText`
    /// throws on a model whose loc table has not been built
    /// (<c>SalonPowers.PrintedTitle</c>'s own note), and this is read from
    /// inside a resolution, where a throw reaches the player as a black screen.
    /// </summary>
    private static string EnemyName(Creature? enemy)
    {
        if (enemy == null) return "";
        try
        {
            return enemy.Monster?.Title.GetFormattedText() ?? "";
        }
        catch (System.Exception)
        {
            return "";
        }
    }

    /// <summary>
    /// One clause, and THE NUMBER IT PRODUCED -- damage that landed, Block
    /// that stuck, HP that was Mended, cards drawn -- or null when the clause
    /// produces no number a player could read off the board.
    ///
    /// THE RETURN IS A DISPLAY VALUE AND NOTHING ELSE. Every call below is the
    /// call that was already here; what changed is that the number each one
    /// already computed is now handed back instead of dropped, so the line the
    /// jellyfish says is the number that LANDED rather than the number the
    /// sheet printed. `EB-270` makes the same argument for the Bomb badge, and
    /// <c>ElementalHit.Deal</c> returns its truncated total for exactly this.
    /// </summary>
    private static async Task<int?> ResolveOne(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
    {
        var player = kokomi.Player;
        if (player == null) return null;

        switch (plan.Kind)
        {
            case Kind.Draw:
                await CardPileCmd.Draw(choiceContext, plan.Amount, player);
                return plan.Amount;

            case Kind.Energy:
                await PlayerCmd.GainEnergy(plan.Amount, player);
                return plan.Amount;

            case Kind.Block:
                // POWERED, and rule 3 is why: "your Strength and Dexterity
                // count, since the plans are hers". Draft 2's Plan Block was
                // `Unpowered` on the NC-11 power-sourced-Block line; draft 6
                // states the opposite rule in the brief itself, so a planned
                // Block is `ValueProp.Move` -- the same prop a card's own Block
                // carries, and the same one Dexterity reads.
                return (int)await CreatureCmd.GainBlock(
                    kokomi, plan.Amount, ValueProp.Move, null);

            case Kind.BlockPerPlanThisMorning:
                // TIDE WALL (`EB-335`). POWERED, exactly as the flat planned
                // Block above is and for the same reason: rule 3 says her
                // Dexterity counts, and two Block clauses of one morning
                // scaling differently is what `SongOfPearlsPower`'s header
                // refuses. A morning that drained nothing pays nothing, which
                // is a printed no-op rather than a failure -- Change of Plans
                // can carry this Plan out on a turn whose own morning was
                // empty, and zero times three is the honest answer.
                return (int)await CreatureCmd.GainBlock(
                    kokomi,
                    plan.Amount * KokomiOverhaulLedger.For(kokomi)
                                      .PlansThisMorning,
                    ValueProp.Move, null);

            case Kind.Mend:
                // Mend returns the HP that actually landed, which is the
                // honest number: "Mend 10" into 4 points of room says 4.
                return await KokomiRules.Mend(
                    choiceContext, kokomi, plan.Amount);

            case Kind.Damage:
                return await Hit(choiceContext, kokomi, plan, plan.Amount);

            case Kind.DamageQuarterMaxHp:
                return await Hit(choiceContext, kokomi, plan,
                                 KokomiRules.QuarterOfMaxHp(kokomi));

            case Kind.DamagePerCompanionLastTurn:
                // Chain of Command. "Last turn" is read at CARRY-OUT: the Plan
                // was written on turn N and resolves at the top of N+1, and the
                // ledger has rolled by then, so the count it holds is turn N's
                // -- the turn the player was looking at when they wrote it.
                return await Hit(choiceContext, kokomi, plan,
                                 plan.Amount * KokomiOverhaulLedger.For(kokomi)
                                                   .CompanionsPlayedLastTurn);

            case Kind.ApplyWeak:
                await Debuff<WeakPower>(choiceContext, kokomi, plan);
                return plan.Amount;

            case Kind.ApplyVulnerable:
                await Debuff<VulnerablePower>(choiceContext, kokomi, plan);
                return plan.Amount;

            case Kind.ReplayExhausted:
                // The replayed card prints its own numbers as it resolves; this
                // clause produced none of its own.
                await Replay(choiceContext, player, plan.Card);
                return null;

            case Kind.PlayCopyOfCompanion:
                // The copy prints its own numbers as it resolves; this
                // clause produced none of its own (`EB-317`'s line names
                // the card alone).
                await PlayCopy(choiceContext, kokomi, plan.Card);
                return null;
        }
        return null;
    }

    /// <summary>
    /// WHAT THE NUMBER ON A CARRY-OUT LINE IS, in the word the page prints
    /// (`EB-426`).
    ///
    /// A NAMED METHOD RATHER THAN A MAP, for <see cref="CarriedOutRow"/>'s
    /// reason: these strings are the contract with `understudy/blindplay`, and
    /// `Il.Strings` over a named method is what a headless pin can read.
    ///
    /// NULL WHERE THE CLAUSE PRODUCES NO NUMBER, which is the same set
    /// <see cref="ResolveOne"/> returns null for -- a replay or a copy prints
    /// its own numbers as it resolves. Those lines carry a card name and
    /// nothing else, so there is no figure to label.
    ///
    /// THE THREE DAMAGE KINDS ARE ONE WORD, because they are one quantity: a
    /// flat hit, a quarter of her Max HP and a per-Companion count all land as
    /// damage, and a reader asking what the figure is is not asking how it was
    /// derived.
    /// </summary>
    private static string? NumberKind(Kind kind) => kind switch
    {
        Kind.Draw => "cards drawn",
        Kind.Energy => "Energy",
        Kind.Block or Kind.BlockPerPlanThisMorning => "Block",
        Kind.Mend => "HP healed",
        Kind.Damage or Kind.DamageQuarterMaxHp
            or Kind.DamagePerCompanionLastTurn => "damage",
        Kind.ApplyWeak => "Weak",
        Kind.ApplyVulnerable => "Vulnerable",
        _ => null,
    };

    /// <summary>
    /// WHAT THE CLAUSE ASKED FOR, before the board had its say (`EB-426`).
    ///
    /// The other half of the seat's derivation: `Cleansing Wave, 7` is a Plan
    /// that asked for 10 and was cut by Frail, and the page can only say so
    /// where it is told the 10. For most kinds that is the clause's own
    /// <c>Amount</c>; the three scaled ones compute it exactly as
    /// <see cref="ResolveOne"/> does, which is why this is a method beside it
    /// rather than a second reading of the same rule somewhere else.
    ///
    /// CALLED BEFORE THE CLAUSE RUNS. Two of the three read a ledger the
    /// clause itself moves -- Tide Wall counts the morning's Plans, Chain of
    /// Command last turn's Companions -- so asking afterwards would answer a
    /// different question.
    /// </summary>
    private static int? AskedFor(Creature kokomi, Planned plan) => plan.Kind
        switch
    {
        Kind.BlockPerPlanThisMorning =>
            plan.Amount * KokomiOverhaulLedger.For(kokomi).PlansThisMorning,
        Kind.DamagePerCompanionLastTurn =>
            plan.Amount * KokomiOverhaulLedger.For(kokomi)
                              .CompanionsPlayedLastTurn,
        Kind.DamageQuarterMaxHp => KokomiRules.QuarterOfMaxHp(kokomi),
        _ => plan.Amount,
    };

    /// <summary>
    /// The front enemy: leftmost alive, SKIPPING A MINION (`R250`, round-5
    /// sec.6 pick 1 at its default). <c>CombatState.Enemies</c> is board order
    /// (it is sorted by encounter slot), so "leftmost" is the first hittable
    /// one and needs no second definition -- but two round-5 formations put a
    /// decoy there on purpose: The Kin's Followers absorbed a Feint Plan for
    /// the Priest, and Queen's Torch Head Amalgam took every single-target
    /// Plan for a whole fight (round-5 packet sec.2). Both already carry
    /// <see cref="MinionPower"/>, the base game's own "secondary enemy" mark,
    /// so this reads it rather than inventing a second one. Falls back to the
    /// leftmost Minion when the board is Minions alone, because a Plan that
    /// lands on nothing is worse than one that lands on the decoy.
    /// </summary>
    public static Creature? FrontEnemy(Creature? kokomi)
    {
        var hittable = kokomi?.CombatState?.HittableEnemies
            .Where(IsAlive).ToList();
        if (hittable == null || hittable.Count == 0) return null;
        return hittable.FirstOrDefault(IsNotMinion) ?? hittable[0];
    }

    private static bool IsAlive(Creature e) => !e.IsDead;

    /// <summary>Named rather than inline so the Minion read is one call a
    /// structural pin can see directly, the same reason the base library's
    /// own predicates are named methods.</summary>
    private static bool IsNotMinion(Creature e) =>
        !e.Powers.OfType<MinionPower>().Any();

    /// <summary>
    /// The bodies one clause lands on, resolved AT CARRY-OUT.
    ///
    /// THE WHOLE CLAUSE AND NOT JUST ITS AIM (`EB-492`), because one aim reads
    /// something the clause carries: <see cref="Aim.EnemiesIntendingAttack"/>
    /// resolves the ids <see cref="Schedule"/> captured, filtered to the bodies
    /// STILL ON THE BOARD. An enemy whose intent changed overnight is still in
    /// the set -- the set was the point -- and one that died is off
    /// <c>HittableEnemies</c> and drops out, which is the same "a Plan that
    /// lands on nothing lands on nothing" rule every other aim already keeps.
    /// </summary>
    private static IEnumerable<Creature> Aimed(Creature kokomi, Planned plan)
    {
        var combat = kokomi.CombatState;
        if (combat == null) yield break;
        if (plan.Aim == Aim.EnemiesIntendingAttack)
        {
            var caught = plan.Targets;
            if (caught == null || caught.Count == 0) yield break;
            foreach (var enemy in combat.HittableEnemies.Where(IsAlive)
                                        .ToList())
            {
                if (caught.Contains(enemy.CombatId.ToString()))
                {
                    yield return enemy;
                }
            }
            yield break;
        }
        if (plan.Aim == Aim.AllEnemies)
        {
            foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                        .ToList())
            {
                yield return enemy;
            }
            yield break;
        }
        var front = FrontEnemy(kokomi);
        if (front != null) yield return front;
    }

    /// <summary>
    /// A Plan's damage, and it is HYDRO, DEALT BY THE BAKE-KURAGE.
    ///
    /// <c>EB-334</c>, RULED R246 PICK 1 AT ITS DEFAULT: "the Bake-Kurage deals
    /// it. The enemy's debuffs apply, Kokomi's own Weak and her attack buffs
    /// do not, and the Plan line prints the number it will deal against the
    /// enemy's current state." Round four-c found the arithmetic exactly the
    /// wrong way round: a Strategic enemy's Weak cut two banked Plans to x0.75
    /// the next morning -- 12 to 9 and 5 to 3, with no screen showing it --
    /// while the enemy's own Vulnerable multiplied nothing
    /// (`review/ruled/kokomi-overhaul-round-4c-2026-09-02.md` sec.2, sec.6).
    ///
    /// <c>powered: false</c> IS THAT SENTENCE. It drops
    /// <see cref="SimDamagePipeline.DealerMods"/> and nothing else, so the
    /// aura still lands, the reaction still fires and the TARGET's Vulnerable
    /// still multiplies -- and <see cref="ElementalHit.Deal"/>'s own header
    /// carries the argument for why a flag rather than swapping the applier to
    /// the pet: a Plan-caused Freeze has to stay a debuff SHE applied, or the
    /// Casket stops answering it. Sim twin: `kokomi_plan._hit`, one flag of
    /// the same name on the same funnel.
    ///
    /// THE FACE SAYS THE SAME NUMBER, which is the row's other half:
    /// <see cref="PlanDamageVar"/> previews this hit's one remaining live term
    /// against the front enemy, so the printed Plan line and the morning agree.
    /// </summary>
    /// <remarks>
    /// RETURNS THE FIRST TARGET'S LANDED NUMBER (`EB-317`). An ALL-enemies
    /// clause prints a different number over each enemy -- one aura reacts,
    /// another is Vulnerable -- and the line has room for one. The front
    /// enemy's is the one taken, because that is the enemy a single-target
    /// Plan would have hit and the one the player is looking at; every number
    /// is still on screen over its own enemy, drawn by the engine.
    /// </remarks>
    /// <remarks>
    /// <c>Times</c> IS A LOOP OF WHOLE HITS AND NOT A MULTIPLIER (`EB-492`,
    /// Pincer's "Deal 3 damage three times"). Three hits of 3 and one hit of 9
    /// are different against Block, against an aura and against a body that
    /// dies partway, so each pass goes out through <c>ElementalHit.Deal</c> on
    /// its own and the AIM IS RE-READ between passes -- a front enemy killed by
    /// the first hit hands the next one to the enemy behind it, which is the
    /// same "leftmost alive" rule read twice rather than a second rule.
    /// `kokomi_plan._hit` loops in the same order.
    /// </remarks>
    private static async Task<int?> Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan,
        int amount)
    {
        if (amount <= 0) return null;
        var times = plan.Times < 1 ? 1 : plan.Times;
        int? first = null;
        for (var pass = 0; pass < times; pass++)
        {
            foreach (var target in Aimed(kokomi, plan))
            {
                if (target.IsDead) continue;
                var landed = await ElementalHit.Deal(
                    choiceContext, target, Element.Hydro, amount, kokomi,
                    powered: false);
                first ??= landed;
            }
        }
        return first;
    }

    private static async Task Debuff<T>(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
        where T : PowerModel
    {
        foreach (var target in Aimed(kokomi, plan))
        {
            if (target.IsDead) continue;
            await PowerCmd.Apply<T>(
                choiceContext, target, plan.Amount, applier: kokomi,
                cardSource: null);
        }
    }

    /// <summary>
    /// Moon's Reflection's second shape: replay a card that had no Plan line.
    ///
    /// THE CARD IS MOVED TO HAND AND THEN AUTO-PLAYED, in that order, and the
    /// argument is <c>KurageMemory.Fire</c>'s: a card resolving out of a pile
    /// it is still a member of is a class of bug this mod has already paid for
    /// once, and <c>CardCmd.AutoPlay</c> -- the game's own free-play door -- is
    /// documented against a card that belongs to no pile. Routing through the
    /// hand borrows the game's own membership handling on both sides, so the
    /// play leaves the card wherever its printed keywords say.
    /// </summary>
    private static async Task Replay(
        PlayerChoiceContext choiceContext, Player player, CardModel? card)
    {
        if (card == null) return;
        await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);
        await CardCmd.AutoPlay(choiceContext, card, null);
    }

    /// <summary>
    /// Crystal Collapse's morning (R236): play a free COPY of the Companion
    /// card it caught.
    ///
    /// A COPY, WHICH IS THE DIFFERENCE FROM <see cref="Replay"/> ABOVE. Moon's
    /// Reflection takes the chosen card OUT of the exhaust pile and plays that
    /// instance; this leaves the original wherever the first play sent it and
    /// plays a clone, so the deck is not quietly one card shorter for having
    /// used the Plan. <c>ICombatState.CloneCard</c> is the mod's own clone
    /// door and is what <c>KurageMemory.Fire</c> uses one file over, so the
    /// copy carries the original's upgrade state -- which is what "a copy of
    /// the card you played" says.
    ///
    /// EXHAUSTED AFTER, through the game's own pile rule rather than a special
    /// case: <c>ExhaustOnNextPlay</c> is the flag <c>CardCmd.AutoPlay</c>'s
    /// routing already reads, so the copy leaves play into the exhaust pile
    /// whatever its printed keywords say. A copy that landed in the discard
    /// pile would be a second permanent card in the deck for one Energy.
    ///
    /// THE AIM IS THE PLAN'S OWN, <see cref="FrontEnemy"/>, which is the
    /// reader every planned hit already uses -- so a copied Attack lands where
    /// a planned one would and the arm has one answer to "where does a Plan
    /// point".
    ///
    /// A PLAN THAT CAUGHT NOTHING IS A PRINTED NO-OP, the shape
    /// <see cref="ResolveFront"/>'s empty queue already has: the face says
    /// what it does when there was no other Companion.
    /// </summary>
    private static async Task PlayCopy(
        PlayerChoiceContext choiceContext, Creature kokomi, CardModel? card)
    {
        if (card == null) return;
        if (kokomi.CombatState is not { } combat) return;
        var copy = combat.CloneCard(card);
        copy.ExhaustOnNextPlay = true;
        await CardCmd.AutoPlay(choiceContext, copy, FrontEnemy(kokomi));
    }

    /// One carried-out Plan on the wire (`EB-317`, widened by `EB-329`).
    ///
    /// A NAMED METHOD RATHER THAN A LAMBDA INSIDE <see cref="Snapshot"/>, and
    /// the reason is the pin: these key names are the contract with
    /// `understudy/blindplay.py`, and the only way a headless test can read
    /// them is <c>Il.Strings</c> over the method that holds them. A lambda
    /// compiles into a display class whose name a pin cannot ask for, so the
    /// literals would sit somewhere no test could see -- which is how a
    /// renamed key becomes a silent hole on a seat's page.
    ///
    /// `moved` AND `on_play` ARE `EB-329`'s TWO. The first is the board's own
    /// answer -- what each enemy lost across this Plan, measured rather than
    /// read off a clause -- and the second is which door the Plan came
    /// through, so the page can head a mid-turn firing apart from the
    /// morning's.
    ///
    /// `moved` KEEPS THE SNAPSHOT'S THREE-STATE DISCIPLINE, one level down.
    /// NULL is "this beat could not be measured" (a combat torn down between
    /// the two reads); an EMPTY LIST is "measured, and no enemy lost HP",
    /// which is the true and useful receipt for a Draw or a Block Plan. The
    /// page reads exactly that split -- `blindplay._carried_out_row`'s
    /// `board_read` -- and prints nothing at all for the first, because a
    /// page that said "nothing moved" there would be inventing a board.
    /// </summary>
    private static object? CarriedOutRow(CarriedOutPlan said) =>
        new Dictionary<string, object?>
        {
            ["card"] = said.Card,
            ["number"] = said.Number,
            ["line"] = said.Line,
            ["on_play"] = said.OnPlay,
            ["moved"] = said.Moved?.Select(MovedRow).ToList(),
            // `EB-426`: what the number IS, and what its clause asked for.
            ["kind"] = said.Kind,
            ["asked"] = said.Asked,
            // `EB-453`: what else landed inside this Plan's window, and
            // whether the Plan happened at all.
            ["riders"] = said.Riders?.Select(RiderRow).ToList(),
            ["unfinished"] = said.Unfinished,
        };

    /// One named rider inside one Plan's window (`EB-453`). A named method for
    /// <see cref="CarriedOutRow"/>'s own reason: these keys are read by
    /// `understudy/blindplay._rider_row` and a pin has to see the literals.
    /// `target` and `combat_id` are `EB-518`'s, and they are `MovedRow`'s two
    /// spellings so the page resolves both rows through one lookup.
    private static object? RiderRow(Rider rider) =>
        new Dictionary<string, object?>
        {
            ["source"] = rider.Source,
            ["amount"] = rider.Amount,
            ["target"] = rider.Target,
            ["combat_id"] = rider.CombatId,
        };

    /// One enemy's share of one Plan, on the wire (`EB-329`).
    ///
    /// A NAMED METHOD FOR <see cref="CarriedOutRow"/>'s OWN REASON: these
    /// five keys are read by `understudy/blindplay._moved_row` and a pin has
    /// to be able to see the literals. `absorbed` is `EB-440`'s.
    private static object? MovedRow(MovedOn moved) =>
        new Dictionary<string, object?>
        {
            ["target"] = moved.Target,
            ["combat_id"] = moved.CombatId,
            ["amount"] = moved.Amount,
            ["dead"] = moved.Dead,
            ["absorbed"] = moved.Absorbed,
        };

    /// <summary>
    /// THE WIRE'S VIEW of the queue (`EB-216`, the draft-6 half).
    ///
    /// A PLAIN DICTIONARY OF PRIMITIVES, and the shape is
    /// <c>KurageMemory.Snapshot</c>'s for the reason that one is: the bridge
    /// (<c>vendor/STS2_MCP/gits/GitsKokomiPlan.cs</c>) reaches it by
    /// REFLECTION, because the whole arm is Compile Remove'd from a release
    /// build and a compile-time reference would make the bridge refuse to load
    /// without it. The field names here ARE the contract, and
    /// <c>understudy/blindplay.kokomi_plans</c> reads them.
    ///
    /// THREE STATES, NOT TWO. An ABSENT key means "no Plan rule in this build";
    /// an EMPTY map means "the rule is here and this seat is not playing it";
    /// a populated map is her queue. A reader is entitled to tell those apart,
    /// which is why this returns an empty map rather than null for a Klee.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        var creature = player?.Creature;
        if (player == null || !KokomiOverhaul.LiveFor(creature))
        {
            return snapshot;
        }

        var pending = Pending(player);
        var pet = BakeKuragePet.Of(creature);
        snapshot["pet"] = pet != null;
        snapshot["pet_name"] = "Bake-Kurage";
        // THE ID THE SEAT AIMS AT. `CombatId` is what
        // `ICombatState.GetCreature` resolves, so a Plan is sent through
        // exactly the door an attack aims through -- no second targeting
        // channel and nothing for the two to disagree about.
        snapshot["pet_entity_id"] = pet == null ? null : pet.CombatId.ToString();
        snapshot["pending"] = pending.Count;
        // A DOUBLED MORNING IS A FACT ABOUT THE NEXT TURN, so it rides the
        // snapshot rather than being inferred from a Power's amount: Nereid's
        // Ascension is the one card that makes the queue's LENGTH stop being
        // the number of things that will happen.
        snapshot["twice"] =
            creature!.Powers.OfType<NereidsAscensionPower>().Any();
        snapshot["queue"] = pending
            .Select(entry => (object?)new Dictionary<string, object?>
            {
                ["name"] = entry.Title,
                ["clauses"] = entry.Clauses.Count,
            })
            .ToList();
        // `EB-317`. WHAT THE JELLYFISH HAS ALREADY DONE THIS TURN, in the
        // order it did it, and in the WORDS IT SAID: `line` is the very string
        // the speech bubble carried, so `understudy/blindplay.render` prints
        // the screen's text rather than recomposing it. `card` and `number`
        // ride alongside because a reader that wants the parts should not have
        // to parse the sentence back apart; `number` is null for a Plan whose
        // clauses produced none.
        //
        // PRESENT AND EMPTY ON A TURN WITH NO CARRY-OUT, which is the same
        // three-state discipline the whole snapshot takes: the key is here
        // because the rule is here, and its emptiness is a fact.
        snapshot["carried_out"] =
            CarriedOut(player).Select(CarriedOutRow).ToList();
        return snapshot;
    }

    /// <summary>
    /// Keep the pending-Plans badge AND the strip in step with the queue.
    ///
    /// ONE FUNNEL, called from every site that moves the queue, which is what
    /// makes the badge, the strip and the list that will resolve the same three
    /// views of one number by construction -- the arrangement
    /// `KurageMemory.RefreshStrip` already makes for the memory arm.
    ///
    /// AND THE METER LEDGER RIDES IT (`EB-273`), for that same reason and no
    /// other: a note written anywhere but the one funnel could be skipped by a
    /// future site that moved the queue and only refreshed the badge, and the
    /// ledger's whole claim is that its arithmetic and the number on screen
    /// cannot come from different reads. <c>SparkPower.Gain</c> makes the
    /// argument one file over.
    ///
    /// <paramref name="before"/> IS PASSED IN RATHER THAN READ HERE, and that
    /// is the difference from the Spark sites: by the time this runs the queue
    /// has already moved, and the badge's own amount is a display value the
    /// engine's modifier chain is entitled to have resized. Each caller knows
    /// the depth it started from exactly, so it hands it over.
    /// </summary>
    private static async Task Sync(
        PlayerChoiceContext choiceContext, Creature kokomi, string source,
        int before)
    {
        Vfx.KokomiPlanStrip.Refresh(kokomi);
        var count = Pending(kokomi.Player).Count;
        Diagnostics.MeterLedger.Note(
            Diagnostics.MeterLedger.Plan, source, count - before, before);
        var badge = kokomi.Powers.OfType<PendingPlansPower>().FirstOrDefault();
        if (count == 0)
        {
            if (badge != null) await PowerCmd.Remove(badge);
            return;
        }
        if (badge == null)
        {
            await PowerCmd.Apply<PendingPlansPower>(
                choiceContext, kokomi, count, applier: kokomi,
                cardSource: null, silent: true);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, badge, count - badge.Amount, applier: kokomi,
            cardSource: null, silent: true);
    }

    /// <summary>
    /// WHAT A PLANNED HIT OF <paramref name="amount"/> LANDS FOR RIGHT NOW --
    /// the whole of what `EB-334` left live on a Plan's damage.
    ///
    /// ONE TERM, and naming it is the point: R246 pick 1 took the dealer's
    /// side off a planned hit, so the only modifier between the printed number
    /// and the board is the TARGET's, which is
    /// <see cref="SimDamagePipeline.TargetMods"/> -- the same call
    /// <see cref="ElementalHit.Deal"/> makes on the same target a beat later.
    /// SHARED AND NOT RE-DERIVED, `EB-265`'s rule: the face
    /// (<see cref="PlanDamageVar"/>) and the pins read this, so a face that
    /// disagrees with the morning is a red test rather than a number a seat
    /// stops trusting.
    ///
    /// THE REACTION AMPLIFIER IS DELIBERATELY LEFT OUT, exactly as
    /// <c>ProtoBombPower.PredictedSetOffDamage</c> leaves it out and for the
    /// same reason: it is one-shot rather than standing state, and an
    /// all-enemies Plan consumes the aura the rest of the volley would have
    /// reacted with, so there is no one multiplier for the line.
    /// </summary>
    public static int PlannedDamage(Creature? target, int amount) =>
        target == null
            ? amount
            : (int)SimDamagePipeline.TargetMods(target, amount);

    /// <summary>
    /// THE PLAN LINE'S PRINTED HIT, READ AGAINST THE BOARD -- `EB-334`'s third
    /// clause, and the one a seat can check in one glance: "the Plan line on
    /// the card face prints the number it will deal against the enemy's current
    /// state" (R246 pick 1).
    ///
    /// A PLAIN <see cref="DynamicVar"/> COULD NOT DO IT, and a
    /// <see cref="DamageVar"/> would have been worse. The plain var prints its
    /// stored base, which is what round four-c read while the morning dealt
    /// something else; the game's own attack var runs the ATTACKER's hooks --
    /// her Strength, her Weak, Fantastic Voyage -- which are exactly the terms
    /// the ruling took OFF a planned hit. What is left is one term, the
    /// target's, so this previews one term.
    ///
    /// <c>UpdateCardPreview</c> IS THE SEAM THE GAME ALREADY OWNS: the engine
    /// calls it on every var of a card in hand or in play whenever it refreshes
    /// a face, and <c>PreviewValue</c> is the number <c>{Var:diff()}</c> prints
    /// -- green when it is above the card's own, which is exactly the read a
    /// Vulnerable enemy should produce. <c>IntValue</c> is untouched and stays
    /// <c>BaseValue</c>, which is what matters: the emitted <c>PlanClauses</c>
    /// property builds the queued clause off <c>IntValue</c>, so the number
    /// WRITTEN into the Plan is still the printed base and the multiplier is
    /// applied once, at the morning, by the pipeline.
    ///
    /// THE FRONT ENEMY, not the card's drag target, and for two reasons: a Plan
    /// card is dragged onto the PET, so the target the preview is handed is
    /// never the enemy that will be hit; and an all-enemies clause lands a
    /// different number on each body, so the face takes the front enemy's --
    /// the same enemy <see cref="Hit"/> reports for the same reason (`EB-317`).
    ///
    /// OUTSIDE COMBAT IT PRINTS ITS BASE. A compendium or reward copy has no
    /// combat and no enemies, and `runGlobalHooks` is false off the hand, so
    /// every such read falls through to <c>BaseValue</c> exactly as a plain var
    /// would.
    /// </summary>
    public sealed class PlanDamageVar : DynamicVar
    {
        public PlanDamageVar(decimal amount) : base("PlanDamage", amount)
        {
        }

        public override void UpdateCardPreview(
            CardModel card, CardPreviewMode previewMode, Creature? target,
            bool runGlobalHooks)
        {
            PreviewValue = BaseValue;
            if (!runGlobalHooks) return;
            // A canonical (compendium) copy has no owner and the getter
            // ASSERTS rather than returning null, which is why this guard is
            // the shape `ProtoBombPower.PredictedSetOffDamage` uses.
            if (!card.IsMutable) return;
            var kokomi = card.Owner?.Creature;
            if (!KokomiOverhaul.LiveFor(kokomi)) return;
            var front = FrontEnemy(kokomi);
            if (front == null) return;
            PreviewValue = PlannedDamage(front, (int)BaseValue);
        }
    }
}

/// <summary>
/// A card that prints a <b>Plan</b> line, and the line itself.
///
/// EMITTED, NOT WRITTEN. `gen_klee_cards` builds this member from the row's
/// top-level `plan:` list, so the clauses the queue stores and the clauses the
/// sheet declares are the same declaration.
///
/// PUBLIC because Moon's Reflection asks a card it was handed for its own Plan
/// line, which a private member could not answer.
/// </summary>
public interface IPlannedCard
{
    /// <summary>The card's printed Plan line, in the order it was written.</summary>
    IReadOnlyList<KokomiPlan.Planned> PlanClauses { get; }
}

/// <summary>
/// Treatise's and Song of Pearls' hook: "Whenever the jellyfish carries out a
/// Plan, ...".
///
/// An interface rather than a type test, the same shape
/// <c>IProtoExplosionListener</c> takes and for the same reason: a listener
/// discovered by interface cannot be forgotten at wire-up.
/// </summary>
public interface IKokomiPlanListener
{
    /// <param name="choiceContext">Live context; a listener may draw or deal.</param>
    /// <param name="kokomi">The seat whose Plan was carried out.</param>
    Task OnPlanResolved(PlayerChoiceContext choiceContext, Creature kokomi);
}

/// <summary>
/// The pending-Plans badge (slice sec.5's UI list). It carries no rule at all:
/// <see cref="KokomiPlan"/> owns the queue and this is its display, so the
/// number on screen and the number that will be carried out are the same number
/// by construction. What each of them IS lives on the strip
/// (<c>Vfx/Prototype/KurageMemoryCard.cs</c>), drawn on the jellyfish.
/// </summary>
public sealed class PendingPlansPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Plan"),
        ("description",
            "Carries out [blue]{Amount}[/blue] "
          + "[gold]Plan{Amount:plural:|s}[/gold] at the start of your next "
          + "turn, in order."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
