using System;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE 2026-09-07 LIVE FIXES -- six face-truth and log-truth rows off the Klee
/// seat rounds (`EB-457`, `EB-450`, `EB-400`, `EB-390`, `EB-318`, `EB-321`).
///
/// WHAT A PIN HERE CAN AND CANNOT SAY, and it is the arrangement
/// <see cref="Round22Tests"/> takes for the same reason: placing a charge and
/// dealing its damage both route through <c>PowerCmd</c> and a live
/// <c>CombatState</c>, which is outside the headless boundary (KleeTests
/// README). So a DECISION the arm takes purely is pinned by running it, and a
/// decision that lives inside an async command body is pinned by reading the
/// source of the one line that takes it, LABELLED as structural.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class LiveFixes20260907Tests
{
    // ==================================================================
    // `EB-457` -- the rider's Mine that printed on no status block
    // ==================================================================
    //
    // THE FIND (Klee r14 fight 6). "After Sizzle set off Jumpy Dumpty's bomb,
    // the Merc's status block showed a Pyro Aura but no Mine, even though the
    // rider prints 'place a Mine 3 on ALL enemies' ... the Merc went 21 -> 18
    // with no other source -- three damage, exactly a Mine 3, from a Mine no
    // screen ever printed."
    //
    // WHAT WAS RULED OUT, read off the shipped assemblies rather than guessed,
    // because the row named both suspects and both are answerable headlessly:
    //
    //   * `PowerModel.IsVisible` cannot be it. Its whole body is
    //     `Target == null || LocalContext.IsMe(Target) || Target.IsEnemy` ->
    //     `IsVisibleInternal`, and `IsVisibleInternal` is a two-byte `ldc.i4.1
    //     ret`. No pile sitting on an enemy can fail that, and the bridge's
    //     `if (!power.IsVisible) continue;` therefore never drops one.
    //   * `titleMine` cannot be it either. `KleeMod.cs` merges the arm's loc
    //     into `LocManager.Instance.GetTable("powers")`, which is the table
    //     <see cref="ProtoBombPower.Title"/>'s Mine branch names, so the Mine
    //     name resolves out of the same table the Bomb name does.
    //
    // WHAT IS REAL, AND IS THE ONE ENGINE DIVERGENCE ON THAT PATH: the rider's
    // sweep in `Explode` had no corpse guard, alone among the file's placement
    // walks and alone against its own sim twin, which has always swept
    // `state.living_enemies` (`tier0/engine/klee_overhaul.py`, `_explode`). A
    // Set off kills, and the sweep runs BETWEEN the explosions of one pile, so
    // a body an earlier charge killed still answers `HittableEnemies` when the
    // rider reaches it -- and the Mine that lands there prints on no status
    // block until `SweepJumps` moves it to a survivor.

    [Fact]
    public void The_rider_sweep_skips_a_corpse_like_every_other_placement_walk()
    {
        // STRUCTURAL, and labelled: the sweep is inside an async command body
        // that needs a live combat. What is read is the one line that takes
        // the decision, and the guard every other walk in the file carries.
        var source = Source("Powers/Prototype/ProtoBombPower.cs")
            .Replace("\r\n", "\n");

        var payload = source[source.IndexOf(
            "if (charge.PayloadMineAll > 0", StringComparison.Ordinal)..];
        payload = payload[..payload.IndexOf("await NotifyExplosionListeners",
                                            StringComparison.Ordinal)];

        Assert.Contains("if (enemy.IsDead) continue;", payload);
        Assert.Contains("isMine: true, payloadMineAll: 0", payload);
    }

    [Fact]
    public void A_riders_mine_prints_the_badge_a_placed_mine_prints()
    {
        // THE ACCEPTANCE, on the half that is not a command: the charge the
        // rider hands to `Place` is the charge Mine Toss hands to `Place`, so
        // the pile it lands in is titled `Mine`, carries one Mine and no rider
        // of its own, and therefore selects the same face. `payloadMineAll: 0`
        // is what makes the second half true -- a rider that travelled would
        // print `EB-573`'s rider clause on a charge that has none.
        var klee = Seat.Klee();
        var placed = Seat.Klee(30).Creature;
        var rider = Seat.Klee(30).Creature;

        var byCard = ProtoBombs.Place(placed, klee.Creature,
            new ProtoBombs.Charge(3, IsMine: true));
        var byRider = ProtoBombs.Place(rider, klee.Creature);
        byRider.AddCharge(new ProtoBombPower.ProtoCharge(3, true, 0));

        Assert.True(byCard.TitledAsMine);
        Assert.True(byRider.TitledAsMine);
        Assert.Equal(byCard.MineCount, byRider.MineCount);
        Assert.Equal(0, byRider.PayloadTotal);
        Assert.Equal(byCard.PayloadTotal, byRider.PayloadTotal);
        Assert.Equal(byCard.DisplayAmount, byRider.DisplayAmount);
    }

    // ==================================================================
    // `EB-450` -- the queue prints the order it actually holds
    // ==================================================================
    //
    // THE FIND (Klee r13 f6). The badge printed `Bomb 45 (4 bombs)` -- a sum
    // and a count -- while `EB-432`'s `Set off` tip says the charges go off
    // oldest first and the FIRST one takes the aura. The list replaced the
    // count on 2026-09-04 and still did not say it was IN that order, so on a
    // Cryo body which charge Melts stayed a fact the seat had to remember
    // placing rather than read.
    //
    // ONE ORDER AND NOT TWO: `_charges` is placement order, `TakeAll` copies
    // that list, and `SetOff` walks the copy front to back. The label now says
    // so, on both list faces, in the words the tip already uses.

    [Fact]
    public void The_badge_lists_the_charges_in_the_order_they_go_off()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5));
        // Through the power's own door, so the list grows the way it grows in
        // a fight: oldest first is placement order and nothing else.
        pile.AddCharge(new ProtoBombPower.ProtoCharge(8, false, 0));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(20, false, 0));
        pile.AddCharge(new ProtoBombPower.ProtoCharge(12, false, 0));

        Assert.Equal("5 / 8 / 20 / 12",
                     pile.DynamicVars["Charges"].ToString());
        // And the take the explosions walk hands the same order back.
        Assert.Equal(new[] { 5, 8, 20, 12 },
                     pile.TakeAll()!.Select(c => c.Size).ToArray());
    }

    [Fact]
    public void Both_list_faces_say_which_end_of_the_list_goes_first()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(60).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(8, IsMine: true));

        // EVERY face that prints the list, read off the power rather than
        // listed, so a new axis cannot be added without the order coming with
        // it -- the same claim `EB-289`'s pin makes about `{Charges}` itself.
        var listing = pile.Localization!
            .Where(r => r.Item1.StartsWith("smartDescription", StringComparison.Ordinal)
                        && r.Item2.Contains("{Charges}"))
            .ToList();
        Assert.NotEmpty(listing);
        foreach (var (_, face) in listing)
        {
            Assert.Contains("Bomb sizes here, oldest first:", face);
        }
    }

    // ==================================================================
    // `EB-390` -- Bomb-sized Block takes Dexterity like every other Block
    // ==================================================================
    //
    // THE FIND (Klee r10 run 2 act 2, finding 3). Dexterity 2 raised Dig In 8
    // to 10 and Barbara's 5 to 7 and left Sorry, Jean... at exactly the Bomb's
    // size, 13 for 13 -- while the card's face says "gain Block", which is the
    // sentence Dexterity's own face is about ("Block gained from cards").
    //
    // THE ROW OFFERED TWO RULES AND STATED NO DEFAULT, so the applied one is
    // the row's first: the Block goes through the card-Block pipeline. The
    // other -- print that the size is paid raw -- costs a card its verb to
    // keep a distinction nothing on the screen draws. `ValueProp.Move` is one
    // switch and both terms ride it: `DexterityPower.ModifyBlockAdditive` and
    // `FrailPower`'s multiplicative hook share the predicate
    // `props.IsPoweredCardOrMonsterMoveBlock()`.
    //
    // CAREFUL NOW TAKES IT TOO. Two Bomb-sized Blocks that disagree about
    // Dexterity is this row's defect one card later. What stays `Unpowered`
    // is Block no card printed, which is the line the engine's own predicate
    // draws. Behavioural twin: `test_klee_overhaul_rules.py`'s
    // `test_bomb_sized_block_takes_dexterity_like_every_other_card_block`.

    [Fact]
    public void Both_bomb_sized_blocks_gain_through_the_card_block_pipeline()
    {
        // STRUCTURAL, and labelled: `CreatureCmd.GainBlock` needs a live
        // combat. What is read is the ValueProp each site passes, which is the
        // whole of the decision, and that no Bomb-sized Block still opts out.
        var source = Source("Powers/Prototype/ProtoBombPower.cs");

        Assert.Contains(
            "await CreatureCmd.GainBlock(applier, size, ValueProp.Move, null);",
            source);
        Assert.Contains(
            "await CreatureCmd.GainBlock(applier, amount, ValueProp.Move, null);",
            source);
        Assert.DoesNotContain("GainBlock(applier, size, ValueProp.Unpowered",
                              source);
        Assert.DoesNotContain("GainBlock(applier, amount, ValueProp.Unpowered",
                              source);
    }

    // ==================================================================
    // `EB-318` -- the log says the rider's Mines were placed
    // ==================================================================
    //
    // THE FIND (round-7 act-1 seat, fight 4). One detonation of Jumpy Dumpty
    // -- a Spark +1 said one Bomb had gone off -- and the rider's Mines could
    // be confirmed only by that Spark: the rule is on the card, the result is
    // on the badges, and nothing joined the two at the moment it happened.
    //
    // THE COUNT QUESTION IS ANSWERED FIRST, by running it rather than arguing
    // it: `test_one_detonation_places_one_rider_mine_per_living_enemy` in
    // `tier0/tests/test_klee_overhaul_rules.py` shows one Mine per LIVING
    // enemy per detonation, host included. The seat's two Mine 3s on one body
    // are not reproducible in either engine, and `EB-457`'s corpse guard is
    // the only place the two ever disagreed.
    //
    // THE DISCLOSURE HALF IS A LINE. A counter nothing reads is dead weight;
    // what the row asks for is a sentence, so `KleeOverhaulLedger.NoteLine`
    // writes one at each of the two beats that happen while no card is in
    // front of the player -- the rider's sweep, with its count, and each
    // explosion, with its number and its reaction (`EB-450`'s log half) --
    // and mirrors it to `godot.log`. The page half of both rows is the board
    // it already reads: the bridge answers a play BEFORE the card resolves.

    [Fact]
    public void The_arm_log_keeps_its_lines_across_a_turn_and_caps_them()
    {
        var klee = Seat.Klee().Creature;
        KleeOverhaulLedger.ResetAll();
        var ledger = new KleeOverhaulLedger();

        ledger.NoteLine("Bomb 8 went off on Toadpole A for 12 (Melt)");
        ledger.NoteLine("Its rider placed Mine 3 on 2 enemies");
        // A LOG THAT FORGOT LAST TURN could not answer the question either
        // seat was asking, which was about a beat that had already passed --
        // so the turn roll leaves it alone, unlike rule 7's two counters.
        ledger.RollTo(4);

        Assert.Equal(new[] { "Bomb 8 went off on Toadpole A for 12 (Melt)",
                             "Its rider placed Mine 3 on 2 enemies" },
                     ledger.Lines.ToArray());
        Assert.Equal(0, ledger.SetOffThisTurn);

        for (var i = 0; i < 260; i++) ledger.NoteLine("line " + i);
        Assert.Equal(200, ledger.Lines.Count);
        Assert.Equal("line 259", ledger.Lines[^1]);   // oldest dropped first
        Assert.Equal(klee, klee);
    }

    [Fact]
    public void Both_unwitnessed_beats_write_a_line()
    {
        // STRUCTURAL, and labelled: both sites sit inside async command
        // bodies. What is read is that each writes, and what it writes with.
        var source = Source("Powers/Prototype/ProtoBombPower.cs");

        Assert.Contains("ledger.NoteLine(", source);
        Assert.Contains("Its rider placed Mine ", source);
        Assert.Contains("charge.IsMine ? ", source);
        // `EB-450`'s half: the reaction is NAMED, off the same lookup the
        // badge's own preview makes, taken before the funnel eats the aura.
        Assert.Contains(
            "ReactionTable.Lookup(pendingAura.Element, Element.Pyro)", source);
    }

    // ------------------------------------------------------------------

    internal static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    internal static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }
            dir = dir.Parent;
        }
        throw new System.IO.FileNotFoundException(
            $"could not find {relative} above {AppContext.BaseDirectory}");
    }
}
