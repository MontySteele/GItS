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

    // ---- Careful Now: the card, real off the shipped class ---------------

    [Fact]
    public void Careful_now_prints_its_cap_and_the_smith_moves_it()
    {
        // The row's ONE printed number is its ceiling, because the payout is
        // read off the board. So the face has to print the cap as a var and
        // `OnUpgrade` has to move that same var -- or the `+` card promises a
        // ceiling it does not have (`EB-283` / `EB-291`).
        var card = new ProtoKoCarefulNow();

        Assert.Contains("{BombCap:diff()}", Face(card));
        Assert.Equal(10m, Vars(card).Single().BaseValue);
        Assert.Contains(Il.Calls(Il.Method("ProtoKoCarefulNow", "OnUpgrade")),
                        c => c.Contains("UpgradeValueBy"));
    }

    [Fact]
    public void Careful_now_retains_and_hands_the_var_to_the_rule()
    {
        // Retain is on the BASE card (the row's own key), and the play passes
        // the VAR rather than a literal -- so the smithed ceiling is the
        // ceiling the rule enforces.
        var card = new ProtoKoCarefulNow();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);

        var play = Il.Calls(Il.Method("ProtoKoCarefulNow", "OnPlay"));
        Assert.Contains("ProtoBombPower.BlockForLargestBomb", play);
        Assert.Contains(play, c => c.EndsWith("get_IntValue"));
    }

    // ---- Barbara, Front Row Seat ----------------------------------------

    [Fact]
    public void Front_row_seat_pays_on_every_bomb_and_noelle_only_on_mines()
    {
        // THE ONE LINE BETWEEN THE TWO CARDS. Both watchers are paid from the
        // same switch, so neither can be forgotten at wire-up; what separates
        // them is the NOUN each prints, and the noun is the rule -- Noelle's
        // window is Mines and Barbara's is Bombs, so a Mine pays both and a
        // plain Bomb pays only Barbara. The arithmetic is the sim twin's
        // (`test_barbara_pays_per_bomb_and_not_only_per_mine`), because the
        // payout is a command.
        var paid = Il.Calls(Il.Method("CompanionStandIns", "OnExplosion"));
        Assert.Contains(paid, c => c.Contains("IGotYourBackPower"));
        Assert.Contains(paid, c => c.Contains("FrontRowSeatPower"));

        Assert.Contains("[gold]Mines[/gold]", Row<IGotYourBackPower>("description"));
        Assert.Contains("[gold]Bombs[/gold]", Row<FrontRowSeatPower>("description"));
        Assert.DoesNotContain("Mine", Row<FrontRowSeatPower>("description"));
    }

    [Fact]
    public void Front_row_seat_closes_where_the_arms_counters_roll()
    {
        // "This turn" is the ROUND, the enemy's half included, because Klee's
        // Mines go off when an ENEMY attacks -- a window that shut at the end
        // of her own turn could not fire at all. So the watcher removes itself
        // at `AfterPlayerTurnStart`, the same boundary Diona's and Noelle's
        // take and the same one the arm's explosion counters roll on.
        var close = typeof(FrontRowSeatPower)
            .GetMethod("AfterPlayerTurnStart", All | BindingFlags.DeclaredOnly);

        Assert.NotNull(close);
        Assert.Contains("PowerCmd.Remove", Il.Calls(close!));
        // And it is NOT on the explosion bus: the bus carries no Mine flag,
        // which is why this seam is paid from `Explode` beside the ledger
        // rather than through `IProtoExplosionListener`.
        Assert.False(typeof(IProtoExplosionListener)
                         .IsAssignableFrom(typeof(FrontRowSeatPower)));
    }

    [Fact]
    public void Front_row_seat_applies_hydro_twice()
    {
        // Round 8's Diona finding on the other element: one application on a
        // board Klee is already cooking is eaten by her own Pyro before the
        // companion's turn comes round, so the applier row worth drafting
        // applies twice.
        var play = Il.CallSequence(Il.Method("ProtoMcBarbaraFrontRowSeat",
                                             "OnPlay"));

        Assert.Equal(2, play.Count(c => c.Contains("ElementalHit.ApplyOnly")));
        Assert.Contains(play, c => c.Contains("FrontRowSeatPower"));
    }

    // ---- the shelf's own rule -------------------------------------------

    [Fact]
    public void No_row_on_the_shelf_is_a_plain_block()
    {
        // THE PACKET'S SCOPE STATEMENT, made mechanical: every Klee row on the
        // shelf names the Bomb state on its own face, so none of them is the
        // unconditional Block the arm deliberately does not have (Dig In is
        // that, and it is a Spark sink priced for it). TWO since the R253
        // charter audit withdrew Fire Safety and Safety Lesson.
        foreach (var card in new CardModel[]
                 {
                     new ProtoKoDodocoCover(), new ProtoKoCarefulNow(),
                 })
        {
            Assert.Contains("Bomb", Face(card));
        }
    }

    [Fact]
    public void Dodoco_cover_places_before_it_blocks()
    {
        // The opening hand's answer to "no placer": one card that cooks AND
        // pays a little safety, in that order, so the Block is what is left
        // over rather than the point of the card.
        var play = Il.CallSequence(Il.Method("ProtoKoDodocoCover", "OnPlay"));
        var place = play.ToList().FindIndex(c => c.Contains("ProtoBombPower.Place"));
        var block = play.ToList().FindIndex(c => c.Contains("CreatureCmd.GainBlock"));

        Assert.True(place >= 0 && block >= 0);
        Assert.True(place < block, "the Bomb is placed before the Block lands");
    }

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
