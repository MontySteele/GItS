using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Enchantments;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SPIRALING WHIRLPOOL, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SpiralingWhirlpool.cs` and cross-checked
/// against the harvest (2 options: Observe, Drink).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `HealVar` set to 33% of max
/// HP in `CalculateVars`, the same gate (every player holding a card `Spiral`
/// can take), the same enchantment hover tip on the first option, the same
/// predicate overload of the enchant selector, and the same enchant VFX.
///
/// THE HEAL IS A FRACTION AND IS COMPUTED IN `CalculateVars`, which is what
/// lets the page print it as a number; the option then spends `IntValue`,
/// which truncates, exactly as the base event does.
///
/// THE GATE AND THE SELECTOR ASK THE SAME QUESTION TWICE, which is the base
/// event's own belt and braces: `IsAllowed` refuses the room when nothing can
/// take Spiral, and the selector's predicate refuses the card anyway.
/// </summary>
public abstract class SpiralingWhirlpoolMirror : TeyvatEventMirror
{
    /// <summary>`SpiralingWhirlpool.cs:19`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new HealVar(0m) };

    /// <summary>The base event's roll-free computation: a third of max
    /// HP.</summary>
    public override void CalculateVars()
    {
        DynamicVars.Heal.BaseValue = (Owner != null) ? (decimal)Owner.Creature.MaxHp * 0.33m : 0m;
    }

    /// <summary>The base event's gate: every player holding a card Spiral can
    /// enchant.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Deck.Cards.Any(ModelDb.Enchantment<Spiral>().CanEnchant));

    /// <summary>Two options, in the base event's order, under its names, with
    /// Spiral's enchantment tip on the first.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ObserveTheSpiral, InitialOptionKey("OBSERVE"),
                HoverTipFactory.FromEnchantment<Spiral>()),
            new EventOption(this, Drink, InitialOptionKey("DRINK")),
        };

    /// <summary>`ObserveTheSpiral`: one Spiral onto a card that can take it,
    /// with the base event's enchant VFX.</summary>
    private async Task ObserveTheSpiral()
    {
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            Owner, ModelDb.Enchantment<Spiral>(), 1,
            (CardModel c) => ModelDb.Enchantment<Spiral>().CanEnchant(c),
            new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<Spiral>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("OBSERVE.description")));
    }

    /// <summary>`Drink`: the third of max HP, truncated.</summary>
    private async Task Drink()
    {
        await CreatureCmd.Heal(Owner.Creature, DynamicVars.Heal.IntValue);
        SetEventFinished(L10NLookup(PageKey("DRINK.description")));
    }
}
