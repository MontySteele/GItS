using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Elements;
using KleeMod.Tests.Harness;
using KleeMod.Vfx;
using MegaCrit.Sts2.Core.Commands;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE HIT'S LOOK AND THE BORROWED VOICES, pinned (2026-10-02, the combat
/// visual audit, gaps 3 and 4).
///
/// WHAT IS REACHABLE HERE. Spawning a scene is not: a Godot node is process
/// death in this host (README, the headless boundary). What the look DEPENDS
/// on is plain data -- the element-to-effect table, the reaction-to-beat
/// table, the base scene paths they name -- and the call graph that makes
/// each table the one door (IL call sets, labelled as structural pins). The
/// sound borrow's mapping is a pure string function and is run directly.
/// </summary>
public class ElementHitFxTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static readonly Element[] Elements =
        Enum.GetValues<Element>().Where(e => e != Element.None).ToArray();

    /// <summary>Every `const string` path on the base game's `VfxCmd`: the
    /// scenes it preloads by path. Read as raw constants, so the class's
    /// static constructor (which reaches Godot) never runs.</summary>
    private static HashSet<string> BaseVfxPaths() => typeof(VfxCmd)
        .GetFields(BindingFlags.Public | BindingFlags.Static)
        .Where(f => f.IsLiteral && f.FieldType == typeof(string))
        .Select(f => (string)f.GetRawConstantValue()!)
        .ToHashSet(StringComparer.Ordinal);

    [Fact]
    public void Every_element_has_its_own_look_and_none_is_the_old_slash()
    {
        var looks = Elements.Select(ElementHitFx.For).ToList();
        Assert.Equal(looks.Count, looks.Distinct().Count());
        Assert.DoesNotContain(looks, l => l.ScenePath == ElementHitFx.SlashPath);
        Assert.Equal(ElementHitFx.SlashPath, ElementHitFx.For(Element.None).ScenePath);
        Assert.Equal(ElementHitFx.HitNode.None, ElementHitFx.For(Element.None).Extra);
    }

    [Theory]
    [InlineData(Element.Pyro, null, ElementHitFx.HitNode.FireBurst)]
    [InlineData(Element.Hydro, null, ElementHitFx.HitNode.Splash)]
    [InlineData(Element.Electro, "vfx/vfx_attack_lightning", ElementHitFx.HitNode.None)]
    [InlineData(Element.Cryo, "vfx/vfx_starry_impact", ElementHitFx.HitNode.Splash)]
    [InlineData(Element.Anemo, "vfx/vfx_flying_slash", ElementHitFx.HitNode.None)]
    [InlineData(Element.Geo, "vfx/vfx_rock_shatter", ElementHitFx.HitNode.None)]
    public void The_element_table(Element element, string? path, ElementHitFx.HitNode node)
    {
        var spec = ElementHitFx.For(element);
        Assert.Equal(path, spec.ScenePath);
        Assert.Equal(node, spec.Extra);
        // A splash with no tint would read as milk on every body.
        if (node == ElementHitFx.HitNode.Splash) Assert.NotNull(spec.TintHex);
    }

    [Fact]
    public void Every_path_scene_is_one_the_base_game_preloads()
    {
        var preloaded = BaseVfxPaths();
        Assert.NotEmpty(preloaded);
        foreach (var e in Elements.Append(Element.None))
        {
            var path = ElementHitFx.For(e).ScenePath;
            if (path != null) Assert.Contains(path, preloaded);
        }
    }

    [Fact]
    public void Every_reaction_has_a_beat_and_the_flash_fits_the_budget()
    {
        foreach (var r in Enum.GetValues<Reaction>().Where(r => r != Reaction.None))
        {
            var beat = ReactionFx.For(r, Element.Hydro);
            Assert.NotEqual(ReactionFx.Effect.None, beat.Effect);
            Assert.StartsWith("#", beat.FlashHex);
        }
        Assert.Equal(ReactionFx.Effect.None, ReactionFx.For(Reaction.None).Effect);
        // The brief: a reaction adds no more than about 0.2 s, and the beat
        // waits on nothing, so the flash itself is the whole cost.
        Assert.True(ReactionFx.FlashSeconds <= 0.2f);
    }

    [Fact]
    public void Swirl_flashes_the_colour_of_what_it_spread()
    {
        Assert.Equal(ReactionFx.ElementFlashHex(Element.Pyro),
                     ReactionFx.For(Reaction.Swirl, Element.Pyro).FlashHex);
        Assert.NotEqual(ReactionFx.For(Reaction.Swirl, Element.Pyro).FlashHex,
                        ReactionFx.For(Reaction.Swirl, Element.Cryo).FlashHex);
    }

    // ---- structural pins: one door each ------------------------------------

    [Fact]
    public void The_one_reaction_site_plays_the_beat()
    {
        // STRUCTURAL. `ReactionEffects.Resolve` is the single site every
        // reaction resolves in, so calling the beat there is "every reaction
        // draws, once".
        Assert.Contains("ReactionFx.Play",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
    }

    [Fact]
    public void A_non_attack_elemental_hit_draws_its_element()
    {
        // STRUCTURAL. Bombs, performers and Plans hit through these two.
        Assert.Contains("ElementHitFx.SpawnOn", Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("ElementHitFx.SpawnOn",
                        Il.Calls(Il.Method("ElementalHit", "DealAsIfAura")));
    }

    [Fact]
    public void No_generated_card_picks_its_hit_scene_by_hand()
    {
        // STRUCTURAL. Every generated Attack goes through the element door;
        // a regen that brought the literal slash back fails here.
        var generated = typeof(ElementHitFx).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && !t.IsNested)
            .Select(t => t.GetMethod("OnPlay", All | BindingFlags.DeclaredOnly))
            .Where(m => m != null)
            .Select(m => Il.Calls(m!))
            .ToList();

        Assert.DoesNotContain(generated, calls => calls.Contains("AttackCommand.WithHitFx"));
        Assert.True(
            // 80, not 100, since the Salon's Tab (2026-10-05) took Furina's
            // pool from 78 rows to the slice's 24.
            generated.Count(calls => calls.Contains("ElementHitFx.WithElementHitFx")) >= 80,
            "expected the generated Attacks to route through ElementHitFx");
    }

    // ---- the borrowed voices (KleeAssetPathFallback) -----------------------

    private static readonly Type Fallback =
        Il.Method("KleeAssetPathFallback", "RedirectSfx").DeclaringType!;

    private static string? Donor(string name) =>
        (string?)Fallback.GetMethod("SfxDonorFor", All)!.Invoke(null, new object[] { name });

    private static string Redirect(string property, string path, string entry, string donor) =>
        (string)Fallback.GetMethod("RedirectSfx", All)!
            .Invoke(null, new object[] { property, path, entry, donor })!;

    [Theory]
    [InlineData("klee", "ironclad")]
    [InlineData("furina", "silent")]
    [InlineData("kokomi", "necrobinder")]
    [InlineData("varka", "regent")]
    public void Each_character_borrows_one_base_voice(string name, string donor)
    {
        Assert.Equal(donor, Donor(name));
    }

    [Fact]
    public void An_unknown_character_borrows_nothing()
    {
        Assert.Null(Donor("ironclad"));
    }

    [Fact]
    public void The_id_derived_events_swap_the_id()
    {
        Assert.Equal(
            "event:/sfx/characters/regent/regent_attack",
            Redirect("AttackSfx",
                     "event:/sfx/characters/kleemod-varka/kleemod-varka_attack",
                     "kleemod-varka", "regent"));
        Assert.Equal(
            "event:/sfx/characters/silent/silent_die",
            Redirect("DeathSfx",
                     "event:/sfx/characters/kleemod-furina/kleemod-furina_die",
                     "kleemod-furina", "silent"));
    }

    [Theory]
    [InlineData("silent", "event:/sfx/ui/wipe_silent")]
    [InlineData("ironclad", "event:/sfx/ui/wipe_ironclad")]
    // The 0.111.0 decompile: Regent, Necrobinder and Defect override the
    // wipe to the Ironclad's, so wipe_regent does not exist.
    [InlineData("regent", "event:/sfx/ui/wipe_ironclad")]
    [InlineData("necrobinder", "event:/sfx/ui/wipe_ironclad")]
    public void The_transition_wipe_is_the_donors_real_one(string donor, string want)
    {
        Assert.Equal(want, Redirect("CharacterTransitionSfx",
                                    "event:/sfx/ui/wipe_kleemod-x", "kleemod-x", donor));
    }

    [Fact]
    public void Only_the_five_sound_events_are_borrowed_for_the_other_three()
    {
        var set = (HashSet<string>)Fallback.GetField("SfxProperties", All)!.GetValue(null)!;
        Assert.Equal(
            new[] { "AttackSfx", "CastSfx", "CharacterSelectSfx",
                    "CharacterTransitionSfx", "DeathSfx" },
            set.OrderBy(s => s, StringComparer.Ordinal).ToArray());
    }
}
