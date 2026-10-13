using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace KleeMod.Cards;

/// <summary>
/// A STORY CURSE: "Unplayable. After 3 combats, remove this from your deck."
/// Klee's <see cref="Confinement"/> (Klee story batch 1 sec.3) and Varka's
/// <see cref="OverdueReports"/> (<c>review/active/varka-story-2026-10-13.md</c>
/// sec.3, "built like Klee's Confinement") share this one clock.
///
/// ONLY ITS STORY EVENT GIVES ONE. Each sits in its character's pool (so its
/// frame and <c>CardModel.Pool</c> resolve) and outside every generated
/// list, so no reward, shop or transform rolls it.
///
/// THE CLOCK IS ON THE DECK CARD. <see cref="CombatsServed"/> counts the
/// combats completed since it was added and is a <c>[SavedProperty]</c>, so a
/// save and reload keep it (Genetic Algorithm's way). The count is taken at
/// each combat's end (<see cref="Story.StoryCombatHooks"/>), and the end of the
/// third removes it.
///
/// "Unplayable." is the game's keyword, which prints itself on the card; the
/// description row carries the rest of the paper's sentence.
/// </summary>
public abstract class StoryCurse : CustomCardModel
{
    /// <summary>The paper's sentence after "Unplayable.", for every story Curse.</summary>
    public static readonly string DescriptionText =
        $"After {Story.StoryRules.StoryCurseCombats} combats, remove this from your deck.";

    /// <summary>The card's name, the paper's.</summary>
    protected abstract string CurseTitle { get; }

    public override List<(string, string)>? Localization => new()
    {
        ("title", CurseTitle),
        ("description", DescriptionText),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Unplayable };

    public override int MaxUpgradeLevel => 0;

    private int _combatsServed;

    /// <summary>Combats completed since this card joined the deck.</summary>
    [SavedProperty]
    public int CombatsServed
    {
        get => _combatsServed;
        set
        {
            AssertMutable();
            _combatsServed = value;
        }
    }

    protected StoryCurse()
        : base(-1, CardType.Curse, CardRarity.Curse, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
        => Task.CompletedTask;
}
