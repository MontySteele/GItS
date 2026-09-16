using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-731` -- EVERY STARTING RELIC IS IN A POOL, ASKED HEADLESSLY.
///
/// THE DEFECT THIS EXISTS FOR. <c>RelicModel.Pool</c> is a non-virtual
/// <c>AllRelicPools.First(p =&gt; p.AllRelicIds.Contains(Id))</c> and THROWS
/// for a relic in no pool -- and that getter runs inside
/// <c>SelectCharacter</c>, which aborts mid-method, so the character looks
/// selected while the run starts as whoever was clicked before. The mod's own
/// check for it, <c>KleeSelfCheck</c> R7, runs AT GAME LAUNCH ONLY. So on
/// 2026-09-08 the Stage's Salon Solitaire shipped poolless through 1,465 green
/// C# tests and the first embark read back Ironclad (fixed in #469). The suite
/// could not see it. This is the seeing.
///
/// WHY IT IS STRUCTURAL. `ModelDb` is populated by the game's boot, so every
/// lookup throws `ModelNotFoundException` here (README, the headless
/// boundary): the pools cannot be BUILT in this process, and R7's own question
/// -- does `relic.Pool` resolve -- cannot be asked. What can be asked is the
/// thing that decides the answer: <c>StartingRelics</c> and the pool's
/// <c>GenerateAllRelics</c> both name their relics as
/// <c>ModelDb.Relic&lt;T&gt;()</c> call sites, so the two sets are readable
/// off the IL and comparable. A relic named by the first and not by the second
/// is exactly the crash, found at build time instead of at character select.
///
/// EVERY ARM AT ONCE, which is the other half of what the row asks. The walk
/// reads all the branches a body CONTAINS, not the one a flag would take, so a
/// build under <c>-p:PrototypeCards=true</c> checks the shipped starter and
/// each arm's replacement together -- and a build without it checks the
/// shipped branch, which is all the IL then holds.
///
/// THE SHARED POOL. A starting relic that is a BASE GAME type is pooled by
/// the borrowed <c>SilentRelicPool</c> that every one of these pools appends
/// to, so it is accepted without being named; only a relic this mod defines
/// has to appear in this mod's own pool body.
/// </summary>
public class StartingRelicPoolTests
{
    private static readonly Assembly Mod = typeof(global::KleeMod.Klee).Assembly;

    public static IEnumerable<object[]> Characters => new[]
    {
        new object[] { typeof(global::KleeMod.Klee) },
        new object[] { typeof(global::KleeMod.Furina) },
        new object[] { typeof(global::KleeMod.Kokomi) },
    };

    [Theory]
    [MemberData(nameof(Characters))]
    public void Every_starting_relic_is_in_the_characters_pool(Type character)
    {
        var starters = RelicsNamedBy(Getter(character, "StartingRelics"));
        Assert.True(starters.Count > 0,
            $"{character.Name}.StartingRelics names no relic at all -- either "
            + "the walk stopped seeing ModelDb.Relic<T> call sites, in which "
            + "case this test passes by reading nothing, or the character has "
            + "no starting relic, which SelectCharacter's unconditional "
            + "StartingRelics[0] does not survive (KleeSelfCheck R1).");

        var pool = PoolOf(character);
        var pooled = RelicsNamedBy(
            pool.GetMethod("GenerateAllRelics", HeadlessGame.All)!);
        Assert.True(pooled.Count > 0,
            $"{pool.Name}.GenerateAllRelics names no relic -- the same "
            + "read-nothing failure one side over.");

        foreach (var relic in starters)
        {
            // A base game relic is pooled by the borrowed SilentRelicPool
            // these pools all append to; it is not this mod's to name.
            if (Mod.GetTypes().All(t => t.Name != relic)) continue;

            Assert.True(pooled.Contains(relic),
                $"{character.Name}'s starting relic {relic} is named by no "
                + $"pool: {pool.Name}.GenerateAllRelics does not append it. "
                + "RelicModel.Pool throws for a poolless relic, inside "
                + "SelectCharacter -- the character will look selected and "
                + "the run will start as the previously clicked one "
                + "(EB-731; the Stage's Salon Solitaire, 2026-09-08).");
        }
    }

    /// <summary>The pool type the character's own <c>RelicPool</c> names.
    /// Read off the getter rather than passed in, so a character that is
    /// repointed at a different pool is checked against the NEW one.</summary>
    private static Type PoolOf(Type character)
    {
        foreach (var call in Il.CallSequence(Getter(character, "RelicPool")))
        {
            var (type, method, arg) = Split(call);
            if (type != "ModelDb" || method != "RelicPool" || arg is null)
                continue;
            return Mod.GetTypes().FirstOrDefault(t => t.Name == arg)
                ?? throw new InvalidOperationException(
                    $"{character.Name}.RelicPool names {arg}, which is not a "
                    + "type in klee.dll");
        }

        throw new InvalidOperationException(
            $"{character.Name}.RelicPool calls no ModelDb.RelicPool<T>() -- "
            + "the walk cannot find which pool to check against.");
    }

    /// <summary>
    /// Every <c>T</c> of every <c>ModelDb.Relic&lt;T&gt;()</c> this method
    /// reaches, following calls into the mod's own methods.
    ///
    /// The following is what makes the ARM branches and the helper bodies
    /// visible: Furina's getter delegates to <c>FurinaStageRoster</c>,
    /// Kokomi's to <c>KokomiOverhaulRoster</c>, and KokomiRelicPool keeps its
    /// shipped half in a private <c>Shipped()</c>. A walk that read one body
    /// would report a clean sheet over three of the six lists.
    /// </summary>
    private static HashSet<string> RelicsNamedBy(MethodBase method)
    {
        var found = new HashSet<string>(StringComparer.Ordinal);
        Walk(method, found, new HashSet<string>(StringComparer.Ordinal), 3);
        return found;
    }

    private static void Walk(MethodBase method, ISet<string> found,
                             ISet<string> seen, int depth)
    {
        foreach (var call in Il.CallSequence(method))
        {
            var (type, name, arg) = Split(call);
            if (type == "ModelDb" && name == "Relic" && arg is not null)
            {
                found.Add(arg);
                continue;
            }

            if (depth == 0 || !seen.Add(call)) continue;
            var owner = Mod.GetTypes().FirstOrDefault(t => t.Name == type);
            var next = owner?.GetMethod(name, HeadlessGame.All);
            if (next != null) Walk(next, found, seen, depth - 1);
        }
    }

    /// <summary>`Type.Method&lt;Arg&gt;` as `Il.CallSequence` spells it.</summary>
    private static (string Type, string Method, string? Arg) Split(string call)
    {
        var head = call;
        string? arg = null;
        var lt = call.IndexOf('<');
        if (lt >= 0)
        {
            head = call[..lt];
            arg = call[(lt + 1)..].TrimEnd('>');
            if (arg.Contains(',')) arg = null;   // not a one-argument generic
        }

        var dot = head.IndexOf('.');
        return dot < 0 ? (head, string.Empty, arg)
                       : (head[..dot], head[(dot + 1)..], arg);
    }

    private static MethodBase Getter(Type type, string property) =>
        type.GetProperty(property, HeadlessGame.All)?.GetMethod
        ?? throw new InvalidOperationException(
            $"{type.Name} has no {property} property");
}
