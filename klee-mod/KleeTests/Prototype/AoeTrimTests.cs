using System;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE AoE TRIM (2026-10-03, <c>review/active/aoe-trim-2026-10-03.md</c>,
/// all picks ruled): Klee's seven, Furina's two, Durin split in two and
/// Yoimiya's Aurous Blaze. The cards are generated; these pin the hand-written
/// rules they call. What awaits a command is pinned off the compiled methods.
/// Sim twin: <c>tier0/tests/test_aoe_trim.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class AoeTrimTests
{
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, Array.Empty<object>());
        return card;
    }

    private static T Owned<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    // ---- Klee ----------------------------------------------------------

    // Mine, All Mine!'s mines-only Set off (`SetOffMinesAimed`) left in the
    // Klee finish-line batch (2026-10-03); its new body is pinned in
    // KleeFinishBatchTests.

    [Fact]
    public void Nobody_holds_a_charge_without_a_combat()
    {
        Assert.Equal(0, ProtoBombPower.EnemiesHoldingChargeFrom(null));
        Assert.Equal(0, ProtoBombPower.EnemiesHoldingChargeFrom(Seat.Klee().Creature));
    }

    [Fact]
    public void Mine_toss_and_red_knight_are_single_target()
    {
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoMineToss().TargetType);
        Assert.Equal(7m, new ProtoKoMineToss().DynamicVars["BombSize"].BaseValue);
        Assert.Equal(TargetType.AnyEnemy, new ProtoKoRedKnight().TargetType);
        Assert.DoesNotContain(Il.Calls(Il.Method("ProtoKoMineToss", "OnPlay")),
                              c => c.Contains("PlaceOnAll"));
    }

    // ---- Durin ---------------------------------------------------------

    [Fact]
    public void Principle_of_purity_prints_and_upgrades_all_three_numbers()
    {
        var face = Face(new ProtoMcDurinPrincipleOfPurity());
        Assert.Contains("{PowerAmount:diff()}", face);
        Assert.Contains("{IfUpgraded:show:75|50}%", face);
        Assert.Contains("{IfUpgraded:show:6|4} additional damage", face);
        Assert.Equal(6m, Upgraded<ProtoMcDurinPrincipleOfPurity>()
            .DynamicVars["PowerAmount"].BaseValue);
        var play = Il.Calls(Il.Method("ProtoMcDurinPrincipleOfPurity", "OnPlay"));
        Assert.Contains(play, c => c.Contains("get_IsUpgraded"));
    }

    [Fact]
    public void Binary_form_swaps_each_modes_number_on_the_face()
    {
        var face = Face(new ProtoMcDurinBinaryForm());
        Assert.Contains("{IfUpgraded:show:8|6}", face);
        Assert.Contains("{IfUpgraded:show:5|4}", face);
    }

    [Fact]
    public void The_turn_start_hit_is_a_pyro_hit_of_its_owner()
    {
        Assert.Contains("ElementalHit.Deal",
                        Il.Calls(Il.Method("PurityStrikePower", "AfterPlayerTurnStart")));
    }

    [Fact]
    public void White_is_percentage_points_added_to_the_reaction_factor()
    {
        var seat = Seat.Klee().WithPower<PurityWhitePower>(50);
        Assert.Equal(1.5m, CompanionOverhaulReactions.DamageMultiplier(seat.Creature));
        Assert.Equal(50, PurityWhitePower.TeamPercent(seat.Creature));
        Assert.Equal(1m, CompanionOverhaulReactions.DamageMultiplier(Seat.Klee().Creature));
        // TEAM-WIDE: the multiplier asks every player's White, not the dealer's.
        Assert.Contains("PurityWhitePower.TeamPercent",
                        Il.Calls(Il.Method("CompanionOverhaulReactions", "DamageMultiplier")));
        Assert.Contains(Il.Calls(Il.Method("PurityWhitePower", "TeamPercent")),
                        c => c.Contains("PlayerCreatures"));
    }

    [Fact]
    public void Dark_adds_to_pyro_only_and_rides_the_elemental_door()
    {
        var seat = Seat.Klee().WithPower<PurityDarkPower>(4);
        Assert.Equal(4, PurityDarkPower.BonusFor(seat.Creature, Element.Pyro));
        Assert.Equal(0, PurityDarkPower.BonusFor(seat.Creature, Element.Hydro));
        Assert.Equal(0, PurityDarkPower.BonusFor(null, Element.Pyro));
        // Bombs, Mines and companion volleys all leave through ElementalHit.
        Assert.Contains("PurityDarkPower.BonusFor",
                        Il.Calls(Il.Method("ElementalHit", "Deal")));
        Assert.Contains("PurityDarkPower.BonusFor",
                        Il.Calls(Il.Method("ElementalHit", "DealAsIfAura")));
    }

    // ---- Yoimiya -------------------------------------------------------

    [Fact]
    public void Aurous_blaze_answers_its_markers_skills_and_not_its_own_play()
    {
        var seat = Seat.Klee();
        var skill = Owned<ProtoKoMineToss>(seat);          // a Skill
        Assert.True(AurousBlazePower.Answers(skill, seat.Creature));
        Assert.False(AurousBlazePower.Answers(Owned<ProtoKoRedKnight>(seat),
                                              seat.Creature));
        Assert.False(AurousBlazePower.Answers(
            Owned<ProtoMiYoimiyaAurousBlaze>(seat), seat.Creature));
        Assert.False(AurousBlazePower.Answers(skill, Seat.Klee().Creature));
        Assert.Contains("ElementalHit.Deal",
                        Il.Calls(Il.Method("AurousBlazePower", "AfterCardPlayed")));
    }

    [Fact]
    public void Aurous_blaze_takes_the_cards_printed_three()
    {
        var power = new AurousBlazePower();
        Assert.Contains(power.GetType().GetInterfaces(), i => i.Name == "ISummonDamagePower");
        var play = Il.Calls(Il.Method("ProtoMiYoimiyaAurousBlaze", "OnPlay"));
        Assert.Contains(play, c => c.StartsWith("DamageCmd.Attack"));
        Assert.Contains(play, c => c.Contains("SummonDamage.Note"));
        Assert.Contains("whenever you play a Skill",
                        Face(new ProtoMiYoimiyaAurousBlaze()));
    }
}
