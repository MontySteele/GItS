using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Rewards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE LANTERN KEY, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TheLanternKey.cs` and cross-checked
/// against the harvest (2 options: Return the Key, Keep the Key).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same combat LAYOUT and canonical
/// encounter (`MysteriousKnightEventEncounter`, which is what draws the
/// knight on the page before a blow is struck), the same `IsShared`, the same
/// flat `GoldVar(100)` -- no roll, so unlike This or That this event's gold is
/// identical across the arm's switch -- the same gold-then-page on Return, and
/// the same second page offering the fight on Keep, with the Lantern Key card
/// itself as the fight's one extra reward and no resume afterwards.
///
/// TWO KEY SHAPES HERE ARE NOT THE USUAL ONES, and the mirror's spec in
/// `gen_teyvat_events.py` names both:
///
///   * Return the Key's outcome page is
///     `pages.DONE.options.RETURN_THE_KEY.description` -- a page called DONE
///     with the option's name buried inside it, not `pages.RETURN_THE_KEY.*`.
///     Nothing derives that, so the spec's `page_source` says which face line
///     supplies it.
///   * `pages.KEEP_THE_KEY.options.FIGHT` is an option only the second page
///     offers and the face writes no line for, so it takes Keep the Key's own
///     line -- the same branch continued, which is what `extra_options` is
///     for.
///
/// THE CARD AND THE ENCOUNTER ARE THE BASE GAME'S. `LanternKey` carries its
/// global row and the knight's NAME is dressed through
/// `Patches/MonsterNamePatch`, which is the seam every dressed monster name
/// goes through and not this file.
/// </summary>
public abstract class TheLanternKeyMirror : TeyvatEventMirror
{
    /// <summary>The base event's own: this event draws the combat room.</summary>
    public override EventLayoutType LayoutType => EventLayoutType.Combat;

    /// <summary>The base event's own: the encounter the layout shows, and the
    /// one the fight enters.</summary>
    public override EncounterModel CanonicalEncounter =>
        ModelDb.Encounter<MysteriousKnightEventEncounter>();

    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>`TheLanternKey.cs:23`, value for value -- a flat 100, not a
    /// roll.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new GoldVar(100) };

    /// <summary>Two options, in the base event's order, under its names.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ReturnTheKey, InitialOptionKey("RETURN_THE_KEY")),
            new EventOption(this, KeepTheKey, InitialOptionKey("KEEP_THE_KEY")),
        };

    /// <summary>`ReturnTheKey`: the 100 gold, then the DONE page.</summary>
    private async Task ReturnTheKey()
    {
        await PlayerCmd.GainGold(DynamicVars.Gold.BaseValue, Owner);
        SetEventFinished(L10NLookup(PageKey("DONE.options.RETURN_THE_KEY.description")));
    }

    /// <summary>`KeepTheKey`: the second page, offering the fight.</summary>
    private Task KeepTheKey()
    {
        SetEventState(L10NLookup(PageKey("KEEP_THE_KEY.description")), new List<EventOption>
        {
            new EventOption(this, Fight, PageKey("KEEP_THE_KEY.options.FIGHT")),
        });
        return Task.CompletedTask;
    }

    /// <summary>`Fight`: the encounter, with the Lantern Key card itself as a
    /// special reward on top of the standard combat reward, and no
    /// resume.</summary>
    private Task Fight()
    {
        List<Reward> extraRewards = new List<Reward>
        {
            new SpecialCardReward(Owner.RunState.CreateCard<LanternKey>(Owner), Owner),
        };
        EnterCombatWithoutExitingEvent<MysteriousKnightEventEncounter>(
            extraRewards, shouldResumeAfterCombat: false);
        return Task.CompletedTask;
    }
}
