using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// TEA MASTER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TeaMaster.cs` and cross-checked against
/// the harvest (3 options: Bone Tea, Ember Tea, Tea of Discourtesy).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two prices (50 and 150), the
/// same three `StringVar`s reading the three relics' own dynamic
/// descriptions, the same gate (acts 1 and 2, every player holding 150), the
/// same `FromRelicExcludingItself` hover tip on all three, and the same
/// pay-then-obtain order on the two that cost anything.
///
/// THE TEAS ARE RELICS AND THEY ARE THE BASE GAME'S. `BoneTea`, `EmberTea`
/// and `TeaOfDiscourtesy` have global loc rows, exactly like the Chosen
/// Cheese; the C# grants the real relics and a dressing renames none of them.
/// What the player reads on the OPTION is the dressing's row, and the
/// description each option prints is the relic's own text through the var --
/// which is why the vars are read off `ModelDb` here and not spelled into the
/// face.
///
/// THE `DONE` PAGE IS SHARED BY TWO OPTIONS, which is why the mirror ledger
/// grew a `page_source` row. Bone Tea and Ember Tea both finish on
/// `pages.DONE.description`, so there is no option of that NAME for the
/// generator to derive the page's text from; the row says Bone Tea's line
/// supplies it -- the first option that lands there -- rather than leaving a
/// page the player can reach with an empty row.
/// </summary>
public abstract class TeaMasterMirror : TeyvatEventMirror
{
    /// <summary>`TeaMaster.cs:25-32`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("BoneTeaCost", 50m),
            new DynamicVar("EmberTeaCost", 150m),
            new StringVar("BoneTeaDescription", ModelDb.Relic<BoneTea>().DynamicDescription.GetFormattedText()),
            new StringVar("EmberTeaDescription", ModelDb.Relic<EmberTea>().DynamicDescription.GetFormattedText()),
            new StringVar("TeaOfDiscourtesyDescription", ModelDb.Relic<TeaOfDiscourtesy>().DynamicDescription.GetFormattedText()),
        };

    /// <summary>
    /// The base event's gate, both clauses: acts 1 and 2 only, and every
    /// player holding the DEARER price -- 150, not 50, so the room is never
    /// offered as a shop whose expensive half nobody can reach.
    /// </summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex < 2)
        {
            return runState.Players.All((Player p) => p.Gold >= 150);
        }

        return false;
    }

    /// <summary>
    /// Three options, in the base event's order, under its names. The two
    /// paid teas lock independently on the OWNER's purse -- the gate asked
    /// about every player, this asks about the one standing here -- and the
    /// free cup is never locked.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();

        if ((decimal)Owner.Gold >= DynamicVars["BoneTeaCost"].BaseValue)
        {
            options.Add(new EventOption(this, BoneTea, InitialOptionKey("BONE_TEA"),
                HoverTipFactory.FromRelicExcludingItself<BoneTea>()));
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("BONE_TEA_LOCKED")));
        }

        if ((decimal)Owner.Gold >= DynamicVars["EmberTeaCost"].BaseValue)
        {
            options.Add(new EventOption(this, EmberTea, InitialOptionKey("EMBER_TEA"),
                HoverTipFactory.FromRelicExcludingItself<EmberTea>()));
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("EMBER_TEA_LOCKED")));
        }

        options.Add(new EventOption(this, TeaOfDiscourtesy, InitialOptionKey("TEA_OF_DISCOURTESY"),
            HoverTipFactory.FromRelicExcludingItself<TeaOfDiscourtesy>()));

        return options;
    }

    /// <summary>`BoneTea`: 50 spent, the relic obtained, the shared
    /// page.</summary>
    private async Task BoneTea()
    {
        await PlayerCmd.LoseGold(DynamicVars["BoneTeaCost"].BaseValue, Owner, GoldLossType.Spent);
        await RelicCmd.Obtain<BoneTea>(Owner);
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
    }

    /// <summary>`EmberTea`: 150 spent, the relic obtained, the same shared
    /// page.</summary>
    private async Task EmberTea()
    {
        await PlayerCmd.LoseGold(DynamicVars["EmberTeaCost"].BaseValue, Owner, GoldLossType.Spent);
        await RelicCmd.Obtain<EmberTea>(Owner);
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
    }

    /// <summary>`TeaOfDiscourtesy`: free, and its own page.</summary>
    private async Task TeaOfDiscourtesy()
    {
        await RelicCmd.Obtain<TeaOfDiscourtesy>(Owner);
        SetEventFinished(L10NLookup(PageKey("TEA_OF_DISCOURTESY.description")));
    }
}
