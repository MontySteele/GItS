using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Models.Cards;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// R242's ONE RULING, ACROSS BOTH ARMS: "where a character's basics are a
/// renamed Strike or Defend with the same stat line, the base game's Strike and
/// Defend replace them." This file is the engine answer that made it buildable
/// and the pins on what it moved.
///
/// THE ENGINE ANSWER, in one line: the base game ships one Strike and one
/// Defend PER CHARACTER, not one shared pair, and a modded character's starting
/// deck can hold any of them because <c>CardModel.Pool</c> resolves by scanning
/// <c>ModelDb.AllCardPools</c> rather than by asking the owner. The upgrades
/// (+3, so Strike+ 9 and Defend+ 8) and the portrait come with the card.
///
/// AND THE ELEMENT. A base card is <c>sealed</c> and cannot implement
/// <see cref="IElementalCard"/>, so it applies nothing -- the ruled reading
/// ("Those cards are supposed to be bad!", 2026-09-02). `EB-307` had made the
/// mod fall back on the PLAYER's element for a card that named none; that
/// fallback is gone ([USER], 2026-10-05: the element "lives in the card pool
/// as a symbol on relevant elemental cards"), so <see cref="CatalystCadence"/>
/// reads the card alone and who plays it never matters.
///
/// THE COLLECTION IS LOAD-BEARING: <c>KleeOverhaul.Enabled</c> and
/// <c>KokomiOverhaul.Enabled</c> are one static apiece for the whole process.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class BaseBasicsTests
{
    private static System.Collections.Generic.IReadOnlyList<string> Cards(
        string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card")).ToList();

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
    }

    // ---- the two starters, draft 4 / R242 ---------------------------------

    [Fact]
    public void Klees_starter_is_four_strikes_four_defends_and_two_of_her_own()
    {
        // Read off the IL rather than by building the models, which needs
        // ModelDb (PrototypeRoster's header has the poisoned-type trap).
        // [USER], R242: "base characters open with four Strikes, four Defends
        // and two good cards of their own, and Klee had three, two and five."
        var deck = Cards("KleeOverhaulRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c.Contains("StrikeIronclad")));
        Assert.Equal(4, deck.Count(c => c.Contains("DefendIronclad")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoKoJumpyDumpty")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoKoKapow")));
        // The two draft-3 rows the ruling deleted are gone from the arm, not
        // merely unused: a `ModelDb.Card<ProtoKoKaboom>` anywhere would not
        // compile, so absence from THIS list is the readable half.
        Assert.DoesNotContain(deck, c => c.Contains("Kaboom"));
        Assert.DoesNotContain(deck, c => c.Contains("DuckAndCover"));
    }

    [Fact]
    public void Kokomis_starter_is_four_strikes_four_defends_and_two_of_her_own()
    {
        var deck = Cards("KokomiOverhaulRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c.Contains("StrikeSilent")));
        Assert.Equal(4, deck.Count(c => c.Contains("DefendSilent")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoKkKuragesOath")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoKkSlackWater")));
        Assert.DoesNotContain(deck, c => c.Contains("WatersEdge"));
        Assert.DoesNotContain(deck, c => c.Contains("CoralGuard"));
    }

    [Fact]
    public void The_stages_starter_is_four_strikes_four_defends_and_two_of_her_own()
    {
        // [USER], 2026-09-28: "Typically we'd include 4 strikes, 4 defends and
        // 2 actually useful cards that teach the character's core mechanics -
        // this seems like an unnecessary power spike." and "I agree with
        // keeping Curtain Raise and Rising Applause."
        var deck = Cards("FurinaStageRoster", "StartingDeck");
        Assert.Equal(10, deck.Count);
        Assert.Equal(4, deck.Count(c => c.Contains("StrikeSilent")));
        Assert.Equal(4, deck.Count(c => c.Contains("DefendSilent")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoFsCurtainRise")));
        Assert.Equal(1, deck.Count(c => c.Contains("ProtoFsStandingOvation")));
        Assert.DoesNotContain(deck, c => c.Contains("SoloistsSolicitation"));
        Assert.DoesNotContain(deck, c => c.Contains("StagePresence"));
        Assert.DoesNotContain(deck, c => c.Contains("RegalBearing"));
        Assert.DoesNotContain(deck, c => c.Contains("SalonDebut"));
    }

    [Fact]
    public void The_base_pair_is_the_base_stat_line_and_the_base_upgrade()
    {
        // THE ANSWER TO "do the base upgrades and art come for free?", run
        // through the game's own `UpgradeInternal` rather than read off the
        // decompile. Both characters' pairs, because the base game's own
        // comment is that the five Strikes differ only in "portrait, attack
        // vfx, and color" -- so if that were ever false, it would be false
        // here.
        foreach (var strike in new CardModel[]
                 { new StrikeIronclad(), new StrikeSilent() })
        {
            Assert.Equal(CardType.Attack, strike.Type);
            Assert.Equal(CardRarity.Basic, strike.Rarity);
            Assert.Equal(6m, strike.DynamicVars.Damage.BaseValue);
            Upgrade(strike);
            Assert.Equal(9m, strike.DynamicVars.Damage.BaseValue);
        }
        foreach (var defend in new CardModel[]
                 { new DefendIronclad(), new DefendSilent() })
        {
            Assert.Equal(CardType.Skill, defend.Type);
            Assert.Equal(CardRarity.Basic, defend.Rarity);
            Assert.Equal(5m, defend.DynamicVars.Block.BaseValue);
            Upgrade(defend);
            Assert.Equal(8m, defend.DynamicVars.Block.BaseValue);
        }
    }

    [Fact]
    public void Each_arm_takes_the_pair_whose_colour_its_own_pool_borrows()
    {
        // WHY IRONCLAD FOR KLEE AND SILENT FOR KOKOMI, and it is not taste. A
        // card's frame and energy orb come off `CardModel.Pool`, which for a
        // base basic is the base character's pool -- so the only way the four
        // Strikes sit in her hand looking like her own cards is to pick the
        // pool her own already borrows from. Both mod pools have borrowed
        // theirs since C1; this pin is what stops one of them being re-skinned
        // without the starter following it.
        // ALLOCATED, NOT RESOLVED THROUGH ModelDb: the base pools are
        // registered by the game's own boot, which this harness does not run
        // (README, "The headless boundary"). Both properties are literal
        // expression bodies, so an uninitialised instance answers them.
        static CardPoolModel Pool<T>() where T : CardPoolModel =>
            (CardPoolModel)System.Runtime.CompilerServices.RuntimeHelpers
                .GetUninitializedObject(typeof(T));

        Assert.Equal(Pool<IroncladCardPool>().EnergyColorName,
                     Pool<KleeCardPool>().EnergyColorName);
        Assert.Equal(Pool<IroncladCardPool>().CardFrameMaterialPath,
                     Pool<KleeCardPool>().CardFrameMaterialPath);
        Assert.Equal(Pool<SilentCardPool>().EnergyColorName,
                     Pool<KokomiCardPool>().EnergyColorName);
        Assert.Equal(Pool<SilentCardPool>().CardFrameMaterialPath,
                     Pool<KokomiCardPool>().CardFrameMaterialPath);
        // The Stage (2026-09-28) deals Silent's pair for the same reason.
        Assert.Equal(Pool<SilentCardPool>().EnergyColorName,
                     Pool<FurinaCardPool>().EnergyColorName);
        Assert.Equal(Pool<SilentCardPool>().CardFrameMaterialPath,
                     Pool<FurinaCardPool>().CardFrameMaterialPath);
    }

    // ---- the two cards of her own -----------------------------------------

    [Fact]
    public void Ka_pow_is_free_to_play_and_retains_from_print()
    {
        // Slice sec.3, draft 4: "Ka-pow! is the detonator at 0 energy: cashing
        // costs a card and a moment, never energy." The ENERGY is still the
        // assertion, and it does not move.
        //
        // ROUND 5 PICK 1, at its default ([USER] 2026-09-02: "I'm fine with
        // the default on Ka-Pow!"): Retain is on the BASE card now, not the
        // upgrade. Draft 4's reasoning was "the upgrade's Retain lets a cooked
        // Bomb be held for" -- and holding the Bomb is the arm's whole tempo,
        // so paying an upgrade for it made the base card fight its own kit.
        // The upgrade buys damage instead, 4 -> 7, by the default rule.
        var card = new ProtoKoKapow();
        Assert.Equal(0, (int)typeof(CardModel)
            .GetProperty("CanonicalEnergyCost", HeadlessGame.All)!
            .GetValue(card)!);
        Assert.Equal(4m, card.DynamicVars.Damage.BaseValue);
        Assert.Contains(CardKeyword.Retain, card.Keywords);

        var upgraded = new ProtoKoKapow();
        Upgrade(upgraded);
        Assert.Contains(CardKeyword.Retain, upgraded.Keywords);
        Assert.Equal(7m, upgraded.DynamicVars.Damage.BaseValue);
    }

    [Fact]
    public void Jumpy_dumpty_plants_on_the_enemy_you_choose()
    {
        // R242's other half of the starter: "Jumpy Dumpty is the bomb, placed
        // on the enemy you choose so the one detonator lines up with it." A
        // random plant and a single detonator is a coin flip, not a plan --
        // so the TARGET is the assertion, and it is read two ways round: the
        // declared TargetType and the call the body makes.
        var card = new ProtoKoJumpyDumpty();
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);
        var body = Il.Calls(Il.Method("ProtoKoJumpyDumpty", "OnPlay"));
        Assert.Contains(body, c => c.Contains("ProtoBombPower.Place"));
        Assert.DoesNotContain(body, c => c.Contains("PlaceOnRandom"));

        // And the payload is still hers: Bomb 8 -> 11, Mine 3 -> 4.
        Assert.Equal(8m, card.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(3m, card.DynamicVars["PayloadMine"].BaseValue);
        var upgraded = new ProtoKoJumpyDumpty();
        Upgrade(upgraded);
        Assert.Equal(11m, upgraded.DynamicVars["BombSize"].BaseValue);
        Assert.Equal(4m, upgraded.DynamicVars["PayloadMine"].BaseValue);
    }

    // ---- rule 5: the element is the card's ----------------------------------

    [Fact]
    public void A_base_strike_applies_nothing_for_anybody()
    {
        try
        {

            // [USER], 2026-09-02: "I think we actually SHOULD remove the
            // elemental application from the basic Strikes for all characters.
            // Those cards are supposed to be bad!" `EB-307` read R242's swap
            // the other way -- that her Strikes had to keep applying -- and
            // this is the ruled reading of the same swap. LAW's cadence line
            // now carries the exemption.
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                new StrikeIronclad(), Seat.Klee().Creature));
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                new StrikeSilent(), Seat.Kokomi().Creature));
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                new DefendIronclad(), Seat.Klee().Creature));
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                new StrikeIronclad(), Seat.Furina().Creature));
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new StrikeIronclad()));
        }
        finally
        {
        }
    }

    [Fact]
    public void An_element_comes_with_the_card_and_not_the_hand()
    {
        // [USER], 2026-10-05: "that effect just lives in the card pool as a
        // symbol on relevant elemental cards". Klee's own Attack declares Pyro
        // through the codegen and keeps it in ANY hand; a base card at any
        // rarity -- `Breakthrough`, the Ironclad event card of `EB-331` --
        // declares nothing and applies nothing in anyone's.
        try
        {
            var fun = new ProtoKoForbiddenFun();
            Assert.Equal(Element.Pyro, CatalystCadence.PrintedElement(fun));
            Assert.Equal(Element.Pyro,
                AuraCmd.ElementOfPlay(fun, Seat.Klee().Creature));
            Assert.Equal(Element.Pyro,
                AuraCmd.ElementOfPlay(fun, Seat.Kokomi().Creature));

            // The Ancient declares Pyro outright, so it needs nobody's hand.
            Assert.Equal(Element.Pyro,
                CatalystCadence.PrintedElement(new JumpyDumptyMkOmega()));

            var breakthrough = new Breakthrough();
            Assert.IsNotAssignableFrom<CustomCardModel>(breakthrough);
            Assert.NotEqual(CardRarity.Basic, breakthrough.Rarity);
            Assert.Equal(CardType.Attack, breakthrough.Type);
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                breakthrough, Seat.Kokomi().Creature));
            Assert.Equal(Element.None, AuraCmd.ElementOfPlay(
                breakthrough, Seat.Klee().Creature));
        }
        finally
        {
        }
    }

    [Fact]
    public void The_element_funnel_still_has_exactly_one_reader()
    {
        // The card read sits INSIDE the funnel, not beside it: an aura
        // applied by one expression and reacted to by another is the worst
        // kind of bug to find in play (AuraCmd.ElementOfPlay's own header).
        Assert.Contains(
            Il.Calls(Il.Method("CompanionOverhaulRiders", "ElementFor")),
            c => c.Contains("CatalystCadence.PrintedElement"));
        Assert.Contains(
            Il.Calls(Il.Method("AuraCmd", "ElementOfPlay")),
            c => c.Contains("CompanionOverhaulRiders.ElementFor"));
    }

    // ---- rule 4's opening Spark (R242 pick 1) -----------------------------

    [Fact]
    public void The_opening_spark_is_three_and_is_granted_on_turn_one()
    {
        // [USER]: "Regent starts with 3 stars and has to generate more through
        // cards, so 1 is a reasonable compromise." The VALUE is mirrored by
        // `tools/lint_constant_parity.py`; what is pinned here is the wiring.
        // THREE since the Klee design review (2026-10-08, sec.4.6): Regent's 3.
        Assert.Equal(3, KleeOverhaulLaw.OpeningSpark);

        var grant = Il.Calls(Il.Method("KleeOverhaulOpening", "GrantSpark"));
        Assert.Contains(grant, c => c.Contains("SparkPower.Gain"));

        // The site is the sim's own combat-start moment -- turn 1 of the
        // player's turn, after the draw -- and the standing listener is what
        // calls it. A KIT RULE, NOT A RELIC CLAUSE: Touch of Orobas swaps
        // Pounding Surprise for ExplosiveFrags at the act-2 reward, and the
        // opening Spark has to survive that, so the grant is not on either.
        Assert.Contains(
            Il.Calls(Il.Method("KleeElementalHooks", "AfterPlayerTurnStart")),
            c => c.Contains("KleeOverhaulOpening.GrantSpark"));
        foreach (var relic in new[] { "PoundingSurprise", "ExplosiveFrags" })
        {
            var declared = typeof(KleeOverhaulLaw).Assembly.GetTypes()
                .Where(x => x.Name == relic)
                .SelectMany(x => x.GetMethods(HeadlessGame.All))
                .Where(m => m.DeclaringType?.Name == relic
                            && m.GetMethodBody() != null)
                .SelectMany(m => Il.Calls(m).ToArray())
                .ToList();
            Assert.DoesNotContain(declared,
                                  c => c.Contains("KleeOverhaulOpening"));
        }
    }

}
