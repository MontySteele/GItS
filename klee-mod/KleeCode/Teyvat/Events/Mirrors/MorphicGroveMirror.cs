using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// MORPHIC GROVE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/MorphicGrove.cs` and cross-checked
/// against the harvest (2 options: Group, Loner).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `IsShared`, the same
/// `MaxHpVar(5)`, the same gate (every player holding 100 gold AND two
/// transformable cards), the same static Transform hover tip on the first
/// option, the same `GoldLossType.Stolen` on the whole purse, and the same
/// two transforms off the EVENT's rng.
///
/// THE GOLD IS STOLEN AND NOT SPENT, which is a real distinction in 0.111.0
/// and not a label: `GoldLossType` is what a relic that reacts to losing gold
/// reads. The base event says Stolen; so does this.
///
/// `Owner.Gold` IS THE AMOUNT, not the gate's 100 -- the option empties the
/// purse whatever is in it, which is what the harvest's "Lose ALL of your
/// Gold" means.
/// </summary>
public abstract class MorphicGroveMirror : TeyvatEventMirror
{
    /// <summary>The base event's own.</summary>
    public override bool IsShared => true;

    /// <summary>`MorphicGrove.cs:22`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new MaxHpVar(5m) };

    /// <summary>
    /// The base event's gate, both clauses: 100 gold and two transformable
    /// cards on every player, so the Group option is never offered as a
    /// choice that cannot be paid for.
    /// </summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) =>
            p.Gold >= 100 && p.Deck.Cards.Count((CardModel c) => c.IsTransformable) >= 2);

    /// <summary>Two options, in the base event's order, under its names, with
    /// the static Transform tip on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Group, InitialOptionKey("GROUP"),
                HoverTipFactory.Static(StaticHoverTip.Transform)),
            new EventOption(this, Loner, InitialOptionKey("LONER")),
        };

    /// <summary>`Loner`: the max HP, and nothing else.</summary>
    private async Task Loner()
    {
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars.MaxHp.BaseValue);
        SetEventFinished(L10NLookup(PageKey("LONER.description")));
    }

    /// <summary>`Group`: the whole purse, then two chosen cards transformed
    /// one after the other.</summary>
    private async Task Group()
    {
        await PlayerCmd.LoseGold(Owner.Gold, Owner, GoldLossType.Stolen);
        List<CardModel> cards = (await CardSelectCmd.FromDeckForTransformation(
            player: Owner, prefs: new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 2)))
            .ToList();
        foreach (CardModel card in cards)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }

        SetEventFinished(L10NLookup(PageKey("GROUP.description")));
    }
}
