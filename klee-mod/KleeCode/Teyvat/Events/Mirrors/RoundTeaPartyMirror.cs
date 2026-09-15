using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
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
/// THE ROUND TEA PARTY, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/RoundTeaParty.cs` and cross-checked
/// against the harvest (2 options: Enjoy Tea, Pick Fight).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `DamageVar(11, Unblockable |
/// Unpowered)` and the `StringVar` that puts Royal Poison's own title into the
/// description, the same every-player-at-12-HP-or-more gate, Royal Poison's
/// relic hover tip on the first option and the damage annotation on the
/// second, the same obtain-then-heal-to-full on Enjoy Tea, and the same second
/// page on Pick Fight whose one option takes the 11 and then the relic off the
/// FRONT of the run's queue.
///
/// THE HEAL IS COMPUTED AFTER THE RELIC LANDS. `targetCreature` is captured
/// first, the relic is obtained, and only THEN is `MaxHp - CurrentHp` read --
/// so a relic that moves the maximum is already in the number. The order is
/// the base event's and is kept exactly, because swapping the two lines is
/// invisible in a diff and changes how much HP the option gives.
///
/// `ThatWontSaveToChoiceHistory` ON THE SECOND PAGE'S OPTION is the base
/// event's own: Continue Fight is not a choice the run history should record,
/// because Pick Fight already recorded it. Dropping it would put a phantom row
/// in every run that took the second option.
///
/// THE GATE IS A REAL GATE, not a flavour note: `RoomSet.EnsureNextEventIsValid`
/// consults the BASE event's `IsAllowed` before the substitution happens, so a
/// mirror whose gate differed would be offered in runs the base event refuses.
/// </summary>
public abstract class RoundTeaPartyMirror : TeyvatEventMirror
{
    /// <summary>`RoundTeaParty.cs:19-23`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(11m, ValueProp.Unblockable | ValueProp.Unpowered),
            new StringVar("Relic", ModelDb.Relic<RoyalPoison>().Title.GetFormattedText()),
        };

    /// <summary>The base event's gate: every player at 12 HP or more.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Creature.CurrentHp >= 12);

    /// <summary>Two options, in the base event's order, with Royal Poison's
    /// relic hover tip on the first and the damage annotation on the
    /// second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, EnjoyTea, InitialOptionKey("ENJOY_TEA"),
                HoverTipFactory.FromRelic<RoyalPoison>()),
            new EventOption(this, PickFight, InitialOptionKey("PICK_FIGHT"))
                .ThatDoesDamage(DynamicVars.Damage.BaseValue),
        };

    /// <summary>`EnjoyTea`: the relic, THEN the heal to full -- so the heal
    /// fills whatever maximum the relic left behind.</summary>
    private async Task EnjoyTea()
    {
        Creature targetCreature = Owner.Creature;
        await RelicCmd.Obtain<RoyalPoison>(Owner);
        await CreatureCmd.Heal(targetCreature, targetCreature.MaxHp - targetCreature.CurrentHp);
        SetEventFinished(L10NLookup(PageKey("ENJOY_TEA.description")));
    }

    /// <summary>`PickFight`: the second page, with one option that is kept out
    /// of the choice history.</summary>
    private Task PickFight()
    {
        SetEventState(L10NLookup(PageKey("PICK_FIGHT.description")), new List<EventOption>
        {
            new EventOption(this, ContinueFight, PageKey("PICK_FIGHT.options.CONTINUE_FIGHT"))
                .ThatWontSaveToChoiceHistory(),
        });
        return Task.CompletedTask;
    }

    /// <summary>`ContinueFight`: the 11, then the relic off the FRONT of the
    /// run's relic queue -- not a fresh roll, so it is the relic the base event
    /// would have granted.</summary>
    private async Task ContinueFight()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.Damage,
            null, null, null);
        await RelicCmd.Obtain(RelicFactory.PullNextRelicFromFront(Owner).ToMutable(), Owner);
        SetEventFinished(L10NLookup(PageKey("CONTINUE_FIGHT.description")));
    }
}
