using System;
using System.Linq;
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
/// AND THE ONE THING THAT DID NOT COME FREE: the element. A base card is
/// <c>sealed</c> and cannot implement <see cref="IElementalCard"/>, and the mod
/// asked the CARD what a hit applies. The sim has always asked the PLAYER
/// (`tier0/engine/effects._element_for`, catalyst cadence), and
/// <see cref="CatalystCadence"/> is the mod catching up (`EB-307`). Without it
/// Klee's four Strikes would have applied no Pyro at all -- half of rule 5,
/// silently absent.
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

    // ---- rule 5: the element is the character's ---------------------------

    [Fact]
    public void A_base_strike_applies_the_characters_element_under_her_arm()
    {
        var klee = KleeOverhaul.Enabled;
        var kokomi = KokomiOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            KokomiOverhaul.Enabled = true;

            // THE WHOLE OF `EB-307`. A base Strike declares nothing, so the
            // per-card read gave it `Element.None` and rule 5 quietly stopped
            // being true of half her deck.
            Assert.Equal(Element.Pyro, CatalystCadence.PrintedElement(
                new StrikeIronclad(), Seat.Klee().Creature));
            Assert.Equal(Element.Hydro, CatalystCadence.PrintedElement(
                new StrikeSilent(), Seat.Kokomi().Creature));

            // A DEFEND STILL APPLIES NOTHING: the cadence is about Attacks,
            // which is the sim's rule too (`_element_for` guards on
            // `card.type == "attack"`).
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new DefendIronclad(), Seat.Klee().Creature));

            // AND IT IS HERS, NOT ANY SEAT'S. Furina is Skill-grade, not
            // catalyst; in co-op her Strike must not start applying Pyro
            // because Klee is at the table.
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new StrikeIronclad(), Seat.Furina().Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }
    }

    [Fact]
    public void A_card_that_declares_an_element_keeps_it_and_a_companion_is_exempt()
    {
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            var seat = Seat.Klee().Creature;

            // The first branch answers a row that DECLARES, so the fallback
            // can never overwrite a printed element -- including a deliberate
            // `Element.None`.
            Assert.Equal(Element.Cryo, CatalystCadence.PrintedElement(
                new ProtoMcKaeyaFrostgnaw(), seat));

            // COMPANIONS ARE EXEMPT FROM CADENCE in both engines (the sim:
            // "what a companion applies is the sheet's explicit call"). Itto's
            // Rare is the case that would otherwise slip through: a companion
            // ATTACK whose damage is all `applies_element: false`, so the
            // codegen gives it no `IElementalCard` at all.
            var itto = new ProtoIttoSuperlativeSuperstrengthEither();
            Assert.IsAssignableFrom<ICompanionCard>(itto);
            Assert.IsNotAssignableFrom<IElementalCard>(itto);
            Assert.Equal(CardType.Attack, itto.Type);
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(itto, seat));
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void With_both_arms_off_the_funnel_is_the_old_expression()
    {
        // THE ACCEPTANCE CONDITION, and the only one this change owes: with
        // the arms off `PrintedElement` is `cardSource is IElementalCard e ?
        // e.Element : Element.None`, character for character.
        var klee = KleeOverhaul.Enabled;
        var kokomi = KokomiOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;
            KokomiOverhaul.Enabled = false;
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new StrikeIronclad(), Seat.Klee().Creature));
            Assert.Equal(Element.None, CatalystCadence.PrintedElement(
                new StrikeSilent(), Seat.Kokomi().Creature));
            // A declaring row is untouched either way, which is what makes the
            // shipped kits byte-identical.
            Assert.Equal(Element.Cryo, CatalystCadence.PrintedElement(
                new ProtoMcKaeyaFrostgnaw(), Seat.Klee().Creature));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }
    }

    [Fact]
    public void The_element_funnel_still_has_exactly_one_reader()
    {
        // The fallback had to go INSIDE the funnel, not beside it: an aura
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
    public void The_opening_spark_is_one_and_is_granted_on_turn_one()
    {
        // [USER]: "Regent starts with 3 stars and has to generate more through
        // cards, so 1 is a reasonable compromise." The VALUE is mirrored by
        // `tools/lint_constant_parity.py`; what is pinned here is the wiring.
        Assert.Equal(1, KleeOverhaulLaw.OpeningSpark);

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
