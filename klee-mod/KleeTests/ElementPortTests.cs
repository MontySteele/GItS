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
/// THE ELEMENT PORT (<c>review/ruled/element-home-review-2026-09-28.md</c> §4 A;
/// ruled §6), AS AMENDED 2026-10-03: no spent auras; EVERY reaction consumes
/// its aura, Swirl and Crystallize included. [USER]: "Should we get rid of
/// the concept of elements being 'spent' after a swirl? It seems to generate
/// confusion." then "agreed ... please proceed".
///
/// WHAT CAN BE PINNED HERE. A hit landing needs a live combat
/// (<c>PowerCmd</c>, <c>CreatureCmd</c>, a <c>CombatState</c>), outside the
/// headless boundary this project draws. So the rule is written as ONE pure
/// decision, <see cref="TriggerRules.Outcome"/>, pinned value by value, and
/// the call graph is pinned to prove every lifecycle site takes that decision
/// rather than its own. The same scenarios run end to end in the sim
/// (<c>tier0/tests/test_element_port.py</c>): Swirl consumes, copies arrive
/// fresh, a Swirl ALL over three enemies and one Pyro aura pays three times,
/// Crystallize consumes, and nothing recurses.
/// </summary>
[Collection(TriggerRulesSwitches.Name)]
public class ElementPortTests : IDisposable
{
    private readonly bool _swirl = TriggerRules.SwirlPays;

    public ElementPortTests() => HeadlessGame.Arm();

    public void Dispose()
    {
        TriggerRules.SwirlPays = _swirl;
        ReactionEvents.ResetFight();
    }

    private static TriggerRules.HitOutcome Hit(Element aura, Element trigger) =>
        TriggerRules.Outcome(aura, trigger);

    // --- the default --------------------------------------------------------

    // ON in every build that does not name the property (Directory.Build.props).
    // SKIPPED, NOT LEFT TO FAIL, where the build opts it out
    // (-p:SwirlPays=false): there the property moved the value this pin
    // asserts (docs/current/operations/prototype.md carries the rule).
#if SWIRL_PAYS
    [Fact]
#else
    [Fact(Skip = "This build opts Swirl's payoff out (-p:SwirlPays=false), which moves the default this pin asserts.")]
#endif
    public void Swirl_pays_ships_on()
    {
        Assert.True(TriggerRules.DefaultSwirlPays);
        Assert.Equal(TriggerRules.DefaultSwirlPays, TriggerRules.SwirlPays);
    }

    [Fact]
    public void The_flat_two_is_the_sims_number()
    {
        // `lint_constant_parity` compares it by value too (SWIRL_DAMAGE).
        Assert.Equal(2, ReactionConstants.SwirlDamage);
    }

    // --- the one rule: every reaction consumes ------------------------------

    [Fact]
    public void Swirl_and_crystallize_consume_the_aura_like_every_reaction()
    {
        foreach (var swirl in new[] { true, false })
        {
            TriggerRules.SwirlPays = swirl;
            foreach (var aura in new[] { Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo })
            {
                Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(aura, Element.Anemo));
                Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(aura, Element.Geo));
            }
        }
    }

    [Fact]
    public void Every_pair_is_refresh_or_consume_and_nothing_else()
    {
        var all = new[] { Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo, Element.Anemo, Element.Geo };
        foreach (var aura in all.Where(e => e.LeavesAura()))
        foreach (var trigger in all)
        {
            var expected = aura == trigger
                ? TriggerRules.HitOutcome.Refresh
                : TriggerRules.HitOutcome.Consume;
            Assert.Equal(expected, Hit(aura, trigger));
        }
        // The outcome enum carries no spent state any more.
        Assert.Equal(new[] { "Nothing", "Refresh", "Consume" },
                     Enum.GetNames(typeof(TriggerRules.HitOutcome)));
    }

    [Fact]
    public void Pyro_onto_hydro_still_vaporizes()
    {
        Assert.Equal(TriggerRules.HitOutcome.Consume, Hit(Element.Hydro, Element.Pyro));
        var reaction = ReactionTable.Lookup(Element.Hydro, Element.Pyro);
        Assert.Equal(Reaction.Vaporize, reaction);
        Assert.Equal(ReactionConstants.VaporizeMult, ReactionTable.AmplifierMultiplier(reaction));
    }

    [Fact]
    public void No_aura_or_no_element_is_nothing()
    {
        Assert.Equal(TriggerRules.HitOutcome.Nothing, Hit(Element.None, Element.Anemo));
        Assert.Equal(TriggerRules.HitOutcome.Nothing, Hit(Element.Pyro, Element.None));
    }

    [Fact]
    public void The_aura_has_no_spent_state_and_no_spent_face()
    {
        Assert.Null(typeof(AuraPower).GetProperty("Spent",
            BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance));
        Assert.Null(typeof(AuraPower).GetField("SpentKey",
            BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static));
        var aura = (PyroAuraPower)RuntimeHelpers.GetUninitializedObject(typeof(PyroAuraPower));
        Assert.DoesNotContain(aura.Localization!, row => row.Item2.Contains("pent"));
    }

    [Fact]
    public void The_spread_refreshes_the_same_element_and_copies_onto_the_rest()
    {
        // Amended 2026-10-01 ([USER]): "reapplying the same element as a
        // refresh mechanic feels fine and we shouldn't let that brick other
        // reactions." A body wearing it already is refreshed; another
        // element or none takes a fresh copy, as today.
        Assert.Equal(TriggerRules.SpreadOutcome.Refresh, TriggerRules.SpreadOn(Element.Pyro, Element.Pyro));
        Assert.Equal(TriggerRules.SpreadOutcome.Copy, TriggerRules.SpreadOn(Element.Pyro, Element.Electro));
        Assert.Equal(TriggerRules.SpreadOutcome.Copy, TriggerRules.SpreadOn(Element.Pyro, Element.None));
    }

    [Fact]
    public void The_spread_refresh_resets_the_clock_and_reacts_with_nothing()
    {
        // STRUCTURAL: the refresh resets the clock through the one duration
        // funnel a fresh application uses and flashes the badge. It resolves
        // no reaction.
        var refresh = Il.Calls(Il.Method("AuraPower", "RefreshFromSpread"));
        Assert.Contains("AuraCmd.Refresh", refresh);
        Assert.DoesNotContain("ReactionEffects.Resolve", refresh);
        Assert.Contains("AuraCmd.Duration", Il.Calls(Il.Method("AuraCmd", "Refresh")));
        Assert.Contains("AuraPower.RefreshFromSpread",
                        Il.Calls(Il.Method("ReactionEffects", "SwirlPays")));
    }

    [Fact]
    public void A_spread_copy_is_a_plain_application_so_nothing_recurses()
    {
        // STRUCTURAL: the copy lands through AuraCmd.Apply, which carries no
        // trigger, never through an elemental hit door that could react and
        // Swirl again.
        var swirl = Il.Calls(Il.Method("ReactionEffects", "SwirlPays"));
        Assert.Contains("AuraCmd.Apply", swirl);
        Assert.DoesNotContain("ElementalHit.Deal", swirl);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", swirl);
        Assert.DoesNotContain("ReactionEffects.Resolve", Il.Calls(Il.Method("AuraCmd", "Apply")));
    }

    // --- every lifecycle site takes the one decision (STRUCTURAL) ------------

    [Fact]
    public void Every_site_that_resolves_a_hit_on_an_aura_asks_TriggerRules()
    {
        Assert.Contains("TriggerRules.Outcome", Il.Calls(Il.Method("AuraPower", "ResolveLifecycle")));
        Assert.Contains("TriggerRules.Outcome", Il.Calls(Il.Method("ElementalHit", "ResolveOnAura")));
        Assert.Contains("ElementalHit.ResolveOnAura", Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("ElementalHit.ResolveOnAura", Il.Calls(Il.Method("ElementalHit", "ApplyOnly")));
        // Both consume sites remove the aura before the reaction resolves.
        Assert.Contains("PowerCmd.Remove", Il.Calls(Il.Method("AuraPower", "ResolveLifecycle")));
        Assert.Contains("PowerCmd.Remove", Il.Calls(Il.Method("ElementalHit", "ResolveOnAura")));
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
