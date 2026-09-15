using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// HUNGRY FOR MUSHROOMS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/HungryForMushrooms.cs` and cross-checked
/// against the harvest (2 options: Big Mushroom, Fragrant Mushroom).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two relics, in the same
/// order, and the same `ThatDoesDamage(15)` annotation on the second -- which
/// is an ANNOTATION and not a hit, exactly as in the base event. Fragrant
/// Mushroom's own on-pickup clause is what actually costs the HP; the event
/// only tells the player so.
///
/// THE TWO OPTIONS ARE `RelicOption&lt;T&gt;`, WHICH IS WHY THIS MIRROR HAS NO
/// `InitialOptionKey` CALL. `EventModel.RelicOption` builds its key as
/// `OptionKey(pageName, relic.Id.Entry)` -- the RELIC's entry, not an option
/// name the event chooses -- so the keys are
/// `&lt;dressed entry&gt;.pages.INITIAL.options.BIG_MUSHROOM` and
/// `...FRAGRANT_MUSHROOM`, and they re-key per face for free like every other
/// derived key because `OptionKey` slugifies `GetType().Name`. The mirror's
/// spec in `gen_teyvat_events.py` DECLARES those two names, because the
/// index's literal scrape cannot see them: they are never written in this
/// file or in the base event's.
///
/// AND THE DRESSED ROWS WIN OVER THE RELICS' OWN. `EventOption.FromRelic` is
/// `GetOptionTitle(textKey) ?? relic.Title` and
/// `GetOptionDescription(textKey) ?? relic.DynamicEventDescription`, so the
/// base game shows the relic's name and description only because no row
/// exists at that key. The generator writes BOTH rows for every option
/// (EB-765), so a dressed Hungry for Mushrooms shows the face's words and the
/// relic's hover tip -- which is the borrowing this arm wants, not a rename of
/// the relic.
/// </summary>
public abstract class HungryForMushroomsMirror : TeyvatEventMirror
{
    /// <summary>Two relic options, in the base event's order, with the damage
    /// annotation on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            RelicOption<BigMushroom>(BigMushroom),
            RelicOption<FragrantMushroom>(FragrantMushroom).ThatDoesDamage(15m),
        };

    /// <summary>`BigMushroom`: the relic, then the page.</summary>
    private async Task BigMushroom()
    {
        await RelicCmd.Obtain<BigMushroom>(Owner);
        SetEventFinished(L10NLookup(PageKey("BIG_MUSHROOM.description")));
    }

    /// <summary>`FragrantMushroom`: the relic, then the page. The HP is the
    /// relic's clause and is not repeated here.</summary>
    private async Task FragrantMushroom()
    {
        await RelicCmd.Obtain<FragrantMushroom>(Owner);
        SetEventFinished(L10NLookup(PageKey("FRAGRANT_MUSHROOM.description")));
    }
}
