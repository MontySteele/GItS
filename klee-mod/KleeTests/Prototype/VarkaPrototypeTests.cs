using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>The one collection every pin that flips
/// <see cref="VarkaPrototype.Enabled"/> runs in.</summary>
[CollectionDefinition(Name, DisableParallelization = true)]
public sealed class VarkaArm
{
    public const string Name = "VarkaArm";
}

/// <summary>
/// VARKA, THE OATH REWORK (<c>review/active/varka-paper-kit-2026-09-28.md</c>,
/// every pick ruled 2026-09-29). The rules are pinned the way the element
/// port's are (<c>ElementPortTests</c>): a hit landing needs a live combat,
/// outside the headless boundary, so each rule is a pure decision read value
/// by value -- the Oath ledger is pure for exactly this -- and the call graph
/// is pinned to prove the live sites take that decision rather than their
/// own. The sim twin is <c>tier0/tests/test_varka_oath.py</c>.
/// </summary>
[Collection(VarkaArm.Name)]
public class VarkaPrototypeTests : IDisposable
{
    private readonly bool _enabled = VarkaPrototype.Enabled;

    public VarkaPrototypeTests()
    {
        HeadlessGame.Arm();
        VarkaPrototype.Enabled = true;
        VarkaOathLedger.ResetAll();
    }

    public void Dispose()
    {
        VarkaPrototype.Enabled = _enabled;
        VarkaOathLedger.ResetAll();
    }

    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static decimal Var(CardModel card, string name) =>
        card.DynamicVars[name].BaseValue;

    private static List<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();

    private static VarkaOathLedger FreshLedger() =>
        VarkaOathLedger.For(Seat.Klee().Creature);

    // ---- the arm -----------------------------------------------------------

    // ON in every build that names no property (Directory.Build.props).
    // SKIPPED, NOT LEFT TO FAIL, where the build opts him out
    // (-p:ShippedKits=true or -p:VarkaPrototype=false): there the property
    // moved the value this pin asserts (operations/prototype.md).
#if VARKA_PROTOTYPE
    [Fact]
#else
    [Fact(Skip = "This build opts Varka out (-p:ShippedKits=true or -p:VarkaPrototype=false), which moves the default this pin asserts.")]
#endif
    public void The_arm_ships_on()
    {
        Assert.True(VarkaPrototype.DefaultEnabled);
    }

    // ---- the Oath ledger (sec.3) ---------------------------------------------

    [Fact]
    public void Oath_is_four_counts_and_the_current_element_starts_empty()
    {
        var ledger = FreshLedger();
        Assert.Equal(new[] { Element.Pyro, Element.Hydro, Element.Electro,
                             Element.Cryo }, VarkaOathLedger.Elements);
        Assert.Equal(Element.None, ledger.Current);
        Assert.Equal(0, ledger.CurrentOath);
        Assert.True(ledger.Add(Element.Pyro, 2));
        Assert.True(ledger.Add(Element.Cryo, 1));
        // Anemo and Geo keep no Oath.
        Assert.False(ledger.Add(Element.Anemo, 1));
        Assert.Equal(2, ledger.ElementsWithOath);
        Assert.Equal(3, ledger.Total);
        // Cards read only the current element's.
        Assert.Equal(0, ledger.CurrentOath);
        Assert.True(ledger.SetCurrent(Element.Pyro));
        Assert.Equal(2, ledger.CurrentOath);
        // The same element again is not a change (Boreas Unbound's question).
        Assert.False(ledger.SetCurrent(Element.Pyro));
        Assert.True(ledger.SetCurrent(Element.Cryo));
        Assert.Equal(1, ledger.CurrentOath);
    }

    [Fact]
    public void Oath_is_counted_per_card_not_per_enemy()
    {
        // sec.3: "A card that applies an element gains 1 Oath of it, however
        // many enemies it hits ... A card that Swirls gains 1 Oath of each
        // element it Swirls." Apply and Swirl are separate credits.
        var ledger = FreshLedger();
        ledger.OpenScope();
        Assert.True(ledger.TryCredit(swirl: false, Element.Hydro));
        Assert.False(ledger.TryCredit(swirl: false, Element.Hydro));
        Assert.True(ledger.TryCredit(swirl: true, Element.Hydro));
        Assert.False(ledger.TryCredit(swirl: true, Element.Hydro));
        Assert.True(ledger.TryCredit(swirl: true, Element.Pyro));
        ledger.CloseScope();
        // A new play starts clean.
        ledger.OpenScope();
        Assert.True(ledger.TryCredit(swirl: false, Element.Hydro));
        ledger.CloseScope();
        // Outside any play each event credits (nothing to dedupe against).
        Assert.True(ledger.TryCredit(swirl: false, Element.Hydro));
        Assert.True(ledger.TryCredit(swirl: false, Element.Hydro));
        Assert.False(ledger.TryCredit(swirl: false, Element.Anemo));
    }

    [Fact]
    public void The_open_oath_switches_on_his_own_non_knight_plays_only()
    {
        // [USER], 2026-09-30: "Any card that applies an element other than
        // Anemo counts for Oath effects". Inside a play of his non-Knight
        // card an Oath element's application becomes his current element.
        var ledger = FreshLedger();
        var card = new object();
        Assert.False(ledger.OpenOathSwitches(Element.Hydro));    // no play
        ledger.OpenScope(open: true, card: card);
        Assert.True(ledger.OpenOathSwitches(Element.Hydro));
        Assert.True(ledger.OpenOathSwitches(Element.Electro, card));
        // Anemo and Geo give nothing.
        Assert.False(ledger.OpenOathSwitches(Element.Anemo));
        Assert.False(ledger.OpenOathSwitches(Element.Geo));
        // A hit naming another card is not this play's.
        Assert.False(ledger.OpenOathSwitches(Element.Pyro, new object()));
        // Ascension's elemental hit credits nothing and switches nothing.
        ledger.SuppressApply++;
        Assert.False(ledger.OpenOathSwitches(Element.Pyro));
        ledger.SuppressApply--;
        // A scoped event inside it (Baron Bunny's shape) is not a play.
        ledger.OpenScope();
        Assert.False(ledger.OpenOathSwitches(Element.Pyro));
        ledger.CloseScope();
        Assert.True(ledger.OpenOathSwitches(Element.Pyro));
        ledger.CloseScope();
        // A Knight's play keeps its own play-time switch only.
        ledger.OpenScope(open: false, card: card);
        Assert.False(ledger.OpenOathSwitches(Element.Pyro, card));
        ledger.CloseScope();
        Assert.False(ledger.OpenOathSwitches(Element.Pyro));
    }

    [Fact]
    public void The_open_oath_sets_the_element_before_it_credits()
    {
        // The switch comes first, so the gain is the current element's and
        // Dawn Wind's March pays as on a Knight; never a Knight's Standard.
        var note = Il.CallSequence(
            Il.Method("VarkaOath", "NoteApplication")).ToList();
        var opens = note.IndexOf("VarkaOathLedger.OpenOathSwitches");
        var set = note.IndexOf("VarkaOath.SetCurrent");
        var credit = note.IndexOf("VarkaOathLedger.TryCredit");
        var gain = note.IndexOf("VarkaOath.Gain");
        Assert.True(opens >= 0 && set > opens && credit > set && gain > credit,
                    string.Join(", ", note));
        Assert.DoesNotContain("VarkaOathLedger.NoteKnight", note);
        // Only a non-Knight play opens an open-Oath scope.
        Assert.Contains("VarkaRules.IsKnight",
                        Il.Calls(Il.Method("VarkaOath", "BeginPlay")));
    }

    [Fact]
    public void Ascensions_elemental_hit_credits_no_application()
    {
        var ledger = FreshLedger();
        ledger.OpenScope();
        ledger.SuppressApply++;
        Assert.False(ledger.TryCredit(swirl: false, Element.Pyro));
        // Its Anemo hit's Swirl still counts.
        Assert.True(ledger.TryCredit(swirl: true, Element.Pyro));
        ledger.SuppressApply--;
        Assert.True(ledger.TryCredit(swirl: false, Element.Pyro));
        ledger.CloseScope();
    }

    [Fact]
    public void Rally_moves_every_point_and_accord_splits_them()
    {
        var ledger = FreshLedger();
        ledger.Add(Element.Pyro, 3);
        ledger.Add(Element.Hydro, 2);
        ledger.Add(Element.Cryo, 4);
        // No current element: Rally does nothing.
        ledger.Rally();
        Assert.Equal(3, ledger.Oath(Element.Pyro));
        ledger.SetCurrent(Element.Hydro);
        ledger.Rally();
        Assert.Equal(9, ledger.Oath(Element.Hydro));
        Assert.Equal(0, ledger.Oath(Element.Pyro));
        Assert.Equal(0, ledger.Oath(Element.Cryo));
        // Accord: 9 / 4 = 2 each, rounding down (the +1s are gains).
        ledger.Split();
        Assert.All(VarkaOathLedger.Elements,
                   e => Assert.Equal(2, ledger.Oath(e)));
    }

    [Fact]
    public void Knights_are_counted_per_turn_and_swirled_bodies_per_play()
    {
        var ledger = FreshLedger();
        ledger.NoteKnight();
        ledger.NoteKnight();
        Assert.Equal(2, ledger.KnightsThisTurn);
        ledger.RollTo(7);
        Assert.Equal(0, ledger.KnightsThisTurn);
        var body = Seat.Klee(30).Creature;
        ledger.OpenScope();
        ledger.NoteSwirl(body);
        Assert.Equal(new[] { body }, ledger.SwirledThisPlay);
        ledger.CloseScope();
        ledger.OpenScope();
        Assert.Empty(ledger.SwirledThisPlay);
        ledger.CloseScope();
        Assert.Equal(1, ledger.SwirlsMade);
    }

    [Fact]
    public void Nobody_but_a_live_varka_has_oath()
    {
        var klee = Seat.Klee().Creature;
        VarkaOathLedger.For(klee).Add(Element.Pyro, 5);
        VarkaOathLedger.For(klee).SetCurrent(Element.Pyro);
        Assert.Equal(0, VarkaOath.CurrentOath(klee));
        Assert.Equal(Element.None, VarkaOath.Current(klee));
        Assert.False(VarkaOath.HasCurrent(null));
    }

    // ---- the Swirl payout (sec.3, pick 1) ------------------------------------

    [Fact]
    public void The_swirl_payout_numbers_are_the_papers()
    {
        Assert.Equal(3, VarkaLaw.SwirlPyroDamage);
        Assert.Equal(3, VarkaLaw.SwirlHydroBlock);
        Assert.Equal(1, VarkaLaw.SwirlCryoVulnerable);
        Assert.Equal(3, VarkaLaw.SwirlElectroDamageAll);
        Assert.Equal(4, VarkaLaw.StormwardOathNeeded);
        Assert.Equal("Your Swirls deal 3 damage to that enemy.",
                     VarkaOath.PayoutSentence(Element.Pyro));
        Assert.Equal("Your Swirls deal 3 damage to ALL enemies.",
                     VarkaOath.PayoutSentence(Element.Electro));
        Assert.Contains("3 [gold]Block[/gold]",
                        VarkaOath.PayoutSentence(Element.Hydro));
        Assert.Contains("1 [gold]Vulnerable[/gold]",
                        VarkaOath.PayoutSentence(Element.Cryo));
    }

    [Fact]
    public void Every_swirl_pays_his_current_element_from_the_one_reaction_site()
    {
        // STRUCTURAL: `ReactionEffects.Resolve` is the single site every
        // reaction in the mod passes; the Swirl credits, then pays.
        Assert.Contains("VarkaOath.OnSwirl",
                        Il.Calls(Il.Method("ReactionEffects", "Resolve")));
        var onSwirl = Il.Calls(Il.Method("VarkaOath", "OnSwirl"));
        Assert.Contains("VarkaOathLedger.TryCredit", onSwirl);
        Assert.Contains("VarkaOath.Gain", onSwirl);
        // The expansion moved the four payouts into one `Pay`, which a
        // Crosscurrent Swirl and Twin Gales call more than once.
        Assert.Contains("VarkaOath.Pay", onSwirl);
        var pay = Il.Calls(Il.Method("VarkaOath", "Pay"));
        Assert.Contains("ElementalHit.DealUnelemented", pay);   // Pyro, Electro
        Assert.Contains("CreatureCmd.GainBlock", pay);          // Hydro
        Assert.Contains("PowerCmd.Apply", pay);                 // Cryo
    }

    // ---- where Oath is credited, and the play bracket ------------------------

    [Fact]
    public void Applications_credit_at_the_hit_and_at_the_damage_less_doors()
    {
        Assert.Contains("VarkaOath.NoteApplication", Il.Calls(
            Il.Method("KleeElementalHooks", "BeforeDamageReceived")));
        Assert.Contains("VarkaOath.NoteApplication",
                        Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("VarkaOath.NoteApplication",
                        Il.Calls(Il.Method("ElementalHit", "ApplyOnly")));
        // A Swirl's spread places its copies without passing the door.
        Assert.DoesNotContain("VarkaOath.NoteApplication",
                              Il.Calls(Il.Method("ReactionEffects", "SwirlPays")));
        var note = Il.Calls(Il.Method("VarkaOath", "NoteApplication"));
        Assert.Contains("VarkaOathLedger.TryCredit", note);
        Assert.Contains("VarkaOath.Gain", note);
    }

    [Fact]
    public void A_knight_sets_the_current_element_before_its_effects()
    {
        Assert.Contains("VarkaOath.BeginPlay", Il.Calls(
            Il.Method("KleeElementalHooks", "BeforeCardPlayed")));
        Assert.Contains("VarkaOath.EndPlay", Il.Calls(
            Il.Method("KleeElementalHooks", "AfterCardPlayed")));
        var begin = Il.Calls(Il.Method("VarkaOath", "BeginPlay"));
        Assert.Contains("VarkaOathLedger.OpenScope", begin);
        Assert.Contains("VarkaOathLedger.NoteKnight", begin);
        Assert.Contains("VarkaOath.SetCurrent", begin);
        var set = Il.Calls(Il.Method("VarkaOath", "SetCurrent"));
        Assert.Contains("BoreasUnboundPower.OnElementChanged", set);  // a change
        Assert.Contains("CreatureCmd.GainBlock", set);                // Standard
        Assert.Contains("OathBadge.Sync", set);
    }

    [Fact]
    public void A_gain_pays_dawn_winds_march_and_wakes_the_fang()
    {
        var gain = Il.Calls(Il.Method("VarkaOath", "Gain"));
        Assert.Contains("VarkaOathLedger.Add", gain);
        Assert.Contains("CreatureCmd.GainBlock", gain);          // the March
        Assert.Contains("BoreasFang.HeldBy", gain);
        Assert.Contains("BoreasFang.AddAscension", gain);
        // Regent's Forge: created in combat, added to the hand.
        Assert.Contains("CardPileCmd.AddGeneratedCardToCombat",
                        Il.Calls(Il.Method("BoreasFang", "AddAscension")));
    }

    [Fact]
    public void His_turn_start_runs_bunny_then_brotherhood_then_the_knights_oath()
    {
        Assert.Contains("VarkaOath.TurnStart", Il.Calls(
            Il.Method("KleeElementalHooks", "AfterPlayerTurnStart")));
        var turn = Il.CallSequence(Il.Method("VarkaOath", "TurnStart")).ToList();
        var bunny = turn.IndexOf("VarkaBaronBunnyPower.Fire");
        var sworn = turn.IndexOf("VarkaOath.Gain");
        var block = turn.LastIndexOf("CreatureCmd.GainBlock");
        Assert.True(bunny >= 0 && sworn > bunny && block > sworn,
                    string.Join(", ", turn));
        // Bunny's burst is one Oath scope of Pyro hits on every enemy.
        var fire = Il.Calls(Il.Method("VarkaBaronBunnyPower", "Fire"));
        Assert.Contains("VarkaOath.Scope", fire);
        Assert.Contains("ElementalHit.DealWithoutDealerMods", fire);
    }

    // ---- the badge -----------------------------------------------------------

    [Fact]
    public void The_badge_is_the_current_elements_oath()
    {
        Assert.Equal(typeof(PyroOathPower), OathBadge.Wanted(Element.Pyro, 0));
        Assert.Equal(typeof(ElectroOathPower), OathBadge.Wanted(Element.Electro, 9));
        Assert.Equal(typeof(UnswornOathPower), OathBadge.Wanted(Element.None, 2));
        Assert.Null(OathBadge.Wanted(Element.None, 0));
        string Row(Type t, string key) =>
            ((OathBadgePower)RuntimeHelpers.GetUninitializedObject(t))
                .Localization!.First(r => r.Item1 == key).Item2;
        Assert.Equal("Hydro Oath", Row(typeof(HydroOathPower), "title"));
        Assert.Equal("Oath", Row(typeof(UnswornOathPower), "title"));
        Assert.EndsWith("\nOath: Pyro {PyroOath}, Hydro {HydroOath}, "
                      + "Electro {ElectroOath}, Cryo {CryoOath}.",
                        Row(typeof(CryoOathPower), "smartDescription"));
        Assert.StartsWith("Your [gold]current element[/gold] is Cryo. Your "
                        + "Swirls apply 1",
                          Row(typeof(CryoOathPower), "description"));
    }

    // ---- Four Winds' Ascension and Boreas's Fang (sec.4) ---------------------

    [Fact]
    public void Ascension_is_six_anemo_then_three_per_oath_and_does_not_exhaust()
    {
        var card = new ProtoVkFourWindsAscension();
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(CardType.Attack, card.Type);
        Assert.DoesNotContain(CardKeyword.Exhaust, card.Keywords);
        Assert.Equal(6m, Var(card, "Damage"));
        Assert.Equal(3m, Var(card, "VkPer"));
        // The upgraded card's numbers: 9 Anemo, 4 per Oath.
        var up = Upgraded<ProtoVkFourWindsAscension>();
        Assert.Equal(9m, Var(up, "Damage"));
        Assert.Equal(4m, Var(up, "VkPer"));
        Assert.Equal(Element.Anemo, ((IElementalCard)card).Element);
        Assert.Contains("VarkaCards.AscensionHit",
                        Il.Calls(Il.Method("ProtoVkFourWindsAscension", "OnPlay")));
        // Its elemental hit carries the current element and credits nothing.
        var hit = Il.Calls(Il.Method("VarkaCards", "CurrentElementHit"));
        Assert.Contains("HitElement.Carry", hit);
        Assert.Contains("VarkaOath.NoApplyCredit", hit);
        Assert.Equal(15, VarkaCards.CurrentElementDamage(0m, 3m, 5));
        Assert.Equal(20, VarkaCards.CurrentElementDamage(10m, 2m, 5));
        Assert.IsAssignableFrom<ITomeCard>(card);
    }

    [Fact]
    public void The_fang_rolls_the_starter_knight_on_a_new_run()
    {
        var obtained = Il.Calls(Il.Method("BoreasFang", "AfterObtained"));
        Assert.Contains("PlayerRngSet.get_Transformations", obtained);
        Assert.Contains("VarkaRules.StarterKnights", obtained);
        Assert.Contains("CardCmd.Transform", obtained);
        Assert.Contains("CompanionSlot.Roll",
                        Il.Calls(Il.Method("BoreasFang", "TryModifyCardRewardOptions")));
    }

    // ---- the cards' own numbers (the ruled picks) ----------------------------

    [Fact]
    public void Lisa_is_four_plus_three_per_attack_and_five_plus_four_upgraded()
    {
        var lisa = new ProtoVkLisaVioletArc();
        Assert.Equal(4m, Var(lisa, "CalculationBase"));
        Assert.Equal(3m, Var(lisa, "CalculationExtra"));
        var up = Upgraded<ProtoVkLisaVioletArc>();
        Assert.Equal(5m, Var(up, "CalculationBase"));
        Assert.Equal(4m, Var(up, "CalculationExtra"));
        Assert.Contains("ElementalHit.ApplyOnly",
                        Il.Calls(Il.Method("ProtoVkLisaVioletArc", "OnPlay")));
    }

    [Fact]
    public void The_ruled_picks_are_on_the_cards()
    {
        var bunny = new ProtoVkAmberBaronBunny();
        Assert.Equal(6m, Var(bunny, "CalculationBase"));
        Assert.Equal(6m, Var(bunny, "PowerAmount"));
        var bunnyUp = Upgraded<ProtoVkAmberBaronBunny>();
        Assert.Equal(8m, Var(bunnyUp, "CalculationBase"));
        Assert.Equal(8m, Var(bunnyUp, "PowerAmount"));
        var standard = new ProtoVkFavonianStandard();
        Assert.Equal(4m, Var(standard, "PowerAmount"));
        Assert.Equal(5m, Var(Upgraded<ProtoVkFavonianStandard>(), "PowerAmount"));
        var avatar = new ProtoVkNorthwindAvatar();
        Assert.Equal(2, avatar.EnergyCost.Canonical);
        Assert.Equal(10m, Var(avatar, "Damage"));
        Assert.Equal(10m, Var(avatar, "VkBase"));
        Assert.Equal(2m, Var(avatar, "VkPer"));
        var up = Upgraded<ProtoVkNorthwindAvatar>();
        Assert.Equal(14m, Var(up, "Damage"));
        Assert.Equal(14m, Var(up, "VkBase"));
        Assert.Equal(2m, Var(up, "VkPer"));
        Assert.Contains(CardKeyword.Exhaust, new ProtoVkEyeOfTheStorm().Keywords);
    }

    [Fact]
    public void Each_starter_knight_is_eight_block_and_its_element()
    {
        var knights = new (CardModel Card, Element Element)[]
        {
            (new ProtoVkAmberFieryRain(), Element.Pyro),
            (new ProtoVkBarbaraMelodyLoop(), Element.Hydro),
            (new ProtoVkLisaLightningRose(), Element.Electro),
            (new ProtoVkKaeyaGlacialWaltz(), Element.Cryo),
        };
        foreach (var (card, element) in knights)
        {
            Assert.Equal(CardRarity.Basic, card.Rarity);
            Assert.Equal(8m, Var(card, "CalculationBase"));
            Assert.Equal(element, VarkaOath.KnightElement(card));
            Assert.True(VarkaRules.IsStarterKnight(card));
            Assert.Contains("ElementalHit.ApplyOnly",
                            Il.Calls(Il.Method(card.GetType().Name, "OnPlay")));
        }
        Assert.Equal(11m, Var(Upgraded<ProtoVkKaeyaGlacialWaltz>(), "CalculationBase"));
        Assert.Equal(knights.Select(k => $"ModelDb.Card<{k.Card.GetType().Name}>"),
                     Cards("VarkaRules", "StarterKnights"));
    }

    [Fact]
    public void The_verbs_are_one_call_each()
    {
        Assert.Contains("VarkaCards.ApplyCurrentElement",
                        Il.Calls(Il.Method("ProtoVkFavoniusDrill", "OnPlay")));
        Assert.Contains("ElementalHit.ApplyOnly",
                        Il.Calls(Il.Method("VarkaCards", "ApplyCurrentElement")));
        Assert.Contains("VarkaOath.Gain",
                        Il.Calls(Il.Method("VarkaCards", "GainCurrentOath")));
        Assert.Contains("VarkaOath.KnightsPlayedThisTurn",
                        Il.Calls(Il.Method("ProtoVkKnightlyGuard", "OnPlay")));
        Assert.Contains("ElementalHit.DealUnelemented",
                        Il.Calls(Il.Method("VarkaCards", "SwirledTakeMore")));
        Assert.Contains("VarkaRules.SwirlFreshAuras",
                        Il.Calls(Il.Method("VarkaCards", "SwirlFreshAuras")));
        Assert.Contains("ElementalHit.ApplyOnly",
                        Il.Calls(Il.Method("VarkaRules", "SwirlFreshAuras")));
        Assert.Contains("VarkaRules.ChooseElement",
                        Il.Calls(Il.Method("VarkaCards", "ChangeOfGuard")));
        Assert.Contains("VarkaOathLedger.Rally",
                        Il.Calls(Il.Method("VarkaCards", "Rally")));
        Assert.Contains("VarkaOathLedger.Split",
                        Il.Calls(Il.Method("VarkaCards", "Accord")));
        Assert.Contains("CardEnergyCost.SetThisTurn",
                        Il.Calls(Il.Method("VarkaCards", "UnfurledBanner")));
        Assert.Contains("VarkaOath.Gain",
                        Il.Calls(Il.Method("VarkaCards", "OathPerCryoEnemy")));
    }

    [Fact]
    public void Change_of_guards_faces_map_to_their_elements()
    {
        var faces = new CardModel[]
        {
            new ElementOptionPyro(), new ElementOptionHydro(),
            new ElementOptionElectro(), new ElementOptionCryo(),
        };
        Assert.Equal(VarkaOathLedger.Elements,
                     faces.Select(f => ((ElementOption)f).OptionElement));
        Assert.Contains("CardSelectCmd.FromSimpleGrid",
                        Il.Calls(Il.Method("VarkaRules", "ChooseElement")));
    }

    // ---- the other powers ----------------------------------------------------

    [Theory]
    [InlineData(true, true, Element.Anemo, 4, true)]
    [InlineData(true, true, Element.Anemo, 7, true)]
    [InlineData(true, true, Element.Anemo, 3, false)]
    [InlineData(true, true, Element.Pyro, 5, false)]
    [InlineData(true, false, Element.Anemo, 5, false)]
    [InlineData(false, true, Element.Anemo, 5, false)]
    public void Stormward_stance_needs_four_oath_and_an_anemo_attack(
        bool powered, bool attack, Element hit, int oath, bool expected)
    {
        Assert.Equal(expected,
            StormwardStancePower.Applies(powered, attack, hit, oath));
    }

    [Theory]
    [InlineData(false, Element.Pyro, Element.Hydro, Reaction.None)]
    [InlineData(true, Element.Pyro, Element.Hydro, Reaction.Vaporize)]
    [InlineData(true, Element.Electro, Element.Pyro, Reaction.Overload)]
    [InlineData(true, Element.Pyro, Element.None, Reaction.None)]
    [InlineData(true, Element.Pyro, Element.Pyro, Reaction.None)]
    public void Converging_winds_reacts_where_a_spread_lands(
        bool converges, Element spread, Element existing, Reaction expected)
    {
        Assert.Equal(expected,
            ConvergingWindsPower.SpreadReaction(converges, spread, existing));
    }

    [Fact]
    public void Gale_sweep_takes_the_fresh_auras_when_it_is_played()
    {
        var fresh = Seat.Klee(30).WithPower<PyroAuraPower>(2);
        var spent = Seat.Klee(30).WithPower<HydroAuraPower>(2);
        spent.Creature.Powers.OfType<AuraPower>().Single().Spent = true;
        var bare = Seat.Klee(30);
        Assert.Equal(new[] { fresh.Creature },
                     VarkaRules.FreshAuraBodies(new[]
                     {
                         fresh.Creature, spent.Creature, bare.Creature,
                     }));
        Assert.Contains("VarkaRules.HitFreshAuras",
                        Il.Calls(Il.Method("ProtoVkGaleSweep", "OnPlay")));
    }

    [Fact]
    public void The_swirl_readers_diff_his_swirl_count()
    {
        foreach (var type in new[] { "ProtoVkTempestCharge", "ProtoVkCrosswind",
                                     "ProtoVkRisingGale" })
        {
            var calls = Il.CallSequence(Il.Method(type, "OnPlay"));
            Assert.Equal(2, calls.Count(c => c == "VarkaOath.SwirlsMadeBy"));
        }
    }

    // ---- the Knights -------------------------------------------------------

    [Fact]
    public void His_knights_are_his_personal_companions()
    {
        // Read off the call graph: ModelDb holds nothing headless.
        CardModel Make(string call) => (CardModel)Activator.CreateInstance(
            typeof(VarkaRules).Assembly.GetTypes().Single(
                t => t.Name == call.Substring("ModelDb.Card<".Length).TrimEnd('>')))!;
        var pool = Cards("VarkaRules", "PoolKnights").Select(Make).ToList();
        var starters = Cards("VarkaRules", "StarterKnights").Select(Make).ToList();
        Assert.Equal(13, pool.Count);          // 9, and 13 since the expansion
        Assert.Equal(4, starters.Count);
        Assert.All(pool, k => Assert.True(VarkaRules.IsKnight(k)));
        Assert.All(starters, k => Assert.True(VarkaRules.IsKnight(k)));
        Assert.DoesNotContain(pool, VarkaRules.IsStarterKnight);
        Assert.Equal(Element.Pyro, VarkaOath.KnightElement(new ProtoVkDilucSearingOnslaught()));
        Assert.Equal(CardType.Attack, new ProtoVkDilucSearingOnslaught().Type);
        Assert.Equal(Element.Cryo, VarkaOath.KnightElement(new ProtoVkEulaIcetideVortex()));
        // Jean is a Skill that sets no element; his own Attacks are not Knights.
        Assert.False(VarkaRules.IsKnight(new ProtoVkJeanDandelionBreeze()));
        Assert.False(VarkaRules.IsKnight(new ProtoVkWindboundExecution()));
        Assert.Equal(Element.None, VarkaOath.KnightElement(new ProtoVkFavoniusDrill()));
    }

    [Fact]
    public void Grand_masters_order_repeats_the_next_knight_this_turn()
    {
        Assert.Contains("VarkaRules.IsKnight",
                        Il.Calls(Il.Method("GrandMastersOrderPower",
                                           "ModifyCardPlayCount")));
        var card = new ProtoVkGrandMastersOrder();
        Assert.Equal(0, card.EnergyCost.Canonical);
        Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        Assert.Contains(CardKeyword.Retain,
                        Upgraded<ProtoVkGrandMastersOrder>().Keywords);
    }

    [Fact]
    public void Roll_call_adds_a_pool_knight_and_chooses_it_upgraded()
    {
        Assert.Contains("VarkaRules.AddKnight",
                        Il.Calls(Il.Method("ProtoVkKnightsRollCall", "OnPlay")));
        var add = Il.Calls(Il.Method("VarkaRules", "AddKnight"));
        Assert.Contains("VarkaRules.PoolKnights", add);
        Assert.Contains("CardSelectCmd.FromSimpleGrid", add);
        Assert.Contains("CardEnergyCost.SetThisTurn", add);
    }

    // ---- the starter and the pool ------------------------------------------

    [Fact]
    public void The_starter_is_the_base_pair_windbound_and_a_starter_knight()
    {
        var deck = Cards("VarkaRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<StrikeSilent>"));
        Assert.Equal(4, deck.Count(c => c == "ModelDb.Card<DefendSilent>"));
        Assert.Single(deck, c => c == "ModelDb.Card<ProtoVkWindboundExecution>");
        Assert.Single(deck, c => c == "ModelDb.Card<ProtoVkAmberFieryRain>");
        Assert.Equal(new[] { "ModelDb.Card<StrikeSilent>" },
                     Cards("VarkaRoster", "StarterStrike"));
        Assert.Equal(new[] { "ModelDb.Card<DefendSilent>" },
                     Cards("VarkaRoster", "StarterDefend"));
        Assert.Contains("ModelDb.Relic",
                        Il.Calls(Il.Method("VarkaRoster", "StartingRelics")));
    }

    [Fact]
    public void The_pool_is_seventy_eight_cards_twenty_thirty_five_and_twenty_three()
    {
        var pool = Cards("VarkaRoster", "Pool")
            .Select(c => c.Substring("ModelDb.Card<".Length).TrimEnd('>'))
            .ToList();
        // The expansion (2026-10-01): 41 to 78.
        Assert.Equal(78, pool.Count);
        Assert.Equal(78, pool.Distinct().Count());
        var types = typeof(VarkaRules).Assembly.GetTypes()
            .Where(t => pool.Contains(t.Name))
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .ToList();
        Assert.Equal(78, types.Count);
        Assert.Equal(20, types.Count(c => c.Rarity == CardRarity.Common));
        Assert.Equal(35, types.Count(c => c.Rarity == CardRarity.Uncommon));
        Assert.Equal(23, types.Count(c => c.Rarity == CardRarity.Rare));
        Assert.Equal(13, types.Count(VarkaRules.IsKnight));
        // The starter's and the Fang's cards are not offered.
        foreach (var starter in new[] { "ProtoVkFourWindsAscension",
                                        "ProtoVkWindboundExecution",
                                        "ProtoVkAmberFieryRain",
                                        "ProtoVkBarbaraMelodyLoop",
                                        "ProtoVkLisaLightningRose",
                                        "ProtoVkKaeyaGlacialWaltz" })
        {
            Assert.DoesNotContain(starter, pool);
        }
    }

    [Fact]
    public void Large_capsule_asks_varka_for_his_pair()
    {
        var strike = Il.Calls(Il.Method("ArmStarterBasics", "StrikeFor"));
        Assert.Contains("VarkaRoster.StarterStrike", strike);
        Assert.Contains("VarkaPrototype.get_Enabled", strike);
        Assert.Contains("VarkaRoster.StarterDefend",
                        Il.Calls(Il.Method("ArmStarterBasics", "DefendFor")));
    }

#if VARKA_PROTOTYPE
    // ---- the character (compiled only with -p:VarkaPrototype=true) ----------

    [Fact]
    public void Varka_is_eighty_hp_ninety_nine_gold_and_he()
    {
        var varka = new Varka();
        Assert.Equal(80, varka.StartingHp);
        Assert.Equal(99, varka.StartingGold);
        Assert.Equal(MegaCrit.Sts2.Core.Entities.Characters.CharacterGender.Masculine,
                     varka.Gender);
        var loc = varka.Localization!.ToDictionary(r => r.Item1, r => r.Item2);
        Assert.Equal("Varka", loc["title"]);
        Assert.Equal("he", loc["pronounSubject"]);
        Assert.IsAssignableFrom<IVarkaCharacter>(varka);
        Assert.Contains("VarkaRoster.StartingDeck",
                        Il.Calls(Il.Method("Varka", "get_StartingDeck")));
        Assert.Contains("VarkaRoster.StartingRelics",
                        Il.Calls(Il.Method("Varka", "get_StartingRelics")));
    }

    [Fact]
    public void His_oath_reads_through_the_door_on_his_own_seat()
    {
        var varka = Seat.Varka().Creature;
        var ledger = VarkaOathLedger.For(varka);
        ledger.Add(Element.Hydro, 3);
        ledger.Add(Element.Pyro, 1);
        Assert.False(VarkaOath.HasCurrent(varka));
        Assert.Equal(0, VarkaOath.CurrentOath(varka));
        Assert.Equal(2, VarkaOath.ElementsWithOath(varka));
        ledger.SetCurrent(Element.Hydro);
        Assert.Equal(Element.Hydro, VarkaOath.Current(varka));
        Assert.Equal(3, VarkaOath.CurrentOath(varka));
        Assert.Equal(1, VarkaOath.Count(varka, Element.Pyro));
        // With the arm off he has none.
        VarkaPrototype.Enabled = false;
        Assert.Equal(0, VarkaOath.CurrentOath(varka));
    }

    /// <summary>
    /// Four Winds' Ascension's and Northwind Avatar's second hit carries his
    /// current element through <see cref="HitElement.Carry"/>, the scope the
    /// retired Knights' Muster's hit took; the Varka seat of 2026-09-29 saw a
    /// carried Vaporize land with no bonus it could see. The bonus is there:
    /// the aura's multiplier reads the carried element. Run for real, both
    /// directions of Vaporize.
    /// </summary>
    [Fact]
    public void A_current_element_hit_amplifies_like_any_hit()
    {
        var varka = Seat.Varka().Creature;
        var avatar = new ProtoVkNorthwindAvatar();
        var hydroBody = Seat.Klee(30).WithPower<HydroAuraPower>(2).Creature;
        var hydro = hydroBody.Powers.OfType<HydroAuraPower>().Single();
        var pyroBody = Seat.Klee(30).WithPower<PyroAuraPower>(2).Creature;
        var pyro = pyroBody.Powers.OfType<PyroAuraPower>().Single();
        var move = MegaCrit.Sts2.Core.ValueProps.ValueProp.Move;
        var vaporize = ReactionTable.AmplifierMultiplier(Reaction.Vaporize, varka);
        Assert.True(vaporize > 1m);
        using (HitElement.Carry(avatar, Element.Pyro))
        {
            Assert.Equal(vaporize, hydro.ModifyDamageMultiplicative(
                hydroBody, 10m, move, varka, avatar, null));
        }
        using (HitElement.Carry(avatar, Element.Hydro))
        {
            Assert.Equal(vaporize, pyro.ModifyDamageMultiplicative(
                pyroBody, 10m, move, varka, avatar, null));
        }
    }

    [Fact]
    public void He_is_a_roster_character_from_mondstadt()
    {
        var seat = Seat.Varka();
        Assert.Equal("varka", CompanionPool.CharacterId(seat.Player));
        Assert.Equal("mondstadt", CompanionPool.HomeNation(seat.Player));
        Assert.True(VarkaPrototype.IsVarka(seat.Creature));
        Assert.False(VarkaPrototype.IsVarka(Seat.Klee().Creature));
    }

    [Fact]
    public void His_pool_offers_the_forty_one_and_holds_the_rest()
    {
        Assert.Contains("VarkaRoster.Pool",
                        Il.Calls(Il.Method("VarkaCardPool", "FilterThroughEpochs")));
        var members = Il.Calls(Il.Method("VarkaCardPool", "GenerateAllCards"));
        Assert.Contains("VarkaRoster.Members", members);
        Assert.Contains("VarkaModalOptions.get_All", members);
        Assert.Contains("ModelDb.Relic",
                        Il.Calls(Il.Method("VarkaRelicPool", "GenerateAllRelics")));
    }
#endif
}
