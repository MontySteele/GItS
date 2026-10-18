using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// The kit display pass (2026-10-18): one pin per BACKLOG line fixed under
/// "Kits and display". Display only; no number or rule moves.
/// </summary>
public class KitDisplayPassTests
{
    // ---- Klee faces: the Bomb number folds Hardened Shell's cap ------------

    /// <summary>A Hardened Shell whose allowance has <paramref name="taken"/>
    /// spent this turn. The harness allocates powers uninitialized, so the
    /// shell's private turn total is built the way the game builds it
    /// (<c>InitInternalData</c>) and then written.</summary>
    private static Seat ShellBody(int allowance, int taken)
    {
        var body = Seat.Klee(60).WithPower<HardenedShellPower>(allowance);
        var shell = body.Creature.Powers.OfType<HardenedShellPower>().Single();
        const BindingFlags all = BindingFlags.Instance | BindingFlags.Public
                                 | BindingFlags.NonPublic;
        var data = typeof(HardenedShellPower)
            .GetMethod("InitInternalData", all)!.Invoke(shell, null)!;
        data.GetType().GetField("damageReceivedThisTurn", all)!
            .SetValue(data, (decimal)taken);
        typeof(PowerModel).GetField("_internalData", all)!.SetValue(shell, data);
        return body;
    }

    [Fact]
    public void A_set_off_into_a_hardened_shell_prints_no_more_than_it_admits()
    {
        var klee = Seat.Klee();
        var fresh = ProtoBombs.Place(ShellBody(5, 0).Creature, klee.Creature,
            new ProtoBombs.Charge(9));
        Assert.Equal(5, fresh.PredictedSetOffDamage());
        Assert.Equal(5, fresh.DisplayAmount);

        // The allowance is one total for the turn: what is left is the cap.
        var spent = ProtoBombs.Place(ShellBody(5, 3).Creature, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(4));
        Assert.Equal(2, spent.PredictedSetOffDamage());

        // Under the allowance the number is untouched.
        var under = ProtoBombs.Place(ShellBody(20, 0).Creature, klee.Creature,
            new ProtoBombs.Charge(9));
        Assert.Equal(9, under.PredictedSetOffDamage());
    }

    [Fact]
    public void A_body_with_no_shell_is_not_capped()
    {
        var klee = Seat.Klee();
        var bare = ProtoBombs.Place(Seat.Klee(60).Creature, klee.Creature,
            new ProtoBombs.Charge(9));
        Assert.Equal(9, bare.PredictedSetOffDamage());
        Assert.Equal(17, ProtoBombPower.ShellCapped(Seat.Klee(60).Creature, 17));
    }

    // ---- The Big One: "(Bombs: N damage)" reads the live preview -----------

    [Fact]
    public void The_big_ones_bombs_line_reads_the_preview_not_the_base_value()
    {
        // A bare `{SetOffBombs}` formats from BaseValue (0); `:diff()` reads
        // the PreviewValue `SetOffBombsVar.UpdateCardPreview` writes.
        var face = new ProtoKoTheBigOne().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("{SetOffBombs:diff()}", face);
        Assert.DoesNotContain("{SetOffBombs}", face);
    }

    // ---- Mika: the discount says it is Energy -----------------------------

    [Fact]
    public void Mikas_discount_prints_the_energy_icon_on_card_and_badge()
    {
        var card = new ProtoMcMikaStarfrostSwirl().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("costs {energyPrefix:energyIcons(1)} less", card);
        var badge = ((BaseLib.Abstracts.ILocalizationProvider)
                new StarfrostDiscountPower())
            .Localization!.First(r => r.Item1 == "description").Item2;
        Assert.Contains("costs {Amount:energyIcons()} less", badge);
    }

    // ---- Chain Fuse: the face names Mines ---------------------------------

    [Fact]
    public void Chain_fuse_says_it_grows_mines()
    {
        var face = new ProtoKoChainFuse().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("[gold]Bomb[/gold] and [gold]Mine[/gold]", face);
    }

    // ---- Varka's screen: an Artifact eats a reaction's debuff -------------

    // `ReactionEffects` is internal to the mod, so its three reads are
    // reached by name (no `InternalsVisibleTo` in this mod).
    private static object? Effects(string method, params object?[] args) =>
        typeof(KleeCardTooltips).Assembly
            .GetType("KleeMod.Powers.ReactionEffects", throwOnError: true)!
            .GetMethod(method, BindingFlags.Public | BindingFlags.Static)!
            .Invoke(null, args);

    private static string? Debuff(Reaction r) =>
        (string?)Effects("ArtifactBlockedDebuff", r);

    private static bool Blocks(Reaction r, MegaCrit.Sts2.Core.Entities.Creatures.Creature c) =>
        (bool)Effects("ArtifactWillBlock", r, c)!;

    [Fact]
    public void The_debuffing_reactions_name_what_an_artifact_blocks()
    {
        Assert.Equal("Weak", Debuff(Reaction.Overload));
        Assert.Equal("Vulnerable",
            Debuff(Reaction.Superconduct));
        Assert.Equal("Poison",
            Debuff(Reaction.ElectroCharged));
        foreach (var none in new[] { Reaction.Vaporize, Reaction.Melt,
                     Reaction.Swirl, Reaction.Crystallize, Reaction.Frozen })
        {
            Assert.Null(Debuff(none));
        }
    }

    [Fact]
    public void Only_a_body_holding_artifact_blocks_and_frozen_still_counts()
    {
        var shielded = Seat.Klee(30).WithPower<ArtifactPower>(1).Creature;
        var bare = Seat.Klee(30).Creature;
        Assert.True(Blocks(Reaction.Overload, shielded));
        Assert.True(Blocks(Reaction.ElectroCharged, shielded));
        Assert.True(Blocks(Reaction.Frozen, shielded));
        Assert.False(Blocks(Reaction.Vaporize, shielded));
        Assert.False(Blocks(Reaction.Overload, bare));
    }

    [Fact]
    public void The_blocked_sentence_names_the_debuff_and_the_enemy()
    {
        Assert.Equal(
            "But its [gold]Artifact[/gold] blocks the [gold]Weak[/gold].",
            KleeCardTooltips.DebuffArtifactSentence("Weak"));
        Assert.Equal(
            "But Cubex's [gold]Artifact[/gold] blocks the [gold]Poison[/gold].",
            KleeCardTooltips.DebuffArtifactSentence("Poison", "Cubex"));
        Assert.Equal("Its Artifact blocked the Vulnerable.",
            (string)Effects("DebuffBlockedByArtifact", "Vulnerable")!);
    }
}
