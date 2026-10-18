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
/// Plan", Nereid's Ascension's "carries out your first Plan twice" and the
/// whenever-a-Plan-is-carried-out payoffs (<see cref="IKokomiPlanListener"/>). War
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
        ApplyWeak,
        ApplyVulnerable,
        ReplayExhausted,
        // R236, Gorou's Crystal Collapse (the Inazuma workshop's one
        // Personal): "Plan: Play a copy of the last Companion card you
        // played" (combat-wide since the Kokomi level pass, 2026-10-12). The
        // card it holds is captured when the Plan is WRITTEN -- see
        // <see cref="Schedule"/> -- and a copy of it is played at the morning.
        PlayCopyOfCompanion,
        // (`EB-685`'s BlockPerPlanHeld left with Dusk, the re-founding,
        // 2026-10-12: Breakwater counts the Plans waiting on its now-line.)
        // Opening Gambit: "the next Plan deals double damage." Second Wave:
        // "the next Plan is carried out twice." A RIDER, written by the entry
        // that prints it and spent by the entry carried out immediately after
        // it in the SAME drain; where none follows, the rider does nothing.
        // <see cref="Drain"/> owns both, and neither is a COUNT: an entry
        // carried out twice under Nereid's Ascension prints its rider twice,
        // and "the next Plan is carried out twice" said twice is still twice
        // -- so the entry it reaches runs <c>CarryOutTimes + 1</c> = 3 and
        // not 4.
        NextPlanDoubleDamage,
        NextPlanExtraCarryOut,
        // R276 PICK 1, THE HALVES REWRITE: Plan lines that buy what only a
        // head start can buy. The three switches mean THIS TURN, the turn the
        // Plan is carried out on:
        //   Pincer: "This turn, your first Attack is played twice."
        //   Battle Plan: "This turn, your Attacks deal N more damage."
        // Feigned Retreat hits harder when she lost no HP since the Plan was
        // WRITTEN (<see cref="Planned.WrittenHp"/>, stamped by
        // <see cref="Schedule"/>), and Tide Wall blocks the largest enemy
        // intent, read at carry-out. Sim twins: `kokomi_plan`, same names.
        FirstAttackTwice,
        BlockMaxIntent,
        // THE CO-OP SET (review/records/coop-set-2026-09-25.md), two clauses
        // about ANOTHER player, and a one-seat fight has none:
        //   Joint Orders: "Plan: They draw 2 cards." THEY is the player the
        //     Plan was written for, captured by <see cref="Schedule"/> onto
        //     <see cref="Planned.Targets"/> as a CombatId and found again at
        //     carry-out; a player who is dead by then draws nothing.
        //   Coordinated Strike: "Plan: Next turn, each other player's Attacks
        //     deal 3 additional damage." Battle Plan's
        //     <see cref="AttackDamageThisTurn"/> mirrored onto every OTHER
        //     living player: the shipped <c>AttackUpThisTurnPower</c> on
        //     each, removed at the end of the player turn it was carried out
        //     on -- which in simultaneous co-op is their turn too.
        // Sim twins: `kokomi_plan`, `ally_draw` and
        // `others_attack_damage_this_turn`, both inert with one seat.
        AllyDraw,
        OthersAttackDamageThisTurn,
        // (The expansion's EnergyIfAlone, DamageIfAlone,
        // BlockPerAttackingEnemy and DoubleBlock left with Lull, Undertide
        // Lance's old Plan and Dusk, the re-founding, 2026-10-12.)
        // POOL COMPLETION (2026-10-01, multiplayer). Tactical Relay: "Plan:
        // Each player gains 1 Energy [and draws 1 card]." EVERY living player
        // in the fight, Kokomi included (<see cref="EachPlayer"/>); the draw
        // is written at 0 on the base card and added by the upgrade. Appended
        // last. Sim twins: `kokomi_plan.EACH_PLAYER_ENERGY` / `_DRAW`.
        EachPlayerEnergy,
        EachPlayerDraw,
        // THE STATUS BATCH (2026-10-01, review/active/kokomi-status-batch-
        // 2026-10-01.md): Kelp Wall's Block per status or curse and Sea Glass
        // Harvest's transform into Sea Glass. THE KOKOMI ROUND-1 FIXES
        // (2026-10-12): both used to read the hand at carry-out, which seats
        // found empty of the statuses they wrote the Plan for. Kelp Wall now
        // counts the hand WHEN WRITTEN (<see cref="Planned.WrittenCount"/>,
        // stamped by <see cref="Schedule"/>: the number the preview showed)
        // and Sea Glass Harvest transforms the DRAW PILE. Bodies in
        // <see cref="KokomiStatusBatch"/>; sim twins `kokomi_plan`, the same
        // names.
        BlockPerStatusInHand,
        TransformStatusesYouHave,
        // THE RE-FOUNDING (2026-10-12, review/active/kokomi-card-paper-
        // 2026-10-12.md). Kurage's Wake's "Add 2 Stings to your hand";
        // Gorou's War Banner "Gain 1 Strength" (permanent since the Kokomi
        // level pass, 2026-10-12) and Juuga "For 3
        // turns, at the end of your turn gain 6 Block" (amount = the turns).
        // Sim twins `kokomi_plan`, the same names. (A written Companion's
        // PlayCompanion left with Kokomi review r9 pick 1 (a), 2026-10-15:
        // only a Companion that prints a Plan line can be planned.)
        AddStings,
        GainStrength,
        JuugaGuard,
        // THE POOL OVERHAUL (2026-10-13, review/active/kokomi-pool-overhaul-
        // 2026-10-13.md sec.2-4; [USER]: "On Kokomi, I'm good with default on
        // 1 and 2."). Three things only a Plan can do:
        //   CHAIN -- Feint, Turning Tide: "Deal N for each Plan carried out
        //     this turn", the ledger's per-turn count, which the carry-out
        //     raises BEFORE its clauses run, so each Chain line counts
        //     itself (<see cref="KokomiOverhaulLedger.PlansCarriedOutThisTurn"/>).
        //   COUNTER -- "since you planned this", from the moment the Plan is
        //     written until it is carried out, read off the entry's own
        //     window (<see cref="Entry.Window"/>): Kelp Wall's damage she
        //     blocked, Turnabout's damage enemies dealt her blocked or not,
        //     Prepared Retreat's "if an enemy attacked you" (and Brine
        //     Sting's <see cref="Aim.EnemiesAttackedSince"/>).
        //   INTENT -- Undercurrent Snare: each enemy that intends to attack
        //     when it lands loses Strength this turn (a temporary loss,
        //     <see cref="UndercurrentSnarePower"/>).
        // And Read the Field's "Put a card from your Draw Pile into your
        // Hand". Sim twins: `kokomi_plan`, the same names.
        DamagePerPlanThisTurn,
        DamageBlockedSince,
        DamageTakenSince,
        EnergyIfAttackedSince,
        LoseStrengthThisTurn,
        DrawPileToHand,
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
    /// <see cref="EnemiesIntendingAttack"/> (`EB-492`, Flank) is "each enemy
    /// that intends to attack", read off the board AT CARRY-OUT since the
    /// Kokomi level pass (2026-10-12), Tide Wall's read. It used to capture
    /// the set when the Plan was written, and seats misread that.
    /// </summary>
    public enum Aim
    {
        Self,
        FrontEnemy,
        AllEnemies,
        EnemiesIntendingAttack,
        // THE POOL OVERHAUL (2026-10-13), Brine Sting: each enemy whose
        // Attack hit her since the Plan was written, read off the entry's
        // window at carry-out.
        EnemiesAttackedSince,
    }

    /// <summary>
    /// One scheduled clause. <paramref name="Card"/> is set for
    /// <see cref="Kind.ReplayExhausted"/> (Moon's Reflection's chosen card),
    /// and for <see cref="Kind.PlayCopyOfCompanion"/> (Crystal Collapse's
    /// captured Companion), and is the one place a Plan holds an object
    /// rather than a number. Both are filled in when the Plan is written, never read
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
    /// <para><paramref name="Alt"/> (R276) is Feigned Retreat's second
    /// printed number, the hit when she lost no HP since the Plan was
    /// written; <paramref name="WrittenHp"/> is her HP at that moment,
    /// stamped by <see cref="Schedule"/> and null until then.</para>
    /// <para><paramref name="WrittenCount"/> (Kokomi round-1 fixes,
    /// 2026-10-12) is Kelp Wall's count of statuses and curses in her hand
    /// when the Plan was written, stamped by <see cref="Schedule"/>; null on
    /// a clause no writer stamped, which reads the hand.</para>
    public readonly record struct Planned(
        Kind Kind, int Amount, Aim Aim, CardModel? Card = null,
        int Times = 1, IReadOnlyList<string>? Targets = null,
        int Alt = 0, int? WrittenHp = null, int StrengthTimes = 1,
        int? WrittenCount = null);

    /// <summary>
    /// ONE PLAN: the card that wrote it and the clauses it wrote. The card is
    /// kept for the DISPLAY -- the strip draws pending Plans face up, in order,
    /// on the jellyfish -- and for nothing else; the clauses are the whole of
    /// what will happen.
    /// </summary>
    /// <param name="AimOverride">`EB-643`. Converging Tide's stamp: the
    /// <c>CombatId</c> of the body every <see cref="Aim.FrontEnemy"/> clause
    /// of this entry lands on instead of the front, or null.
    ///
    /// AN ID AND NOT A CREATURE, which is <see cref="Planned.Targets"/>'
    /// discipline verbatim and for its reason: a Plan written last turn must
    /// not hold a reference to a creature the game has torn down. It is
    /// resolved against the live board at carry-out and falls back to the
    /// front where that body is gone (<see cref="Aimed"/>), which is the
    /// arm's standing rule for a Plan pointed at something it no longer
    /// finds.</param>
    /// <param name="Extra">All Streams Flow to the Sea's gift: this entry is
    /// carried out once plus this many more times. Sim twin:
    /// `PlanEntry.extra`.</param>
    /// <param name="Writer">The card a cancel gives back (Kokomi follow-ups,
    /// 2026-10-01), where it is not <paramref name="Source"/>: Moon's
    /// Reflection writes its Plan under the card it FOUND, which stays in the
    /// exhaust pile, and what cancelling that Plan undoes is Moon's
    /// Reflection. Sim twin: `PlanEntry.card_id`, which is already the
    /// writing card.</param>
    /// <param name="Now">A PLAN STAYS OPEN (2026-10-01): the player flipped
    /// this waiting Plan to its now-line (<see cref="Flip"/>, pick 5a). Every
    /// carry-out of the entry takes it.
    /// Sim twin: `PlanEntry.line == "now"`.</param>
    /// <param name="Window">THE POOL OVERHAUL (2026-10-13): "since you
    /// planned this" -- the ledger's running totals at the moment this Plan
    /// was written (<see cref="KokomiOverhaulLedger.OpenWindow"/>), so a
    /// Counter clause reads the difference and each Plan has its own window.
    /// Null on an entry nobody stamped, which reads nothing. Sim twin:
    /// `PlanEntry.since_blocked` and the two beside it.</param>
    public sealed record Entry(CardModel? Source, IReadOnlyList<Planned> Clauses,
                              string? Label = null,
                              string? AimOverride = null,
                              int Extra = 0, CardModel? Writer = null,
                              bool Now = false,
                              KokomiOverhaulLedger.Since? Window = null,
                              int? WrittenStrength = null)
    {
        /// <summary>A PLAN STAYS OPEN: does this Plan offer the choice? A
        /// two-line card's own line (Moon's Reflection's found card
        /// included). Sim twin: `kokomi_plan.two_line`.</summary>
        public bool TwoLine => Source is INowLineCard;

        /// <summary>The card a cancel returns to the hand.</summary>
        public CardModel? Returns => Writer ?? Source;

        /// <summary>What the strip prints for this Plan.
        ///
        /// <paramref name="Label"/> WINS WHERE ONE IS SET, and only a Plan
        /// that HOLDS a card sets one (R236): Crystal Collapse's face means a
        /// different thing every time it is written, so the strip has to say
        /// which card it caught -- "Crystal Collapse: Gorou &#8212; Juuga",
        /// or "Crystal Collapse: nothing" for a turn with no other Companion
        /// in it. Every other Plan is its own card's name, unchanged. (The
        /// "Dusk: " prefix left with Dusk, 2026-10-12.)</summary>
        public string Title =>
            Label ?? Source?.Title.ToString() ?? "Plan";
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
        IReadOnlyList<Rider>? Riders = null, bool Unfinished = false,
        bool NoTarget = false, IReadOnlyList<string>? Reactions = null,
        string? Again = null);

    /// <summary>KOKOMI REVIEW R8 (2026-10-14, item 9): the Elemental
    /// Reactions a carry-out's own hits set off, by name, in order. A
    /// Masterstroke written for 42 landed 63 on a Pyro body: the Plan's Hydro
    /// Vaporized it, and the receipt said only "the clause asked for 42",
    /// because the target died and nothing on the next board could name the
    /// bonus. Filled inside the carrying window (<see cref="NoteReaction"/>)
    /// and read onto the row as <c>reactions</c>.</summary>
    private static readonly Dictionary<Player, List<string>> _reactions = new();

    /// <summary>KOKOMI REVIEW R9 (2026-10-15, item 6): the seats inside an
    /// end-of-turn summon's volley now, and the reactions each volley set
    /// off. <see cref="Summon"/> opens and closes the window.</summary>
    private static readonly HashSet<Player> _summoning = new();
    private static readonly Dictionary<Player, List<string>> _summonReactions
        = new();

    /// <summary>A reaction just resolved with <paramref name="dealer"/> as
    /// its dealer. Inside a carry-out of hers it is the Plan's, and its name
    /// goes on that carry-out's receipt; anywhere else nothing. Called by
    /// <c>CompanionOverhaulReactions.Note</c>. Display only.</summary>
    public static void NoteReaction(Creature? dealer, Reaction reaction)
    {
        var seat = dealer?.Player;
        if (seat == null || reaction == Reaction.None) return;
        // KOKOMI REVIEW R9 (2026-10-15, item 6): and inside an end-of-turn
        // summon's volley (Sanctifying Ring), whose row names it.
        if (_summoning.Contains(seat))
        {
            if (!_summonReactions.TryGetValue(seat, out var said))
            {
                _summonReactions[seat] = said = new List<string>();
            }
            said.Add(ReactionName(reaction));
        }
        if (!IsCarryingOut(seat)) return;
        if (!_reactions.TryGetValue(seat, out var names))
        {
            _reactions[seat] = names = new List<string>();
        }
        names.Add(ReactionName(reaction));
    }

    /// <summary>A reaction as the page prints it. PURE.</summary>
    public static string ReactionName(Reaction reaction) => reaction switch
    {
        Reaction.ElectroCharged => "Electro-Charged",
        Reaction.Overload => "Overloaded",
        _ => reaction.ToString(),
    };

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
    /// (the Tamakushi Casket's strike, retired 2026-09-28), and the page prints the delivered
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

    /// <summary>
    /// THE TWO-PLAN CAP -- A LANE RULE BEHIND A RUNTIME TOGGLE, DEFAULT OFF
    /// (`EB-643`, R265). "At most N Plans a morning; the rest wait, in order."
    ///
    /// ZERO IS UNLIMITED AND ZERO IS THE DEFAULT, so an unconfigured build
    /// drains exactly what it drained before -- the trial is a trial, and a
    /// lane that did not ask for it must not get it.
    ///
    /// READ FROM THE ENVIRONMENT, ONCE, AT FIRST ASK, and that is the existing
    /// per-lane pattern rather than a new one: `GITS_LANE` is how a lane
    /// declares itself to the harness and `GITS_TELEMETRY_FEED` /
    /// `GITS_TELEMETRY_INTENT` are how a harness tells THIS MOD what run it is
    /// driving (<see cref="Diagnostics.PlayTelemetry"/>, whose `Intent()` this
    /// method is shaped after down to the cache). The seats launch a lane's
    /// game as a child process, so an exported variable is what a lane already
    /// has and a rebuild per arm is what the toggle exists to avoid.
    ///
    /// READ ONCE PER SESSION, for `Intent()`'s reason word for word: the cap
    /// is a statement about the run you are about to play, and re-reading it
    /// mid-session would let one run's mornings disagree with each other about
    /// what rule they were under. Anything unparseable, negative or absent is
    /// 0 -- "nobody declared a cap" and "somebody declared nonsense" should
    /// look the same in a column, and neither is worth a throw inside a turn.
    ///
    /// NOT A `lint_constant_parity` MIRROR. `C.KOKOMI_PLAN_CAP` is the sim's
    /// twin RULE and never the same literal: that one is a module constant a
    /// test monkeypatches and this one is an environment read a lane sets, so
    /// comparing the two defaults by value would pin 0 against 0 and say
    /// nothing about the thing they share.
    /// </summary>
    private const string PlanCapEnvVar = "GITS_KOKOMI_PLAN_CAP";

    private static int? _planCap;

    public static int PlanCap
    {
        get
        {
            if (_planCap is { } cached) return cached;
            var declared =
                System.Environment.GetEnvironmentVariable(PlanCapEnvVar);
            if (!int.TryParse(declared, out var cap) || cap < 0) cap = 0;
            return (_planCap = cap).Value;
        }
    }

    /// <summary>
    /// `EB-653` (Kokomi r24). THE SENTENCE THE CAP PRINTS, IN ONE PLACE.
    ///
    /// THE FIND. Under `GITS_KOKOMI_PLAN_CAP=2` the r24 lane wrote four Plans
    /// and the jellyfish carried out two, four mornings running, and NO SCREEN
    /// SAID SO -- while the blind page's own panel printed "the number on the
    /// Plan badge is how many are written, not a limit". The seat's verdict:
    /// "either the cap is real and the panel's sentence is false, or the panel
    /// is right and the carry-out is dropping Plans". The cap is real, so the
    /// sentence was false, and the rule was read as a WALL for three
    /// occurrences before it was read as a choice.
    ///
    /// A CLAUSE ON TWO FACES AND NOT A THIRD SURFACE. The rule binds where the
    /// Plans are held, so it prints on the two badges that describe holding
    /// them -- <c>ProtoBakeKuragePower</c>, which says what the jellyfish does
    /// with a Plan, and <see cref="PendingPlansPower"/>, which says how many
    /// are waiting. The `Plan` keyword tip is at its 135-character ceiling
    /// (`ArmKeywordTips.ForPlan`) and cannot carry a word more.
    ///
    /// EMPTY AT 0, WHICH IS THE DEFAULT, so an unconfigured build prints
    /// exactly the two faces it always printed -- the trial is a trial, and a
    /// lane that did not ask for the rule must not be told about it.
    ///
    /// ONE FORMAT STRING, so the two faces cannot drift and
    /// `lint_text_conventions` can measure the capped face by reading the
    /// constant rather than counting an identifier as one numeral. Page twin:
    /// `blindplay_notes.PLAN_COUNT_CAPPED_NOTE`, which does not re-spell the
    /// rule -- it READS this sentence off the wire (`EB-653`'s other half).
    /// </summary>
    /// <summary>
    /// `EB-650`, R266 (2026-09-07). THE SENTENCE SAID "A TURN" AND THE RULE IS
    /// ABOUT THE MORNING. The Dusk drain (retired 2026-10-12) was not capped
    /// -- a Dusk Plan had waited for nothing -- so under a declared cap a turn could
    /// carry out more Plans than the face claimed was its limit, which is the
    /// r24 defect one word over. "At the start of your turn" is the drain the
    /// cap binds.
    /// </summary>
    private const string CapSentenceFormat =
        " Carries out at most {0} at the start of your turn; the rest wait "
      + "in order.";

    /// <summary>The cap's sentence for a face, or empty where no cap was
    /// declared. See <see cref="CapSentenceFormat"/>.</summary>
    public static string CapSentence =>
        PlanCap > 0
            ? string.Format(CapSentenceFormat, PlanCap)
            : string.Empty;

    private static object? _combat;
    private static readonly Dictionary<Player, List<Entry>> _queues = new();

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

    /// <summary>The players whose morning drain is running right now
    /// (<see cref="ResolveAll"/>). Read by <see cref="Hit"/> alone: a dusk or
    /// on-play carry-out is not followed by a turn-start tick in the same beat,
    /// so only a morning hit spares its aura.</summary>
    private static readonly HashSet<Player> _morning = new();

    /// <summary>Is <paramref name="kokomi"/>'s morning drain running now?
    /// Read by Following Current (Kokomi review r6, 2026-10-14), whose hit
    /// spares its Hydro the turn-start tick as a Plan's own hit does.</summary>
    public static bool InMorning(Creature? kokomi) =>
        kokomi?.Player is { } player && _morning.Contains(player);

    /// <summary>THE RE-FOUNDING (2026-10-12): the seats whose Plan is being
    /// carried out right now, one entry's clauses at a time
    /// (<see cref="ResolveEntry"/>). Grand Strategist reads it.</summary>
    private static readonly HashSet<Player> _carrying = new();

    /// <summary>The seats whose carry-out had a hit with no living body to
    /// aim at (an earlier Plan that morning killed it). <see cref="Hit"/>
    /// marks it inside the carrying window; the carry-out's row reads it as
    /// <c>no_target</c>, so the page can tell "its target was already dead"
    /// from a Plan that missed (Kokomi round 5, lane 3).</summary>
    private static readonly HashSet<Player> _aimedAtNoOne = new();

    /// <summary>Is a Plan of this seat being carried out right now? Grand
    /// Strategist's "Whenever a Plan causes an Elemental Reaction": a
    /// reaction inside this window was caused by the Plan -- its own hit, or
    /// the hit of a card it plays (Crystal Collapse's copy). Sim twin:
    /// `state.kk_carrying_out`.</summary>
    public static bool IsCarryingOut(Player? player) =>
        player != null && _carrying.Contains(player);

    /// <summary>This turn's carry-out lines, in the order they were said.
    /// Cleared at the top of every morning, so a page never shows yesterday's.
    /// </summary>
    private static readonly
        Dictionary<Player, List<CarriedOutPlan>> _carriedOut = new();

    /// <summary>
    /// `EB-654` (Kokomi r24). WHAT A COMPANION SUMMON DID AT THE END OF THE
    /// LAST TURN, in the carry-out log's own rows.
    ///
    /// THE FIND. "Yae Miko's Sakura took 10 HP off an enemy with no line in
    /// the log" -- the summon's hit is the one thing on this board that moves
    /// a bar and names nothing, where a Plan carry-out prints a line and the
    /// Tamakushi Casket's answering strike prints one inside the beat it
    /// landed in.
    ///
    /// A SECOND LIST AND NOT <see cref="_carriedOut"/>, and the reason is the
    /// CLOCK. A summon fires at the END of the player's turn and
    /// <see cref="ResolveAll"/> clears the morning's list at the START of the
    /// next one -- so a row filed with the carry-outs would be written after
    /// the last page of one turn and erased before the first page of the next,
    /// which is a receipt no seat could ever read. This list is cleared where
    /// the volleys FIRE (<see cref="OpenSummonLog"/>), so it holds exactly the
    /// last turn-end's hits for the whole of the turn that follows them.
    ///
    /// SAME ROW TYPE, SAME WIRE SHAPE, SAME PAGE RENDERER: the seats already
    /// read <see cref="CarriedOutPlan"/> rows, and a summon's hit is the same
    /// three facts (who acted, what number, what the board lost).
    /// </summary>
    private static readonly
        Dictionary<Player, List<CarriedOutPlan>> _summonHits = new();

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
        _summonHits.Clear();
        _summoning.Clear();
        _summonReactions.Clear();
        _carrying.Clear();
        // `EB-643`: the cached environment read too, so a test that declares a
        // cap and one that does not cannot see each other's answer.
        _planCap = null;
    }

    /// <summary>KOKOMI REVIEW R9 (2026-10-15, item 9): the "last carry-out"
    /// box clears when a combat OPENS. <see cref="Rebase"/> ran only when a
    /// Plan was first written or carried out, so a fight that ended before
    /// either left the fight before it on the page: a Sludge Spinner Plan
    /// showed at a rest site two fights later. Only the two receipt lists;
    /// the queues belong to <see cref="Rebase"/>. Called from
    /// <c>ElementalApplication.BeforeCombatStart</c>.</summary>
    public static void ResetFight()
    {
        _carriedOut.Clear();
        _summonHits.Clear();
        // Co-op state divergence (2026-10-17): a drain or carry-out the last
        // fight left suspended (paused on a choice that never came) never ran
        // its `finally`, so its seat stayed "in the morning" / "carrying out"
        // into the next fight on that machine alone. Cleared on every machine.
        _morning.Clear();
        _carrying.Clear();
        _aimedAtNoOne.Clear();
        _summoning.Clear();
        KokomiRefounding.ResetFight();
    }

    private static void Rebase(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (ReferenceEquals(_combat, combat)) return;
        _combat = combat;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
        // `EB-654`: and last fight's summon hits, for the same reason -- a
        // volley that landed in the fight before owes this one no receipt.
        _summonHits.Clear();
    }

    /// <summary>Kokomi review r9 (2026-10-15, item 4): does this entry write
    /// Opening Gambit's rider ("the next Plan deals double damage") when it
    /// is carried out? Not a flipped two-line Plan, which carries out its
    /// now-line and writes no rider. PURE.</summary>
    public static bool WritesDoubleRider(Entry? entry) =>
        entry != null
        && !(entry.Now && entry.TwoLine)
        && entry.Clauses.Any(c => c.Kind == Kind.NextPlanDoubleDamage);

    /// <summary>Kokomi review r9 (2026-10-15, item 4): will the drain hand
    /// <paramref name="entry"/> the double-damage rider the entry
    /// <paramref name="previous"/> before it wrote? A flipped two-line Plan
    /// carries out its now-line at printed size, so the rider does not reach
    /// it. PURE; <c>Drain</c> is the rule, this is its display twin.</summary>
    public static bool DoubledBy(Entry? previous, Entry entry) =>
        WritesDoubleRider(previous) && !(entry.Now && entry.TwoLine);

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

    /// <summary>What the Companion summons did at the end of the last turn
    /// (`EB-654`). Never null.</summary>
    public static IReadOnlyList<CarriedOutPlan> SummonHits(Player? player) =>
        player != null && _summonHits.TryGetValue(player, out var hit)
            ? hit
            : (IReadOnlyList<CarriedOutPlan>)
              System.Array.Empty<CarriedOutPlan>();

    /// <summary>
    /// `EB-654`. THE LOG OPENS WHERE THE VOLLEYS FIRE, which is what makes the
    /// rows survive the turn boundary they have to be read across: the list
    /// filled at the end of turn N is the list a seat reads on turn N+1, and
    /// it is emptied here, one beat before turn N+1's own volleys go out.
    ///
    /// Called once per creature by <c>CompanionOverhaulTurnEnd</c>, before the
    /// walk. A creature with no seat has no page and files nothing.
    /// </summary>
    public static void OpenSummonLog(Creature? owner)
    {
        var player = owner?.Player;
        if (player != null) _summonHits.Remove(player);
    }

    /// <summary>
    /// `EB-654`. RUN ONE END-OF-TURN SUMMON AND SAY WHAT IT DID.
    ///
    /// THE FIND (Kokomi r24, sec.2 "Smaller"). Yae Miko's Sesshou Sakura took
    /// 10 HP off an enemy and NOTHING named it: the carry-out log prints a
    /// line for every Plan the jellyfish resolves and the Tamakushi Casket
    /// names itself inside the beat it lands in, so a summon's hit was the one
    /// bar on the board that moved anonymously.
    ///
    /// EVERY SUMMON THE SAME WAY, WHICH IS WHY THE SEAM IS HERE. There are
    /// fifteen end-of-turn actors in <c>CompanionOverhaulTurnEnd</c>'s walk
    /// and instrumenting fifteen volley bodies would be fifteen chances to
    /// forget one; wrapping the CALL treats them alike by construction, and a
    /// summon added later joins the log by being called through this door.
    ///
    /// MEASURED, NOT DECLARED. The number is what the BOARD lost across the
    /// volley (<see cref="Moved"/>, the same measurement a Plan's own receipt
    /// takes), so a hit into Vulnerable, a reaction it set off and a second
    /// charge are all inside it -- and a volley that only granted Block, or
    /// that found no target, files no row at all. That is what keeps this a
    /// log of HITS rather than a list of powers on the board.
    ///
    /// THE VOLLEY RUNS EITHER WAY. The measurement is in a `finally`, and an
    /// owner with no seat or a combat torn down mid-volley simply files
    /// nothing: a legibility row must never be able to eat a rule.
    /// </summary>
    public static async Task Summon(
        Creature? owner, string source, System.Func<Task> volley)
    {
        if (volley == null) return;
        if (owner?.Player == null || string.IsNullOrEmpty(source))
        {
            await volley();
            return;
        }
        var before = BoardHp(owner);
        // KOKOMI REVIEW R9 (2026-10-15, item 6): "Poison appeared on enemies
        // after the Ring's tick with no reaction named." The volley's
        // reactions are filed under the summon's own name (the reaction log
        // read "off Kokomi") and ride its row.
        var seat = owner.Player;
        _summoning.Add(seat);
        _summonReactions.Remove(seat);
        using var attribution = ReactionLog.Attribute(source);
        try
        {
            await volley();
        }
        finally
        {
            _summoning.Remove(seat);
            _summonReactions.Remove(seat, out var reactions);
            var moved = Moved(before, owner);
            var lost = moved?.Sum(row => row.Amount) ?? 0;
            if (moved != null && (lost > 0 || reactions is { Count: > 0 }))
            {
                RecordSummon(owner, new CarriedOutPlan(
                    source, lost, SummonLine(source, lost), moved, false,
                    // The word the page prints after the figure, and it is
                    // `NumberKind(Kind.Damage)`'s: what a reader wants to know
                    // is what the number IS, not how it was derived.
                    "damage", Reactions: reactions));
            }
        }
    }

    /// <summary>
    /// The summon line's format, in ONE place so a pin can read it back
    /// without a game -- <c>Vfx.KurageBeat.Line</c>'s arrangement, one actor
    /// over.
    ///
    /// NO `Bake-Kurage:` PREFIX, and that is the whole difference: the
    /// jellyfish did not do this. The source names ITSELF, which is the form
    /// the seats already read on a rider ("Tamakushi Casket 2") and on a
    /// carry-out ("Ambush, 12"), so "Sesshou Sakura, 10" needs no new grammar.
    /// </summary>
    internal static string SummonLine(string source, int number) =>
        $"{source}, {number}";

    /// <summary>The one writer of the summon log, <see cref="Record"/>'s twin
    /// and for its reason: one door, one order.</summary>
    private static void RecordSummon(Creature owner, CarriedOutPlan row)
    {
        var player = owner.Player;
        if (player == null) return;
        if (!_summonHits.TryGetValue(player, out var hits))
        {
            hits = new List<CarriedOutPlan>();
            _summonHits[player] = hits;
        }
        hits.Add(row);
    }

    /// <summary>
    /// WAS THIS PLAY AIMED AT THE JELLYFISH? The one question the generated
    /// branch asks, and the decompile read is what makes it one line: the play
    /// pipeline hands <c>OnPlay</c> the <c>Creature</c> that was targeted
    /// (<c>CardPlay.Target</c>), so "played on the Bake-Kurage" is a property
    /// of the play rather than of a mode, a keyword or a second card.
    ///
    /// `EB-347`: AND ONLY WHEN A PLAYER AIMED IT. Uproar's "Play a random
    /// Attack from your Draw Pile" wrote Slack Water onto the jellyfish as a
    /// Plan instead of playing it at the enemy (Kokomi r4d act 1 fight 3),
    /// while the identical card pulled by the identical Uproar one fight
    /// earlier had gone at the enemy -- a screen contradicting itself. The
    /// roll is <c>BaseLib.Patches.Features.AutoPlayCustomTargetPatch</c>,
    /// which fills a null target for any custom TargetType from every live
    /// creature its predicate accepts, and <see cref="KokomiTargets.PetOrEnemy"/>
    /// accepts the pet. <see cref="AutoPlayNeverAimsAtThePetPatch"/> takes the
    /// pet out of that roll; this line is the rule itself, so a pet aim that
    /// arrives by any other door still writes no Plan. The pet is a
    /// DELIBERATE target -- the mod draws it so a player has something to drag
    /// a card onto -- and an auto-play has nobody at the mouse. The sim's twin
    /// is `kokomi_plan.plan_aimed_at_pet`, which refuses on
    /// `force_random_targeting` and `kurage_autoplaying` for the same reason.
    /// </summary>
    /// <remarks>THE RE-FOUNDING (2026-10-12): Grand Design's free write is
    /// the one auto-play that writes, because the card it plays was CHOSEN
    /// to be written (<see cref="KokomiRefounding.WriteFree"/>).</remarks>
    public static bool PlayedOnPet(CardPlay cardPlay) =>
        (!cardPlay.IsAutoPlay || KokomiRefounding.IsFreeWrite(cardPlay.Card))
        && BakeKuragePet.Is(cardPlay.Target);

    /// <summary>
    /// Write one Plan down: rule 2's whole engine side.
    ///
    /// THE MOON OVERLOOKS THE WATERS IS RESOLVED HERE, and "also" is taken at
    /// its word: the Rare's face is "Plans also happen now", so the Plan
    /// happens NOW and is STILL queued for the start of her next turn. Reading
    /// it as "instead" would delete rule 2 rather than break it.
    /// </summary>
    /// <param name="writer">The card that was played to write this Plan where
    /// it is not <paramref name="source"/> (Moon's Reflection's found card).
    /// The write payoffs (<see cref="KokomiRefounding.OnWritten"/>) read the
    /// card that was written, which is this one where it is set.</param>
    public static async Task Schedule(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? source,
        IReadOnlyList<Planned> clauses, CardModel? writer = null)
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
        // `EB-580` AND `EB-599`. HER SIDE OF THE LINE, FOLDED INTO THE NUMBER
        // THAT IS WRITTEN DOWN -- see <see cref="Hers"/> for both findings and
        // the measured API. AT WRITING TIME, Crystal Collapse's and Flank's
        // rule below: her Strength and this card's enchantment are what the
        // player was looking at when they decided to write the Plan, and both
        // the buff and the card can be anywhere by the morning.
        //
        // THE PRINTED-DAMAGE CLAUSE ONLY, and that is exact rather than
        // partial. `DamageQuarterMaxHp` prints no flat number for a flat
        // rider to join -- it is read off Max HP -- so there is nothing on
        // that face the fold could be about. `PlanDamageVar` previews the same call, so the number
        // queued here is the number the face printed.
        for (var i = 0; i < body.Count; i++)
        {
            if (body[i].Kind == Kind.Damage)
            {
                body[i] = body[i] with
                {
                    Amount = Hers(kokomi, source, body[i].Amount,
                                  body[i].StrengthTimes),
                };
            }
        }
        string? label = null;
        CardModel? held = null;
        if (body.Any(c => c.Kind == Kind.PlayCopyOfCompanion))
        {
            held = KokomiOverhaulLedger.For(kokomi)
                                       .LastCompanionPlayed;
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
        // FLANK READS AT CARRY-OUT since the Kokomi level pass (2026-10-12):
        // "each enemy that intends to attack" is the board when the Plan is
        // carried out, as Tide Wall reads it (<see cref="Aimed"/>). Seats
        // misread the old "when you wrote this", so nothing is captured here.
        // KELP WALL COUNTS AT WRITING TIME (Kokomi round-1 fixes,
        // 2026-10-12): "plus 3 for each status or curse in your hand when
        // written" is the hand on screen NOW, the number the face's preview
        // (<see cref="PlanStatusBlockVar"/>) printed. Sim twin:
        // `kokomi_plan.schedule`, `written_count`.
        if (body.Any(c => c.Kind == Kind.BlockPerStatusInHand))
        {
            var heldNow = KokomiStatusBatch.StatusesInHand(player);
            for (var i = 0; i < body.Count; i++)
            {
                if (body[i].Kind == Kind.BlockPerStatusInHand)
                {
                    body[i] = body[i] with { WrittenCount = heldNow };
                }
            }
        }
        // THE CO-OP SET, JOINT ORDERS: "Plan: They draw 2 cards" remembers
        // the player it is for, and it is fixed HERE, when the Plan is
        // written -- Flank's discipline one clause over: an id and not a
        // creature, found again on the live board at carry-out. See
        // <see cref="CoopSet.PlanAlly"/> for which player that is when the
        // card was played on the Bake-Kurage.
        if (body.Any(c => c.Kind == Kind.AllyDraw))
        {
            var ally = CoopSet.PlanAlly(kokomi);
            var ids = ally == null
                ? new List<string>()
                : new List<string> { ally.CombatId.ToString() };
            for (var i = 0; i < body.Count; i++)
            {
                if (body[i].Kind == Kind.AllyDraw)
                {
                    body[i] = body[i] with { Targets = ids };
                }
            }
        }
        // THE EXPANSION, BATCH ONE. All Streams' pending gift is taken by the
        // first Plan written after it this turn (0 cancelled is still taken:
        // "once, plus once for each" with none is once).
        var ledger = KokomiOverhaulLedger.For(kokomi);
        var extra = ledger.NextPlanExtra ?? 0;
        ledger.NextPlanExtra = null;
        var entry = new Entry(source, body, label, Extra: extra,
                              Writer: writer,
                              // THE POOL OVERHAUL (2026-10-13): the Plan's
                              // own "since you planned this" opens now.
                              Window: ledger.OpenWindow(),
                              // KOKOMI REVIEW R5 (2026-10-14, A2): her
                              // Strength as the hit was written, which `Hers`
                              // folded in above; the page names it beside
                              // what the Plan will land. Null for a Plan
                              // with no flat hit.
                              WrittenStrength: body.Any(c => c.Kind == Kind.Damage)
                                  ? (int)(kokomi?.Powers.OfType<StrengthPower>()
                                              .FirstOrDefault()?.Amount ?? 0)
                                  : null);
        int before = queue.Count;
        queue.Add(entry);
        // The whole-run telemetry's count of Plans written (Moon's
        // Reflection's included). Sim twin: `kokomi_plan.schedule`.
        ledger.NotePlanWritten();
        // The jellyfish build (2026-10-12): a written Sting, for telemetry.
        if (source is global::KleeMod.Cards.Prototype.Generated.ProtoKkSting)
        {
            ledger.NoteStingWritten();
        }
        await Sync(choiceContext, kokomi,
            SparkPower.SourceOf(source), before);
        // THE RE-FOUNDING (2026-10-12): the write payoffs -- Watchful
        // Shoal's Block for an Ethereal card, Watatsumi Resistance's Sting
        // for a Companion. After the queue moved, so a payoff reads the Plan
        // as written. Sim twin: `kokomi_plan.note_written`.
        await KokomiRefounding.OnWritten(choiceContext, kokomi,
                                         entry.Returns);

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
        // THE WRITER IS MOON'S REFLECTION, so a cancel gives back the card
        // that was played and never the one it found in the exhaust pile.
        await Schedule(choiceContext, owner.Creature, pick, clauses,
                       writer: source);
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

    /// <summary>Keyed on the VERB, the way Rally's search screen was: one
    /// screen, one string, however many carriers eventually print it.</summary>
    public const string ReflectionPromptKey =
        "KLEEMOD-KOKOMI_EXHAUST_PLAN.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source.</summary>
    public const string ReflectionPromptText =
        "Choose a card. Next turn its Plan is carried out, or it's played if "
      + "it has none.";

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
    /// which is what "the jellyfish carries out your first Plan twice" says --
/// the first entry OF THE DRAIN being carried out, whichever card wrote it.
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
        // `EB-643`, R265. THE TWO-PLAN CAP, read here and nowhere else: at N
        // the front N entries are carried out and THE REST STAY QUEUED IN
        // ORDER for the next morning -- not discarded, not re-sorted, because
        // the whole trial is about whether queue order becomes a decision. At
        // 0, which is the default, this is the list it always was.
        var cap = PlanCap;
        var due = cap > 0 && queue.Count > cap
            ? new List<Entry>(queue.GetRange(0, cap))
            : new List<Entry>(queue);
        var held = cap > 0 && queue.Count > cap
            ? new List<Entry>(queue.GetRange(cap, queue.Count - cap))
            : null;
        // A PLAN STAYS OPEN (2026-10-01, pick 5a): each Plan is carried out
        // as the line it was flipped to while it waited.
        due = ChooseLines(due);
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
        // `EB-655`. ONE EXTRA CARRY-OUT AND NOT A DOUBLING: the Rare doubles
        // the FIRST entry alone, so a three-Plan morning under it is four
        // carry-outs and not six. `kokomi_plan.resolve_all` counts the same.
        KokomiOverhaulLedger.For(kokomi).NoteMorning(
            StratagemTimes(kokomi) > 1
                ? due.Count * StratagemTimes(kokomi)
                : due.Count + (CarryOutTimes(kokomi) > 1 ? 1 : 0));
        // The display list is handed over BEFORE the sync, because `Sync`
        // refreshes the strip and the strip reads `Showing`: the badge goes
        // away in the same beat the column stays up, which is the true
        // statement (nothing is pending; four things are happening).
        _showing[player] = new List<Entry>(due);
        await Sync(choiceContext, kokomi, "rule:morning_drain", due.Count);

        // THE MORNING WINDOW (co-op playtest 2026-09-30): a Plan hit inside it
        // spares its aura this turn start's tick (<see cref="Hit"/>). Per
        // player, opened and closed around the drain and on every path.
        // Kokomi follow-ups (2026-10-01): the window is also open for every
        // other door an aura is touched through, so a card Moon's Reflection
        // replays (<see cref="Replay"/>) keeps its Hydro whole too.
        _morning.Add(player);
        AuraPower.OpenMorning(kokomi);
        try
        {
            await Drain(choiceContext, kokomi, due);
        }
        finally
        {
            AuraPower.CloseMorning(kokomi);
            _morning.Remove(player);
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
            // `EB-643`. WHAT THE CAP HELD BACK GOES BACK ON THE FRONT OF THE
            // QUEUE, in order, AFTER the drain and not before it -- a Plan
            // carried out this morning can write another (Moon's Reflection
            // reaches a card that does), and that new Plan waits for the next
            // morning like every other. The held entries go in FRONT of it for
            // the reason they are kept in order at all: they were written
            // first. On the unwind path too, because a fight that ended
            // mid-drain does not un-cap the Plans it never reached.
            if (held is { Count: > 0 })
            {
                if (!_queues.TryGetValue(player, out var back))
                {
                    back = new List<Entry>();
                    _queues[player] = back;
                }
                back.InsertRange(0, held);
                // AND THE BADGE IS PUT BACK WITH THEM (round 23, beside
                // `EB-650`). The sync above ran at depth 0 and REMOVED the
                // badge; without this the morning ends with Plans written and
                // nothing on screen saying how many. `RefreshBadge` counts
                // `Pending` itself, so the number cannot disagree with the
                // queue -- and it deliberately does NOT note the meter, which
                // its own header explains (`R101b`: one row per drain).
                await RefreshBadge(choiceContext, kokomi,
                                   Pending(player).Count);
            }
            Vfx.KokomiPlanStrip.Refresh(kokomi);
        }
    }

    /// <summary>
    /// CARRY A LIST OF PLANS OUT, IN ORDER -- the one loop both drains share
    /// (the morning's, and `EB-643`'s dusk).
    ///
    /// THE RIDERS LIVE HERE AND NOWHERE ELSE, which is the whole reason this
    /// is a method rather than two loops. "The next Plan" means the entry
    /// carried out immediately after this one IN THIS DRAIN: a rider is
    /// written by the entry that prints it, applies to the entry that follows,
    /// and is gone when this list runs out. A rider written by the last Plan
    /// of a morning does not reach into the evening, and one written at dusk
    /// does not reach into the next morning -- both fall off the end of a
    /// LOCAL, which is the shape that cannot leak.
    ///
    /// <see cref="ResolveFront"/> (Change of Plans) DOES NOT COME THROUGH HERE
    /// and so neither sets nor consumes a rider: it carries ONE entry out, and
    /// there is no "next" for the word to name. `kokomi_plan._drain` is the
    /// twin, with the same two callers and the same non-caller.
    ///
    /// THE THUMBNAIL LEAVES AFTER ITS PLAN HAS HAPPENED, front first, so the
    /// column shortens from the top in the order the Plans were written --
    /// the order the page prints. That is the morning's behaviour unchanged;
    /// a dusk drain simply has no thumbnails of its own to remove, because
    /// <see cref="Showing"/> is only handed a list by <see cref="ResolveAll"/>.
    ///
    /// A RIDER THAT REACHED NOTHING SAYS SO (`EB-645`, round 23). The r23
    /// defence lane wrote Second Wave with no Plan behind it in the same
    /// morning; the rider fell off the end of this local exactly as designed,
    /// and the page carried nothing at all -- the seat read "no enemy lost HP"
    /// off a Plan that had done its whole job and found no follower. So the
    /// drain files one more row on the carry-out log the seats read,
    /// `"&lt;card&gt;: no Plan followed"`, and the three rider faces now print
    /// the window the rider lives in. `kokomi_plan._drain` emits the same
    /// sentence as `plan_no_follower`.
    ///
    /// ONLY ON A DRAIN THAT RAN OUT. A fight that ends inside a carry-out
    /// unwinds this loop and files nothing, which is <see cref="NoteUnfinished"/>'s
    /// own reading: "no Plan followed" would be a receipt about a morning
    /// nobody is playing any more.
    /// </summary>
    private static async Task Drain(
        PlayerChoiceContext choiceContext, Creature kokomi, List<Entry> due)
    {
        var player = kokomi.Player;
        var doubleNext = false;
        var extraNext = false;
        // `EB-645`. WHO WROTE THE PENDING RIDER, so the line can name the
        // card. ONE SLOT for both riders, and that is exact rather than
        // approximate: both flags are cleared at the top of every entry, so
        // whatever is pending was written by the entry immediately before.
        string? riderSource = null;
        // (Spring Tide's mid-turn drain left with the card, the jellyfish
        // build, 2026-10-12.)
        var firstTimes = CarryOutTimes(kokomi);
        for (var index = 0; index < due.Count; index++)
        {
            var entry = due[index];
            // THE RIDERS THE ENTRY BEFORE THIS ONE WROTE, taken and cleared in
            // the same breath: a rider is spent by the entry it reaches, so
            // two Plans in a row that each double cannot both land on a third.
            var doubleThis = doubleNext;
            var extraThis = extraNext;
            doubleNext = extraNext = false;
            // `CarryOutTimes + 1` UNDER SECOND WAVE, and the rider is a FLAG:
            // under Nereid's Ascension the entry it reaches is carried out
            // three times, not four.
            // `EB-655`. THE FIRST ENTRY OF THIS DRAIN IS THE ONE NEREID'S
            // DOUBLES, and "each turn" is read as "each DRAIN": a morning and
            // a dusk are two drains on one turn and each pays its own first
            // entry. That is the drain-local reading every other positional
            // rule in this arm already takes -- "the next Plan" means "in this
            // drain" -- and it is what lets the Rare pay a one-Plan morning.
            // A STUNNING STRATAGEM (Kokomi's own potions, 2026-10-15): "Next
            // turn, every Plan is carried out twice." Read per entry like
            // Nereid's, and twice said twice is still twice.
            var times = System.Math.Max(index == 0 ? firstTimes : 1,
                                        StratagemTimes(kokomi))
                      + (extraThis ? 1 : 0)
                      + System.Math.Max(0, entry.Extra);
            // Kokomi v2 seats (2026-10-18): a lane read "War Council" twice
            // on the morning's list and could not tell a second carry-out
            // from a repeated line. Each carry-out past the first names the
            // card that bought it (`AgainSources`), and the page prints it.
            var again = AgainFor(
                kokomi, index == 0 ? firstTimes : 1, extraThis,
                extraThis ? riderSource : null, entry.Extra);
            for (var i = 0; i < times; i++)
            {
                var (wroteDouble, wroteExtra) = await ResolveEntry(
                    choiceContext, kokomi, entry, onPlay: false,
                    doubleDamage: doubleThis,
                    drainEntries: due.Count,
                    again: i == 0 ? null
                        : again[System.Math.Min(i, again.Count) - 1]);
                // OR'd ACROSS THIS ENTRY'S OWN CARRY-OUTS, for the reason
                // above: an entry doubled by Nereid's prints its rider twice
                // and twice said twice is still twice.
                doubleNext = doubleNext || wroteDouble;
                extraNext = extraNext || wroteExtra;
            }
            if (doubleNext || extraNext) riderSource = entry.Title;
            if (player != null
                && _showing.TryGetValue(player, out var shown)
                && shown.Count > 0)
            {
                shown.RemoveAt(0);
            }
            Vfx.KokomiPlanStrip.Refresh(kokomi);
        }
        // `EB-645`. THE DRAIN RAN OUT WITH A RIDER STILL IN HAND.
        if ((doubleNext || extraNext) && riderSource != null)
        {
            NoteNoFollower(kokomi, riderSource);
        }
    }

    /// <summary>
    /// `EB-645`. A RIDER THAT REACHED NO FOLLOWER, on the carry-out log the
    /// seats read. NO BUBBLE, for <see cref="NoteUnfinished"/>'s reason:
    /// nothing was said over the pet, this is a page row about the shape of
    /// the morning. `Number` and `Moved` are null because no board was
    /// measured across a Plan that never ran.
    /// </summary>
    private static void NoteNoFollower(Creature kokomi, string card) =>
        Record(kokomi, new CarriedOutPlan(
            card, null, NoFollowerLine(card), null, false));

    /// <summary>The sentence, in ONE place so a pin can read it back without a
    /// game. `kokomi_plan._drain` emits the same string.</summary>
    internal static string NoFollowerLine(string card) =>
        card + ": no Plan followed";

    /// <summary>
    /// EBB TIDE (`EB-643`): "cancel every Plan you have queued; gain 1 Energy
    /// and draw 1 card for each."
    ///
    /// NO CARD SPELLS IT SINCE `EB-649` (round 23), AND THE OP STAYS. Ebb Tide
    /// drew three times on the r23 cap lane and was played none of them -- it
    /// is "only live in the situation you spent the previous turn trying to
    /// create" -- so <c>ProtoKkEbbTide</c> left the sheet and the generated
    /// roster with it. This method is kept because the RULE is the one a
    /// re-issue would want and deleting a resolver to re-derive it later is
    /// how a reading is lost; its pins drive it by reflection, with no card in
    /// the path. `kokomi_plan.cancel_all_plans_cash` carries the same note.
    ///
    /// PER ENTRY AND NOT PER CARRY-OUT, which is the one reading here and it
    /// is the face's own word: "for each" counts the Plans she is HOLDING, and
    /// what she is holding is entries -- the same quantity the pending badge
    /// shows and <see cref="PlansHeld"/> answers. Nereid's Ascension would
    /// have doubled them at the morning and did not, which is exactly the
    /// thing this card gives up.
    ///
    /// THE ENERGY IS PAID BEFORE THE DRAW, in that order, so a drawn card
    /// meets a hand that can already afford it. Sim twin:
    /// `kokomi_plan.cancel_all_plans_cash`.
    /// </summary>
    public static async Task CancelAllForCash(
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
        int cancelled = queue.Count;
        queue.Clear();
        await Sync(choiceContext, kokomi, "rule:plans_cashed", cancelled);
        await PlayerCmd.GainEnergy(cancelled, player);
        await CardPileCmd.Draw(choiceContext, cancelled, player);
    }

    /// <summary>
    /// CONVERGING TIDE (`EB-643`): "every queued Plan aims at this enemy
    /// instead of the front."
    ///
    /// IT STAMPS THE ENTRIES THAT ARE ALREADY WRITTEN AND NOTHING ELSE. A Plan
    /// written after the redirect aims at the front as usual, because the card
    /// names the queue as it stands -- "every queued Plan" -- and a rule that
    /// kept re-aiming later writes would be a Power the row does not print.
    ///
    /// ONLY THE FRONT AIM MOVES, which is <see cref="Aimed"/>'s half of the
    /// same rule: <see cref="Aim.AllEnemies"/> does not aim at the front, so
    /// there is nothing on it for "instead of the front" to be about, and
    /// Flank's captured set was fixed when its Plan was written for reasons of
    /// its own (`EB-492`).
    ///
    /// THE ID AND NOT THE CREATURE, <see cref="Planned.Targets"/>' discipline
    /// verbatim: nothing on the queue may hold a body the game can tear down.
    /// A dead target falls back to the front at carry-out.
    ///
    /// IT STAMPS DUSK ENTRIES TOO -- they are in the queue, the face says
    /// every queued Plan, and the redirect happens on the turn they will land
    /// on. NOT ASYNC and no <see cref="Sync"/>: the queue's DEPTH does not
    /// move, so the badge has nothing to say; the strip is refreshed because
    /// its aim line does. Sim twin: `kokomi_plan.redirect_queued_plans`.
    /// </summary>
    public static void Redirect(Creature? kokomi, Creature? target)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null || target == null || target.IsDead) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue) || queue.Count == 0)
        {
            return;
        }
        var id = target.CombatId.ToString();
        for (var i = 0; i < queue.Count; i++)
        {
            queue[i] = queue[i] with { AimOverride = id };
        }
        Vfx.KokomiPlanStrip.Refresh(kokomi);
    }

    /// <summary>
    /// How many times THE FIRST Plan of a drain is carried out right now: two
    /// while Nereid's Ascension is on her, one otherwise.
    ///
    /// `EB-655` (pool pass three) NARROWED THE CALLER AND NOT THIS FUNCTION.
    /// The Rare used to double every Plan, which paid for writing MORE and
    /// made a deep morning its only line; keyed to the first entry of each
    /// drain it pays a one-Plan morning too, and makes queue ORDER the
    /// decision the card is about. <see cref="Drain"/> is where that is read.
    ///
    /// A NAMED READ rather than an inline predicate, because WHERE it is asked
    /// is the rule: <see cref="Drain"/> calls it inside the loop, so a Rare
    /// played in the same morning is on her by the time the question is
    /// asked.
    ///
    /// A POWER AND NO LONGER A WINDOW (`EB-492`). The Rare is a Power costing
    /// 2 and lasting the fight; there is nothing to tick down, and "every Plan
    /// twice" is read here at the one place the number of carry-outs is
    /// decided.
    /// </summary>
    private static int CarryOutTimes(Creature kokomi) =>
        kokomi.Powers.OfType<NereidsAscensionPower>().Any() ? 2 : 1;

    // ---- A PLAN STAYS OPEN (2026-10-01, ruled) ---------------------------
    //
    // review/active/kokomi-delay-pays-2026-10-01.md sec.2: "When the
    // Bake-Kurage carries out a Plan, you choose which line it is: its Plan
    // line, or its now line." Two-line cards only (<see cref="INowLineCard"/>);
    // Plan-only cards and Dusk Plans are unchanged; the now-line is printed
    // size. Every carry-out of an entry (Nereid's Ascension, Second Wave, All
    // Streams) takes the line chosen for it. Plan payoffs count either line,
    // because <see cref="ResolveEntry"/> rings them after either.
    //
    // SEC.3, PICK 5 (a) (2026-10-01, ruled): "Plans carry out on their Plan
    // line; click a waiting Plan to flip it." NO SCREEN. A waiting two-line
    // Plan carries <see cref="Entry.Now"/>; during her own turn the player
    // flips it by clicking its picture in the Plan strip
    // (<c>Vfx.KokomiPlanStrip</c>), and a second click flips it back. The
    // click is a synced game action (<see cref="FlipPlanGameAction"/>), so a
    // co-op peer carries out the same line. At carry-out each Plan uses the
    // line it holds. Sim twin: `kokomi_plan.flip` / `kokomi_plan.choose_lines`.

    /// <summary>The beat's name for a Plan carried out as its now-line.</summary>
    public static string NowLineTitle(string title) =>
        title + " (now-line)";

    /// <summary>
    /// The lines the due entries are carried out as: each keeps the line it
    /// was flipped to while it waited, and an entry that cannot offer the
    /// choice (Plan-only) is always its Plan line. No
    /// screen (pick 5a).
    /// Returns the entries in the same order.
    /// </summary>
    public static List<Entry> ChooseLines(List<Entry> due) =>
        due.Select(e => e.Now && !e.TwoLine ? e with { Now = false } : e)
           .ToList();

    /// <summary>
    /// Flip the waiting Plan at <paramref name="index"/> between its Plan line
    /// and its now-line. False, and nothing moves, where there is no entry
    /// there or it offers no choice. The list is the queue itself.
    /// </summary>
    public static bool FlipAt(List<Entry> queue, int index)
    {
        if (index < 0 || index >= queue.Count || !queue[index].TwoLine)
        {
            return false;
        }
        queue[index] = queue[index] with { Now = !queue[index].Now };
        return true;
    }

    /// <summary>
    /// THE FLIP ITSELF, run by <see cref="FlipPlanGameAction"/> on every peer.
    /// Only during the player's own play phase and never mid-drain: a flip
    /// that arrived late must not land on whatever entry now holds its index.
    /// Redraws the strip, whose labels and forecast read the flip.
    /// </summary>
    public static bool Flip(Player? player, int index)
    {
        var kokomi = player?.Creature;
        if (player == null || !KokomiOverhaul.LiveFor(kokomi)) return false;
        Rebase(kokomi!);
        if (_showing.ContainsKey(player)) return false;
        if (player.PlayerCombatState?.Phase != PlayerTurnPhase.Play)
        {
            return false;
        }
        if (!_queues.TryGetValue(player, out var queue)) return false;
        if (!FlipAt(queue, index)) return false;
        Vfx.KokomiPlanStrip.Refresh(kokomi);
        return true;
    }

    /// <summary>
    /// Ask for a flip: the strip's click and the bridge's `flip` verb both
    /// come here. Null when the request was sent; otherwise the reason it was
    /// not, in plain words. It goes through the game's action queue, as a card
    /// play does, so every co-op peer flips the same Plan.
    /// </summary>
    public static string? RequestFlip(Player? player, int index)
    {
        var kokomi = player?.Creature;
        if (player == null || !KokomiOverhaul.LiveFor(kokomi))
        {
            return "there is no Bake-Kurage here";
        }
        if (player.PlayerCombatState?.Phase != PlayerTurnPhase.Play)
        {
            return "a Plan can be flipped only during your turn";
        }
        var queue = Pending(player);
        if (index < 0 || index >= queue.Count)
        {
            return "there is no waiting Plan " + (index + 1);
        }
        if (!queue[index].TwoLine)
        {
            return queue[index].Title + " has only one line";
        }
        MegaCrit.Sts2.Core.Runs.RunManager.Instance.ActionQueueSynchronizer
            .RequestEnqueue(new FlipPlanGameAction(player, (uint)index));
        return null;
    }

    /// <summary>
    /// THE NOW-LINE, CARRIED OUT BY THE BAKE-KURAGE: the card's own
    /// <see cref="INowLineCard.PlayNowLine"/>, at printed size, on a play the
    /// game never sees (no cost, no card moved, not a card played). Aimed by
    /// the Plan's retargeting rule: the front enemy, or Converging Tide's
    /// override while that body stands (<see cref="Aimed"/>); Joint Orders'
    /// captured ally, and nothing if that player is gone. No target where one
    /// is needed and the line does nothing. Sim twin:
    /// `kokomi_plan.carry_out_now_line`.
    /// </summary>
    public static async Task CarryOutNowLine(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry)
    {
        if (entry.Source is not INowLineCard card) return;
        if (kokomi.Player is not { } player) return;
        Creature? target = card.NowLineAim switch
        {
            DivineStrategyPower.Aim.FrontEnemy => Aimed(
                kokomi, new Planned(Kind.Damage, 0, Aim.FrontEnemy), entry)
                .FirstOrDefault(),
            DivineStrategyPower.Aim.Ally => entry.Clauses
                .Where(c => c.Targets is { Count: > 0 })
                .Select(c => CoopSet.PlanAllyFor(kokomi, c))
                .FirstOrDefault(c => c != null),
            _ => null,
        };
        if (card.NowLineAim != DivineStrategyPower.Aim.None && target == null)
        {
            return;
        }
        var play = new CardPlay
        {
            Card = entry.Source!,
            Player = player,
            Target = target,
            ResultPile = PileType.None,
            Resources = new ResourceInfo
            {
                EnergySpent = 0, EnergyValue = 0, StarsSpent = 0,
                StarValue = 0,
            },
            IsAutoPlay = true,
            PlayIndex = 0,
            PlayCount = 1,
        };
        await card.PlayNowLine(choiceContext, play);
    }

    /// <summary>
    /// A two-line card's two lines as text, for the blind page's waiting list:
    /// the now-line, and the Plan line without its "Or plan:" head. Read off
    /// the card's own rendered face, split where the face prints "Or plan:".
    /// Empty strings where the face could not be read.
    /// </summary>
    internal static (string Now, string Plan) LineTexts(CardModel? card)
    {
        if (card == null) return ("", "");
        string text;
        try
        {
            text = card.GetDescriptionForPile(PileType.Hand);
        }
        catch (System.Exception)
        {
            return ("", "");
        }
        return SplitFace(text);
    }

    /// <summary><see cref="LineTexts"/>'s split of a rendered face, its tags
    /// stripped. Pure, so a headless test can read it.</summary>
    internal static (string Now, string Plan) SplitFace(string? text)
    {
        text = System.Text.RegularExpressions.Regex.Replace(
            text ?? "", @"\[[^\]]*\]", "");
        var at = text.IndexOf("Or plan:", System.StringComparison.Ordinal);
        var head = "Or plan:".Length;
        if (at < 0) return (text.Trim(), "");
        return (text.Substring(0, at).Trim(),
                text.Substring(at + head).Trim());
    }

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
        // A PLAN STAYS OPEN (pick 5a): the line it was flipped to.
        front = ChooseLines(new List<Entry> { front })[0];
        // `EB-329`: Change of Plans is one of the two mid-turn doors, and its
        // card says so in as many words -- "carries out your front Plan NOW".
        // THE EXPANSION: an All Streams gift rides the entry, so a hurried
        // Plan is carried out its full number of times too.
        // A Stunning Stratagem's turn carries it out twice here too.
        var times = StratagemTimes(kokomi) + System.Math.Max(0, front.Extra);
        for (var i = 0; i < times; i++)
        {
            if (kokomi.IsDead) return;
            await ResolveNow(choiceContext, kokomi, front);
        }
    }

    /// <summary>
    /// Bottled Tide (Kokomi's own potions, 2026-10-15): "The Bake-Kurage
    /// carries out every waiting Plan now." Change of Plans' door
    /// (<see cref="ResolveFront"/>) once for each Plan waiting when it is
    /// drunk, front first. A Plan written by one of those carry-outs waits
    /// for the next morning like every other; the cap does not apply, since
    /// the face says every Plan.
    /// </summary>
    public static async Task ResolveEveryNow(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var waiting = Pending(kokomi!.Player).Count;
        for (var i = 0; i < waiting; i++)
        {
            if (kokomi.IsDead || kokomi.CombatState == null) return;
            await ResolveFront(choiceContext, kokomi);
        }
    }

    /// <summary>How many times every Plan is carried out right now: two on
    /// the turn A Stunning Stratagem armed, one otherwise
    /// (<see cref="StunningStratagemPower.LiveNow"/>).</summary>
    public static int StratagemTimes(Creature kokomi) =>
        kokomi.Powers.OfType<StunningStratagemPower>().Any(p => p.LiveNow)
            ? 2 : 1;

    /// <summary>"Each player" (pool completion, Tactical Relay): every living
    /// player creature on her side, herself included -- the base game's
    /// teammates walk (<c>Rally</c>, <c>HuddleUp</c>), with no "other"
    /// clause. Just her in a one-seat fight.</summary>
    internal static IReadOnlyList<Creature> EachPlayer(Creature kokomi)
    {
        if (kokomi.CombatState is not { } combat) return new[] { kokomi };
        var all = combat.GetTeammatesOf(kokomi)
            .Where(c => c != null && c.IsAlive && c.IsPlayer)
            .ToList();
        if (!all.Contains(kokomi) && kokomi.IsAlive) all.Insert(0, kokomi);
        return all;
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
    private static Task<(bool Double, bool Extra)> ResolveNow(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry) =>
        ResolveEntry(choiceContext, kokomi, entry, onPlay: true);

    /// <summary>
    /// ONE PLAN CARRIED OUT, which is the unit the plan-bus payoffs are
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
    /// <param name="doubleDamage">`EB-643`. Opening Gambit's rider, spent on
    /// THIS entry by the drain that carried the entry before it out.</param>
    /// <returns>`EB-643`. The riders THIS entry wrote, which the drain spends
    /// on the carry-out that follows it. They are handed back rather than stored because the clause
    /// that writes one is inside the loop below and the drain that spends it is
    /// outside -- returning them is what keeps "the next Plan" a fact about a
    /// DRAIN rather than a flag on this class that could outlive one.</returns>
    private static async Task<(bool Double, bool Extra)> ResolveEntry(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry,
        bool onPlay = false, bool doubleDamage = false,
        int drainEntries = 1, string? again = null)
    {
        var wroteDouble = false;
        var wroteExtra = false;
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
        // THE RE-FOUNDING (2026-10-12): Grand Strategist's "Whenever a Plan
        // causes an Elemental Reaction" reads this window, open for exactly
        // the clauses of one carry-out (<see cref="IsCarryingOut"/>).
        var seat = kokomi.Player;
        // THE POOL OVERHAUL (2026-10-13), CHAIN: this carry-out counts
        // itself, so the per-turn count rises before its clauses run (and
        // before `AskedFor` reads it). Sim twin: `kokomi_plan._resolve_entry`.
        KokomiOverhaulLedger.For(kokomi).NotePlanCarryingOut();
        // Kokomi round-3 changes (2026-10-12): what else landed in this
        // carry-out's window, named on the results line. (Coordinated Tide's
        // hit, its one rider, left with the pool overhaul, 2026-10-13.)
        var riders = new List<Rider>();
        if (seat != null) _aimedAtNoOne.Remove(seat);
        if (seat != null) _reactions.Remove(seat);
        if (seat != null) _carrying.Add(seat);
        try
        {
            // A PLAN STAYS OPEN (2026-10-01): the player chose the now-line.
            // It replaces the Plan line whole, so it writes no rider and
            // Opening Gambit's double does not reach it (printed size). It is
            // still a carry-out: everything after this block pays either line.
            if (entry.Now && entry.TwoLine)
            {
                await CarryOutNowLine(choiceContext, kokomi, entry);
            }
            foreach (var clause in entry.Now && entry.TwoLine
                         ? (IReadOnlyList<Planned>)System.Array.Empty<Planned>()
                         : entry.Clauses)
            {
                // `EB-643`. THE RIDERS ARE NOTED HERE AND NOWHERE ELSE, before
                // the switch, because they do nothing when they resolve: what
                // they do is tell the drain about the entry that follows.
                if (clause.Kind == Kind.NextPlanDoubleDamage) wroteDouble = true;
                if (clause.Kind == Kind.NextPlanExtraCarryOut) wroteExtra = true;
                var wanted = AskedFor(kokomi, clause, entry);
                var produced = await ResolveOne(choiceContext, kokomi, clause,
                                                entry, doubleDamage,
                                                drainEntries);
                if (number == null && produced != null)
                {
                    number = produced;
                    kind = NumberKind(clause.Kind);
                    asked = wanted;
                }
            }
            // (Coordinated Tide's carry-out hit left with the pool overhaul,
            // 2026-10-13: it reads a Companion's reaction now,
            // `KokomiRefounding.OnReaction`.)
            if (seat != null) _carrying.Remove(seat);
        }
        finally
        {
            if (seat != null) _carrying.Remove(seat);
            // `EB-329`, THE OTHER HALF OF THE ROW: A LINE EVEN WHEN THE PLAN'S
            // KILL ENDS THE FIGHT. The round-5 act-1 seat banked two Plans for
            // an exactly-lethal morning, and "the next screen was the reward
            // screen" -- the beat it had spent a turn setting up was the one
            // beat of the run it never got a receipt for. A combat that ends
            // inside a clause unwinds this method, so the announcement is on
            // the unwind path and not after it. Every number the board already
            // moved is still measured; the clauses that never ran moved
            // nothing, which is the honest reading.
            var noTarget = seat != null && _aimedAtNoOne.Remove(seat)
                           && number == null;
            // Item 9 (Kokomi review r8): the reactions its hits set off.
            List<string>? reactions = null;
            if (seat != null && _reactions.Remove(seat, out var noted))
            {
                reactions = noted;
            }
            Announce(kokomi,
                     entry.Now && entry.TwoLine
                         ? NowLineTitle(entry.Title) : entry.Title,
                     number, Moved(before, kokomi),
                     onPlay, kind, asked, riders, noTarget, reactions,
                     again);
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
                await listener.OnPlanResolved(choiceContext, kokomi,
                                              entry.Source);
            }
        }
        // THE RE-FOUNDING (2026-10-12): Endless Shoal (Coordinated Tide moved
        // inside the window above). Once per carry-out, either line, like the
        // bus above; since the Kokomi card paper v2 (2026-10-18) not for a
        // Sting's or Ward's line (`entry.Source`, the card whose line it is).
        // Sim twin: `kokomi_plan.note_carried_out`.
        await KokomiRefounding.OnCarriedOut(choiceContext, kokomi,
                                            entry.Returns, entry.Source);
        // KOKOMI'S OWN RELICS (2026-10-15): Everlasting Moonglow, after the
        // turn's first carry-out, through either door.
        await Relics.KokomiArmRelics.AfterPlanCarriedOut(kokomi,
                                                        entry.Returns);
        return (wroteDouble, wroteExtra);
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
                                 IReadOnlyList<Rider>? riders = null,
                                 bool noTarget = false,
                                 IReadOnlyList<string>? reactions = null,
                                 string? again = null)
    {
        var line = Vfx.KurageBeat.Line(card, number);
        Vfx.KurageBeat.Say(BakeKuragePet.Of(kokomi) ?? kokomi, line);
        Record(kokomi, new CarriedOutPlan(card, number, line, moved, onPlay,
                                          kind, asked, riders,
                                          NoTarget: noTarget,
                                          Reactions: reactions,
                                          Again: again));
    }

    /// <summary>
    /// Kokomi v2 seats (2026-10-18): WHY a morning entry is carried out more
    /// than once, one name per extra carry-out, in the order
    /// <see cref="Drain"/> adds them: Nereid's Ascension or A Stunning
    /// Stratagem (whichever sets the base count), then the rider the entry
    /// before wrote (Second Wave), then All Streams' gift on the entry
    /// itself. PURE; the page prints "(again: Nereid's Ascension)" on the
    /// second row.
    /// </summary>
    public static IReadOnlyList<string> AgainSources(
        int baseTimes, int stratagemTimes, bool extraRider,
        string? riderSource, int entryExtra)
    {
        var names = new List<string>();
        var times = System.Math.Max(baseTimes, stratagemTimes);
        var by = stratagemTimes >= times && stratagemTimes > 1
            ? "A Stunning Stratagem" : "Nereid's Ascension";
        for (var i = 1; i < times; i++) names.Add(by);
        if (extraRider) names.Add(riderSource ?? "Second Wave");
        for (var i = 0; i < entryExtra; i++) names.Add("All Streams");
        return names;
    }

    private static IReadOnlyList<string> AgainFor(
        Creature kokomi, int baseTimes, bool extraRider, string? riderSource,
        int entryExtra) =>
        AgainSources(baseTimes, StratagemTimes(kokomi), extraRider,
                     riderSource, System.Math.Max(0, entryExtra));

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
    /// from its own fight memory (`MovedOn`, `Rider`). Flank's old strip
    /// label baked its names into a string with no id on it (retired by the
    /// Kokomi level pass, 2026-10-12, when Flank moved to a carry-out read).
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
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan,
        Entry? entry = null, bool doubleDamage = false,
        int drainEntries = 1)
    {
        var player = kokomi.Player;
        if (player == null) return null;

        switch (plan.Kind)
        {
            case Kind.NextPlanDoubleDamage:
            case Kind.NextPlanExtraCarryOut:
                // THE RIDERS DO NOTHING HERE, and that is the whole of them:
                // <see cref="ResolveEntry"/> noted the clause before the switch
                // and <see cref="Drain"/> spends it on the entry that follows.
                // No number, so the beat says the card's name alone -- which is
                // the honest line for a Plan whose effect is on the NEXT one.
                return null;

            case Kind.FirstAttackTwice:
                // R276, PINCER. A switch; no number on the beat.
                await KokomiOverhaulKit.FirstAttackTwice(choiceContext, kokomi);
                return null;

            // THE RE-FOUNDING (2026-10-12).
            case Kind.AddStings:
                return await KokomiCards.AddJellyfish(
                    player, KokomiCards.Jellyfish.Sting, plan.Amount,
                    upgraded: false);

            case Kind.GainStrength:
                await KokomiRefounding.GainStrength(
                    choiceContext, kokomi, plan.Amount);
                return plan.Amount;

            case Kind.JuugaGuard:
                await PowerCmd.Apply<JuugaGuardPower>(
                    choiceContext, kokomi, plan.Amount, applier: kokomi,
                    cardSource: null);
                return null;

            case Kind.AllyDraw:
            {
                // THE CO-OP SET, JOINT ORDERS: the player captured when the
                // Plan was written, if they are still alive; otherwise
                // nothing. The base game's own door for a draw on ANOTHER
                // seat (Huddle Up), so the other player's draw cannot block
                // this one's turn.
                if (CoopSet.PlanAllyFor(kokomi, plan) is not { Player: { } them })
                {
                    return null;
                }
                if (entry?.Source is { } writer)
                {
                    await CardPileCmd.DrawWithoutBlockingOnOtherPlayers(
                        choiceContext, plan.Amount, them, writer);
                }
                else
                {
                    await CardPileCmd.Draw(choiceContext, plan.Amount, them);
                }
                return plan.Amount;
            }

            case Kind.OthersAttackDamageThisTurn:
                // THE CO-OP SET, COORDINATED STRIKE: Battle Plan's power on
                // every OTHER living player, applied by her. No number on the
                // beat, Battle Plan's own shape.
                foreach (var other in CoopSet.OtherPlayers(kokomi))
                {
                    await PowerCmd.Apply<AttackUpThisTurnPower>(
                        choiceContext, other, plan.Amount, applier: kokomi,
                        cardSource: null);
                }
                return null;

            case Kind.BlockMaxIntent:
                // R276, TIDE WALL. POWERED, the flat planned Block's funnel.
                // The intents are read NOW, at carry-out, after the coming
                // enemy turn's intents are up. Kokomi round-3 changes
                // (2026-10-12): the LARGEST intent on the board, not the
                // front body's, which read 0 against the Queen.
                return (int)await CreatureCmd.GainBlock(
                    kokomi,
                    KokomiOverhaulKit.MostIntendedDamage(kokomi)
                        + plan.Amount,
                    ValueProp.Move, null);

            case Kind.Draw:
                await CardPileCmd.Draw(choiceContext, plan.Amount, player);
                return plan.Amount;

            case Kind.Energy:
                await PlayerCmd.GainEnergy(plan.Amount, player);
                return plan.Amount;

            case Kind.EachPlayerEnergy:
                // POOL COMPLETION, TACTICAL RELAY: every living player.
                foreach (var each in EachPlayer(kokomi))
                {
                    if (each.Player is { } them)
                    {
                        await PlayerCmd.GainEnergy(plan.Amount, them);
                    }
                }
                return plan.Amount;

            case Kind.EachPlayerDraw:
            {
                // Written at 0 on the base card: a 0 draws nothing. Another
                // seat draws through the base game's door for a draw on a
                // player who is not acting (Joint Orders' shape).
                if (plan.Amount <= 0) return null;
                foreach (var each in EachPlayer(kokomi))
                {
                    if (each.Player is not { } them) continue;
                    if (them == player || entry?.Source is not { } writer)
                    {
                        await CardPileCmd.Draw(choiceContext, plan.Amount, them);
                    }
                    else
                    {
                        await CardPileCmd.DrawWithoutBlockingOnOtherPlayers(
                            choiceContext, plan.Amount, them, writer);
                    }
                }
                return plan.Amount;
            }

            case Kind.Block:
                // POWERED, and rule 3 is why: "your Strength and Dexterity
                // count, since the plans are hers". Draft 2's Plan Block was
                // `Unpowered` on the NC-11 power-sourced-Block line; draft 6
                // states the opposite rule in the brief itself, so a planned
                // Block is `ValueProp.Move` -- the same prop a card's own Block
                // carries, and the same one Dexterity reads.
                // THE FEED PASS (2026-09-29): a 0 flat Block is the clause
                // Current Read's upgrade adds, unprinted on the base face, so
                // it is nothing -- never a Dexterity-sized Block. The sim's
                // twin is `kokomi_plan._carry_out`'s `block` branch.
                if (plan.Amount <= 0)
                {
                    return 0;
                }
                return (int)await CreatureCmd.GainBlock(
                    kokomi, plan.Amount, ValueProp.Move, null);

            case Kind.Mend:
                // Mend returns the HP that actually landed, which is the
                // honest number: "Mend 10" into 4 points of room says 4.
                return await KokomiRules.Mend(
                    choiceContext, kokomi, plan.Amount);

            case Kind.Damage:
                return await Hit(choiceContext, kokomi, plan, plan.Amount,
                                 entry, doubleDamage);

            case Kind.DamageQuarterMaxHp:
                return await Hit(choiceContext, kokomi, plan,
                                 KokomiRules.QuarterOfMaxHp(kokomi),
                                 entry, doubleDamage);

            case Kind.ApplyWeak:
                await Debuff<WeakPower>(choiceContext, kokomi, plan, entry);
                return plan.Amount;

            case Kind.ApplyVulnerable:
                await Debuff<VulnerablePower>(choiceContext, kokomi, plan,
                                              entry);
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

            // THE STATUS BATCH (2026-10-01). Kelp Wall pays the count it was
            // written with; Sea Glass Harvest reads the draw pile now
            // (Kokomi round-1 fixes, 2026-10-12).
            case Kind.BlockPerStatusInHand:
                return await KokomiStatusBatch.BlockPerStatus(
                    kokomi, plan.Amount, plan.WrittenCount);
            case Kind.TransformStatusesYouHave:
                return await KokomiStatusBatch.TransformStatuses(
                    player, entry?.Source?.IsUpgraded ?? false);

            // THE POOL OVERHAUL (2026-10-13): the Chain, Counter and Intent
            // lines, and Read the Field's fetch.
            case Kind.DamagePerPlanThisTurn:
            case Kind.DamageBlockedSince:
            case Kind.DamageTakenSince:
                return await Hit(choiceContext, kokomi, plan,
                                 AskedFor(kokomi, plan, entry) ?? 0,
                                 entry, doubleDamage);

            case Kind.EnergyIfAttackedSince:
                if (!KokomiOverhaulLedger.For(kokomi)
                        .AttackedSince(entry?.Window))
                {
                    return 0;
                }
                await PlayerCmd.GainEnergy(plan.Amount, player);
                return plan.Amount;

            case Kind.LoseStrengthThisTurn:
                foreach (var target in Aimed(kokomi, plan, entry).ToList())
                {
                    if (target.IsDead) continue;
                    await PowerCmd.Apply<UndercurrentSnarePower>(
                        choiceContext, target, plan.Amount, applier: kokomi,
                        cardSource: null);
                }
                return plan.Amount;

            case Kind.DrawPileToHand:
                return await DrawPileToHand(choiceContext, player);
        }
        return null;
    }

    /// <summary>Read the Field's Plan line (the pool overhaul, 2026-10-13):
    /// "Put a card from your Draw Pile into your Hand." The base game's
    /// Secret Technique screen over the whole Draw Pile, her choice; an empty
    /// pile is a no-op. Returns 1 when a card moved. Sim twin:
    /// `kokomi_plan.draw_pile_to_hand`.</summary>
    public const string DrawPilePromptKey =
        "KLEEMOD-KOKOMI_DRAW_PILE_TO_HAND.selectionScreenPrompt";

    public const string DrawPilePromptText =
        "Choose a card to put into your [gold]Hand[/gold].";

    private static async Task<int?> DrawPileToHand(
        PlayerChoiceContext choiceContext, Player player)
    {
        var pile = CardPile.Get(PileType.Draw, player);
        if (pile == null || pile.Cards.Count == 0) return 0;
        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, player,
            new CardSelectorPrefs(new LocString("cards", DrawPilePromptKey),
                                  1))).FirstOrDefault();
        if (pick == null) return 0;
        await CardPileCmd.Add(pick, PileType.Hand, CardPilePosition.Top);
        // Kokomi review r6 pick 3 (a) (2026-10-14): "It costs 0 this turn."
        pick.EnergyCost.SetThisTurn(0);
        return 1;
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
        // THE CO-OP SET: the cards the OTHER player drew.
        Kind.AllyDraw => "cards drawn",
        Kind.Energy => "Energy",
        // POOL COMPLETION: Tactical Relay's figure is HER share of it.
        Kind.EachPlayerEnergy => "Energy",
        Kind.EachPlayerDraw => "cards drawn",
        Kind.Block => "Block",
        Kind.Mend => "HP healed",
        Kind.Damage or Kind.DamageQuarterMaxHp => "damage",
        Kind.BlockMaxIntent => "Block",
        Kind.ApplyWeak => "Weak",
        Kind.ApplyVulnerable => "Vulnerable",
        // The two riders produce no number at all and fall to the default.
        // THE STATUS BATCH (2026-10-01).
        Kind.BlockPerStatusInHand => "Block",
        Kind.TransformStatusesYouHave => "cards transformed",
        // THE RE-FOUNDING (2026-10-12).
        Kind.AddStings => "cards added",
        Kind.GainStrength => "Strength",
        // THE POOL OVERHAUL (2026-10-13).
        Kind.DamagePerPlanThisTurn or Kind.DamageBlockedSince
            or Kind.DamageTakenSince => "damage",
        Kind.EnergyIfAttackedSince => "Energy",
        Kind.LoseStrengthThisTurn => "Strength lost",
        Kind.DrawPileToHand => "cards added",
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
    private static int? AskedFor(Creature kokomi, Planned plan,
                                 Entry? entry = null) => plan.Kind
        switch
    {
        Kind.DamageQuarterMaxHp => KokomiRules.QuarterOfMaxHp(kokomi),
        // THE POOL OVERHAUL (2026-10-13). Chain: the rate times the Plans
        // carried out this turn, this one included (the count rose before
        // the clauses ran). Counter: the entry's own window.
        Kind.DamagePerPlanThisTurn =>
            plan.Amount
            * KokomiOverhaulLedger.For(kokomi).PlansCarriedOutThisTurn,
        Kind.DamageBlockedSince =>
            KokomiOverhaulLedger.For(kokomi).BlockedSince(entry?.Window),
        Kind.DamageTakenSince =>
            KokomiOverhaulLedger.For(kokomi).TakenSince(entry?.Window),
        // R276. Tide Wall asks for the largest intent plus its bonus.
        Kind.BlockMaxIntent =>
            KokomiOverhaulKit.MostIntendedDamage(kokomi) + plan.Amount,
        // THE STATUS BATCH: Kelp Wall's rate times the statuses in hand
        // when the Plan was written (Kokomi round-1 fixes, 2026-10-12).
        Kind.BlockPerStatusInHand =>
            plan.Amount * (plan.WrittenCount
                ?? KokomiStatusBatch.StatusesInHand(kokomi.Player)),
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
    /// <see cref="Aim.EnemiesIntendingAttack"/> (Flank) reads the intents on
    /// the board AT CARRY-OUT since the Kokomi level pass (2026-10-12), as
    /// Tide Wall does: the living, hittable enemies that intend to attack.
    /// </summary>
    /// <param name="entry">`EB-643`. The entry the clause belongs to, for its
    /// <see cref="Entry.AimOverride"/> alone: Converging Tide re-points
    /// <see cref="Aim.FrontEnemy"/> and nothing else, so the override is read
    /// on that branch and only while the body it names is still on the board.
    /// Null is "no entry to ask", which is the honest answer for a caller
    /// resolving a bare clause.</param>
    private static IEnumerable<Creature> Aimed(Creature kokomi, Planned plan,
                                               Entry? entry = null)
    {
        var combat = kokomi.CombatState;
        if (combat == null) yield break;
        if (plan.Aim == Aim.EnemiesIntendingAttack)
        {
            // The Kokomi level pass (2026-10-12): the intents on the board at
            // carry-out, Tide Wall's read.
            foreach (var enemy in IntendingAttack(kokomi))
            {
                yield return enemy;
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
        if (plan.Aim == Aim.EnemiesAttackedSince)
        {
            // THE POOL OVERHAUL (2026-10-13), Brine Sting: each living,
            // hittable enemy whose Attack hit her since this Plan was
            // written, once each, in board order. Sim twin:
            // `kokomi_plan._aimed`.
            var hitBy = KokomiOverhaulLedger.For(kokomi)
                .AttackersSince(entry?.Window);
            foreach (var enemy in combat.HittableEnemies.Where(IsAlive)
                         .Where(e => hitBy.Contains(e.CombatId.ToString() ?? ""))
                         .ToList())
            {
                yield return enemy;
            }
            yield break;
        }
        // `EB-643`, CONVERGING TIDE. The one aim a now-line may re-point:
        // "every queued Plan aims at this enemy instead of the front". Read
        // ONLY WHILE THAT BODY IS STILL ON THE BOARD and falling back to the
        // front otherwise, which is the same "a Plan that lands on nothing
        // lands on nothing" rule every other aim keeps -- and deliberately not
        // extended to `AllEnemies` or Flank's captured set: neither of those
        // aims at the front, so there is nothing on either for "instead of the
        // front" to be about.
        if (entry?.AimOverride is { } wanted)
        {
            var chosen = combat.HittableEnemies.Where(IsAlive)
                .FirstOrDefault(e => e.CombatId.ToString() == wanted);
            if (chosen != null)
            {
                yield return chosen;
                yield break;
            }
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
    /// <param name="doubleDamage">`EB-643`, Opening Gambit's rider, and it
    /// lands HERE -- the one funnel every damaging Plan clause goes through,
    /// so "the next Plan deals double damage" is true of the flat hit, of
    /// Sango Isshin's quarter and of Chain of Command's per-Companion total
    /// without three separate readings.
    ///
    /// AFTER THE FOLD AND BEFORE THE BOARD, which is what the printed order
    /// says: her Strength and her enchantment are already inside
    /// <paramref name="amount"/> (folded at writing time, <see cref="Hers"/>),
    /// the doubling is applied to that written number, and the target's
    /// Vulnerable and Block are read after it by <see cref="ElementalHit.Deal"/>
    /// as they always are. It doubles the SIZE and not the number of passes,
    /// so Pincer's three hits stay three and each is twice as large -- which
    /// is the difference that matters against Block.</param>
    private static async Task<int?> Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan,
        int amount, Entry? entry = null, bool doubleDamage = false)
    {
        if (amount <= 0) return null;
        if (doubleDamage) amount *= 2;
        // TELEMETRY ONLY: a Plan's hit is the Bake-Kurage's (`EB-334`), so it
        // is Kokomi's pet damage. The applier the engine reads is unchanged.
        // `damage_by_source` files it under the card that wrote the Plan
        // (the one a cancel would return), so a Plan card's damage reads per
        // card; "(Bake-Kurage)" only where no card is known. The same name is
        // the cause a reaction inside the hit reports.
        var writer = entry?.Returns;
        var writerName = writer == null
            ? null : Diagnostics.PlayTelemetry.CardNameOf(writer);
        using var credit = Diagnostics.DamageCredit.Open(
            kokomi, Diagnostics.DamageCredit.Pet, "Bake-Kurage",
            cause: writerName, card: writerName);
        // THE POOL OVERHAUL (2026-10-13): a Plan line's hit is the writing
        // card's own hit -- a written Sting's reacts for Jellyfish Current, a
        // Companion's Plan line for Coordinated Tide. `ElementalHit.Deal`
        // carries no card, so the reaction reads it off this scope. Sim
        // twin: `kokomi_plan._resolve_entry`'s `kk_hit_card`.
        using var hitCard = KokomiRefounding.CreditHits(entry?.Source);
        var times = plan.Times < 1 ? 1 : plan.Times;
        int? first = null;
        var aimedAtAnyone = false;
        for (var pass = 0; pass < times; pass++)
        {
            foreach (var target in Aimed(kokomi, plan, entry))
            {
                if (target.IsDead) continue;
                aimedAtAnyone = true;
                var landed = await ElementalHit.Deal(
                    choiceContext, target, Element.Hydro, amount, kokomi,
                    powered: false);
                // A MORNING HIT'S HYDRO IS WHOLE (co-op playtest 2026-09-30).
                // The aura tick runs after this broadcast, so without the
                // spare the Hydro just applied or refreshed reads 1 turn, not
                // 2 -- one turn short of a card's, and short of the sim's,
                // which ticks before the morning. See
                // <see cref="AuraPower.SpareThisTurnStartTick"/>.
                if (kokomi.Player is { } owner && _morning.Contains(owner))
                {
                    AuraPower.SpareThisTurnStartTick(target, Element.Hydro);
                }
                first ??= landed;
            }
        }
        if (!aimedAtAnyone && kokomi.Player is { } seat
            && _carrying.Contains(seat))
        {
            _aimedAtNoOne.Add(seat);
        }
        return first;
    }

    /// <summary>A planned Weak or Vulnerable. It takes the entry for
    /// <see cref="Hit"/>'s reason (`EB-643`): a single-target debuff aims at
    /// the front, and Converging Tide re-points exactly that aim.</summary>
    private static async Task Debuff<T>(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan,
        Entry? entry = null)
        where T : PowerModel
    {
        foreach (var target in Aimed(kokomi, plan, entry))
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
            // A hit that found no living body to aim at (BACKLOG 2026-10-13).
            ["no_target"] = said.NoTarget,
            // Kokomi review r8 (2026-10-14, item 9): the reactions its own
            // hits set off, which the receipt names beside a number above
            // its ask (a Vaporize). Null where none.
            ["reactions"] = said.Reactions?.ToList(),
            // Kokomi v2 seats (2026-10-18): a carry-out past an entry's
            // first names the card that bought it. Null on the first.
            ["again"] = said.Again,
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
    /// <summary>
    /// `EB-773`. The damage this queued entry has WRITTEN against a single
    /// body, or 0.
    ///
    /// ONLY <see cref="Kind.Damage"/>, and only where it aims at the front.
    /// The other damage kind is derived at CARRY-OUT --
    /// <see cref="Kind.DamageQuarterMaxHp"/> off the target's max HP -- so a
    /// number for it here would be a forecast, and this
    /// key's whole claim is that it is a read of a number already fixed
    /// (`PLAN_WRITTEN_NUMBER_NOTE`). An entry that mixes one in reports the
    /// part it knows, and the page's own sentence says "may".
    ///
    /// <see cref="Planned.Times"/> MULTIPLIES, because "deal 3 damage three
    /// times" is three hits into the same aim and the running total the page
    /// keeps is a total. Block is the page's subtraction, not this one's: the
    /// body's Block is a fact about the board at the morning and it is on the
    /// wire already.
    /// </summary>
    private static int WrittenFrontDamage(Entry entry) =>
        entry.Clauses
            .Where(clause => clause.Kind == Kind.Damage
                             && clause.Aim == Aim.FrontEnemy)
            .Sum(clause => clause.Amount * System.Math.Max(1, clause.Times));

    /// <summary>
    /// What <see cref="WrittenFrontDamage"/> will deal at the front body:
    /// the written number with that body's Vulnerable folded, the call the
    /// card face prints (<see cref="PlannedDamage"/>). An entry Converging
    /// Tide has stamped at another body keeps its written number, since the
    /// front is not where it lands.
    /// </summary>
    public static int ForecastFrontDamage(Entry entry, Creature? kokomi,
                                          bool doubled = false)
    {
        var written = WrittenFrontDamage(entry);
        // Kokomi review r9 (2026-10-15, item 4): Opening Gambit's rider
        // doubles the written number BEFORE the board, as `Hit` does.
        if (doubled) written *= 2;
        if (written <= 0 || entry.AimOverride != null) return written;
        return PlannedDamage(FrontEnemy(kokomi), written);
    }

    /// <summary>
    /// Set a waiting two-line Plan's printed plan-line damage to what it will
    /// deal. Only for an entry with exactly one front damage clause whose
    /// card prints <see cref="PlanDamageVar"/>, and not for one aimed
    /// elsewhere by Converging Tide. Display only.
    /// </summary>
    private static void ShowQueuedPlanDamage(Entry entry, Creature? kokomi,
                                             bool doubled = false)
    {
        if (entry.AimOverride != null || entry.Source == null) return;
        var front = entry.Clauses
            .Where(c => c.Kind == Kind.Damage && c.Aim == Aim.FrontEnemy)
            .ToList();
        if (front.Count != 1) return;
        if (!entry.Source.DynamicVars.TryGetValue(PlanDamageVar.VarName,
                                                  out var v)
            || v is not PlanDamageVar planVar) return;
        planVar.ShowQueued(PlannedDamage(FrontEnemy(kokomi),
            doubled ? front[0].Amount * 2 : front[0].Amount));
    }

    /// <summary>
    /// `EB-773`. WHERE this queued entry's damage lands, in one word.
    ///
    /// "front" is the single-target aim `PLAN_AIM_NOTE` describes and the only
    /// one the page's running total is about. "all" is a Plan whose face says
    /// ALL, which takes every living body and cannot be over-killed past the
    /// front one. "other" is <see cref="Entry.AimOverride"/> -- Converging
    /// Tide has stamped a body by <c>CombatId</c> and the page has no way to
    /// resolve that id against the list it prints, so it says nothing rather
    /// than guessing. "" is an entry with no damage clause at all.
    /// </summary>
    private static string WrittenAim(Entry entry)
    {
        var damage = entry.Clauses.Where(clause =>
            clause.Kind == Kind.Damage
            || clause.Kind == Kind.DamageQuarterMaxHp).ToList();
        if (damage.Count == 0) return "";
        if (entry.AimOverride != null) return "other";
        if (damage.Any(clause => clause.Aim == Aim.AllEnemies)) return "all";
        return damage.Any(clause => clause.Aim == Aim.FrontEnemy)
            ? "front" : "other";
    }

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
            .Select((entry, index) => (object?)QueueRow(
                entry, creature, index,
                index > 0 && DoubledBy(pending[index - 1], entry)))
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
        // `EB-654`. WHAT A COMPANION SUMMON DID AT THE END OF THE LAST TURN,
        // in the same rows and read by the same page code. A separate key
        // because it is a separate MOMENT: these fired after the last page a
        // seat saw, which is exactly why they arrived unexplained.
        //
        // PRESENT AND EMPTY WHERE NOTHING FIRED, the whole snapshot's
        // three-state discipline: the key is here because the log is here.
        snapshot["summon_hits"] =
            SummonHits(player).Select(CarriedOutRow).ToList();
        return snapshot;
    }

    /// <summary>One waiting Plan on the wire. A named method for
    /// <see cref="CarriedOutRow"/>'s reason: the key names are the contract
    /// with `understudy/blindplay_board.kokomi_plans`.</summary>
    private static Dictionary<string, object?> QueueRow(
        Entry entry, Creature? kokomi, int index = 0, bool doubled = false)
    {
        // A PLAN STAYS OPEN (2026-10-01): a two-line Plan carries both lines
        // while it waits, so the choice is readable a turn early (sec.3).
        // The Plan list prints what the Plan will deal: a queued card is in
        // no pile, so the game never refreshes its face, and the plan line
        // is set here to the written number with the front body's Vulnerable
        // folded (`PlannedDamage`), before the face is read.
        // Kokomi review r9 (2026-10-15, item 4): the Plan Opening Gambit's
        // rider reaches shows the doubled number, the one that will land.
        if (entry.TwoLine) ShowQueuedPlanDamage(entry, kokomi, doubled);
        var (now, plan) = entry.TwoLine ? LineTexts(entry.Source)
            : ("", "");
        return new Dictionary<string, object?>
            {
                ["name"] = entry.Title,
                ["two_line"] = entry.TwoLine,
                ["now_line"] = now,
                ["plan_line"] = plan,
                // PICK 5 (a): the line it will be carried out as, "now" once
                // the player has flipped it, "plan" otherwise.
                ["line"] = entry.Now && entry.TwoLine ? "now" : "plan",
                ["clauses"] = entry.Clauses.Count,
                // `EB-773`. WHAT THIS ENTRY HAS ALREADY WRITTEN AGAINST THE
                // FRONT BODY, so the blind page can say that a Plan queued
                // behind a lethal one will find its target gone. The seat
                // read in `EB-714` is the row: two 8-damage Plans into an
                // 11-HP body, the second landing on 3 HP with 5 wasted, and
                // "nothing on the Plan screen warns you".
                //
                // THE NUMBERS ARE ALREADY FIXED, which is what makes this
                // reportable at all: `PLAN_WRITTEN_NUMBER_NOTE`'s rule is
                // that a written Plan carries the number it was written with.
                // So these two keys are a read of state, not a forecast.
                //
                // A FLIPPED PLAN WRITES NOTHING AT THE FRONT: its now-line is
                // carried out instead, at printed size, and the forecast
                // follows the flip (pick 5a).
                // And the number is what the morning will deal: the front
                // body's Vulnerable folded, the face's own `PlannedDamage`.
                ["damage"] = entry.Now && entry.TwoLine
                    ? 0 : ForecastFrontDamage(entry, kokomi, doubled),
                // Item 4: the number above already carries the rider.
                ["doubled"] = doubled && !(entry.Now && entry.TwoLine),
                ["aim"] = entry.Now && entry.TwoLine ? "" : WrittenAim(entry),
                // Kokomi whole-run round 2 (2026-10-10): the printed Plan
                // line folds the front body's Vulnerable (`PlanDamageVar`),
                // and a seat read the number rising as the Plan changing.
                // The page says "(after Vulnerable)" where it did.
                ["after_vulnerable"] = RaisedByVulnerable(entry, kokomi),
                // Kokomi review 2026-10-13: a Block Plan that reads the
                // board (Tide Wall) carries its total against the board as it
                // stands, Frail and Dexterity folded; null for every other
                // entry. The page prints it beside the name.
                ["block_now"] = LiveBlock(entry, kokomi),
                // THE POOL OVERHAUL (2026-10-13): a Counter or Chain Plan's
                // number as it stands, the strip's caption ("Deals 14",
                // "2 attackers", "Energy 1"); null for every other entry.
                ["live"] = LiveLine(entry, kokomi, index),
                // KOKOMI REVIEW R5 (2026-10-14, A2): what the Plan will land
                // per body, every flat hit summed whatever its aim, and her
                // Strength when it was written. Zero and null on a Plan with
                // no flat hit, and on a flipped one.
                ["written"] = entry.Now && entry.TwoLine
                    ? 0 : WrittenDamage(entry) * (doubled ? 2 : 1),
                ["written_strength"] = entry.Now && entry.TwoLine
                    ? null : entry.WrittenStrength,
                // KOKOMI REVIEW R6 (2026-10-14, item 7): a Counter Plan that
                // pays only for an enemy Attack in its window -- "attackers"
                // (Brine Sting), "blocked" (Kelp Wall), "energy" (Prepared
                // Retreat) -- so the page can warn when no enemy intends to
                // attack. Null for every other entry and a flipped one.
                ["needs_attack"] = entry.Now && entry.TwoLine
                    ? null : NeedsAttack(entry),
                // Item 11: the card written is an Attack, which the base
                // game counts as an Attack played this turn (Ripple Basin).
                ["attack"] = entry.Source?.Type == CardType.Attack,
                // KOKOMI ROUND 7 (2026-10-14): the Plan plays a card through
                // the game's own auto-play, which Ringing counts as the
                // turn's one card; and where the Vulnerable it applies lands,
                // which a later Plan's hit in the same morning meets. Display
                // only; false and "" for a flipped one.
                ["plays_card"] = !(entry.Now && entry.TwoLine)
                    && PlaysACard(entry),
                ["vulnerable_aim"] = entry.Now && entry.TwoLine
                    ? "" : VulnerableAim(entry),
            };
    }

    /// <summary>KOKOMI ROUND 7 (2026-10-14): does carrying this entry out
    /// play a card? Moon's Reflection (<see cref="Replay"/>) and Crystal Collapse
    /// (<see cref="PlayCopy"/>) go through <c>CardCmd.AutoPlay</c>, which
    /// logs a card play the way the base game's own auto-plays do, so
    /// <c>RingingPower.ShouldPlay</c> counts it. Every other clause plays no
    /// card. Display only.</summary>
    public static bool PlaysACard(Entry entry) =>
        entry.Clauses.Any(clause => clause.Kind is Kind.ReplayExhausted
            or Kind.PlayCopyOfCompanion);

    /// <summary>KOKOMI ROUND 7 (2026-10-14): where this entry's Vulnerable
    /// lands, in <see cref="WrittenAim"/>'s words ("all", "front", "other"),
    /// or "" for an entry that applies none. Display only.</summary>
    public static string VulnerableAim(Entry entry)
    {
        var vulnerable = entry.Clauses
            .Where(clause => clause.Kind == Kind.ApplyVulnerable).ToList();
        if (vulnerable.Count == 0) return "";
        if (entry.AimOverride != null) return "other";
        if (vulnerable.Any(clause => clause.Aim == Aim.AllEnemies))
        {
            return "all";
        }
        return vulnerable.Any(clause => clause.Aim == Aim.FrontEnemy)
            ? "front" : "other";
    }

    /// <summary>KOKOMI REVIEW R6 (2026-10-14, item 7): which Counter reading
    /// this entry pays off an enemy Attack in its window, in the page's word,
    /// or null. Display only.</summary>
    public static string? NeedsAttack(Entry entry)
    {
        foreach (var clause in entry.Clauses)
        {
            switch (clause.Kind)
            {
                case Kind.DamageBlockedSince: return "blocked";
                case Kind.EnergyIfAttackedSince: return "energy";
                case Kind.Damage when clause.Aim == Aim.EnemiesAttackedSince:
                    return "attackers";
            }
        }
        return null;
    }

    /// <summary>KOKOMI REVIEW R6 (2026-10-14, item 7): does any living enemy
    /// intend to attack right now? The arm's one definition
    /// (<see cref="KokomiRefounding.EnemiesIntendingAttack"/>).</summary>
    public static bool AnyEnemyIntendsAttack(Creature kokomi) =>
        KokomiRefounding.EnemiesIntendingAttack(kokomi) > 0;

    /// <summary>KOKOMI REVIEW R5 (2026-10-14, A2): the flat hits this entry
    /// has written, per body, whatever their aim -- the number a page prints
    /// as what the Plan will land. Display only.</summary>
    public static int WrittenDamage(Entry entry) =>
        entry.Clauses
            .Where(clause => clause.Kind == Kind.Damage)
            .Sum(clause => clause.Amount * System.Math.Max(1, clause.Times));

    /// <summary>
    /// THE POOL OVERHAUL (2026-10-13): a waiting Counter or Chain Plan's
    /// number as it stands, in the strip's words, or null for any other
    /// entry, a flipped one, or no combat. Display only.
    ///
    /// COUNTER: its window so far -- Kelp Wall "N blocked so far" (the damage
    /// she has blocked since it was written), Turnabout "N taken so far" (all
    /// the damage enemies have dealt her), Brine Sting "N attackers", Prepared Retreat
    /// "Energy N" or "No attack yet".
    ///
    /// CHAIN: what it deals if the queue lands as it stands at the start of
    /// her next turn: the rate times its place in the queue
    /// (<paramref name="index"/> + 1), one more behind a first Plan Nereid's
    /// Ascension doubles. A Change of Plans or a Second Wave moves it; the
    /// carry-out reads the real count.
    /// </summary>
    public static string? LiveLine(Entry entry, Creature? kokomi, int index)
    {
        if (kokomi?.CombatState == null) return null;
        if (entry.Now && entry.TwoLine) return null;
        try
        {
            var ledger = KokomiOverhaulLedger.For(kokomi);
            foreach (var clause in entry.Clauses)
            {
                switch (clause.Kind)
                {
                    // Kokomi wording pass (2026-10-14): Crystal Collapse's
                    // picture names the Companion it caught.
                    case Kind.PlayCopyOfCompanion:
                        return CopiesCaption(clause.Card?.Title.ToString());
                    case Kind.DamagePerPlanThisTurn:
                        var twice = index > 0
                            && kokomi.Powers.OfType<NereidsAscensionPower>()
                                    .Any();
                        return LiveDeals(clause.Amount
                            * (index + 1 + (twice ? 1 : 0)));
                    // KOKOMI REVIEW R5 (2026-10-14, A3): a Counter's running
                    // count in its own words ("7 blocked so far"); the hit
                    // is that count.
                    case Kind.DamageBlockedSince:
                        var blocked = ledger.BlockedSince(entry.Window);
                        // KOKOMI REVIEW R6 (2026-10-14, item 7).
                        if (blocked == 0 && !AnyEnemyIntendsAttack(kokomi))
                            return NoAttackIntended;
                        return LiveBlocked(blocked);
                    case Kind.DamageTakenSince:
                        return LiveTaken(ledger.TakenSince(entry.Window));
                    case Kind.EnergyIfAttackedSince:
                        if (ledger.AttackedSince(entry.Window))
                            return $"Energy {clause.Amount}";
                        return AnyEnemyIntendsAttack(kokomi)
                            ? NoAttackYet : NoAttackIntended;
                    case Kind.Damage when clause.Aim == Aim.EnemiesAttackedSince:
                        var n = ledger.AttackersSince(entry.Window).Count;
                        if (n == 0)
                            return AnyEnemyIntendsAttack(kokomi)
                                ? NoAttackYet : NoAttackIntended;
                        return n == 1 ? "1 attacker" : $"{n} attackers";
                }
            }
            return null;
        }
        catch (System.Exception)
        {
            return null;
        }
    }

    /// <summary>Crystal Collapse's caption (Kokomi wording pass,
    /// 2026-10-14): "Copies Juuga", the caught card's own name -- the half
    /// after a Companion's em dash, cut at a colon so it fits the picture --
    /// or "Copies nothing". PURE. The full name is the entry's
    /// <see cref="Entry.Title"/>.</summary>
    public static string CopiesCaption(string? title)
    {
        if (string.IsNullOrWhiteSpace(title)) return "Copies nothing";
        var name = title!;
        var dash = name.LastIndexOf('—');
        if (dash >= 0) name = name.Substring(dash + 1).Trim();
        var colon = name.IndexOf(':');
        if (colon > 0) name = name.Substring(0, colon).Trim();
        if (name.Length == 0) name = title!.Trim();
        return "Copies " + name;
    }

    /// <summary>The strip's damage caption, "Deals N".</summary>
    public static string LiveDeals(int amount) => $"Deals {amount}";

    /// <summary>Kelp Wall's running count, "N blocked so far" (Kokomi
    /// review r5, 2026-10-14, A3).</summary>
    public static string LiveBlocked(int amount) => $"{amount} blocked so far";

    /// <summary>Turnabout's running count, "N taken so far".</summary>
    public static string LiveTaken(int amount) => $"{amount} taken so far";

    /// <summary>A Counter Plan no enemy has attacked into yet.</summary>
    public const string NoAttackYet = "No attack yet";

    /// <summary>KOKOMI REVIEW R6 (2026-10-14, item 7): a Counter Plan that
    /// pays only for an enemy Attack, on a board where no enemy intends one,
    /// so as things stand it lands nothing.</summary>
    public const string NoAttackIntended = "No enemy intends to attack";

    /// <summary>
    /// THE KOKOMI REVIEW (2026-10-13), Tide Wall's live total. "Tide Wall
    /// paid 4 on a Defend turn and 29 on an attack turn ... the screen never
    /// told me" (A F10). The Block this entry would give if it were carried
    /// out on the board as it stands: each Block clause's
    /// <see cref="AskedFor"/>, folded through <c>Hook.ModifyBlock</c> with the
    /// payout's own arguments (<see cref="Kind.Block"/>'s
    /// <c>GainBlock(kokomi, n, ValueProp.Move, null)</c>), so Frail and
    /// Dexterity read it as the carry-out will.
    ///
    /// ONLY FOR AN ENTRY THAT READS THE BOARD (<see cref="Kind.BlockMaxIntent"/>):
    /// a flat Block Plan already prints its number on its face. Null for
    /// every other entry, for a flipped Plan (its now-line is carried out
    /// instead) and where there is no combat to read. The intents it reads
    /// are the ones up NOW; the carry-out reads them again on the turn it
    /// lands, which is what the face says.
    /// </summary>
    public static int? LiveBlock(Entry entry, Creature? kokomi)
    {
        if (kokomi?.CombatState is not { } combat) return null;
        if (entry.Now && entry.TwoLine) return null;
        if (!entry.Clauses.Any(c => c.Kind == Kind.BlockMaxIntent)) return null;
        try
        {
            var total = 0m;
            foreach (var clause in entry.Clauses)
            {
                if (clause.Kind is not (Kind.Block or Kind.BlockMaxIntent
                                        or Kind.BlockPerStatusInHand))
                {
                    continue;
                }
                var asked = AskedFor(kokomi, clause) ?? 0;
                if (asked <= 0) continue;
                total += FoldUnsourcedBlock(combat, kokomi, asked);
            }
            return (int)total;
        }
        catch (System.Exception)
        {
            return null;
        }
    }

    /// <summary>
    /// <c>Hook.ModifyBlock</c>'s fold for a Block with no card source -- the
    /// carry-out's own arguments (<c>ValueProp.Move</c>, no card, no play) --
    /// walked over the combat's listeners directly, as
    /// <c>FoldedCalculatedBlockVar.Fold</c> does and for its reason: the
    /// hook's own walk yields nothing while the combat manager says the
    /// combat is ending, and a display read is not a dispatch. Every
    /// listener's additive term (Dexterity), then every multiplier (Frail),
    /// floored at 0.
    /// </summary>
    internal static decimal FoldUnsourcedBlock(
        ICombatState combat, Creature kokomi, decimal block)
    {
        var num = block;
        var listeners = combat.IterateHookListeners().ToList();
        foreach (var model in listeners)
        {
            num += model.ModifyBlockAdditive(kokomi, num, ValueProp.Move,
                                             null, null);
        }
        foreach (var model in listeners)
        {
            num *= model.ModifyBlockMultiplicative(kokomi, num, ValueProp.Move,
                                                   null, null);
        }
        return System.Math.Max(0m, num);
    }

    /// <summary>
    /// THE KOKOMI REVIEW (2026-10-13): "Plans into enemy Block" -- three seats
    /// on four turns wrote an Attack Plan into Block they had been warned
    /// about (C F4, C F14, B F8, A F5). The Block the front body will still
    /// be standing in at the morning, which is its Block NOW only where it
    /// keeps Block through its own turn start (the game's own
    /// <c>Hook.ShouldClearBlock</c>: Barricade, Burrowed); a body that clears
    /// it meets the Plan with whatever it gains on its turn, which no intent
    /// prices (<see cref="DefendsAhead"/>). 0 for an entry with no front
    /// damage written, a flipped Plan, or no front body.
    /// </summary>
    public static int KeptBlockAhead(Entry entry, Creature? kokomi)
    {
        if (entry.Now && entry.TwoLine) return 0;
        if (WrittenAim(entry) != "front") return 0;
        var front = FrontEnemy(kokomi);
        if (front == null || front.CombatState is not { } combat) return 0;
        try
        {
            if (front.Block <= 0) return 0;
            return MegaCrit.Sts2.Core.Hooks.Hook.ShouldClearBlock(
                    combat, front, out _)
                ? 0
                : (int)front.Block;
        }
        catch (System.Exception)
        {
            return 0;
        }
    }

    /// <summary>Does the front body intend to Defend this turn? Its Block
    /// will be up when a waiting Attack Plan lands. False with no front
    /// damage written or no front body.</summary>
    public static bool DefendsAhead(Entry entry, Creature? kokomi)
    {
        if (entry.Now && entry.TwoLine) return false;
        if (WrittenAim(entry) != "front") return false;
        var front = FrontEnemy(kokomi);
        try
        {
            return front?.Monster?.NextMove?.Intents.Any(
                intent => intent.IntentType ==
                    MegaCrit.Sts2.Core.MonsterMoves.Intents.IntentType.Defend)
                ?? false;
        }
        catch (System.Exception)
        {
            return false;
        }
    }

    /// <summary>
    /// THE KOKOMI REVIEW (2026-10-13): the words under one waiting Plan's
    /// picture on the strip, or null for none. PURE over its inputs, so a
    /// headless test can read every branch.
    ///
    /// ONE LINE, IN THIS ORDER. A flipped Plan says it is the now-line (the
    /// tint says so too). A Plan that reads the board prints its total
    /// ("Block 29"). An Attack Plan says what Block it will land in ("into 8
    /// Block", or "into Block" where the body defends and the size is not
    /// known). A two-line Plan otherwise says "Plan line".
    /// </summary>
    public static string? StripCaption(bool twoLine, bool flipped,
                                       int? blockNow, int keptBlock,
                                       bool defends, string? live = null)
    {
        if (twoLine && flipped) return Vfx.KokomiPlanStrip.NowLineCaption;
        if (blockNow is { } block) return $"Block {block}";
        // THE POOL OVERHAUL (2026-10-13): a Counter or Chain Plan's number
        // as it stands (<see cref="LiveLine"/>).
        if (live != null) return live;
        if (keptBlock > 0) return $"into {keptBlock} Block";
        if (defends) return "into Block";
        return twoLine ? Vfx.KokomiPlanStrip.PlanLineCaption : null;
    }

    /// <summary>Does the front body's Vulnerable raise the damage this entry
    /// has written at it? False with no front damage, no front body or no
    /// Vulnerable on it. The same fold the face prints
    /// (<see cref="PlannedDamage"/>).</summary>
    public static bool RaisedByVulnerable(Entry entry, Creature? kokomi)
    {
        var written = WrittenFrontDamage(entry);
        if (written <= 0) return false;
        var front = FrontEnemy(kokomi);
        if (front == null || !VulnerableAtMorning(front))
            return false;
        return PlannedDamage(front, written) > written;
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
        await RefreshBadge(choiceContext, kokomi, count);
    }

    /// <summary>
    /// THE BADGE ALONE, OFF THE TRUE QUEUE DEPTH -- <see cref="Sync"/>'s
    /// second half, split out in round 23 (beside `EB-650`).
    ///
    /// WHY IT IS SEPARATE. <see cref="ResolveAll"/>'s capped path clears the
    /// queue, syncs at depth 0 -- which REMOVES the badge -- drains, and only
    /// then puts the held entries back at the front. It had no second sync, so
    /// a capped morning left the player holding Plans with no badge saying so:
    /// the one surface that answers "how many are written" read absent while
    /// the queue was not empty.
    ///
    /// AND IT DOES NOT NOTE THE METER, which is the whole reason it is not
    /// simply a second <see cref="Sync"/>. `R101b` and
    /// <c>KurageBeatTests.The_morning_still_mints_exactly_one_ledger_row</c>
    /// hold the drain to ONE row on a published instrument: the display list
    /// exists precisely so the strip can shorten per entry without the ledger
    /// moving per entry, and a second row here would be a second row on a
    /// record that has already been published. The badge is the PLAYER's
    /// surface and the meter is the instrument; only the first was wrong.
    /// </summary>
    private static async Task RefreshBadge(
        PlayerChoiceContext choiceContext, Creature kokomi, int count)
    {
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
        }
        else
        {
            await PowerCmd.ModifyAmount(
                choiceContext, badge, count - badge.Amount, applier: kokomi,
                cardSource: null, silent: true);
        }
        // THE KOKOMI REVIEW (2026-10-13): "The Plan badge text ('Next turn,
        // the Bake-Kurage carries out 1 Plan') stayed even when 2 plans were
        // written" (D2). `PowerCmd` runs the power-amount modifier chain
        // (`Hook.ModifyPowerAmountGiven` / `Received`) on the way in, and the
        // badge is a COUNT, not a buff any modifier may resize. So the
        // queue's depth is written over whatever the chain left.
        PinBadge(kokomi, count);
    }

    /// <summary>Set the badge's amount to the queue's depth, whatever the
    /// modifier chain did to it (Kokomi review 2026-10-13). No badge, no
    /// write. Display only: the badge is read by nothing that decides.</summary>
    public static void PinBadge(Creature kokomi, int count)
    {
        var badge = kokomi.Powers.OfType<PendingPlansPower>().FirstOrDefault();
        if (badge == null || count <= 0 || badge.Amount == count) return;
        badge.SetAmount(count);
    }

    /// <summary>
    /// WHAT A PLANNED HIT OF <paramref name="amount"/> LANDS FOR RIGHT NOW --
    /// the whole of what `EB-334` left live on a Plan's damage AT THE MORNING.
    ///
    /// ONE TERM, and naming it is the point: R246 pick 1 took the dealer's
    /// side off a planned hit, so the only modifier between the queued number
    /// and the board is the TARGET's, which is
    /// <see cref="SimDamagePipeline.TargetMods"/> -- the same call
    /// <see cref="ElementalHit.Deal"/> makes on the same target a beat later.
    ///
    /// `EB-599` TOOK THIS OFF THE FACE for one build and the live look of
    /// 2026-09-16 put it back (`EB-334`): a Plan printed "Deal 10" and the
    /// morning carried out 15 against a Vulnerable-2 body, which is the two
    /// numbers R246 pick 1 forbids. `EB-599` was the r22 packet's D default
    /// and R246 is [USER]'s ruling, so the default yields; what survives of it
    /// is the Plan word saying WHEN each side is read, which is the fact a
    /// printed number cannot carry on its own.
    ///
    /// THE REACTION AMPLIFIER IS DELIBERATELY LEFT OUT, exactly as
    /// <c>ProtoBombPower.PredictedSetOffDamage</c> leaves it out and for the
    /// same reason: it is one-shot rather than standing state, and an
    /// all-enemies Plan consumes the aura the rest of the volley would have
    /// reacted with, so there is no one multiplier for the line.
    ///
    /// ONLY A VULNERABLE THAT WILL STILL BE UP (Kokomi round-3 changes,
    /// 2026-10-12). The Plan lands next morning, after the enemy's turn has
    /// ticked its Vulnerable down by one, so a Vulnerable of 1 is gone by
    /// then: seats read Oath 13 and saw 9, Lance 27 and 18. The face folds the
    /// target's Vulnerable only at 2 or more
    /// (<see cref="VulnerableAtMorning"/>). The carry-out itself is
    /// unchanged: <see cref="ElementalHit.Deal"/> reads the Vulnerable the
    /// body wears THEN.
    /// </summary>
    public static int PlannedDamage(Creature? target, int amount) =>
        target == null || !VulnerableAtMorning(target)
            ? amount
            : (int)SimDamagePipeline.TargetMods(target, amount);

    /// <summary>Will <paramref name="target"/> still wear Vulnerable when a
    /// Plan written now is carried out? Its Vulnerable ticks down once at the
    /// end of the enemy turn between, so 2 or more.</summary>
    public static bool VulnerableAtMorning(Creature target) =>
        (target.Powers.OfType<VulnerablePower>().FirstOrDefault()?.Amount ?? 0)
            >= 2;

    /// <summary>
    /// `EB-599`. HER SIDE OF A PLAN LINE, FOLDED AT WRITING TIME -- her
    /// Strength on top of <see cref="Enchanted"/>'s rider.
    ///
    /// THE FIND (Kokomi r22 lane 2). <i>Kurage's Oath</i> printed "Plan: Deal
    /// 10" under the target's Vulnerable, the seat paid for it, and the
    /// morning carried out 7 once the Vulnerable had expired: "for a mechanic
    /// sold on committing a turn early, the committed number moving is the
    /// sharpest contradiction in the kit." Both lanes then read the two lines
    /// computing under two rules -- her Strength moved the own line only and
    /// the target's Vulnerable moved the Plan line only.
    ///
    /// THE RULE (r22 packet sec.5, a D default): the Plan line folds HERS and
    /// nothing of the target's. Rule 3 says her Strength counts for a
    /// carry-out, and a Plan resolves next morning against whatever the target
    /// wears THEN -- so the target's terms are exactly the ones a line written
    /// today cannot honestly print, and hers are the ones it can.
    ///
    /// HER STRENGTH AND NOT <see cref="SimDamagePipeline.DealerMods"/>, which
    /// is the one judgement in this method: that call also carries her Weak,
    /// and round four-c's finding is what took her Weak off a carry-out. The
    /// default names her Strength and her enchantments, so this folds those
    /// two and no more.
    ///
    /// AT WRITING TIME AND ONCE. <see cref="Hit"/> still goes out
    /// <c>powered: false</c>, so the queued number is the number the morning
    /// deals and nothing adds her Strength a second time.
    ///
    /// <paramref name="strengthTimes"/> (the big-Plan pass, 2026-10-04) is
    /// the clause's own "Strength affects this Plan N times": Masterstroke 3,
    /// Surging Shoal 2. The enchantment still counts once.
    ///
    /// Sim twin: `kokomi_plan.hers`.
    /// </summary>
    public static int Hers(Creature? kokomi, CardModel? source, int amount,
                           int strengthTimes = 1)
    {
        var folded = Enchanted(source, amount);
        if (folded <= 0 || kokomi == null) return folded;
        // Kokomi round-3 changes (2026-10-12): Watchful Shoal's Sting bonus,
        // folded where her Strength is, because a planned hit never reaches
        // the engine's damage hooks.
        return folded
             + WatchfulShoalPower.StingBonus(kokomi, source)
             + (int)(kokomi.Powers.OfType<StrengthPower>()
                           .FirstOrDefault()?.Amount ?? 0)
               * System.Math.Max(1, strengthTimes);
    }

    /// <summary>
    /// `EB-580`. THE CARD'S OWN ENCHANTMENT, FOLDED INTO ITS PLAN LINE.
    ///
    /// THE FIND (Kokomi r21 lane 2 (c) 3). A Sharp 2 raised Riptide's now-line
    /// from 9 to 11 and left its Plan line printing 13, with nothing on screen
    /// saying which of the two the enchantment had bought: the seat read the
    /// pair as evidence that the Plan was now the worse half, and it
    /// "silently reversed the right play on my best card". Ruled at the r21
    /// packet's D default -- a card's own enchantment applies to BOTH its
    /// lines, since both are the card's.
    ///
    /// WHY IT WAS MISSING RATHER THAN REFUSED. The game folds an enchantment
    /// inside <c>Hook.ModifyDamage</c>, off the play's <c>cardSource</c> --
    /// and a planned hit is not a card being played (`EB-538`), so it goes out
    /// through <see cref="ElementalHit.Deal"/> and that hook never sees the
    /// card at all. The rider is a fact about the CARD, so it is asked of the
    /// card, here, once.
    ///
    /// <c>ValueProp.Move</c> AND NOT THE PLANNED HIT'S <c>Unpowered</c>, which
    /// is the one argument in this method and is deliberate: the question is
    /// what the enchantment adds to THIS CARD'S PRINTED DAMAGE -- which is
    /// what a Plan line is -- and the base game's riders gate on the prop.
    /// MEASURED on the shipped assembly rather than assumed:
    /// <c>Corrupted</c> answers x1.5 to <c>Move</c> and x1 to
    /// <c>Unpowered</c>, so passing the hit's own prop would have answered a
    /// different question and dropped every multiplier; and
    /// <c>Multiplicative</c> returns a MULTIPLIER (1 where there is none)
    /// while <c>Additive</c> returns a DELTA.
    ///
    /// Sim twin: `kokomi_plan._enchanted`.
    /// </summary>
    public static int Enchanted(CardModel? source, int amount)
    {
        var enchantment = source?.Enchantment;
        if (enchantment == null || amount <= 0) return amount;
        var folded = amount
                   + enchantment.EnchantDamageAdditive(amount, ValueProp.Move);
        return (int)(folded * enchantment.EnchantDamageMultiplicative(
            folded, ValueProp.Move));
    }

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
    /// Strength buff should produce. <c>IntValue</c> is untouched and stays
    /// <c>BaseValue</c>, which is what matters: the emitted <c>PlanClauses</c>
    /// property builds the queued clause off <c>IntValue</c> and
    /// <see cref="Schedule"/> folds <see cref="Hers"/> onto it once, so the
    /// fold is applied exactly once and by one call.
    ///
    /// BOTH SIDES ARE ON THIS LINE. `EB-599` added hers -- her Strength and
    /// this copy's enchantment, folded at WRITING time by <see cref="Hers"/>
    /// so the face and the queue print one number (`EB-265`'s rule) -- and in
    /// the same move took the target's off, which the live look of 2026-09-16
    /// found printing 10 where the morning dealt 15. That half was a D default
    /// against [USER]'s R246 pick 1 and is reversed here; the fact it was
    /// reaching for (a Plan resolves against whatever the body wears NEXT
    /// morning) is carried by the Plan keyword's own sentence instead.
    ///
    /// OUTSIDE COMBAT IT PRINTS ITS BASE. A compendium or reward copy has no
    /// combat and no enemies, and `runGlobalHooks` is false off the hand, so
    /// every such read falls through to <c>BaseValue</c> exactly as a plain var
    /// would.
    /// </summary>
    public sealed class PlanDamageVar : DynamicVar
    {
        /// <summary>The clause's "Strength affects this Plan N times"
        /// (<see cref="Planned.StrengthTimes"/>), so the face previews the
        /// number <see cref="Schedule"/> queues.</summary>
        private readonly int _strengthTimes;

        public const string VarName = "PlanDamage";

        public PlanDamageVar(decimal amount, int strengthTimes = 1)
            : base(VarName, amount)
        {
            _strengthTimes = strengthTimes;
        }

        /// <summary>A queued card is in no pile, so nothing refreshes its
        /// face; <see cref="QueueRow"/> sets the number the Plan will deal
        /// before the Plan list reads it.</summary>
        internal void ShowQueued(int amount) => PreviewValue = amount;

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
            // `EB-580`: THE ENCHANTMENT FIRST, AND WITHOUT A BOARD. It is a
            // fact about THIS COPY of the card rather than about the fight, so
            // it folds on a reward screen and in a deck view as well -- which
            // is where the r21 seat was reading the two lines against each
            // other.
            PreviewValue = Enchanted(card, (int)BaseValue);
            var kokomi = card.Owner?.Creature;
            if (!KokomiOverhaul.LiveFor(kokomi)) return;
            // `EB-599`: AND HER STRENGTH, WHICH NEEDS THE CREATURE. It is
            // folded at WRITING time -- `Schedule` puts `Hers` onto the queued
            // clause -- so the face previews the same call the queue holds.
            PreviewValue = Hers(kokomi, card, (int)BaseValue, _strengthTimes);
            // Kokomi review r9 (2026-10-15, item 4): the Plan written now
            // goes behind the queue's last entry, and when that one is
            // Opening Gambit's the rider reaches this one. The face prints
            // the doubled number, the one that will land.
            var tail = Pending(card.Owner).LastOrDefault();
            if (WritesDoubleRider(tail)) PreviewValue *= 2;
            // AND THEN THE TARGET'S, WHICH `EB-599` HAD TAKEN OFF (live look
            // 8b, `EB-334`). A Plan printed "Deal 10" and carried out 15
            // against a body wearing Vulnerable 2, so the line and the
            // morning were two numbers again -- which is exactly what R246
            // pick 1 rules out: "the Plan line prints the number it will deal
            // against the enemy's current state".
            //
            // A RULING BEATS A D DEFAULT, and that is the whole decision here.
            // `EB-599` is the r22 packet sec.5 default (a D, taken by Claude,
            // recorded as one in the packet and in the row); R246 is [USER]'s,
            // and neither it nor any later ruling was amended when the default
            // was taken. So the default yields and the fold comes back.
            //
            // THE HONEST HALF OF `EB-599` SURVIVES AS THE PLAN WORD, not as a
            // missing term: the keyword says WHEN each side is read ("Your
            // Strength folds in as you write it; the enemy's Vulnerable counts
            // at the morning"), so a reader is told that the target's half of
            // this number is today's board and may not be tomorrow's. That
            // sentence is what a printed number cannot carry; dropping the
            // term instead made the printed number wrong today as well.
            //
            // THE BODY IS THE PLAN'S OWN, never the hovered one:
            // `Aim.FrontEnemy` is where a carry-out lands, and previewing
            // against whatever the cursor happens to be over would print a
            // number for a body the morning will not hit. `HitOrder` answers
            // the same question for every other folded face on this kit.
            PreviewValue = PlannedDamage(
                HitOrder.BodyForPreview(
                    card, previewMode, target, FrontEnemy(kokomi)),
                (int)PreviewValue);
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
/// A TWO-LINE card: a now-line and a Plan line (a Plan stays open,
/// 2026-10-01, ruled; review/active/kokomi-delay-pays-2026-10-01.md sec.2).
/// Emitted by the generator on every row with both <c>effects:</c> and
/// <c>plan:</c>. When the Bake-Kurage carries out a Plan this card wrote, the
/// player may take <see cref="PlayNowLine"/> instead of the Plan line
/// (<see cref="KokomiPlan.Flip"/>, <see cref="KokomiPlan.CarryOutNowLine"/>).
/// </summary>
public interface INowLineCard
{
    /// <summary>Where the now-line aims off the jellyfish: Divine Strategy's
    /// three answers.</summary>
    DivineStrategyPower.Aim NowLineAim { get; }

    /// <summary>The card's now-line, at printed size, on the play given.</summary>
    Task PlayNowLine(PlayerChoiceContext choiceContext, CardPlay cardPlay);
}

/// <summary>
/// The plan bus: "Whenever the jellyfish carries out a Plan, ...". Her
/// Ancient under the arm and the co-op set ride it; Treatise and Song of
/// Pearls left it in the Kokomi core pass (2026-09-27).
///
/// An interface rather than a type test, the same shape
/// <c>IProtoExplosionListener</c> takes and for the same reason: a listener
/// discovered by interface cannot be forgotten at wire-up.
/// </summary>
public interface IKokomiPlanListener
{
    /// <param name="choiceContext">Live context; a listener may draw or deal.</param>
    /// <param name="kokomi">The seat whose Plan was carried out.</param>
    /// <param name="line">The card whose line was carried out
    /// (<see cref="KokomiPlan.Entry.Source"/>): Kurage Canopy skips a Sting's
    /// or Ward's (Kokomi card paper v2, 2026-10-18).</param>
    Task OnPlanResolved(PlayerChoiceContext choiceContext, Creature kokomi,
                        CardModel? line);
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
            // THE 2026-09-25 TEXT PASS: the count and the order, nothing else.
            // "Later debuffs do
            // not change what you wrote" is the panel's
            // (`blindplay_notes.PLAN_WRITTEN_NUMBER_NOTE`). Spec:
            // `review/records/text-pass-2026-09-25/kokomi-rewrite.md`.
            "Next turn, the [gold]Bake-Kurage[/gold] carries out "
          + "[blue]{Amount}[/blue] [gold]Plan{Amount:plural:|s}[/gold] in "
          + "order."
          // `EB-653` (round 24). AND THE CAP, WHERE IT BINDS. Empty on an
          // unconfigured build, which is every build but a cap lane's; the
          // sentence is `KokomiPlan.CapSentence`'s, spelled once for both
          // badges.
          + KokomiPlan.CapSentence),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
