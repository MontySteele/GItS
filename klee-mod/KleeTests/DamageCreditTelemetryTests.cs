using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading.Tasks;
using KleeMod.Diagnostics;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// 2026-10-02 — THE PLAY TELEMETRY CREDITS EVERY KIND OF HIT TO ITS SEAT.
///
/// THE DEFECT (the Klee+Varka co-op fact-check). `PlayTelemetry.Damage`
/// credited a hit only when the engine named the seat's own creature as the
/// dealer, and every element hit, reaction, Bomb, Mine and pet hit reaches
/// the engine with `dealer: null` on purpose -- so credited damage covered 36%
/// of the enemies' HP plus Block, and the killing hit on every enemy (which
/// never reaches `AfterDamageReceived`) was nobody's.
///
/// THE BOUNDARY. The paths themselves (`ElementalHit.Deal`,
/// `ReactionEffects.Resolve`, `ProtoBombPower.Explode`, `KokomiPlan.Hit`,
/// `FurinaStage.Act`) need a live combat, which the headless suite cannot
/// build (README). So the suite pins two halves: the TELEMETRY's crediting,
/// driven directly through its hook-free seams under the same scopes those
/// paths open, and a STRUCTURAL pin that each path really opens its scope.
/// </summary>
public class DamageCreditTelemetryTests : IDisposable
{
    private static readonly Type Telemetry = typeof(PlayTelemetryHooks).Assembly
        .GetTypes().First(t => t.Name == "PlayTelemetry");

    public DamageCreditTelemetryTests()
    {
        // `Intent()` would otherwise read `intent.txt` under `user://`, a Godot
        // call the test host cannot make. Set-but-empty declares nothing.
        Environment.SetEnvironmentVariable("GITS_TELEMETRY_INTENT", "");
        Invoke("ResetForTest");
    }

    public void Dispose() => Invoke("ResetForTest");

    private static object? Invoke(string name, params object?[] args) =>
        Telemetry.GetMethod(name, HeadlessGame.All)!.Invoke(null, args);

    private static void Open(Seat seat, int seats, int index) =>
        Invoke("OpenSeatForTest", seat.Player, seats, index);

    private static void Hit(Creature target, int unblocked, int blocked = 0,
                            Creature? dealer = null) =>
        Invoke("RecordDamage", target, unblocked, blocked, dealer, null);

    private static JsonElement Record(Seat seat)
    {
        var json = (string?)Invoke("JsonForTest", seat.Player);
        Assert.NotNull(json);
        return JsonDocument.Parse(json!).RootElement.Clone();
    }

    private static int Kind(JsonElement record, string kind) =>
        record.GetProperty("damage_by_kind").TryGetProperty(kind, out var v)
            ? v.GetInt32() : 0;

    private static int Source(JsonElement record, string source) =>
        record.GetProperty("damage_by_source").TryGetProperty(source, out var v)
            ? v.GetInt32() : 0;

    /// <summary>An enemy: a creature with no player, built through the real
    /// constructor the harness seats use.</summary>
    private static Creature Enemy(int hp = 40)
    {
        var ctor = typeof(Creature).GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        return (Creature)ctor.Invoke(new object?[] { null, hp, hp });
    }

    /// <summary>A pet: an enemy-shaped creature whose `PetOwner` is the seat.</summary>
    private static Creature Pet(Seat owner)
    {
        var pet = Enemy(10);
        typeof(Creature).GetProperty("PetOwner")!.SetValue(pet, owner.Player);
        return pet;
    }

    [Fact]
    public void Each_kind_credits_the_seat_that_owns_it()
    {
        var klee = Seat.Klee();
        Open(klee, 1, 0);
        var enemy = Enemy();

        Hit(enemy, 6, dealer: klee.Creature);                         // a card
        using (DamageCredit.Open(klee.Creature, DamageCredit.Element))
            Hit(enemy, 4);                                            // element
        using (DamageCredit.Open(klee.Creature, DamageCredit.Reaction, "Overload"))
            Hit(enemy, 3);                                            // reaction
        using (DamageCredit.Open(klee.Creature, DamageCredit.Bomb, "Mine"))
            Hit(enemy, 7, blocked: 2);                                // bomb
        Hit(enemy, 5, dealer: Pet(klee));                             // pet dealer

        var r = Record(klee);
        Assert.Equal(6, Kind(r, DamageCredit.Direct));
        Assert.Equal(4, Kind(r, DamageCredit.Element));
        Assert.Equal(3, Kind(r, DamageCredit.Reaction));
        Assert.Equal(7, Kind(r, DamageCredit.Bomb));
        Assert.Equal(5, Kind(r, DamageCredit.Pet));
        Assert.Equal(25, r.GetProperty("damage_dealt").GetInt32());
        Assert.Equal(2, r.GetProperty("damage_blocked").GetInt32());
        Assert.Equal(3, Source(r, "(Overload)"));
        Assert.Equal(7, Source(r, "(Mine)"));
        Assert.Equal(6, Source(r, "(uncredited)"));
    }

    [Fact]
    public void Two_seats_each_get_their_own_hits()
    {
        var klee = Seat.Klee();
        var varka = Seat.Varka();
        Open(klee, 2, 0);
        Open(varka, 2, 1);
        var enemy = Enemy();

        using (DamageCredit.Open(klee.Creature, DamageCredit.Bomb, "Bomb"))
            Hit(enemy, 9);
        using (DamageCredit.Open(varka.Creature, DamageCredit.Element))
            Hit(enemy, 4);
        using (DamageCredit.Open(varka.Creature, DamageCredit.Reaction, "Swirl"))
            Hit(enemy, 2);
        Hit(enemy, 8, dealer: varka.Creature);

        var k = Record(klee);
        var v = Record(varka);
        Assert.Equal(9, k.GetProperty("damage_dealt").GetInt32());
        Assert.Equal(9, Kind(k, DamageCredit.Bomb));
        Assert.Equal(0, Kind(k, DamageCredit.Reaction));
        Assert.Equal(14, v.GetProperty("damage_dealt").GetInt32());
        Assert.Equal(4, Kind(v, DamageCredit.Element));
        Assert.Equal(2, Kind(v, DamageCredit.Reaction));
        Assert.Equal(8, Kind(v, DamageCredit.Direct));
        Assert.Equal(0, Kind(v, DamageCredit.Bomb));
    }

    [Fact]
    public void A_hit_with_no_dealer_and_no_scope_is_still_nobody_s()
    {
        // The old behaviour, kept where nothing names an owner: an enemy's
        // own Thorns-style hit, a relic with no seat.
        var klee = Seat.Klee();
        Open(klee, 1, 0);
        Hit(Enemy(), 5);
        Assert.Equal(0, Record(klee).GetProperty("damage_dealt").GetInt32());
    }

    [Fact]
    public void An_element_hit_inside_a_bomb_or_a_pet_keeps_the_outer_kind()
    {
        // `ElementalHit` opens its scope with `OpenIfNone`, so a Bomb's or a
        // Plan's hit through it stays a Bomb or a pet hit; a reaction opens
        // with `Open` and replaces it.
        var kokomi = Seat.Kokomi();
        Open(kokomi, 1, 0);
        var enemy = Enemy();
        using (DamageCredit.Open(kokomi.Creature, DamageCredit.Pet, "Bake-Kurage"))
        {
            using (DamageCredit.OpenIfNone(kokomi.Creature, DamageCredit.Element))
                Hit(enemy, 6);
            using (DamageCredit.Open(kokomi.Creature, DamageCredit.Reaction, "Frozen"))
                Hit(enemy, 2);
            Assert.Equal(DamageCredit.Pet, DamageCredit.Current!.Kind);
        }

        Assert.Null(DamageCredit.Current);
        var r = Record(kokomi);
        Assert.Equal(6, Kind(r, DamageCredit.Pet));
        Assert.Equal(6, Source(r, "(Bake-Kurage)"));
        Assert.Equal(2, Kind(r, DamageCredit.Reaction));
        Assert.Equal(0, Kind(r, DamageCredit.Element));
    }

    [Fact]
    public async Task A_scope_flows_through_an_await_and_never_back_to_the_caller()
    {
        var klee = Seat.Klee();
        Open(klee, 1, 0);
        var enemy = Enemy();

        async Task Explode()
        {
            using var credit = DamageCredit.Open(klee.Creature, DamageCredit.Bomb, "Bomb");
            await Task.Yield();
            Hit(enemy, 11);
        }

        await Explode();
        Assert.Null(DamageCredit.Current);
        Hit(enemy, 3);                       // after the scope: nobody's
        Assert.Equal(11, Kind(Record(klee), DamageCredit.Bomb));
        Assert.Equal(11, Record(klee).GetProperty("damage_dealt").GetInt32());
    }

    [Fact]
    public void The_killing_hit_is_credited_from_its_before_snapshot()
    {
        // `CreatureCmd.Damage` skips `AfterDamageReceived` for a creature the
        // hit killed; the snapshot from `BeforeDamageReceived` is filed when
        // the death arrives instead, for the HP the body had.
        var klee = Seat.Klee();
        var varka = Seat.Varka();
        Open(klee, 2, 0);
        Open(varka, 2, 1);
        var enemy = Enemy(13);

        using (DamageCredit.Open(klee.Creature, DamageCredit.Bomb, "Bomb"))
            Invoke("NoteBeforeDamage", enemy, null, null);
        Invoke("RecordDeath", enemy);

        var k = Record(klee);
        Assert.Equal(13, Kind(k, DamageCredit.Bomb));
        Assert.Equal(1, k.GetProperty("killing_blows").GetInt32());
        Assert.Equal(0, Record(varka).GetProperty("damage_dealt").GetInt32());

        // A hit that LANDED on a survivor spends its snapshot, so a later
        // death with nothing in flight files nothing.
        var other = Enemy(20);
        Invoke("NoteBeforeDamage", other, varka.Creature, null);
        Hit(other, 5, dealer: varka.Creature);
        Invoke("RecordDeath", other);
        var v = Record(varka);
        Assert.Equal(5, v.GetProperty("damage_dealt").GetInt32());
        Assert.Equal(0, v.GetProperty("killing_blows").GetInt32());
    }

    [Fact]
    public void Block_gained_is_logged_per_seat_per_round()
    {
        var klee = Seat.Klee();
        var varka = Seat.Varka();
        Open(klee, 2, 0);
        Open(varka, 2, 1);

        Invoke("RecordBlock", varka.Creature, 5, varka.Player, 1);
        Invoke("RecordBlock", varka.Creature, 3, varka.Player, 1);
        Invoke("RecordBlock", varka.Creature, 4, null, 2);
        Invoke("RecordBlock", klee.Creature, 6, varka.Player, 2);   // Varka's card, Klee's Block

        var v = Record(varka);
        var k = Record(klee);
        Assert.Equal("[[1,8],[2,4]]", v.GetProperty("block_gained_by_turn").GetRawText());
        Assert.Equal(12, v.GetProperty("block_gained").GetInt32());
        Assert.Equal(6, v.GetProperty("block_given").GetInt32());
        Assert.Equal("[[2,6]]", k.GetProperty("block_gained_by_turn").GetRawText());
        Assert.Equal(0, k.GetProperty("block_given").GetInt32());
    }

    /// <summary>2026-10-05: Block for EVERY character, the base game's
    /// included, and the Block a relic gave before the record opened (Anchor
    /// walks <c>BeforeCombatStart</c> ahead of the mod's listener).</summary>
    [Fact]
    public void Block_is_logged_for_a_base_character_including_block_from_before_the_record()
    {
        var ironclad = Seat.Of(new MegaCrit.Sts2.Core.Models.Characters.Ironclad());
        Open(ironclad, 1, 0);

        Invoke("SeedOpeningBlock", ironclad.Player, 10, 0);   // Anchor, round 0 at open
        Invoke("RecordBlock", ironclad.Creature, 5, ironclad.Player, 1);
        Invoke("RecordBlock", ironclad.Creature, 8, ironclad.Player, 3);
        Invoke("SeedOpeningBlock", ironclad.Player, 0, 1);    // nothing standing: no row

        var r = Record(ironclad);
        Assert.Equal("[[1,15],[3,8]]", r.GetProperty("block_gained_by_turn").GetRawText());
        Assert.Equal(23, r.GetProperty("block_gained").GetInt32());
        Assert.Contains("PlayTelemetry.SeedOpeningBlock",
            Il.Calls(Il.Method("PlayTelemetry", "OpenFight")));
    }

    [Fact]
    public void The_prototype_bomb_counts_its_detonations_per_seat()
    {
        // The counter `PlayTelemetry.SampleDetonations` now reads beside the
        // old Bomb's: per combat, per placer, Mines counted beside the total.
        var combat = RuntimeHelpers.GetUninitializedObject(typeof(CombatState));
        var klee = Seat.Klee();
        var other = Seat.Klee();
        ProtoBombPower.RecordExplosion(combat, klee.Player, isMine: false);
        ProtoBombPower.RecordExplosion(combat, klee.Player, isMine: true);
        ProtoBombPower.RecordExplosion(combat, other.Player, isMine: true);

        var state = (ICombatState)combat;
        Assert.Equal(2, ProtoBombPower.ExplosionsThisCombat(state, klee.Player));
        Assert.Equal(1, ProtoBombPower.MineExplosionsThisCombat(state, klee.Player));
        Assert.Equal(1, ProtoBombPower.ExplosionsThisCombat(state, other.Player));

        var next = (ICombatState)RuntimeHelpers.GetUninitializedObject(typeof(CombatState));
        Assert.Equal(0, ProtoBombPower.ExplosionsThisCombat(next, klee.Player));

        var sample = Il.Calls(Il.Method("PlayTelemetry", "SampleDetonations"));
        Assert.Contains("ProtoBombPower.ExplosionsThisCombat", sample);
        Assert.Contains("ProtoBombPower.MineExplosionsThisCombat", sample);
        Assert.Contains("ProtoBombPower.RecordExplosion",
                        Il.Calls(Il.Method("ProtoBombPower", "Explode")));
    }

    /// <summary>STRUCTURAL: each dealer-less path opens the scope that names
    /// its seat. Deleting one would silently send that kind back to nobody.
    /// </summary>
    [Theory]
    [InlineData("ElementalHit", "Deal", "DamageCredit.OpenIfNone")]
    [InlineData("ElementalHit", "DealAsIfAura", "DamageCredit.OpenIfNone")]
    [InlineData("ElementalHit", "DealUnelemented", "DamageCredit.OpenIfNone")]
    [InlineData("ReactionEffects", "Resolve", "DamageCredit.Open")]
    [InlineData("FrozenPower", "AfterDamageReceived", "DamageCredit.Open")]
    [InlineData("ProtoBombPower", "Explode", "DamageCredit.Open")]
    [InlineData("BombEchoPower", "Fire", "DamageCredit.Open")]
    [InlineData("BombPower", "ResolvePayload", "DamageCredit.Open")]
    [InlineData("KokomiPlan", "Hit", "DamageCredit.Open")]
    [InlineData("GameStageBoard", "Damage", "DamageCredit.Open")]
    public void Each_dealerless_path_opens_its_credit_scope(
        string type, string method, string call)
    {
        Assert.Contains(call, Il.Calls(Il.Method(type, method)));
    }

    [Fact]
    public void The_hooks_feed_the_kill_snapshot_and_the_block_log()
    {
        Assert.Contains("PlayTelemetry.NoteBeforeDamage",
            Il.Calls(Il.Method("PlayTelemetryHooks", "BeforeDamageReceived")));
        Assert.Contains("PlayTelemetry.RecordDeath",
            Il.Calls(Il.Method("PlayTelemetryHooks", "AfterDeath")));
        Assert.Contains("PlayTelemetry.BlockGained",
            Il.Calls(Il.Method("PlayTelemetryHooks", "AfterBlockGained")));
    }

    /// <summary>2026-10-05: Strength at each turn end, for a base character
    /// and a kit character alike, 0 with none, and its own row per turn.
    /// </summary>
    [Fact]
    public void Strength_is_logged_by_turn_for_base_and_kit_characters()
    {
        var ironclad = Seat.Of(new MegaCrit.Sts2.Core.Models.Characters.Ironclad())
            .WithPower<StrengthPower>(2);
        var klee = Seat.Klee();
        Open(ironclad, 2, 0);
        Open(klee, 2, 1);

        Invoke("RecordTurnEnd", 1);
        ironclad.SetPowerAmount<StrengthPower>(5);
        Invoke("RecordTurnEnd", 2);

        Assert.Equal("[[1,2],[2,5]]",
            Record(ironclad).GetProperty("strength_by_turn").GetRawText());
        Assert.Equal("[[1,0],[2,0]]",
            Record(klee).GetProperty("strength_by_turn").GetRawText());
        Assert.Contains("PlayTelemetry.RecordTurnEnd",
            Il.Calls(Il.Method("PlayTelemetry", "CloseTurn")));
    }

    /// <summary>A combat that answers only `Enemies`, enough for the two
    /// pool readers.</summary>
    public class CombatProxy : DispatchProxy
    {
        public System.Collections.Generic.IReadOnlyList<Creature> Enemies = Array.Empty<Creature>();

        protected override object? Invoke(MethodInfo? m, object?[]? args)
        {
            if (m!.Name == "get_Enemies") return Enemies;
            throw new NotSupportedException(m.Name);
        }
    }

    /// <summary>2026-10-05: `enemy_hp_by_turn` is the pool without Block.</summary>
    [Fact]
    public void Enemy_hp_field_counts_hp_only_where_the_pool_counts_block_too()
    {
        var a = Enemy(30);
        var b = Enemy(20);
        Seat.Force(a, "Block", 8);
        var combat = DispatchProxy.Create<MegaCrit.Sts2.Core.Combat.ICombatState, CombatProxy>();
        ((CombatProxy)(object)combat).Enemies = new[] { a, b };

        Assert.Equal(58, (int)Invoke("EnemyPool", combat)!);
        Assert.Equal(50, (int)Invoke("EnemyHp", combat)!);
        Assert.Contains("PlayTelemetry.EnemyHp",
            Il.Calls(Il.Method("PlayTelemetry", "OpenTurn")));
        var klee = Seat.Klee();
        Open(klee, 1, 0);
        Assert.Equal("[]", Record(klee).GetProperty("enemy_hp_by_turn").GetRawText());
    }

    /// <summary>The fight's line, as written to the log, read back. The log
    /// path is pointed at a temp file so no Godot path is resolved.</summary>
    private static string[] WrittenLines(Action act)
    {
        var field = Telemetry.GetField("_path", HeadlessGame.All)!;
        var saved = field.GetValue(null);
        var path = Path.Combine(Path.GetTempPath(),
            $"gits-telemetry-test-{Guid.NewGuid():N}.jsonl");
        field.SetValue(null, path);
        try
        {
            act();
            return File.Exists(path) ? File.ReadAllLines(path) : Array.Empty<string>();
        }
        finally
        {
            field.SetValue(null, saved);
            if (File.Exists(path)) File.Delete(path);
        }
    }

    private static void Die(Seat seat) => Seat.Force(seat.Creature, "CurrentHp", 0);

    /// <summary>2026-10-05 — THE FATAL FIGHT IS WRITTEN. A fight the player
    /// died in wrote no line (Klee suite 1, two act-1 boss deaths). The seat's
    /// death now closes it: once, as `died`, HP at 0, turn rows kept.</summary>
    [Fact]
    public void A_fight_the_player_dies_in_is_written_once_as_died()
    {
        var klee = Seat.Klee();
        Open(klee, 1, 0);
        var enemy = Enemy();

        var lines = WrittenLines(() =>
        {
            Invoke("RecordTurnEnd", 1);
            Hit(enemy, 6, dealer: klee.Creature);
            Die(klee);
            Invoke("CloseOnSeatDeath", klee.Creature, true);
            Invoke("CloseOnSeatDeath", klee.Creature, true);   // a second call writes nothing
        });

        var row = Assert.Single(lines);
        var r = JsonDocument.Parse(row).RootElement;
        Assert.Equal("fight", r.GetProperty("record").GetString());
        Assert.Equal("died", r.GetProperty("outcome").GetString());
        Assert.Equal(0, r.GetProperty("hp_end").GetInt32());
        Assert.Equal(6, Kind(r, DamageCredit.Direct));
        Assert.Equal("[[1,0]]", r.GetProperty("strength_by_turn").GetRawText());
        Assert.Null(Invoke("JsonForTest", klee.Player));
    }

    /// <summary>In co-op the fight goes on while a seat stands: the first
    /// death writes nothing, the last writes both seats, both `died`.</summary>
    [Fact]
    public void In_coop_the_fight_is_written_when_the_last_seat_dies()
    {
        var klee = Seat.Klee();
        var varka = Seat.Varka();
        Open(klee, 2, 0);
        Open(varka, 2, 1);

        var lines = WrittenLines(() =>
        {
            Die(klee);
            Invoke("CloseOnSeatDeath", klee.Creature, true);
            Assert.NotNull(Invoke("JsonForTest", klee.Player));   // still open
            Die(varka);
            Invoke("CloseOnSeatDeath", varka.Creature, true);
        });

        Assert.Equal(2, lines.Length);
        Assert.All(lines, l => Assert.Equal("died",
            JsonDocument.Parse(l).RootElement.GetProperty("outcome").GetString()));
    }

    [Fact]
    public void The_death_hook_closes_the_fatal_fight()
    {
        Assert.Contains("PlayTelemetry.SeatDied",
            Il.Calls(Il.Method("PlayTelemetryHooks", "AfterDeath")));
        Assert.Contains("PlayTelemetry.CloseOnSeatDeath",
            Il.Calls(Il.Method("PlayTelemetry", "SeatDied")));
    }
}
