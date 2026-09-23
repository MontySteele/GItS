using System;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- the two round-two rows that are about NUMBERS the
/// player reads rather than about what the page draws: `EB-745` (the shipped
/// meters are never granted under the arm) and `EB-747` (a reader face prints
/// the live number, and 0 before the play).
///
/// Both rows were BUILT before this file existed and neither named a test, so
/// the guards below are the acceptance sentences of the two rows, word for
/// word, turned into assertions:
///
///   * `EB-745` -- "no Fanfare buff or Encore in an arm run's status list or
///     wire resources". The status list and the wire's resources block are two
///     READINGS of the same three resources (<c>FanfareResource</c>,
///     <c>FanfareFloorResource</c>, <c>EncoreResource</c>) plus the badge
///     Power that mirrors the first, so the honest place to assert is the
///     resources themselves and the creature's own power list -- which is what
///     both surfaces walk. A bridge-shaped assertion would only prove the
///     bridge's copy of a number this file already has at the source.
///   * `EB-747` -- "an empty-stage scenario prints Ousia Surge as 0 before
///     play." Her reader faces compute from the bars through
///     <see cref="FurinaStage"/>, so the number the face prints and the number
///     asserted here are one expression (see the row's header on
///     <c>SpentOrBackFanfare</c>). The FACE's own render is out of reach
///     headless -- <c>DynamicVar.UpdateCardPreview</c> reaches
///     <c>CardModel.CombatState</c> (KleeTests/README.md) -- so the multiplier
///     the generated card declares is pinned as source beside the arithmetic.
///
/// NOTHING MEASURED HERE IS QUOTABLE (R215 B): a prototype arm's arithmetic,
/// not a number about a game.
/// </summary>
public class FurinaStageShippedMeterTests
{
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal Arm(bool on = true)
        {
            FurinaStageLedger.ResetAll();
            FurinaStage.Enabled = on;
        }

        public void Dispose()
        {
            FurinaStage.Enabled = _enabled;
            FurinaStageLedger.ResetAll();
        }
    }

    /// <summary>A card in a seat's hand: mutable, owned, and therefore
    /// askable. `IsMutable` first -- Owner's setter calls AssertMutable. The
    /// idiom is <c>MeterCostBadgeTests.Held</c>'s.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>A generated card's own source, found by walking up from this
    /// test's source path -- <c>FurinaStageRoundTwoTests</c>'s idiom, so a run
    /// from any working directory reads the tree the build compiled.</summary>
    private static string Generated(string type,
                                    [CallerFilePath] string here = "")
    {
        var relative = Path.Combine("klee-mod", "KleeCode", "Cards",
                                    "Prototype", "Generated", type + ".cs");
        var dir = Path.GetDirectoryName(here);
        while (dir != null)
        {
            var candidate = Path.Combine(dir, relative);
            if (File.Exists(candidate)) return File.ReadAllText(candidate);
            dir = Path.GetDirectoryName(dir);
        }
        throw new FileNotFoundException(relative);
    }

    // ==================================================================
    // `EB-745`. THE ARM NEVER GRANTS THE SHIPPED FANFARE OR ENCORE.
    // ==================================================================

    /// <summary>
    /// THE ACCEPTANCE SENTENCE. All four mint doors are knocked on at once --
    /// HP-loss Fanfare, the floor, the cap and Encore -- and every one of them
    /// refuses, so the three resources a status list or a wire block would
    /// read are still at nothing and the badge Power was never applied.
    ///
    /// THE CAP IS ASSERTED TOO, and it is the door that would have been easy
    /// to miss: <c>RaiseFanfareCap</c> writes a DIFFERENT resource
    /// (<c>FanfareCapBonusResource</c>) from the one the meter lives in, so a
    /// gate on the meter alone would leave a bonus sitting in the save that
    /// the shipped cap formula reads the moment the arm comes off.
    /// </summary>
    [Fact]
    public void Under_the_stage_the_shipped_meters_never_mint()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();

        FurinaResources.GainFanfare(seat.Creature, 30);
        FurinaResources.GainFanfareFloor(seat.Creature, 10);
        FurinaResources.RaiseFanfareCap(seat.Creature, 40);
        FurinaResources.GainEncore(seat.Creature, 5);

        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(0, FurinaResources.FanfareFloor(seat.Creature));
        Assert.Equal(0, FurinaResources.Encore(seat.Creature));

        // The cap is still the sheet's own fraction of her max HP and carries
        // no bonus: nothing was banked behind the gate.
        Assert.Equal(
            (int)(FurinaResourceConstants.FanfareCapFraction * seat.Creature.MaxHp),
            FurinaResources.FanfareCap(seat.Creature));

        // THE STATUS LIST. "Fanfare 30 (buff), generated by losing HP, nothing
        // spends it" is the line three round-two seats read; it is this Power.
        Assert.Empty(seat.Creature.Powers.OfType<FanfareMeterPower>());
        Assert.Empty(seat.Creature.Powers.OfType<EncoreMeterPower>());
    }

    /// <summary>
    /// THE CONTROL. Flag off, every one of the same four doors mints exactly
    /// as it ships -- so the pin above is about the ARM and not about a
    /// headless harness that could never grant anything.
    ///
    /// The numbers follow the shipped arithmetic in call order: the floor
    /// grant raises the floor, the cap bonus AND the meter by the same amount
    /// (<c>GainFanfareFloor</c>'s three lines), and the cap raise adds to the
    /// same bonus resource.
    /// </summary>
    [Fact]
    public void Flag_off_the_shipped_meters_mint_as_they_ship()
    {
        using var _ = new Arm(on: false);
        var seat = Seat.Furina().WithCombatState();
        var baseCap =
            (int)(FurinaResourceConstants.FanfareCapFraction * seat.Creature.MaxHp);

        FurinaResources.GainFanfare(seat.Creature, 12);
        FurinaResources.GainEncore(seat.Creature, 5);
        FurinaResources.GainFanfareFloor(seat.Creature, 4);
        FurinaResources.RaiseFanfareCap(seat.Creature, 6);

        Assert.Equal(16, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(4, FurinaResources.FanfareFloor(seat.Creature));
        Assert.Equal(5, FurinaResources.Encore(seat.Creature));
        Assert.Equal(baseCap + 10, FurinaResources.FanfareCap(seat.Creature));
    }

    /// <summary>
    /// AND THE GATE IS HERS ALONE. Klee at the table in co-op keeps every
    /// meter she has; the arm's switch is asked about a CREATURE, not about a
    /// build (`EB-194` / `EB-221`, the shape this repo keeps meeting).
    /// </summary>
    [Fact]
    public void The_retirement_is_hers_and_not_the_tables()
    {
        using var _ = new Arm();

        Assert.True(FurinaResources.StageRetiresTheShippedMeters(
            Seat.Furina().Creature));
        Assert.False(FurinaResources.StageRetiresTheShippedMeters(
            Seat.Klee().Creature));
        Assert.False(FurinaResources.StageRetiresTheShippedMeters(null));
    }

    // ==================================================================
    // `EB-747`. A READER FACE PRINTS THE LIVE NUMBER, AND 0 BEFORE PLAY.
    // ==================================================================

    /// <summary>
    /// THE ACCEPTANCE SENTENCE: an empty-stage board prints <i>Ousia
    /// Surge</i> as 0 before the play.
    ///
    /// The face's multiplier IS <c>FurinaStage.BackFanfare(card)</c> since
    /// R276 (pinned as source below), so this is the number the card prints,
    /// asked at the moment the preview asks it -- before anything has been
    /// spent.
    /// </summary>
    [Fact]
    public void An_empty_stage_prints_ousia_surge_as_zero()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var card = Held<ProtoFsOusiaSurge>(seat);

        Assert.False(FurinaStage.Occupied(seat.Creature));
        Assert.Equal(0, FurinaStage.BackFanfare(card));
    }

    /// <summary>
    /// AND WITH A LEAD AT N FANFARE IT PRINTS N. The bar is built through the
    /// ledger's own verbs -- a summon lands at
    /// <c>FurinaStageLaw.SummonFanfare</c> and a Raise goes to the back seat,
    /// which with one performer is also the lead -- so the fixture cannot set
    /// a bar no game can produce.
    /// </summary>
    [Fact]
    public void A_lead_at_n_fanfare_prints_n_on_ousia_surge()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var card = Held<ProtoFsOusiaSurge>(seat);

        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        stage.Raise(7 - FurinaStageLaw.SummonFanfare);

        // One performer: the lead IS the back performer, so both reads agree.
        Assert.Equal(7, FurinaStage.BackFanfare(card));
        Assert.Equal(7, FurinaStage.LeadFanfare(seat.Creature));
    }

    /// <summary>
    /// THE OTHER TWO READERS, at the same two moments. <i>Final Bow</i> reads
    /// the BACK performer's bar (R276) and <i>Let the People Rejoice</i> the
    /// whole company's,
    /// and each answers with what the play TOOK once it has taken it -- one
    /// expression, so the previewed number and the resolved number cannot
    /// differ. 0 on an empty stage in both moments is the row's own wording.
    /// </summary>
    [Fact]
    public void The_spend_readers_print_the_bar_before_and_the_take_after()
    {
        using var _ = new Arm();
        var seat = Seat.Furina().WithCombatState();
        var bow = Held<ProtoFsFinalBow>(seat);
        var rejoice = Held<ProtoFsLetThePeopleRejoice>(seat);

        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();

        // Empty stage, nothing spent: both print 0.
        stage.BeginPlay();
        Assert.Equal(0, FurinaStage.SpentOrBackFanfare(bow));
        Assert.Equal(0, FurinaStage.SpentOrTotalFanfare(rejoice));

        stage.Summon(StagePerformer.Usher);
        stage.Raise(5 - FurinaStageLaw.SummonFanfare);
        stage.Summon(StagePerformer.Chevalmarin);
        stage.Raise(3 - FurinaStageLaw.SummonFanfare);

        // BEFORE THE PLAY. The back performer is the last seat (3) and the
        // company is both bars (8) -- the numbers the two faces are ABOUT to
        // take.
        stage.BeginPlay();
        Assert.Equal(3, FurinaStage.SpentOrBackFanfare(bow));
        Assert.Equal(8, FurinaStage.SpentOrTotalFanfare(rejoice));

        // DURING THE PLAY. The bars are gone and the record is what the card
        // took, which is the same number the preview showed. THE LEDGER'S OWN
        // verb rather than `FurinaStage.CollectAll`, which also reflows the
        // placement and refreshes the strip -- a scene tree this harness does
        // not have (KleeTests/README.md); the arithmetic is the same object's.
        Assert.Equal(8, stage.CollectAll());
        Assert.Equal(8, FurinaStage.SpentOrTotalFanfare(rejoice));
    }

    /// <summary>
    /// SOURCE PIN, and the one this file cannot do without: the three faces
    /// declare the STAGE's readers as their multiplier. A face that grew its
    /// own copy of the arithmetic -- or that went back to a printed constant,
    /// which is the defect round two filed ("the readers print a rule where a
    /// number is known") -- reads identically in every behavioural assertion
    /// above, because those ask the calculator directly.
    /// </summary>
    [Fact]
    public void The_reader_faces_ask_the_stage_for_their_number()
    {
        // R276 pick 2: Ousia Surge reads the bank, Pneuma Refrain the shield.
        Assert.Contains(
            "FurinaStage.BackFanfare(card)",
            Generated("ProtoFsOusiaSurge"));
        Assert.Contains(
            "FurinaStage.SpentOrBackFanfare(card)",
            Generated("ProtoFsFinalBow"));
        Assert.Contains(
            "FurinaStage.SpentOrTotalFanfare(card)",
            Generated("ProtoFsLetThePeopleRejoice"));
        Assert.Contains(
            "FurinaStage.LeadFanfare(card)",
            Generated("ProtoFsPneumaRefrain"));
    }
}
