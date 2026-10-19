using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FONTAINE POOL REWORK (2026-10-19,
/// <c>review/active/fontaine-companions-2026-10-19.md</c>; sim twin
/// <c>tier0/tests/test_fontaine_companion_rework.py</c>): thirty cards,
/// 8 / 13 / 9, five kept, eleven rebuilt on their ids, fourteen new.
///
/// On <see cref="InazumaCompanionOverhaulTests"/>' terms: the pure readers
/// run for real against <see cref="Seat"/>s built for every character that
/// drafts companions; resolution needs a live combat, so the mutating halves
/// are pinned off the compiled methods and labelled STRUCTURAL, and their
/// arithmetic is asserted in the sim twin.
/// </summary>
public class FontaineCompanionReworkTests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>The thirty, in the roster's order.</summary>
    private static readonly Type[] Rows =
    {
        typeof(ProtoMfChevreuseInterdictionFire),
        typeof(ProtoMfChevreuseVanguardsValor),
        typeof(ProtoMfChevreuseBurstingGrenades),
        typeof(ProtoMfLynetteEnigmaticFeint),
        typeof(ProtoMfLynetteBoxTrick),
        typeof(ProtoMfLynetteAstonishingShift),
        typeof(ProtoMfCharlotteFreezingPoint),
        typeof(ProtoMfCharlotteEnduringFrosthelm),
        typeof(ProtoMfCharlotteSnappySilhouette),
        typeof(ProtoMfFreminetPersDeploy),
        typeof(ProtoMfFreminetPressurizedFloe),
        typeof(ProtoMfFreminetShatteringPressure),
        typeof(ProtoMfNaviaCeremonialCrystalshot),
        typeof(ProtoMfClorindeHuntersVigil),
        typeof(ProtoMfNeuvilletteOTears),
        typeof(ProtoMfArlecchinoBalemoonRising),
        typeof(ProtoMfWriothesleyGraciousRebuke),
        typeof(ProtoMfLyneyGrinMalkinHat),
        typeof(ProtoMfSigewinneReboundHydrotherapy),
        typeof(ProtoMfEscoffierLowTemperatureCooking),
        typeof(ProtoMfEmilieLumidouceLegacy),
        typeof(ProtoMfNaviaCannonFireSupport),
        typeof(ProtoMfClorindeImpaleTheNight),
        typeof(ProtoMfNeuvilletteAncientSeaAuthority),
        typeof(ProtoMfArlecchinoMasqueRedDeath),
        typeof(ProtoMfWriothesleyChillingPenalty),
        typeof(ProtoMfLyneyMiracleParade),
        typeof(ProtoMfSigewinneSuperSaturatedSyringing),
        typeof(ProtoMfEscoffierRehabDiet),
        typeof(ProtoMfEmilieAromaticExplication),
    };

    /// <summary>The Powers the rework built, and Navia's rebuilt one.</summary>
    private static readonly Type[] NewPowers =
    {
        typeof(GrinMalkinHatPower), typeof(ReboundHydrotherapyPower),
        typeof(ChillingPenaltyPower), typeof(AromaticExplicationPower),
        typeof(CannonFireSupportPower),
    };

    private static CardModel New(Type t) => (CardModel)Activator.CreateInstance(t)!;

    // ---- THE ROWS -------------------------------------------------------

    [Fact]
    public void The_rows_are_thirty_offerable_fontaine_companions()
    {
        Assert.Equal(30, Rows.Length);
        foreach (var type in Rows)
        {
            var comp = Assert.IsAssignableFrom<ICompanionCard>(New(type));
            Assert.Equal("fontaine", comp.Nation);
            Assert.Null(comp.PersonalPool);
        }
        var referenced = Il.CallSequence(
                Il.Method("CompanionOverhaulRoster", "FontaineUniversals"))
            .Count(c => c.StartsWith("ModelDb.Card"));
        Assert.Equal(30, referenced);
    }

    [Fact]
    public void The_rarity_split_is_eight_thirteen_nine()
    {
        var byRarity = Rows.Select(t => New(t).Rarity)
            .GroupBy(r => r).ToDictionary(g => g.Key, g => g.Count());
        Assert.Equal(8, byRarity[CardRarity.Common]);
        Assert.Equal(13, byRarity[CardRarity.Uncommon]);
        Assert.Equal(9, byRarity[CardRarity.Rare]);
        // Seven Powers: two Uncommon (the Hat, Rebound Hydrotherapy) and the
        // paper's five Rare Powers.
        Assert.Equal(7, Rows.Count(t => New(t).Type == CardType.Power));
        Assert.Equal(5, Rows.Count(t => New(t).Type == CardType.Power
                                        && New(t).Rarity == CardRarity.Rare));
    }

    [Fact]
    public void Emilie_and_shattering_pressure_declare_no_element()
    {
        // Emilie is Dendro, which the mod has no aura for; Shattering
        // Pressure is Physical in the game. Element.None, Kirara's rule.
        foreach (var type in new[] { typeof(ProtoMfEmilieLumidouceLegacy),
                                     typeof(ProtoMfEmilieAromaticExplication),
                                     typeof(ProtoMfFreminetShatteringPressure) })
        {
            Assert.Equal(Element.None, ((ICompanionCard)New(type)).CompanionElement);
        }
        Assert.False(New(typeof(ProtoMfFreminetShatteringPressure)) is IElementalCard);
        Assert.Equal(Element.Geo,
            ((IElementalCard)New(typeof(ProtoMfNaviaCeremonialCrystalshot))).Element);
    }

    [Fact]
    public void The_new_powers_are_counter_buffs()
    {
        foreach (var type in NewPowers)
        {
            var power = (PowerModel)Activator.CreateInstance(type)!;
            Assert.Equal(PowerType.Buff, power.Type);
            Assert.Equal(PowerStackType.Counter, power.StackType);
        }
    }

    // ---- SHATTERING PRESSURE: grows each time it is Retained ------------

    [Fact]
    public void Shattering_pressure_retains_and_grows_only_when_it_is_kept()
    {
        var card = OffCharacterSweep.HeldBy(
            typeof(ProtoMfFreminetShatteringPressure), Seat.Klee());
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);
        var damage = card.DynamicVars.CalculationBase;
        Assert.Equal(8m, damage.BaseValue);

        // REAL: the rule against the flush's two lists.
        Assert.False(FontaineCompanion.GrowOnRetain(
            card, damage, Array.Empty<CardModel>(), 5));
        Assert.Equal(8m, damage.BaseValue);
        Assert.True(FontaineCompanion.GrowOnRetain(
            card, damage, new[] { card }, 5));
        Assert.True(FontaineCompanion.GrowOnRetain(
            card, damage, new[] { card }, 5));
        Assert.Equal(18m, damage.BaseValue);

        // STRUCTURAL: the card hears the flush and asks about itself.
        var flush = typeof(ProtoMfFreminetShatteringPressure)
            .GetMethod("AfterFlush", All | BindingFlags.DeclaredOnly)!;
        Assert.Contains(Il.Calls(flush),
                        c => c.EndsWith("FontaineCompanion.GrowOnRetain",
                                        StringComparison.Ordinal));
    }

    // ---- CRYSTALSHOT: the draw keys off this hit's own Crystallize ------

    [Fact]
    public void Crystalshot_draws_on_its_own_crystallize()
    {
        // STRUCTURAL: the snapshot is taken at the top of the play and read
        // after the hit; the counter is bumped at the one reaction site.
        var calls = Il.CallSequence(typeof(ProtoMfNaviaCeremonialCrystalshot)
            .GetMethod("OnPlay", All)!);
        var reads = calls.Select((c, i) => (c, i))
            .Where(x => x.c.Contains("CrystallizeResolved")).ToList();
        Assert.Equal(2, reads.Count);
        var attack = calls.ToList().FindIndex(c => c.Contains("Execute"));
        Assert.True(reads[0].i < attack && attack < reads[1].i);
        Assert.Contains(calls, c => c.Contains("CardPileCmd.Draw"));
    }

    // ---- SIGEWINNE: Block for each enemy hit ----------------------------

    [Fact]
    public void Syringing_pays_four_for_each_enemy_its_play_reached()
    {
        Assert.Equal(0, FontaineCompanion.BlockForHits(4, 0));
        Assert.Equal(4, FontaineCompanion.BlockForHits(4, 1));
        Assert.Equal(12, FontaineCompanion.BlockForHits(4, 3));

        // REAL: the ledger counts distinct enemies and BeginPlay clears them.
        CompanionOverhaulLedger.ResetAll();
        try
        {
            var seat = Seat.Klee();
            var a = Seat.Of(new Ironclad()).Creature;
            var b = Seat.Of(new Ironclad()).Creature;
            var ledger = CompanionOverhaulLedger.For(seat.Creature);
            ledger.BeginPlay();
            ledger.NoteEnemyHit(a);
            ledger.NoteEnemyHit(a);
            ledger.NoteEnemyHit(b);
            Assert.Equal(2, ledger.EnemiesHitThisPlay);
            ledger.BeginPlay();
            Assert.Equal(0, ledger.EnemiesHitThisPlay);
        }
        finally
        {
            CompanionOverhaulLedger.ResetAll();
        }

        // STRUCTURAL: the card opens the ledger, hits, then asks it.
        var calls = Il.CallSequence(typeof(ProtoMfSigewinneSuperSaturatedSyringing)
            .GetMethod("OnPlay", All)!).ToList();
        var open = calls.FindIndex(c => c.EndsWith("BeginPlay", StringComparison.Ordinal));
        var block = calls.FindIndex(c => c.EndsWith("FontaineCompanion.BlockPerEnemyHit",
                                                    StringComparison.Ordinal));
        Assert.True(open >= 0 && block > open);
    }

    // ---- EMILIE: the Hand first, then the Draw Pile; any card for Lumidouce

    [Fact]
    public void Aromatic_explication_takes_the_hands_junk_first()
    {
        var wound = new MegaCrit.Sts2.Core.Models.Cards.Wound();
        var dazed = new MegaCrit.Sts2.Core.Models.Cards.Dazed();
        var strike = New(typeof(ProtoMfFreminetPersDeploy));
        Assert.Equal(new CardModel[] { wound },
                     FontaineCompanion.JunkPool(new[] { strike, wound }, new[] { dazed }));
        Assert.Equal(new CardModel[] { dazed },
                     FontaineCompanion.JunkPool(new[] { strike }, new[] { strike, dazed }));
        Assert.Empty(FontaineCompanion.JunkPool(new[] { strike }, null));
        Assert.Equal(1, AromaticExplicationPower.EnergyPerExhaust);
    }

    [Fact]
    public void Lumidouce_lets_any_card_in_the_hand_go()
    {
        // "Exhaust a card in your Hand": Burning Pact's, for anyone, so the
        // selector is not Kokomi's own-card filter.
        var calls = Il.Calls(typeof(ProtoMfEmilieLumidouceLegacy)
            .GetMethod("OnPlay", All)!);
        Assert.Contains(calls, c => c.Contains("CardSelectCmd.FromHand"));
        Assert.DoesNotContain(calls, c => c.Contains("KokomiResources.OwnCard"));
    }

    // ---- THE POWERS' TRIGGERS -------------------------------------------

    [Fact]
    public void Each_power_listens_where_the_paper_says()
    {
        static IReadOnlyCollection<string> On(Type t, string hook) =>
            Il.Calls(t.GetMethod(hook, All | BindingFlags.DeclaredOnly)!);

        Assert.Contains(On(typeof(GrinMalkinHatPower), "AfterCardExhausted"),
                        c => c.EndsWith("ElementalHit.Deal", StringComparison.Ordinal));
        Assert.Contains(On(typeof(ChillingPenaltyPower), "AfterDamageReceived"),
                        c => c.EndsWith("ElementalHit.Deal", StringComparison.Ordinal));
        var rebound = On(typeof(ReboundHydrotherapyPower), "AfterPlayerTurnStart");
        Assert.Contains(rebound, c => c.Contains("GainBlock"));
        Assert.Contains(rebound, c => c.EndsWith("ElementalHit.ApplyOnly", StringComparison.Ordinal));
        var aromatic = On(typeof(AromaticExplicationPower), "AfterPlayerTurnStart");
        Assert.Contains(aromatic, c => c.Contains("CardCmd.Exhaust"));
        Assert.Contains(aromatic, c => c.Contains("PlayerCmd.GainEnergy"));
        Assert.Contains(On(typeof(CannonFireSupportPower), "AfterPlayerTurnStart"),
                        c => c.EndsWith("ElementalHit.Deal", StringComparison.Ordinal));
        // Navia left the reaction site.
        Assert.Null(typeof(CannonFireSupportPower).GetMethod("OnReaction", All));
        Assert.DoesNotContain(
            Il.Calls(Il.Method("CompanionOverhaulReactions", "Note")),
            c => c.Contains("CannonFireSupportPower"));
    }

    [Fact]
    public void Chilling_penalty_hears_furinas_drains()
    {
        // GPT's review (2026-10-19): every Drain is an HP loss, so each one
        // hits once. STRUCTURAL: a Drain is `CreatureCmd.Damage` on her, which
        // is the `AfterDamageReceived` the power reads.
        var drain = typeof(GameStageBoard).GetMethod("LoseHp", All)!;
        Assert.Contains(Il.Calls(drain), c => c.Contains("CreatureCmd.Damage"));
    }

    [Fact]
    public void Vanguards_valor_ends_with_the_turn()
    {
        Assert.NotNull(typeof(NextAttackUpPower).GetMethod(
            "AfterSideTurnEnd", All | BindingFlags.DeclaredOnly));
        var face = new NextAttackUpPower().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("this turn", face);
    }

    // ---- FOR EVERY CHARACTER THAT DRAFTS COMPANIONS ---------------------

    public static IEnumerable<object[]> Kits() => new[]
    {
        new object[] { "klee" }, new object[] { "kokomi" },
        new object[] { "varka" }, new object[] { "furina" },
        new object[] { "yae" },
    };

    private static Seat SeatOf(string who) => who switch
    {
        "klee" => Seat.Klee(),
        "kokomi" => Seat.Kokomi(),
        "varka" => Seat.Varka(),
        "furina" => Seat.Furina(),
        _ => Seat.Yae(),
    };

    private static (Type[] Types, MethodBase Predicate) IdentityOf(string who) => who switch
    {
        "klee" => (new[] { typeof(IKleeCharacter), typeof(global::KleeMod.Klee) },
                   typeof(VarkaPrototype).GetMethod(nameof(VarkaPrototype.IsVarka))!),
        "kokomi" => (new[] { typeof(IKokomiCharacter) },
                     typeof(KokomiResources).GetMethod(nameof(KokomiResources.IsKokomi))!),
        "varka" => (new[] { typeof(IVarkaCharacter) },
                    typeof(VarkaPrototype).GetMethod(nameof(VarkaPrototype.IsVarka))!),
        "furina" => (new[] { typeof(IFurinaCharacter) },
                     typeof(FurinaResources).GetMethod(nameof(FurinaResources.IsFurina))!),
        _ => (new[] { typeof(IYaeCharacter) },
              typeof(YaePrototype).GetMethod(nameof(YaePrototype.IsYae),
                                             new[] { typeof(Creature) })!),
    };

    /// <summary>The rework's own code: the thirty cards, the new Powers and
    /// the helper class, each with its compiler-made lambdas and state
    /// machines.</summary>
    private static IEnumerable<MethodBase> OwnMethods()
    {
        static IEnumerable<Type> WithNested(Type t) =>
            new[] { t }.Concat(t.GetNestedTypes(All).SelectMany(WithNested));
        return Rows.Concat(NewPowers).Append(typeof(FontaineCompanion))
            .SelectMany(WithNested)
            .SelectMany(t => t.GetMethods(All | BindingFlags.DeclaredOnly)
                .Cast<MethodBase>());
    }

    /// <summary>
    /// NONE OF THE REWORK'S OWN CODE ASKS WHO IS PLAYING. The kit sweeps walk
    /// a card's whole closure, and a companion's reaches the shared reaction
    /// pipeline, whose kit reads each kit sweep already names by design; so
    /// this asks the narrower question the rework owns: no method the rework
    /// wrote tests for a character type or calls a character predicate.
    /// </summary>
    [Theory]
    [MemberData(nameof(Kits))]
    public void No_fontaine_card_or_power_reads_a_kits_identity(string who)
    {
        var (types, predicate) = IdentityOf(who);
        var findings = OwnMethods()
            .Where(m => Il.TypesTested(m).Any(types.Contains)
                        || Il.Callees(m).Any(c => c == predicate))
            .Select(m => OffCharacterSweep.SiteOf(m))
            .Distinct().ToList();
        Assert.True(findings.Count == 0,
            $"{who} identity read in the Fontaine rework's code:\n  "
            + string.Join("\n  ", findings));
    }

    [Fact]
    public void The_identity_check_bites()
    {
        // The same reader finds the one Varka test his own Oath code makes.
        var live = typeof(VarkaOath).GetMethod("Live", All)!;
        var isVarka = typeof(VarkaPrototype).GetMethod(nameof(VarkaPrototype.IsVarka))!;
        Assert.Contains(Il.Callees(live), c => c == isVarka);
        Assert.True(OwnMethods().Count() > 60);
    }

    [Theory]
    [MemberData(nameof(Kits))]
    public void Every_fontaine_face_reads_the_same_for_every_kit(string who)
    {
        CompanionOverhaulLedger.ResetAll();
        try
        {
            var problems = OffCharacterSweep.FaceProblems(
                Rows, () => Seat.Of(new Ironclad()), () => SeatOf(who));
            Assert.True(problems.Count == 0, string.Join("\n", problems));
        }
        finally
        {
            CompanionOverhaulLedger.ResetAll();
        }
    }

    [Theory]
    [MemberData(nameof(Kits))]
    public void The_powers_answer_their_own_owner_whoever_it_is(string who)
    {
        var seat = SeatOf(who);
        var other = Seat.Of(new Ironclad());
        var mine = OffCharacterSweep.HeldBy(typeof(ProtoMfFreminetPersDeploy), seat);
        var theirs = OffCharacterSweep.HeldBy(typeof(ProtoMfFreminetPersDeploy), other);
        Assert.True(GrinMalkinHatPower.Answers(seat.Creature, mine));
        Assert.False(GrinMalkinHatPower.Answers(seat.Creature, theirs));
        Assert.True(ChillingPenaltyPower.Pays(seat.Creature, seat.Creature, 2));
        Assert.False(ChillingPenaltyPower.Pays(seat.Creature, seat.Creature, 0));
        Assert.False(ChillingPenaltyPower.Pays(seat.Creature, other.Creature, 5));
    }
}
