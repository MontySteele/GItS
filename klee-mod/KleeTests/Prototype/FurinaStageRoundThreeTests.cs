using System;
using System.IO;
using System.Runtime.CompilerServices;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// FURINA, THE STAGE -- what round three sent back
/// sec.4. The read is not on main; it is on PR #476's branch, retrieved as
/// <c>git show origin/furina-r3:review/active/furina-stage-round-3-2026-09-09.md</c>
/// (CLAUDE.md, "History retrieval").
///
/// The two rows pinned here are the two that are about the MOD rather than
/// about the blind-play page:
///
///   * the Rare's stale forecast -- "Let the People Rejoice printed 'Deal 2
///     damage to ALL' with the stage reading Usher 12": an earlier card's
///     spend, still in the per-play record while the Rare sat in hand.
///   * the mode chooser's option faces -- "unupgraded (8/12 in hand, 5/9 in
///     the chooser) and unfolded under Weak": the option classes printed the
///     sheet's authored label and declared no vars at all.
///
/// THE SECOND IS A SOURCE PIN, and that is the headless boundary rather than a
/// preference (KleeTests/README.md, "The headless boundary"):
/// <c>DynamicVar.UpdateCardPreview</c> reaches <c>CardModel.CombatState</c>,
/// which this harness cannot build. What a pin CAN say is which shape the
/// generator emitted, which is where the defect lived -- literals on the face
/// and an empty <c>CanonicalVars</c>.
/// </summary>
public class FurinaStageRoundThreeTests
{
    private static string Source(string relativePath) => RepoFile(relativePath);

    /// <summary>A file from the repo, found by walking up from this test's own
    /// source path -- <see cref="FurinaStageRoundTwoTests"/>'s idiom.</summary>
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

    private static string Generated(string type) =>
        Source(Path.Combine("klee-mod", "KleeCode", "Cards", "Prototype",
                            "Generated", type + ".cs"));

    private sealed class StageArm : IDisposable
    {
        private readonly bool _enabled = FurinaStage.Enabled;

        internal StageArm()
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

    // ==================================================================
    // THE FORECAST READS THE BARS, NEVER A REMEMBERED SPEND.
    // ==================================================================

    [Fact]
    public void The_spend_record_is_empty_once_the_play_that_opened_it_ends()
    {
        // ROUND THREE's Rare: a card spent 2, and the NEXT screen's Let the
        // People Rejoice previewed 2 off a stage holding 12. `EB-747` opened
        // the record at BeforeCardPlayed and nothing ever closed it, so
        // between two plays the forecast was the last play's number.
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        stage.Raise(11);                       // a fat bar, as the seat had

        stage.BeginPlay();
        var paid = stage.Spend(2);
        Assert.Equal(2, paid.Paid);
        Assert.Equal(2, stage.SpentThisPlay);  // DURING the play: the record

        stage.EndPlay();

        Assert.Equal(0, stage.SpentThisPlay);  // between two plays: nothing
    }

    [Fact]
    public void An_inner_play_hands_the_outer_card_back_its_own_number()
    {
        // The record is a STACK for `combat.SAVED_PER_CARD`'s reason one
        // engine over: "a free play that spent inside an outer card would
        // otherwise hand the outer card its number". The outer card's own
        // total survives the inner play; the outermost close lands on 0.
        using var _ = new StageArm();
        var seat = Seat.Furina().WithCombatState();
        var stage = FurinaStageLedger.For(seat.Creature);
        stage.Clear();
        stage.Summon(StagePerformer.Usher);
        stage.Raise(11);

        stage.BeginPlay();
        stage.Spend(3);
        stage.BeginPlay();                     // a free play inside it
        stage.Spend(1);
        Assert.Equal(1, stage.SpentThisPlay);
        stage.EndPlay();

        Assert.Equal(3, stage.SpentThisPlay);  // the outer card's own number

        stage.EndPlay();
        Assert.Equal(0, stage.SpentThisPlay);
    }

    [Fact]
    public void The_hook_closes_the_record_the_hook_opened()
    {
        // A source pin because `AfterCardPlayed` needs a CardPlay and a live
        // combat. The pair is what the row is: an opener with no closer is the
        // defect, and the two calls are one arm apart in one file.
        var source = Source(Path.Combine(
            "klee-mod", "KleeCode", "Powers", "Prototype",
            "FurinaStageHooks.cs"));

        Assert.Contains("FurinaStage.BeginPlay(cardPlay.Card?.Owner?.Creature)",
                        source);
        Assert.Contains("FurinaStage.EndPlay(cardPlay.Card?.Owner?.Creature)",
                        source);
    }

    // ==================================================================
    // THE CHOOSER'S OPTION FACES ARE THE PARENT'S OWN.
    // ==================================================================

    [Fact]
    public void A_mode_option_prints_the_parents_tokens_and_not_a_literal()
    {
        // "unupgraded (8/12 in hand, 5/9 in the chooser)". Tidal Flourish's
        // two modes carry the parent's own two damage vars now, so the
        // chooser's body is the sentence the hand printed.
        var source = Generated("ProtoFsTidalFlourish");

        Assert.Contains(
            "(\"description\", \"Deal {PlainDamage:diff()} damage to ALL "
          + "enemies\")", source);
        Assert.Contains(
            "(\"description\", \"[gold]Spend[/gold] 2: deal "
          + "{BranchDamage:diff()} and apply [gold]Hydro[/gold] to ALL "
          + "instead\")", source);
        // AND THE VARS THEY NEED, on the option class rather than only on the
        // parent: a token with no var behind it prints nothing at all.
        Assert.Contains("class ProtoFsTidalFlourishModeA : ModalOptionCard",
                        source);
        Assert.Contains("new DamageVar(\"PlainDamage\", 5m, ValueProp.Move)",
                        source);
        Assert.Contains("new DamageVar(\"BranchDamage\", 9m, ValueProp.Move)",
                        source);
    }

    [Fact]
    public void A_mode_option_takes_the_parents_upgrade_with_it()
    {
        // The option is built from a canonical template on every play, so the
        // smith's +3 reaches it only because the parent is handed in and the
        // option carries the parent's own DynamicVars bumps.
        var source = Generated("ProtoFsTidalFlourish");

        Assert.Contains(
            "ModalChoice.CreateMatchingOption<ProtoFsTidalFlourishModeA>"
          + "(Owner, this)", source);
        Assert.Contains("DynamicVars[\"PlainDamage\"].UpgradeValueBy(3m);",
                        source);

        var modal = Source(Path.Combine("klee-mod", "KleeCode", "Cards",
                                        "ModalChoice.cs"));
        // A DISTINCT NAME and not an overload: `Type.GetMethod` is ambiguous
        // across an overload pair, which is `SelectAffordableMode`'s own rule
        // and which took `ModalChoicePinTests` down when this row broke it.
        Assert.Contains("public static CardModel CreateMatchingOption<T>(",
                        modal);
        Assert.Contains("parent is { IsUpgraded: true }", modal);
        Assert.Contains("option.UpgradeInternal();", modal);
    }

    /// <summary>
    /// `EB-780`'s OTHER HALF, found failing by the live look of 2026-09-16
    /// (proofs-9 lane 0, B3): under Weak 3 an upgraded Curtain Rise read
    /// 7 / 12 in the hand and 10 / 16 in the chooser. The upgrade above
    /// carried -- 10 and 16 ARE the upgraded literals, which is what the test
    /// above bought -- and the board never reached the face at all.
    ///
    /// AND THE CAUSE IS NOT THE VARS. The option already carries the parent's
    /// <c>CanonicalVars</c>, bound to the parent's owner. What it does not
    /// carry is a PILE: <c>CardModel.UpdateDynamicVarPreview</c> hands its
    /// vars <c>runGlobalHooks: CombatState != null &amp;&amp; (Pile?.Type is
    /// Hand or Play || UpgradePreviewType == Combat)</c>, and an option is in
    /// no pile by construction -- which also nulls <c>CombatState</c>, whose
    /// getter reads the same two facts. Both halves failed, so every var on
    /// the face printed its <c>BaseValue</c>.
    ///
    /// The repair is the game's own door for exactly this case, whose summary
    /// in the 0.111.0 decompile is "to facilitate having upgrade previews
    /// reflect power values from the player in combat (i.e. Armaments)".
    ///
    /// A SOURCE PIN, for the reason this class's header gives: the number
    /// itself needs a live combat this harness cannot build, so what is pinned
    /// is the wiring and the number is owed a live look.
    /// </summary>
    [Fact]
    public void A_mode_option_is_a_combat_preview_so_the_board_folds_into_it()
    {
        var modal = Source(Path.Combine("klee-mod", "KleeCode", "Cards",
                                        "ModalChoice.cs"));

        Assert.Contains(
            "option.UpgradePreviewType = CardUpgradePreviewType.Combat;",
            modal);
        // AFTER the upgrade, never before: the setter asserts mutability and
        // refuses to leave the preview state once entered, so `UpgradeInternal`
        // runs on a card the game does not yet consider a preview.
        Assert.True(
            modal.IndexOf("option.UpgradeInternal();", StringComparison.Ordinal)
            < modal.IndexOf(
                "option.UpgradePreviewType = CardUpgradePreviewType.Combat;",
                StringComparison.Ordinal));
        // And the decompiled rule it turns on is written down beside it, so a
        // later reader need not re-derive why an off-pile face is unfolded.
        Assert.Contains("runGlobalHooks", modal);
    }
}
