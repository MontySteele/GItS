using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-531` -- the two faces written near Grounded, so neither drifts on to
/// the other's rule.
///
/// KAEYA'S HALF IS BUILT (`EB-576`): Cold-Blooded Strike and the buff it
/// leaves behind both print "This turn, Grounded counts a Bomb as on the
/// field", which is the rule `EB-516` gave the engine. Its words are pinned
/// here beside the other half's.
///
/// JEAN'S HALF IS THIS FILE'S OWN CLAIM. Lion's Fang, Fair Protector keeps its
/// own condition -- "if none of your Bombs went off last turn" -- and neither
/// its card nor its Power names Grounded anywhere a player can read, so no tip
/// sends a reader to Grounded's rule to understand Jean's. The behavioural
/// discriminator (a turn that opens with a Bomb on the field AFTER one went
/// off pays Grounded and not Lion's Fang) needs a live `CombatState` and is
/// pinned in tier0, `test_eb531_the_two_grounded_faces.py`.
///
/// NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
/// </summary>
public class GroundedFacesTests
{
    private const BindingFlags All =
        BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;

    [Fact]
    public void Jeans_card_keeps_its_own_condition_and_never_names_grounded()
    {
        var face = Face(new ProtoMcJeanLionsFang());

        Assert.Contains("if none of your [gold]Bombs[/gold] went off last turn",
            face);
        Assert.DoesNotContain("Grounded", face);
    }

    [Fact]
    public void Jeans_power_keeps_its_own_condition_and_never_names_grounded()
    {
        var face = Row<LionsFangPower>("description");

        Assert.Contains("went off last turn", face);
        Assert.DoesNotContain("Grounded", face);
    }

    [Fact]
    public void Kaeyas_card_names_the_rule_the_engine_has()
    {
        var face = Face(new ProtoMcKaeyaColdBloodedStrike());

        Assert.Contains("counts a Bomb as on the field", face);
        Assert.DoesNotContain("counts nothing as having gone off", face);
    }

    [Fact]
    public void Kaeyas_buff_says_the_same_sentence_the_card_did()
    {
        var face = Row<ColdBloodedPower>("description");

        Assert.Contains("counts a Bomb as on the field", face);
        Assert.DoesNotContain("counts nothing as having gone off", face);
    }

    [Fact]
    public void Only_kaeyas_face_carries_the_grounded_definition()
    {
        // The tip travels with the WORD, so the card that prints Grounded
        // carries its definition and the card that does not, does not.
        var kaeya = Source(
            "Cards/Prototype/Generated/ProtoMcKaeyaColdBloodedStrike.cs");
        var jean = Source(
            "Cards/Prototype/Generated/ProtoMcJeanLionsFang.cs");

        Assert.Contains("ArmKeywordTips.ForGrounded", kaeya);
        Assert.DoesNotContain("ArmKeywordTips.ForGrounded", jean);
    }

    // ---- helpers ---------------------------------------------------------

    private static string Face(CustomCardModel card) =>
        card.Localization!.First(r => r.Item1 == "description").Item2;

    /// <summary>A power's loc rows off an instance allocated uninitialised:
    /// these getters are pure string builders (<c>DefenceShelfTests</c>'
    /// idiom).</summary>
    private static string Row<T>(string key) where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", All)!.GetValue(model)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

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

        throw new System.IO.FileNotFoundException(relative);
    }
}
