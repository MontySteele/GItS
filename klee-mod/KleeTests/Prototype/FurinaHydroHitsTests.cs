#nullable enable

using System;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- HER HYDRO RIDES THE HIT (the seat round of 2026-09-26,
/// act 2 lane 2). Quick Cue's Spend mode ("deal 8 and apply Hydro") hit an
/// enemy wearing Pyro, Vaporize was listed, and the 8 landed at face value:
/// the row dealt a plain hit and then applied Hydro, so the reaction fired on
/// the application and multiplied nothing, and Courtroom Drama's Vulnerable
/// landed after the hit too. The ruling makes each such hit a Hydro hit, the
/// mechanism Klee's rows use. The sim's pins are
/// <c>tier0/tests/test_furina_hydro_hits.py</c>.
///
/// THE MULTIPLIER IS RUN FOR REAL HERE: <c>AuraPower.ModifyDamageMultiplicative</c>
/// on a harness body wearing Pyro, with the card as the source. What needs a
/// live combat (the aura's own lifecycle) is the sim's.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B).
/// </summary>
public class FurinaHydroHitsTests
{
    private static string Generated(string type,
                                    [CallerFilePath] string here = "")
    {
        var relative = Path.Combine("klee-mod", "KleeCode", "Cards",
                                    "Prototype", "Generated", type + ".cs");
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relative);
            if (File.Exists(candidate))
                return File.ReadAllText(candidate).Replace("\r\n", "\n");
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relative);
    }

    private static PyroAuraPower PyroOn(out MegaCrit.Sts2.Core.Entities.Creatures.Creature body)
    {
        var enemy = Seat.Klee(30).WithPower<PyroAuraPower>(2);
        body = enemy.Creature;
        return body.Powers.OfType<PyroAuraPower>().Single();
    }

    // ---- the scope ------------------------------------------------------------

    [Fact]
    public void A_carried_hit_prints_the_element_only_inside_its_scope()
    {
        var furina = Seat.Furina().Creature;
        var cue = new ProtoFsQuickCue();

        // Outside the scope Quick Cue is a plain Attack of a Skill-grade
        // character: its plain mode applies nothing, as before.
        Assert.IsNotAssignableFrom<IElementalCard>(cue);
        Assert.Equal(Element.None, CatalystCadence.PrintedElement(cue));

        using (HitElement.Carry(cue, Element.Hydro))
        {
            Assert.Equal(Element.Hydro,
                         CatalystCadence.PrintedElement(cue));
            Assert.Equal(Element.Hydro, AuraCmd.ElementOfPlay(cue, furina));
            // KEYED ON THE CARD: another copy is not carried.
            Assert.Equal(Element.None,
                         AuraCmd.ElementOfPlay(new ProtoFsQuickCue(), furina));
        }

        Assert.Equal(Element.None, AuraCmd.ElementOfPlay(cue, furina));
    }

    // ---- the finding, run for real -----------------------------------------

    [Fact]
    public void Vaporize_off_quick_cues_spend_mode_multiplies_its_eleven()
    {
        var furina = Seat.Furina().Creature;
        var cue = new ProtoFsQuickCue();
        var pyro = PyroOn(out var body);

        // The old shape: the hit carried nothing, so nothing multiplied it.
        Assert.Equal(1m, pyro.ModifyDamageMultiplicative(
            body, 11m, ValueProp.Move, furina, cue, null));

        using (HitElement.Carry(cue, Element.Hydro))
        {
            var mult = pyro.ModifyDamageMultiplicative(
                body, 11m, ValueProp.Move, furina, cue, null);
            Assert.Equal(ReactionTable.AmplifierMultiplier(
                Reaction.Vaporize, furina), mult);
            Assert.True(mult > 1m);
        }
    }

    [Fact]
    public void Courtroom_dramas_vulnerable_lands_on_the_reacting_hit()
    {
        // "Your first Elemental Reaction each turn applies 1 Vulnerable and 1
        // Weak to its target before the hit lands." It could not while the
        // Hydro came after the hit; with the Hydro on the hit, the reacting
        // hit is the one the Vulnerable multiplies.
        var furina = Seat.Furina().WithPower<CrossExaminationPower>(1).Creature;
        var cue = new ProtoFsQuickCue();
        var pyro = PyroOn(out var body);

        Assert.Equal(1m, pyro.ModifyDamageMultiplicative(
            body, 8m, ValueProp.Move, furina, cue, null));

        using (HitElement.Carry(cue, Element.Hydro))
        {
            Assert.Equal(
                ReactionTable.AmplifierMultiplier(Reaction.Vaporize, furina)
                * ReactionConstants.VulnerableTakenMult,
                pyro.ModifyDamageMultiplicative(
                    body, 8m, ValueProp.Move, furina, cue, null));
        }
    }

    [Fact]
    public void Grand_deluge_carries_hydro_on_every_hit_like_a_klee_row()
    {
        // Its one hit is its whole damage, so the card-level interface says
        // it, exactly as Klee's rows do.
        var furina = Seat.Furina().Creature;
        var deluge = new ProtoFsGrandDeluge();
        Assert.IsAssignableFrom<IElementalCard>(deluge);
        Assert.Equal(Element.Hydro, CatalystCadence.PrintedElement(deluge));
        var pyro = PyroOn(out var body);
        Assert.Equal(ReactionTable.AmplifierMultiplier(Reaction.Vaporize, furina),
                     pyro.ModifyDamageMultiplicative(
                         body, 10m, ValueProp.Move, furina, deluge, null));
    }

    // ---- the emitted plays ----------------------------------------------------

    [Theory]
    [InlineData("ProtoFsQuickCue")]
    [InlineData("ProtoFsTidalFlourish")]
    public void The_spend_modes_hit_carries_hydro_and_nothing_applies_it_after(
        string type)
    {
        var source = Generated(type);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", source);
        // The Spend mode's hit sits inside the scope, and the plain mode's
        // does not: one Carry, after the Spend, before the mode's attack.
        var spend = source.IndexOf("FurinaStage.Spend(", StringComparison.Ordinal);
        var carry = source.IndexOf("using (HitElement.Carry(this, Element.Hydro))",
                                   StringComparison.Ordinal);
        Assert.True(spend >= 0 && carry > spend, source);
        Assert.True(source.IndexOf("DamageCmd.Attack", carry,
                                   StringComparison.Ordinal) > carry);
        Assert.Equal(1, CountOf(source, "HitElement.Carry("));
        Assert.True(source.IndexOf("DamageCmd.Attack", StringComparison.Ordinal)
                    < spend, "the plain mode's hit comes first and is plain");
        // The Hydro tip no longer says the card applies without a hit.
        Assert.DoesNotContain("appliesWithoutHit: true", source);
        Assert.Contains("KleeKeywords.AppliesHydro", source);
    }

    [Fact]
    public void Quick_cues_spend_face_previews_inside_the_same_scope()
    {
        var source = Generated("ProtoFsQuickCue");
        Assert.Contains(
            // The rules pass (2026-10-01): 11 (was 14).
            "new FoldedDamageVar(\"BranchDamage\", 11m, ValueProp.Move, carries: Element.Hydro)",
            source);
        Assert.Contains(
            "new FoldedDamageVar(\"PlainDamage\", 3m, ValueProp.Move)", source);
        var cue = new ProtoFsQuickCue();
        Assert.Equal(Element.Hydro,
                     ((FoldedDamageVar)cue.DynamicVars["BranchDamage"]).Carries);
        Assert.Equal(Element.None,
                     ((FoldedDamageVar)cue.DynamicVars["PlainDamage"]).Carries);
    }

    [Fact]
    public void Bubble_arias_first_hit_carries_hydro_and_its_second_is_plain()
    {
        var source = Generated("ProtoFsBubbleAria");
        Assert.DoesNotContain("ElementalHit.ApplyOnly", source);
        Assert.DoesNotContain("WithHitCount", source);
        var carry = source.IndexOf("using (HitElement.Carry(this, Element.Hydro))",
                                   StringComparison.Ordinal);
        var first = source.IndexOf("DamageCmd.Attack(DynamicVars.Damage.BaseValue)",
                                   carry, StringComparison.Ordinal);
        var close = source.IndexOf("        }\n", first, StringComparison.Ordinal);
        var second = source.IndexOf("DamageCmd.Attack(DynamicVars.Damage.BaseValue)",
                                    close, StringComparison.Ordinal);
        Assert.True(carry >= 0 && first > carry && close > first && second > close,
                    source);
        Assert.Equal(2, CountOf(source, "DamageCmd.Attack("));
        // Both hits read the one var, so the upgrade moves both.
        Assert.Contains("DynamicVars.Damage.UpgradeValueBy(1m);", source);
        Assert.IsNotAssignableFrom<IElementalCard>(new ProtoFsBubbleAria());
    }

    [Fact]
    public void Grand_deluge_applies_nothing_after_its_hit()
    {
        var source = Generated("ProtoFsGrandDeluge");
        Assert.DoesNotContain("ElementalHit.ApplyOnly", source);
        Assert.Contains("public Element Element => Element.Hydro;", source);
        // The reaction count is read before the hit, so a reaction the hit
        // itself causes pays the performers.
        Assert.True(
            source.IndexOf("var reactionsAtStart", StringComparison.Ordinal)
            < source.IndexOf("DamageCmd.Attack", StringComparison.Ordinal));
    }

    private static int CountOf(string haystack, string needle)
    {
        var count = 0;
        for (var at = haystack.IndexOf(needle, StringComparison.Ordinal);
             at >= 0;
             at = haystack.IndexOf(needle, at + needle.Length,
                                   StringComparison.Ordinal))
        {
            count++;
        }
        return count;
    }
}
