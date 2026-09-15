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
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events;

/// <summary>
/// THE SPRINGVALE CHEESE CELLAR -- Room Full of Cheese, converted (spike item
/// 4.2). Text is `docs/current/dossiers/content/event-conversion-gallery.md`
/// variant 1 (Mondstadt / Adventurers' Guild, "literal"); mechanics are the
/// base event's, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/RoomFullOfCheese.cs` and cross-checked
/// against the frozen harvest in `docs/sts2-events-harvest.txt:247-251`.
///
/// NOTHING MECHANICAL IS AUTHORED HERE, and the diff against the base class
/// says so: the same `DamageVar(14m, Unblockable | Unpowered)`, the same eight
/// Commons at uniform odds with `NoRarityModification`, the same take-two
/// selector, the same `CreatureCmd.Damage` then `RelicCmd.Obtain&lt;ChosenCheese&gt;`
/// on the second option, the same `IsAllowed` act gate. What changed is three
/// loc keys and the class name. That is what "text conversions are
/// hygiene-grade" (frame packet sec.5) has to mean to be checkable.
///
/// THE ONE THING THE CONVERSION COULD NOT CARRY is the relic's NAME. The
/// gallery calls it The Anointed Wheel; `RelicCmd.Obtain&lt;ChosenCheese&gt;` grants
/// The Chosen Cheese, whose own loc rows are the base game's and are global --
/// a merge cannot hold two values for one key, exactly as with monster names,
/// and relics have no `L10NMonsterLookup`-shaped choke point. Renaming it
/// needs its own seam and is NOT in this spike. The gallery's flag about the
/// sim's substitution of a plain random relic is a tier05 matter and is
/// untouched here: the C# grants the real relic, as it always did.
///
/// AND IT IS NOT IN ANY ACT'S `AllEvents`. It reaches the map by substitution
/// at pull time -- `Patches/PullNextEventPatch` has the argument, and the
/// short version is that the base event is a SHARED event, so swapping it
/// inside a dressing's pool would have changed the pool's LENGTH and moved the
/// run's `UpFront` rng.
/// </summary>
public sealed class SpringvaleCheeseCellar : EventModel
{
    /// <summary>
    /// The base event's damage var, value for value: 14, `Unblockable` so
    /// Block cannot absorb it and `Unpowered` so Strength cannot move it
    /// (`RoomFullOfCheese.cs:21`). The harvest prints "Lose 14 HP" and the
    /// gallery's variant 1 prints the same number.
    /// </summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DamageVar(14m, ValueProp.Unblockable | ValueProp.Unpowered) };

    /// <summary>
    /// The base event's act gate, unchanged: acts 1 and 2 only
    /// (`RoomFullOfCheese.cs:23-26`). It is asked of the SUBSTITUTE as well as
    /// of the base event, because `RoomSet.EnsureNextEventIsValid` consults
    /// whatever event is at the head of the list -- which is the base one --
    /// and the postfix then swaps. Keeping the gates identical is what makes
    /// that ordering irrelevant.
    /// </summary>
    public override bool IsAllowed(IRunState runState) => runState.CurrentActIndex < 2;

    /// <summary>
    /// Two options, in the base event's order, with the base event's hover tip
    /// and the base event's damage annotation on the second. The loc keys are
    /// this class's own (`SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.options.*`)
    /// and `TeyvatLoc` merges their strings; the verbs they name are the
    /// gallery's -- "Taste the Racks" and "Haul Out the Back Wall" -- where
    /// the base event's are "Gorge" and "Search".
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, TasteTheRacks,
                "SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.options.TASTE_THE_RACKS"),
            new EventOption(this, HaulOutTheBackWall,
                "SPRINGVALE_CHEESE_CELLAR.pages.INITIAL.options.HAUL_OUT_THE_BACK_WALL",
                HoverTipFactory.FromRelic<ChosenCheese>())
                .ThatDoesDamage(DynamicVars.Damage.BaseValue),
        };

    /// <summary>
    /// `Gorge`, renamed. Eight Commons from the owner's own character pool at
    /// UNIFORM odds with `NoRarityModification` -- which is what makes the
    /// harvest's "the 8 cards will not contain any duplicates" and the
    /// gallery's "the eight wheels offered are never duplicates" true, since
    /// both are properties of `CardFactory.CreateForReward`'s sampler and not
    /// of this method. Take two.
    /// </summary>
    private async Task TasteTheRacks()
    {
        Player owner = Owner;
        CardCreationOptions options = CardCreationOptions
            .ForNonCombatWithUniformOdds(
                new List<CardPoolModel> { owner.Character.CardPool },
                (CardModel c) => c.Rarity == CardRarity.Common)
            .WithFlags(CardCreationFlags.NoRarityModification);

        List<CardCreationResult> cards = CardFactory.CreateForReward(owner, 8, options).ToList();
        CardSelectorPrefs prefs = new CardSelectorPrefs(
            L10NLookup("SPRINGVALE_CHEESE_CELLAR.pages.TASTE_THE_RACKS.selectionScreenPrompt"), 2);

        await SelectCardsToAddToDeckFromGrid(cards, prefs);
        SetEventFinished(L10NLookup("SPRINGVALE_CHEESE_CELLAR.pages.TASTE_THE_RACKS.description"));
    }

    /// <summary>
    /// `Search`, renamed. The damage then the relic, in the base event's
    /// order, through the base event's two commands.
    /// </summary>
    private async Task HaulOutTheBackWall()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.Damage, null, null, null);
        await RelicCmd.Obtain<ChosenCheese>(Owner);
        SetEventFinished(L10NLookup("SPRINGVALE_CHEESE_CELLAR.pages.HAUL_OUT_THE_BACK_WALL.description"));
    }
}
