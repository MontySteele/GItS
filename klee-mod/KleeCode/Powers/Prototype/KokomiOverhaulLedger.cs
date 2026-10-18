using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S MEMORY: the facts a rule asks about that no game object holds.
///
/// DRAFT 6 LEFT IT WITH THREE. Draft 2's ledger carried the pulse's per-combat
/// budget, the did-she-Surge latch, the Surge total for the current play and
/// the enemy count at play start; the ruled brief's sec.6 cuts every rule that
/// read them, so they are gone rather than kept "in case".
///
/// PER COMBAT
///   * <see cref="EntryHp"/> -- the Mend rule: "never above the HP you entered
///     the fight with". Captured once, at combat start, and never moved by
///     anything inside the fight.
///
/// PER TURN
///   * <see cref="CompanionsPlayedThisTurn"/> -- Chain of Command's own
///     now-line ("deal 3 damage for each Companion card you played THIS
///     turn"), written by <c>ProtoBakeKuragePower.AfterCardPlayed</c> (rule 1
///     guarantees that marker is on her every turn of every combat --
///     `EB-362`: it used to be written by The General's Banner's play hook
///     alone, a card she may never draw, so the count read a permanent zero
///     on most boards).
///   * the ONCE-PER-TURN latches (<see cref="ClaimOncePerTurn"/>) -- Treatise,
///     Song of Pearls and The General's Banner, capped at one payout a turn
///     each by [USER]'s live 2026-09-02 verdict.
///   * <see cref="PlanCarriedOutThisTurn"/> -- Sango Isshin's condition.
///   * <see cref="PlansThisMorning"/> -- Tide Wall's multiplier (`EB-335`):
///     how many Plans this morning's drain held, written once by
///     <c>KokomiPlan.ResolveAll</c> before the first clause runs.
///
/// PER COMBAT, AGAIN: <see cref="PlansWrittenThisCombat"/> and
/// <see cref="PlansCarriedOutThisCombat"/> (Sango Isshin and telemetry), and
/// since the jellyfish build (2026-10-12) the Stings played (All Streams Flow
/// to the Sea; per turn for The Shape of Water), made and written. The
/// Tamakushi Casket's count left with the Casket (the re-founding,
/// 2026-10-12).
///
/// PER PLAYER, keyed the way <c>KleeOverhaulLedger</c> is keyed and for the
/// same reason (R205): in co-op the other seat's turn is not hers.
///
/// THE TURN ROLLS ON READ, not on a hook -- the same arrangement
/// <c>KleeOverhaulLedger</c> makes, and here it is belt rather than braces: the
/// marker power IS guaranteed to be on her (rule 1), so a hook would work too.
/// It is done this way anyway so that a rule read from a card body, a power and
/// a relic can never see three different turns.
///
/// NOT A LEAK: the whole table is dropped when the combat instance changes, so
/// it holds at most the current combat's seats.
///
/// PUBLIC, for the reason <c>Diagnostics.MeterLedger</c> gives: KleeTests is a
/// separate assembly and these numbers are what the Mend cap and the Commander
/// loop read.
/// </summary>
public sealed class KokomiOverhaulLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, KokomiOverhaulLedger> _byKokomi = new();

    /// <summary>This Kokomi's ledger for this combat, rolled to this round and
    /// created on first ask. Creation CAPTURES HER ENTRY HP, so a ledger that
    /// was never explicitly opened still caps her Mends at something honest
    /// rather than at zero.</summary>
    public static KokomiOverhaulLedger For(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byKokomi.Clear();
        }
        if (!_byKokomi.TryGetValue(kokomi, out var ledger))
        {
            ledger = new KokomiOverhaulLedger { EntryHp = (int)kokomi.CurrentHp };
            _byKokomi[kokomi] = ledger;
        }
        ledger.RollTo(kokomi.CombatState?.RoundNumber ?? 0);
        return ledger;
    }

    /// <summary>This Kokomi's ledger for her CURRENT combat, or null when
    /// none exists yet. A read for telemetry: it creates nothing and rolls
    /// nothing (rule 1).</summary>
    public static KokomiOverhaulLedger? Peek(Creature kokomi)
    {
        if (!ReferenceEquals(_combat, (object?)kokomi.CombatState)) return null;
        return _byKokomi.TryGetValue(kokomi, out var ledger) ? ledger : null;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byKokomi.Clear();
    }

    /// <summary>
    /// The combat opens: capture her entry HP FROM HERE rather than from the
    /// lazy creation above, so the number is the one she walked in with even
    /// when the first read happens after she has taken a hit.
    /// </summary>
    public static void OpenCombat(Creature kokomi)
    {
        For(kokomi).EntryHp = (int)kokomi.CurrentHp;
    }

    /// <summary>The HP she walked in with. Every Mend's ceiling.</summary>
    public int EntryHp { get; private set; }

    /// <summary>Companion cards played this turn.</summary>
    public int CompanionsPlayedThisTurn { get; private set; }

    /// <summary>
    /// THE ONCE-PER-TURN LATCHES, one set shared by every payoff that has one
    /// ([USER], live 2026-09-02). Keyed by the claiming power's own name.
    /// </summary>
    private readonly HashSet<string> _claimed = new();

    /// <summary>
    /// Has the Bake-Kurage carried out a Plan this turn? Sango Isshin's
    /// condition, and it is a per-turn FACT rather than a latch: reading it
    /// spends nothing.
    ///
    /// Written by <see cref="NotePlanCarriedOut"/> from
    /// <c>KokomiPlan.ResolveEntry</c>, the one place a Plan is carried out --
    /// so the morning queue, Change of Plans' early resolution and The Moon
    /// Overlooks the Waters' play-time one all count. All three carry a Plan
    /// out, which is the phrase the card prints.
    /// </summary>
    public bool PlanCarriedOutThisTurn { get; private set; }

    /// <summary>
    /// HOW MANY PLANS THIS MORNING'S DRAIN HELD (`EB-335`) -- Tide Wall's "for
    /// each Plan the Bake-Kurage carries out this morning".
    ///
    /// THE WHOLE MORNING'S DEPTH, taken once at the top of the drain rather
    /// than counted up as it goes, so a Tide Wall written first, second or last
    /// in the queue pays the same number; a count that grew would make one
    /// card's Block depend on the order the player happened to write in. Zero
    /// on a turn whose morning drained nothing, which is what the card's own
    /// printed no-op says.
    /// </summary>
    public int PlansThisMorning { get; private set; }

    /// <summary>The Kokomi whole-run round (2026-10-10): Plans written and
    /// carried out THIS COMBAT. Telemetry reads both; since [USER]'s run
    /// (2026-10-11) Sango Isshin reads the carried-out count too (sim twin:
    /// <c>CombatState.kk_plans_carried_out_this_combat</c>). Never rolled; a
    /// new combat is a new ledger. A Plan carried out twice counts twice.
    /// (The per-turn counts Feint and Shoal of Spears read left with the
    /// re-founding, 2026-10-12: both read the Plans waiting.)</summary>
    public int PlansWrittenThisCombat { get; private set; }

    /// <inheritdoc cref="PlansWrittenThisCombat"/>
    public int PlansCarriedOutThisCombat { get; private set; }

    /// <summary>One Plan written onto the Bake-Kurage.</summary>
    public void NotePlanWritten()
    {
        PlansWrittenThisCombat++;
    }

    /// <summary>
    /// THE JELLYFISH BUILD (2026-10-12): Stings PLAYED -- face-up, the
    /// now-line -- this combat (All Streams Flow to the Sea) and this turn
    /// (The Shape of Water). A write is not a play and neither is a
    /// carry-out: Treatise's reading. Written by
    /// <c>ProtoBakeKuragePower.AfterCardPlayed</c>, the marker every board
    /// has. Sim twins: <c>CombatState.kk_stings_played_this_combat</c> /
    /// <c>kk_stings_played_this_turn</c>.
    /// </summary>
    public int StingsPlayedThisCombat { get; private set; }

    /// <inheritdoc cref="StingsPlayedThisCombat"/>
    public int StingsPlayedThisTurn { get; private set; }

    /// <summary>Telemetry (the jellyfish paper's first check line): Stings
    /// made and Stings written this combat. Lost Stings are counted on the
    /// fight record (<c>PlayTelemetry.EtherealLost</c>).</summary>
    public int StingsMadeThisCombat { get; private set; }

    /// <inheritdoc cref="StingsMadeThisCombat"/>
    public int StingsWrittenThisCombat { get; private set; }

    /// <summary>One Sting played face-up.</summary>
    public void NoteStingPlayed()
    {
        StingsPlayedThisCombat++;
        StingsPlayedThisTurn++;
    }

    /// <summary><paramref name="made"/> Stings added to her hand.</summary>
    public void NoteStingsMade(int made) => StingsMadeThisCombat += made;

    /// <summary>One Sting written as a Plan.</summary>
    public void NoteStingWritten() => StingsWrittenThisCombat++;

    /// <summary>THE EXPANSION, BATCH ONE: All Streams Flow to the Sea's
    /// pending gift for the next Plan written this turn (null when none is
    /// pending). Per turn; <see cref="RollTo"/> clears it. Sim twin:
    /// `state.kk_next_plan_extra`.</summary>
    public int? NextPlanExtra { get; set; }

    private int _round = -1;

    /// <summary>
    /// The last Companion card she played this COMBAT, or null (R236; combat-
    /// wide since the Kokomi level pass, 2026-10-12: "Play a copy of the last
    /// Companion card you played").
    ///
    /// Crystal Collapse's whole reading, and it is a CARD rather than a count
    /// because the Plan plays a copy of it. Written by
    /// <c>ProtoBakeKuragePower.AfterCardPlayed</c> -- the marker power rule 1
    /// guarantees is on her -- rather than by The General's Banner's hook
    /// beside the counter above, because the Banner is a card she may not
    /// have and a memory that only exists while a Power is out is a memory
    /// that reads null on most boards.
    ///
    /// CRYSTAL COLLAPSE IS NEVER RECORDED (<see cref="NoteCompanionCard"/>):
    /// a copy of it would only write the same Plan again, so its own plays
    /// leave the last Companion where it was.
    /// </summary>
    public CardModel? LastCompanionPlayed { get; private set; }

    /// <summary>One Companion play finished.</summary>
    public void NoteCompanionPlayed() => CompanionsPlayedThisTurn++;

    /// <summary>One Companion play finished, and this is the card. Separate
    /// from the counter above because the two have different writers: the
    /// counter is The General's Banner's hook and this is the marker
    /// power's.</summary>
    public void NoteCompanionCard(CardModel card)
    {
        if (card is global::KleeMod.Cards.Prototype.Generated
                .ProtoMiGorouCrystalCollapse) return;
        LastCompanionPlayed = card;
    }

    /// <summary>
    /// THE ONE ONCE-PER-TURN GATE, and the three powers that cap a payoff at a
    /// turn all call it: true the FIRST time <paramref name="key"/> is claimed
    /// in a round and false for the rest of that round.
    ///
    /// [USER], live 2026-09-02, on the shape all three had: "Treatise looks
    /// too good (one draw per turn if a Plan fired might be ok; one draw per
    /// Plan is too abuseable)", "Likewise" of Song of Pearls, and "The
    /// General's Banner applies a LOT of Weak. Probably too strong."
    ///
    /// ON THE LEDGER RATHER THAN ON EACH POWER, because the ledger is the one
    /// thing in this arm that knows what turn it is: <see cref="For"/> ROLLS
    /// ON READ, so a latch clears itself at the first ask of a new round no
    /// matter which broadcast asks first. Nothing has to remember to clear it,
    /// and the three cannot drift apart into three answers about when a turn
    /// began.
    ///
    /// IT IS A CLAIM AND NOT A QUESTION: the caller that gets `true` has taken
    /// the turn's payout, so the read and the write cannot be separated by an
    /// `await` that another listener could slip through.
    /// </summary>
    public static bool ClaimOncePerTurn(Creature? kokomi, string key)
    {
        if (kokomi == null) return false;
        return For(kokomi).Claim(key);
    }

    /// <summary>One Plan carried out: the per-turn fact and the per-combat
    /// count Sango Isshin reads.</summary>
    public void NotePlanCarriedOut()
    {
        PlanCarriedOutThisTurn = true;
        PlansCarriedOutThisCombat++;
    }

    // ---- THE POOL OVERHAUL (2026-10-13) ------------------------------------
    // review/active/kokomi-pool-overhaul-2026-10-13.md, picks 1 (a) and 2 (a).
    // [USER]: "On Kokomi, I'm good with default on 1 and 2."

    /// <summary>
    /// CHAIN: the Plans carried out THIS TURN, the one being carried out
    /// included -- Feint's and Turning Tide's "for each Plan carried out this
    /// turn" and Battle Formation's third. Raised by
    /// <see cref="NotePlanCarryingOut"/> at the top of each carry-out, before
    /// its clauses run, so each Chain line counts itself; a doubled carry-out
    /// counts twice. Rolled with the turn. Sim twin:
    /// <c>CombatState.kk_plans_carried_out_this_turn</c>.
    /// </summary>
    public int PlansCarriedOutThisTurn { get; private set; }

    /// <summary>
    /// KOKOMI V3 (2026-10-18, review/active/kokomi-cards-2026-10-18.md sec.6;
    /// [USER]: "Makes sense! ... let's do both."): the same count less the
    /// Sting and Ward Plans -- Feint's and Turning Tide's "Stings and Wards
    /// don't count". Battle Formation keeps <see cref="PlansCarriedOutThisTurn"/>.
    /// Rolled with the turn. Sim twin:
    /// <c>CombatState.kk_chain_plans_this_turn</c>.
    /// </summary>
    public int ChainPlansThisTurn { get; private set; }

    /// <summary>A carry-out begins (<c>KokomiPlan.ResolveEntry</c>).
    /// <paramref name="jellyfish"/>: it is a Sting's or Ward's Plan, which
    /// the Chain count skips.</summary>
    public void NotePlanCarryingOut(bool jellyfish = false)
    {
        PlansCarriedOutThisTurn++;
        if (!jellyfish) ChainPlansThisTurn++;
    }

    /// <summary>
    /// COUNTER: the running totals every "since you planned this" Plan reads
    /// the difference of, per combat and never rolled. Written by
    /// <see cref="NoteEnemyHit"/> from
    /// <c>ProtoBakeKuragePower.AfterDamageReceived</c>, the marker every
    /// board has:
    ///   * <see cref="DamageBlockedTotal"/> -- Block that absorbed enemy
    ///     ATTACK damage (Kelp Wall);
    ///   * <see cref="DamageTakenTotal"/> -- all the damage enemies dealt
    ///     her, blocked or not (Turnabout);
    ///   * the attackers -- one entry per enemy Attack hit aimed at her,
    ///     blocked or not, by <c>CombatId</c> (Brine Sting, Prepared
    ///     Retreat).
    /// Sim twins: <c>CombatState.kk_damage_blocked_total</c>,
    /// <c>kk_damage_taken_total</c>, <c>kk_attackers</c>.
    /// </summary>
    public int DamageBlockedTotal { get; private set; }

    /// <inheritdoc cref="DamageBlockedTotal"/>
    public int DamageTakenTotal { get; private set; }

    /// <summary>KOKOMI V3 (2026-10-18): all the HP she lost this combat,
    /// from any source -- Unbroken Tide's "if you lost no HP since you
    /// planned this". Written by <see cref="NoteHpLost"/> from
    /// <c>ProtoBakeKuragePower.AfterCurrentHpChanged</c>. Sim twin:
    /// <c>CombatState.hp_lost_this_combat</c>.</summary>
    public int HpLostTotal { get; private set; }

    /// <summary>She lost <paramref name="amount"/> HP.</summary>
    public void NoteHpLost(int amount)
    {
        if (amount > 0) HpLostTotal += amount;
    }

    private readonly List<string> _attackers = new();

    /// <summary>One enemy hit landed on her. <paramref name="attack"/> is a
    /// powered Attack (the game's <c>IsPoweredAttack</c>): only an Attack
    /// counts as "attacked you" and only an Attack's absorbed damage as
    /// "damage you blocked"; every enemy hit counts toward the damage dealt
    /// her.</summary>
    public void NoteEnemyHit(string attackerId, int blocked, int unblocked,
                             bool attack)
    {
        DamageTakenTotal += System.Math.Max(0, blocked)
                          + System.Math.Max(0, unblocked);
        if (!attack) return;
        DamageBlockedTotal += System.Math.Max(0, blocked);
        _attackers.Add(attackerId);
    }

    /// <summary>
    /// ONE PLAN'S "SINCE YOU PLANNED THIS": the three running totals at the
    /// moment it was written. Stamped on the entry by
    /// <c>KokomiPlan.Schedule</c> (<see cref="OpenWindow"/>); each Counter
    /// clause reads its total less this. Sim twin: <c>PlanEntry.since_*</c>.
    /// </summary>
    public readonly record struct Since(int Blocked, int Taken, int Attacks,
                                        int HpLost = 0);

    /// <summary>A Plan is written: its window opens on the totals as they
    /// stand.</summary>
    public Since OpenWindow() =>
        new(DamageBlockedTotal, DamageTakenTotal, _attackers.Count,
            HpLostTotal);

    /// <summary>Unbroken Tide (Kokomi v3, 2026-10-18): did she lose any HP
    /// since the window opened? No window reads false. Sim twin:
    /// <c>kokomi_plan.hp_lost_since</c>.</summary>
    public bool HpLostSince(Since? window) =>
        window is { } w && HpLostTotal > w.HpLost;

    /// <summary>Kelp Wall: the damage she blocked since the window opened.
    /// No window reads 0.</summary>
    public int BlockedSince(Since? window) =>
        window is { } w ? System.Math.Max(0, DamageBlockedTotal - w.Blocked)
                        : 0;

    /// <summary>Turnabout: all the damage enemies dealt her since, blocked
    /// or not.</summary>
    public int TakenSince(Since? window) =>
        window is { } w ? System.Math.Max(0, DamageTakenTotal - w.Taken) : 0;

    /// <summary>Brine Sting: the enemies (by <c>CombatId</c>) whose Attack
    /// hit her since the window opened.</summary>
    public HashSet<string> AttackersSince(Since? window)
    {
        var set = new HashSet<string>();
        if (window is not { } w) return set;
        for (var i = System.Math.Max(0, w.Attacks); i < _attackers.Count; i++)
        {
            set.Add(_attackers[i]);
        }
        return set;
    }

    /// <summary>Prepared Retreat: did any enemy attack her since?</summary>
    public bool AttackedSince(Since? window) =>
        window is { } w && _attackers.Count > w.Attacks;

    /// <summary>All Streams Flow to the Sea: the Elemental Reactions she
    /// triggered this combat (<c>KokomiRefounding.OnReaction</c>). Never
    /// rolled. Sim twin: <c>CombatState.kk_reactions_this_combat</c>.
    /// </summary>
    public int ReactionsThisCombat { get; private set; }

    /// <summary>One reaction she triggered.</summary>
    public void NoteReaction() => ReactionsThisCombat++;

    /// <summary>The morning opens with <paramref name="plans"/> Plans due.
    /// Written by <c>KokomiPlan.ResolveAll</c> and by nothing else.</summary>
    public void NoteMorning(int plans) => PlansThisMorning = plans;

    /// <summary>The claim itself, on the ledger a caller already holds. Public
    /// to the pins for the reason <see cref="RollTo"/> is: a turn boundary can
    /// then be exercised without a combat, which is what the headless suite
    /// has.</summary>
    public bool Claim(string key) => _claimed.Add(key);

    /// <summary>
    /// THE ONCE-PER-COMBAT LATCH (Kokomi's own relics, 2026-10-15): Sango
    /// Pearl's "the first card you plan each combat". True the first time
    /// <paramref name="key"/> is claimed in this combat. Never rolled: the
    /// ledger itself is made fresh for each combat (<see cref="For"/>).
    /// </summary>
    public bool ClaimOncePerCombat(string key) => _claimedCombat.Add(key);

    private readonly HashSet<string> _claimedCombat = new();

    /// <summary>
    /// Roll the per-turn state to <paramref name="round"/>. Public to the pins
    /// so a turn boundary can be exercised without a combat.
    ///
    /// THE HANDOVER IS THE WHOLE POINT: this turn's count becomes last turn's,
    /// in the one place that can be true, so a Plan carried out at the top of a
    /// turn reads the turn that just ended.
    /// </summary>
    public void RollTo(int round)
    {
        if (round == _round) return;
        CompanionsPlayedThisTurn = 0;
        _claimed.Clear();
        PlanCarriedOutThisTurn = false;
        // `EB-335`. Cleared rather than handed over, and cleared HERE rather
        // than at the drain: `For` rolls on read, so the first ask of a new
        // round zeroes this before `ResolveAll` writes the new morning's depth
        // -- which is what makes a morning with no Plans read an honest zero.
        PlansThisMorning = 0;
        // (The last Companion played is combat-wide since the Kokomi level
        // pass, 2026-10-12, so a turn boundary leaves it alone.)
        NextPlanExtra = null;
        // The jellyfish build (2026-10-12): The Shape of Water's "this turn".
        StingsPlayedThisTurn = 0;
        // The pool overhaul (2026-10-13): the Chain count's "this turn".
        PlansCarriedOutThisTurn = 0;
        ChainPlansThisTurn = 0;
        _round = round;
    }
}
