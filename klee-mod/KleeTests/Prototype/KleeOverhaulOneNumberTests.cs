using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-270`: ONE NUMBER ON A BOMB PILE, not two.
///
/// THE DEFECT, and it is a defect the previous fix created. `EB-265` taught the
/// TOOLTIP to print what a Set off would actually deal -- Strength and Weak
/// included -- and left the BADGE printing the raw charge sum beside it. So a
/// Weak'd Klee looking at two Bombs of 8 and 9 read, in bold, `Bomb 17`, over a
/// sentence that said `a Set off here deals 12 Pyro damage in total, after
/// Weak`. The r2 Opus seat read the bold number first and called it "the wrong
/// one" (`klee-overhaul-r2-opus`); the r3 Codex seat got there by reasoning:
/// "the Bomb display showed Bomb 17 but said Set off would deal 12, which I
/// inferred was the Weak-adjusted amount but had to reason through".
///
/// THE THIRD SURFACE IS BIG BADDA BOOM'S BONUS LINE, which `EB-291` had
/// already reworded to "hit again for the damage the Bombs dealt" while the
/// ledger behind it still banked the charge SIZES -- so on that same board the
/// card promised 12 and hit for 17. Three surfaces, one arithmetic now:
/// <c>PredictedSetOffDamage</c> for the two the player reads before the play,
/// and <c>ElementalHit.Deal</c>'s own return value for the one read after it.
///
/// `EB-343` (R248) MOVED WHICH MODIFIERS ARE IN THE NUMBER -- a Bomb carries
/// the target's only -- and left this file's claim untouched: whatever is in
/// it, the badge, the tooltip and the bonus line print the SAME number. The
/// boards below were re-aimed from Klee's Weak onto the enemy's Vulnerable for
/// that reason and no other.
///
/// WHAT IS REAL HERE. The pile, its charges, the badge and the face are the
/// real power's, and Weak/Strength/Vulnerable are the game's own powers on a
/// real Creature. What is NOT reachable is an explosion: <c>Explode</c> needs
/// <c>ElementalHit.Deal</c> and a live <c>CombatState</c> (README, "The
/// headless boundary"), so the ledger's half is pinned as the arithmetic it
/// performs plus a structural read of the one call site that feeds it.
///
/// THE COLLECTION IS LOAD-BEARING, for the reason
/// <c>KleeOverhaulRoundOneFixTests</c> gives: <c>KleeOverhaul.Enabled</c> is
/// one static for the whole process.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulOneNumberTests
{
    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    private static string LocKey(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(pile)!;

    /// <summary>The `{Size}` var as the face renders it -- the live subclass,
    /// asked the way SmartFormat asks it.</summary>
    private static string PrintedSize(ProtoBombPower pile) =>
        pile.DynamicVars["Size"].ToString()!;

    // ---- the seat's own board --------------------------------------------

    [Fact]
    public void The_badge_and_the_face_agree_on_the_modified_board()
    {
        // The r3 Codex seat's board, in the shape R248 left it: two Bombs,
        // "Bomb 17" over "deals 17" until the ENEMY is debuffed, then both move
        // together. The seat's own board used Klee's Weak, which `EB-343` took
        // out of a Bomb entirely -- what EB-270 pinned is that the two surfaces
        // are ONE number, and that is what is pinned here.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(8), new ProtoBombs.Charge(9));

        Assert.Equal(17, pile.DisplayAmount);
        Assert.Equal(17, pile.PredictedSetOffDamage());

        enemy.WithPower<VulnerablePower>(1);

        Assert.Equal(25, pile.PredictedSetOffDamage());   // 12 + 13, per charge
        Assert.Equal(25, pile.DisplayAmount);
        Assert.Equal("25", PrintedSize(pile));
        // ... and the face still says WHY it is 25, which is EB-287's half
        // widened by R248: one number, and every modifier in it named.
        Assert.EndsWith(".smartDescriptionVulnerable", LocKey(pile));
        Assert.Contains("after [gold]Vulnerable[/gold]",
                        Row(pile, "smartDescriptionVulnerable"));
    }

    [Fact]
    public void The_badge_does_not_follow_klees_own_strength_or_weak()
    {
        // `EB-343`, and it is the reverse of what this file pinned before: the
        // badge sits on the ENEMY and reads as incoming damage, so pricing it
        // through Klee's swing stats made it unreadable -- [USER]'s three Bombs
        // of printed 6, 4 and 4 read `Bomb -1` under Tender's minus 5 Strength.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6));

        Assert.Equal(10, pile.DisplayAmount);

        klee.WithPower<StrengthPower>(2);

        Assert.Equal(10, pile.DisplayAmount);
        Assert.Equal(pile.PredictedSetOffDamage(), pile.DisplayAmount);
        Assert.Equal("10", PrintedSize(pile));
        // The face says so too: nothing of hers is folded in, so nothing of
        // hers is named.
        Assert.EndsWith(".smartDescription", LocKey(pile));
    }

    [Fact]
    public void Vulnerable_on_the_holder_moves_the_badge_too()
    {
        // The target-side term, and since `EB-343` the ONLY kind there is. It
        // is in `SimDamagePipeline.ResolveOnTarget` and so it is in the face;
        // the point of the pin is that the badge is the SAME call and cannot be
        // left behind by a second modifier.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(10));

        Assert.Equal(10, pile.DisplayAmount);

        enemy.WithPower<VulnerablePower>(1);

        Assert.Equal(15, pile.DisplayAmount);
        Assert.Equal(pile.PredictedSetOffDamage(), pile.DisplayAmount);
    }

    [Fact]
    public void An_empty_pile_reads_zero_on_both_surfaces()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature);

        Assert.Equal(0, pile.DisplayAmount);
        Assert.Equal(0, pile.PredictedSetOffDamage());
    }

    [Fact]
    public void The_raw_charge_sum_is_still_what_the_rules_are_priced_in()
    {
        // `TotalSize` is not deleted, and this says why: the growth, the jump
        // and Sorry Jean's Block all read the charge, not the damage. What
        // changed is that no PLAYER-facing surface reads it any more.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(8), new ProtoBombs.Charge(9));

        enemy.WithPower<VulnerablePower>(1);

        Assert.Equal(17, pile.TotalSize);
        Assert.Equal(25, pile.DisplayAmount);
    }

    // ---- the third surface: the bonus line -------------------------------

    [Fact]
    public void The_ledger_banks_damage_and_big_badda_boom_reads_it()
    {
        // The play memory is arithmetic and is reachable; what it is FED is
        // the structural half below.
        KleeOverhaulLedger.ResetAll();
        var ledger = new KleeOverhaulLedger();
        ledger.RollTo(1);

        ledger.NoteExplosion(reacted: false, damageDealt: 6);
        ledger.NoteExplosion(reacted: false, damageDealt: 6);

        Assert.Equal(12, ledger.DamageSetOffThisPlay);
        Assert.Equal(2, ledger.SetOffThisTurn);
    }

    [Fact]
    public void The_explosion_feeds_the_ledger_the_number_the_hit_returned()
    {
        // STRUCTURAL (Il): an explosion needs a live CombatState, so what is
        // asserted is that `Explode` takes the funnel's RESULT -- which is only
        // possible because it returns one -- and hands it to `NoteExplosion`.
        // Before EB-270 the funnel returned `Task` and the ledger was fed
        // `size`, and no value test could have seen the difference on an
        // unmodified board. `EB-343` renamed the door the Bomb goes through
        // (`DealWithoutDealerMods`) and both return the same `Task<int>`.
        foreach (var name in new[] { "Deal", "DealWithoutDealerMods" })
        {
            Assert.Equal(typeof(System.Threading.Tasks.Task<int>),
                         ((MethodInfo)Il.Method("ElementalHit", name)).ReturnType);
        }

        var explode = typeof(ProtoBombPower)
            .GetMethod("Explode", HeadlessGame.All)!;
        var calls = Il.Calls(explode);
        Assert.Contains(calls, c => c.Contains("ElementalHit.Deal"));
        Assert.Contains(calls, c => c.Contains("KleeOverhaulLedger.NoteExplosion"));
    }

    [Fact]
    public void The_badge_and_the_face_are_one_call_and_not_two_spellings()
    {
        // The anti-drift lock, the same shape `KleeOverhaulRoundOneFixTests`
        // uses on the pipeline: both player-facing surfaces must REACH
        // `PredictedSetOffDamage`, so a future edit cannot re-derive one of
        // them and put the two numbers back.
        var badge = typeof(ProtoBombPower)
            .GetProperty("DisplayAmount", HeadlessGame.All)!.GetGetMethod(true)!;
        Assert.Contains(Il.Calls(badge),
                        c => c.Contains("PredictedSetOffDamage"));

        var live = typeof(ProtoBombPower)
            .GetNestedType("SetOffDamageVar", HeadlessGame.All)!
            .GetProperty("Live", HeadlessGame.All)!.GetGetMethod(true)!;
        Assert.Contains(Il.Calls(live),
                        c => c.Contains("PredictedSetOffDamage"));
    }
}
