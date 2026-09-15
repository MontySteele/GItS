using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
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
/// WATERLOGGED SCRIPTORIUM, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/WaterloggedScriptorium.cs` and
/// cross-checked against the harvest (3 options: Bloody Ink, Tentacle Quill,
/// Prickly Sponge).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same four vars (`MaxHpVar(6)`,
/// the 55 and 99 prices, `CardsVar(2)`), the same 55-gold gate, the same two
/// independent locks, the same Steady hover tip on both paid options, and the
/// same enchant VFX on each card enchanted.
///
/// THE SPONGE'S SELECTOR TAKES TWO AND ENCHANTS BY ONE, which is the base
/// event's own shape and reads oddly enough to be worth stating: the prefs
/// say `DynamicVars.Cards` (2) cards may be picked, the `amount` argument to
/// `FromDeckForEnchantment` is 1, and the loop applies `Enchant<Steady>(card,
/// 1)` to each. Two cards, one Steady apiece -- which is what the face's
/// "Enchant 2 cards with Steady" says.
///
/// THE QUILL PRICE IS THE UNNAMED `GoldVar` AND THE SPONGE'S IS THE NAMED
/// ONE. `DynamicVars.Gold` is the 55 and `DynamicVars["PricklySpongeGold"]`
/// is the 99; the gate reads the first and so does the quill's lock, which is
/// why the same `GoldVar(55)` is both the spawn requirement and a price.
/// </summary>
public abstract class WaterloggedScriptoriumMirror : TeyvatEventMirror
{
    /// <summary>`WaterloggedScriptorium.cs:26-32`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new MaxHpVar(6m),
            new GoldVar(55),
            new GoldVar("PricklySpongeGold", 99),
            new CardsVar(2),
        };

    /// <summary>The base event's gate: every player holding 55.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Gold >= 55);

    /// <summary>
    /// Three options, in the base event's order, under its names: the free
    /// one first, then the two paid ones, each locked independently on the
    /// OWNER's purse.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>
        {
            new EventOption(this, BloodyInk, InitialOptionKey("BLOODY_INK")),
        };

        if (Owner.Gold >= DynamicVars.Gold.IntValue)
        {
            options.Add(new EventOption(this, TentacleQuill, InitialOptionKey("TENTACLE_QUILL"),
                HoverTipFactory.FromEnchantment<Steady>()));
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("TENTACLE_QUILL_LOCKED")));
        }

        if (Owner.Gold >= DynamicVars["PricklySpongeGold"].IntValue)
        {
            options.Add(new EventOption(this, PricklySponge, InitialOptionKey("PRICKLY_SPONGE"),
                HoverTipFactory.FromEnchantment<Steady>()));
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("PRICKLY_SPONGE_LOCKED")));
        }

        return options;
    }

    /// <summary>`PricklySponge`: 99 spent, then up to `Cards` cards each
    /// enchanted with one Steady.</summary>
    private async Task PricklySponge()
    {
        await PlayerCmd.LoseGold(DynamicVars["PricklySpongeGold"].BaseValue, Owner, GoldLossType.Spent);
        CardSelectorPrefs prefs = new CardSelectorPrefs(
            CardSelectorPrefs.EnchantSelectionPrompt, DynamicVars.Cards.IntValue);
        Steady enchantment = ModelDb.Enchantment<Steady>();
        foreach (CardModel card in await CardSelectCmd.FromDeckForEnchantment(Owner, enchantment, 1, prefs))
        {
            CardCmd.Enchant<Steady>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("PRICKLY_SPONGE.description")));
    }

    /// <summary>`TentacleQuill`: 55 spent, then one card enchanted with one
    /// Steady.</summary>
    private async Task TentacleQuill()
    {
        await PlayerCmd.LoseGold(DynamicVars.Gold.BaseValue, Owner, GoldLossType.Spent);
        CardModel card = (await CardSelectCmd.FromDeckForEnchantment(
            player: Owner, enchantment: ModelDb.Enchantment<Steady>(), amount: 1,
            prefs: new CardSelectorPrefs(CardSelectorPrefs.EnchantSelectionPrompt, 1)))
            .FirstOrDefault();
        if (card != null)
        {
            CardCmd.Enchant<Steady>(card, 1m);
            NCardEnchantVfx vfx = NCardEnchantVfx.Create(card);
            if (vfx != null)
            {
                NRun.Instance?.GlobalUi.CardPreviewContainer.AddChildSafely(vfx);
            }
        }

        SetEventFinished(L10NLookup(PageKey("TENTACLE_QUILL.description")));
    }

    /// <summary>`BloodyInk`: the free 6 max HP.</summary>
    private async Task BloodyInk()
    {
        await CreatureCmd.GainMaxHp(Owner.Creature, DynamicVars.MaxHp.BaseValue);
        SetEventFinished(L10NLookup(PageKey("BLOODY_INK.description")));
    }
}
