using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Teyvat;
using KleeMod.Teyvat.Acts;
using KleeMod.Teyvat.Patches;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Events;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE DRESSED ANCIENTS' pins (R275, 2026-09-17).
///
/// WHAT A HEADLESS SUITE CAN SAY HERE is bounded exactly as `TeyvatFrameTests`
/// says: `ModelDb` is not populated outside the game, so no test below
/// constructs an `AncientEventModel` or calls `ModelDb.AncientEvent`. The
/// `Dressings` table's VALUES are `Func<AncientEventModel>` for that reason --
/// a pin can count and key them without ever invoking one.
///
/// What it CAN do is the two things that matter most, and both are exercised
/// for real rather than structurally.
///
/// First, THE LOC DERIVATION. `LocTable`'s constructor is public, so a fake
/// `ancients` table can be built here and handed to
/// `TeyvatAncients.RowsFor` -- which means the alias pass, the promise that
/// an empty faces-file cell keeps the game's own line, and the promise that no
/// boon row is ever written are all pinned against real code and not against a
/// comment.
///
/// Second, THE POOL. `Dress` is a pure function over a sequence and a face, so
/// its length, its order and its arm-off identity are all directly testable
/// with fakes standing in for the models.
/// </summary>
public class TeyvatAncientsTests : IDisposable
{
    private readonly bool _enabled = TeyvatFrame.Enabled;

    public void Dispose() => TeyvatFrame.Enabled = _enabled;

    /// <summary>The slate R275 ruled, as (base Ancient, face, dressed name).
    /// Written out here rather than read from the generated table, so the pin
    /// fails when the generator and the ruling disagree.</summary>
    public static IEnumerable<object[]> Slate => new[]
    {
        new object[] { "NEOW", "MONDSTADT", "Dvalin" },
        new object[] { "NEOW", "LIYUE", "Moon Carver" },
        new object[] { "OROBAS", "NATLAN", "Xbalanque" },
        new object[] { "OROBAS", "INAZUMA", "the Sacred Sakura" },
        new object[] { "PAEL", "NATLAN", "Och-Kan" },
        new object[] { "PAEL", "INAZUMA", "Orobashi" },
        new object[] { "TEZCATARA", "NATLAN", "Tezcatara" },
        new object[] { "TEZCATARA", "INAZUMA", "Ioroi" },
        new object[] { "NONUPEIPE", "FONTAINE", "Egeria" },
        new object[] { "NONUPEIPE", "SUMERU", "Greater Lord Rukkhadevata" },
        new object[] { "TANX", "FONTAINE", "Elynas" },
        new object[] { "TANX", "SUMERU", "Apep" },
        new object[] { "VAKUU", "FONTAINE", "Remus" },
        new object[] { "VAKUU", "SUMERU", "King Deshret" },
        new object[] { "DARV", "NATLAN", "Alice" },
        new object[] { "DARV", "INAZUMA", "Alice" },
        new object[] { "DARV", "FONTAINE", "Alice" },
        new object[] { "DARV", "SUMERU", "Alice" },
    };

    // ==================================================================
    // THE BODIES
    // ==================================================================

    [Theory]
    [MemberData(nameof(Slate))]
    public void Every_slate_row_has_a_body_with_the_ruled_name(
        string baseEntry, string face, string name)
    {
        var dressed = TeyvatGeneratedAncients.BaseEntries
            .Where(kv => kv.Value == baseEntry)
            .Select(kv => kv.Key)
            .Where(e => TeyvatGeneratedAncients.FacePools[face].Contains(e))
            .ToList();

        var entry = Assert.Single(dressed);
        Assert.Equal(name,
            TeyvatGeneratedAncients.Rows[entry + ".title"]);
    }

    /// <summary>
    /// A dressed Ancient is A NAME AND A BASE AND NOTHING ELSE. If one ever
    /// carried a member, the mechanic it changed would be invisible to every
    /// other pin here -- so the shape is asserted directly.
    /// </summary>
    [Fact]
    public void A_dressed_ancient_declares_no_member_of_its_own()
    {
        foreach (var type in DressedTypes())
        {
            Assert.True(type.IsSealed, $"{type.Name} is not sealed");
            Assert.DoesNotContain(
                type.GetMembers(BindingFlags.Public | BindingFlags.NonPublic
                                | BindingFlags.Instance | BindingFlags.Static
                                | BindingFlags.DeclaredOnly),
                m => m is not ConstructorInfo);
        }
    }

    /// <summary>
    /// `Id.Entry` is `StringHelper.Slugify(type.Name)` (`ModelDb.GetEntry`),
    /// and EVERYTHING -- the title key, the epithet key, every dialogue key,
    /// all five asset paths -- hangs off it. So the generator's table and the
    /// engine's derivation are pinned to agree, with the engine's own helper.
    /// </summary>
    [Fact]
    public void Every_dressed_entry_is_its_own_class_name_slugified()
    {
        var byEntry = DressedTypes().ToDictionary(
            t => StringHelper.Slugify(t.Name), t => t);

        Assert.Equal(TeyvatGeneratedAncients.BaseEntries.Keys.OrderBy(k => k),
                     byEntry.Keys.OrderBy(k => k));

        foreach (var (entry, type) in byEntry)
        {
            Assert.Equal(TeyvatGeneratedAncients.BaseEntries[entry],
                         StringHelper.Slugify(type.BaseType!.Name));
        }
    }

    /// <summary>A dressed entry that collided with a base Ancient's would make
    /// the merge rewrite the shipped game's own text, globally.</summary>
    [Fact]
    public void No_dressed_entry_collides_with_a_base_ancients()
    {
        var bases = TeyvatGeneratedAncients.BaseEntries.Values.ToHashSet();
        foreach (var dressed in TeyvatGeneratedAncients.BaseEntries.Keys)
        {
            Assert.DoesNotContain(dressed, bases);
        }
    }

    // ==================================================================
    // THE POOLS
    // ==================================================================

    [Theory]
    [InlineData("MONDSTADT", 1)]
    [InlineData("LIYUE", 1)]
    [InlineData("NATLAN", 3)]
    [InlineData("INAZUMA", 3)]
    [InlineData("FONTAINE", 3)]
    [InlineData("SUMERU", 3)]
    public void A_faces_act_pool_is_the_base_acts_length(string face, int count)
    {
        // The base acts' own pools: Overgrowth and Underdocks hold Neow alone,
        // the Hive holds Orobas / Pael / Tezcatara, Glory holds Nonupeipe /
        // Tanx / Vakuu. Darv belongs to no act and is excluded here; the pin
        // below is his.
        var actPool = TeyvatGeneratedAncients.FacePools[face]
            .Where(e => TeyvatGeneratedAncients.BaseEntries[e] != "DARV")
            .ToList();

        Assert.Equal(count, actPool.Count);
    }

    [Theory]
    [InlineData("NATLAN")]
    [InlineData("INAZUMA")]
    [InlineData("FONTAINE")]
    [InlineData("SUMERU")]
    public void Darv_is_dressed_on_every_act_2_and_act_3_face(string face)
    {
        var darv = TeyvatGeneratedAncients.FacePools[face]
            .Where(e => TeyvatGeneratedAncients.BaseEntries[e] == "DARV")
            .ToList();

        Assert.Single(darv);
        Assert.Equal("Alice", TeyvatGeneratedAncients.Rows[darv[0] + ".title"]);
        Assert.True(
            TeyvatGeneratedAncients.Dressings.ContainsKey((face, typeof(Darv))),
            $"{face} has no dressing for Darv, so "
            + $"{nameof(ActModel_SetSharedAncientSubset_TeyvatAncients_Patch)} "
            + "would hand the act the base Darv");
    }

    [Fact]
    public void Act_1_deals_no_shared_ancient_so_neither_face_dresses_darv()
    {
        // `RunManager.GenerateRooms` walks `State.Acts.Skip(1)`, so act 1 is
        // never handed a shared Ancient. A Darv body on an act-1 face would be
        // one nothing could ever reach.
        foreach (var face in new[] { "MONDSTADT", "LIYUE" })
        {
            Assert.DoesNotContain(
                TeyvatGeneratedAncients.FacePools[face],
                e => TeyvatGeneratedAncients.BaseEntries[e] == "DARV");
        }
    }

    [Fact]
    public void Dress_is_the_identity_with_the_arm_off()
    {
        TeyvatFrame.Enabled = false;
        var source = new AncientEventModel[3];

        Assert.Same(source, TeyvatGeneratedAncients.Dress("MONDSTADT", source));
    }

    [Fact]
    public void Dress_never_adds_or_drops_an_ancient()
    {
        // `Dress` is a `Select`, which is the whole length argument -- a pin
        // rather than a comment, because a future edit to a `Where` here would
        // move every roll `ActModel.GenerateRooms` makes after the pool.
        TeyvatFrame.Enabled = true;
        var source = new AncientEventModel?[4];

        Assert.Equal(4,
            TeyvatGeneratedAncients.Dress("NATLAN", source!).Count());
    }

    // ==================================================================
    // THE LOC DERIVATION
    // ==================================================================

    /// <summary>
    /// A stand-in `ancients` table carrying one base Ancient's whole key
    /// family, in the shapes the real pack uses.
    /// </summary>
    private static LocTable FakeAncients() => new("ancients",
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["NEOW.title"] = "BASE TITLE",
            ["NEOW.epithet"] = "BASE EPITHET",
            ["NEOW.results.prefix"] = "BASE PREFIX",
            ["NEOW.pages.DONE.description"] = "BASE DONE",
            // An option row: the shape a boon's title takes when the base
            // game gives one at all.
            ["NEOW.pages.INITIAL.options.ARCANE_SCROLL.title"] = "BASE BOON",
            // A dialogue line, and its Next button.
            ["NEOW.talk.firstVisitEver.0-0.ancient"] = "BASE HELLO",
            ["NEOW.talk.ANY.0-0r.ancient"] = "BASE REPEAT",
            ["NEOW.talk.ANY.0-0r.next"] = "BASE NEXT",
            // Another Ancient's family, to prove the prefix does not leak.
            ["DARV.title"] = "DARV TITLE",
        });

    [Fact]
    public void An_empty_faces_cell_keeps_the_games_own_line()
    {
        TeyvatFrame.Enabled = true;
        var rows = TeyvatAncients.RowsFor(FakeAncients());

        // The faces file writes only the name today, so every other row of
        // Neow's family reaches the dressed entry as the game's own words.
        Assert.Equal("BASE EPITHET", rows["DVALIN_MONDSTADT.epithet"]);
        Assert.Equal("BASE PREFIX", rows["DVALIN_MONDSTADT.results.prefix"]);
        Assert.Equal("BASE DONE", rows["DVALIN_MONDSTADT.pages.DONE.description"]);
        Assert.Equal("BASE HELLO",
            rows["DVALIN_MONDSTADT.talk.firstVisitEver.0-0.ancient"]);
        Assert.Equal("BASE REPEAT", rows["DVALIN_MONDSTADT.talk.ANY.0-0r.ancient"]);
        Assert.Equal("BASE NEXT", rows["DVALIN_MONDSTADT.talk.ANY.0-0r.next"]);
    }

    [Fact]
    public void The_dressed_name_wins_over_the_alias()
    {
        TeyvatFrame.Enabled = true;
        var rows = TeyvatAncients.RowsFor(FakeAncients());

        Assert.Equal("Dvalin", rows["DVALIN_MONDSTADT.title"]);
        Assert.Equal("Moon Carver", rows["MOON_CARVER_LIYUE.title"]);
    }

    [Fact]
    public void The_boon_row_is_the_games_and_the_generator_writes_none()
    {
        TeyvatFrame.Enabled = true;
        var rows = TeyvatAncients.RowsFor(FakeAncients());

        // The alias carries the game's own option row across unchanged...
        Assert.Equal("BASE BOON",
            rows["DVALIN_MONDSTADT.pages.INITIAL.options.ARCANE_SCROLL.title"]);

        // ...and nothing the generator emits is an option row. An Ancient's
        // options are `RelicOption<T>()`, and `EventOption.FromRelic` falls
        // through to the relic's own rows for any key the event lacks, so a
        // dressed option row is the ONE way this arm could reword a boon.
        Assert.DoesNotContain(TeyvatGeneratedAncients.Rows.Keys,
                              k => k.Contains(".options."));
    }

    [Fact]
    public void No_merged_row_reaches_a_base_ancients_key()
    {
        TeyvatFrame.Enabled = true;
        var rows = TeyvatAncients.RowsFor(FakeAncients());
        var bases = TeyvatGeneratedAncients.BaseEntries.Values.ToHashSet();

        // `LocTable.MergeWith` overwrites, so one stray key here would rewrite
        // the shipped game's text for everyone.
        foreach (var key in rows.Keys)
        {
            var entry = key.Split('.')[0];
            Assert.DoesNotContain(entry, bases);
            Assert.Contains(entry, TeyvatGeneratedAncients.BaseEntries.Keys);
        }
    }

    [Fact]
    public void The_alias_does_not_leak_between_ancients()
    {
        TeyvatFrame.Enabled = true;
        var rows = TeyvatAncients.RowsFor(FakeAncients());

        // Darv's family is in the fake table too. Neow's dressings must carry
        // Neow's keys and only Neow's: a prefix match that forgot its dot, or
        // one that walked the whole table, would put `DARV.title`'s words
        // under a Neow dressing.
        Assert.False(rows.ContainsKey("DVALIN_MONDSTADT.DARV.title"));
        Assert.False(rows.ContainsKey("DVALIN_MONDSTADT.talk.ANY.0-0r.char"));

        // And Alice takes Darv's, not Neow's -- she has no `results.prefix`
        // because Darv has none.
        Assert.False(rows.ContainsKey("ALICE_NATLAN.results.prefix"));
    }

    // ==================================================================
    // THE PICTURE
    // ==================================================================

    [Fact]
    public void The_picture_table_is_the_generators_and_is_off_with_the_arm()
    {
        TeyvatFrame.Enabled = false;
        Assert.Null(AncientPicture.BaseEntry("DVALIN_MONDSTADT"));

        TeyvatFrame.Enabled = true;
        Assert.Equal("NEOW", AncientPicture.BaseEntry("DVALIN_MONDSTADT"));

        // A base Ancient, and anything else, gets nothing back -- so every one
        // of the five path postfixes returns on its first branch.
        Assert.Null(AncientPicture.BaseEntry("NEOW"));
        Assert.Null(AncientPicture.BaseEntry("ROOM_FULL_OF_CHEESE"));
        Assert.Null(AncientPicture.BaseEntry(null));
    }

    private static IEnumerable<Type> DressedTypes() =>
        typeof(TeyvatFrame).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Teyvat.Ancients"
                        && typeof(AncientEventModel).IsAssignableFrom(t));
}
