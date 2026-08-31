using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-155`: a missing hover-tip TITLE row fails the self-check.
///
/// THE DEFECT. `KleeSelfCheck` R4 walks the card pool and R8 walks the
/// powers, so a keyword belonging to NEITHER -- a rider tip, a meter's word,
/// a salon member's hover -- was covered by nothing at all. Raw keys reached
/// live builds twice, both found by a person looking at a screen:
/// `Blocking Notes+` rendering "card_keywords.KLEEMOD-COMPANION_RIDER.title"
/// on a card-reward screen (0.2-589), and `Reinforcements` rendering
/// "card_keywords.KLEEMOD-MUSTER.title" on a shop screen (0.2-634).
///
/// WHAT R20 DOES. It finds the keyword ids BY REFLECTION rather than from a
/// list, because a curated list would have to be updated in the same commit
/// that adds the key -- and the failure being fixed IS the commit that adds a
/// key and forgets its row. Then it asks the merged `card_keywords` table for
/// each `.title`.
///
/// WHAT IS TESTED HERE AND WHY IN TWO HALVES. `LocManager` is outside the
/// headless boundary (README), so the table lookup itself cannot run. The key
/// DISCOVERY can, and does, against the real shipped assembly; the COVERAGE
/// claim is then read off the compiled `InjectLocStrings` with `Il.Strings`,
/// which is the actual registration, not a copy of it.
/// </summary>
public class KeywordTitleRowTests
{
    private static readonly Assembly Mod = typeof(global::KleeMod.KleeMod).Assembly;

    /// <summary>`KleeSelfCheck` is internal, like most of the mod: resolved by
    /// name off the shipped assembly, the way CoopSeamTests reaches
    /// `FightRecord`.</summary>
    private static readonly Type SelfCheck =
        Mod.GetTypes().First(t => t.Name == "KleeSelfCheck");

    private static IReadOnlyList<string> Keywords()
    {
        var method = SelfCheck.GetMethod("KeywordIds", HeadlessGame.All)!;
        var rows = (System.Collections.IEnumerable)method.Invoke(
            null, new object[] { Mod })!;
        return rows.Cast<object>()
            .Select(row => (string)row.GetType().GetField("Item2")!.GetValue(row)!)
            .ToList();
    }

    /// <summary>Every loc key registered by `KleeMod.InjectLocStrings`.
    /// `const` values are inlined AND folded, so `SomeTips.SomeKey + ".title"`
    /// compiles to one `ldstr` of the whole key -- which is exactly the string
    /// the game will look up.</summary>
    private static IReadOnlyCollection<string> Registered()
        => Il.Strings(typeof(global::KleeMod.KleeMod)
                          .GetMethod("InjectLocStrings", HeadlessGame.All)!);

    [Fact]
    public void The_rule_finds_the_two_keys_that_shipped_raw()
    {
        var keywords = Keywords();

        Assert.Contains("KLEEMOD-COMPANION_RIDER", keywords);
        Assert.Contains("KLEEMOD-MUSTER", keywords);
    }

    [Fact]
    public void The_rule_finds_every_tip_family_and_not_the_card_pool()
    {
        var keywords = Keywords();

        // One from each family that owns hover tips.
        Assert.Contains("KLEEMOD-FANFARE_RIDER", keywords);     // Furina riders
        Assert.Contains("KLEEMOD-KURAGE_PULSE_RIDER", keywords); // Kokomi riders
        Assert.Contains("KLEEMOD-TURNEND_MASQUE", keywords);     // the docket
        Assert.Contains("KLEEMOD-BURST", keywords);              // a meter word
        // EB-155 hoisted the three salon members out of a switch body: a key
        // that is only ever a literal inside a method is a key reflection
        // cannot see, which is the blind spot this rule exists to close.
        Assert.Contains("KLEEMOD-SALON_CRABALETTA", keywords);

        // NOT a fully-qualified loc key: SlyGrant's prompt carries a dot and
        // belongs to whatever table declares it, not to card_keywords.
        Assert.DoesNotContain(
            "KLEEMOD-SLY_GRANT.selectionScreenPrompt", keywords);
        Assert.All(keywords, k => Assert.DoesNotContain(".", k));
    }

    [Fact]
    public void Every_keyword_the_rule_finds_has_a_registered_title_row()
    {
        // The acceptance, read off the compiled registration. This is the
        // assertion that would have failed on 0.2-589 and on 0.2-634.
        var registered = Registered();

        var missing = Keywords()
            .Where(k => !registered.Contains($"{k}.title")).ToList();

        Assert.Empty(missing);
    }

    [Fact]
    public void A_keyword_with_no_row_is_reported_by_name()
    {
        // SEEN TO FAIL. The rule's decision, driven against a registration
        // that is missing one key -- the 0.2-634 state exactly.
        var keywords = Keywords();
        var asIfMusterHadNoRow = Registered()
            .Where(s => s != "KLEEMOD-MUSTER.title").ToList();

        var missing = keywords
            .Where(k => !asIfMusterHadNoRow.Contains($"{k}.title")).ToList();

        Assert.Equal(new[] { "KLEEMOD-MUSTER" }, missing);
    }

    [Fact]
    public void The_rule_is_wired_into_the_boot_check_and_counted()
    {
        // A rule nobody runs is not a rule; and RuleCount is printed in the
        // one line a live session reads ("SELFCHECK passed (N rule families)").
        var run = SelfCheck.GetMethod("Run", HeadlessGame.All)!;

        Assert.Contains(Il.Calls(run),
                        c => c.EndsWith("CheckKeywordTitleRows", StringComparison.Ordinal));
        Assert.Equal(20, (int)SelfCheck
            .GetField("RuleCount", HeadlessGame.All)!.GetValue(null)!);
    }
}
