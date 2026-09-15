using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// UNREST SITE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/UnrestSite.cs` and cross-checked against
/// the harvest (2 options: Rest, Kill).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two vars, the same 70%-HP
/// gate, the same Poor Sleep card hover tip on the first option and
/// `.ThatDecreasesMaxHp` on the second, the same heal-to-full-then-curse, and
/// the same max-HP-then-relic-off-the-front.
///
/// THE HEAL IS COMPUTED IN `CalculateVars`, not in the option, which is what
/// makes the page able to PRINT it: `MaxHp - CurrentHp` is resolved when the
/// room is prepared, so the dressing's "Heal to full HP" reads as a number
/// before the player commits. Moving it into `Rest` would have left the
/// printed value zero.
///
/// `.ThatDecreasesMaxHp` AND NOT `.ThatDoesDamage`, because the Kill branch
/// takes MAX HP: the two annotations drive different warnings and the base
/// event chose this one.
/// </summary>
public abstract class UnrestSiteMirror : TeyvatEventMirror
{
    /// <summary>`UnrestSite.cs:20-24`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new HealVar(0m),
            new DynamicVar("MaxHpLoss", 8m),
        };

    /// <summary>The base event's gate: every player at 70% of max HP or
    /// below -- a rest site nobody needs is a room the base game declines to
    /// offer.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) =>
            (decimal)p.Creature.CurrentHp <= (decimal)p.Creature.MaxHp * 0.70m);

    /// <summary>Two options, in the base event's order, under its names.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Rest, InitialOptionKey("REST"),
                HoverTipFactory.FromCardWithCardHoverTips<PoorSleep>()),
            new EventOption(this, Kill, InitialOptionKey("KILL"))
                .ThatDecreasesMaxHp(DynamicVars["MaxHpLoss"].BaseValue),
        };

    /// <summary>The base event's heal: the whole missing bar.</summary>
    public override void CalculateVars()
    {
        DynamicVars.Heal.BaseValue = Owner.Creature.MaxHp - Owner.Creature.CurrentHp;
    }

    /// <summary>`Rest`: healed to full, and Poor Sleep into the deck.</summary>
    private async Task Rest()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars.Heal.BaseValue);
        await CardPileCmd.AddCursesToDeck(new List<CardModel> { ModelDb.Card<PoorSleep>() }, Owner);
        SetEventFinished(L10NLookup(PageKey("REST.description")));
    }

    /// <summary>`Kill`: 8 max HP, then the relic off the front of the run's
    /// queue -- the same relic the base event would have granted.</summary>
    private async Task Kill()
    {
        await CreatureCmd.LoseMaxHp(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            DynamicVars["MaxHpLoss"].BaseValue, isFromCard: false);
        RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        SetEventFinished(L10NLookup(PageKey("KILL.description")));
    }
}
