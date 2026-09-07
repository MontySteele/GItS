using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-626`: the self-check's R6b said seven power descriptions were broken,
/// and the check was the thing that was wrong.
///
/// THE FIND ([USER]'s run, godot.log 2026-09-07). Seven lines, all the same
/// shape -- `"[blue]" is not a known BBCode tag` -- against
/// `MasqueRedDeathPower`, `CeremonialGarmentPower`, `WarBannerPower`,
/// `SoumetsuPower`, `SesshouSakuraPower`, `SanctifyingRingPower` and
/// `MujiMujiDarumaPower`.
///
/// `[blue]` IS THE BASE GAME'S OWN TAG, which is what makes all seven false
/// positives. It is how a shipped power or relic string marks a numeral:
/// `KleeMod.InjectLocStrings` carries two shipped descriptions verbatim off
/// `SlayTheSpire2.pck` v0.111.0 and both use it, and
/// `docs/current/text-conventions.md` records it as a measured convention of
/// the corpus rather than a house style. `KleeSelfCheck.KnownBbcodeTags`
/// simply did not list it.
///
/// WHY ONLY SEVEN OF EIGHTY-THREE. The mod prints `[blue]` in 83 power
/// descriptions. R6b is reached through `CheckLocEntry`, which R8 calls for
/// the powers `ModelDb.AllPowers` actually holds at boot -- so the seven are
/// the registered ones the sweep reached on that run, not a class of string
/// that differs from the other seventy-six. There was never a second kind of
/// defect hiding among them, which is the thing this file is here to
/// establish: the check below runs over EVERY power in the assembly, not the
/// seven, and finds nothing.
///
/// WHAT IS RUN HERE. `CheckLocSyntax` itself, off the shipped assembly by
/// reflection (`KleeSelfCheck` is internal and this mod carries no
/// `InternalsVisibleTo` -- the standing call, and `KeywordTitleRowTests`
/// reaches it the same way), against each power's own `Localization` rows.
/// `LocManager` is outside the headless boundary (README), so what cannot run
/// is the TABLE lookup; the syntax rule is pure and runs exactly as it does in
/// the game.
/// </summary>
public class SelfCheckBbcodeTests
{
    private static readonly Assembly Mod =
        typeof(global::KleeMod.KleeMod).Assembly;

    private static readonly Type SelfCheck =
        Mod.GetTypes().First(t => t.Name == "KleeSelfCheck");

    /// <summary>The mutable finding list the rule appends to.</summary>
    private static IList Findings() =>
        (IList)SelfCheck.GetField("Findings", HeadlessGame.All)!.GetValue(null)!;

    private static IReadOnlyList<string> Check(string owner, string key,
                                               string raw)
    {
        var findings = Findings();
        findings.Clear();
        SelfCheck.GetMethod("CheckLocSyntax", HeadlessGame.All)!
            .Invoke(null, new object?[] { owner, key, raw });
        return findings.Cast<string>().ToList();
    }

    /// <summary>Every power this mod ships that states its own strings.
    /// Concrete, constructible, and read the way the game reads them.</summary>
    private static IEnumerable<(string Owner, string Key, string Raw)> Rows()
    {
        foreach (var type in Mod.GetTypes()
                     .Where(t => !t.IsAbstract
                                 && typeof(PowerModel).IsAssignableFrom(t)
                                 && typeof(ILocalizationProvider)
                                     .IsAssignableFrom(t))
                     .OrderBy(t => t.Name))
        {
            object? instance;
            try
            {
                instance = Activator.CreateInstance(type);
            }
            catch (MissingMethodException)
            {
                // A power with no parameterless constructor is not one the
                // game registers by itself either.
                continue;
            }

            var rows = ((ILocalizationProvider)instance!).Localization;
            if (rows == null) continue;
            foreach (var (suffix, raw) in rows)
            {
                yield return (type.Name, suffix, raw);
            }
        }
    }

    [Fact]
    public void No_power_description_in_this_assembly_trips_R6b()
    {
        var hits = Rows()
            .SelectMany(r => Check(r.Owner, r.Key, r.Raw))
            .Where(f => f.StartsWith("[R6b]", StringComparison.Ordinal))
            .ToList();

        Assert.Empty(hits);
    }

    [Fact]
    public void The_seven_the_run_reported_are_clean_and_still_say_what_they_said()
    {
        // Named, because a fix to a list is only as good as the strings it was
        // supposed to be about. Each is checked BY ITS OWN Localization, so a
        // reworded description is read here rather than a copy of one.
        // Five of the seven are the Inazuma companion arm, which a release
        // build Compile-Removes -- so the two SHIPPED ones are required and
        // the arm's five are checked wherever the build has them. Under
        // `-p:PrototypeCards=true`, which is the configuration the gate runs
        // and the configuration [USER]'s run was in, that is all seven.
        var required = new[] { "MasqueRedDeathPower",
                               "CeremonialGarmentPower" };
        foreach (var name in required.Concat(new[]
                 {
                     "WarBannerPower", "SoumetsuPower", "SesshouSakuraPower",
                     "SanctifyingRingPower", "MujiMujiDarumaPower",
                 }))
        {
            var rows = Rows().Where(r => r.Owner == name).ToList();
            if (rows.Count == 0)
            {
                Assert.DoesNotContain(name, required);
                continue;
            }
            // Each one really does print the tag -- otherwise this would pass
            // by the strings having quietly been rewritten, which is the one
            // outcome the row forbade.
            Assert.Contains(rows, r => r.Raw.Contains("[blue]",
                                                      StringComparison.Ordinal));
            foreach (var row in rows)
            {
                Assert.Empty(Check(row.Owner, row.Key, row.Raw));
            }
        }
    }

    [Fact]
    public void The_rule_still_bites_on_a_variable_written_as_a_tag()
    {
        // A check nobody has watched fail is not a check, and this is the
        // failure R6b exists for: a DynamicVar written "[Block]" collides with
        // the [center] wrapper the card renderer adds and throws.
        var hits = Check("Fake", "x.description", "Gain [Block] Block.");
        Assert.Single(hits);
        Assert.StartsWith("[R6b]", hits[0], StringComparison.Ordinal);
        Assert.Contains("not a known BBCode tag", hits[0]);

        // And R6a beside it, so the harness is reading the real rule.
        Assert.Contains(Check("Fake", "x.description", "Gain {{Damage}}."),
                        f => f.StartsWith("[R6a]", StringComparison.Ordinal));
    }

    [Fact]
    public void Blue_is_on_the_list_because_the_shipped_strings_use_it()
    {
        // The citation, in code: the two base-game descriptions the mod
        // re-registers are quoted verbatim off the pck and both mark their
        // numerals with the tag. If those ever stop using it, this goes red
        // and the list's reason goes with it.
        // The re-registration itself is behind the prototype arm, so what is
        // read here is the source it is written in -- the quotation is the
        // citation either way, and the file is in the tests' own tree.
        Assert.Contains(
            "Vulnerable creatures take [blue]50%[/blue] more ",
            Source("KleeMod.cs"));

        var tags = (IEnumerable<string>)SelfCheck
            .GetField("KnownBbcodeTags", HeadlessGame.All)!.GetValue(null)!;
        Assert.Contains("blue", tags);
    }

    /// <summary>The text-pin idiom used across these tests: read the SOURCE
    /// out of the repo above the test binary, never a copy beside the dll.
    /// </summary>
    private static string Source(string relativePath) =>
        Read(System.IO.Path.Combine("klee-mod", "KleeCode",
            relativePath.Replace('/', System.IO.Path.DirectorySeparatorChar)));

    private static string Read(string relative)
    {
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = System.IO.Path.Combine(dir.FullName, relative);
            if (System.IO.File.Exists(candidate))
            {
                return System.IO.File.ReadAllText(candidate);
            }
            dir = dir.Parent;
        }

        throw new System.IO.FileNotFoundException(
            "no " + relative + " above " + AppContext.BaseDirectory);
    }
}
