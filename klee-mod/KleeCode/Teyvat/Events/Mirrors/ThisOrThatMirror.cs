using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THIS OR THAT?, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/ThisOrThat.cs` and cross-checked against
/// the harvest (2 options: Plain, Ornate).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three canonical vars
/// (`HpLossVar(6)`, `GoldVar(0)`, and the `StringVar("Curse", ...)` that puts
/// Clumsy's own title into the description), the same
/// `Rng.NextInt(41, 69)` roll in `CalculateVars`, the same unblockable
/// unpowered 6 then `GainGold` on the first option, and the same
/// `RelicFactory.PullNextRelicFromFront` then `AddCurseToDeck&lt;Clumsy&gt;` on the
/// second, in that order.
///
/// THE GOLD IS ROLLED OFF THE EVENT'S OWN `Rng`, NOT THE RUN'S, which is
/// `EventModel.BeginEvent`'s doing: `Rng` is seeded from the run seed plus
/// `StringHelper.GetDeterministicHashCode(Id.Entry)`. A DRESSED entry hashes
/// differently from the base one, so a dressed This or That rolls a different
/// number in the 41-68 band than the base event would have on the same seed.
/// That is a per-event stream the engine explicitly says it does not track
/// ("we don't need to keep track of a given event's RNG state once it's over",
/// `EventModel.cs`), so it moves no later roll and no map -- but it does mean
/// a fixed-seed replay across the arm's switch shows a different gold number,
/// and the calibration deploys keep the arm off for exactly that class of
/// reason.
///
/// The StringVar names the CURSE, and the curse is the base game's Clumsy with
/// the base game's global loc row -- the same thing the Chosen Cheese is in
/// the cheese cellar. A dressing renames neither.
/// </summary>
public abstract class ThisOrThatMirror : TeyvatEventMirror
{
    /// <summary>`ThisOrThat.cs:16-21`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new HpLossVar(6m),
            new GoldVar(0),
            new StringVar("Curse", ModelDb.Card<Clumsy>().Title),
        };

    /// <summary>The base event's roll, on the base event's bounds
    /// (`NextInt` is exclusive at the top, so 41-68).</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue = Rng.NextInt(41, 69);
    }

    /// <summary>
    /// Two options, in the base event's order, under its names, with the
    /// damage annotation on the first and the Clumsy hover tip on the second.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Plain, InitialOptionKey("PLAIN"))
                .ThatDoesDamage(DynamicVars.HpLoss.IntValue),
            new EventOption(this, Ornate, InitialOptionKey("ORNATE"),
                HoverTipFactory.FromCardWithCardHoverTips<Clumsy>()),
        };

    /// <summary>`Plain`: the HP loss, then the gold.</summary>
    private async Task Plain()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.HpLoss.IntValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null, null);
        await PlayerCmd.GainGold(DynamicVars.Gold.IntValue, Owner);
        SetEventFinished(L10NLookup(PageKey("PLAIN.description")));
    }

    /// <summary>
    /// `Ornate`: the relic off the FRONT of the run's relic queue -- not a
    /// fresh roll, which is what makes it the same relic the base event would
    /// have granted -- then the curse.
    /// </summary>
    private async Task Ornate()
    {
        RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        await CardPileCmd.AddCurseToDeck<Clumsy>(Owner);
        SetEventFinished(L10NLookup(PageKey("ORNATE.description")));
    }
}
