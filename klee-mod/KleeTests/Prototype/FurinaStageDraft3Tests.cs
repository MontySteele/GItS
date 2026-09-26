#nullable enable

using System;
using System.Linq;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- DRAFT 3, THE RULES PASS (2026-09-25), the mod's
/// halves. [USER] ruled the Stage review: pick 1a (the Bow is the act, once
/// more), Hydro off the acts ("we may need to do the same here, removing the
/// Hydro application from the end-of-turn effects on Chevalmarin and
/// Crabaletta"), and a fade that does not punish building up ("taking away
/// half from the back means it's hard to build up fanfare"). The sim twin is
/// <c>tier0/tests/test_furina_stage.py</c>'s draft-3 block, which runs every
/// payout for real; what needs a live combat is read off IL here.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic.
/// </summary>
public class FurinaStageDraft3Tests
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

    private static FurinaStageLedger Stage(
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
        stage.ClearBeats();
        return stage;
    }

    // ---- 1. The acts carry no element -------------------------------------

    [Fact]
    public void No_act_applies_hydro()
    {
        // Both damage acts go out through the element-less door, unpowered
        // (`EB-495` D3 stands), and nothing in the act touches an aura.
        var act = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("ElementalHit.DealUnelemented", act);
        Assert.DoesNotContain("ElementalHit.Deal", act);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", act);
        var seq = Il.CallSequence(Il.Method("FurinaStage", "Act"));
        Assert.Equal(2, seq.Count(c => c == "ElementalHit.DealUnelemented"));
    }

    [Fact]
    public void The_element_less_door_keeps_its_old_callers_byte_identical()
    {
        // Spark Knight passes no `powered`, so it still takes the dealer's
        // terms; the Stage passes false.
        var door = Il.Method("ElementalHit", "DealUnelemented");
        var powered = door.GetParameters().Single(p => p.Name == "powered");
        Assert.True(powered.HasDefaultValue);
        Assert.Equal(true, powered.DefaultValue);
    }

    // ---- 2. The Bow is the act, once more ----------------------------------

    [Fact]
    public void A_bow_is_one_act_then_the_readers()
    {
        var bow = Il.CallSequence(Il.Method("FurinaStage", "Bow")).ToList();
        var act = bow.IndexOf("FurinaStage.Act");
        var after = bow.IndexOf("FurinaStage.AfterBow");
        Assert.True(act >= 0 && after > act, string.Join(", ", bow));
        Assert.Equal(1, bow.Count(c => c == "FurinaStage.Act"));
        // Ousia and Pneuma double it like any act: `Act` reads them.
        var body = Il.Calls(Il.Method("FurinaStage", "Act"));
        Assert.Contains("FurinaStageLedger.get_ActDamageMultiplier", body);
        Assert.Contains("FurinaStageLedger.get_ActBlockMultiplier", body);
        // Full House does not repeat it: only the sweep reads Full House.
        Assert.DoesNotContain("FurinaStage.FullHouseActs", bow);
        Assert.Contains("FurinaStage.FullHouseActs",
                        Il.Calls(Il.Method("FurinaStage", "EndOfTurnActs")));
        // No separate Bow effect is left: no Raise, no aura.
        Assert.DoesNotContain("FurinaStage.RaiseLead", bow);
        Assert.DoesNotContain("ElementalHit.ApplyOnly", bow);
    }

    [Fact]
    public void The_act_and_the_bow_are_filed_as_their_own_beats()
    {
        var strings = Il.Strings(Il.Method("FurinaStage", "Perform"))
            .Concat(Il.Strings(Il.Method("FurinaStage", "Bow")));
        Assert.Contains("act", strings);
        Assert.Contains("bow", strings);
    }

    // ---- 3. The applause fades ---------------------------------------------

    [Theory]
    [InlineData(1, 1)]
    [InlineData(5, 5)]
    [InlineData(6, 6)]
    [InlineData(7, 6)]
    [InlineData(9, 7)]
    [InlineData(15, 10)]
    [InlineData(25, 15)]
    public void The_fade_table(int before, int after)
    {
        Assert.Equal(after, before - FurinaStageLaw.FadeLoss(before));
    }

    [Fact]
    public void The_middle_and_back_fade_and_the_front_never_does()
    {
        using var _ = new Arm();
        var stage = Stage((StagePerformer.Usher, 25),
                          (StagePerformer.Chevalmarin, 9),
                          (StagePerformer.Crabaletta, 15));

        Assert.Equal(2 + 5, stage.Fade());

        Assert.Equal(new[] { 25, 7, 10 },
                     stage.Seats.Select(s => s.Fanfare).ToArray());
        var beats = stage.Beats.Where(b => b.Event == FurinaStageLedger.FadeEvent)
            .ToList();
        Assert.Equal(2, beats.Count);
        Assert.Equal(StagePerformer.Chevalmarin, beats[0].Who);
        Assert.Equal(2, beats[0].Moved);
        Assert.Equal(7, beats[0].Fanfare);
        Assert.Equal(StagePerformer.Crabaletta, beats[1].Who);
        Assert.Equal(5, beats[1].Moved);
        Assert.Equal(10, beats[1].Fanfare);
    }

    [Fact]
    public void A_lone_performer_is_the_front_and_does_not_fade()
    {
        using var _ = new Arm();
        var stage = Stage((StagePerformer.Crabaletta, 25));
        Assert.Equal(0, stage.Fade());
        Assert.Equal(25, stage.Lead!.Fanfare);
        Assert.Empty(stage.Beats);
    }

    [Fact]
    public void The_fade_never_empties_never_goes_below_five_and_never_bows()
    {
        using var _ = new Arm();
        var stage = Stage((StagePerformer.Usher, 1),
                          (StagePerformer.Chevalmarin, 1),
                          (StagePerformer.Crabaletta, 6));
        for (var i = 0; i < 5; i++) Assert.Equal(0, stage.Fade());
        Assert.Equal(new[] { 1, 1, 6 },
                     stage.Seats.Select(s => s.Fanfare).ToArray());
        Assert.Empty(stage.TakePendingHitBows());
        Assert.Empty(stage.Beats);
        for (var bar = 0; bar < 40; bar++)
        {
            Assert.True(bar - FurinaStageLaw.FadeLoss(bar)
                        >= Math.Min(bar, FurinaStageLaw.FadeThreshold));
        }
    }

    [Fact]
    public void The_fade_runs_after_the_acts()
    {
        var sweep = Il.CallSequence(Il.Method("FurinaStage", "EndOfTurnActs"))
            .ToList();
        var lastAct = sweep.LastIndexOf("FurinaStage.Perform");
        // 2026-09-26: the sweep fades through FurinaStage.FadeAndShow, which
        // is the ledger's fade, then the bars, then the loss numbers.
        var fade = sweep.IndexOf("FurinaStage.FadeAndShow");
        Assert.True(lastAct >= 0 && fade > lastAct, string.Join(", ", sweep));
        var shown = Il.CallSequence(Il.Method("FurinaStage", "FadeAndShow"))
            .ToList();
        var ledgerFade = shown.IndexOf("FurinaStageLedger.Fade");
        Assert.True(ledgerFade >= 0, string.Join(", ", shown));
        Assert.Contains("FurinaStagePets.SyncBars", shown.Skip(ledgerFade));
    }

    // ---- 4. Hydro comes from cards ------------------------------------------

    [Theory]
    [InlineData("ProtoFsTidalFlourish")]
    [InlineData("ProtoFsQuickCue")]
    public void The_spend_modes_apply_hydro_after_their_damage(string card)
    {
        var play = Il.CallSequence(Il.Method(card, "OnPlay")).ToList();
        var aura = play.IndexOf("ElementalHit.ApplyOnly");
        Assert.True(aura >= 0, string.Join(", ", play));
        Assert.Equal(1, play.Count(c => c == "ElementalHit.ApplyOnly"));
        // After the Spend mode's hit: the last Attack before it.
        Assert.True(play.Take(aura).Contains("AttackCommand.Execute"),
                    string.Join(", ", play));
    }

    [Fact]
    public void Chevalmarins_card_applies_hydro_then_summons()
    {
        var play = Il.CallSequence(
            Il.Method("ProtoFsSurintendanteChevalmarin", "OnPlay")).ToList();
        var aura = play.IndexOf("ElementalHit.ApplyOnly");
        var summon = play.IndexOf("FurinaStage.Summon");
        Assert.True(aura >= 0 && summon > aura, string.Join(", ", play));
    }

    [Theory]
    [InlineData("ProtoFsTidalFlourish")]
    [InlineData("ProtoFsQuickCue")]
    [InlineData("ProtoFsSurintendanteChevalmarin")]
    public void The_hydro_tip_attaches_where_the_keyword_prints(string card)
    {
        var tips = Il.Calls(Il.Method(card, "get_ExtraHoverTips"));
        Assert.Contains("KleeCardTooltips.ForCard", tips);
    }
}
