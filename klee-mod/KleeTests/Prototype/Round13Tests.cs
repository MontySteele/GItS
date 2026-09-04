using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 13, the legibility rows -- what a face has to say before it is read
/// for the first time.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round13Tests
{
    /// <summary>A generated card's printed face, off an instance allocated
    /// uninitialised: these `Localization` getters are pure string builders
    /// (`Round12Tests`' idiom, and the headless boundary's reason).</summary>
    private static string Face<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == "description").Item2;
    }

    // ==================================================================
    // `EB-446` -- a name one card is written against and another grants
    // ==================================================================
    //
    // THE FIND (Furina r7 (c) 5). <i>Fischl -- Nightrider</i> prints "If Oz is
    // out, he deals 5 Electro damage to a random enemy" and nothing on the
    // screen says what puts Oz out. The seat played it five times and never
    // learned: the thing the word names is a DIFFERENT companion card, the
    // Power <i>Fischl -- Oz, at Your Side</i>, which that run never held.
    //
    // `ForGrounded`'s SHAPE, and its argument: the attach travels with the
    // printed WORD (`gen_klee_cards.arm_keyword_tip_calls`), so the face that
    // names him carries the definition whether or not the deck can grant him
    // -- which is the state the seat was in for all five plays.

    [Fact]
    public void Nightrider_golds_the_name_it_cannot_grant()
    {
        var face = Face<ProtoMcFischlNightrider>();

        Assert.Contains("If [gold]Oz[/gold] is out", face);
    }

    [Fact]
    public void The_face_that_names_him_carries_the_definition()
    {
        // The whole of the fix: the tip is attached FROM THE FACE, so a reader
        // who has never seen the Power still gets told which card it is.
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlNightrider",
                                           "get_ExtraHoverTips")));
        Assert.Contains("ArmKeywordTips.ForOz",
                        Il.Calls(Il.Method("ProtoMcFischlOz",
                                           "get_ExtraHoverTips")));
    }

    // ==================================================================
    // `EB-454` -- the two elements that printed no tag
    // ==================================================================
    //
    // THE FIND (Kokomi r13 (c) 8). <i>Jean -- Gale Blade</i> "read as untyped
    // until a Reaction preview named Anemo mid-fight", on a screen where every
    // Hydro, Electro, Cryo and Pyro card carries its element. Anemo and Geo
    // leave no aura, so they got no gem and, until now, no keyword either --
    // and the keyword is the tag, not the gem.

    /// <summary>The `KleeKeywords` field a card's `CanonicalKeywords` LOADS.
    /// `ElementBadgeTests.KeywordFieldOf`'s scan, and its reason: BaseLib fills
    /// these fields at `ModelDb.Init`, so in this host every one of them reads
    /// `None` and comparing VALUES would pass for any element at all. A static
    /// field read is `ldsfld`, which `Il.Calls` cannot see, so the byte scan is
    /// the reachable form.</summary>
    private static string[] KeywordFieldsOf(System.Type card)
    {
        var body = card.GetProperty("CanonicalKeywords", HeadlessGame.All)!
            .GetGetMethod()!.GetMethodBody()!.GetILAsByteArray()!;
        var found = new List<string>();
        for (var i = 0; i < body.Length - 4; i++)
        {
            if (body[i] != 0x7E) continue;              // ldsfld
            try
            {
                var field = card.Module.ResolveField(
                    System.BitConverter.ToInt32(body, i + 1));
                if (field?.DeclaringType?.Name == "KleeKeywords")
                {
                    found.Add(field.Name);
                }
            }
            catch
            {
                // Not a field token. Expected while byte-scanning.
            }
        }

        return found.ToArray();
    }

    [Fact]
    public void Gale_blade_declares_the_element_its_damage_carries()
    {
        Assert.Contains("AppliesAnemo",
                        KeywordFieldsOf(typeof(ProtoMcJeanGaleBlade)));
    }

    [Fact]
    public void A_geo_face_declares_its_element_too()
    {
        // Both of the two, because "the tag map covers all six" is the claim
        // and Geo is the half no seat happened to report.
        Assert.Contains("AppliesGeo",
                        KeywordFieldsOf(typeof(ProtoMiGorouInuzaka)));
    }

    [Fact]
    public void The_two_that_leave_no_aura_still_draw_no_gem()
    {
        // THE SPLIT IS THE FIX, and it is why this is a separate assertion
        // rather than one wider map: the gem is the AURA's own icon -- the
        // badge a player will see on the enemy -- and there is none to paint
        // for an element that leaves nothing. `ElementBadge.IconPathFor` is
        // internal, so it is reached the way `ElementBadgeTests` reaches it.
        var badge = typeof(global::KleeMod.KleeMod).Assembly
            .GetTypes().Single(t => t.Name == "ElementBadge");
        var iconPathFor = badge.GetMethod("IconPathFor", HeadlessGame.All)!;

        Assert.Null(iconPathFor.Invoke(null, new object[] { Element.Anemo }));
        Assert.Null(iconPathFor.Invoke(null, new object[] { Element.Geo }));
        Assert.NotNull(iconPathFor.Invoke(null, new object[] { Element.Pyro }));
    }

    [Fact]
    public void The_tip_names_the_power_that_puts_him_out()
    {
        var body = string.Concat(Il.Strings(
            Il.Method("ArmKeywordTips", "ForOz")));

        Assert.Contains("Oz, at Your Side", body);
        // The title is quoted WITHOUT its `Fischl --` prefix: the text
        // conventions ban a dash of any kind in player-facing text, and the
        // lint bites on one.
        Assert.DoesNotContain("--", body);
    }
}
