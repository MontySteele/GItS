using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// BRAIN LEECH, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/BrainLeech.cs` and cross-checked against
/// the harvest (2 options: Share Knowledge, Rip).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same four canonical vars
/// (`DamageVar("RipHpLoss", 5, Unblockable | Unpowered)` and the three counts
/// that make the prose say "1 of 5"), the same acts-1-and-2 gate, the same
/// five-from-the-character-pool grid with `Cancelable` FALSE, and the same
/// colourless three-card reward offered `RewardCount` times after the damage.
///
/// THE COUNTS ARE VARS AND THE MIRROR READS THEM AS VARS. `RewardCount` is
/// the loop bound, `FromCardChoiceCount` is the number of cards created and
/// `CardChoiceCount` is the number the grid takes -- all three are printed in
/// the dressing's prose, so reading the literal 5 instead of the var would
/// have let the page and the grid drift apart.
///
/// THE COLOURLESS REWARD IS THE BASE GAME'S POOL, not a dressed one, for the
/// same reason the cheese cellar grants the real Chosen Cheese: a card pool
/// is a global model and this arm renames nothing in it.
/// </summary>
public abstract class BrainLeechMirror : TeyvatEventMirror
{
    /// <summary>`BrainLeech.cs:27-33`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar("RipHpLoss", 5m, ValueProp.Unblockable | ValueProp.Unpowered),
            new IntVar("RewardCount", 1m),
            new IntVar("CardChoiceCount", 1m),
            new IntVar("FromCardChoiceCount", 5m),
        };

    /// <summary>The base event's act gate, unchanged: acts 1 and 2 only.
    /// It is asked of the SUBSTITUTE as well as of the base event, because
    /// `RoomSet.EnsureNextEventIsValid` consults whatever event is at the head
    /// of the list -- which is the base one -- and the postfix then
    /// swaps.</summary>
    public override bool IsAllowed(IRunState runState) => runState.CurrentActIndex < 2;

    /// <summary>Two options, in the base event's order, under its names, with
    /// the damage annotation on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ShareKnowledge, InitialOptionKey("SHARE_KNOWLEDGE")),
            new EventOption(this, Rip, InitialOptionKey("RIP"))
                .ThatDoesDamage(DynamicVars["RipHpLoss"].BaseValue),
        };

    /// <summary>
    /// `Rip`. The damage first, then `RewardCount` colourless card rewards of
    /// three, at DEFAULT odds with no rarity modification and no card-pool
    /// modifications -- the harvest's "Colorless 2 card reward" read as the
    /// base event builds it.
    /// </summary>
    private async Task Rip()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            (DamageVar)DynamicVars["RipHpLoss"], null, null, null);

        for (int i = 0; i < DynamicVars["RewardCount"].IntValue; i++)
        {
            CardCreationOptions options = CardCreationOptions
                .ForNonCombatWithDefaultOdds(
                    new List<CardPoolModel> { ModelDb.CardPool<ColorlessCardPool>() })
                .WithFlags(CardCreationFlags.NoRarityModification | CardCreationFlags.NoCardPoolModifications);
            CardReward reward = new CardReward(options, 3, Owner);
            await RewardsCmd.OfferCustom(Owner, new List<Reward>(1) { reward });
        }

        SetEventFinished(L10NLookup(PageKey("RIP.description")));
    }

    /// <summary>
    /// `ShareKnowledge`. `FromCardChoiceCount` cards off the owner's own
    /// character pool at default odds, offered on a grid that CANNOT be
    /// cancelled -- the base event's own `Cancelable = false`, which is what
    /// makes the option a choice of card rather than a choice of whether to
    /// take one.
    /// </summary>
    private async Task ShareKnowledge()
    {
        Player owner = Owner;
        List<CardCreationResult> cards = CardFactory.CreateForReward(
            owner, DynamicVars["FromCardChoiceCount"].IntValue,
            CardCreationOptions.ForNonCombatWithDefaultOdds(
                new List<CardPoolModel> { owner.Character.CardPool })).ToList();

        CardSelectorPrefs prefs = new CardSelectorPrefs(
            L10NLookup(PageKey("SHARE_KNOWLEDGE.selectionScreenPrompt")), 1)
        {
            // The base event's own `Cancelable = false`, written as an object
            // initialiser because the property is init-only in 0.111.0 -- the
            // decompile prints the setter as a statement, which is what an
            // initialiser lowers to.
            Cancelable = false,
        };

        await SelectCardsToAddToDeckFromGrid(cards, prefs);
        SetEventFinished(L10NLookup(PageKey("SHARE_KNOWLEDGE.description")));
    }
}
