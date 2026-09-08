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
        // `EB-685`, POOL PASS FIVE. Breakwater: "Dusk Plan: Gain 5 Block,
        // plus 3 for each Plan the Bake-Kurage is HOLDING."
        //
        // WHY IT IS NOT THE LINE ABOVE, which is the count pool pass four gave
        // it: <see cref="BlockPerPlanThisMorning"/> is the MORNING's depth,
        // and a Dusk Plan lands on the evening of the turn it was written on
        // -- so a Breakwater written after an empty morning read 0 and paid
        // its base, which is what r27's two seats saw on four plays out of
        // four. The wall now rises on the turn the engine is WRITTEN.
        //
        // THE COUNT IS <see cref="PlansHeld"/> READ LIVE, at the moment this
        // entry resolves, and the two exclusions the face needs are true BY
        // CONSTRUCTION rather than by a filter: <see cref="ResolveDusk"/>
        // takes every dusk entry off the queue before the first clause runs,
        // so this entry is never one of the Plans it pays for and neither is a
        // second Dusk Plan written the same turn. What is left is exactly
        // "written this turn and still waiting for the next morning". A Plan
        // hurried out by Change of Plans has already left the queue and does
        // not count. Sim twin: `kokomi_plan.BLOCK_PER_PLAN_HELD`.
        BlockPerPlanHeld,
        // `EB-643`, R265. THE DRAIN-POSITIONAL CLAUSES, and what makes them one
        // group is that each names a PLACE IN A RUNNING DRAIN rather than a
        // quantity. They are plan-only on both sides for that reason
        // (`gen_klee_cards.PLAN_ONLY_OPS`): a now-line spelling would name a
        // drain that is not running and answer nothing, every time.
        //
        // Scout Ahead: "draw 1 card for each LATER Plan carried out with this
        // one" (R267 pick 3, which put back the clause pool pass four removed).
        // The count is the carry-outs that FOLLOW this entry in the same drain,
        // which is `EB-501`'s carry-outs-not-entries reading pointed forwards:
        // first of three draws 2, last draws 0, alone draws 0. NEREID'S
        // ASCENSION ADDS NOTHING TO IT, and that is `EB-655`'s rule rather than
        // a choice here -- the Rare carries out the FIRST entry of a drain and
        // no other, and an entry is never the first when something follows it,
        // so every entry after this one is exactly one carry-out.
        DrawPerPlanAfter,
        // `EB-679`'s WHOLE-DRAIN count, "each Plan carried out this turn, this
        // one included": Scout Ahead briefly took it and R267 pick 3 took it
        // back off. NO CARD SPELLS IT TODAY -- it is kept resolved the way the
        // arm keeps other unrowed clauses, so a sheet can reach for it without
        // a build. Still carry-outs and not entries, so Nereid's adds one.
        DrawPerPlanThisTurn,
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
        // `EB-655`, R266 (pool pass three), reworked by `EB-668`. BATTLE
        // PLAN: "the next Attack you play face-up this turn deals 4 more
        // damage." A RIDER and not a number -- the size is the rule's
        // (<see cref="NextAttackDamagePower.Bonus"/>) -- so the clause carries
        // no amount, exactly as the two riders above carry none. It replaced
        // an `Energy` clause that paid the write back its own cost, which is
        // the shape this pass exists to undo; `EB-668` then made it DAMAGE,
        // because a cost seam cannot tell a face-up play from a write.
        NextAttackDamage,
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
    /// <param name="Dusk">`EB-643`, R265. This Plan is carried out at the END
    /// of the turn it was written on, before the enemies act
    /// (<see cref="ResolveDusk"/>), instead of at the start of her next one.
    /// A property of the WRITING CARD's printed face (`plan_dusk:` on the row)
    /// and not of its clauses, deliberately: Dusk is WHEN the whole line
    /// lands, so a card cannot have one dusk clause and one morning clause any
    /// more than it can be played on two turns -- and <see cref="Kind"/> stays
    /// closed on what a Plan DOES.</param>
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
    public sealed record Entry(CardModel? Source, IReadOnlyList<Planned> Clauses,
                              string? Label = null, bool Dusk = false,
                              string? AimOverride = null)
    {
        /// <summary>What the strip prints for this Plan.
        ///
        /// <paramref name="Label"/> WINS WHERE ONE IS SET, and only a Plan
        /// that HOLDS a card sets one (R236): Crystal Collapse's face means a
        /// different thing every time it is written, so the strip has to say
        /// which card it caught -- "Crystal Collapse: Gorou &#8212; Juuga",
        /// or "Crystal Collapse: nothing" for a turn with no other Companion
        /// in it. Every other Plan is its own card's name, unchanged.
        ///
        /// `EB-643`: A DUSK ENTRY SAYS SO, and it is a prefix on the strip's
        /// line rather than a second badge or a colour. The queue is ONE
        /// queue and two of its entries now land at different moments, so a
        /// player reading the column has to be able to tell which -- and
        /// "Dusk: Breakwater" is the smallest thing that says it. The
        /// carry-out lines that <see cref="Announce"/> builds are unchanged:
        /// by the time one is said the beat has happened, and WHEN it
        /// happened is what the reader just watched.</summary>
        public string Title => Dusk ? "Dusk: " + Named : Named;

        /// <summary>The line without the Dusk mark -- `Title`'s old body,
        /// split out so the prefix above is one word rather than a second
        /// copy of the fallback chain.</summary>
        private string Named =>
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
    /// ABOUT THE MORNING. <see cref="ResolveDusk"/> is not capped -- a Dusk
    /// Plan has waited for nothing -- so under a declared cap a turn could
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
        _summonHits.Clear();
        _tideCharts.Clear();
        // `EB-643`: the cached environment read too, so a test that declares a
        // cap and one that does not cannot see each other's answer.
        _planCap = null;
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
        try
        {
            await volley();
        }
        finally
        {
            var moved = Moved(before, owner);
            var lost = moved?.Sum(row => row.Amount) ?? 0;
            if (moved != null && lost > 0)
            {
                RecordSummon(owner, new CarriedOutPlan(
                    source, lost, SummonLine(source, lost), moved, false,
                    // The word the page prints after the figure, and it is
                    // `NumberKind(Kind.Damage)`'s: what a reader wants to know
                    // is what the number IS, not how it was derived.
                    "damage"));
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
    /// <param name="dusk">`EB-643`, R265. Write this Plan as a DUSK Plan: it
    /// is carried out at the end of the turn it was written on, before the
    /// enemies act (<see cref="ResolveDusk"/>), instead of next morning. The
    /// generated card passes it only where its row declares `plan_dusk:`, so
    /// every card authored before the field existed emits exactly the call it
    /// always did. <see cref="ScheduleFromExhaust"/> never passes it: Moon's
    /// Reflection contributes another card's LINE and not its face, and Dusk
    /// is a fact about the face.</param>
    public static async Task Schedule(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? source,
        IReadOnlyList<Planned> clauses, bool dusk = false)
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
        // partial. `DamageQuarterMaxHp` and `DamagePerCompanionLastTurn` print
        // no flat number for a flat rider to join -- one is read off Max HP and
        // the other is a per-companion RATE, where a flat add would be paid
        // once per body counted -- so there is nothing on those faces the fold
        // could be about. `PlanDamageVar` previews the same call, so the number
        // queued here is the number the face printed.
        for (var i = 0; i < body.Count; i++)
        {
            if (body[i].Kind == Kind.Damage)
            {
                body[i] = body[i] with
                {
                    Amount = Hers(kokomi, source, body[i].Amount),
                };
            }
        }
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
        var entry = new Entry(source, body, label, dusk);
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
        //
        // DUSK ENTRIES CANNOT BE IN THIS QUEUE. <see cref="ResolveDusk"/>
        // drains them at the end of the turn they were written on, so by the
        // next morning the queue holds only entries that waited for one --
        // which is what makes "dusk carry-outs are not counted against the
        // morning cap" true by construction rather than by a filter.
        var cap = PlanCap;
        var due = cap > 0 && queue.Count > cap
            ? new List<Entry>(queue.GetRange(0, cap))
            : new List<Entry>(queue);
        var held = cap > 0 && queue.Count > cap
            ? new List<Entry>(queue.GetRange(cap, queue.Count - cap))
            : null;
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
            due.Count + (CarryOutTimes(kokomi) > 1 ? 1 : 0));
        // The display list is handed over BEFORE the sync, because `Sync`
        // refreshes the strip and the strip reads `Showing`: the badge goes
        // away in the same beat the column stays up, which is the true
        // statement (nothing is pending; four things are happening).
        _showing[player] = new List<Entry>(due);
        await Sync(choiceContext, kokomi, "rule:morning_drain", due.Count);

        try
        {
            await Drain(choiceContext, kokomi, due);
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
        // `EB-679`, SCOUT AHEAD'S COUNT: THE WHOLE DRAIN, itself included,
        // read ONCE before the first clause runs. Order-independence is the
        // point of the redesign -- a reader whose number depends on where in
        // the queue it sits is a card whose value is its position -- so this
        // is computed here rather than per entry, the discipline
        // <see cref="ResolveAll"/> already keeps for <c>PlansThisMorning</c>.
        //
        // ONE EXTRA FOR NEREID'S ASCENSION, the same term `ResolveAll` writes
        // and for the same reason: the Rare carries the FIRST entry of a drain
        // out twice, and every reader in this arm counts CARRY-OUTS
        // (`EB-501`). It deliberately does NOT fold in an extra carry-out a
        // later entry may write -- that rider is not on the board when the
        // number is asked, which is the reading the old per-entry term took.
        var drainPlans = due.Count
                       + (due.Count > 0 && CarryOutTimes(kokomi) > 1 ? 1 : 0);
        for (var index = 0; index < due.Count; index++)
        {
            var entry = due[index];
            // R267 PICK 3, SCOUT AHEAD'S COUNT: the carry-outs still to come
            // after this entry -- ENTRIES AFTER IT, ONE CARRY-OUT EACH, because
            // Nereid's Ascension doubles the FIRST entry of a drain only and
            // this entry is never the first when anything follows it
            // (`EB-655`). It deliberately does NOT fold in an extra carry-out a
            // LATER entry may write: that rider is not on the board when this
            // number is asked. Read PER ENTRY, so a Scout Ahead written first
            // and one written last answer honestly -- the ordering decision the
            // card exists for, which pool pass four had removed.
            var after = due.Count - index - 1;
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
            var times = (index == 0 ? CarryOutTimes(kokomi) : 1)
                      + (extraThis ? 1 : 0);
            for (var i = 0; i < times; i++)
            {
                var (wroteDouble, wroteExtra) = await ResolveEntry(
                    choiceContext, kokomi, entry, doubleDamage: doubleThis,
                    after: after, drainPlans: drainPlans);
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
    /// `EB-643` (R265), DUSK: "the Bake-Kurage carries this Plan out at the
    /// end of this turn, before enemies act."
    ///
    /// THE HOOK IS <c>ProtoBakeKuragePower.BeforeSideTurnEnd</c> on the PLAYER
    /// side, which is the nearest broadcast this mod has to the printed
    /// sentence and the one the sim mirrors (`combat._player_turn`, beside
    /// `klee_overhaul.turn_end`). What the point buys is the whole promise:
    /// the Block is on her before the swing, which is the only clause of the
    /// face a card can tell apart.
    ///
    /// A DUSK CARRY-OUT IS A CARRY-OUT. It goes through
    /// <see cref="ResolveEntry"/> like every other, so Treatise draws on it,
    /// Song of Pearls blocks on it and Sango Isshin's condition is met.
    ///
    /// IT DOES NOT TOUCH `PlansThisMorning`, and that is the one place the two
    /// drains differ on purpose: Tide Wall, Well Laid and Tide Chart all print
    /// "this morning", and an evening is not one.
    ///
    /// NOT CAPPED. <see cref="PlanCap"/> is a rule about the MORNING -- "at
    /// most N Plans a morning, the rest wait" -- and a Dusk Plan has already
    /// waited for nothing.
    ///
    /// THE DUSK ENTRIES LEAVE THE QUEUE AND THE OTHERS STAY, taken before the
    /// first clause runs for <see cref="ResolveAll"/>'s reason: a Dusk Plan
    /// whose body writes another Plan must not carry its own child out on the
    /// same boundary.
    /// </summary>
    public static async Task ResolveDusk(
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
        var due = queue.Where(e => e.Dusk).ToList();
        if (due.Count == 0) return;
        queue.RemoveAll(e => e.Dusk);
        int before = queue.Count + due.Count;
        await Sync(choiceContext, kokomi, "rule:dusk_drain", before);
        try
        {
            await Drain(choiceContext, kokomi, due);
        }
        finally
        {
            Vfx.KokomiPlanStrip.Refresh(kokomi);
        }
    }

    /// <summary>
    /// SECOND THOUGHTS (`EB-643`): "cancel your last Plan: its card returns to
    /// your hand and you regain its cost."
    ///
    /// THE LAST ENTRY AND NOT THE FRONT ONE, which is the whole card:
    /// <see cref="ResolveFront"/> hurries the OLDEST Plan and this takes back
    /// the NEWEST, so the two tempo cards operate on opposite ends of one
    /// queue and a player who has just written the wrong Plan has a way back.
    ///
    /// THE CARD COMES OUT OF THE DISCARD PILE. <see cref="Entry.Source"/> is
    /// the card that wrote the Plan and the discard pile is where a played
    /// card is, on the ordinary path -- so the move is a real pile-to-pile
    /// move of that instance rather than a new copy.
    ///
    /// AND ON THE PATHS THAT ARE NOT ORDINARY, NOTHING RETURNS. A Plan written
    /// by Moon's Reflection off a card in the EXHAUST pile has a source that
    /// is not in the discard pile, and an Exhaust row's own card is not there
    /// either. The Plan is still cancelled and no Energy is paid, because what
    /// the face promises is the card and the card is not there to promise. It
    /// is a printed no-op of the kind this arm already has several of, not a
    /// search of every pile for something that looks similar.
    ///
    /// THE ENERGY IS THE RETURNED CARD'S CURRENT COST, read off the card that
    /// is coming back -- a smithed copy that costs 0 refunds 0, which is what
    /// "its cost" says. AN EMPTY QUEUE IS A PRINTED NO-OP, the shape
    /// <see cref="ResolveFront"/> already has. Sim twin:
    /// `kokomi_plan.cancel_last_plan`.
    /// </summary>
    public static async Task CancelLast(
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
        var last = queue[queue.Count - 1];
        int before = queue.Count;
        queue.RemoveAt(queue.Count - 1);
        await Sync(choiceContext, kokomi, "rule:plan_cancelled", before);

        var card = last.Source;
        var discard = CardPile.Get(PileType.Discard, player);
        if (card == null || discard == null || !discard.Cards.Contains(card))
        {
            return;
        }
        // `CardPileCmd.Add` IS THE MOVE, which is the door <see cref="Replay"/>
        // one method down already takes a card out of the exhaust pile with:
        // the game's own pile command removes it from wherever it is. TOP of
        // the hand, so the card the player just took back is the one they are
        // looking at.
        await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);
        // THE RESOLVED COST, which is the number the player would have to pay
        // to play the card again -- `EnergyCost.GetResolved()` is the game's
        // own read and it is what a mid-combat discount or a smith has already
        // moved. "Its cost" on the face means the cost it has now.
        var cost = card.EnergyCost.GetResolved();
        if (cost > 0) await PlayerCmd.GainEnergy(cost, player);
    }

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
    /// NO CARD COMES BACK, unlike <see cref="CancelLast"/>, and that is the
    /// trade rather than an omission: this cancels a whole queue for a
    /// currency and that one buys a single Plan back at its own price.
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
    private static Task<(bool Double, bool Extra)> ResolveNow(
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
    /// <param name="doubleDamage">`EB-643`. Opening Gambit's rider, spent on
    /// THIS entry by the drain that carried the entry before it out.</param>
    /// <param name="after">R267 pick 3. Scout Ahead's count: the carry-outs
    /// still to come in this drain after this entry. The default is the honest
    /// answer for a drain of one -- nothing follows
    /// (<see cref="ResolveFront"/>).</param>
    /// <param name="drainPlans">`EB-679`. The whole-drain count, this entry
    /// included, which no card spells today. The default is the honest answer
    /// for a drain of one (<see cref="ResolveFront"/>).</param>
    /// <returns>`EB-643`. The riders THIS entry wrote, which the drain spends
    /// on the entry that follows it. They are handed back rather than stored
    /// because the clause that writes one is inside the loop below and the
    /// drain that spends it is outside -- returning them is what keeps "the
    /// next Plan" a fact about a DRAIN rather than a flag on this class that
    /// could outlive one.</returns>
    private static async Task<(bool Double, bool Extra)> ResolveEntry(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry,
        bool onPlay = false, bool doubleDamage = false, int after = 0,
        int drainPlans = 1)
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
                // `EB-643`. THE RIDERS ARE NOTED HERE AND NOWHERE ELSE, before
                // the switch, because they do nothing when they resolve: what
                // they do is tell the drain about the entry that follows.
                if (clause.Kind == Kind.NextPlanDoubleDamage) wroteDouble = true;
                if (clause.Kind == Kind.NextPlanExtraCarryOut) wroteExtra = true;
                var wanted = AskedFor(kokomi, clause, after, drainPlans);
                var produced = await ResolveOne(choiceContext, kokomi, clause,
                                                entry, doubleDamage,
                                                after, drainPlans);
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
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan,
        Entry? entry = null, bool doubleDamage = false, int after = 0,
        int drainPlans = 1)
    {
        var player = kokomi.Player;
        if (player == null) return null;

        switch (plan.Kind)
        {
            case Kind.DrawPerPlanAfter:
            {
                // SCOUT AHEAD (R267 pick 3): "draw 1 card for each later Plan
                // carried out with this one." <paramref name="after"/> is the
                // drain's count -- see <see cref="Drain"/>, which reads it PER
                // ENTRY -- and the printed amount is the RATE, the shape Tide
                // Wall's clause already has. Change of Plans carries ONE entry
                // out, so a Scout Ahead hurried that way draws nothing: nothing
                // follows it, which is the face read literally.
                var cards = plan.Amount * after;
                if (cards > 0)
                {
                    await CardPileCmd.Draw(choiceContext, cards, player);
                }
                return cards;
            }
            case Kind.DrawPerPlanThisTurn:
            {
                // `EB-679`'s WHOLE-DRAIN count, on no card since R267 pick 3.
                // <paramref name="drainPlans"/> is read once for the drain --
                // see <see cref="Drain"/> -- and the printed amount is the
                // RATE. Change of Plans carries ONE entry out and pays 1.
                var cards = plan.Amount * drainPlans;
                if (cards > 0)
                {
                    await CardPileCmd.Draw(choiceContext, cards, player);
                }
                return cards;
            }

            case Kind.NextPlanDoubleDamage:
            case Kind.NextPlanExtraCarryOut:
                // THE RIDERS DO NOTHING HERE, and that is the whole of them:
                // <see cref="ResolveEntry"/> noted the clause before the switch
                // and <see cref="Drain"/> spends it on the entry that follows.
                // No number, so the beat says the card's name alone -- which is
                // the honest line for a Plan whose effect is on the NEXT one.
                return null;

            case Kind.NextAttackDamage:
                // `EB-668`. BATTLE PLAN's rider, applied here and read at the
                // damage seam. No number on the beat: the size is the rule's
                // and the line the player wants is "Battle Plan happened", the
                // same shape the two riders above take.
                await KokomiOverhaulKit.NextAttackDamage(
                    choiceContext, kokomi, null);
                return null;

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

            case Kind.BlockPerPlanHeld:
                // BREAKWATER (`EB-685`). POWERED, the flat planned Block's
                // funnel exactly and for the reason Tide Wall's branch above
                // states. The count is the QUEUE AS IT STANDS RIGHT NOW --
                // <see cref="PlansHeld"/>, read live rather than once at the
                // drain -- and <see cref="Kind.BlockPerPlanHeld"/> carries the
                // whole argument for why. An empty queue pays nothing, a
                // printed no-op: a Breakwater with no Plan standing behind it
                // is the base alone.
                return (int)await CreatureCmd.GainBlock(
                    kokomi, plan.Amount * PlansHeld(kokomi),
                    ValueProp.Move, null);

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

            case Kind.DamagePerCompanionLastTurn:
                // Chain of Command. "Last turn" is read at CARRY-OUT: the Plan
                // was written on turn N and resolves at the top of N+1, and the
                // ledger has rolled by then, so the count it holds is turn N's
                // -- the turn the player was looking at when they wrote it.
                return await Hit(choiceContext, kokomi, plan,
                                 plan.Amount * KokomiOverhaulLedger.For(kokomi)
                                                   .CompanionsPlayedLastTurn,
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
        Kind.Block or Kind.BlockPerPlanThisMorning
            or Kind.BlockPerPlanHeld => "Block",
        Kind.Mend => "HP healed",
        Kind.Damage or Kind.DamageQuarterMaxHp
            or Kind.DamagePerCompanionLastTurn => "damage",
        Kind.ApplyWeak => "Weak",
        Kind.ApplyVulnerable => "Vulnerable",
        // `EB-643`. Scout Ahead's figure is cards, the same word Draw's is:
        // the reader is asking what the number IS and not how it was derived,
        // which is the argument the three damage kinds above make. The two
        // riders produce no number at all and fall to the default.
        Kind.DrawPerPlanAfter or Kind.DrawPerPlanThisTurn => "cards drawn",
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
                                 int after = 0,
                                 int drainPlans = 1) => plan.Kind
        switch
    {
        // `EB-643`. A FOURTH SCALED KIND, and it reads the DRAIN rather than a
        // ledger -- which is why `after` and `drainPlans` are parameters here
        // and the other three are computed from state: nothing on the board
        // says how many Plans are still to come or how deep the drain around
        // this entry is, so the drain is the only thing that knows.
        Kind.DrawPerPlanAfter => plan.Amount * after,
        Kind.DrawPerPlanThisTurn => plan.Amount * drainPlans,
        Kind.BlockPerPlanThisMorning =>
            plan.Amount * KokomiOverhaulLedger.For(kokomi).PlansThisMorning,
        // `EB-685`. A FIFTH SCALED KIND, and it reads the QUEUE rather than a
        // ledger -- asked here BEFORE the clause runs, which for this one is
        // the same moment the clause itself asks: `ResolveDusk` has already
        // emptied the dusk entries out, and nothing between here and the
        // `GainBlock` touches the queue.
        Kind.BlockPerPlanHeld => plan.Amount * PlansHeld(kokomi),
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
        var times = plan.Times < 1 ? 1 : plan.Times;
        int? first = null;
        for (var pass = 0; pass < times; pass++)
        {
            foreach (var target in Aimed(kokomi, plan, entry))
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
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, badge, count - badge.Amount, applier: kokomi,
            cardSource: null, silent: true);
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
    /// `EB-599` TOOK THIS OFF THE FACE and left it here. It is a fact about
    /// the body the hit finds NEXT MORNING, and the r22 lane-2 seat paid for
    /// a "Plan: Deal 10" that arrived as 7 once the Vulnerable it was folding
    /// had expired. So the line previews <see cref="Hers"/> and this stays
    /// what the morning does -- the pins below are its readers.
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
    /// Sim twin: `kokomi_plan.hers`.
    /// </summary>
    public static int Hers(Creature? kokomi, CardModel? source, int amount)
    {
        var folded = Enchanted(source, amount);
        if (folded <= 0 || kokomi == null) return folded;
        return folded
             + (int)(kokomi.Powers.OfType<StrengthPower>()
                           .FirstOrDefault()?.Amount ?? 0);
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
    /// `EB-599` TOOK THE TARGET'S SIDE OFF THIS LINE AND PUT HERS ON. It used
    /// to fold the FRONT enemy's <see cref="PlannedDamage"/>, and the r22
    /// lane-2 seat paid for a "Plan: Deal 10" that the morning carried out as
    /// 7 once that Vulnerable had expired -- "for a mechanic sold on
    /// committing a turn early, the committed number moving is the sharpest
    /// contradiction in the kit". A Plan resolves against whatever the target
    /// wears NEXT MORNING, which is a thing no line written today knows; her
    /// Strength and this copy's enchantment are things it does know, and
    /// <see cref="Hers"/> folds both into the number that is queued, so the
    /// face and the queue print one number (`EB-265`'s rule).
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
            // `EB-580`: THE ENCHANTMENT FIRST, AND WITHOUT A BOARD. It is a
            // fact about THIS COPY of the card rather than about the fight, so
            // it folds on a reward screen and in a deck view as well -- which
            // is where the r21 seat was reading the two lines against each
            // other.
            PreviewValue = Enchanted(card, (int)BaseValue);
            var kokomi = card.Owner?.Creature;
            if (!KokomiOverhaul.LiveFor(kokomi)) return;
            // `EB-599`: AND HER STRENGTH, WHICH NEEDS THE CREATURE. Nothing of
            // the TARGET's is folded here any more: the Plan lands next
            // morning, against whatever that body wears then, and the r22
            // lane-2 seat paid for a "Plan: Deal 10" that arrived as 7 once
            // the Vulnerable the line was folding had expired.
            PreviewValue = Hers(kokomi, card, (int)BaseValue);
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
            // `EB-680`: AND WHICH TURN'S END. A Dusk Plan lands at the end
            // of the turn it is written on (R265), and this badge counted it
            // into "the start of your next turn" with the rest -- the second
            // of the three timings one Dusk Plan printed at once. 115 of 125.
            "Carries out [blue]{Amount}[/blue] "
          + "[gold]Plan{Amount:plural:|s}[/gold] in order next turn; a "
          + "[gold]Dusk[/gold] Plan at this turn's end. "
          // `EB-647` (round 23). THE NUMBER IS FIXED WHEN THE PLAN IS
          // WRITTEN. Three r23 lanes met it from the wrong side: under Shrink
          // the hand reprinted `Kurage's Oath` as 2 and the jellyfish carried
          // it out for 7, which is `Hers` working exactly as ruled -- her
          // Strength and her enchantment fold at WRITING time and nothing
          // that lands on her afterwards follows. Nothing printed it. It goes
          // on THIS badge rather than the `Plan` keyword tip, which is at its
          // 135-character ceiling (`ArmKeywordTips.ForPlan`), and rather than
          // `ProtoBakeKuragePower`'s description, which stands at 122 of the
          // power surface's 125. Page twin:
          // `blindplay_notes.PLAN_WRITTEN_NUMBER_NOTE`.
          + "Later debuffs do not change what you wrote."
          // `EB-653` (round 24). AND THE CAP, WHERE IT BINDS. Empty on an
          // unconfigured build, which is every build but a cap lane's; the
          // sentence is `KokomiPlan.CapSentence`'s, spelled once for both
          // badges.
          + KokomiPlan.CapSentence),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
