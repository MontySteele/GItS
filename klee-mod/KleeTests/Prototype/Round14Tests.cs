using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 14, the rows the seats filed against faces that promised one thing
/// and did another.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class Round14Tests
{
    /// <summary>A generated card's printed face, off an instance allocated
    /// uninitialised: these `Localization` getters are pure string builders
    /// (`Round13Tests`' idiom, and the headless boundary's reason).</summary>
    private static string Face<T>() where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization")!.GetValue(model)!;
        return rows.Single(r => r.Item1 == "description").Item2;
    }

    // ==================================================================
    // `EB-462` -- the tag and the rider disagreed, and the tag won
    // ==================================================================
    //
    // THE FIND (Kokomi r14 (c) 4). <i>Kurage's Oath</i> prints [Hydro] in its
    // title while a rider said "its own hit applies no aura -- the Bake-Kurage
    // carries out the Plan as a Hydro hit, which does". The seat built a turn
    // on the tag: the same Electro-then-Hydro sequence that reacted through
    // <i>Deep Current</i> did nothing through the Oath's now-line.
    //
    // THE RULING (D default, the r14 packet sec.4): the now-line applies Hydro
    // like the carry-out, and the rider goes. It is declared ON THE SHEET --
    // `applies_element: true` on the row's own damage clause -- which is a
    // field both engines already read, so the two cannot drift: the generator
    // emits `IElementalCard` from it and `effects._element_for` answers off the
    // same key. `CatalystCadence.PrintedElement` tests `IElementalCard` FIRST,
    // before it asks whether the card is an Attack, so a Skill that declares
    // one elements its own hit.

    [Fact]
    public void The_oaths_now_line_declares_hydro()
    {
        var card = new ProtoKkKuragesOath();

        Assert.IsAssignableFrom<IElementalCard>(card);
        Assert.Equal(Element.Hydro, ((IElementalCard)card).Element);
    }

    [Fact]
    public void The_declaration_is_what_the_cadence_reads()
    {
        // The join, and the reason the interface is enough: the cadence asks
        // `IElementalCard` before it asks anything about the card's type, so
        // this Skill's own hit is a Hydro hit at the aura funnel.
        Assert.Equal(Element.Hydro,
            CatalystCadence.PrintedElement(new ProtoKkKuragesOath(), null));
    }

    [Fact]
    public void The_no_aura_rider_is_off_this_face()
    {
        // `ForPlanElement` explains a disagreement that no longer exists here.
        // It still rides the rows whose now-line really does apply nothing --
        // Ambush, Chain of Command, War Council -- so the pin is that this one
        // is not among them.
        var tips = Il.Calls(
            Il.Method("ProtoKkKuragesOath", "get_ExtraHoverTips"));

        Assert.DoesNotContain(tips, c => c.Contains("ForPlanElement"));
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKkAmbush", "get_ExtraHoverTips")),
            c => c.Contains("ForPlanElement"));
    }

    [Fact]
    public void The_face_still_prints_the_plan_it_writes()
    {
        // Nothing about the printed rules moved: this is an element the card
        // was already tagged with, applied where the tag said it was.
        var face = Face<ProtoKkKuragesOath>();

        Assert.Contains("damage to ALL enemies.", face);
        Assert.Contains("[gold]Plan[/gold]", face);
        Assert.DoesNotContain("aura", face);
    }
}
