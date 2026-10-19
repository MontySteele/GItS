#nullable enable

using System;
using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Furina;
using KleeMod.Cards.Kokomi;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE ANCIENT AUDIT (review/ruled/ancient-audit-2026-10-12.md, ruled
/// 2026-10-12: "Otherwise agreed.- let's fix them all"). Every kit has one
/// Dusty Tome card and one Archaic Tooth card, Varka's pattern
/// (<c>VarkaAncientsTests</c>): Jumpy Dumpty becomes Mk.Omega, Kurage's Oath
/// becomes Princess of Watatsumi, Rising Applause becomes All the World's a
/// Stage. Also the Watatsumi Casket's per-Plan Block, Center of Attention's
/// and Alice's Masterpiece's faces, and the Dodoco Tales one-payment check.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class AncientAuditTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object?>());
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!.First(r => r.Item1 == "description").Item2;

    /// <summary>The type argument of every <c>ModelDb.Card&lt;T&gt;()</c> call
    /// in the body, read off its IL (<c>VarkaAncientsTests</c>' scan).</summary>
    private static List<Type> CardTypesCalled(System.Reflection.MethodBase method)
    {
        var found = new List<Type>();
        var il = method.GetMethodBody()?.GetILAsByteArray() ?? Array.Empty<byte>();
        for (var i = 0; i < il.Length - 4; i++)
        {
            if (il[i] != 0x28) continue; // call
            try
            {
                var target = method.Module.ResolveMethod(BitConverter.ToInt32(il, i + 1));
                if (target is { IsGenericMethod: true, Name: "Card" })
                {
                    found.AddRange(target.GetGenericArguments());
                }
            }
            catch
            {
                // Not a method token.
            }
        }
        return found;
    }

    private static void AssertTooth<TStarter>(Type ancient) where TStarter : CardModel, new()
    {
        Assert.IsAssignableFrom<ITranscendenceCard>(new TStarter());
        var made = Il.Method(typeof(TStarter).Name, "GetTranscendenceTransformedCard");
        Assert.Contains(ancient, CardTypesCalled(made));
    }

    // ==== the doors ===========================================================

    [Fact]
    public void The_archaic_tooth_turns_each_starter_into_its_ancient()
    {
        AssertTooth<ProtoKoJumpyDumpty>(typeof(JumpyDumptyMkOmega));
        AssertTooth<ProtoKkKuragesOath>(typeof(PrincessOfWatatsumi));
        AssertTooth<ProtoFsStandingOvation>(typeof(AllTheWorldsAStage));
    }

    [Theory]
    [InlineData("Klee", "JumpyDumptyMkOmega", "AlicesMasterpiece")]
    [InlineData("Kokomi", "PrincessOfWatatsumi", "DivineStrategy")]
    [InlineData("Furina", "AllTheWorldsAStage", "CenterOfAttention")]
    public void Each_kit_lists_its_tooth_card_then_its_tome_card(
        string kit, string tooth, string tome)
    {
        var ledger = Il.CallSequence(
                typeof(RosterAncientCards).GetProperty(kit)!.GetGetMethod()!)
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(new[] { $"ModelDb.Card<{tooth}>", $"ModelDb.Card<{tome}>" },
                     ledger);
    }

    // ==== Klee ================================================================

    [Fact]
    public void Mk_omega_is_innate_and_its_text_is_unchanged()
    {
        var card = new JumpyDumptyMkOmega();
        Assert.Contains(CardKeyword.Innate, card.CanonicalKeywords);
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(2, card.EnergyCost.Canonical);
        Assert.Equal(
            "Deal {Damage:diff()} [gold]Pyro[/gold] damage to a random enemy 3 "
          + "times. Place a [gold]Bomb[/gold] {BombDamage:diff()} on ALL enemies.",
            Face(card));
    }

    [Fact]
    public void Alices_masterpiece_says_bombs_and_mines()
    {
        const string face =
            "Whenever one of your [gold]Bombs[/gold] or [gold]Mines[/gold] goes off, "
          + "it stays on the enemy at half its size, rounded down.";
        Assert.Equal(face, Face(new AlicesMasterpiece()));
        Assert.Equal(face, new AlicesMasterpiecePower().Localization!
            .First(r => r.Item1 == "description").Item2);
    }

    // ==== Kokomi ==============================================================

    [Fact]
    public void Princess_is_a_two_line_plan_skill_like_kurages_oath()
    {
        var card = new PrincessOfWatatsumi();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(KokomiTargets.PetOrSelf, card.TargetType);
        Assert.IsAssignableFrom<IPlannedCard>(card);
        Assert.IsAssignableFrom<INowLineCard>(card);
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold]. Draw 2 cards.\n"
          + "Or [gold]plan[/gold]: Deal {PlanDamage:diff()} [gold]Hydro[/gold] "
          + "damage to ALL enemies 5 times.",
            Face(card));

        Assert.Equal(9m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(2m, card.DynamicVars.Cards.BaseValue);
        var clause = Assert.Single(card.PlanClauses);
        Assert.Equal(KokomiPlan.Kind.Damage, clause.Kind);
        Assert.Equal(KokomiPlan.Aim.AllEnemies, clause.Aim);
        Assert.Equal(3, clause.Amount);
        Assert.Equal(5, clause.Times);

        var up = Upgraded<PrincessOfWatatsumi>();
        Assert.Equal(12m, up.DynamicVars.Block.BaseValue);
        Assert.Equal(5, Assert.Single(up.PlanClauses).Amount);
    }

    [Fact]
    public void Princess_schedules_on_the_jellyfish_and_otherwise_blocks_and_draws()
    {
        var play = Il.CallSequence(Il.Method("PrincessOfWatatsumi", "OnPlay")).ToList();
        Assert.Contains("KokomiPlan.PlayedOnPet", play);
        Assert.Contains("KokomiPlan.Schedule", play);
        var now = Il.CallSequence(Il.Method("PrincessOfWatatsumi", "PlayNowLine")).ToList();
        var block = now.IndexOf("CreatureCmd.GainBlock");
        var draw = now.IndexOf("CardPileCmd.Draw");
        Assert.True(block >= 0 && draw > block);
    }

    [Fact]
    public void Princess_power_and_its_plan_bus_listener_are_gone()
    {
        var types = typeof(RosterAncientCards).Assembly.GetTypes();
        Assert.DoesNotContain(types, t => t.Name == "PrincessOfWatatsumiPlanPower");
        Assert.DoesNotContain(types, t => t.Name == "StageRaisePerTurnPower");
    }

    [Fact]
    public void The_watatsumi_casket_pays_more_from_the_same_hook()
    {
        // Ward and Casket (2026-10-18): 2 Block a play, the starter's 1.
        Assert.Contains("TamakushiCasket.get_Block",
            Il.Calls(Il.Method("TamakushiCasket", "AfterCardPlayed")));
        Assert.Equal(2, new WatatsumiCasket().Block);
        Assert.Equal(1, new TamakushiCasket().Block);
    }

    // ==== Furina ==============================================================

    [Fact]
    public void All_the_worlds_a_stage_is_a_bigger_rising_applause()
    {
        var card = new AllTheWorldsAStage();
        Assert.Equal(CardRarity.Ancient, card.Rarity);
        Assert.Equal(CardType.Skill, card.Type);
        Assert.Equal(1, card.EnergyCost.Canonical);
        Assert.Equal(TargetType.AllEnemies, card.TargetType);
        Assert.IsAssignableFrom<IStageSpendCard>(card);
        Assert.Equal(
            "Gain {Block:diff()} [gold]Block[/gold]. [gold]Spend[/gold] all your "
          + "[gold]Fanfare[/gold] and deal that much [gold]Hydro[/gold] damage to "
          + "ALL enemies twice.{InCombat:\n(Deals {CalculatedDamage:diff()} damage)|}",
            Face(card));
        Assert.Equal(8m, card.DynamicVars.Block.BaseValue);
        Assert.Equal(11m, Upgraded<AllTheWorldsAStage>().DynamicVars.Block.BaseValue);

        // Rising Applause's spend-all, then two hits of what it spent.
        var play = Il.CallSequence(Il.Method("AllTheWorldsAStage", "OnPlay")).ToList();
        var spend = play.IndexOf("FurinaStage.SpendAll");
        var hits = play.FindIndex(c => c.Contains("WithHitCount"));
        Assert.True(spend >= 0 && hits > spend);
        Assert.Contains(play, c => c.Contains("TargetingAllOpponents"));
    }

    [Fact]
    public void Center_of_attention_names_what_it_covers_and_spend_all_is_never_free()
    {
        const string face =
            "The first [gold]Spend[/gold] N or [gold]Spend[/gold] up to N each "
          + "turn takes no [gold]Fanfare[/gold].";
        Assert.Equal(face, Face(new CenterOfAttention()));
        Assert.Equal(face, new CenterOfAttentionPower().Localization!
            .First(r => r.Item1 == "description").Item2);
        Assert.DoesNotContain("CenterOfAttentionPower.TryClaim",
            Il.Calls(Il.Method("FurinaStage", "SpendAll")));
        Assert.Contains("CenterOfAttentionPower.TryClaim",
            Il.Calls(Il.Method("FurinaStage", "Spend")));
        // furina-next paper 2 (2026-10-16): the card verb adds Extended Run
        // to its cap, then pays through the one "Spend up to" path.
        Assert.Contains("FurinaStage.SpendUpToCap",
            Il.Calls(Il.Method("FurinaStage", "SpendUpTo")));
        Assert.Contains("CenterOfAttentionPower.TryClaim",
            Il.Calls(Il.Method("FurinaStage", "SpendUpToCap")));
    }

    // ==== Dodoco Tales: one payment per explosion =============================

    [Fact]
    public void Dodoco_tales_hears_one_bus_per_explosion()
    {
        // It listens on the shipped detonation bus and on the arm's explosion
        // bus. Only the shipped BombPower rings the first, and nothing places
        // one: no method outside BombPower calls its placers or detonators.
        var shipped = new HashSet<string>(StringComparer.Ordinal)
        {
            "BombPower.Place", "BombPower.DetonateOn", "BombPower.DetonateAll",
            "BombPower.MoveAllTo", "BombPower.ResolveTurnStartPiles",
        };
        var callers = new List<string>();
        foreach (var type in typeof(RosterAncientCards).Assembly.GetTypes())
        {
            if (type == typeof(BombPower) || type.DeclaringType == typeof(BombPower))
            {
                continue;
            }
            foreach (var method in type.GetMethods(HeadlessGame.All)
                         .Where(m => m.DeclaringType == type))
            {
                IReadOnlyCollection<string> calls;
                try
                {
                    calls = Il.Calls(method);
                }
                catch (Exception)
                {
                    continue;
                }
                if (calls.Any(shipped.Contains))
                {
                    callers.Add(type.Name + "." + method.Name);
                }
            }
        }
        Assert.Empty(callers);

        // And the arm's explosion bus rings the arm's listeners alone.
        var bus = Il.Calls(Il.Method("ProtoBombPower", "NotifyExplosionListeners"));
        Assert.Contains("IProtoExplosionListener.OnBombExploded", bus);
        Assert.DoesNotContain("IBombDetonationListener.OnBombDetonated", bus);
    }
}
