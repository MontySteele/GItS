using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 7b -- the two RULE defects the blind act-2 seat found
/// (`klee round 7b, opus-act2.md` section (c) and
/// `opus-act2b.md` finding 3). Rows `EB-336` and `EB-337`.
///
/// BOTH ARE PARITY REPAIRS, which is why the sim needed no rule written for
/// either: `combat._enemy_turn` has always broken out of the hit loop when a
/// trap killed the attacker, and both start-of-turn blocks in `effects.py`
/// have always clamped their Block mark. The MOD had neither.
///
/// WHAT IS REAL AND WHAT IS STRUCTURAL, on the terms the README sets. The
/// pre-emption predicate and both marks' printed numbers are PURE reads and are
/// asserted for real against `Seat`-built creatures. What needs a live
/// `CombatState` -- the Mine actually exploding, `PowerCmd.Remove` actually
/// removing -- is pinned off the compiled method and says so.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round7bTests
{
    /// <summary>`IsPoweredAttack()`: Move without Unpowered. An enemy's swing.
    /// </summary>
    private static ValueProp Attack => ValueProp.Move;

    /// <summary>A Bomb's own hit, which is Unpowered and must never be
    /// pre-empted by this rule.</summary>
    private static ValueProp Explosion => ValueProp.Unpowered;

    /// <summary>The standing listener, allocated rather than resolved:
    /// `ModelDb` is outside the headless boundary and this hook reads no
    /// instance state at all.</summary>
    private static KleeOverhaulSweepHooks Hooks() =>
        (KleeOverhaulSweepHooks)RuntimeHelpers
            .GetUninitializedObject(typeof(KleeOverhaulSweepHooks));

    /// <summary>The one step of the game's kill path this rule reads, and the
    /// step `BombDeathTeardownTests` already pins on `CreatureCmd`: the
    /// creature is dead.</summary>
    private static void Kill(Creature creature) =>
        Seat.Set(creature, "CurrentHp", 0);

    // ---- EB-336: a lethal Mine pre-empts the hit that fired it -----------

    [Fact]
    public void EB336_a_mine_that_kills_the_attacker_costs_klee_no_hp()
    {
        // The seat's own board: a Chomper on 4 HP under a Mine 4, swinging.
        // The Mine fires from inside `Hook.BeforeDamageReceived`, the kill
        // lands, and the hit that triggered it is already in flight -- so the
        // pre-emption is spent one hook later, here.
        var klee = Seat.Klee();
        var chomper = Seat.Klee(4).Creature;
        KleeOverhaul.Enabled = true;
        ProtoBombPower.Preempted.Clear();
        try
        {
            Kill(chomper);
            ProtoBombPower.Preempted.Note(klee.Creature, chomper);

            Assert.Equal(0m, Hooks().ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Attack, chomper, cardSource: null));
        }
        finally
        {
            ProtoBombPower.Preempted.Clear();
            KleeOverhaul.Enabled = KleeOverhaul.DefaultEnabled;
        }
    }

    [Fact]
    public void EB336_a_mine_that_does_not_kill_leaves_the_hit_intact()
    {
        // The other half of the acceptance, and the half that was always
        // right: nothing was noted, the attacker is alive, the hit is the hit.
        var klee = Seat.Klee();
        var chomper = Seat.Klee(62).Creature;
        KleeOverhaul.Enabled = true;
        ProtoBombPower.Preempted.Clear();
        try
        {
            Assert.False(chomper.IsDead);

            Assert.Equal(8m, Hooks().ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Attack, chomper, cardSource: null));
        }
        finally
        {
            KleeOverhaul.Enabled = KleeOverhaul.DefaultEnabled;
        }
    }

    [Fact]
    public void EB336_the_note_is_spent_on_one_victim_one_attacker_and_one_arm()
    {
        // Three guards, each of which is a way the rule could have leaked:
        // another creature's hit, an explosion rather than an attack, and the
        // arm being off. The note is deliberately not cleared between them --
        // it cannot be, purely -- so every one of these is the predicate
        // refusing rather than an empty latch answering.
        var klee = Seat.Klee();
        var other = Seat.Klee(40).Creature;
        var chomper = Seat.Klee(4).Creature;
        ProtoBombPower.Preempted.Clear();
        try
        {
            Kill(chomper);
            ProtoBombPower.Preempted.Note(klee.Creature, chomper);

            KleeOverhaul.Enabled = true;
            // a different victim
            Assert.Equal(8m, Hooks().ModifyHpLostBeforeOsty(
                other, 8m, Attack, chomper, cardSource: null));
            // a different dealer
            Assert.Equal(8m, Hooks().ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Attack, other, cardSource: null));
            // not an attack -- a Bomb's own Unpowered hit
            Assert.Equal(8m, Hooks().ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Explosion, chomper, cardSource: null));

            KleeOverhaul.Enabled = false;
            Assert.Equal(8m, Hooks().ModifyHpLostBeforeOsty(
                klee.Creature, 8m, Attack, chomper, cardSource: null));
        }
        finally
        {
            ProtoBombPower.Preempted.Clear();
            KleeOverhaul.Enabled = KleeOverhaul.DefaultEnabled;
        }
    }

    [Fact]
    public void EB336_the_mine_hook_notes_the_pre_emption_and_the_rebase_drops_it()
    {
        // STRUCTURAL: the Mine actually exploding needs a live combat. What is
        // read here is that `BeforeDamageReceived` reaches the note at all --
        // the wiring that turns a kill into a pre-empted hit -- and that the
        // arm's one per-combat reset drops it, so a note can never outlive the
        // fight it was taken in.
        Assert.Contains("Preempted.Note",
                        Il.Calls(Il.Method("ProtoBombPower",
                                           "BeforeDamageReceived")));
        Assert.Contains("Preempted.Clear",
                        Il.Calls(Il.Method("Register", "Rebase")));
    }

    // ---- EB-337: the Block marks print what is actually left -------------

    [Fact]
    public void EB337_the_barrier_prints_the_block_that_is_actually_standing()
    {
        // The seat's own screen: "Blazing Barrier 6 -- 6 Block left" with
        // `Block` at 0, and a 15 through the middle of it. The mark is a mark
        // on a pool that had been cleared; the number now reads the pool.
        var klee = Seat.Klee().WithPower<BlazingBarrierPower>(6);
        var barrier = Barrier<BlazingBarrierPower>(klee);

        Seat.Set(klee.Creature, "Block", 6);
        Assert.Equal(6, barrier.DisplayAmount);

        Seat.Set(klee.Creature, "Block", 2);
        Assert.Equal(2, barrier.DisplayAmount);

        Seat.Set(klee.Creature, "Block", 0);
        Assert.Equal(0, barrier.DisplayAmount);
    }

    [Fact]
    public void EB337_dionas_paws_are_the_same_mark_and_take_the_same_number()
    {
        // The two are one construction -- the file says so and the sim clamps
        // both -- so the fix is one construction too. Pinned because a mark
        // that lies is the defect, not the character whose card carries it.
        var klee = Seat.Klee().WithPower<IcyPawsPower>(6);
        var paws = Barrier<IcyPawsPower>(klee);

        Seat.Set(klee.Creature, "Block", 4);

        Assert.Equal(4, paws.DisplayAmount);
    }

    [Fact]
    public void EB337_the_mark_never_reports_more_block_than_it_marked()
    {
        // The other direction, and the reason it is a MIN rather than a read
        // of the pool: Block granted by anything else is not this card's, so a
        // 6-mark under 20 Block is still a 6-mark.
        var klee = Seat.Klee().WithPower<BlazingBarrierPower>(6);
        var barrier = Barrier<BlazingBarrierPower>(klee);

        Seat.Set(klee.Creature, "Block", 20);

        Assert.Equal(6, barrier.DisplayAmount);
    }

    [Fact]
    public void EB337_a_spent_mark_leaves_at_the_start_of_the_turn()
    {
        // STRUCTURAL: `PowerCmd.Remove` needs a live combat. What is read is
        // the wiring the sim already has and the mod did not -- both marks
        // reach the shared clamp from `AfterPlayerTurnStart`, and the clamp
        // removes rather than merely reporting.
        Assert.Contains("BlockMark.ClearIfSpent",
                        Il.Calls(Il.Method("BlazingBarrierPower",
                                           "AfterPlayerTurnStart")));
        Assert.Contains("BlockMark.ClearIfSpent",
                        Il.Calls(Il.Method("IcyPawsPower",
                                           "AfterPlayerTurnStart")));
        Assert.Contains("PowerCmd.Remove",
                        Il.Calls(Il.Method("BlockMark", "ClearIfSpent")));
    }

    [Fact]
    public void EB337_the_rider_still_pays_on_absorbed_damage()
    {
        // STRUCTURAL, and it is the half the row asks to be sure of: the "gain
        // 3" is still what `Thicken` does, off the same `Owner.Block` the
        // printed number now reads, and it still lowers the mark it spent.
        var thicken = Il.Calls(Il.Method("BlazingBarrierPower", "Thicken"));

        Assert.Contains("CreatureCmd.GainBlock", thicken);
        Assert.Contains(thicken, c => c.Contains("ModifyAmount")
                                      || c.Contains("Remove"));
    }

    /// <summary>The power this seat was just given, read back off the creature
    /// -- `Seat.WithPower` returns the seat, not the power.</summary>
    private static T Barrier<T>(Seat seat) where T : MegaCrit.Sts2.Core.Models.PowerModel
    {
        foreach (var power in seat.Creature.Powers)
        {
            if (power is T match) return match;
        }
        throw new System.InvalidOperationException("the power was not applied");
    }
}
