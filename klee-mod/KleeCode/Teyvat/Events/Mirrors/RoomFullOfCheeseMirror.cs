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

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// ROOM FULL OF CHEESE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/RoomFullOfCheese.cs` and cross-checked
/// against the frozen harvest in `docs/sts2-events-harvest.txt:247-251`.
///
/// NOTHING MECHANICAL IS AUTHORED HERE, and the diff against the base class
/// says so: the same `DamageVar(14m, Unblockable | Unpowered)`, the same eight
/// Commons at uniform odds with `NoRarityModification`, the same take-two
/// selector, the same `CreatureCmd.Damage` then `RelicCmd.Obtain&lt;ChosenCheese&gt;`
/// on the second option, the same `IsAllowed` act gate, in the same order.
/// What changed is that every loc key is DERIVED rather than written out, so
/// the class carries no dressing at all and every nation that dresses this
/// event is a one-line generated subclass.
///
/// THIS REPLACES THE SPIKE'S `SpringvaleCheeseCellar` (item 4.2), which was
/// this body with `SPRINGVALE_CHEESE_CELLAR.` spelled into six literals. The
/// Mondstadt dressing is now
/// `Teyvat/Events/Mondstadt/SpringvaleCheeseCellar.cs`, generated, and the
/// Liyue dressing costs the same nothing.
///
/// THE ONE THING A CONVERSION CANNOT CARRY is the relic's NAME.
/// `RelicCmd.Obtain&lt;ChosenCheese&gt;` grants The Chosen Cheese, whose loc rows are
/// the base game's and are GLOBAL -- a merge cannot hold two values for one
/// key, exactly as with monster names, and relics have no
/// `L10NMonsterLookup`-shaped choke point. Renaming it needs its own seam and
/// is not in this surface: the C# grants the real relic, as it always did.
///
/// AND IT IS IN NO ACT'S `AllEvents`. A dressed event reaches the map by
/// substitution at pull time -- `Patches/PullNextEventPatch` has the argument,
/// and the short version is that the base event is a SHARED event, so swapping
/// it inside a dressing's pool would have changed the pool's LENGTH and moved
/// the run's `UpFront` rng.
/// </summary>
public abstract class RoomFullOfCheeseMirror : TeyvatEventMirror
{
    /// <summary>
    /// The base event's damage var, value for value: 14, `Unblockable` so
    /// Block cannot absorb it and `Unpowered` so Strength cannot move it
    /// (`RoomFullOfCheese.cs:21`). The harvest prints "Lose 14 HP".
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
    /// Two options, in the base event's order, under the base event's option
    /// NAMES (`GORGE`, `SEARCH`) and with the base event's hover tip and
    /// damage annotation on the second.
    ///
    /// THE NAMES STAY THE BASE GAME'S ON PURPOSE. They are internal keys, not
    /// text: what the player reads is the `.title` row the generator writes
    /// for this dressing, and the spike's rename to `TASTE_THE_RACKS` bought
    /// nothing but a second thing to keep in step. `InitialOptionKey` prefixes
    /// them with the DRESSED entry, so Mondstadt's and Liyue's rows never
    /// collide and neither can reach `ROOM_FULL_OF_CHEESE.*`.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Gorge, InitialOptionKey("GORGE")),
            new EventOption(this, Search, InitialOptionKey("SEARCH"),
                HoverTipFactory.FromRelic<ChosenCheese>())
                .ThatDoesDamage(DynamicVars.Damage.BaseValue),
        };

    /// <summary>
    /// `Gorge`. Eight Commons from the owner's own character pool at UNIFORM
    /// odds with `NoRarityModification` -- which is what makes the harvest's
    /// "the 8 cards will not contain any duplicates" true, since that is a
    /// property of `CardFactory.CreateForReward`'s sampler and not of this
    /// method. Take two.
    /// </summary>
    private async Task Gorge()
    {
        Player owner = Owner;
        CardCreationOptions options = CardCreationOptions
            .ForNonCombatWithUniformOdds(
                new List<CardPoolModel> { owner.Character.CardPool },
                (CardModel c) => c.Rarity == CardRarity.Common)
            .WithFlags(CardCreationFlags.NoRarityModification);

        List<CardCreationResult> cards = CardFactory.CreateForReward(owner, 8, options).ToList();
        CardSelectorPrefs prefs = new CardSelectorPrefs(
            L10NLookup(PageKey("GORGE.selectionScreenPrompt")), 2);

        await SelectCardsToAddToDeckFromGrid(cards, prefs);
        SetEventFinished(L10NLookup(PageKey("GORGE.description")));
    }

    /// <summary>
    /// `Search`. The damage then the relic, in the base event's order, through
    /// the base event's two commands.
    /// </summary>
    private async Task Search()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.Damage, null, null, null);
        await RelicCmd.Obtain<ChosenCheese>(Owner);
        SetEventFinished(L10NLookup(PageKey("SEARCH.description")));
    }
}
