using System;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>The one collection every pin that flips a
/// <see cref="TriggerRules"/> switch runs in, so no two flip it at once.</summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class TriggerRulesSwitches
{
    public const string Name = "TriggerRulesSwitches";
}

/// <summary>
/// THE ELEMENT PORT, PHASE ONE: fresh and spent auras, Swirl pays, Crystallize
/// keeps the aura (<c>review/ruled/element-home-review-2026-09-28.md</c> §3,
/// §4, §7; ruled §6, [USER]: "That makes sense").
///
/// WHAT CAN BE PINNED HERE. A hit landing needs a live combat
/// (<c>PowerCmd</c>, <c>CreatureCmd</c>, a <c>CombatState</c>), outside the
/// headless boundary this project draws. So the rule is written as ONE pure
/// decision, <see cref="TriggerRules.Outcome"/>, pinned value by value on
/// both sides of each switch, and the call graph is pinned to prove every
/// lifecycle site takes that decision rather than its own. The same scenarios
/// run end to end in the sim: <c>tier0/tests/test_element_port.py</c>.
/// </summary>
[Collection(TriggerRulesSwitches.Name)]
public class ElementPortTests : IDisposable
{
    private readonly bool _swirl = TriggerRules.SwirlPays;
    private readonly bool _crystallize = TriggerRules.CrystallizeKeepsAura;

    public ElementPortTests() => HeadlessGame.Arm();

    public void Dispose()
    {
        TriggerRules.SwirlPays = _swirl;
        TriggerRules.CrystallizeKeepsAura = _crystallize;
        ReactionEvents.ResetFight();
    }

    private static void Switches(bool swirl, bool crystallize)
    {
        TriggerRules.SwirlPays = swirl;
        TriggerRules.CrystallizeKeepsAura = crystallize;
    }

    private static TriggerRules.HitOutcome Hit(Element aura, bool spent, Element trigger) =>
        TriggerRules.Outcome(aura, spent, trigger);

    // --- the defaults -------------------------------------------------------

    // ON in every build that names neither property (Directory.Build.props).
    // SKIPPED, NOT LEFT TO FAIL, where the build opts them out
    // (-p:ShippedKits=true, or -p:SwirlPays=false / -p:CrystallizeKeepsAura=false):
    // there the property moved the value this pin asserts
    // (docs/current/operations/prototype.md carries the rule).
#if SWIRL_PAYS && CRYSTALLIZE_KEEPS_AURA
    [Fact]
#else
    [Fact(Skip = "This build opts the element port out (-p:ShippedKits=true, -p:SwirlPays=false or -p:CrystallizeKeepsAura=false), which moves the defaults this pin asserts.")]
#endif
    public void Both_changes_ship_on()
    {
        Assert.True(TriggerRules.DefaultSwirlPays);
        Assert.True(TriggerRules.DefaultCrystallizeKeepsAura);
        Assert.Equal(TriggerRules.DefaultSwirlPays, TriggerRules.SwirlPays);
        Assert.Equal(TriggerRules.DefaultCrystallizeKeepsAura, TriggerRules.CrystallizeKeepsAura);
    }

    [Fact]
    public void The_flat_two_is_the_sims_number()
    {
        // `lint_constant_parity` compares it by value too (SWIRL_DAMAGE).
        Assert.Equal(2, ReactionConstants.SwirlDamage);
    }

    // --- the shared rule, both switches on ------------------------------------

    [Fact]
    public void A_trigger_on_a_fresh_aura_reacts_and_spends_it()
    {
        Switches(true, true);
        Assert.Equal(TriggerRules.HitOutcome.Spend, Hit(Element.Pyro, false, Element.Anemo));
        Assert.Equal(TriggerRules.HitOutcome.Spend, Hit(Element.Electro, false, Element.Geo));
        Assert.Equal(Reaction.Swirl, TriggerRules.ReactionFor(Element.Pyro, false, Element.Anemo));
        Assert.Equal(Reaction.Crystallize, TriggerRules.ReactionFor(Element.Electro, false, Element.Geo));
    }

    [Fact]
    public void A_trigger_on_a_spent_aura_pays_nothing()
    {
        // Covers: a second Anemo hit on the same aura, a spread copy (it
        // arrives spent), Geo on spent, and Swirl-then-Crystallize on one aura
        // (the Swirl spent it, so Crystallize gets nothing).
        Switches(true, true);
        foreach (var aura in new[] { Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo })
        {
            Assert.Equal(TriggerRules.HitOutcome.SpentNothing, Hit(aura, true, Element.Anemo));
            Assert.Equal(TriggerRules.HitOutcome.SpentNothing, Hit(aura, true, Element.Geo));
            Assert.Equal(Reaction.None, TriggerRules.ReactionFor(aura, true, Element.Anemo));
            Assert.Equal(Reaction.None, TriggerRules.ReactionFor(aura, true, Element.Geo));
        }
    }

    [Fact]
    public void Its_own_element_refreshes_a_spent_aura()
    {
        // Refresh is the outcome that clears Spent at every site
        // (AuraPower.ResolveLifecycle, ElementalHit.ResolveOnAura), so a
        // trigger after it reacts again.
        Switches(true, true);
        Assert.Equal(TriggerRules.HitOutcome.Refresh, Hit(Element.Pyro, true, Element.Pyro));
        Assert.Equal(TriggerRules.HitOutcome.Spend, Hit(Element.Pyro, false, Element.Geo));
    }

    [Fact]
    public void Pyro_onto_a_spent_hydro_aura_still_vaporizes()
    {
        Switches(true, true);
        Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(Element.Hydro, true, Element.Pyro));
        var reaction = TriggerRules.ReactionFor(Element.Hydro, true, Element.Pyro);
        Assert.Equal(Reaction.Vaporize, reaction);
        Assert.Equal(ReactionConstants.VaporizeMult, ReactionTable.AmplifierMultiplier(reaction));
    }

    [Fact]
    public void No_aura_or_no_element_is_nothing()
    {
        Switches(true, true);
        Assert.Equal(TriggerRules.HitOutcome.Nothing, Hit(Element.None, false, Element.Anemo));
        Assert.Equal(TriggerRules.HitOutcome.Nothing, Hit(Element.Pyro, false, Element.None));
    }

    [Fact]
    public void The_spread_refreshes_the_same_element_and_copies_onto_the_rest()
    {
        // Amended 2026-10-01 ([USER]): "reapplying the same element as a
        // refresh mechanic feels fine and we shouldn't let that brick other
        // reactions." A body wearing it already, fresh or spent, is
        // refreshed; another element or none takes a spent copy, as today.
        Assert.Equal(TriggerRules.SpreadOutcome.Refresh, TriggerRules.SpreadOn(Element.Pyro, Element.Pyro));
        Assert.Equal(TriggerRules.SpreadOutcome.Copy, TriggerRules.SpreadOn(Element.Pyro, Element.Electro));
        Assert.Equal(TriggerRules.SpreadOutcome.Copy, TriggerRules.SpreadOn(Element.Pyro, Element.None));
    }

    [Fact]
    public void The_spread_refresh_makes_the_aura_fresh_at_full_duration_and_reacts_with_nothing()
    {
        // STRUCTURAL: the refresh clears Spent, resets the clock through the
        // one duration funnel a fresh application uses, and flashes the badge.
        // It resolves no reaction.
        var refresh = Il.Calls(Il.Method("AuraPower", "RefreshFromSpread"));
        Assert.Contains("AuraPower.set_Spent", refresh);
        Assert.Contains("AuraCmd.Refresh", refresh);
        Assert.DoesNotContain("ReactionEffects.Resolve", refresh);
        Assert.Contains("AuraCmd.Duration", Il.Calls(Il.Method("AuraCmd", "Refresh")));
        Assert.Contains("AuraPower.RefreshFromSpread",
                        Il.Calls(Il.Method("ReactionEffects", "SwirlPays")));
    }

    // --- each switch alone (§6 pick 4.4), and both off --------------------

    [Fact]
    public void Swirl_alone_leaves_crystallize_consuming_even_a_spent_aura()
    {
        Switches(true, false);
        Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(Element.Pyro, true, Element.Geo));
        Assert.Equal(TriggerRules.HitOutcome.SpentNothing, Hit(Element.Pyro, true, Element.Anemo));
        Assert.Equal("Anemo", TriggerRules.SpentTriggers());
    }

    [Fact]
    public void Crystallize_alone_leaves_swirl_consuming_even_a_spent_aura()
    {
        Switches(false, true);
        Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(Element.Pyro, true, Element.Anemo));
        Assert.Equal(TriggerRules.HitOutcome.SpentNothing, Hit(Element.Pyro, true, Element.Geo));
        Assert.Equal("Geo", TriggerRules.SpentTriggers());
    }

    [Fact]
    public void Both_off_is_todays_consume_and_react_for_every_pair()
    {
        Switches(false, false);
        var all = new[] { Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo, Element.Anemo, Element.Geo };
        foreach (var aura in all.Where(e => e.LeavesAura()))
        foreach (var trigger in all)
        foreach (var spent in new[] { false, true })
        {
            var expected = aura == trigger
                ? TriggerRules.HitOutcome.Refresh
                : TriggerRules.HitOutcome.Consume;
            Assert.Equal(expected, Hit(aura, spent, trigger));
            Assert.Equal(aura == trigger ? Reaction.None : ReactionTable.Lookup(aura, trigger),
                         TriggerRules.ReactionFor(aura, spent, trigger));
        }
        Assert.Equal(string.Empty, TriggerRules.SpentTriggers());
    }

    // --- the badge (§7.1) ----------------------------------------------------

    [Fact]
    public void A_new_aura_is_fresh_and_the_badge_has_a_spent_face()
    {
        var aura = (PyroAuraPower)RuntimeHelpers.GetUninitializedObject(typeof(PyroAuraPower));
        Assert.False(aura.Spent);
        Assert.Equal("smartDescriptionSpent", AuraPower.SpentKey);
        Switches(true, true);
        var face = aura.Localization!.Single(row => row.Item1 == AuraPower.SpentKey).Item2;
        Assert.StartsWith("Spent: Anemo and Geo do nothing to it until Pyro hits it again.", face);
    }

    // --- every lifecycle site takes the one decision (STRUCTURAL) ------------

    [Fact]
    public void Every_site_that_resolves_a_hit_on_an_aura_asks_TriggerRules()
    {
        Assert.Contains("TriggerRules.Outcome", Il.Calls(Il.Method("AuraPower", "ResolveLifecycle")));
        Assert.Contains("TriggerRules.Outcome", Il.Calls(Il.Method("ElementalHit", "ResolveOnAura")));
        Assert.Contains("ElementalHit.ResolveOnAura", Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("ElementalHit.ResolveOnAura", Il.Calls(Il.Method("ElementalHit", "ApplyOnly")));
        // The damage forecast (Courtroom Drama's first-reaction Vulnerable)
        // asks the spent-aware question too, so a trigger that pays nothing
        // forecasts nothing.
        Assert.Contains("TriggerRules.ReactionFor",
                        Il.Calls(Il.Method("AuraPower", "ModifyDamageMultiplicative")));
        // And the preview that explains a spent aura.
        Assert.Contains("TriggerRules.Outcome", Il.Calls(Il.Method("KleeCardTooltips", "ForCard")));
    }

    [Fact]
    public void The_swirls_two_is_the_overload_splash_call_and_reacts_with_nothing()
    {
        var swirl = Il.Calls(Il.Method("ReactionEffects", "SwirlPays"));
        Assert.Contains("CreatureCmd.Damage", swirl);
        Assert.Contains("TriggerRules.SpreadOn", swirl);
        // Element-less: not through either elemental door.
        Assert.DoesNotContain("ElementalHit.Deal", swirl);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", swirl);
        Assert.Contains("ReactionEffects.SwirlPays", Il.Calls(Il.Method("ReactionEffects", "Resolve")));
    }

    // --- the one reaction event (§7.3) ---------------------------------------

    [Fact]
    public void Every_reaction_is_raised_from_the_one_funnel()
    {
        Assert.Contains("ReactionEvents.Raise", Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        Assert.Contains("ReactionEvents.CardPlayBegins",
                        Il.Calls(Il.Method("KleeElementalHooks", "BeforeCardPlayed")));
        Assert.Contains("ReactionEvents.CardPlayEnds",
                        Il.Calls(Il.Method("KleeElementalHooks", "AfterCardPlayed")));
    }

    private static CardModel Card(Type type) =>
        (CardModel)RuntimeHelpers.GetUninitializedObject(type);

    [Fact]
    public void The_source_kind_is_the_card_resolving_or_automatic()
    {
        ReactionEvents.ResetFight();
        Assert.Equal(ReactionSourceKind.Automatic, ReactionEvents.SourceKindFor(null));

        var companionType = typeof(ICompanionCard).Assembly.GetTypes()
            .First(t => !t.IsAbstract && typeof(CardModel).IsAssignableFrom(t)
                        && typeof(ICompanionCard).IsAssignableFrom(t));
        var cardType = typeof(ICompanionCard).Assembly.GetTypes()
            .First(t => !t.IsAbstract && typeof(CardModel).IsAssignableFrom(t)
                        && !typeof(ICompanionCard).IsAssignableFrom(t));
        var companion = Card(companionType);
        var card = Card(cardType);

        Assert.Equal(ReactionSourceKind.Card, ReactionEvents.SourceKindFor(card));
        Assert.Equal(ReactionSourceKind.Companion, ReactionEvents.SourceKindFor(companion));

        // A reaction with no card source inside a play (a Set off, a
        // damage-less Swirl op) is the resolving card's.
        ReactionEvents.CardPlayBegins(card);
        Assert.Equal(ReactionSourceKind.Card, ReactionEvents.SourceKindFor(null));
        ReactionEvents.CardPlayBegins(companion);
        Assert.Equal(ReactionSourceKind.Companion, ReactionEvents.SourceKindFor(null));
        ReactionEvents.CardPlayEnds(companion);
        Assert.Equal(ReactionSourceKind.Card, ReactionEvents.SourceKindFor(null));
        ReactionEvents.CardPlayEnds(card);
        Assert.Equal(ReactionSourceKind.Automatic, ReactionEvents.SourceKindFor(null));
    }

    [Fact]
    public void A_partner_is_the_dealer_seen_from_another_player()
    {
        var klee = Seat.Klee().Creature;
        var furina = Seat.Furina().Creature;
        var fromKlee = new ReactionEvent(Reaction.Swirl, furina, klee, ReactionSourceKind.Card);
        Assert.True(fromKlee.IsPartnerOf(furina));
        Assert.False(fromKlee.IsPartnerOf(klee));
        var automatic = new ReactionEvent(Reaction.Swirl, furina, null, ReactionSourceKind.Automatic);
        Assert.False(automatic.IsPartnerOf(furina));
    }
}
