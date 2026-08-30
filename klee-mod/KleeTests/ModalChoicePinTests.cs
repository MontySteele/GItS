using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// EB-118 §5.4: the choose-one / modal surface, C# leg.
///
/// A modal card's OnPlay is outside the headless boundary — it needs a live
/// CombatState and a screen — so what is graded here is the NON-UI half:
/// the index resolution, the emit-row shape, and the structural fact that the
/// selection goes through the base game's own choice surface rather than a
/// prompt this mod invented.
///
/// ONE SHIPPED CARD IS MODAL (`deep_breath`), and since EB-182 the selection
/// is made over the AFFORDABLE modes only -- pinned below on the same ground
/// as the unfiltered path.
/// </summary>
public class ModalChoicePinTests
{
    // ---------------------------------------------------------------
    // Index resolution. Generic over `class` on purpose: the rule is
    // reference identity, and stating it over plain strings is what makes it
    // gradeable without a CardModel (which cannot be constructed headlessly).
    // ---------------------------------------------------------------

    [Fact]
    public void Resolve_index_names_the_mode_by_reference_not_by_text()
    {
        var a = new string("gain".ToCharArray());
        var b = new string("gain".ToCharArray());
        var options = new List<string> { a, b };

        Assert.Equal(0, ModalChoice.ResolveIndex(options, a));
        Assert.Equal(1, ModalChoice.ResolveIndex(options, b));
    }

    [Fact]
    public void An_unrecognised_answer_falls_back_to_mode_zero()
    {
        // The screen is opened with canSkip: false, so this is an instrument
        // failure rather than a player action. Resolving mode 0 is preferred
        // to a modal card that resolves nothing; ModalChoice logs a warning.
        var options = new List<string> { "a", "b" };

        Assert.Equal(0, ModalChoice.ResolveIndex(options, "c"));
        Assert.Equal(0, ModalChoice.ResolveIndex<string>(options, null));
    }

    // ---------------------------------------------------------------
    // The emit row. tier0.engine.effects emits
    //   {"event": "mode_chosen", "card": ..., "index": ..., "label": ...}
    // and these two members are the C# mirror. The cross-engine half of this
    // pin lives in tier0/tests/test_eb118_modal_parity.py, which reads both
    // sources; this half stops the C# side moving without that test seeing it.
    // ---------------------------------------------------------------

    [Fact]
    public void The_mode_chosen_row_carries_the_tier0_event_name_and_fields()
    {
        Assert.Equal("mode_chosen", ModalChoice.EventName);
        Assert.Equal(new[] { "card", "index", "label" }, ModalChoice.EventFields);
        Assert.Equal("mode_chosen card=the_card index=1 label=Draw 2",
                     ModalChoice.FormatChoice("the_card", 1, "Draw 2"));
    }

    // ---------------------------------------------------------------
    // Structural pin (see Harness/Il.cs for what that means and what it
    // cannot see). The whole argument for this surface is that the game
    // already owns a card-level player choice and the mod reuses it. If
    // SelectMode ever stopped routing through CardSelectCmd, the co-op sync
    // (PlayerChoiceType.Index) and the ICardSelector automation seam would be
    // lost silently — a bot wall and a desync, neither of which a value test
    // would notice.
    // ---------------------------------------------------------------

    [Fact]
    public void Mode_selection_goes_through_the_games_own_choice_screen()
    {
        var calls = Il.Calls(Il.Method("ModalChoice", "SelectMode"));

        Assert.Contains("CardSelectCmd.FromChooseACardScreen", calls);
        Assert.Contains("ModalChoice.ResolveIndex", calls);
    }

    [Fact]
    public void The_affordable_selection_path_uses_the_same_choice_screen()
    {
        // EB-182: filtering the offered modes must not fork the selection off
        // the base game's screen -- that is the whole co-op/automation
        // argument, and the filtered path is the one a priced card takes.
        var calls = Il.Calls(Il.Method("ModalChoice", "SelectAffordableMode"));

        Assert.Contains("CardSelectCmd.FromChooseACardScreen", calls);
        Assert.Contains("ModalChoice.ResolveIndex", calls);
    }

    [Fact]
    public void Option_cards_are_combat_scoped_owned_instances()
    {
        // The choose-a-card screen dereferences the first option's Owner, so
        // a canonical ModelDb template softlocks it. CreateOption must go
        // through CombatState.CreateCard, the base game's own pattern.
        var calls = Il.Calls(Il.Method("ModalChoice", "CreateOption"));

        Assert.Contains("ICombatState.CreateCard", calls);
    }
}
