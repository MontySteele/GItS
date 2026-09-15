using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE SUNKEN STATUE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SunkenStatue.cs` and cross-checked
/// against the harvest (2 options: Grab the Sword, Dive into the Water).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three vars (the Sword of
/// Stone's title, `GoldVar(111)`, a 7 HP loss), no act gate, the same
/// `Rng.NextInt(-10, 11)` jitter -- the 101-121 band the face prints -- the
/// same relic hover tip and damage annotation, and the same
/// GOLD-THEN-DAMAGE order on the dive.
///
/// THE ORDER ON THE DIVE IS THE BASE EVENT'S AND IS NOT THE OBVIOUS ONE. The
/// gold lands BEFORE the 7 unblockable unpowered damage, so a player the dive
/// kills has already banked the purse. That is the opposite of the cheese
/// cellar's damage-then-relic and of Whispering Hollow's transform-then-
/// damage; each is its own event's order and none of the three is tidied
/// toward the others.
///
/// THE SWORD IS THE BASE GAME'S RELIC with the base game's global rows, like
/// every other named grant in this surface.
/// </summary>
public abstract class SunkenStatueMirror : TeyvatEventMirror
{
    /// <summary>`SunkenStatue.cs:22-27`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("Relic", ModelDb.Relic<SwordOfStone>().Title.GetFormattedText()),
            new GoldVar(111),
            new DynamicVar("HpLoss", 7m),
        };

    /// <summary>The base event's roll: -10 to +10 on the 111 (`NextInt` is
    /// exclusive at the top).</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue += (decimal)Rng.NextInt(-10, 11);
    }

    /// <summary>Two options, in the base event's order, under its names, with
    /// the relic's tip on the first and the damage annotation on the
    /// second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, GrabSword, InitialOptionKey("GRAB_SWORD"),
                HoverTipFactory.FromRelic<SwordOfStone>()),
            new EventOption(this, DiveIntoWater, InitialOptionKey("DIVE_INTO_WATER"))
                .ThatDoesDamage(DynamicVars["HpLoss"].BaseValue),
        };

    /// <summary>`GrabSword`: the named relic, and nothing else.</summary>
    private async Task GrabSword()
    {
        await RelicCmd.Obtain<SwordOfStone>(Owner);
        SetEventFinished(L10NLookup(PageKey("GRAB_SWORD.description")));
    }

    /// <summary>`DiveIntoWater`: the gold FIRST, then the damage.</summary>
    private async Task DiveIntoWater()
    {
        await PlayerCmd.GainGold(DynamicVars.Gold.BaseValue, Owner);
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars["HpLoss"].BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null, null);
        SetEventFinished(L10NLookup(PageKey("DIVE_INTO_WATER.description")));
    }
}
