using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// AROMA OF CHAOS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/AromaOfChaos.cs` and cross-checked
/// against the harvest (2 options: Let Go, Maintain Control).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: no canonical vars, no act gate, the
/// same one-card transform selector under `TransformSelectionPrompt` with the
/// same static Transform hover tip, and the same one-card upgrade selector
/// under `UpgradeSelectionPrompt`. Both branches null-guard the selection the
/// way the base event does, because a cancelled selector answers an empty
/// list.
///
/// THE ONE CLAUSE WORTH READING TWICE is the `AromaPrinciple` var on the
/// second page. The base event pulls it out of the CHARACTER table --
/// `new LocString("characters", Owner.Character.Id.Entry + ".aromaPrinciple")`
/// -- so the Maintain Control page can end in a line the played character
/// says. That is a base-game row per character and it is NOT this arm's to
/// write: the mirror adds the var exactly as the base event does, and a
/// dressing whose outcome text does not reference `{AromaPrinciple}` simply
/// never prints it. Dropping the `Add` would have been a mechanical change to
/// what the page can say, which is the one thing a mirror may not do.
/// </summary>
public abstract class AromaOfChaosMirror : TeyvatEventMirror
{
    /// <summary>`AromaOfChaos.cs:16`: none.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars => Array.Empty<DynamicVar>();

    /// <summary>Two options, in the base event's order, under its names, with
    /// the static Transform tip on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, LetGo, InitialOptionKey("LET_GO"),
                HoverTipFactory.Static(StaticHoverTip.Transform)),
            new EventOption(this, MaintainControl, InitialOptionKey("MAINTAIN_CONTROL")),
        };

    /// <summary>`LetGo`: one chosen card transformed at random, off the
    /// EVENT's rng.</summary>
    private async Task LetGo()
    {
        CardModel card = (await CardSelectCmd.FromDeckForTransformation(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("LET_GO.description")));
    }

    /// <summary>`MaintainControl`: one chosen card upgraded, and the
    /// character's own aroma line added to the page.</summary>
    private async Task MaintainControl()
    {
        CardModel card = (await CardSelectCmd.FromDeckForUpgrade(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Upgrade(card);
        }

        LocString description = L10NLookup(PageKey("MAINTAIN_CONTROL.description"));
        description.Add("AromaPrinciple", new LocString("characters", Owner.Character.Id.Entry + ".aromaPrinciple"));
        SetEventFinished(description);
    }
}
