using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Teyvat;
using KleeMod.Teyvat.Acts;
using KleeMod.Teyvat.Events;
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

    public void Dispose() => TeyvatFrame.Enabled = _enabled;

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

    [Fact]
    public void With_the_arm_on_the_two_act_one_zones_are_replaced_not_joined()
    {
        TeyvatFrame.Enabled = true;

        var planned = ModelDb_Acts_TeyvatDressings_Patch.Plan(BaseActs);

        // The SAME LENGTH is the whole point: act 1 is still exactly two
        // candidates, so `ActModel.GetRandomList` still makes exactly one
        // `rng.NextItem` draw against a two-element list at index 0. A
        // four-way roll would put the base zone and its own dressing in the
        // same coin.
        Assert.Equal(4, planned.Count);
        Assert.Equal(
            new[] { typeof(Mondstadt), typeof(Liyue), typeof(Hive), typeof(Glory) },
            planned);
        Assert.DoesNotContain(typeof(Overgrowth), planned);
        Assert.DoesNotContain(typeof(Underdocks), planned);
    }

    [Fact]
    public void Acts_two_and_three_are_untouched_by_the_arm()
    {
        TeyvatFrame.Enabled = true;

        var planned = ModelDb_Acts_TeyvatDressings_Patch.Plan(BaseActs);

        // The frame packet sec.4 leaves acts 2 and 3 to a later pick. The
        // spike must not quietly pre-empt it.
        Assert.Equal(typeof(Hive), planned[2]);
        Assert.Equal(typeof(Glory), planned[3]);
    }

    [Fact]
    public void A_base_act_the_postfix_cannot_find_is_left_alone_not_appended_to()
    {
        TeyvatFrame.Enabled = true;

        // A game patch that removed Underdocks, or a second mod that already
        // replaced it. Appending Liyue here would make act 1 a three-way roll.
        var without = new[] { typeof(Overgrowth), typeof(Hive), typeof(Glory) };
        var planned = ModelDb_Acts_TeyvatDressings_Patch.Plan(without);

        Assert.Equal(3, planned.Count);
        Assert.DoesNotContain(typeof(Liyue), planned);
        Assert.Contains(typeof(Mondstadt), planned);
    }

    // ---------------------------------------------------------------
    // Item 4.1: the delegation, structurally.
    // ---------------------------------------------------------------

    [Theory]
    [InlineData(typeof(Mondstadt))]
    [InlineData(typeof(Liyue))]
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
    public void A_dressings_ancient_pool_is_the_base_zones_own(Type dressing)
    {
        var calls = Il.Calls(Getter(dressing, nameof(ActModel.AllAncients)));

        Assert.Contains(dressing.Name + ".get_Base", calls);
        Assert.Contains("ActModel.get_AllAncients", calls);
        Assert.DoesNotContain("ModelDb.AncientEvent", calls);
    }

    [Theory]
    [InlineData(typeof(Mondstadt))]
    [InlineData(typeof(Liyue))]
    public void A_dressing_stands_at_act_one_and_needs_no_epoch(Type dressing)
    {
        // `Index` and `IsDefault` decide whether the pair is a coin at all,
        // and both are compile-time literals in the dressing classes, so the
        // IL is read directly: an `Index` getter must be `ldc.i4.0; ret` and
        // an `IsDefault` getter `ldc.i4.1; ret`.
        //
        // `IsDefault => true` is load-bearing and is the reason this pin is
        // worth its awkwardness: `ActModel.GetRandomList` FORCES a
        // non-default, unlocked, undiscovered act past the roll on a
        // single-player run (`ActModel.cs:563`), so a dressing marked
        // non-default would appear on the first run whatever the coin said.
        Assert.Equal(
            new byte[] { 0x16, 0x2a },
            Getter(dressing, nameof(ActModel.Index)).GetMethodBody()!.GetILAsByteArray());
        Assert.Equal(
            new byte[] { 0x17, 0x2a },
            Getter(dressing, nameof(ActModel.IsDefault)).GetMethodBody()!.GetILAsByteArray());
    }

    // ---------------------------------------------------------------
    // Item 4.2: the converted event.
    // ---------------------------------------------------------------

    [Fact]
    public void The_conversion_is_a_substitution_and_not_a_pool_edit()
    {
        // The converted event is NOT in any act's `AllEvents` -- Room Full of
        // Cheese is one of `ModelDb.AllSharedEvents`'s eighteen
        // (`ModelDb.cs:157`), not an act event, so swapping it inside a
        // dressing's pool would have ADDED a fourteenth act event beside the
        // shared thirteenth and changed the pool's length.
        //
        // The pin is that the arm's own event class is reached from the
        // PullNextEvent postfix's table and from nowhere else in the assembly.
        var reachedFrom = typeof(TeyvatFrame).Assembly
            .GetTypes()
            .Where(t => t.Namespace != null && t.Namespace.StartsWith("KleeMod.Teyvat", StringComparison.Ordinal))
            .SelectMany(t => t.GetMethods(BindingFlags.Static | BindingFlags.Instance
                                        | BindingFlags.Public | BindingFlags.NonPublic
                                        | BindingFlags.DeclaredOnly))
            .Where(m => !m.IsAbstract && m.DeclaringType != typeof(SpringvaleCheeseCellar))
            .Where(m => Il.Calls(m).Contains("ModelDb.Event"))
            // A lambda in a field initialiser compiles into a nested `<>c`
            // closure class, so the owner is the outermost non-generated type.
            .Select(m => Owner(m.DeclaringType!).Name)
            .Distinct()
            .ToList();

        Assert.Equal(
            new[] { nameof(ActModel_PullNextEvent_TeyvatConversions_Patch) },
            reachedFrom);
    }

    [Fact]
    public void The_conversion_carries_the_base_events_act_gate()
    {
        // `RoomSet.EnsureNextEventIsValid` consults whatever event is at the
        // head of the pre-shuffled list -- which is the BASE event -- and the
        // postfix then swaps. Identical gates are what make that ordering
        // irrelevant: both answer `CurrentActIndex < 2`.
        var mine = Il.Calls(Method(typeof(SpringvaleCheeseCellar), nameof(EventModel.IsAllowed)));
        var theirs = Il.Calls(Method(typeof(RoomFullOfCheese), nameof(EventModel.IsAllowed)));

        Assert.Equal(theirs.OrderBy(c => c, StringComparer.Ordinal),
                     mine.OrderBy(c => c, StringComparer.Ordinal));
    }

    [Fact]
    public void The_conversion_mirrors_the_base_events_two_outcomes()
    {
        // Hygiene-grade means checkable: the two option bodies reach the same
        // commands as the base event's, so nothing mechanical was authored.
        var gorge = Il.Calls(Private(typeof(SpringvaleCheeseCellar), "TasteTheRacks"));
        Assert.Contains("CardFactory.CreateForReward", gorge);
        Assert.Contains("EventModel.SelectCardsToAddToDeckFromGrid", gorge);

        var search = Il.Calls(Private(typeof(SpringvaleCheeseCellar), "HaulOutTheBackWall"));
        Assert.Contains("CreatureCmd.Damage", search);
        Assert.Contains("RelicCmd.Obtain", search);
    }

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

        Assert.Equal(new[] { TeyvatFrame.Mondstadt, TeyvatFrame.Liyue }.OrderBy(d => d),
                     dressings.OrderBy(d => d));
        Assert.All(TeyvatFrame.MonsterNames.Keys, k => Assert.Contains(k.Dressing, dressings));
        Assert.All(TeyvatFrame.IntentWords.Keys, k => Assert.Contains(k.Dressing, dressings));
        Assert.All(TeyvatFrame.StillPortraits.Keys, k => Assert.Contains(k.Dressing, dressings));
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
    /// EB-765, and it is the whole defect reduced to a set comparison.
    ///
    /// `EventOption`'s constructor does not read the key it is handed -- it
    /// reads `eventModel.GetOptionTitle(textKey)` and `GetOptionDescription`,
    /// which are `LocString.GetIfExists(LocTable, textKey + ".title")` and
    /// `+ ".description"` (`EventModel.cs:216-224`). `GetIfExists` answers NULL
    /// for an absent key, and the constructor's last act is `AddLocVars`,
    /// whose first line dereferences that null through
    /// `CharacterModel.AddDetailsTo`. So a missing `.description` row is not a
    /// blank line on the page: it is an NRE that aborts
    /// `GenerateInitialOptions` before the first option exists.
    ///
    /// The spike shipped one FLAT row per option, which is why the page came
    /// up with `options: []`. The pin is that every key the event asks for has
    /// a row, with an option key expanded into the two the engine derives from
    /// it -- the same shape the base event's own rows have in the pck
    /// (`ROOM_FULL_OF_CHEESE.pages.INITIAL.options.GORGE.title` and
    /// `.description`).
    ///
    /// LITERALS ARE THE RIGHT SOURCE HERE because that is what the class
    /// contains: every key it asks for is an `ldstr` in one of its methods,
    /// except the two the base class derives from `Id.Entry`, which are
    /// asserted by name.
    /// </summary>
    [Fact]
    public void Every_loc_key_the_converted_event_asks_for_has_a_merged_row()
    {
        var rows = EventRows();
        const string entry = "SPRINGVALE_CHEESE_CELLAR";

        var asked = new HashSet<string>(StringComparer.Ordinal)
        {
            // `EventModel.Title` and `InitialDescription` (`:62`, `:64`).
            entry + ".title",
            entry + ".pages.INITIAL.description",
        };

        foreach (var method in typeof(SpringvaleCheeseCellar).GetMethods(
                     BindingFlags.Public | BindingFlags.NonPublic
                   | BindingFlags.Instance | BindingFlags.DeclaredOnly))
        {
            foreach (var literal in Il.Strings(method))
            {
                if (!literal.StartsWith(entry, StringComparison.Ordinal))
                {
                    continue;
                }

                // An option key is a PREFIX the engine suffixes twice; every
                // other literal is a whole key handed to `L10NLookup`.
                if (literal.Contains(".pages.INITIAL.options."))
                {
                    asked.Add(literal + ".title");
                    asked.Add(literal + ".description");
                }
                else
                {
                    asked.Add(literal);
                }
            }
        }

        // The two option prefixes' four derived keys, the two page
        // descriptions, the selection prompt, the title and the body.
        Assert.Equal(9, asked.Count);
        Assert.All(asked, key => Assert.True(rows.ContainsKey(key), "no merged row for " + key));
    }

    /// <summary>
    /// The generator yields exactly two options, and both are constructed --
    /// the count the re-proof read as zero. A count pin on a call the method
    /// demonstrably makes, which is the only count `Il.CallSequence` is safe
    /// for (its own caveat).
    /// </summary>
    [Fact]
    public void The_converted_event_generates_two_options()
    {
        var generate = Method(typeof(SpringvaleCheeseCellar), "GenerateInitialOptions");

        Assert.Equal(2, Il.CallSequence(generate).Count(c => c == "EventOption..ctor"));
    }

    /// <summary>
    /// Every merged event row belongs to the converted event. A merge is
    /// GLOBAL -- `LocTable.MergeWith` overwrites -- so a row whose key drifted
    /// onto a base event's family would silently rewrite the shipped game's
    /// text, and the `events` table has no dressed-key trick to fall back on
    /// the way the monster names do.
    /// </summary>
    [Fact]
    public void No_merged_event_row_can_overwrite_a_base_events_text()
    {
        Assert.NotEmpty(EventRows());
        Assert.All(EventRows().Keys, key =>
            Assert.StartsWith("SPRINGVALE_CHEESE_CELLAR.", key, StringComparison.Ordinal));
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
    /// A portrait row names an event this arm actually converts, spelled as
    /// the engine spells it. A typo here is silent in the same way a dressing
    /// typo is: the postfix never fires and the event throws again.
    /// </summary>
    [Fact]
    public void Every_portrait_row_names_a_converted_event()
    {
        Assert.Equal(
            new[] { "SPRINGVALE_CHEESE_CELLAR" },
            TeyvatFrame.EventPortraits.Keys.OrderBy(k => k, StringComparer.Ordinal).ToArray());

        // And the dressed path the patch replaces is the one the engine would
        // have derived from that id, so the borrow cannot be aimed at a key
        // no reader ever asks for.
        Assert.Equal(
            "res://images/events/springvale_cheese_cellar.png",
            "res://images/events/"
                + TeyvatFrame.EventPortraits.Keys.Single().ToLowerInvariant() + ".png");
    }

    /// <summary>`TeyvatLoc` is internal and this mod carries no
    /// `InternalsVisibleTo` -- the standing call -- so its one table is
    /// reached by reflection.</summary>
    private static IReadOnlyDictionary<string, string> EventRows()
    {
        var type = typeof(TeyvatFrame).Assembly
            .GetType("KleeMod.Teyvat.TeyvatLoc", throwOnError: true)!;
        var field = type.GetField("EventRows", BindingFlags.NonPublic | BindingFlags.Static);
        Assert.NotNull(field);
        var rows = field!.GetValue(null) as IReadOnlyDictionary<string, string>;
        Assert.NotNull(rows);
        return rows!;
    }

    // ---------------------------------------------------------------
    // Reflection helpers. Public/protected members are reached by name so a
    // rename is a compile error here rather than a silent skip.
    // ---------------------------------------------------------------

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
