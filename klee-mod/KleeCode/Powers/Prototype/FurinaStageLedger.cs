using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>Why a performer left the stage. Only one of the three earns a bow.
/// </summary>
public enum StageDeparture
{
    /// <summary>Rotated off the front to make room (rule 3). No bow: a bow is
    /// earned by Spend alone (sec.10 default 5).</summary>
    Rotated,

    /// <summary>Emptied by a hit (rule 7, first clause). No bow.</summary>
    Struck,

    /// <summary>Emptied by Spend (rule 7, second clause). Bows (rule 9).
    /// </summary>
    Spent,
}

/// <summary>One performer leaving, and how. The <c>Bows</c> read is the rule
/// rather than a field, so no caller can record a departure and then decide
/// for itself whether a bow was earned.</summary>
public readonly struct StageExit
{
    public StageExit(StagePerformer who, StageDeparture cause)
    {
        Who = who;
        Cause = cause;
    }

    public StagePerformer Who { get; }

    public StageDeparture Cause { get; }

    public bool Bows => Cause == StageDeparture.Spent;
}

/// <summary>What a Spend did. <see cref="Fired"/> is the rider's own question
/// -- rule 8 says a rider fires IN FULL whenever anybody is on stage, however
/// little they can pay, and cannot fire at all on an empty one.</summary>
public readonly struct StageSpend
{
    public StageSpend(bool fired, int paid, StageExit? exit)
    {
        Fired = fired;
        Paid = paid;
        Exit = exit;
    }

    public bool Fired { get; }

    /// <summary>What the lead actually had. Never more than the ask, often
    /// less, and never the reason the rider does or does not fire.</summary>
    public int Paid { get; }

    public StageExit? Exit { get; }
}

/// <summary>What one attack's post-Block remainder did to the stage.</summary>
public readonly struct StageAbsorb
{
    public StageAbsorb(int absorbed, int reachedFurina, StageExit? exit)
    {
        Absorbed = absorbed;
        ReachedFurina = reachedFurina;
        Exit = exit;
    }

    public int Absorbed { get; }

    public int ReachedFurina { get; }

    public StageExit? Exit { get; }
}

/// <summary>What a summon did: who arrived, and who rotated off to make room.
/// </summary>
public readonly struct StageSummon
{
    public StageSummon(StagePerformer arrived, int atFanfare, StageExit? exit)
    {
        Arrived = arrived;
        AtFanfare = atFanfare;
        Exit = exit;
    }

    public StagePerformer Arrived { get; }

    /// <summary>The bar the newcomer took the back seat with -- normally
    /// <see cref="FurinaStageLaw.SummonFanfare"/>, and the LEAVER'S bar on a
    /// rotation (rule 3, "pools are never lost to rotation").</summary>
    public int AtFanfare { get; }

    public StageExit? Exit { get; }
}

/// <summary>A seat and the performer standing in it. Mutable because the bar
/// moves every turn; the LIST is what carries the seat order.</summary>
public sealed class StageSeat
{
    internal StageSeat(StagePerformer who, int fanfare)
    {
        Who = who;
        Fanfare = fanfare;
    }

    public StagePerformer Who { get; }

    /// <summary>The bar. No cap (rule 4); zero means the performer is leaving
    /// and the ledger removes it in the same call.</summary>
    public int Fanfare { get; internal set; }

    /// <summary>
    /// THE BODY THIS SEAT IS WEARING, or null until
    /// <c>FurinaStagePets.Sync</c> has fielded one -- which is always, in a
    /// headless pin.
    ///
    /// ON THE SEAT AND NOT LOOKED UP BY KIND, because duplicates are legal:
    /// two Crabalettas may stand on the stage at once (the summon Commons name
    /// their performer and nothing forbids naming one twice, exactly as the
    /// shipped <i>Grand Gala</i> deploys Crabaletta twice one arm over). A
    /// reconciler that matched a pet to a seat by MODEL TYPE would hand the
    /// front seat's bar to the back seat's body on the turn one of them left.
    /// </summary>
    public Creature? Pet { get; internal set; }
}

/// <summary>
/// THE STAGE ITSELF: three seats, front first, and every rule in brief sec.3
/// that is arithmetic rather than an engine command.
///
/// WHY THE RULES LIVE HERE AND NOT ON THE PET. The performers ARE pets and
/// their bars ARE the pets' HP bars on screen -- but a pet is a
/// <c>Creature</c> in a live <c>CombatState</c>, and <c>KleeTests</c> runs
/// with no combat, no scene tree and no <c>PlayerChoiceContext</c>
/// (KleeTests/README.md, "the headless boundary"). A rule written against the
/// pet would have been a rule no pin could ask a question of, and this arm's
/// whole acceptance is questions about rules: does a 12 through Block 6 kill a
/// 3-bar lead and land 3 on her, does a 3x2 flurry leave her whole, does a
/// Spend 3 from a 1-bar lead fire in full.
///
/// SO THE LEDGER IS CANONICAL AND THE PET MIRRORS IT.
/// <see cref="FurinaStagePets"/> pushes each seat's <see cref="StageSeat.Fanfare"/>
/// onto its pet as max-and-current HP after every change. That is safe rather
/// than merely convenient, and by construction: enemies cannot target a pet at
/// all (<c>MonsterModel.PerformMove</c> is handed
/// <c>CombatState.PlayerCreatures</c>, which is <c>Where(c =&gt; c.IsPlayer)</c>,
/// and a pet has no <c>Player</c> -- the finding written out in
/// <c>BakeKuragePet</c>), so nothing in the game can move a performer's HP
/// behind the ledger's back. Every point a performer loses comes through
/// <see cref="Absorb"/> or <see cref="Spend"/>.
///
/// PER FURINA AND PER COMBAT, keyed the way <c>FurinaReframeLedger</c>,
/// <c>KleeOverhaulLedger</c> and <c>KokomiOverhaulLedger</c> are keyed and for
/// their reason (R205): in co-op the other seat's stage is not hers, and pets
/// live one combat (rule 1), so a table that outlived the combat would field a
/// stage the fight never summoned.
/// </summary>
public sealed class FurinaStageLedger
{
    private static object? _combat;

    private static readonly Dictionary<Creature, FurinaStageLedger> _byFurina =
        new();

    private readonly List<StageSeat> _seats = new();

    /// <summary>This Furina's stage for this combat, created on first ask.
    /// </summary>
    public static FurinaStageLedger For(Creature furina)
    {
        var combat = (object?)furina.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byFurina.Clear();
        }
        if (!_byFurina.TryGetValue(furina, out var ledger))
        {
            ledger = new FurinaStageLedger();
            _byFurina[furina] = ledger;
        }
        return ledger;
    }

    /// <summary>Test seam: forget every stage. The mod never calls it -- the
    /// combat-identity check above is what clears a real run.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byFurina.Clear();
    }

    /// <summary>The stage, FRONT FIRST. The head of the list is the lead, and
    /// that is the whole of the seat order: rule 6 reads
    /// <c>[0]</c>, rule 5 reads the last, and rule 3 moves the head off and
    /// appends. A second field naming the front is a second source of truth
    /// for a fact the list already carries (`EB-506`, one arm over).</summary>
    public IReadOnlyList<StageSeat> Seats => _seats;

    /// <summary>The front performer: the one that absorbs (rule 6), the one
    /// that Spend pays from (rule 8) and the one that regenerates (rule 4).
    /// </summary>
    public StageSeat? Lead => _seats.Count > 0 ? _seats[0] : null;

    /// <summary>The back-most performer, which is the LEAD when it is alone
    /// (rule 5's second sentence).</summary>
    public StageSeat? Back => _seats.Count > 0 ? _seats[^1] : null;

    public bool IsEmpty => _seats.Count == 0;

    public bool IsFull => _seats.Count >= FurinaStageLaw.SeatCount;

    /// <summary>Every performer on stage, front to back. What the acts walk
    /// (rule 10, "from any seat") and what the strip draws.</summary>
    public IEnumerable<StagePerformer> Company => _seats.Select(s => s.Who);

    /// <summary>
    /// RULE 3. A summon fills the back-most empty seat at
    /// <see cref="FurinaStageLaw.SummonFanfare"/>; on a FULL stage the front
    /// performer leaves without a bow, the other two step forward and the
    /// newcomer takes the back seat WITH THE LEAVER'S FANFARE.
    ///
    /// THE POOL IS NOT LOST, which is the clause that makes rotation a play
    /// and not a punishment: a three-seat stage carrying 8 on the front hands
    /// that 8 to whoever arrives. The bar moves, the performer does not.
    ///
    /// THE NEWCOMER PERFORMS THE SAME TURN and there is no code for it, which
    /// is the point: the acts fire at the END of her turn over whoever is on
    /// stage then (rule 10), so a performer summoned during the turn is
    /// standing there when they fire. Pinned rather than commented, because
    /// "the rule needs no code" and "the rule is missing" look identical.
    /// </summary>
    public StageSummon Summon(StagePerformer who)
    {
        if (!IsFull)
        {
            _seats.Add(new StageSeat(who, FurinaStageLaw.SummonFanfare));
            return new StageSummon(who, FurinaStageLaw.SummonFanfare, null);
        }

        var leaver = _seats[0];
        _seats.RemoveAt(0);
        _seats.Add(new StageSeat(who, leaver.Fanfare));
        return new StageSummon(
            who, leaver.Fanfare,
            new StageExit(leaver.Who, StageDeparture.Rotated));
    }

    /// <summary>
    /// RULE 5. "Raise N Fanfare on the back performer" -- the back-most, which
    /// is the lead when it is alone. Returns what it raised, which is 0 on an
    /// empty stage and N otherwise: bars have no cap (rule 4), so a Raise
    /// never lands short.
    ///
    /// THE BACK AND NOT THE LEAD, and it is a lever rather than a detail:
    /// sec.8's second failure mode is the cast becoming a second life bar, and
    /// Refill landing at the back is what stops a Defend-priced Refill topping
    /// up the buffer that is currently eating the hits.
    /// </summary>
    public int Raise(int amount)
    {
        if (amount <= 0 || Back is not { } seat) return 0;
        seat.Fanfare += amount;
        return amount;
    }

    /// <summary>
    /// RULE 8. Spend N pays from the LEAD. Three clauses, and the second is
    /// the one that surprises:
    ///
    ///   * enough on the bar: pays N, the rider fires, the performer stays;
    ///   * NOT enough: THE RIDER STILL FIRES IN FULL, the lead pays what it
    ///     has, and it leaves with a BOW (rule 7 second clause, rule 9).
    ///     `Paid` is what it had, and no caller may price the rider off it --
    ///     that is sec.10 default 4, "as [USER] said";
    ///   * empty stage: the rider CANNOT fire, and the card plays at its base
    ///     number. Not a refusal and not a whiff: the card is fine, the rider
    ///     is not there.
    ///
    /// A lead emptied EXACTLY by a Spend that it could afford still bows: it
    /// was emptied by Spend, which is the whole of rule 7's test.
    /// </summary>
    public StageSpend Spend(int amount)
    {
        if (Lead is not { } lead) return new StageSpend(false, 0, null);
        if (amount <= 0) return new StageSpend(true, 0, null);

        var paid = lead.Fanfare < amount ? lead.Fanfare : amount;
        lead.Fanfare -= paid;
        if (lead.Fanfare > 0) return new StageSpend(true, paid, null);

        _seats.RemoveAt(0);
        return new StageSpend(
            true, paid, new StageExit(lead.Who, StageDeparture.Spent));
    }

    /// <summary>
    /// RULE 6, the middle term of the damage order: Furina's Block, then the
    /// LEAD's bar, then Furina.
    ///
    /// PER ATTACK, AND IT NEVER RUNS ON. The lead absorbs what one attack put
    /// through her Block, up to its bar, and the remainder reaches HER -- not
    /// the middle seat. That is what makes the two intents different plays: a
    /// big single hit rips through the lead and lands on her, a flurry is
    /// resolved hit by hit and can kill the lead while leaving her whole.
    /// Nothing in this method loops, and that absence is the rule.
    ///
    /// A LEAD EMPTIED HERE TAKES NO BOW (rule 7, first clause). The bow is
    /// bought with a Spend; a performer that merely died did not buy one.
    ///
    /// SYNCHRONOUS ON PURPOSE. Its caller is
    /// <c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c>, which the engine
    /// calls per damage instance and which returns a number rather than
    /// awaiting one. The pet's own HP bar and the departure's teardown are
    /// flushed a hook later, in <c>AfterDamageReceived</c>, exactly as
    /// <c>FlushFanfareDeltaBlock</c> already defers the shipped kit's Block.
    /// </summary>
    public StageAbsorb Absorb(int incoming)
    {
        if (incoming <= 0 || Lead is not { } lead)
        {
            return new StageAbsorb(0, incoming < 0 ? 0 : incoming, null);
        }

        var absorbed = lead.Fanfare < incoming ? lead.Fanfare : incoming;
        lead.Fanfare -= absorbed;
        var reached = incoming - absorbed;
        if (lead.Fanfare > 0) return new StageAbsorb(absorbed, reached, null);

        _seats.RemoveAt(0);
        return new StageAbsorb(
            absorbed, reached,
            new StageExit(lead.Who, StageDeparture.Struck));
    }

    /// <summary>
    /// RULE 4. The LEAD regains <see cref="FurinaStageLaw.LeadRegen"/> at the
    /// start of Furina's turn, from her SECOND turn on. Only the lead; bars
    /// have no cap.
    ///
    /// THE TURN NUMBER IS THE ARGUMENT rather than a counter of its own, for
    /// <c>FurinaReframeOpening</c>'s reason one arm over: the seat's
    /// <c>PlayerCombatState.TurnNumber</c> is per-PLAYER, so a co-op partner's
    /// turn cannot pay hers, and an extra first turn cannot pay twice.
    ///
    /// WHY NOT TURN ONE. The relic opens the fight with Usher at
    /// <see cref="FurinaStageLaw.OpeningFanfare"/> (rule 2). A regen on turn
    /// one would make that opening a 4 the relic never printed.
    /// </summary>
    public int Regen(int turnNumber)
    {
        if (turnNumber < FurinaStageLaw.RegenFromTurn) return 0;
        if (Lead is not { } lead) return 0;
        lead.Fanfare += FurinaStageLaw.LeadRegen;
        return FurinaStageLaw.LeadRegen;
    }

    /// <summary>
    /// The relic's opening (rule 2), and the ONE entry that is not a summon:
    /// Usher takes the FRONT seat at <see cref="FurinaStageLaw.OpeningFanfare"/>
    /// rather than the back-most empty one at 1. It is idempotent on a
    /// non-empty stage, so a relic and a kit install that both make the
    /// sentence true cost one list check between them -- the belt
    /// <c>TamakushiCasket</c> wears for the same reason.
    /// </summary>
    public StageSeat? OpenWith(StagePerformer who)
    {
        if (!IsEmpty) return null;
        var seat = new StageSeat(who, FurinaStageLaw.OpeningFanfare);
        _seats.Add(seat);
        return seat;
    }

    /// <summary>Test and teardown seam: the stage is empty at the end of a
    /// combat because pets live one combat (rule 1). The combat-identity check
    /// in <see cref="For"/> is what does this in a real run.</summary>
    public void Clear() => _seats.Clear();
}
