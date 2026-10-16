#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Potions;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Models;
using SilentRelics = MegaCrit.Sts2.Core.Models.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KOKOMI'S OWN RELICS AND POTIONS
/// (<c>review/active/kokomi-relics-potions-2026-10-15.md</c>, kit census pick
/// 1 (a)). On <c>VarkaRelicsPotionsTests</c>' terms: every decision (a count,
/// a gate, a latch, a keyword) runs on a headless seat; what awaits a command
/// that needs a live combat (Block, Energy, a Mend, a pile move, a screen, a
/// carry-out) is pinned by its doors.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KokomiRelicsPotionsTests : IDisposable
{
    public KokomiRelicsPotionsTests()
    {
        HeadlessGame.Arm();
        KokomiOverhaulLedger.ResetAll();
    }

    public void Dispose()
    {
        KokomiOverhaulLedger.ResetAll();
    }

    // ==== the shape ==========================================================

    [Fact]
    public void Seven_relics_in_the_base_games_shape_and_three_potions()
    {
        var rarities = KokomiArmRelics.Types
            .Select(t => Canon<RelicModel>(t).Rarity).ToList();
        Assert.Equal(new[]
        {
            RelicRarity.Common, RelicRarity.Uncommon, RelicRarity.Uncommon,
            RelicRarity.Rare, RelicRarity.Rare, RelicRarity.Rare,
            RelicRarity.Shop,
        }, rarities.ToArray());

        var potions = KokomiPotions.Types.Select(t => Canon<PotionModel>(t)).ToList();
        Assert.Equal(
            new[] { PotionRarity.Common, PotionRarity.Uncommon, PotionRarity.Rare },
            potions.Select(p => p.Rarity).ToArray());
        Assert.All(potions, p => Assert.Equal(PotionUsage.CombatOnly, p.Usage));
        Assert.All(potions, p => Assert.Equal(TargetType.AnyPlayer, p.TargetType));
    }

    [Fact]
    public void Every_face_is_the_papers_word_for_word()
    {
        var faces = KokomiArmRelics.Types.Concat(KokomiPotions.Types)
            .Select(t => ((ILocalizationProvider)Canon<AbstractModel>(t)).Localization!)
            .Select(loc => (loc[0].Item2, Plain(loc[1].Item2)))
            .ToArray();
        Assert.Equal(new[]
        {
            ("Sango Pearl", "The first card you plan each combat costs 0."),
            ("Resistance Armband",
             "The first time each turn you play a Companion, gain 4 Block."),
            ("Electro Sigil",
             "At the start of each combat, apply Electro to ALL enemies."),
            ("Everlasting Moonglow",
             "After your first Plan each turn is carried out, return it to "
           + "your Hand unless it Exhausts."),
            ("Ocean-Hued Clam",
             "Whenever you trigger an Elemental Reaction, Mend 1."),
            ("Kurage Lantern", "Your Stings and Wards are not Ethereal."),
            ("Resistance Muster Roll",
             "At the start of each combat, choose 1 of 3 random Inazuma "
           + "Companions to add to your Hand. It costs 0 this turn."),
            ("Bottled Shoal", "Add 3 Stings to your Hand."),
            ("Bottled Tide",
             "The Bake-Kurage carries out every waiting Plan now."),
            ("A Stunning Stratagem",
             "Next turn, every Plan is carried out twice."),
        }, faces);
    }

    // ==== the pools ==========================================================

    [Fact]
    public void Her_pool_lists_her_seven_and_offers_them_without_the_borrow()
    {
        Assert.Equal(
            new[] { typeof(TamakushiCasket) }.Concat(KokomiArmRelics.Types)
                .Append(typeof(WatatsumiCasket)),
            ArmRelicPools.KokomiArmPool);

        var members = Il.CallSequence(Il.Method("KokomiRelicPool", "GenerateAllRelics"));
        foreach (var t in ArmRelicPools.KokomiArmPool)
        {
            Assert.Contains($"ModelDb.Relic<{t.Name}>", members);
        }

        var pool = (KokomiRelicPool)RuntimeHelpers.GetUninitializedObject(typeof(KokomiRelicPool));
        SetField(pool, "_relics", Silent().Concat(ArmRelicPools.KokomiArmPool)
            .Select(t => (RelicModel)RuntimeHelpers.GetUninitializedObject(t)).ToList());
        var offer = pool.GetUnlockedRelics(null!).Select(r => r.GetType()).ToList();
        Assert.Equal(ArmRelicPools.KokomiArmPool.OrderBy(t => t.Name),
                     offer.OrderBy(t => t.Name));
        Assert.DoesNotContain(offer, t => t.Assembly != typeof(KokomiRelicPool).Assembly);
    }

    [Fact]
    public void Her_potion_pool_is_her_three()
    {
        var calls = Il.CallSequence(typeof(Kokomi).GetProperty("PotionPool")!.GetGetMethod()!);
        Assert.Contains("ModelDb.PotionPool<KokomiPotionPool>", calls);
        Assert.DoesNotContain("ModelDb.PotionPool<SilentPotionPool>", calls);

        var pool = Il.CallSequence(Il.Method("KokomiPotionPool", "GenerateAllPotions"));
        Assert.Equal(KokomiPotions.Types.Select(t => $"ModelDb.Potion<{t.Name}>").ToArray(),
                     pool.Where(c => c.StartsWith("ModelDb.Potion<")).ToArray());
        var potions = (KokomiPotionPool)RuntimeHelpers.GetUninitializedObject(typeof(KokomiPotionPool));
        SetField(potions, "_allPotions", KokomiPotions.Types.Select(t => Canon<PotionModel>(t)).ToList());
        Assert.Equal(KokomiPotions.Types, potions.GetUnlockedPotions(null!).Select(p => p.GetType()));
    }

    // ==== the relics =========================================================

    [Fact]
    public void Sango_pearl_refunds_the_first_planned_card_once_a_combat()
    {
        // The latch: the first claim in a combat wins, the rest lose.
        var kokomi = Seat.Kokomi().Creature;
        var ledger = KokomiOverhaulLedger.For(kokomi);
        Assert.True(ledger.ClaimOncePerCombat(SangoPearl.Latch));
        Assert.False(ledger.ClaimOncePerCombat(SangoPearl.Latch));
        // A new round does not reopen it (the per-turn latch would).
        ledger.RollTo(5);
        Assert.False(ledger.ClaimOncePerCombat(SangoPearl.Latch));

        // "Plan" is a play on the Bake-Kurage; the refund is what was paid.
        var claims = Il.CallSequence(Il.Method("SangoPearl", "Claims")).ToList();
        Assert.Contains("KokomiPlan.PlayedOnPet", claims);
        Assert.Contains("KokomiOverhaulLedger.ClaimOncePerCombat", claims);
        Assert.True(claims.IndexOf("KokomiPlan.PlayedOnPet")
                    < claims.IndexOf("KokomiOverhaulLedger.ClaimOncePerCombat"));
        Assert.Contains("PlayerCmd.GainEnergy",
                        Il.Calls(Il.Method("SangoPearl", "AfterCardPlayed")));
    }

    [Fact]
    public void Resistance_armband_pays_four_block_a_copy_once_a_turn_and_only_her()
    {
        var kokomi = Seat.Kokomi();
        Assert.Equal(0, ResistanceArmband.BlockFor(kokomi.Creature));
        kokomi.WithRelic<ResistanceArmband>();
        Assert.Equal(4, ResistanceArmband.BlockFor(kokomi.Creature));
        kokomi.WithRelic<ResistanceArmband>();
        Assert.Equal(8, ResistanceArmband.BlockFor(kokomi.Creature));
        var klee = Seat.Klee().WithRelic<ResistanceArmband>();
        Assert.Equal(0, ResistanceArmband.BlockFor(klee.Creature));

        // A Companion of hers counts; a non-Companion does not.
        var companion = Owned(new ProtoMiAyakaSoumetsu(), kokomi);
        var strike = Owned(new MegaCrit.Sts2.Core.Models.Cards.StrikeSilent(), kokomi);
        Assert.True(ResistanceArmband.Counts(Play(companion, kokomi), kokomi.Creature));
        Assert.False(ResistanceArmband.Counts(Play(strike, kokomi), kokomi.Creature));
        Assert.False(ResistanceArmband.Counts(Play(companion, kokomi), klee.Creature));

        // Once a turn: the shared latch, cleared by the next round.
        var ledger = KokomiOverhaulLedger.For(kokomi.Creature);
        Assert.True(ledger.Claim(ResistanceArmband.Latch));
        Assert.False(ledger.Claim(ResistanceArmband.Latch));
        ledger.RollTo(7);
        Assert.True(ledger.Claim(ResistanceArmband.Latch));
        var hook = Il.CallSequence(Il.Method("ResistanceArmband", "AfterCardPlayed")).ToList();
        Assert.Contains("KokomiOverhaulLedger.ClaimOncePerTurn", hook);
        Assert.Contains("CreatureCmd.GainBlock", hook);
    }

    [Fact]
    public void Electro_sigil_applies_electro_to_every_enemy_on_her_first_turn()
    {
        var calls = Il.CallSequence(Il.Method("ElectroSigil", "AfterPlayerTurnStart")).ToList();
        Assert.Contains("KokomiArmRelics.FirstTurnOf", calls);
        Assert.Contains("ElementalHit.ApplyOnly", calls);

        var kokomi = Seat.Kokomi().WithCombatState();
        var sigil = kokomi.OwnRelic<ElectroSigil>();
        Assert.True(KokomiArmRelics.FirstTurnOf(sigil, kokomi.Player));
        kokomi.Player.PlayerCombatState!.IncrementTurnNumber();
        Assert.False(KokomiArmRelics.FirstTurnOf(sigil, kokomi.Player));
        // Held by anyone else it does nothing.
        var klee = Seat.Klee().WithCombatState();
        Assert.False(KokomiArmRelics.FirstTurnOf(klee.OwnRelic<ElectroSigil>(), klee.Player));
    }

    [Fact]
    public void Everlasting_moonglow_returns_the_first_carry_out_from_draw_or_discard()
    {
        // Wired at the one place a Plan is carried out, after its payoffs.
        var entry = Il.CallSequence(Il.Method("KokomiPlan", "ResolveEntry")).ToList();
        Assert.True(entry.IndexOf("KokomiRefounding.OnCarriedOut")
                    < entry.IndexOf("KokomiArmRelics.AfterPlanCarriedOut"));
        var ret = Il.CallSequence(Il.Method("EverlastingMoonglow", "Return")).ToList();
        Assert.True(ret.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn")
                    < ret.IndexOf("EverlastingMoonglow.Returnable"));
        Assert.Contains("CardPileCmd.Add", ret);
        // A card in no pile (exhausted cards are in the Exhaust Pile; this
        // one is nowhere) is not returned.
        Assert.False(EverlastingMoonglow.Returnable(null));
        Assert.False(EverlastingMoonglow.Returnable(new MegaCrit.Sts2.Core.Models.Cards.StrikeSilent()));
    }

    [Fact]
    public void Ocean_hued_clam_mends_one_a_copy_per_reaction_through_the_funnel()
    {
        var kokomi = Seat.Kokomi();
        Assert.Equal(0, OceanHuedClam.MendFor(kokomi.Creature));
        kokomi.WithRelic<OceanHuedClam>();
        Assert.Equal(1, OceanHuedClam.MendFor(kokomi.Creature));
        Assert.Equal(0, OceanHuedClam.MendFor(Seat.Klee().WithRelic<OceanHuedClam>().Creature));
        // From the one reaction funnel, and through Mend's capped door.
        Assert.Contains("KokomiArmRelics.OnReaction",
                        Il.Calls(Il.Method("KokomiRefounding", "OnReaction")));
        Assert.Contains("KokomiRules.Mend", Il.Calls(Il.Method("OceanHuedClam", "Mend")));
    }

    [Fact]
    public void Kurage_lantern_takes_ethereal_off_stings_and_wards_made_while_held()
    {
        var kokomi = Seat.Kokomi();
        var before = Loose(new ProtoKkSting());
        KurageLantern.Steady(kokomi.Creature, before);
        Assert.Contains(CardKeyword.Ethereal, before.Keywords);

        kokomi.WithRelic<KurageLantern>();
        foreach (var card in new CardModel[] { Loose(new ProtoKkSting()),
                                               Loose(new ProtoKkWard()) })
        {
            KurageLantern.Steady(kokomi.Creature, card);
            Assert.DoesNotContain(CardKeyword.Ethereal, card.Keywords);
            Assert.Contains(CardKeyword.Exhaust, card.Keywords);
        }
        // Read where every Sting and Ward is made, before it reaches the hand.
        var add = Il.CallSequence(Il.Method("KokomiCards", "AddJellyfish")).ToList();
        Assert.True(add.IndexOf("KurageLantern.Steady")
                    < add.IndexOf("CardPileCmd.AddGeneratedCardToCombat"));
        // Anyone else's Stings keep it.
        var klee = Seat.Klee().WithRelic<KurageLantern>();
        var theirs = Loose(new ProtoKkSting());
        KurageLantern.Steady(klee.Creature, theirs);
        Assert.Contains(CardKeyword.Ethereal, theirs.Keywords);
    }

    [Fact]
    public void Resistance_muster_roll_offers_three_of_any_rarity_free_this_turn()
    {
        var hook = Il.CallSequence(Il.Method("ResistanceMusterRoll", "AfterPlayerTurnStart")).ToList();
        Assert.Contains("KokomiArmRelics.FirstTurnOf", hook);
        Assert.Contains("ResistanceMusterRoll.Roster", hook);
        Assert.Contains("CardSelectCmd.FromChooseACardScreen", hook);
        Assert.Contains("CardEnergyCost.SetThisTurn", hook);
        // The face names no Ethereal: the pick is not made a generated
        // Companion (Ethereal and Exhaust).
        Assert.DoesNotContain("KokomiCompanionPlan.Generate", hook);
        Assert.Equal(3, KokomiCompanionPlan.GeneralsOffered);
        // Every rarity.
        var roster = Il.CallSequence(Il.Method("ResistanceMusterRoll", "Roster"));
        Assert.Contains("KokomiCompanionPlan.Generated", Il.Calls(Il.Method("ResistanceMusterRoll", "Roster"))
            .Concat(roster));
    }

    // ==== the potions ========================================================

    [Fact]
    public void Bottled_shoal_adds_three_stings_through_the_jellyfish_door()
    {
        Assert.Equal(3, BottledShoal.Stings);
        Assert.Contains("KokomiCards.AddJellyfish", Il.Calls(Il.Method("BottledShoal", "OnUse")));
    }

    [Fact]
    public void Bottled_tide_carries_out_each_waiting_plan_through_change_of_plans_door()
    {
        Assert.Contains("KokomiPlan.ResolveEveryNow", Il.Calls(Il.Method("BottledTide", "OnUse")));
        var every = Il.CallSequence(Il.Method("KokomiPlan", "ResolveEveryNow")).ToList();
        Assert.True(every.IndexOf("KokomiPlan.Pending")
                    < every.IndexOf("KokomiPlan.ResolveFront"));
        // An empty queue is a no-op (nothing waiting, nothing carried out).
        Assert.Empty(KokomiPlan.Pending(Seat.Kokomi().Player));
    }

    [Fact]
    public void A_stunning_stratagem_doubles_every_plan_on_the_next_turn_only()
    {
        var power = Canon<StunningStratagemPower>(typeof(StunningStratagemPower));
        power.Arm(3);
        Assert.False(power.LiveIn(3));
        Assert.True(power.LiveIn(4));
        Assert.False(power.LiveIn(5));
        // It stays through the turn it was drunk on and leaves after the next.
        Assert.True(power.OwedAfter(3));
        Assert.False(power.OwedAfter(4));
        // Read by both doors: the morning drain (every entry) and Change of
        // Plans / Bottled Tide.
        Assert.Contains("KokomiPlan.StratagemTimes", Il.Calls(Il.Method("KokomiPlan", "Drain")));
        Assert.Contains("KokomiPlan.StratagemTimes", Il.Calls(Il.Method("KokomiPlan", "ResolveFront")));
        var use = Il.CallSequence(Il.Method("AStunningStratagem", "OnUse")).ToList();
        Assert.True(use.IndexOf("PowerCmd.Apply") < use.IndexOf("AStunningStratagem.Arm"));
        // Off a seat with no power, once.
        Assert.Equal(1, KokomiPlan.StratagemTimes(Seat.Kokomi().Creature));
    }

    // ==== helpers ============================================================

    private static string Plain(string face) =>
        System.Text.RegularExpressions.Regex.Replace(face, @"\[/?\w+\]", "");

    private static T Canon<T>(Type type) where T : class =>
        (T)RuntimeHelpers.GetUninitializedObject(type);

    private static IEnumerable<Type> Silent() => new[]
    {
        typeof(SilentRelics.NinjaScroll), typeof(SilentRelics.PaperKrane),
        typeof(SilentRelics.RingOfTheSnake), typeof(SilentRelics.TwistedFunnel),
    };

    /// <summary>A mutable card in no player's piles: its keyword list reads
    /// without a combat (an owned one walks piles a headless seat lacks).
    /// </summary>
    private static T Loose<T>(T card) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    private static T Owned<T>(T card, Seat owner) where T : CardModel
    {
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", owner.Player);
        return card;
    }

    private static CardPlay Play(CardModel card, Seat by) => new()
    {
        Card = card,
        Player = by.Player,
        Target = null,
        ResultPile = PileType.Discard,
        Resources = default,
        IsAutoPlay = false,
        PlayIndex = 0,
        PlayCount = 1,
    };

    private static void SetField(object target, string field, object value)
    {
        for (var t = target.GetType(); t != null; t = t.BaseType)
        {
            var f = t.GetField(field, HeadlessGame.All);
            if (f == null) continue;
            f.SetValue(target, value);
            return;
        }
        throw new InvalidOperationException($"{field} is gone");
    }
}
