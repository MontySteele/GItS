using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE MONDSTADT COMPANION OVERHAUL, pinned (the approved workshop
/// `companion-workshop-mondstadt-2026-09-01.md`; sim twin
/// <c>tier0/tests/test_companion_overhaul.py</c>).
///
/// This whole file is compiled only under <c>-p:PrototypeCards=true</c>
/// (KleeTests.csproj), the same switch that compiles the arm. That is the point
/// rather than an inconvenience: the arm's C# does not exist in a release build,
/// so a pin against it cannot either.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, said once. The CARDS are real --
/// a <c>CardModel</c> can be constructed headlessly, so its cost, type, rarity
/// and companion identity are direct reads. The POWERS' printed faces are real
/// too, and they are asserted against <see cref="CompanionOverhaulLaw"/> so a
/// face cannot drift from the number the power pays. What is NOT reachable is
/// RESOLUTION: <c>PowerCmd</c>, <c>ElementalHit</c> and a live
/// <c>CombatState</c> are all outside the headless boundary (KleeTests/README),
/// so the wiring and the firing ORDER are pinned off the compiled method and
/// are labelled STRUCTURAL wherever they are. The arithmetic those hooks
/// perform is asserted for real in the sim twin, against the same constants.
/// </summary>
[Collection(CompanionOverhaulArm.Name)]
public class CompanionOverhaulTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>Every generated row of the arm, by class -- all thirty-four,
    /// in two waves. The compiler holds the correspondence with the sheet -- a
    /// deleted row takes its class with it and this file stops building --
    /// which is the same guarantee <see cref="CompanionOverhaulRoster"/> buys
    /// by listing types.</summary>
    private static readonly Type[] Universals =
    {
        typeof(ProtoMcDionaSignatureMix),
        typeof(ProtoMcNoelleBreastplate),
        typeof(ProtoMcKaeyaFrostgnaw),
        typeof(ProtoMcKaeyaGlacialWaltz),
        typeof(ProtoMcBarbaraShowBegin),
        typeof(ProtoMcAlbedoSolarIsotoma),
        typeof(ProtoMcJeanGaleBlade),
        typeof(ProtoMcJeanDandelionBreeze),
        typeof(ProtoMcFischlNightrider),
        typeof(ProtoMcFischlOz),
        typeof(ProtoMcSucroseGust),
        typeof(ProtoMcSucroseAstable),
        typeof(ProtoMcSucroseCatalystConversion),
        typeof(ProtoMcBennettFantasticVoyage),
        typeof(ProtoMcNicoleRevelation),
        typeof(ProtoMcMonaStellarisPhantasm),
        typeof(ProtoMcVentiGrandOde),
        typeof(ProtoMcAmberFieryRain),
        typeof(ProtoMcLisaVioletArc),
        typeof(ProtoMcLisaLightningRose),
        typeof(ProtoMcRosariaRavagingConfession),
        // THE SECOND WAVE: the thirteen rows whose printed text needed an
        // engine hook. Their own pins are in CompanionOverhaulHookTests; they
        // are listed here because THIS file owns the "the assembly holds no
        // overhaul row the roster forgot" sweep, which is a statement about
        // every ProtoMc row there is.
        typeof(ProtoMcDionaIcyPaws),
        typeof(ProtoMcNoelleSweepingTime),
        typeof(ProtoMcBarbaraMelodyLoop),
        typeof(ProtoMcBennettPassionOverload),
        typeof(ProtoMcDahliaSacramentalShower),
        typeof(ProtoMcDahliaFavonianFavor),
        typeof(ProtoMcDurinBinaryForm),
        typeof(ProtoMcRazorClawAndThunder),
        typeof(ProtoMcRazorLightningFang),
        typeof(ProtoMcVarkaSturmUndDrang),
        typeof(ProtoMcAmberExplosivePuppet),
        typeof(ProtoMcEulaGlacialIllumination),
        typeof(ProtoMcMikaStarfrostSwirl),
    };

    /// <summary>The six powers that fire at the end of the player's turn, in
    /// the sequence <see cref="CompanionOverhaulTurnEnd"/> must walk. Mirrors
    /// tier0 `effects.companion_overhaul_turn_end`, which the sim twin pins
    /// against this same list.</summary>
    private static readonly string[] TurnEndOrder =
    {
        nameof(GlacialWaltzPower),
        nameof(MondstadtOzPower),
        nameof(LightningRosePower),
        nameof(GrandOdePower),
        nameof(DandelionBreezePower),
        nameof(SolarIsotomaBloomPower),
    };

    private static readonly Type[] StartOfTurnPowers =
    {
        typeof(SignatureMixPower),
        typeof(RevelationPower),
        typeof(StellarisOmenPower),
    };

    private static Type[] EndOfTurnPowers() => new[]
    {
        typeof(GlacialWaltzPower), typeof(MondstadtOzPower),
        typeof(LightningRosePower), typeof(GrandOdePower),
        typeof(DandelionBreezePower), typeof(SolarIsotomaBloomPower),
    };

    // ---- THE FLAG, OFF --------------------------------------------------

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST (2026-09-02).
    //
    // `dotnet test -p:CompanionOverhaul=true` defines `COMPANION_OVERHAUL`, which is what MOVES
    // `DefaultEnabled` -- the exact value this pin asserts. So under that
    // property the pin cannot say anything true: green would mean the property
    // did nothing, and red is the property working. It is skipped there rather
    // than left to fail, because a red that means "the switch works" trains
    // everyone to ignore reds.
    //
    // ARM PROPERTIES ARE DEPLOY-LINE ONLY. The supported test configurations
    // are `dotnet test` and `dotnet test -p:PrototypeCards=true`, and this pin
    // runs in both -- which is where the acceptance condition has to hold.
    // docs/current/operations/prototype.md carries the rule.
#if COMPANION_OVERHAUL
    [Fact(Skip = "-p:CompanionOverhaul=true moves CompanionOverhaul.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        // The acceptance condition, and everything else here only matters
        // while it holds. `Enabled` is settable so a pin can exercise both
        // sides in one build; nothing in the mod ever writes it.
        Assert.False(CompanionOverhaul.DefaultEnabled);
        Assert.Equal(CompanionOverhaul.DefaultEnabled, CompanionOverhaul.Enabled);
    }

    [Fact]
    public void The_one_wiring_seam_reads_the_flag_and_nothing_else()
    {
        // STRUCTURAL. Flag off is byte-identical, pinned where it is decided
        // rather than asserted in prose: the seam is one `if` on the property,
        // so with the arm off `CompanionPool.All` falls through to the
        // generated roster it always returned.
        var all = typeof(CompanionPool)
            .GetProperty("All", All)!.GetGetMethod(true)!;
        var calls = Il.Calls(all);
        Assert.Contains("CompanionOverhaul.get_Enabled", calls);
        Assert.Contains("CompanionOverhaulRoster.Roster", calls);
        Assert.Contains("CompanionRoster.get_All", calls);
    }

    [Fact]
    public void Both_offer_surfaces_read_the_one_door()
    {
        // STRUCTURAL, and it is the whole reason the seam is on CompanionPool
        // rather than on the reward slot: the Featured Banner and the slot
        // have to see ONE roster, or a run features five-stars it cannot be
        // offered -- the split R64 shipped the banner to close. Reading
        // CompanionRoster directly is what would re-open it, so that is what
        // this refuses.
        foreach (var method in new MethodBase[]
                 {
                     typeof(CompanionSlot).GetMethod("Roll", All)!,
                     typeof(CompanionBanner).GetMethod("Roll", All)!,
                 })
        {
            var calls = Il.Calls(method);
            Assert.Contains("CompanionPool.get_All", calls);
            Assert.DoesNotContain("CompanionRoster.get_All", calls);
        }
    }

    [Fact]
    public void The_arm_does_not_edit_the_shipped_companion_powers()
    {
        // The reason every rewritten power is a SECOND class rather than a
        // retune of the shipped one: a flag-off build has to keep meaning what
        // it printed. Oz is the sharpest case -- the shipped power is a
        // three-turn Counter and this arm's is permanent.
        var shipped = new[] { typeof(OzSummonPower), typeof(SolarIsotomaPower),
                              typeof(CelestialGiftPower), typeof(WitchsFlamePower) }
            .SelectMany(t => t.GetMethods(All).Where(m => m.DeclaringType == t))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.DoesNotContain(shipped, c => c.StartsWith("CompanionOverhaul"));
        Assert.DoesNotContain(shipped, c => c.StartsWith("MondstadtOz"));
    }

    // ---- THE ROWS -------------------------------------------------------

    [Fact]
    public void Every_row_is_an_offerable_mondstadt_companion()
    {
        Assert.Equal(34, Universals.Length);
        foreach (var type in Universals)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            var comp = Assert.IsAssignableFrom<ICompanionCard>(card);
            Assert.Equal("mondstadt", comp.Nation);
            // A Universal, never a Personal: a personal-pool row would be
            // Klee's kit and could not be offered to another character, which
            // is the one thing every row here is required to be able to be
            // (the workshop's brick test).
            Assert.Null(comp.PersonalPool);
            Assert.True(comp.Star == 4 || comp.Star == 5,
                $"{type.Name}: star {comp.Star}");
            Assert.NotEqual(CardRarity.Basic, card.Rarity);
        }
    }

    [Fact]
    public void The_assembly_holds_no_overhaul_row_the_roster_forgot()
    {
        // The compiler holds the roster -> class direction (a deleted row
        // stops the build). This is the other direction: a row generated onto
        // the surface and never added to CompanionOverhaulRoster would compile
        // fine, load fine, and simply never be offered.
        var generated = typeof(ProtoMcDionaSignatureMix).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && t.Name.StartsWith("ProtoMc", StringComparison.Ordinal)
                        // A modal row's MODE FACES are generated beside it and
                        // are pool members (EB-150), but they are not rows: no
                        // reward slot may offer one, so the roster does not
                        // list them and this sweep does not ask about them.
                        && !typeof(ModalOptionCard).IsAssignableFrom(t))
            // NOR IS A PERSONAL-POOL ROW A UNIVERSAL, and the sweep could not
            // tell the difference until `EB-320` -- which is how it came to be
            // failing here for every stand-in and every Klee-personal
            // companion the surface has grown (the four R236 caretakers, the
            // four Hexerei, and Prune, Qiqi, Sayu and Yaoyao before them).
            // `CompanionOverhaulRoster` is the OFFER list, and a card carrying
            // a PersonalPool is deliberately not on it: a stand-in is reached
            // at the hand-off and nowhere else (`CompanionStandIns`), and a
            // personal companion is offered through its own character's route.
            // So "the roster forgot a row" is a question about Universals, and
            // this is where the two are separated. What the personal rows are
            // swept for instead is the value of that very key:
            // `CompanionStandInHandOffTests`.
            .Where(t => (Activator.CreateInstance(t) as ICompanionCard)
                            ?.PersonalPool == null)
            .ToList();
        Assert.Equal(
            Universals.OrderBy(t => t.Name).Select(t => t.Name).ToList(),
            generated.OrderBy(t => t.Name).Select(t => t.Name).ToList());
    }

    [Fact]
    public void Every_rare_belongs_to_a_five_star_character()
    {
        // The sheet's star-to-rarity rule, which the workshop's sec.5 says
        // stands. Jean is the one five-star with a second, Uncommon card
        // (Gale Blade), so this asserts the RARE tier rather than the star
        // tier -- and the asymmetry is recorded in the provenance note. Eight
        // across the two waves: Albedo, Jean, Nicole, Mona and Venti first,
        // then Durin, Varka and Eula.
        var rares = Universals
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .Where(c => c.Rarity == CardRarity.Rare)
            .ToList();
        Assert.Equal(8, rares.Count);
        Assert.All(rares, c => Assert.Equal(5, ((ICompanionCard)c).Star));
    }

    // ---- THE POWERS -----------------------------------------------------

    [Fact]
    public void Every_power_is_a_counter_buff()
    {
        // Counter, not Stack: every one of these carries either a duration or
        // a copy count, and both are numbers the badge should print.
        foreach (var type in StartOfTurnPowers.Concat(EndOfTurnPowers()))
        {
            var power = (PowerModel)Activator.CreateInstance(type)!;
            Assert.Equal(PowerType.Buff, power.Type);
            Assert.Equal(PowerStackType.Counter, power.StackType);
        }
    }

    [Theory]
    [InlineData(typeof(SignatureMixPower), CompanionOverhaulLaw.SignatureMixBlock)]
    [InlineData(typeof(GlacialWaltzPower), CompanionOverhaulLaw.GlacialWaltzDamage)]
    [InlineData(typeof(MondstadtOzPower), CompanionOverhaulLaw.OzDamage)]
    [InlineData(typeof(LightningRosePower), CompanionOverhaulLaw.LightningRoseDamage)]
    [InlineData(typeof(DandelionBreezePower), CompanionOverhaulLaw.DandelionBreezeBlock)]
    [InlineData(typeof(SolarIsotomaBloomPower), CompanionOverhaulLaw.IsotomaDamage)]
    [InlineData(typeof(RevelationPower), CompanionOverhaulLaw.RevelationBlock)]
    [InlineData(typeof(StellarisOmenPower), CompanionOverhaulLaw.OmenVulnerable)]
    public void Every_power_face_prints_the_number_it_pays(Type type, int number)
    {
        // FACE FROM BODY, at the power level: the description is built by
        // interpolating the CompanionOverhaulLaw constant the hook spends, so
        // a retune moves both or neither. A power whose face hard-coded a
        // literal would pass every parity lint and still lie on screen.
        var power = (ILocalizationProvider)Activator.CreateInstance(type)!;
        var description = power.Localization!
            .Single(entry => entry.Item1 == "description").Item2;
        Assert.Contains(number.ToString(), description);
    }

    [Fact]
    public void The_permanent_powers_never_tick_down()
    {
        // The workshop's sec.1 rule: "A Power has no turn limit. A Power
        // cannot be reapplied, so a timed effect is a Skill with Exhaust; a
        // Power lasts the fight." These four are the Powers, and the tick is
        // what would quietly turn one back into a timed Skill.
        foreach (var type in new[] { typeof(MondstadtOzPower),
                                     typeof(DandelionBreezePower),
                                     typeof(SolarIsotomaBloomPower),
                                     typeof(RevelationPower) })
        {
            var calls = type.GetMethods(All)
                .Where(m => m.DeclaringType == type)
                .SelectMany(Il.Calls)
                .ToList();
            Assert.DoesNotContain("PowerCmd.TickDownDuration", calls);
        }
    }

    [Fact]
    public void The_timed_powers_all_tick_down()
    {
        foreach (var type in new[] { typeof(SignatureMixPower),
                                     typeof(GlacialWaltzPower),
                                     typeof(LightningRosePower),
                                     typeof(GrandOdePower) })
        {
            var calls = type.GetMethods(All)
                .Where(m => m.DeclaringType == type)
                .SelectMany(Il.Calls)
                .ToList();
            Assert.Contains("PowerCmd.TickDownDuration", calls);
        }
    }

    [Fact]
    public void The_omen_is_removed_whole_rather_than_ticked()
    {
        // Two copies pay two Vulnerable NEXT turn, not one Vulnerable on each
        // of two turns. TickDownDuration is exactly the call that would do the
        // second thing, so its absence beside a Remove is the pin.
        var calls = typeof(StellarisOmenPower).GetMethods(All)
            .Where(m => m.DeclaringType == typeof(StellarisOmenPower))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.Contains("PowerCmd.Remove", calls);
        Assert.DoesNotContain("PowerCmd.TickDownDuration", calls);
    }

    // ---- THE END-OF-TURN ORDER ------------------------------------------

    [Fact]
    public void No_end_of_turn_power_overrides_a_broadcast_of_its_own()
    {
        // EB-19/races-c, applied to this arm. Six powers fire at the end of
        // the player's turn, four of them put an element on an enemy that may
        // already carry one and three draw from Rng.CombatTargets -- so a
        // power that took its own broadcast would put the reaction board, and
        // every later roll in the run, at the mercy of listener iteration
        // order.
        foreach (var type in EndOfTurnPowers())
        {
            foreach (var hook in new[] { "BeforeSideTurnEnd", "AfterSideTurnEnd" })
            {
                var method = type.GetMethod(hook, All);
                Assert.True(method == null || method.DeclaringType != type,
                    $"{type.Name} overrides {hook}; the arm has ONE tenant "
                    + "(CompanionOverhaulTurnEnd) and it drives all six.");
            }
        }
    }

    [Fact]
    public void The_one_tenant_walks_the_six_in_the_sims_order()
    {
        // STRUCTURAL, and its twin is real: the sim's order is asserted
        // against this same list in tier0/tests/test_companion_overhaul.py,
        // which reads BOTH files. Here the pin is that the listener actually
        // names all six types.
        var walk = typeof(CompanionOverhaulTurnEnd)
            .GetMethod("AfterSideTurnEnd", All)!;
        var calls = Il.Calls(walk);
        foreach (var name in TurnEndOrder)
        {
            Assert.Contains(calls, c => c.StartsWith(name + "."));
        }
        // And the latch, which must be walked LAST because two of the six
        // grant Block and Nicole's question is whether the turn ENDED with
        // any standing.
        Assert.Contains("RevelationPower.NoteEndOfTurn", calls);
    }

    [Fact]
    public void Nicole_reads_a_latch_rather_than_live_block()
    {
        // The card cannot ask its question at the start of the turn: the turn
        // tick clears Block first, which is exactly why CelestialGiftPower can
        // GRANT Block from this same hook and have it survive. So the answer
        // is written at the previous turn's end and only read here.
        var start = typeof(RevelationPower)
            .GetMethod("AfterPlayerTurnStart", All)!;
        var calls = Il.Calls(start);
        Assert.DoesNotContain(calls, c => c.EndsWith("get_Block"));
        Assert.Contains("RevelationPower.get_HeldTheLine", calls);
    }

    [Fact]
    public void The_start_of_turn_three_keep_their_own_broadcast()
    {
        // Deliberate, and the difference from the six above is argued rather
        // than inherited: these three are COMMUTATIVE. Two grant the player
        // Block or Strength and the third applies Vulnerable to enemies; none
        // reads a value another writes, and the one that reads Block reads a
        // latch. Order among them cannot change an outcome.
        foreach (var type in StartOfTurnPowers)
        {
            var method = type.GetMethod("AfterPlayerTurnStart", All);
            Assert.True(method != null && method.DeclaringType == type,
                $"{type.Name} no longer pays at the start of the turn.");
        }
    }

    [Fact]
    public void The_listener_is_subscribed_only_under_the_prototype_switch()
    {
        // The subscription lives in KleeMod.Register behind `#if
        // PROTOTYPE_CARDS`, which is what keeps a release build from even
        // referencing the type. This pin is the compiled proof: the call is in
        // the assembly we are testing, which is a PROTOTYPE build.
        // NESTED TYPES INCLUDED, and they are the point: the subscription is
        // a LAMBDA passed to ModHelper.SubscribeForCombatStateHooks, and a C#
        // lambda compiles into a generated closure class rather than into the
        // method that wrote it. A sweep over the declaring type alone reads
        // empty here and would pass whatever the mod did.
        var host = typeof(global::KleeMod.KleeMod);
        var bodies = new[] { host }
            .Concat(host.GetNestedTypes(All))
            .SelectMany(t => t.GetMethods(All).Where(m => m.DeclaringType == t))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.Contains("CompanionOverhaulTurnEnd.Subscribe", bodies);
    }
}
