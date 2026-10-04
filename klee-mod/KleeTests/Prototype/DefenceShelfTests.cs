using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE DEFENCE SHELF -- <c>R252</c>, Klee round 9 pick 1 taken at its default
/// (<c>review/ruled/klee-overhaul-round-9-2026-09-04.md</c>).
///
/// The round-9 run died on act-2 floor 22 with no Block in hand, and the arm
/// offered none of its four defensive rows in ten rewards. The answer is four
/// rows in Klee's pool plus a fifth companion stand-in, and the rule the whole
/// shelf is written to is one sentence: EVERY ROW IS KEYED TO THE BOMB STATE
/// AND NONE IS A PLAIN BLOCK. That is what most of this file pins.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on the README's terms. The READ
/// half of Careful Now is real -- <c>LargestPlacedBy</c> against real piles on
/// a real <c>CombatState</c>, and the two paths that pay nothing run all the
/// way through <see cref="ProtoBombPower.BlockForLargestBomb"/> itself. What
/// needs <c>CreatureCmd.GainBlock</c> to actually spend a command, and every
/// explosion that would fire a listener, is outside the headless boundary and
/// is pinned off the compiled method, labelled. The end-to-end arithmetic is
/// the sim twin's: <c>tier0/tests/test_klee_overhaul_rules.py</c>, section
/// "THE DEFENCE SHELF".
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class DefenceShelfTests
{
    private const BindingFlags All = HeadlessGame.All;

    // ---- Careful Now: the read, real ------------------------------------

    [Fact]
    public void Careful_now_reads_the_largest_single_charge_board_wide()
    {
        // THE READ IS THE CARD. "Block equal to your largest Bomb" is the
        // largest ONE charge anywhere on the board -- not the sum of a pile
        // (that is `TotalPlacedBy`, which every other rule in the arm is still
        // priced in) and not one enemy's, because the row takes no target.
        var klee = Seat.Klee();
        var a = Seat.Klee(200).Creature;
        var b = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, a, b);

        ProtoBombs.Place(a, klee.Creature,
                         new ProtoBombs.Charge(3), new ProtoBombs.Charge(4));
        ProtoBombs.Place(b, klee.Creature, new ProtoBombs.Charge(9));

        // The card pays 9 on this board: the largest ONE charge. Not 7 (a's
        // pile summed, which is what `TotalPlacedBy` answers and what every
        // OTHER rule in the arm is still priced in), and not 16 (the board
        // summed, which nothing answers at all).
        Assert.Equal(4, ProtoBombPower.LargestPlacedBy(a, klee.Creature));
        Assert.Equal(9, ProtoBombPower.LargestPlacedBy(b, klee.Creature));
        Assert.Equal(7, ProtoBombPower.TotalPlacedBy(a, klee.Creature));
    }

    [Fact]
    public async Task Careful_now_on_a_bomb_less_board_pays_nothing()
    {
        // REAL, all the way through the shipped method: with nothing to read
        // it returns before it can reach `CreatureCmd.GainBlock`, so a Retain
        // card held on an empty board banks no Block. A row that paid its cap
        // regardless would be the flat Block this shelf is written not to be.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        Assert.Equal(0, await ProtoBombPower.BlockForLargestBomb(
            null!, klee.Creature, cap: 10));
    }

    [Fact]
    public async Task Careful_now_pays_nothing_for_a_cap_of_zero_or_less()
    {
        // The row's own guard, real: a cap of 0 is a sheet defect and not an
        // uncapped card, so it grants nothing rather than everything. The
        // codegen refuses such a row outright (`blocked_reason`), and this is
        // the runtime's own answer beside it.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(200).Creature;
        ProtoBombs.Board(klee.Creature, enemy);
        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(9));

        Assert.Equal(0, await ProtoBombPower.BlockForLargestBomb(
            null!, klee.Creature, cap: 0));
    }

    [Fact]
    public void Careful_now_spends_nothing_and_caps_what_it_pays()
    {
        // STRUCTURAL: the payout runs `CreatureCmd.GainBlock`, which needs a
        // live combat. What is read off the compiled method is the whole of
        // what separates this row from Sorry, Jean... one method up -- it
        // calls the READER and none of the three ways this arm takes a charge
        // off a pile, so the Bombs are still there and still growing
        // afterwards.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "BlockForLargestBomb"));

        Assert.Contains("ProtoBombPower.LargestPlacedBy", calls);
        Assert.Contains(calls, c => c.StartsWith("CreatureCmd.GainBlock"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeAll"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeAt"));
        Assert.DoesNotContain(calls, c => c.Contains("TakeMines"));
        Assert.DoesNotContain(calls, c => c.StartsWith("PowerCmd.Remove"));
    }

    // (Careful Now's card pins left with the row: the Klee status package,
    // 2026-10-01, cut it and Dodoco Cover. The reader above stays.)

    // (Barbara, Front Row Seat was cut by the Klee-only companions, 2026-10-03.)

    // ---- helpers ---------------------------------------------------------

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary><c>CanonicalVars</c> is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();

    /// <summary>A power's loc rows, off an instance allocated uninitialised:
    /// these `Localization` getters are pure string builders that read nothing
    /// off the instance (<c>Round8Tests</c>' idiom).</summary>
    private static string Row<T>(string key) where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", All)!.GetValue(model)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

}
