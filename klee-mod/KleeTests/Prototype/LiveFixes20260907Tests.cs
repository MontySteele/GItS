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
