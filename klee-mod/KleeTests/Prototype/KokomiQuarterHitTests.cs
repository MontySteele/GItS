using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-693` -- SANGO ISSHIN'S QUARTER HIT IS ONE KIND OF DAMAGE, and
/// `EB-563` -- the jellyfish's box says how many Plans it holds.
///
/// `EB-693`, THE FIND (Kokomi r29, lane 1 (c)). The quarter-of-Max-HP hit took
/// her Strength -- 22 where the face said 20 -- and did NOT take the Effigy's
/// Slow, while Strike and Feint took that same Slow on the next turn. Two hits
/// from one seat one turn apart, obeying two different rule sets, off a card
/// whose own type is `Attack`.
///
/// WHY. <c>QuarterMaxHp</c> went out through <c>ElementalHit.Deal</c>, the
/// UNPOWERED door: it hand-rolls the dealer's Strength and the target's
/// Vulnerable and reaches <c>CreatureCmd.Damage</c> as
/// <c>ValueProp.Unpowered</c> with <c>dealer: null</c>. Every game power that
/// answers an ATTACK gates on <c>props.IsPoweredAttack()</c>
/// (<c>SlowPower</c>, <c>VigorPower</c>, the lot, read off the 0.111.0
/// decompile), so all of them were skipped by construction. That door is right
/// for a Bomb and for a Plan carry-out, where the rule IS that the hit is
/// nobody's attack; it is wrong for an Attack card's own damage.
///
/// THE D DEFAULT, APPLIED: Attack damage with ALL modifiers, in both engines.
///
/// WHAT A HEADLESS TEST CAN SAY ABOUT SLOW. Nothing about the NUMBER: a hit in
/// this mod needs a live <c>CombatState</c> (KleeTests/README.md, "The
/// headless boundary"). What it can say is WHICH DOOR the call takes, and that
/// is the whole of the rule here -- Slow answers a powered attack and skips an
/// unpowered hit, so "this call site uses the powered builder" IS "Slow
/// applies". Same discipline as <c>ElementalHit.DealWithoutDealerMods</c>,
/// which exists to make the opposite fact pinnable.
///
/// Sim twin: `tier0/tests/test_eb693_the_quarter_hit_is_attack_damage.py`,
/// which runs the numbers the sim can run.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class KokomiQuarterHitTests
{
    [Fact]
    public void The_aimed_quarter_goes_out_through_the_powered_attack_door()
    {
        var calls = Il.Calls(Il.Method("KokomiRules", "QuarterMaxHp"));

        Assert.Contains(calls, c => c.EndsWith("DamageCmd.Attack"));
        Assert.DoesNotContain(calls, c => c.EndsWith("ElementalHit.Deal"));
    }

    [Fact]
    public void And_so_does_the_all_enemies_volley()
    {
        // ONE DOOR FOR BOTH CLAUSES, which is the row's acceptance sentence
        // ("one damage kind"): an enemy's Slow must not be read on one half of
        // this card and not the other.
        var calls = Il.Calls(Il.Method("KokomiRules", "QuarterMaxHpAll"));

        Assert.Contains(calls, c => c.EndsWith("DamageCmd.Attack"));
        Assert.DoesNotContain(calls, c => c.EndsWith("ElementalHit.Deal"));
    }

    [Fact]
    public void The_quarter_is_still_computed_in_one_place()
    {
        // Unmoved by `EB-693` and load-bearing: the face, the aimed hit and
        // the planned all-enemies version read one `QuarterOfMaxHp`, so they
        // cannot round differently (the Furina legibility lesson).
        foreach (var name in new[] { "QuarterMaxHp", "QuarterMaxHpAll" })
        {
            Assert.Contains(Il.Calls(Il.Method("KokomiRules", name)),
                            c => c.EndsWith("KokomiRules.QuarterOfMaxHp"));
        }
    }

    [Fact]
    public void The_planned_carry_out_keeps_the_unpowered_door()
    {
        // THE OTHER CLAUSE DID NOT MOVE. A Plan's carry-out is dealt by the
        // Bake-Kurage and not by her (`EB-334`, R246 pick 1), so it stays an
        // unpowered `ElementalHit` -- which is exactly what the `Plan` keyword
        // prints ("A carry-out is not a hit: no when-hit power fires") and
        // what a seat commits a turn against. One card, two clauses, two
        // rules.
        Assert.Contains(Il.Calls(Il.Method("KokomiPlan", "Hit")),
                        c => c.EndsWith("ElementalHit.Deal"));
    }

    // ==================================================================
    // `EB-563` -- the box says how many Plans the jellyfish holds
    // ==================================================================

    [Fact]
    public void The_jellyfish_box_says_it_holds_any_number_of_plans()
    {
        // THE FIND (Kokomi r20 lane 2). No screen said how many Plans the
        // Bake-Kurage holds, and the seat wrote ONE at a time for four
        // fights. Three r4c seats read the `Plan` badge's number as a
        // capacity for the same reason. `KokomiPlan` caps nothing on an
        // unconfigured build. The row's acceptance sentence was this box's
        // until the 2026-09-25 text pass cut the box to two plain facts; the
        // "any number" sentence is the panel's (`PLAN_COUNT_NOTE`) now, and
        // the box still speaks of the queue in the plural.
        var body = Description<ProtoBakeKuragePower>();

        Assert.Contains("It holds your [gold]Plans[/gold]", body);
        // "Plans" when more than one, which is the row's other half: the
        // count badge pluralizes off its own amount, so it prints `Plan` at 1
        // and `Plans` above it, and the box -- which speaks of the whole queue
        // -- is plural flat.
        Assert.Contains("[gold]Plan{Amount:plural:|s}[/gold]",
                        Description<PendingPlansPower>());
    }

    [Fact]
    public void The_box_still_says_what_the_jellyfish_is_and_when_it_acts()
    {
        // THE 2026-09-25 TEXT PASS: two plain facts, the untargetable rule
        // and when the held Plans are carried out. The Dusk timing is the
        // `Dusk` tip's alone, and `EB-293`'s "where" is on the `Plan` word
        // ("Play the card on the Bake-Kurage") and on a Plan-only row's own
        // face ("Play on the Bake-Kurage.").
        var body = Description<ProtoBakeKuragePower>();

        Assert.StartsWith("Enemies can't target it. It holds your "
                        + "[gold]Plans[/gold] until your next turn.", body);
        Assert.DoesNotContain("Dusk", body);
    }

    private static string Description<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", HeadlessGame.All)!
            .GetValue(model)!;
        return rows.First(r => r.Item1 == "description").Item2;
    }
}
