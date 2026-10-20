using System;
using System.Linq;
using System.Text.Json;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Tests.Prototype;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// 2026-10-19 -- WHAT BOREAS'S FANG PAID (Varka Fang review, pick 2a: "Cryo
/// stays and gets measured"). The fight record's appended `fang_*` fields:
/// payouts and damage by element, Block, Vulnerable stacks, and the
/// Vulnerable bonus credited to the Fang's share of an enemy's stacks
/// (<c>PlayTelemetry</c>'s "Boreas's Fang" section states the rule). The
/// hook-free halves, as <see cref="TempoTelemetryTests"/> drives them.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class FangTelemetryTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public FangTelemetryTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
    }

    public void Dispose() => Invoke("ResetForTest");

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static JsonElement Record(Player player)
    {
        var json = (string?)Invoke("JsonForTest", player);
        Assert.NotNull(json);
        return JsonDocument.Parse(json!).RootElement.Clone();
    }

    private static Creature Enemy(int hp = 40)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        return (Creature)ctor.Invoke(new object?[] { null, hp, hp });
    }

    private static decimal Bonus(JsonElement r) =>
        decimal.Parse(r.GetProperty("fang_vulnerable_bonus_damage").GetRawText(),
                      System.Globalization.CultureInfo.InvariantCulture);

    [Fact]
    public void Fang_damage_is_filed_by_element_and_still_under_swirl()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var a = Enemy();
        var b = Enemy();

        // The Swirl's own flat hit: no Fang tag.
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
        {
            Invoke("RecordDamage", a, 2, 0, null, null);
            // A Pyro payout: 5, one point of it into Block.
            Invoke("FangPaidForTest", varka.Player, "Pyro", 0, null, 0, 0);
            using (DamageCredit.OpenFang("Pyro"))
                Invoke("RecordDamage", a, 4, 1, null, null);
            // An Electro payout on two bodies.
            Invoke("FangPaidForTest", varka.Player, "Electro", 0, null, 0, 0);
            using (DamageCredit.OpenFang("Electro"))
            {
                Invoke("RecordDamage", a, 3, 0, null, null);
                Invoke("RecordDamage", b, 3, 0, null, null);
            }
        }
        Assert.Null(DamageCredit.FangElement);

        var r = Record(varka.Player);
        var paid = r.GetProperty("fang_payouts_by_element");
        Assert.Equal(1, paid.GetProperty("Pyro").GetInt32());
        Assert.Equal(1, paid.GetProperty("Electro").GetInt32());
        var dmg = r.GetProperty("fang_damage_by_element");
        Assert.Equal(4, dmg.GetProperty("Pyro").GetInt32());
        Assert.Equal(6, dmg.GetProperty("Electro").GetInt32());
        Assert.Equal(1, r.GetProperty("fang_damage_blocked").GetInt32());
        // Back-compat: every point is still under "(Swirl)".
        Assert.Equal(12, r.GetProperty("damage_by_source")
                          .GetProperty("(Swirl)").GetInt32());
    }

    [Fact]
    public void A_killing_fang_hit_is_filed_from_its_snapshot()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var enemy = Enemy(3);
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
        using (DamageCredit.OpenFang("Pyro"))
            Invoke("NoteBeforeDamage", enemy, null, null);
        Invoke("RecordDeath", enemy);
        var r = Record(varka.Player);
        Assert.Equal(3, r.GetProperty("fang_damage_by_element")
                         .GetProperty("Pyro").GetInt32());
    }

    [Fact]
    public void Hydro_block_and_cryo_stacks_are_counted()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var enemy = Enemy();
        Invoke("FangPaidForTest", varka.Player, "Hydro", 3, null, 0, 0);
        Invoke("FangPaidForTest", varka.Player, "Hydro", 3, null, 0, 0);
        Invoke("FangPaidForTest", varka.Player, "Cryo", 0, enemy, 0, 1);
        // An Artifact ate this one: no stack added.
        Invoke("FangPaidForTest", varka.Player, "Cryo", 0, enemy, 1, 1);
        var r = Record(varka.Player);
        Assert.Equal(2, r.GetProperty("fang_payouts_by_element")
                         .GetProperty("Hydro").GetInt32());
        Assert.Equal(2, r.GetProperty("fang_payouts_by_element")
                         .GetProperty("Cryo").GetInt32());
        Assert.Equal(6, r.GetProperty("fang_block").GetInt32());
        Assert.Equal(1, r.GetProperty("fang_vulnerable").GetInt32());
    }

    [Fact]
    public void The_vulnerable_bonus_goes_to_the_fangs_share_of_the_stacks()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var enemy = Enemy();
        var other = Enemy();

        // The Fang owns all of 1 stack: a 9-point hit's bonus is 9 - 9/1.5 = 3.
        Invoke("FangPaidForTest", varka.Player, "Cryo", 0, enemy, 0, 1);
        Invoke("RecordVulnerableHit", enemy, 9, 1);
        Assert.Equal(3m, Bonus(Record(varka.Player)));

        // Another source adds 2: the Fang owns 1 of 3, a third of the next 6.
        Invoke("RecordVulnerableHit", enemy, 6, 3);
        Assert.Equal(3.67m, Bonus(Record(varka.Player)));

        // The decay takes 3 to 2 at turn open: the Fang's 1 becomes 2/3, a
        // third of the stacks still, so a 6-point hit adds 2/3 again.
        Invoke("SyncFangVulnerableForTest", enemy, 2);
        Invoke("RecordVulnerableHit", enemy, 6, 2);
        Assert.Equal(4.33m, Bonus(Record(varka.Player)));

        // Vulnerable gone: nothing more, even when another source re-applies.
        Invoke("RecordVulnerableHit", enemy, 6, 0);
        Invoke("RecordVulnerableHit", enemy, 6, 2);
        // An enemy the Fang never touched files nothing.
        Invoke("RecordVulnerableHit", other, 9, 1);
        Assert.Equal(4.33m, Bonus(Record(varka.Player)));
    }

    [Fact]
    public void A_seat_with_no_fang_writes_no_fang_fields()
    {
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        var r = Record(klee.Player);
        Assert.False(r.TryGetProperty("fang_payouts_by_element", out _));
    }
}
