using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Saves.Runs;

namespace KleeMod.Cards;

/// <summary>
/// CONFINEMENT, Klee's own Curse (Klee story batch 1 sec.3,
/// <c>review/active/klee-story-batch-1-2026-10-12.md</c>): "Unplayable. After
/// 3 combats, remove this from your deck." Jean always lets her out
/// eventually.
///
/// ONLY STARSNATCH CLIFF GIVES IT. It sits in Klee's pool (so its frame and
/// <c>CardModel.Pool</c> resolve) on the never-generated list
/// (<see cref="KleeOffPoolCards"/>), so no reward, shop or transform rolls it.
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
public sealed class Confinement : CustomCardModel
{
    public const string TitleText = "Confinement";

    public static readonly string DescriptionText =
        $"After {Story.StoryRules.ConfinementCombats} combats, remove this from your deck.";

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("proto_ko_sorry_jean");

    public override List<(string, string)>? Localization => new()
    {
        ("title", TitleText),
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

    public Confinement()
        : base(-1, CardType.Curse, CardRarity.Curse, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
        => Task.CompletedTask;
}
