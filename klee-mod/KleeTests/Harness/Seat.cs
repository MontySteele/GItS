using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Tests.Harness;

/// <summary>
/// One player seat, built out of REAL game objects.
///
/// WHY A FACTORY AND NOT A MOCK. The mod's per-seat logic is written against
/// <see cref="Creature"/>, <see cref="Player"/> and
/// <see cref="PlayerCombatState"/>; a mock of those would only ever prove the
/// mock's own arithmetic. Every object below is the shipped type.
///
/// WHY <see cref="RuntimeHelpers.GetUninitializedObject"/> FOR THE PLAYER.
/// Player's real constructor reaches <c>SaveManager.Instance</c>, which builds
/// a Godot Dictionary and takes the process down. So a Player is allocated and
/// the two fields the code under test reads are seeded directly:
/// <c>Character</c> (identity gating) and <c>_relics</c> (run-state relic
/// queries). Everything the mod actually reads off a Player in the tested
/// paths is one of those two plus <c>PlayerCombatState</c>. Any test that
/// needs a THIRD Player field is a test that has left the boundary -- see
/// README.md -- and should say so rather than seeding its way past it.
///
/// The Creature, by contrast, uses its REAL constructor
/// <c>Creature(Player, maxHp, hp)</c>, which initialises its power list and
/// its HP the way the game does.
/// </summary>
internal sealed class Seat
{
    internal Player Player { get; }

    internal Creature Creature { get; }

    private Seat(Player player, Creature creature)
    {
        Player = player;
        Creature = creature;
    }

    /// <summary>A Furina seat at the sheet's printed 60 max HP.</summary>
    internal static Seat Furina(int maxHp = 60) => Build(new global::KleeMod.Furina(), maxHp);

    internal static Seat Klee(int maxHp = 80) => Build(new global::KleeMod.Klee(), maxHp);

    internal static Seat Kokomi(int maxHp = 70) => Build(new global::KleeMod.Kokomi(), maxHp);

    private static Seat Build(CharacterModel character, int maxHp)
    {
        var player = (Player)RuntimeHelpers.GetUninitializedObject(typeof(Player));
        Set(player, "Character", character);
        SetField(player, "_relics", new List<RelicModel>());

        var ctor = typeof(Creature)
            .GetConstructors(HeadlessGame.All)
            .First(c => c.GetParameters().Length == 3
                        && c.GetParameters()[0].ParameterType == typeof(Player));
        var creature = (Creature)ctor.Invoke(new object[] { player, maxHp, maxHp });
        // The constructor sets Creature.Player but not the reverse link; in
        // game that is done by the combat setup this harness does not run, and
        // several predicates (SpotlightSystem.IsSpotlighted, the telemetry
        // writer) walk Player -> Creature.
        Force(player, "Creature", creature);

        return new Seat(player, creature);
    }

    /// <summary>Give this seat a per-combat resource table. Without it every
    /// resource accessor reads its `?? 0` fallback, which is itself worth
    /// testing (see the FanfareCap pins).</summary>
    internal Seat WithCombatState()
    {
        Set(Player, "PlayerCombatState",
            Activator.CreateInstance(typeof(PlayerCombatState), Player));
        return this;
    }

    /// <summary>Put a relic in THIS seat's run state. The relic model is
    /// allocated uninitialised: every relic query in the mod is an
    /// `is SomeRelic` type test, so identity is the whole payload, and a
    /// CustomRelicModel's constructor registers with BaseLib's model tables,
    /// which is state a test has no business mutating.</summary>
    internal Seat WithRelic<T>() where T : RelicModel
    {
        var relics = (List<RelicModel>)typeof(Player)
            .GetField("_relics", HeadlessGame.All)!
            .GetValue(Player)!;
        relics.Add((RelicModel)RuntimeHelpers.GetUninitializedObject(typeof(T)));
        return this;
    }

    internal Seat WithMaxHp(int maxHp)
    {
        Set(Creature, "MaxHp", maxHp);
        return this;
    }

    /// <summary>Put a power on THIS seat's creature at a given amount.
    ///
    /// The real path is PowerCmd.Apply, which needs a PlayerChoiceContext and
    /// a live combat -- outside the headless boundary. So the power is
    /// allocated uninitialised (a CustomPowerModel's constructor registers
    /// with BaseLib's model tables, which is state a test has no business
    /// mutating), its Owner and Amount are seeded, and it is pushed onto the
    /// creature's own `_powers` list -- the list every reader under test
    /// walks (Creature.Powers is a read-only view of it).
    ///
    /// What is bypassed is the APPLY pipeline: stacking rules, hooks, VFX. A
    /// test that needs any of those has left the boundary. What is exercised
    /// is the READ, which is what these pins are about.</summary>
    internal Seat WithPower<T>(int amount) where T : PowerModel
    {
        var power = (T)RuntimeHelpers.GetUninitializedObject(typeof(T));
        // The BACKING FIELDS, not the properties: PowerModel.Owner's setter
        // refuses to move a power between owners and its getter asserts
        // mutability, and Amount's setter routes through SetAmount, which
        // raises display events into objects this harness has no scene tree
        // for. IsMutable is set through its own setter -- the flag the
        // game's ToMutable would have set, and the one Owner's getter reads.
        SetField(power, "_owner", Creature);
        SetField(power, "_amount", amount);
        Set(power, "IsMutable", true);

        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(Creature)!;
        powers.Add(power);
        return this;
    }

    /// <summary>Move a power's Amount after the fact -- a bank going down.
    /// The real mover is PowerCmd.ModifyAmount, which needs a combat.</summary>
    internal Seat SetPowerAmount<T>(int amount) where T : PowerModel
    {
        var power = Creature.Powers.OfType<T>().First();
        SetField(power, "_amount", amount);
        return this;
    }

    /// <summary>Write a property's BACKING FIELD, skipping its setter.
    ///
    /// Needed for CardModel.Owner: the setter calls AbstractModel.AssertMutable,
    /// which refuses to mutate a canonical model, and the game's own escape
    /// hatch (ToMutable) resolves through ModelDb -- a registry that only the
    /// game's boot populates, so it is outside the headless boundary. The
    /// getter this feeds is the real one, and the guard being bypassed is about
    /// protecting the shared prototype, not about the value's meaning.</summary>
    internal static void Force(object target, string property, object value)
    {
        var candidates = new[]
        {
            $"<{property}>k__BackingField",
            "_" + char.ToLowerInvariant(property[0]) + property.Substring(1),
        };

        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var field = candidates
                .Select(name => t.GetField(name, HeadlessGame.All))
                .FirstOrDefault(f => f != null);
            if (field == null) continue;
            field.SetValue(target, value);
            return;
        }

        throw new InvalidOperationException(
            $"{target.GetType().Name}.{property} has no backing field -- the "
            + "game's shape changed under this harness.");
    }

    /// <summary>Set a property through its non-public setter, or through the
    /// compiler-generated backing field of a get-only auto-property.</summary>
    internal static void Set(object target, string property, object value)
    {
        var setter = target.GetType()
            .GetProperty(property, HeadlessGame.All)?.GetSetMethod(true);
        if (setter != null)
        {
            setter.Invoke(target, new[] { value });
            return;
        }

        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var field = t.GetField($"<{property}>k__BackingField", HeadlessGame.All);
            if (field == null) continue;
            field.SetValue(target, value);
            return;
        }

        throw new InvalidOperationException(
            $"{target.GetType().Name}.{property} has neither a setter nor a "
            + "backing field -- the game's shape changed under this harness.");
    }

    private static void SetField(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }

        throw new InvalidOperationException(
            $"{target.GetType().Name}.{field} is gone -- the game's shape "
            + "changed under this harness.");
    }
}
