using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Teyvat;
using KleeMod.Teyvat.Acts;
using KleeMod.Teyvat.Events.Mirrors;
using KleeMod.Teyvat.Patches;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Acts;
using MegaCrit.Sts2.Core.Models.Events;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE TEYVAT RUN FRAME ARM's pins (spike item 4.1-4.4).
///
/// WHAT A HEADLESS SUITE CAN AND CANNOT SAY HERE, stated first because it
/// bounds every assertion below. `ModelDb` is outside the headless boundary --
/// it is populated only by the game's boot, and `AllAbstractModelSubtypes`
/// reaches `ReflectionHelper.GetSubtypesInMods`, which THROWS before
/// `ModManager` has initialised. So no test in this file can call
/// `ModelDb.Acts`, construct an `ActModel`, or compare two encounter lists by
/// reference: the objects do not exist outside the game.
///
/// What it CAN do is two things, and both are real.
///
/// First, the arm's decisions are written as pure functions over TYPES and
/// TABLES -- `ModelDb_Acts_TeyvatDressings_Patch.Plan`, `TeyvatFrame`'s four
/// dictionaries -- and those can be exercised directly, with the flag moved
/// both ways in one build.
///
/// Second, the DELEGATION can be pinned structurally through `Harness/Il`:
/// reading `Mondstadt.GenerateAllEncounters`'s call set proves it reaches the
/// base act's `AllEncounters` and constructs nothing, which is the property
/// "reference-equal to the base zone's" reduced to what a compiler can be
/// asked. A deploy still has to prove the references really are equal at
/// runtime; that is in the spike's report as such.
/// </summary>
public class TeyvatFrameTests : IDisposable
{
    /// <summary>
    /// The flag is a settable static, so every test that moves it restores it.
    /// xUnit constructs a fresh instance per test and `Dispose` runs after
    /// each, which is the same discipline the arm suites already use.
    /// </summary>
    private readonly bool _enabled = TeyvatFrame.Enabled;

    public void Dispose()
    {
        TeyvatFrame.Enabled = _enabled;
        // EB-758's pins move `TeyvatMusic`'s three probes and populate its
        // per-directory cache. Both are process-wide statics, so both are put
        // back HERE rather than in the tests that moved them: a pin that
        // leaked a fake probe would hand the next test a lookup answering out
        // of a table that is not the engine's.
        TeyvatMusic.ResetProbes();
        TeyvatMusic.ClearCache();
    }

    // ---------------------------------------------------------------
    // The acceptance condition the whole quarantine rests on.
    // ---------------------------------------------------------------

    /// <summary>
    /// SKIPPED, NOT FAILED, under `-p:TeyvatFrame=true`, on
    /// `operations/prototype.md`'s rule and for its reason: under the property
    /// this pin cannot say anything true -- green would mean the property did
    /// nothing, and red is the property working. A red that means "the switch
    /// works" teaches everyone to ignore reds.
    /// </summary>
#if !TEYVAT_FRAME
    [Fact]
    public void The_arm_ships_off()
    {
        Assert.False(TeyvatFrame.DefaultEnabled);
    }
#endif

    // ---------------------------------------------------------------
    // Item 4.1: the act list, both ways.
    // ---------------------------------------------------------------

    /// <summary>The base game's four, in `ModelDb.Acts`'s own order
    /// (`Models/ModelDb.cs:299`).</summary>
    private static readonly IReadOnlyList<Type> BaseActs = new[]
    {
        typeof(Overgrowth), typeof(Underdocks), typeof(Hive), typeof(Glory),
    };

    [Fact]
    public void With_the_arm_off_the_act_list_is_the_base_four_unchanged()
    {
        TeyvatFrame.Enabled = false;

        Assert.Equal(BaseActs, ModelDb_Acts_TeyvatDressings_Patch.Plan(BaseActs));
    }

    /// <summary>
    /// THE SIX-ACT SHAPE, which is the whole of R273's engineering.
    ///
    /// The base game ships TWO zones at index 0 and exactly ONE at each of
    /// index 1 and 2. So act 1's dressings are a one-for-one swap that leaves
    /// the bucket size alone, while acts 2 and 3 each replace their single
    /// base act with a PAIR of faces on the same zone
    /// (`review/ruled/teyvat-nation-mapping-2026-09-14.md` sec.1). Four acts
    /// in, six out, two per index, and no base zone reachable with the arm on.
    /// </summary>
    [Fact]
    public void With_the_arm_on_every_base_zone_is_replaced_by_its_faces()
    {
        TeyvatFrame.Enabled = true;

        var planned = ModelDb_Acts_TeyvatDressings_Patch.Plan(BaseActs);

        Assert.Equal(6, planned.Count);
        Assert.Equal(
            new[]
            {
                typeof(Mondstadt), typeof(Liyue),
                typeof(Natlan), typeof(Inazuma),
                typeof(Fontaine), typeof(Sumeru),
            },
            planned);

        // Not a single base zone survives: appending a face beside the zone it
        // dresses would put the same zone in its own coin twice.
        foreach (var baseAct in BaseActs)
        {
            Assert.DoesNotContain(baseAct, planned);
        }
    }

    /// <summary>
    /// TWO CANDIDATES AT EVERY INDEX, expressed over the swap table rather
    /// than over the planned list, because `Plan` deals in types and
    /// `ActsByIndex` is the game's own derivation from `Acts` that no headless
    /// process can build.
    ///
    /// `ActModel.GetRandomList` (`ActModel.cs:551-578`) calls `rng.NextItem`
    /// ONCE per index bucket whatever the bucket holds -- the loop is over
    /// `actsByIndex` and not over candidates -- so three draws before and
    /// three after, and a two-element bucket is a coin.
    /// </summary>
    [Fact]
    public void Each_act_index_ends_up_with_exactly_two_faces()
    {
        var byBase = ModelDb_Acts_TeyvatDressings_Patch.Swaps
            .ToDictionary(s => s.BaseAct, s => s.Dressings.Count);

        // Act 1: two base zones, one face each.
        Assert.Equal(1, byBase[typeof(Overgrowth)]);
        Assert.Equal(1, byBase[typeof(Underdocks)]);

        // Acts 2 and 3: one base zone, two faces each.
        Assert.Equal(2, byBase[typeof(Hive)]);
        Assert.Equal(2, byBase[typeof(Glory)]);

        // Every face appears exactly once across the whole table.
        var faces = ModelDb_Acts_TeyvatDressings_Patch.Swaps
            .SelectMany(s => s.Dressings).ToList();
        Assert.Equal(6, faces.Count);
        Assert.Equal(6, faces.Distinct().Count());
    }

    /// <summary>
    /// EQUAL EVENT COUNTS AT EVERY INDEX, BY IDENTITY, which is the hard rule
    /// the whole arm rests on (`review/records/teyvat-spike-zone-read-2026-09-14.md`
    /// sec.6). `ActModel.GenerateRooms` shuffles `AllEvents.Concat(
    /// AllSharedEvents)` on the run's `UpFront` rng at run start, so two faces
    /// at one index whose pools differed in LENGTH would consume different
    /// numbers of draws and move every later roll -- bosses, Ancients,
    /// encounter order.
    ///
    /// The pin is stronger than a count comparison and cheaper: each face's
    /// private `Base` property is typed as the zone it dresses, so proving
    /// both faces at an index name the SAME base type proves they return the
    /// same list object, and one list has one count. The delegation itself is
    /// pinned above, through `Il`, for each of the six.
    /// </summary>
    [Fact]
    public void Both_faces_at_an_index_dress_the_same_base_zone()
    {
        foreach (var (baseAct, dressings, _) in ModelDb_Acts_TeyvatDressings_Patch.Swaps)
        {
            foreach (var dressing in dressings)
            {
                var basis = dressing.GetProperty(
                    "Base", BindingFlags.NonPublic | BindingFlags.Static);

                Assert.NotNull(basis);
                Assert.Equal(baseAct, basis!.PropertyType);
            }
        }
    }

    /// <summary>
    /// EVERY FACE IS IN THE DRESSING REGISTRY, and its fallback points at the
    /// zone it actually dresses.
    ///
    /// `TeyvatFrame.AssetAlias` is both the alias table and the registry
    /// `TeyvatFrame.IsDressing` answers from, so a face published as an act
    /// but missing here would be named by its loc row and then silently
    /// unable to carry a monster name or an event substitution. The alias
    /// value is the base zone's own `FilePathIdentifier` -- `Id.Entry`
    /// lowercased, which for every base act is its class name lowercased --
    /// so a face whose placeholder set has not reached the pck borrows the
    /// right zone's art rather than some other act's.
    /// </summary>
    [Fact]
    public void Every_face_is_registered_and_falls_back_to_its_own_base_zone()
    {
        foreach (var (baseAct, dressings, _) in ModelDb_Acts_TeyvatDressings_Patch.Swaps)
        {
            foreach (var dressing in dressings)
            {
                var entry = dressing.Name.ToUpperInvariant();

                Assert.True(TeyvatFrame.IsDressing(entry), entry);
                Assert.Equal(baseAct.Name.ToLowerInvariant(), TeyvatFrame.AssetAlias[entry]);
            }
        }
    }

    [Fact]
    public void A_base_act_the_postfix_cannot_find_is_left_alone_not_spliced_around()
    {
        TeyvatFrame.Enabled = true;

        // A game patch that removed Underdocks, or a second mod that already
        // replaced it. Splicing Liyue in here would make act 1 a three-way
        // roll against a zone that is no longer the one it dresses.
        var without = new[] { typeof(Overgrowth), typeof(Hive), typeof(Glory) };
        var planned = ModelDb_Acts_TeyvatDressings_Patch.Plan(without);

        // Mondstadt (1 for 1), then the Hive's two and Glory's two.
        Assert.Equal(5, planned.Count);
        Assert.DoesNotContain(typeof(Liyue), planned);
        Assert.Contains(typeof(Mondstadt), planned);
        Assert.Contains(typeof(Natlan), planned);
        Assert.Contains(typeof(Sumeru), planned);
    }

    // ---------------------------------------------------------------
    // Item 4.1: the delegation, structurally.
    // ---------------------------------------------------------------

    [Theory]
    [InlineData(typeof(Mondstadt))]
    [InlineData(typeof(Liyue))]
    [InlineData(typeof(Natlan))]
    [InlineData(typeof(Inazuma))]
    [InlineData(typeof(Fontaine))]
    [InlineData(typeof(Sumeru))]
    public void A_dressings_encounter_table_is_the_base_zones_own_object(Type dressing)
    {
        var calls = Il.Calls(Method(dressing, nameof(ActModel.GenerateAllEncounters)));

        // The dressing's own `Base` property (which is `ModelDb.Act<T>()`,
        // pinned below) and then the base act's CACHED `AllEncounters`, which
        // is what makes the result the same object rather than an equal one.
        // If this method ever grew an encounter list of its own it would have
        // to call `ModelDb.Encounter`, and that is not here.
        Assert.Contains(dressing.Name + ".get_Base", calls);
        Assert.Contains("ActModel.get_AllEncounters", calls);
        Assert.DoesNotContain("ModelDb.Encounter", calls);
        Assert.Contains("ModelDb.Act", Il.Calls(Getter(dressing, "Base")));
    }

    [Theory]
    [InlineData(typeof(Mondstadt))]
    [InlineData(typeof(Liyue))]
    [InlineData(typeof(Natlan))]
    [InlineData(typeof(Inazuma))]
    [InlineData(typeof(Fontaine))]
    [InlineData(typeof(Sumeru))]
    public void A_dressings_event_pool_is_the_base_zones_own_list(Type dressing)
    {
        // EQUAL COUNTS ARE A HARD RULE (the read's sec.6): `GenerateRooms`
        // shuffles `AllEvents.Concat(AllSharedEvents)` on the run's `UpFront`
        // rng at run start, so a pool of a different LENGTH moves every later
        // roll on that rng -- bosses, Ancients, encounter order, and with them
        // the Klee calibration seed's whole map.
        //
        // Delegating makes the counts equal by IDENTITY rather than by
        // arithmetic, which is a stronger statement than any count assertion
        // could make headlessly: there is one list, so there is one count.
        var calls = Il.Calls(Getter(dressing, nameof(ActModel.AllEvents)));

        Assert.Contains(dressing.Name + ".get_Base", calls);
        Assert.Contains("ActModel.get_AllEvents", calls);
        Assert.DoesNotContain("ModelDb.Event", calls);
    }

    [Theory]
    [InlineData(typeof(Mondstadt))]
    [InlineData(typeof(Liyue))]
    [InlineData(typeof(Natlan))]
    [InlineData(typeof(Inazuma))]
    [InlineData(typeof(Fontaine))]
    [InlineData(typeof(Sumeru))]
    public void A_dressings_ancient_pool_is_the_base_zones_own(Type dressing)
    {
        var calls = Il.Calls(Getter(dressing, nameof(ActModel.AllAncients)));

        Assert.Contains(dressing.Name + ".get_Base", calls);
        Assert.Contains("ActModel.get_AllAncients", calls);
        Assert.DoesNotContain("ModelDb.AncientEvent", calls);
    }

    [Theory]
    [InlineData(typeof(Mondstadt), 0)]
    [InlineData(typeof(Liyue), 0)]
    [InlineData(typeof(Natlan), 1)]
    [InlineData(typeof(Inazuma), 1)]
    [InlineData(typeof(Fontaine), 2)]
    [InlineData(typeof(Sumeru), 2)]
    public void A_dressing_stands_at_its_base_zones_index_and_needs_no_epoch(
        Type dressing, int index)
    {
        // `Index` and `IsDefault` decide whether the pair is a coin at all,
        // and both are compile-time literals in the dressing classes, so the
        // IL is read directly: an `Index` getter must be `ldc.i4.<n>; ret` --
        // the `ldc.i4.<n>` short forms are consecutive opcodes from `ldc.i4.0`
        // at 0x16, so index n is 0x16 + n for the 0..2 this can ever be -- and
        // an `IsDefault` getter `ldc.i4.1; ret`.
        //
        // THE INDEX IS THE PAIRING, which is why it is pinned per dressing. A
        // face at the wrong index joins the wrong coin, and since its base
        // zone has already been removed that leaves one index with a single
        // candidate and another with three. Act 1's two faces stand at 0
        // (Overgrowth's and Underdocks'), act 2's at 1 (the Hive's) and act
        // 3's at 2 (Glory's).
        //
        // `IsDefault => true` is load-bearing and is the reason this pin is
        // worth its awkwardness: `ActModel.GetRandomList` FORCES a
        // non-default, unlocked, undiscovered act past the roll on a
        // single-player run (`ActModel.cs:563`), so a dressing marked
        // non-default would appear on the first run whatever the coin said.
        Assert.Equal(
            new byte[] { (byte)(0x16 + index), 0x2a },
            Getter(dressing, nameof(ActModel.Index)).GetMethodBody()!.GetILAsByteArray());
        Assert.Equal(
            new byte[] { 0x17, 0x2a },
            Getter(dressing, nameof(ActModel.IsDefault)).GetMethodBody()!.GetILAsByteArray());
    }

    // ---------------------------------------------------------------
    // Item 4.2, generalised: the DRESSED EVENTS.
    //
    // The spike had one, hand-written. There are six now, generated from the
    // curated faces by `tools/gen_teyvat_events.py`, and every pin below is
    // written over the GENERATED TABLE rather than over a class name, so
    // adding a seventh costs no test.
    // ---------------------------------------------------------------

    /// <summary>Every dressed event type the generator emitted, with the
    /// mirror it subclasses and the base event it stands in for.</summary>
    public static IEnumerable<object[]> DressedEvents() =>
        Shapes().Select(kv => new object[] { kv.Key });

    [Fact]
    public void Every_dressed_event_is_a_one_line_subclass_of_a_mirror()
    {
        // THE SHAPE DECISION, pinned. A dressed event declares no member of
        // its own: every mechanic is in the mirror, and everything else --
        // `Id.Entry`, `Title`, `InitialDescription`, every option key -- is
        // derived by the engine from the class NAME. A generated class that
        // grew a body would mean a mechanic had been authored per nation,
        // which is the exact drift this surface exists to prevent.
        Assert.NotEmpty(Shapes());
        foreach (var (dressed, shape) in Shapes())
        {
            Assert.True(dressed.IsSealed, dressed.Name + " is not sealed");
            Assert.Equal(shape.Mirror, dressed.BaseType!.Name);
            Assert.True(dressed.BaseType.IsAbstract,
                shape.Mirror + " must be abstract so ModelDb does not register it");
            Assert.Empty(dressed.GetMembers(
                BindingFlags.Public | BindingFlags.NonPublic
              | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Where(m => m.Name != ".ctor"));
        }
    }

    [Fact]
    public void A_dressed_events_entry_is_slugified_from_its_own_class_name()
    {
        // `ModelDb.GetEntry(type)` is `StringHelper.Slugify(type.Name)` and
        // `OptionKey` slugifies `GetType().Name`, so the id and every loc key
        // follow the dressed name with no table. The generator's rows are
        // written against that derivation; this is the two sides agreeing.
        foreach (var (dressed, shape) in Shapes())
        {
            Assert.Equal(shape.BaseEntry, Slugify(dressed.Name));
        }
    }

    [Fact]
    public void The_substitution_is_a_substitution_and_not_a_pool_edit()
    {
        // A dressed event is NOT in any act's `AllEvents`. The four base
        // events dressed today are all in `ModelDb.AllSharedEvents`'s eighteen
        // (`ModelDb.cs:157`), not act events, so swapping one inside a
        // dressing's pool would have ADDED an event beside the shared one and
        // changed the pool's LENGTH -- which moves the run's `UpFront` rng.
        //
        // The pin is that a dressed model is constructed from the generated
        // substitution table and from nowhere else in the assembly.
        var dressed = Shapes().Keys.ToHashSet();
        var reachedFrom = typeof(TeyvatFrame).Assembly
            .GetTypes()
            .Where(t => t.Namespace != null && t.Namespace.StartsWith("KleeMod.Teyvat", StringComparison.Ordinal))
            .SelectMany(t => t.GetMethods(BindingFlags.Static | BindingFlags.Instance
                                        | BindingFlags.Public | BindingFlags.NonPublic
                                        | BindingFlags.DeclaredOnly))
            .Where(m => !m.IsAbstract && !dressed.Contains(m.DeclaringType!))
            .Where(m => Il.Calls(m).Contains("ModelDb.Event"))
            // A lambda in a field initialiser compiles into a nested `<>c`
            // closure class, so the owner is the outermost non-generated type.
            .Select(m => Owner(m.DeclaringType!).Name)
            .Distinct()
            .ToList();

        Assert.Equal(new[] { "TeyvatGeneratedEvents" }, reachedFrom);
    }

    [Theory]
    [MemberData(nameof(MirrorPairs))]
    public void A_mirror_carries_its_base_events_act_gate(Type mirror, Type baseEvent)
    {
        // `RoomSet.EnsureNextEventIsValid` consults whatever event is at the
        // head of the pre-shuffled list -- which is the BASE event -- and the
        // postfix then swaps. Identical gates are what make that ordering
        // irrelevant.
        // A base event that does not OVERRIDE `IsAllowed` takes
        // `EventModel`'s `return true` -- This or That is one -- so "no
        // declared method" is itself an answer the mirror has to match, and
        // `DeclaredOnlyCalls` returns null for it rather than throwing.
        var mine = DeclaredOnlyCalls(mirror, nameof(EventModel.IsAllowed));
        var theirs = DeclaredOnlyCalls(baseEvent, nameof(EventModel.IsAllowed));

        Assert.Equal(theirs == null, mine == null);
        if (theirs != null)
        {
            Assert.Equal(theirs, mine);
        }
    }

    [Theory]
    [MemberData(nameof(MirrorPairs))]
    public void A_mirror_offers_the_same_number_of_options_as_its_base(Type mirror, Type baseEvent)
    {
        // A count pin on a call the method demonstrably makes, which is the
        // only count `Il.CallSequence` is safe for (its own caveat). The count
        // the re-proof read as zero is the one this is looking at.
        var mine = Il.CallSequence(Method(mirror, "GenerateInitialOptions"))
            .Count(c => c == "EventOption..ctor");
        var theirs = Il.CallSequence(Method(baseEvent, "GenerateInitialOptions"))
            .Count(c => c == "EventOption..ctor");

        Assert.Equal(theirs, mine);
        Assert.NotEqual(0, mine);
    }

    [Theory]
    [MemberData(nameof(MirrorPairs))]
    public void A_mirror_reaches_the_same_commands_as_its_base(Type mirror, Type baseEvent)
    {
        // Hygiene-grade means checkable: the mirror's option bodies reach the
        // same COMMANDS as the base event's, so nothing mechanical was
        // authored. Compared as a SET over the private option handlers,
        // because the handlers are renamed by nothing and ordered by nothing
        // that matters -- what matters is that no command appears in one and
        // not the other.
        Assert.Equal(CommandsIn(baseEvent), CommandsIn(mirror));
    }

    /// <summary>
    /// The call set of one DECLARED method, or null when the type does not
    /// declare it. Compiler-generated lambda names are normalised: a lambda in
    /// `IsAllowed` compiles to `&lt;&gt;c.&lt;IsAllowed&gt;b__N_M`, where N is the
    /// ordinal of the declaring method within its type -- which differs between
    /// a base event and a mirror for no reason that means anything, and would
    /// otherwise make every predicate-carrying gate look changed.
    /// </summary>
    private static IReadOnlyList<string> DeclaredOnlyCalls(Type type, string name)
    {
        var method = type.GetMethod(name,
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic
          | BindingFlags.DeclaredOnly);
        if (method == null)
        {
            return null;
        }

        return Il.Calls(method)
            .Select(c => System.Text.RegularExpressions.Regex.Replace(
                c, @"b__\d+_(\d+)$", "b__$1"))
            // The SAME ordinal, on the other shape a lambda compiles to. A
            // gate whose predicate CAPTURES something -- Luminous Choir's
            // closes over `runState` -- gets a `<>c__DisplayClassN_M` rather
            // than the cached `<>c`, and N is again the declaring method's
            // ordinal within its type, which differs between a base event and
            // a mirror for no reason that means anything.
            .Select(c => System.Text.RegularExpressions.Regex.Replace(
                c, @"<>c__DisplayClass\d+_(\d+)", "<>c__DisplayClass_$1"))
            .OrderBy(c => c, StringComparer.Ordinal)
            .ToList();
    }

    private static IReadOnlyList<string> CommandsIn(Type eventType) =>
        eventType
            .GetMethods(BindingFlags.Instance | BindingFlags.NonPublic
                      | BindingFlags.Public | BindingFlags.DeclaredOnly)
            .SelectMany(Il.Calls)
            .Where(c => c.Contains("Cmd.") || c.StartsWith("CardFactory.", StringComparison.Ordinal)
                     || c.StartsWith("RelicFactory.", StringComparison.Ordinal))
            .Distinct()
            .OrderBy(c => c, StringComparer.Ordinal)
            .ToList();

    public static IEnumerable<object[]> MirrorPairs() =>
        new[]
        {
            new object[] { typeof(RoomFullOfCheeseMirror), typeof(RoomFullOfCheese) },
            new object[] { typeof(TheLegendsWereTrueMirror), typeof(TheLegendsWereTrue) },
            new object[] { typeof(ThisOrThatMirror), typeof(ThisOrThat) },
            new object[] { typeof(SelfHelpBookMirror), typeof(SelfHelpBook) },
            new object[] { typeof(SlipperyBridgeMirror), typeof(SlipperyBridge) },
            new object[] { typeof(AromaOfChaosMirror), typeof(AromaOfChaos) },
            new object[] { typeof(BrainLeechMirror), typeof(BrainLeech) },
            new object[] { typeof(ByrdonisNestMirror), typeof(ByrdonisNest) },
            new object[] { typeof(DenseVegetationMirror), typeof(DenseVegetation) },
            new object[] { typeof(JungleMazeAdventureMirror), typeof(JungleMazeAdventure) },
            new object[] { typeof(LuminousChoirMirror), typeof(LuminousChoir) },
            new object[] { typeof(MorphicGroveMirror), typeof(MorphicGrove) },
            new object[] { typeof(SapphireSeedMirror), typeof(SapphireSeed) },
            new object[] { typeof(TeaMasterMirror), typeof(TeaMaster) },
            new object[] { typeof(UnrestSiteMirror), typeof(UnrestSite) },
            new object[] { typeof(WellspringMirror), typeof(Wellspring) },
            new object[] { typeof(WhisperingHollowMirror), typeof(WhisperingHollow) },
            new object[] { typeof(WoodCarvingsMirror), typeof(WoodCarvings) },
            new object[] { typeof(DoorsOfLightAndDarkMirror), typeof(DoorsOfLightAndDark) },
            new object[] { typeof(DrowningBeaconMirror), typeof(DrowningBeacon) },
            new object[] { typeof(PunchOffMirror), typeof(PunchOff) },
            new object[] { typeof(SpiralingWhirlpoolMirror), typeof(SpiralingWhirlpool) },
            new object[] { typeof(SunkenTreasuryMirror), typeof(SunkenTreasury) },
            new object[] { typeof(SunkenStatueMirror), typeof(SunkenStatue) },
            new object[] { typeof(TrashHeapMirror), typeof(TrashHeap) },
            new object[] { typeof(WaterloggedScriptoriumMirror), typeof(WaterloggedScriptorium) },
        };

    // ---------------------------------------------------------------
    // Items 4.3 and 4.4: the dressing tables, and the music's silence.
    // ---------------------------------------------------------------

    [Fact]
    public void Every_dressing_table_row_names_a_dressing_that_exists()
    {
        // A typo in a table key is a SILENT no-op -- the patch simply never
        // fires -- which is the failure mode this arm is most exposed to,
        // since every one of its patches is table-driven.
        var dressings = TeyvatFrame.AssetAlias.Keys.ToHashSet(StringComparer.Ordinal);

        Assert.Equal(
            new[]
            {
                TeyvatFrame.Mondstadt, TeyvatFrame.Liyue,
                TeyvatFrame.Natlan, TeyvatFrame.Inazuma,
                TeyvatFrame.Fontaine, TeyvatFrame.Sumeru,
            }.OrderBy(d => d, StringComparer.Ordinal),
            dressings.OrderBy(d => d, StringComparer.Ordinal));
        Assert.All(TeyvatFrame.MonsterNames.Keys, k => Assert.Contains(k.Dressing, dressings));
        Assert.All(TeyvatFrame.IntentWords.Keys, k => Assert.Contains(k.Dressing, dressings));
        Assert.All(TeyvatFrame.StillPortraits.Keys, k => Assert.Contains(k.Dressing, dressings));
    }

    /// <summary>
    /// EVERY FACE HAS AN ACT TITLE, or the map screen prints a raw key.
    ///
    /// `ActModel.Title` is `new LocString("acts", Id.Entry + ".title")` and
    /// there is no fallback: an unmerged key renders as `NATLAN.title` on the
    /// map, in the run-history row and in rich presence. The rows are written
    /// inline in `TeyvatLoc.Inject` rather than in a table, so the pin reads
    /// the method's string literals -- which is what a missing row actually
    /// looks like from here.
    /// </summary>
    [Fact]
    public void Every_dressing_has_an_act_title_row()
    {
        // Reached by name through the assembly: `TeyvatLoc` is `internal`,
        // like most of the arm, and an `InternalsVisibleTo` for one pin is a
        // bigger change than this line.
        var strings = Il.Strings(StaticMethod(
            InArm("KleeMod.Teyvat.TeyvatLoc"), "Inject")).ToHashSet(
                StringComparer.Ordinal);

        foreach (var dressing in TeyvatFrame.AssetAlias.Keys)
        {
            // ONE `ldstr` AND NOT TWO: `TeyvatFrame.<Face>` is a `const`, so
            // `<Face> + ".title"` is folded at compile time and the literal in
            // the method body is the whole key. That is the key
            // `ActModel.Title` asks the `acts` table for.
            Assert.Contains(dressing + ".title", strings);

            // And the value, which is the entry in title case -- the only
            // thing in this arm a player ever reads as the act's name.
            Assert.Contains(
                dressing[..1] + dressing[1..].ToLowerInvariant(), strings);
        }
    }

    [Fact]
    public void The_intent_word_table_ships_empty()
    {
        // The frame packet sec.7.1's design view: per-monster MOVE titles
        // carry the nation, the generic verbs do not. The mechanism is armed;
        // using it is a [USER] taste call and costs one row.
        Assert.Empty(TeyvatFrame.IntentWords);
    }

    [Fact]
    public void A_dressed_key_cannot_collide_with_a_shipped_one()
    {
        var dressed = MonsterModel_L10NMonsterLookup_TeyvatNames_Patch
            .Dressed("NIBBIT.name", TeyvatFrame.Mondstadt);

        Assert.Equal("NIBBIT.name@MONDSTADT", dressed);
        Assert.Equal("NIBBIT.name",
            MonsterModel_L10NMonsterLookup_TeyvatNames_Patch.Dressed("NIBBIT.name", null));
    }

    [Fact]
    public void With_the_arm_off_there_is_no_dressing_at_all()
    {
        TeyvatFrame.Enabled = false;

        // Every patch in the arm leads with this question, so a null here is
        // the whole flag-off guarantee in one assertion.
        Assert.Null(TeyvatFrame.CurrentActEntry);
        Assert.False(TeyvatFrame.IsDressing(TeyvatFrame.Mondstadt) && !TeyvatFrame.Enabled
                     && TeyvatFrame.CurrentActEntry != null);
    }

    [Fact]
    public void The_music_arm_does_nothing_without_a_packaged_track()
    {
        // Item 4.4's acceptance condition: no audio file is added by this
        // commit, so the lookup must answer null rather than guess a name.
        // `TrackFor` is pure and Godot-free on this path -- it returns before
        // touching `DirAccess` when handed nothing.
        Assert.Null(TeyvatMusic.TrackFor(null));
        Assert.Null(TeyvatMusic.TrackFor(string.Empty));
    }

    [Fact]
    public void The_music_root_is_the_frames_namespace_not_a_characters()
    {
        Assert.Equal("res://teyvat/music/", TeyvatMusic.Root);
        Assert.Equal(new[] { ".ogg", ".mp3" }, TeyvatMusic.Extensions);
    }

    // ---------------------------------------------------------------
    // EB-758: the no-track path costs nothing and says nothing.
    // ---------------------------------------------------------------

    /// <summary>
    /// EB-758, AND IT IS THE WHOLE ROW. The spike's deploy proved the arm's
    /// control flow correct and its LOG wrong: `DirAccess.GetFilesAt` on the
    /// absent `res://teyvat/music/mondstadt` is an `ERR_FAIL_COND_V_MSG`, so
    /// every miss printed an engine ERROR with a 31-frame backtrace through
    /// `TrackFor` → `Play` → `UpdateMusicPostfix`.
    ///
    /// The repair is a silent existence question in front of the enumeration,
    /// and THE THING TO PIN IS THAT THE ENUMERATION IS NOT REACHED. Asserting
    /// only that `TrackFor` returns null would pass against the defect — it
    /// returned null before, noisily. So the enumerating probe counts its
    /// calls and the assertion is that the count is zero.
    /// </summary>
    [Fact]
    public void A_missing_directory_is_never_enumerated()
    {
        var listed = 0;
        var probed = new List<string>();
        TeyvatMusic.ClearCache();
        TeyvatMusic.DirectoryExists = path => { probed.Add(path); return false; };
        TeyvatMusic.ListFiles = _ => { listed++; return Array.Empty<string>(); };
        TeyvatMusic.ResourceExists = _ => true;

        Assert.Null(TeyvatMusic.TrackFor("Mondstadt"));

        Assert.Equal(0, listed);
        Assert.Equal(new[] { "res://teyvat/music/mondstadt" }, probed);
    }

    /// <summary>
    /// The cache is the second half of the cost, and it covers the existence
    /// question too. `UpdateMusic` runs on every room change; a probe per room
    /// for an answer that cannot change inside a session is a cost, and before
    /// this row it was a LOG LINE per act id per boot as well.
    /// </summary>
    [Fact]
    public void The_absence_is_asked_once_per_act_and_then_remembered()
    {
        var probes = 0;
        TeyvatMusic.ClearCache();
        TeyvatMusic.DirectoryExists = _ => { probes++; return false; };
        TeyvatMusic.ListFiles = _ => Array.Empty<string>();

        for (var i = 0; i < 5; i++)
        {
            Assert.Null(TeyvatMusic.TrackFor("Mondstadt"));
        }

        Assert.Equal(1, probes);

        // A DIFFERENT act is a different question, and must not read the first
        // one's answer: the entry is what the directory is named after.
        Assert.Null(TeyvatMusic.TrackFor("Liyue"));
        Assert.Equal(2, probes);
    }

    /// <summary>
    /// The other side of the same switch, so the guard cannot be "return null
    /// always" wearing a probe: with a directory present and a loadable file
    /// in it, the lookup still finds the track, still prefers `.ogg` over
    /// `.mp3`, and still refuses a name `ResourceLoader` says will not load.
    /// </summary>
    [Fact]
    public void A_present_directory_still_resolves_its_track()
    {
        TeyvatMusic.ClearCache();
        TeyvatMusic.DirectoryExists = _ => true;
        // Deliberately NOT in preference order on disk, and with one loadable
        // `.mp3` beside the `.ogg`, so the assertion is about the preference
        // list and not about enumeration order.
        TeyvatMusic.ListFiles = _ => new[] { "theme.mp3", "theme.ogg" };
        TeyvatMusic.ResourceExists = _ => true;

        Assert.Equal("res://teyvat/music/mondstadt/theme.ogg",
                     TeyvatMusic.TrackFor("Mondstadt"));

        TeyvatMusic.ClearCache();
        TeyvatMusic.ResourceExists = path => path.EndsWith(".mp3", StringComparison.Ordinal);
        Assert.Equal("res://teyvat/music/mondstadt/theme.mp3",
                     TeyvatMusic.TrackFor("Mondstadt"));
    }

    // NOT PINNED HERE, and for the boundary's reason rather than for want of
    // trying: that a throwing probe answers null instead of taking the run's
    // music controller down with it. `TrackFor`'s catch clause calls
    // `Log.Warn`, and `MegaCrit.Sts2.Core.Logging.Logger`'s static
    // constructor calls `OS.GetCmdlineArgs()` — a Godot call, outside this
    // suite's headless boundary. The `try`/`catch` is still there and still
    // the right shape; only a deploy can watch it work.

    // ---------------------------------------------------------------
    // EB-759 / EB-760: the two seams the spike's deploy proved wrong.
    // ---------------------------------------------------------------

    /// <summary>
    /// EB-759, STRUCTURALLY, because that is as far as a headless suite can
    /// go. `LocManager` is outside the headless boundary -- its tables are
    /// built by the game's boot and this process never loads them -- so no pin
    /// here can assert that the Mondstadt rows are PRESENT after init; only a
    /// deploy can, and the row's acceptance line says so. What a pin CAN say
    /// is the thing that was actually wrong: WHICH SEAM the merge is called
    /// from.
    ///
    /// `TeyvatLoc.Inject` ran from `KleeMod.Initialize`, a `[ModInitializer]`,
    /// which is upstream of `LocManager.Initialize`. `LocManager.Instance` had
    /// no tables yet, the merge threw an NRE on every boot, its own catch
    /// turned that into one ERROR line, and zero rows landed -- so every
    /// dressed string rendered as its raw key. The card rows never had the bug
    /// because they have always ridden the postfix. Both halves are pinned: it
    /// IS in the postfix, and it is NOT in `Initialize`.
    /// </summary>
    [Fact]
    public void The_loc_merge_rides_the_LocManager_postfix_and_not_the_ModInitializer()
    {
        var patch = typeof(TeyvatFrame).Assembly
            .GetType("KleeMod.LocManager_Initialize_Patch", throwOnError: true)!;
        var postfix = StaticMethod(patch, "Postfix");

        var inPostfix = Il.Calls(postfix);
        Assert.Contains("TeyvatLoc.Inject", inPostfix);
        Assert.Contains("KleeMod.InjectLocStrings", inPostfix);

        var initialize = StaticMethod(typeof(KleeMod), nameof(KleeMod.Initialize));
        Assert.DoesNotContain("TeyvatLoc.Inject", Il.Calls(initialize));
    }

    /// <summary>
    /// EB-760. `MonsterModel.CreateVisuals` CASTS the instantiated scene root
    /// to `NCreatureVisuals`, and a script-less scene's root is a plain
    /// `Node2D`, so the still portrait drew the game's pink error creature.
    /// BaseLib's auto-conversion is what makes the cast succeed, and
    /// `NodeFactory.TryAutoConvert` converts only a REGISTERED path --
    /// registration being exactly what nothing did, because the automatic pass
    /// (`PostModInitPatch.RegisterSceneConversions`) only reaches models that
    /// are our own and a dressed base-game monster is not.
    ///
    /// The registration sits at `[ModInitializer]` time, and NOT on the loc
    /// postfix EB-759 just moved the merge to: it writes into a BaseLib
    /// dictionary that exists from the moment BaseLib loads, and only has to
    /// precede the scene's first INSTANTIATION, which is first combat at the
    /// earliest. The two halves are that the registration reaches BaseLib's
    /// extension at all, and that `KleeMod.Initialize` is where it is reached
    /// from.
    /// </summary>
    [Fact]
    public void Every_still_portrait_is_registered_for_BaseLib_auto_conversion()
    {
        var calls = Il.Calls(
            StaticMethod(typeof(TeyvatVisuals), nameof(TeyvatVisuals.RegisterStillPortraits)));

        Assert.Contains(calls, c => c.EndsWith("RegisterSceneForConversion", StringComparison.Ordinal));

        // The same `ResourceLoader.Exists` guard the path patch uses: a build
        // whose pck was not rebuilt registers nothing rather than registering
        // a dead path and putting a misleading line in the boot log.
        Assert.Contains("ResourceLoader.Exists", calls);

        Assert.Contains(
            "TeyvatVisuals.RegisterStillPortraits",
            Il.Calls(StaticMethod(typeof(KleeMod), nameof(KleeMod.Initialize))));
    }

    [Fact]
    public void With_the_arm_off_the_registration_returns_before_it_touches_Godot()
    {
        TeyvatFrame.Enabled = false;

        // The flag is this method's first line, as it is in every file in the
        // arm -- and it has to be the FLAG and not `CurrentActEntry`, because
        // this is the arm's one call that runs outside a run entirely. The
        // assertion is that it neither throws nor reaches `ResourceLoader`
        // (which would need a Godot runtime this process does not have).
        TeyvatVisuals.RegisterStillPortraits();
    }

    /// <summary>
    /// The scene the registration names is the scene the pck ships, spelled
    /// identically. Drift here is silent twice over -- the path patch declines
    /// to swap AND the registration registers a path nothing will instantiate
    /// -- so the spelling is pinned against the source tree's own layout.
    /// </summary>
    [Fact]
    public void Every_still_portrait_names_a_scene_in_the_frames_own_namespace()
    {
        Assert.NotEmpty(TeyvatFrame.StillPortraits);
        Assert.All(TeyvatFrame.StillPortraits.Values, scene =>
        {
            Assert.StartsWith("res://teyvat/creature_visuals/", scene, StringComparison.Ordinal);
            Assert.EndsWith(".tscn", scene, StringComparison.Ordinal);
        });
    }

    // ---------------------------------------------------------------
    // EB-764 / EB-765: the two throws that made the converted event
    // unplayable the first time it was reached in a real run.
    // ---------------------------------------------------------------

    /// <summary>
    /// EB-765, and it is the whole defect reduced to a set comparison --
    /// now asked of every generated dressing at once.
    ///
    /// `EventOption`'s constructor does not read the key it is handed: it
    /// reads `eventModel.GetOptionTitle(textKey)` and `GetOptionDescription`,
    /// which are `LocString.GetIfExists(LocTable, textKey + ".title")` and
    /// `+ ".description"` (`EventModel.cs:216-224`). `GetIfExists` answers NULL
    /// for an absent key, and the constructor's last act is `AddLocVars`,
    /// whose first line dereferences that null through
    /// `CharacterModel.AddDetailsTo`. So a missing `.description` row is not a
    /// blank line on the page: it is an NRE that aborts
    /// `GenerateInitialOptions` before the first option exists. The spike
    /// shipped one FLAT row per option, which is why the page came up with
    /// `options: []`.
    ///
    /// THE GENERATED SHAPE IS THE RIGHT SOURCE HERE, where the spike's pin
    /// read `ldstr` literals out of the class. A dressed event has no
    /// literals -- it has no body at all -- because every key is derived from
    /// its name at runtime by `EventModel.OptionKey` and `Id.Entry`. So the
    /// key set is rebuilt here the same way the engine builds it, from the
    /// option and page names the generator recorded off the base event, and
    /// compared against the merged rows.
    /// </summary>
    [Fact]
    public void Every_loc_key_a_dressed_event_asks_for_has_a_merged_row()
    {
        var rows = EventRows();
        Assert.NotEmpty(Shapes());

        foreach (var (dressed, shape) in Shapes())
        {
            var entry = shape.BaseEntry;
            var asked = new HashSet<string>(StringComparer.Ordinal)
            {
                // `EventModel.Title` and `InitialDescription` (`:62`, `:64`).
                entry + ".title",
                entry + ".pages.INITIAL.description",
            };

            // An option key is a PREFIX the engine suffixes twice.
            foreach (var option in shape.OptionKeys)
            {
                asked.Add($"{entry}.pages.INITIAL.options.{option}.title");
                asked.Add($"{entry}.pages.INITIAL.options.{option}.description");
            }

            // An option key that is NOT on the INITIAL page, or that has no
            // face line of its own -- a `_LOCKED` twin, an option a later
            // page offers -- is a full suffix under the entry, and is a
            // prefix exactly like the ones above.
            foreach (var extra in shape.ExtraOptionKeys)
            {
                asked.Add($"{entry}.{extra}.title");
                asked.Add($"{entry}.{extra}.description");
            }

            // Every other key the mirror hands to `L10NLookup` whole.
            foreach (var page in shape.PageKeys)
            {
                asked.Add($"{entry}.{page}");
            }

            if (shape.HasLossRow)
            {
                asked.Add(entry + ".loss");
            }

            Assert.All(asked, key => Assert.True(
                rows.ContainsKey(key), $"no merged row for {key} ({dressed.Name})"));
        }
    }

    /// <summary>
    /// THE MIRROR AND THE GENERATED SHAPE CANNOT DISAGREE about which keys
    /// exist. The mirror builds its keys from `InitialOptionKey("GORGE")` and
    /// `PageKey("GORGE.description")`, so the option and page NAMES are
    /// `ldstr` literals in its methods; the shape table carries the same names
    /// read off the decompiled base event by `--refresh`. A mirror that
    /// renamed a page, or a shape row that went stale, shows up here and
    /// nowhere else -- the loc pin above would still pass, because it builds
    /// the asked-for set from the shape rather than from the code.
    /// </summary>
    [Theory]
    [MemberData(nameof(MirrorPairs))]
    public void A_mirrors_key_literals_are_exactly_its_shape(Type mirror, Type baseEvent)
    {
        _ = baseEvent;

        var shape = Shapes().Values.First(s => s.Mirror == mirror.Name);
        var expected = shape.OptionKeys
            .Concat(shape.PageKeys.Select(Unprefixed))
            .Concat(shape.ExtraOptionKeys.Select(Unprefixed))
            // Both sides are filtered by the SAME shape test, so the pin
            // compares exactly the literals it can see and says so. A key
            // deeper than one page word -- Dense Vegetation's
            // `REST.options.FIGHT`, Slippery Bridge's
            // `HOLD_ON_0.options.HOLD_ON_1` -- is out of BOTH sets rather
            // than in one and not the other; the loc pin above still
            // requires its rows, because that pin builds its asked-for set
            // from the shape and not from the IL.
            .Where(IsComparableKey)
            .Distinct()
            .OrderBy(k => k, StringComparer.Ordinal)
            .ToList();

        var actual = mirror
            .GetMethods(BindingFlags.Instance | BindingFlags.NonPublic
                      | BindingFlags.Public | BindingFlags.DeclaredOnly)
            .SelectMany(Il.Strings)
            // A mirror also carries literals that are not loc keys at all --
            // `ThisOrThat`'s `StringVar("Curse", ...)` names a DynamicVar. A
            // key name is an ALL-CAPS option segment, optionally followed by
            // one camelCase page word; nothing else is compared.
            .Where(IsComparableKey)
            .Distinct()
            .OrderBy(k => k, StringComparer.Ordinal)
            .ToList();

        Assert.Equal(expected, actual);
    }

    /// <summary>A shape key as the MIRROR spells it.
    ///
    /// The shape carries full suffixes under the dressed entry; the mirror
    /// builds them through two helpers that supply the front of the key --
    /// `EventModel.InitialOptionKey(name)` for an option on the INITIAL page
    /// (a `_LOCKED` twin included) and `TeyvatEventMirror.PageKey(suffix)`
    /// for everything else -- so the literal in the IL is what is left after
    /// the helper's own prefix.</summary>
    private static string Unprefixed(string key) =>
        key.StartsWith("pages.INITIAL.options.", StringComparison.Ordinal)
            ? key.Substring("pages.INITIAL.options.".Length)
        : key.StartsWith("pages.", StringComparison.Ordinal)
            ? key.Substring("pages.".Length) : key;

    private static bool IsComparableKey(string s) =>
        System.Text.RegularExpressions.Regex.IsMatch(
            s, @"^[A-Z0-9_]+(\.[A-Za-z]+)?$");

    /// <summary>
    /// Every merged event row belongs to a dressed event. A merge is GLOBAL --
    /// `LocTable.MergeWith` overwrites -- so a row whose key drifted onto a
    /// base event's family would silently rewrite the shipped game's text, and
    /// the `events` table has no dressed-key trick to fall back on the way the
    /// monster names do.
    /// </summary>
    [Fact]
    public void No_merged_event_row_can_overwrite_a_base_events_text()
    {
        var prefixes = Shapes().Values.Select(s => s.BaseEntry + ".").ToList();

        Assert.NotEmpty(EventRows());
        Assert.All(EventRows().Keys, key => Assert.True(
            prefixes.Any(p => key.StartsWith(p, StringComparison.Ordinal)),
            key + " is not under any dressed event's id"));
    }

    /// <summary>
    /// EB-764. The portrait patch sits on the GETTER, not on
    /// `CreateInitialPortrait` -- because `EventModel.GetAssetPaths` (`:431`)
    /// feeds the same private property to the preloader, and a fix on the
    /// create call would leave the preload asking for the dead path and
    /// caching the failure. The two halves pinned here are the target and the
    /// `ResourceLoader.Exists` fall-through that retires the borrow the day a
    /// real portrait lands.
    /// </summary>
    [Fact]
    public void The_converted_events_portrait_falls_back_to_the_base_events_image()
    {
        var patch = typeof(TeyvatFrame).Assembly.GetType(
            "KleeMod.Teyvat.Patches.EventModel_InitialPortraitPath_TeyvatConversions_Patch",
            throwOnError: true)!;

        var target = patch.GetCustomAttribute<HarmonyPatch>();
        Assert.NotNull(target);
        Assert.Equal(typeof(EventModel), target!.info.declaringType);
        Assert.Equal("get_InitialPortraitPath", target.info.methodName);

        Assert.Contains("ResourceLoader.Exists", Il.Calls(StaticMethod(patch, "Postfix")));

        // Every row names an image the base game ships, under the path shape
        // `ImageHelper.GetImagePath("events/...")` builds.
        Assert.NotEmpty(TeyvatFrame.EventPortraits);
        Assert.All(TeyvatFrame.EventPortraits.Values, path =>
        {
            Assert.StartsWith("res://images/events/", path, StringComparison.Ordinal);
            Assert.EndsWith(".png", path, StringComparison.Ordinal);
        });
    }

    /// <summary>
    /// EVERY DRESSED EVENT HAS A PORTRAIT ROW, AND EVERY ROW NAMES ONE. EB-764
    /// was one missing borrow; the shape of it was that the class and the row
    /// were written in different files by different hands. They are generated
    /// together now, and this is that statement as a set equality -- plus the
    /// derivation the patch depends on: the value is the BASE event's image at
    /// the path `ImageHelper.GetImagePath("events/...")` builds, and the key is
    /// the dressed id the engine would have derived the dead path from.
    /// </summary>
    [Fact]
    public void Every_dressed_event_has_a_portrait_row_and_every_row_is_a_dressed_event()
    {
        var dressedIds = Shapes().Values.Select(s => s.BaseEntry)
            .OrderBy(k => k, StringComparer.Ordinal).ToArray();

        Assert.Equal(dressedIds,
            TeyvatFrame.EventPortraits.Keys.OrderBy(k => k, StringComparer.Ordinal).ToArray());

        Assert.All(TeyvatFrame.EventPortraits, row =>
        {
            Assert.StartsWith("res://images/events/", row.Value, StringComparison.Ordinal);
            Assert.EndsWith(".png", row.Value, StringComparison.Ordinal);
            // The borrow points at a BASE event's image, never at the dressed
            // path -- which is the path the patch is standing in for.
            Assert.NotEqual(
                "res://images/events/" + row.Key.ToLowerInvariant() + ".png", row.Value);
        });
    }

    /// <summary>`TeyvatLoc` is internal and this mod carries no
    /// `InternalsVisibleTo` -- the standing call -- so its one table is
    /// reached by reflection. It is a PROPERTY now, aliasing the generated
    /// rows, so both member kinds are tried.</summary>
    private static IReadOnlyDictionary<string, string> EventRows()
    {
        var type = typeof(TeyvatFrame).Assembly
            .GetType("KleeMod.Teyvat.TeyvatLoc", throwOnError: true)!;
        const BindingFlags flags = BindingFlags.NonPublic | BindingFlags.Public
                                 | BindingFlags.Static;
        var rows = (type.GetProperty("EventRows", flags)?.GetValue(null)
                 ?? type.GetField("EventRows", flags)?.GetValue(null))
            as IReadOnlyDictionary<string, string>;
        Assert.NotNull(rows);
        return rows!;
    }

    /// <summary>
    /// The generated shape table, flattened into something a pin can read
    /// without an `InternalsVisibleTo`: dressed event type -> (the dressed
    /// `Id.Entry`, the mirror's name, the option key names, the other page
    /// keys, whether a `.loss` row was written).
    ///
    /// Reached by reflection over the record's properties rather than by
    /// name-and-cast, because `TeyvatGeneratedEvents` and its `EventShape` are
    /// both internal and both GENERATED -- a pin that named their members in
    /// C# would have to be regenerated beside them.
    /// </summary>
    private static IReadOnlyDictionary<Type, TestShape> Shapes()
    {
        var owner = typeof(TeyvatFrame).Assembly
            .GetType("KleeMod.Teyvat.TeyvatGeneratedEvents", throwOnError: true)!;
        var table = owner.GetField("Shapes",
            BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetValue(null)!;

        var result = new Dictionary<Type, TestShape>();
        foreach (var entry in (System.Collections.IEnumerable)table)
        {
            var kvType = entry.GetType();
            var key = (Type)kvType.GetProperty("Key")!.GetValue(entry)!;
            var value = kvType.GetProperty("Value")!.GetValue(entry)!;
            var shapeType = value.GetType();
            result[key] = new TestShape(
                (string)shapeType.GetProperty("BaseEntry")!.GetValue(value)!,
                (string)shapeType.GetProperty("Mirror")!.GetValue(value)!,
                (IReadOnlyList<string>)shapeType.GetProperty("OptionKeys")!.GetValue(value)!,
                (IReadOnlyList<string>)shapeType.GetProperty("PageKeys")!.GetValue(value)!,
                (IReadOnlyList<string>)shapeType.GetProperty("ExtraOptionKeys")!.GetValue(value)!,
                (bool)shapeType.GetProperty("HasLossRow")!.GetValue(value)!);
        }
        return result;
    }

    private sealed record TestShape(
        string BaseEntry,
        string Mirror,
        IReadOnlyList<string> OptionKeys,
        IReadOnlyList<string> PageKeys,
        IReadOnlyList<string> ExtraOptionKeys,
        bool HasLossRow);

    /// <summary>`StringHelper.Slugify` for a C# type name, reimplemented so
    /// the pin does not depend on an internal of the game assembly: an
    /// underscore at each lower-to-upper boundary, then upper-cased. That is
    /// the derivation `ModelDb.GetEntry` and `EventModel.OptionKey` both
    /// make.</summary>
    private static string Slugify(string name) =>
        System.Text.RegularExpressions.Regex
            .Replace(name, "([a-z0-9])([A-Z])", "$1_$2")
            .ToUpperInvariant();

    // ---------------------------------------------------------------
    // The dressed asset set, and the alias that now stands down for it.
    // ---------------------------------------------------------------

    /// <summary>
    /// THE ALIAS DECISION, BOTH DIRECTIONS, over a predicate rather than over
    /// a real `ResourceLoader` -- which is the only reason it is answerable in
    /// a headless process at all.
    ///
    /// The direction that matters is the FALSE one. A dressing whose set is
    /// half-landed must take the alias whole: `BackgroundAssets`'s constructor
    /// throws on a missing `layers` directory AND on a layer file matching
    /// neither prefix, and the map PNGs and the rest-site scene have no
    /// fallback, so "use the two files that did arrive" is not a state the
    /// engine has.
    /// </summary>
    [Fact]
    public void A_dressing_takes_its_own_assets_only_when_the_whole_set_is_there()
    {
        var complete = new HashSet<string>(StringComparer.Ordinal)
        {
            TeyvatActAssets.FirstLayerPath("mondstadt"),
            TeyvatActAssets.BackgroundScenePath("mondstadt"),
            TeyvatActAssets.RestSiteScenePath("mondstadt"),
        };

        Assert.True(TeyvatActAssets.HasDressedAssets(
            TeyvatFrame.Mondstadt, complete.Contains));

        // Any ONE of the three missing puts the dressing back on the alias.
        foreach (var path in complete.ToArray())
        {
            var partial = new HashSet<string>(complete, StringComparer.Ordinal);
            partial.Remove(path);
            Assert.False(TeyvatActAssets.HasDressedAssets(
                TeyvatFrame.Mondstadt, partial.Contains), path);
        }

        // Nothing at all -- a build whose pck predates the set.
        Assert.False(TeyvatActAssets.HasDressedAssets(TeyvatFrame.Mondstadt, _ => false));

        // And "we could not ask" answers the same as "it is not there",
        // because the alias points at a tree that is certainly present.
        Assert.False(TeyvatActAssets.HasDressedAssets(TeyvatFrame.Mondstadt, null));
    }

    /// <summary>
    /// The paths are `ActModel`'s own, spelled out because the postfix runs
    /// INSIDE the getter that would otherwise build them. `FilePathIdentifier`
    /// is `Id.Entry.ToLowerInvariant()`, so the lowercasing is part of the
    /// contract and not a convenience.
    /// </summary>
    [Fact]
    public void The_dressed_paths_are_the_engines_own_spelling()
    {
        Assert.Equal("res://scenes/backgrounds/liyue/liyue_background.tscn",
                     TeyvatActAssets.BackgroundScenePath("liyue"));
        Assert.Equal("res://scenes/backgrounds/liyue/layers/liyue_bg_00_a.tscn",
                     TeyvatActAssets.FirstLayerPath("liyue"));
        Assert.Equal("res://scenes/rest_site/liyue_rest_site.tscn",
                     TeyvatActAssets.RestSiteScenePath("liyue"));

        foreach (var dressing in TeyvatFrame.AssetAlias.Keys)
        {
            Assert.Contains(dressing.ToLowerInvariant(),
                            TeyvatActAssets.BackgroundScenePath(dressing.ToLowerInvariant()));
        }
    }

    /// <summary>
    /// The alias postfix ASKS. Structural, through `Il`, because the getter it
    /// postfixes cannot be invoked without an `ActModel` -- and the thing that
    /// would go wrong silently is the check being DROPPED, not being wrong.
    /// </summary>
    [Fact]
    public void The_alias_postfix_stands_down_when_the_set_is_present()
    {
        // Reached by name through the assembly rather than by `typeof`: the
        // patch class is `internal`, like every other file in `Teyvat/Patches`
        // except the one whose helper the loc merge calls, and an
        // `InternalsVisibleTo` for one pin is a bigger change than this line.
        var calls = Il.Calls(StaticMethod(
            InArm("KleeMod.Teyvat.Patches.ActModel_FilePathIdentifier_TeyvatAlias_Patch"),
            "Postfix"));

        Assert.Contains("TeyvatActAssets.HasDressedAssetsCached", calls);
        // The alias table is still consulted first -- a base zone reached
        // while the flag is on has no row and the postfix must not ask the
        // pack about `overgrowth`. (`AssetAlias` itself is an `ldsfld`, not a
        // call, so the lookup through it is what the IL can show.)
        Assert.Contains(calls, c => c.EndsWith("TryGetValue", StringComparison.Ordinal));
    }

    /// <summary>
    /// The background root is converted, and by a factory that exists.
    /// BaseLib ships six and none is for `NCombatBackground`, so registration
    /// alone would log "no factory exists for that type" and fall through to
    /// the same failed cast EB-760 diagnosed for the still portrait.
    /// </summary>
    [Fact]
    public void Act_backgrounds_are_registered_with_a_factory_that_exists()
    {
        var calls = Il.Calls(StaticMethod(typeof(TeyvatActAssets),
                                          nameof(TeyvatActAssets.RegisterActBackgrounds)));

        Assert.Contains("NCombatBackgroundFactory.Ensure", calls);
        Assert.Contains(calls,
                        c => c.EndsWith("RegisterSceneForConversion", StringComparison.Ordinal));

        Assert.Contains("TeyvatActAssets.RegisterActBackgrounds",
                        Il.Calls(StaticMethod(typeof(KleeMod), nameof(KleeMod.Initialize))));
    }

    /// <summary>
    /// The slots the factory declares are the slots the generator writes into
    /// the background scene, and they are `AddLayer`'s own names
    /// (`$"Layer_{i:D2}"`, then `"Foreground"`). A drift here is an
    /// `InvalidOperationException` on the first frame of the first combat of a
    /// dressed run.
    /// </summary>
    [Fact]
    public void The_factorys_layer_slots_match_AddLayers_naming()
    {
        var slots = InArm("KleeMod.Teyvat.NCombatBackgroundFactory")
            .GetField("LayerSlots", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null) as string[];

        Assert.NotNull(slots);
        Assert.Equal(new[] { "Layer_00", "Layer_01", "Layer_02", "Layer_03", "Layer_04",
                             "Foreground" }, slots!);
    }

    [Fact]
    public void With_the_arm_off_the_act_background_registration_touches_nothing()
    {
        TeyvatFrame.Enabled = false;

        // The flag is the method's first line, as everywhere in the arm: this
        // one runs outside a run entirely, so it cannot key off the current
        // act, and it must not reach Godot or BaseLib in a process with no
        // runtime behind either.
        TeyvatActAssets.RegisterActBackgrounds();
    }

    // ---------------------------------------------------------------
    // Reflection helpers. Public/protected members are reached by name so a
    // rename is a compile error here rather than a silent skip.
    // ---------------------------------------------------------------

    /// <summary>
    /// A type in the mod assembly by full name, for the arm's `internal`
    /// classes. Asserting rather than returning null so a rename reads as a
    /// named failure instead of an NRE three lines later.
    /// </summary>
    private static Type InArm(string fullName)
    {
        var type = typeof(TeyvatFrame).Assembly.GetType(fullName, throwOnError: false);
        Assert.NotNull(type);
        return type!;
    }

    /// <summary>The outermost non-compiler-generated type enclosing
    /// <paramref name="type"/>.</summary>
    private static Type Owner(Type type)
    {
        while (type.Name.StartsWith("<", StringComparison.Ordinal) && type.DeclaringType != null)
        {
            type = type.DeclaringType;
        }

        return type;
    }

    private static MethodBase Method(Type type, string name)
    {
        var m = type.GetMethod(name, BindingFlags.Public | BindingFlags.NonPublic
                                   | BindingFlags.Instance | BindingFlags.DeclaredOnly);
        Assert.NotNull(m);
        return m!;
    }

    private static MethodBase Private(Type type, string name) => Method(type, name);

    /// <summary>The same lookup for a STATIC method -- the boot seams
    /// EB-759/EB-760 pin are all static.</summary>
    private static MethodBase StaticMethod(Type type, string name)
    {
        var m = type.GetMethod(name, BindingFlags.Public | BindingFlags.NonPublic
                                   | BindingFlags.Static | BindingFlags.DeclaredOnly);
        Assert.NotNull(m);
        return m!;
    }

    private static MethodBase Getter(Type type, string name)
    {
        var p = type.GetProperty(name, BindingFlags.Public | BindingFlags.NonPublic
                                     | BindingFlags.Instance | BindingFlags.Static
                                     | BindingFlags.DeclaredOnly);
        Assert.NotNull(p);
        var g = p!.GetGetMethod(nonPublic: true);
        Assert.NotNull(g);
        return g!;
    }
}
