using System;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA RULES PASS (2026-10-01,
/// review/active/furina-rules-pass-2026-10-01.md, all picks ruled).
///
///   * Rule 8: a Spend pays from the back performer first, then forward, and
///     is refused only when the whole stage holds less. Palais Ledger is
///     re-aimed to "Your Spends cost 1 less Fanfare"; Center of Attention
///     drops its short-bar clause.
///   * Rule 5: only a card or potion you play summons on an empty stage; a
///     Power's, a relic's, a Bow reader's or a reaction's gain does nothing
///     there, and "each performer" has nobody to land on.
///   * Rule 4 cut: the front regains nothing; The Curtain Never Falls' 2 is
///     the only regain.
///   * Wriothesley: "Always your front performer."
///   * Sec.3: the twelve old-kit rows, ported.
///
/// Sim twin: <c>tier0/tests/test_furina_rules_pass.py</c>. NOTHING MEASURED
/// HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaRulesPassTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm()
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = true;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    private static (Seat Seat, FurinaStageLedger Stage) Stage(
        params (StagePerformer Who, int Fanfare)[] seats)
    {
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        foreach (var (who, fanfare) in seats)
        {
            stage.Summon(who);
            stage.Raise(fanfare - FurinaStageLaw.SummonFanfare);
        }
        return (seat, stage);
    }

    private static string Face(CardModel card) =>
        ((BaseLib.Abstracts.ILocalizationProvider)card).Localization!
            .Single(l => l.Item1 == "description").Item2;

    private static string RepoFile(string relativePath,
                                   [CallerFilePath] string here = "")
    {
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relativePath);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relativePath);
    }

    // ---- rule 8 ------------------------------------------------------------

    [Fact]
    public void A_spend_pays_the_back_first_then_forward_and_bows_back_to_front()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 4),
                                  (StagePerformer.Chevalmarin, 2),
                                  (StagePerformer.Crabaletta, 1));
        Assert.True(FurinaStage.CanSpend(seat.Creature, 7));
        Assert.False(FurinaStage.CanSpend(seat.Creature, 8));

        var spent = stage.Spend(5);
        Assert.True(spent.Fired);
        Assert.Equal(5, spent.Paid);
        Assert.Equal(new[] { StagePerformer.Crabaletta, StagePerformer.Chevalmarin },
                     spent.Exits.Select(e => e.Who).ToArray());
        Assert.Equal(new[] { (StagePerformer.Usher, 2) },
                     stage.Seats.Select(s => (s.Who, s.Fanfare)).ToArray());
        Assert.Equal(5, stage.SpentThisPlay);
    }

    [Fact]
    public void An_empty_stage_is_never_offered_a_spend()
    {
        using var _ = new Arm();
        var (seat, _) = Stage();
        Assert.False(FurinaStage.CanSpend(seat.Creature, 0));
        Assert.False(FurinaStage.CanSpend(seat.Creature, 1));
    }

    [Fact]
    public void Center_of_attention_no_longer_bends_the_gate_and_says_so()
    {
        Assert.DoesNotContain("CenterOfAttentionPower.Covers",
                              Il.Calls(Il.Method("FurinaStage", "CanSpend")));
        var face = Face(new global::KleeMod.Cards.Furina.CenterOfAttention());
        Assert.Equal("The first [gold]Spend[/gold] you choose each turn takes "
                     + "no [gold]Fanfare[/gold].", face);
    }

    [Fact]
    public void Palais_ledgers_face_is_the_discount()
    {
        var relic = new global::KleeMod.Relics.PalaisLedger();
        var face = relic.Localization!.Single(l => l.Item1 == "description").Item2;
        Assert.Equal("Your [gold]Spend[/gold]s cost [blue]1[/blue] less "
                     + "[gold]Fanfare[/gold].", face);
    }

    // ---- rule 5 ------------------------------------------------------------

    [Fact]
    public void A_triggered_gain_does_nothing_on_an_empty_stage()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage();
        Assert.Equal(0, FurinaStage.Raise(seat.Creature, 3, played: false).Result);
        Assert.Equal(0, FurinaStage.RaiseLead(seat.Creature, 3, played: false).Result);
        Assert.Equal(0, FurinaStage.RaiseAll(seat.Creature, 3).Result);
        Assert.Empty(stage.Seats);
    }

    [Fact]
    public void Every_trigger_raises_as_unplayed()
    {
        // The Ancient's turn-start Raise, Thunderous Applause, Tide of
        // Applause, Season Tickets and the co-op powers pass `played: false`;
        // the cards and Bottled Applause take the default.
        var src = RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                        "FurinaStage.cs"))
                + RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                        "FurinaStageSupporting.cs"))
                + RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                        "StageRaisePerTurnPower.cs"))
                + RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                        "CoopSet.cs"));
        Assert.Contains("await Raise(owner, (int)applause.Amount, played: false);", src);
        Assert.Contains("await Raise(dealer, amount, played: false);", src);
        Assert.Contains("await Raise(furina, tickets, played: false);", src);
        Assert.Contains("await FurinaStage.Raise(Owner, (int)Amount, played: false);", src);
        Assert.Contains("await FurinaStage.RaiseLead(Owner, (int)Amount, played: false);", src);
        var potions = RepoFile(Path.Combine("KleeCode", "Potions", "ArmPotions.cs"));
        Assert.Contains("await FurinaStage.Raise(target, Fanfare);", potions);
    }

    // ---- rule 4 ------------------------------------------------------------

    [Fact]
    public void The_front_regains_nothing_without_the_curtain()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 3));
        Assert.Equal(0, FurinaStageLaw.LeadRegen);
        Assert.Equal(0, stage.Regen(turnNumber: 2));
        Assert.Equal(3, stage.Lead!.Fanfare);
        Assert.Empty(stage.Beats.Where(b => b.Event == "regain"));
        // The Curtain Never Falls keeps its 2.
        Assert.Equal(2, stage.Regen(2, global::KleeMod.Relics.CurtainNeverFalls.LeadRegen,
                                    firstTurn: 2));
    }

    // ---- Wriothesley ---------------------------------------------------------

    [Fact]
    public void A_summon_around_wriothesley_bows_the_one_behind_him()
    {
        using var _ = new Arm();
        var (_, stage) = Stage((StagePerformer.Usher, 2),
                               (StagePerformer.Crabaletta, 4));
        Assert.True(stage.ArriveAtFront(StagePerformer.Wriothesley, 5));
        Assert.True(stage.FrontHeld);
        Assert.Equal(1, stage.LeaverIndex);
        var leaver = stage.BowFromFront()!;
        Assert.Equal(StagePerformer.Usher, leaver.Who);
        Assert.Equal(StagePerformer.Wriothesley, stage.Lead!.Who);
    }

    // ---- sec.3: the ported rows -----------------------------------------------

    [Fact]
    public void The_twelve_are_offered_in_place_of_the_old_rows()
    {
        var offer = Il.CallSequence(Il.Method("FurinaStageRoster",
                                              "Pool")).ToList();
        foreach (var row in new[]
                 {
                     "ProtoFsOpeningNumber", "ProtoFsCommandingGaze",
                     "ProtoFsUndercurrent", "ProtoFsWarmupAct",
                     "ProtoFsLeadingLady", "ProtoFsCourtroomDrama",
                     "ProtoFsCrashingWaves", "ProtoFsDuet",
                     "ProtoFsQuickChange", "ProtoFsWitnessStand",
                     "ProtoFsSingerOfManyWaters", "ProtoFsEndlessWaltz",
                 })
        {
            Assert.Contains(offer, c => c.Contains(row));
        }
        var roster = RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                           "FurinaStageRoster.cs"));
        foreach (var old in new[]
                 {
                     "AnInvitation", "GuestList", "CommandPerformance",
                     "SingerOfManyWaters", "CommandingGaze", "Undercurrent",
                     "WarmupAct", "CourtroomDrama", "CrashingWaves", "Duet",
                     "QuickChange", "WitnessStand",
                 })
        {
            // Legacy cleanup stage 4: the pool is a list, not a swap over the
            // shipped sheet, so no shipped row is named in it at all.
            Assert.DoesNotContain($"FurinaGen.{old}", roster);
        }
    }

    [Fact]
    public void The_new_rows_print_the_papers_faces()
    {
        Assert.Equal("Your [gold]front performer[/gold] gains "
                     + "{RaiseAmount:diff()} [gold]Fanfare[/gold].",
                     Face(new ProtoFsSingerOfManyWaters()));
        Assert.Equal(CardRarity.Rare, new ProtoFsSingerOfManyWaters().Rarity);
        Assert.Equal(CardRarity.Common, new ProtoFsOpeningNumber().Rarity);
        Assert.Equal(CardRarity.Uncommon, new ProtoFsLeadingLady().Rarity);
        Assert.Equal(CardRarity.Rare, new ProtoFsEndlessWaltz().Rarity);
        Assert.Equal(CardType.Attack, new ProtoFsEndlessWaltz().Type);
        Assert.Equal(2, new ProtoFsEndlessWaltz().EnergyCost.Canonical);
        var waltz = RepoFile(Path.Combine("KleeCode", "Cards", "Prototype",
                                          "Generated", "ProtoFsEndlessWaltz.cs"));
        Assert.Contains("FurinaStage.PerformAll(choiceContext, Owner.Creature, "
                        + "minFanfare: 5);", waltz);
        var opening = RepoFile(Path.Combine("KleeCode", "Cards", "Prototype",
                                            "Generated", "ProtoFsOpeningNumber.cs"));
        Assert.Contains("FurinaStage.CardsPlayedThisTurn(Owner.Creature) == 0",
                        opening);
    }

    [Fact]
    public void Opening_numbers_count_is_the_turns_finished_cards()
    {
        using var _ = new Arm();
        var (seat, stage) = Stage((StagePerformer.Usher, 3));
        Assert.Equal(0, FurinaStage.CardsPlayedThisTurn(seat.Creature));
        FurinaStage.NoteCardPlayed(seat.Creature);
        FurinaStage.NoteCardPlayed(seat.Creature);
        Assert.Equal(2, FurinaStage.CardsPlayedThisTurn(seat.Creature));
        FurinaStage.BeginTurn(seat.Creature);
        Assert.Equal(0, FurinaStage.CardsPlayedThisTurn(seat.Creature));
        Assert.Contains("FurinaStage.NoteCardPlayed",
                        Il.Calls(Il.Method("FurinaStageHooks", "AfterCardPlayed")));
    }

    [Fact]
    public void Perform_all_reads_who_qualifies_before_any_act()
    {
        // Endless Waltz: the qualifying cast is filtered in the snapshot.
        var src = RepoFile(Path.Combine("KleeCode", "Powers", "Prototype",
                                        "FurinaStage.cs"));
        Assert.Contains("foreach (var seat in Of(owner).Where(s => s.Fanfare >= minFanfare)",
                        src);
    }
}
