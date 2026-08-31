using System;
using System.Linq;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// `EB-214` / R224 item 6 (`M54` pick 1): RULE 1 IS THE MUSTER KEYWORD'S OWN
/// TEXT, and the shipped keyword did not move.
///
/// WHY BOTH ARMS ARE IN ONE FILE. The claim has two halves and they are
/// opposite signs of the same fact: with `-p:PrototypeCards=true` the keyword
/// carries the memory-creation rule, and WITHOUT it the keyword is
/// byte-for-byte the text that has shipped since R78. A pin that could only
/// be compiled on one side of the switch could not say the second half -- the
/// reason KleeTests.csproj defines `PROTOTYPE_CARDS` as well as removing
/// `Prototype/` from the compile.
///
/// The reading is `Il.Strings`, i.e. the `ldstr` literals of the compiled
/// `ForMuster` (an iterator, so the harness walks its `MoveNext`). That is the
/// actual shipped text, not a copy of it: a tip whose wording moved cannot
/// pass this while a file-text grep could be satisfied by a comment.
///
/// The BUILD-LEVEL twin -- the release `klee.dll` is byte-identical across the
/// change -- is recorded in the commit rather than asserted here; nothing
/// headless can rebuild the other side of its own commit.
/// </summary>
public class KokomiMusterKeywordTests
{
    /// <summary>The literal chunks of R78's definition as `EB-254` amended it,
    /// which is what ships. Split the way the source splits them so a re-wrap
    /// of the source is not a false failure, while a WORDING change is a real
    /// one.
    ///
    /// `EB-254` MOVED THE DISCOUNT'S DURATION INTO THE SENTENCE, and that is
    /// the only thing that moved. The build is `EnergyCost.AddThisCombat`
    /// (`KokomiConscript.Recruit`), so "this combat" is the true scope; the
    /// bare phrase was the defect, because four sibling Companion faces print
    /// "cost 1 less this turn" for a rider that really is turn-scoped and a
    /// reader took the elision for the same duration
    /// (`playtest 2026-08-31 B2`).</summary>
    private static readonly string[] Shipped =
    {
        "[gold]Muster N[/gold]: transform N cards in your hand into ",
        "random Inazuma [gold]Companion[/gold] cards. Each costs ",
        " less this combat and [gold]Exhausts[/gold]. Kit ",
        "cards and Companions you already hold are never chosen.",
    };

    /// <summary>The phrase `EB-254` retired. A pin on the new words alone
    /// would still pass if somebody re-added the bare clause beside them.
    /// </summary>
    private const string Bare = " less and [gold]Exhausts[/gold].";

    private static string Blob()
        => string.Concat(Il.Strings(Il.Method("KokomiRiderTips", "ForMuster"))
                           .OrderBy(s => s, StringComparer.Ordinal));

    [Fact]
    public void The_shipped_muster_definition_is_word_for_word_R78s()
    {
        var blob = Blob();
        foreach (var chunk in Shipped)
        {
            Assert.Contains(chunk, blob, StringComparison.Ordinal);
        }
    }

    [Fact]
    public void The_discount_never_ships_without_its_duration_again()
    {
        // `EB-254`, the red half: the keyword's -1 is rest-of-COMBAT and the
        // sentence must say so. The bare clause is what a reader mistook for
        // the `this turn` its four siblings print.
        Assert.DoesNotContain(Bare, Blob(), StringComparison.Ordinal);
    }

#if PROTOTYPE_CARDS
    [Fact]
    public void Under_the_flag_the_keyword_also_carries_rule_one()
    {
        // §11.7 v3's ruled sentence, and the price `P3` asks a tester to be
        // able to state. One surface: this is the keyword's own body, not a
        // second tip beside it.
        var blob = Blob();

        Assert.Contains("creates a memory of the card it ate", blob,
                        StringComparison.Ordinal);
        Assert.Contains("recruit creates a second when it burns", blob,
                        StringComparison.Ordinal);
        Assert.Contains("[gold]Charge[/gold] equal to", blob,
                        StringComparison.Ordinal);
        Assert.Contains("x its Cost.", blob, StringComparison.Ordinal);
    }
#else
    [Fact]
    public void A_release_build_says_nothing_about_the_memory()
    {
        // THE RELEASE PIN. The rule is quarantined behind `#if
        // PROTOTYPE_CARDS`; a build without the property must not be able to
        // print a sentence about a jellyfish whose type it does not compile.
        var blob = Blob();

        Assert.DoesNotContain("memory", blob, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("Charge", blob, StringComparison.Ordinal);
        Assert.DoesNotContain("recruit", blob, StringComparison.OrdinalIgnoreCase);
    }
#endif
}
