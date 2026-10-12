using System;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using KleeMod.Tests.Prototype;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// 2026-10-12 -- THE FURINA/VARKA ROUND'S UNREADABLE WATCH ITEMS. The fight
/// record gains cards drawn and Energy per turn (every character), Varka's
/// Oath by element per turn with its peaks and his current element, a Swirl's
/// damage by the card behind it (`swirl_damage_by_card`, beside the unchanged
/// "(Swirl)" source), and Furina's Full House triggers. The hooks need a live
/// combat; the suite drives the hook-free halves, as
/// <c>DamageCreditTelemetryTests</c> does. Python twin:
/// <c>tier0/tests/test_telemetry_report.py</c>.
/// </summary>
[Collection(CombatInProgressSwitch.Name)]
public class TempoTelemetryTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public TempoTelemetryTests()
    {
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        Invoke("ResetForTest");
        FurinaStageLedger.ResetAll();
    }

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static JsonElement Record(Player player)
    {
        var json = (string?)Invoke("JsonForTest", player);
        Assert.NotNull(json);
        return JsonDocument.Parse(json!).RootElement.Clone();
    }

    private static int[][] Rows(JsonElement r, string key) =>
        r.GetProperty(key).EnumerateArray()
            .Select(row => row.EnumerateArray().Select(v => v.GetInt32()).ToArray())
            .ToArray();

    private static Creature Enemy(int hp = 40)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        return (Creature)ctor.Invoke(new object?[] { null, hp, hp });
    }

    [Fact]
    public void Draws_are_counted_per_round_and_a_turn_with_none_reads_zero()
    {
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordTurnStartForTest", 1);
        for (var i = 0; i < 5; i++) Invoke("RecordCardDrawn", klee.Player, 1);
        Invoke("RecordTurnStartForTest", 2);                  // drew nothing
        Invoke("RecordCardDrawn", klee.Player, 3);            // an effect's draw
        Invoke("RecordTurnStartForTest", 3);                  // keeps the 1
        var r = Record(klee.Player);
        Assert.Equal(new[] { new[] { 1, 5 }, new[] { 2, 0 }, new[] { 3, 1 } },
                     Rows(r, "cards_drawn_by_turn"));
    }

    [Fact]
    public void Energy_rows_pair_the_turn_start_with_what_was_spent()
    {
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Invoke("RecordEnergyTurnStart", klee.Player, 1, 3);
        Invoke("RecordEnergyTurnStart", klee.Player, 1, 9);   // first kept
        Invoke("RecordEnergySpent", klee.Player, 1, 1);
        Invoke("RecordEnergySpent", klee.Player, 1, 2);
        Invoke("RecordEnergyTurnStart", klee.Player, 2, 4);   // spent nothing
        Invoke("RecordEnergySpent", klee.Player, 3, 2);       // start unread
        var r = Record(klee.Player);
        Assert.Equal(new[] { new[] { 1, 3, 3 }, new[] { 2, 4, 0 },
                             new[] { 3, -1, 2 } },
                     Rows(r, "energy_by_turn"));
    }

    [Fact]
    public void Oath_keys_are_written_for_varka_alone()
    {
        var varka = Seat.Varka();
        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", varka.Player, 2, 0);
        Invoke("OpenSeatForTest", klee.Player, 2, 1);
        var names = new[] { "Pyro", "Hydro", "Electro", "Cryo" };
        Invoke("RecordOathForTest", varka.Player, 1, names,
               new[] { 2, 0, 1, 0 }, "Pyro");
        Invoke("RecordOathForTest", varka.Player, 2, names,
               new[] { 1, 3, 1, 0 }, "Hydro");
        var r = Record(varka.Player);
        var turns = r.GetProperty("oath_by_turn").EnumerateArray().ToArray();
        Assert.Equal(2, turns.Length);
        Assert.Equal(1, turns[0][0].GetInt32());
        Assert.Equal(2, turns[0][1].GetProperty("Pyro").GetInt32());
        Assert.Equal(3, turns[1][1].GetProperty("Hydro").GetInt32());
        var peak = r.GetProperty("oath_peak");
        Assert.Equal(2, peak.GetProperty("Pyro").GetInt32());
        Assert.Equal(3, peak.GetProperty("Hydro").GetInt32());
        Assert.Equal(1, peak.GetProperty("Electro").GetInt32());
        Assert.Equal(0, peak.GetProperty("Cryo").GetInt32());
        Assert.Equal(new[] { "Pyro", "Hydro" },
            r.GetProperty("current_element_by_turn").EnumerateArray()
                .Select(row => row[1].GetString()).ToArray());

        var k = Record(klee.Player);
        Assert.False(k.TryGetProperty("oath_by_turn", out _));
        Assert.False(k.TryGetProperty("oath_peak", out _));
        Assert.False(k.TryGetProperty("current_element_by_turn", out _));
        // The every-character keys are there, empty.
        Assert.Equal(0, k.GetProperty("cards_drawn_by_turn").GetArrayLength());
        Assert.Equal(0, k.GetProperty("energy_by_turn").GetArrayLength());
    }

    [Fact]
    public void A_swirl_is_credited_to_the_card_behind_it_and_still_to_swirl()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var enemy = Enemy();

        // The reaction named its card (an Attack's hit set it off).
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl",
                                 cause: "Converging Winds"))
        {
            Invoke("RecordDamage", enemy, 2, 0, null, null);
            Invoke("RecordDamage", enemy, 2, 0, null, null);
        }

        // No card on the reaction: the card the seat is resolving.
        Invoke("OpenPlayBlockForTest", varka.Player, "Gale Sweep");
        using (DamageCredit.Open(varka.Creature, DamageCredit.Element))
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
            Invoke("RecordDamage", enemy, 3, 0, null, null);
        Invoke("ClosePlayBlockForTest", varka.Player, "Gale Sweep",
               "Gale Sweep", 1, true, true);

        // Inside a Bomb's scope: the Bomb.
        using (DamageCredit.Open(varka.Creature, DamageCredit.Bomb, "Bomb"))
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
            Invoke("RecordDamage", enemy, 1, 0, null, null);

        // Nothing at all (a turn-start Swirl).
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
            Invoke("RecordDamage", enemy, 2, 0, null, null);

        // Another reaction is no Swirl's.
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Overload",
                                 cause: "Converging Winds"))
            Invoke("RecordDamage", enemy, 5, 0, null, null);

        var r = Record(varka.Player);
        var swirl = r.GetProperty("swirl_damage_by_card");
        Assert.Equal(4, swirl.GetProperty("Converging Winds").GetInt32());
        Assert.Equal(3, swirl.GetProperty("Gale Sweep").GetInt32());
        Assert.Equal(1, swirl.GetProperty("(Bomb)").GetInt32());
        Assert.Equal(2, swirl.GetProperty("(no card)").GetInt32());
        Assert.Equal(4, swirl.EnumerateObject().Count());
        // Back-compat: every Swirl point is still under "(Swirl)".
        Assert.Equal(10, r.GetProperty("damage_by_source")
                          .GetProperty("(Swirl)").GetInt32());
        Assert.Equal(5, r.GetProperty("damage_by_source")
                         .GetProperty("(Overload)").GetInt32());
    }

    [Fact]
    public void A_killing_swirl_is_credited_to_its_card()
    {
        var varka = Seat.Varka();
        Invoke("OpenSeatForTest", varka.Player, 1, 0);
        var enemy = Enemy(3);
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl",
                                 cause: "Converging Winds"))
            Invoke("NoteBeforeDamage", enemy, null, null);
        Invoke("RecordDeath", enemy);
        var r = Record(varka.Player);
        Assert.Equal(3, r.GetProperty("swirl_damage_by_card")
                         .GetProperty("Converging Winds").GetInt32());
    }

    [Fact]
    public void Full_house_triggers_ride_furina_s_record()
    {
        var furina = Seat.Furina(80).WithCombatState();
        var combat = DispatchProxy.Create<ICombatState,
            FurinaSpendAllPreviewWeakTests.ListenerProxy>();
        furina.Creature.CombatState = combat;
        Invoke("OpenSeatForTest", furina.Player, 1, 0);
        var ledger = FurinaStageLedger.For(furina.Creature);
        ledger.FullHouseTriggers = 3;
        Invoke("RecordTurnEnd", 1);
        Assert.Equal(3, Record(furina.Player)
                           .GetProperty("full_house_triggers").GetInt32());
        ledger.Clear();
        Assert.Equal(0, ledger.FullHouseTriggers);

        var klee = Seat.Klee();
        Invoke("OpenSeatForTest", klee.Player, 1, 0);
        Assert.False(Record(klee.Player)
                         .TryGetProperty("full_house_triggers", out _));
    }

    [Fact]
    public void The_director_counts_a_full_house_trigger_before_it_spends()
    {
        // The live path needs a stage; pin that the counter is bumped in
        // `FullHouse()` after its cap / fight-over gate, ahead of the Spend.
        var src = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "klee-mod", "KleeCode", "Powers", "Prototype",
            "FurinaStageDirector.cs"));
        var body = src.Substring(src.IndexOf("public async Task<int> FullHouse()",
                                             StringComparison.Ordinal));
        var gate = body.IndexOf("if (cap <= 0 || _board.Over) return 0;",
                                StringComparison.Ordinal);
        var bump = body.IndexOf("_stage.FullHouseTriggers++;",
                                StringComparison.Ordinal);
        var spend = body.IndexOf("SpendUpTo(", StringComparison.Ordinal);
        Assert.True(gate >= 0 && bump > gate && spend > bump);
    }

    [Fact]
    public void The_hooks_feed_the_new_columns()
    {
        var src = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "klee-mod", "KleeCode", "Diagnostics", "PlayTelemetry.cs"));
        Assert.Contains("PlayTelemetry.CardDrawn(card);", src);
        Assert.Contains("PlayTelemetry.EnergyTurnStart(player);", src);
        Assert.Contains("PlayTelemetry.EnergySpent(card, amount);", src);
        Assert.Contains("NoteOath(record, creature, round);", src);
        var effects = System.IO.File.ReadAllText(System.IO.Path.Combine(
            RepoRoot(), "klee-mod", "KleeCode", "Powers", "ReactionEffects.cs"));
        Assert.Contains("cause: cardSource != null", effects);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(
                   System.IO.Path.Combine(dir.FullName, "klee-mod", "KleeCode")))
        {
            dir = dir.Parent;
        }
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}
