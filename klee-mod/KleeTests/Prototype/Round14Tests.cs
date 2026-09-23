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

    // R276 MOVED BOTH HALVES OF THIS. Pick 1 gave Kurage's Oath a Block
    // now-line, so its face-up half no longer hits and it is a Plan-only-hit
    // row; pick 2 made every damaging card of hers elemental under the arm,
    // so a Skill's own hit is Hydro without a per-row declaration. The pins
    // below are the finding's rule on the rows that carry it now.

    [Fact]
    public void A_skills_face_up_hit_declares_hydro()
    {
        var card = new ProtoKkOpeningGambit();

        Assert.IsAssignableFrom<IElementalCard>(card);
        Assert.Equal(Element.Hydro, ((IElementalCard)card).Element);
        // The Oath's face-up half is Block now, and declares nothing.
        Assert.IsNotAssignableFrom<IElementalCard>(new ProtoKkKuragesOath());
    }

    [Fact]
    public void The_declaration_is_what_the_cadence_reads()
    {
        // The join, and the reason the interface is enough: the cadence asks
        // `IElementalCard` before it asks anything about the card's type, so
        // this Skill's own hit is a Hydro hit at the aura funnel.
        Assert.Equal(Element.Hydro,
            CatalystCadence.PrintedElement(new ProtoKkOpeningGambit(), null));
    }

    [Fact]
    public void The_plan_element_rider_rides_the_plan_only_hits()
    {
        // `ForPlanElement` rides the rows whose Plan is their only hit: the
        // Oath (Block now, Plan 7 to ALL) and Feigned Retreat. A row whose
        // face-up half hits carries the gem instead.
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKkKuragesOath", "get_ExtraHoverTips")),
            c => c.Contains("ForPlanElement"));
        Assert.Contains(
            Il.Calls(Il.Method("ProtoKkFeignedRetreat", "get_ExtraHoverTips")),
            c => c.Contains("ForPlanElement"));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoKkOpeningGambit", "get_ExtraHoverTips")),
            c => c.Contains("ForPlanElement"));
    }

    [Fact]
    public void EB561_war_councils_hit_obeys_its_one_aura_statement()
    {
        // `EB-561`. THE FIND (Kokomi r20 lane 1): the face said "Its own hit
        // applies no aura" and four Wrigglers came out of a direct play
        // wearing Hydro -- the Tamakushi Casket's answering strike (`EB-562`).
        //
        // THE HIT WAS NEVER THE DEFECT. Played directly the card applies Weak
        // to every enemy and nothing else: no damage, no elemental call, so no
        // aura and no reaction. R276 pick 1 made its Plan Energy, so neither
        // half hits and the face carries no aura statement at all.
        var play = Il.Calls(Il.Method("ProtoKkWarCouncil", "OnPlay"));
        Assert.DoesNotContain(play, c => c.Contains("ElementalHit"));
        Assert.DoesNotContain(play, c => c.Contains("Aura"));
        Assert.Contains(play, c => c.Contains("PowerCmd.Apply"));

        Assert.DoesNotContain(
            Il.Calls(Il.Method("ProtoKkWarCouncil", "get_ExtraHoverTips")),
            c => c.Contains("ForPlanElement"));
        Assert.IsNotAssignableFrom<IElementalCard>(new ProtoKkWarCouncil());
    }
    [Fact]
    public void Klees_mint_keeps_the_gate_the_performance_lost()
    {
        // The other half, and the reason the gate existed: LAW:145 bounds what
        // a Companion play GENERATES, so the Spark mint still asks.
        var calls = Il.Calls(
            Il.Method("KleeElementalHooks", "AfterCardPlayed"));

        Assert.Contains(calls, c => c.Contains("IsFirstInSeries"));
    }

    [Fact]
    public void The_arm_face_no_longer_promises_one_performance()
    {
        // `ReplayNextCompanionPower`'s arm clause said "Your Salon performs on
        // the first play only" and printed a rule that is gone. The shipped
        // face is true on every arm again, so there is one face and no
        // `smartDescriptionReframe` row to pick between.
        var strings = Il.Strings(
            Il.Method("ReplayNextCompanionPower", "get_Localization"));

        Assert.DoesNotContain(strings, s => s.Contains("first play only"));
        Assert.DoesNotContain(strings,
            s => s.Contains("smartDescriptionReframe"));
        Assert.Contains(strings, s => s.Contains("extra time"));
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
