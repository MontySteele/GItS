using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE DROP OF HELICAL DART AND SNECKO SKULL, PINNED.
///
/// [USER] ruled QUEUE pick `fanout-picks-2026-09-16 4.3` at its default on
/// 2026-09-16: the two misleading inherited Silent relics leave all three
/// pools (Klee, Kokomi, Furina) and every other inherited relic and potion
/// stays. The census the ruling reads is
/// `review/active/inherited-potions-relics-census-2026-09-16.md`.
///
/// WHAT CAN AND CANNOT BE ASKED HERE. `ModelDb` is populated by the game's
/// boot, so no pool can be BUILT in this process (README, the headless
/// boundary) and `AllRelics` cannot be read. What can be read is the thing
/// that decides the answer: the source roster and the three pool bodies are
/// `ModelDb.Relic&lt;T&gt;()` and `ModelDb.RelicPool&lt;T&gt;()` call sites in
/// IL, and <see cref="InheritedSilentRelics.Dropped"/> is a static field of
/// `typeof` tokens that needs nothing at all. So this pins the CALL SITES and
/// the FILTER; `KleeSelfCheck` R21 pins the RESULT at boot, against the pools
/// the game actually built. The two together are the drop.
/// </summary>
public class InheritedSilentRelicsTests
{
    private static readonly Assembly Mod = typeof(global::KleeMod.Klee).Assembly;

    public static IEnumerable<object[]> Pools => new[]
    {
        new object[] { typeof(global::KleeMod.KleeRelicPool) },
        new object[] { typeof(global::KleeMod.KokomiRelicPool) },
        new object[] { typeof(global::KleeMod.FurinaRelicPool) },
    };

    /// <summary>
    /// The ruling named TWO relics. Not one, not three, and not two others.
    /// </summary>
    [Fact]
    public void The_drop_list_is_exactly_the_two_relics_the_ruling_named()
    {
        Assert.Equal(
            new[] { "HelicalDart", "SneckoSkull" },
            InheritedSilentRelics.Dropped.Select(t => t.Name).OrderBy(n => n).ToArray());

        // Base game types, not mod types -- a mod type of the same name would
        // filter nothing out of the borrowed roster and this pin would be
        // reading its own reflection.
        foreach (var dropped in InheritedSilentRelics.Dropped)
        {
            Assert.NotEqual(Mod, dropped.Assembly);
            Assert.Equal("MegaCrit.Sts2.Core.Models.Relics", dropped.Namespace);
        }
    }

    /// <summary>
    /// THE COUNT MOVED BY EXACTLY TWO, read off the SHIPPED roster rather than
    /// off the census's prose. `SilentRelicPool.GenerateAllRelics` names its
    /// members as `ModelDb.Relic&lt;T&gt;()` call sites, so the source roster
    /// is readable here without building anything, and the filter is applied
    /// to it type by type.
    /// </summary>
    [Fact]
    public void The_filter_drops_two_of_the_borrowed_roster_and_keeps_the_rest()
    {
        var roster = BorrowedRoster();
        Assert.True(roster.Count >= 8,
            $"read only {roster.Count} relic(s) off SilentRelicPool."
            + "GenerateAllRelics; the census counted 8 off the shipped DLL. "
            + "Either the game patch changed how that pool is built -- in "
            + "which case this walk reads nothing and would pass vacuously -- "
            + "or the roster genuinely shrank. Re-read the pool before "
            + "relaxing this.");

        var dropped = roster.Where(t => !InheritedSilentRelics.IsKept(Uninitialized(t)))
                            .Select(t => t.Name)
                            .OrderBy(n => n)
                            .ToArray();
        Assert.Equal(new[] { "HelicalDart", "SneckoSkull" }, dropped);

        // Said as a count as well as a membership, because that is the half of
        // the ruling that says everything unnamed STAYS.
        var kept = roster.Count(t => InheritedSilentRelics.IsKept(Uninitialized(t)));
        Assert.Equal(roster.Count - 2, kept);
    }

    /// <summary>
    /// EVERY POOL GOES THROUGH THE CURATION, and none reads the uncurated
    /// roster beside it. This is what makes the drop true of all three rather
    /// than of the two that happened to be edited.
    /// </summary>
    [Theory]
    [MemberData(nameof(Pools))]
    public void Each_pool_inherits_the_curated_roster_only(Type pool)
    {
        var calls = Reachable(
            pool.GetMethod("GenerateAllRelics", HeadlessGame.All)!);

        Assert.True(calls.Contains("InheritedSilentRelics.Curated"),
            $"{pool.Name}.GenerateAllRelics does not reach "
            + "InheritedSilentRelics.Curated(), so whatever it inherits is "
            + "uncurated: Helical Dart and Snecko Skull are back in this "
            + "character's reward rolls (the ruling on QUEUE pick "
            + "`fanout-picks-2026-09-16 4.3`).");

        // And reaches the uncurated roster ONLY through it: the walk below
        // stops at `InheritedSilentRelics`, so this call site could only be
        // the pool's own second, uncurated door.
        Assert.DoesNotContain("ModelDb.RelicPool<SilentRelicPool>", calls);
    }

    /// <summary>
    /// AND NOWHERE ELSE IN THE MOD, which is the same statement made once for
    /// the whole assembly: `InheritedSilentRelics` is the only door to the
    /// borrowed roster, so a FOURTH pool added later cannot quietly inherit
    /// the uncurated eight by copying the line the three used to have.
    /// </summary>
    [Fact]
    public void Only_the_curation_reads_the_borrowed_roster()
    {
        // The two methods that read the uncurated roster ON PURPOSE: the
        // curation itself, which filters it, and KleeSelfCheck's R21, which
        // compares the built pool against it and would have nothing to
        // compare against otherwise.
        var allowed = new HashSet<string>(StringComparer.Ordinal)
        {
            "InheritedSilentRelics.Curated",
            "KleeSelfCheck.CheckInheritedRelicCuration",
        };

        var offenders = new List<string>();
        foreach (var type in Mod.GetTypes())
        {
            foreach (var method in type.GetMethods(HeadlessGame.All))
            {
                if (method.DeclaringType != type) continue;
                var name = $"{type.Name}.{method.Name}";
                if (allowed.Contains(name)) continue;
                if (Il.CallSequence(method)
                      .Contains("ModelDb.RelicPool<SilentRelicPool>"))
                {
                    offenders.Add(name);
                }
            }
        }

        Assert.True(offenders.Count == 0,
            "these read ModelDb.RelicPool<SilentRelicPool>() directly instead "
            + "of InheritedSilentRelics.Curated(), so they inherit the "
            + "uncurated roster: " + string.Join(", ", offenders));
    }

    // -----------------------------------------------------------------------

    /// <summary>
    /// The relic TYPES the shipped `SilentRelicPool` names, read off its IL.
    /// </summary>
    private static IReadOnlyList<Type> BorrowedRoster()
    {
        var pool = typeof(SilentRelicPool);
        var body = pool.GetMethod("GenerateAllRelics", HeadlessGame.All)
            ?? throw new InvalidOperationException(
                "SilentRelicPool has no GenerateAllRelics");

        var found = new List<Type>();
        foreach (var call in Il.CallSequence(body))
        {
            var lt = call.IndexOf('<');
            if (lt < 0 || !call[..lt].EndsWith("ModelDb.Relic", StringComparison.Ordinal))
                continue;
            var arg = call[(lt + 1)..].TrimEnd('>');
            if (arg.Contains(',')) continue;
            var type = pool.Assembly.GetTypes()
                .FirstOrDefault(t => t.Name == arg && typeof(RelicModel).IsAssignableFrom(t));
            if (type != null && !found.Contains(type)) found.Add(type);
        }

        return found;
    }

    /// <summary>
    /// An instance of a relic type WITHOUT running its constructor. The
    /// filter is a type test, so an uninitialized object answers it exactly;
    /// constructing a real `RelicModel` reaches `ModelDb` and the loc tables,
    /// which is over the headless boundary.
    /// </summary>
    private static RelicModel Uninitialized(Type relic) =>
        (RelicModel)RuntimeHelpers.GetUninitializedObject(relic);

    /// <summary>
    /// Every `Type.Method` this method reaches, following calls into the mod's
    /// own methods -- KokomiRelicPool keeps its shipped half in a private
    /// `Shipped()`, so a walk of one body would report a clean sheet over it.
    /// </summary>
    private static HashSet<string> Reachable(MethodBase method)
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
            found.Add(call);
            var head = call;
            var lt = call.IndexOf('<');
            if (lt >= 0) head = call[..lt];
            // The generic-free spelling too, so a caller can ask for
            // `Type.Method` without knowing the type argument.
            found.Add(head);

            var dot = head.IndexOf('.');
            if (dot < 0 || depth == 0 || !seen.Add(call)) continue;
            // THE WALK STOPS AT THE CURATION. Curated() necessarily reads
            // ModelDb.RelicPool<SilentRelicPool>() -- it is the thing being
            // filtered -- so a walk that descended into it would report that
            // call site for every caller and the assertion above would be
            // unsatisfiable by any pool at all.
            if (head[..dot] == nameof(InheritedSilentRelics)) continue;
            var owner = Mod.GetTypes().FirstOrDefault(t => t.Name == head[..dot]);
            var next = owner?.GetMethod(head[(dot + 1)..], HeadlessGame.All);
            if (next != null) Walk(next, found, seen, depth - 1);
        }
    }
}

