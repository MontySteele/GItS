using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;
using BaseLib.Abstracts;
using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-751 -- EVERY CUSTOM RESOURCE NAMES A TEXTURE THAT SHIPS.
///
/// THE DEFECT. Steam moved BaseLib from 3.4.5 to 3.4.7 (re-pinned on main in
/// #483). In 3.4.7 <c>BasicCustomResource.RegisterResourceVisuals&lt;T&gt;</c>
/// registers, through <c>ExtraCardUi.RegisterCreateCardUiElement</c>, a
/// <c>new NAdditionalCostDisplay(Id, TexturePath, MainColor)</c> for EVERY card
/// node, and that constructor calls
/// <c>ResourceLoader.Load&lt;Texture2D&gt;(imagePath, null, CacheMode 1)</c>
/// unconditionally -- there is no empty-path arm and no try/catch. The base
/// declaration is <c>public virtual string TexturePath =&gt; "";</c>. Our
/// twelve subclasses overrode none of it, so every card grid (Neow's removal
/// grid, a hand, a reward) logged
/// <c>ERROR: No loader found for resource: res:// (expected type: unknown)</c>
/// once per resource per card -- twelve resources times a ten-card grid is 120
/// lines -- and the understudy's error-storm guard tore the lane down on them.
///
/// WHAT THIS PINS, AND WHY IT IS A PIN RATHER THAN A ONE-TIME FIX. The twelve
/// overrides are one line each and nothing in the compiler or in any other
/// test notices when a THIRTEENTH resource is added without one: the defect is
/// structurally invisible in exactly the house sense -- it shows up only as
/// log noise in a live game, which is the surface the gates cannot see. So the
/// rule is enforced over the ASSEMBLY, by reflection, rather than over the
/// twelve names we happen to know today.
///
/// THE SHIPPING CHECK IS REAL, NOT A PREFIX MATCH. A path is only useful if
/// klee.pck actually carries the file, and the art tree itself
/// (<c>ImageGen/images</c>) is gitignored -- Tier F art never enters the
/// repo -- so "does the file exist" cannot be asked on disk from a checkout.
/// What IS in the repo is the two places a packed out-path can legitimately
/// come from: a row in <c>art/plan.tsv</c> (the fetch/process plan) or a
/// <c>GENERATOR_OWNED</c> entry in <c>tools/art_lint.py</c> (a path a
/// generator script writes, which by construction has no plan row). Every
/// PNG <c>tools/build_pck.ps1</c> copies is one or the other, so a declared
/// path that appears in neither is a path nothing produces.
///
/// The reading is deliberately NOT done by constructing a resource:
/// <c>BasicCustomResource</c>'s constructor chain reaches BaseLib and the
/// game, which is process death in this headless host (KleeTests/README, the
/// headless boundary). <c>GetUninitializedObject</c> runs no constructor, and
/// the getters under test compile to a single <c>ldstr</c>.
/// </summary>
public class KleeResourceTexturePathTests
{
    private const BindingFlags All =
        BindingFlags.Public | BindingFlags.NonPublic |
        BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly;

    /// <summary>
    /// The twelve as of EB-751. Named so the count assertion below says WHICH
    /// resource is new rather than only that the number moved -- a thirteenth
    /// is fine and expected, the point is that it arrives with an override.
    /// </summary>
    private static readonly string[] KnownTwelve =
    {
        "ChargeResource",
        "EncoreResource",
        "FanfareCapBonusResource",
        "FanfareFloorResource",
        "FanfareResource",
        "FurinaBurstResource",
        "KleeBurstResource",
        "KokomiBurstResource",
        "SpotlightModeResource",
        "SpotlightMovedResource",
        "SpotlightPlaysResource",
        "SpotlightSpendBoostResource",
    };

    private static List<Type> Resources() =>
        typeof(KleeBurstResource).Assembly
            .GetTypes()
            .Where(t => !t.IsAbstract && typeof(BasicCustomResource).IsAssignableFrom(t))
            .OrderBy(t => t.Name, StringComparer.Ordinal)
            .ToList();

    private static string TexturePathOf(Type t)
    {
        var getter = t.GetMethod("get_TexturePath", All);
        Assert.True(getter != null,
            t.Name + " does not OVERRIDE TexturePath. BaseLib 3.4.7 loads the "
            + "base's empty string for every card node; see EB-751.");

        var instance = RuntimeHelpers.GetUninitializedObject(t);
        return (string?)getter!.Invoke(instance, null) ?? "";
    }

    [Fact]
    public void The_resource_set_is_the_twelve_this_pin_was_written_against()
    {
        // Not a freeze: a thirteenth resource is a normal addition. It is here
        // so that the assertions below are known to have covered EVERY
        // resource, and so a rename shows up as a name rather than a count.
        var found = Resources().Select(t => t.Name).ToArray();

        Assert.Equal(KnownTwelve, found);
    }

    [Fact]
    public void Every_custom_resource_overrides_TexturePath_with_a_res_path()
    {
        foreach (var t in Resources())
        {
            var path = TexturePathOf(t);

            Assert.False(string.IsNullOrWhiteSpace(path),
                t.Name + ".TexturePath is empty; BaseLib 3.4.7 hands it to "
                + "ResourceLoader.Load unconditionally (EB-751).");
            Assert.StartsWith("res://", path, StringComparison.Ordinal);
            Assert.True(path.Length > "res://".Length,
                t.Name + ".TexturePath is a bare res:// root.");
            Assert.EndsWith(".png", path, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void Every_declared_texture_is_a_path_the_art_pipeline_produces()
    {
        var produced = ProducedOutPaths();

        foreach (var t in Resources())
        {
            var source = ImageGenSourceOf(TexturePathOf(t));

            Assert.True(produced.Contains(source),
                t.Name + ".TexturePath resolves to " + source
                + ", which has no row in art/plan.tsv and no GENERATOR_OWNED "
                + "entry in tools/art_lint.py -- nothing produces it, so "
                + "build_pck.ps1 cannot pack it and the load fails exactly as "
                + "the empty path did (EB-751).");
        }
    }

    /// <summary>
    /// The ImageGen out-path a packed res:// path is copied FROM, per
    /// `tools/build_pck.ps1`: Klee's surfaces predate the roster and live at
    /// `ImageGen/images/&lt;surface&gt;` while packing into the `klee/`
    /// namespace; Furina's and Kokomi's live under their own directory and
    /// pack under their own namespace.
    /// </summary>
    private static string ImageGenSourceOf(string resPath)
    {
        var relative = resPath.Substring("res://".Length);
        var slash = relative.IndexOf('/');
        Assert.True(slash > 0, "not a namespaced pck path: " + resPath);

        var ns = relative.Substring(0, slash);
        var rest = relative.Substring(slash + 1);

        return ns == "klee"
            ? "ImageGen/images/" + rest
            : "ImageGen/images/" + ns + "/" + rest;
    }

    /// <summary>
    /// Every ImageGen out-path the repo claims a producer for: the `out`
    /// column of `art/plan.tsv`, plus the `GENERATOR_OWNED` keys in
    /// `tools/art_lint.py` (paths a generator script writes, which L11 forbids
    /// a plan row from claiming).
    /// </summary>
    private static HashSet<string> ProducedOutPaths()
    {
        var produced = new HashSet<string>(StringComparer.Ordinal);

        foreach (var line in RepoFile("art/plan.tsv").Split('\n'))
        {
            var row = line.TrimEnd('\r');
            if (row.Length == 0 || row[0] == '#') continue;

            var columns = row.Split('\t');
            if (columns.Length > 1) produced.Add(columns[1].Trim());
        }

        foreach (Match m in Regex.Matches(
                     RepoFile("tools/art_lint.py"), "\"(ImageGen/images/[^\"]+)\""))
        {
            produced.Add(m.Groups[1].Value);
        }

        Assert.True(produced.Count > 50,
            "read only " + produced.Count + " art out-paths; the plan or the "
            + "lint registry moved and this check would pass vacuously.");
        return produced;
    }

    /// <summary>A repo-root-relative file, found by walking up from the test
    /// binary (the same walk `CompanionSlotRarityTests.Source` uses).</summary>
    private static string RepoFile(string relativePath)
    {
        var relative = relativePath.Replace('/', Path.DirectorySeparatorChar);
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = dir.Parent;
        }

        throw new FileNotFoundException(relative);
    }
}
