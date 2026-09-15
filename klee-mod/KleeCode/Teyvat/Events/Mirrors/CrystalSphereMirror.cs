using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Events.Custom.CrystalSphereEvent;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// CRYSTAL SPHERE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/CrystalSphere.cs` and cross-checked
/// against the harvest (2 options: Uncover Future, Payment Plan).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same four vars, the same
/// `IsDeterministic => false`, the same two-part gate (every player at 100
/// gold or more, AND act 2 or later), the same `Rng.NextInt(1, 50)` added to
/// the 50-gold base cost, Debt's card hover tip on the second option, and the
/// same MINIGAME on both -- three divinations after paying, six after taking
/// the curse.
///
/// BOTH OPTIONS END ON THE SAME PAGE. `pages.FINISH.description` is the only
/// non-INITIAL key this event has and Uncover Future and Payment Plan both
/// land on it, so the mirror's spec says in `page_source` which face line
/// supplies it -- the first, as Tea Master's `DONE` takes Bone Tea's.
///
/// THE MINIGAME IS THE BASE GAME'S, CONSTRUCTED NOT COPIED.
/// `CrystalSphereMinigame` is a public class in
/// `MegaCrit.Sts2.Core.Events.Custom.CrystalSphereEvent` taking
/// `(Player, Rng, int divinationCount)`, so the mirror hands it the same three
/// arguments the base event does and re-implements none of it. Its own text
/// belongs to the base game's `events` table and is NOT dressed: a dressing
/// writes the event's pages, and the minigame is a screen.
///
/// `IsDeterministic => false` IS WHY THE ROLL HERE IS NOT THE ThisOrThat
/// CAVEAT. The event already tells the engine it does not replay identically,
/// so a dressed entry hashing to a different `Rng` seed changes nothing the
/// engine was promising.
/// </summary>
public abstract class CrystalSphereMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names and numbers.</summary>
    private const string UncoverFutureCostKey = "UncoverFutureCost";

    private const string UncoverFutureProphesizeKey = "UncoverFutureProphesizeCount";

    private const string PaymentPlanKey = "PaymentPlanCount";

    // The base event's five NUMBERS are inlined at their use sites rather
    // than named, which is this directory's standing choice (This or That's
    // 41-69 roll, Punch Off's 91-99). A mirror's numbers are the shipped
    // game's, not the sim's, and `lint_constant_parity` reads a named C#
    // constant as one the sim should have a counterpart for.

    /// <summary>The base event's own: this event does not replay
    /// identically.</summary>
    public override bool IsDeterministic => false;

    /// <summary>`CrystalSphere.cs:36-42`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar(UncoverFutureCostKey, 50m),
            new DynamicVar(UncoverFutureProphesizeKey, 3m),
            new DynamicVar(PaymentPlanKey, 6m),
            new StringVar("CurseTitle", ModelDb.Card<Debt>().Title),
        };

    /// <summary>The base event's swing, ADDED to the 50: 51-99 (`NextInt` is
    /// exclusive at the top).</summary>
    public override void CalculateVars()
    {
        DynamicVars[UncoverFutureCostKey].BaseValue +=
            (decimal)Rng.NextInt(1, 50);
    }

    /// <summary>The base event's gate, both halves: 100 gold on every player,
    /// and act 2 or later.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.Players.All((Player p) => p.Gold >= 100))
        {
            return runState.CurrentActIndex > 0;
        }

        return false;
    }

    /// <summary>Two options, in the base event's order, with Debt's card hover
    /// tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, UncoverFuture, InitialOptionKey("UNCOVER_FUTURE")),
            new EventOption(this, PaymentPlan, InitialOptionKey("PAYMENT_PLAN"),
                HoverTipFactory.FromCardWithCardHoverTips<Debt>()),
        };

    /// <summary>`UncoverFuture`: the rolled gold is SPENT, then three
    /// divinations.</summary>
    private async Task UncoverFuture()
    {
        await PlayerCmd.LoseGold(
            DynamicVars[UncoverFutureCostKey].BaseValue, Owner, GoldLossType.Spent);
        CrystalSphereMinigame minigame =
            new CrystalSphereMinigame(Owner, Rng, 3);
        await minigame.PlayMinigame();
        SetEventFinished(L10NLookup(PageKey("FINISH.description")));
    }

    /// <summary>`PaymentPlan`: one Debt instead of the gold, then six
    /// divinations.</summary>
    private async Task PaymentPlan()
    {
        await CardPileCmd.AddCurseToDeck<Debt>(Owner);
        CrystalSphereMinigame minigame = new CrystalSphereMinigame(Owner, Rng, 6);
        await minigame.PlayMinigame();
        SetEventFinished(L10NLookup(PageKey("FINISH.description")));
    }
}
