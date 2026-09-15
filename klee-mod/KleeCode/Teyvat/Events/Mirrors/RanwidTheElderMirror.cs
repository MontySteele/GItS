using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// RANWID THE ELDER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/RanwidTheElder.cs` and cross-checked
/// against the harvest (3 options: the potion, the gold, the relic).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three vars, the same potions
/// lock while the page is open, the same FOUR-clause gate (not act 1; every
/// player holding a tradable relic, 100 gold, and a potion), the same
/// `_LOCKED` twins on the first and third options, the same
/// discard-then-one-relic, lose-100-then-one-relic, and
/// remove-then-TWO-relics, each off the FRONT of the run's relic queue.
///
/// THIS IS THE ONE EVENT THAT BUILDS A `LocString` BY HAND, and it is the one
/// clause a dressed mirror could not copy verbatim. The base event writes
/// `new LocString("events", "RANWID_THE_ELDER.pages.INITIAL.options.POTION.title")`
/// -- a hardcoded key, not `InitialOptionKey` -- because the potion and relic
/// options carry a DYNAMIC title (`ThatHasDynamicTitle`) and so need the title
/// and description LocStrings handed to the `EventOption` constructor rather
/// than looked up from the key alone. A mirror that kept those literals would
/// read the BASE event's global rows and print the base game's words on a
/// dressed page. So the two pairs are rebuilt off `Id.Entry` through
/// <see cref="OptionText"/>, which is the same string with the dressed entry
/// in front -- the one place in this surface where a key had to be
/// re-derived rather than inherited.
///
/// THE OFFERED ITEM IS ROLLED AT OPTION-BUILD TIME, like The Stone of All
/// Time's potion and for the same reason: the option has to NAME what it will
/// take. That is why the potions lock exists, and why the relic is captured in
/// the closure rather than re-rolled in the handler.
///
/// THE HARVEST STRIPS THE THIRD OPTION'S NAME. Both Glory and Hive faces note
/// it: the wiki row reads `[Give ]` with the item template stripped, so the
/// face writes the option's words itself and the mechanics line beneath says
/// so. Nothing mechanical is affected -- the option is the relic trade either
/// way.
/// </summary>
public abstract class RanwidTheElderMirror : TeyvatEventMirror
{
    /// <summary>The base event's own var key names.</summary>
    private const string PotionKey = "Potion";

    private const string RelicKey = "Relic";

    /// <summary>
    /// One of THIS dressing's option-text rows, as a `LocString` the
    /// `EventOption` constructor can be handed directly.
    ///
    /// The base event hardcodes these four keys under its own entry; a mirror
    /// must build them under the DRESSED entry or the page prints the base
    /// game's words. `Id.Entry` is the dressed name for the same reason every
    /// other key in this surface re-keys for free.
    /// </summary>
    private LocString OptionText(string option, string suffix) =>
        new LocString("events", Id.Entry + ".pages.INITIAL.options." + option + "." + suffix);

    /// <summary>`RanwidTheElder.cs:32-37`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(100),
            new StringVar(PotionKey, PotionKey),
            new StringVar(RelicKey, RelicKey),
        };

    /// <summary>The base event's lock: the belt cannot be touched while an
    /// option names a potion off it.</summary>
    protected override Task BeforeEventStarted(bool isPreFinished)
    {
        Owner.CanUseOrRemovePotions = false;
        return Task.CompletedTask;
    }

    /// <summary>And the base event's unlock.</summary>
    protected override void OnEventFinished()
    {
        Owner.CanUseOrRemovePotions = true;
    }

    /// <summary>The base event's gate, all four clauses in its order.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex == 0)
        {
            return false;
        }

        if (runState.Players.Any((Player p) => !GetValidRelics(p).Any()))
        {
            return false;
        }

        if (runState.Players.Any((Player p) => p.Gold < 100))
        {
            return false;
        }

        if (runState.Players.Any((Player p) => !p.Potions.Any()))
        {
            return false;
        }

        return true;
    }

    /// <summary>The base event's own: only a TRADABLE relic can be given.</summary>
    private IEnumerable<RelicModel> GetValidRelics(Player player) =>
        player.Relics.Where((RelicModel r) => r.IsTradable);

    /// <summary>Three options, in the base event's order. The first and third
    /// name the item they will take and fall back to a `_LOCKED` twin when
    /// there is none.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();

        PotionModel potion = Rng.NextItem(Owner.Potions);
        if (potion != null)
        {
            ((StringVar)DynamicVars[PotionKey]).StringValue = potion.Title.GetFormattedText();
            options.Add(new EventOption(
                this, async delegate { await GivePotion(potion); },
                OptionText("POTION", "title"), OptionText("POTION", "description"),
                InitialOptionKey("POTION"), potion.HoverTips).ThatHasDynamicTitle());
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("POTION_LOCKED")));
        }

        options.Add(new EventOption(this, GiveGold, InitialOptionKey("GOLD")));

        RelicModel relic = Rng.NextItem(Owner.Relics.Where((RelicModel r) => r.IsTradable));
        if (relic != null)
        {
            ((StringVar)DynamicVars[RelicKey]).StringValue = relic.Title.GetFormattedText();
            options.Add(new EventOption(
                this, async delegate { await GiveRelic(relic); },
                OptionText("RELIC", "title"), OptionText("RELIC", "description"),
                InitialOptionKey("RELIC"), relic.HoverTips).ThatHasDynamicTitle());
        }
        else
        {
            options.Add(new EventOption(this, null, InitialOptionKey("RELIC_LOCKED")));
        }

        return options;
    }

    /// <summary>`GivePotion`: the named potion out, one relic off the front of
    /// the queue in.</summary>
    private async Task GivePotion(PotionModel potion)
    {
        await PotionCmd.Discard(potion);
        RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        SetEventFinished(L10NLookup(PageKey("POTION.description")));
    }

    /// <summary>`GiveGold`: the 100 spent, one relic in.</summary>
    private async Task GiveGold()
    {
        await PlayerCmd.LoseGold(DynamicVars.Gold.IntValue, Owner, GoldLossType.Spent);
        RelicModel relic = RelicFactory.PullNextRelicFromFront(Owner).ToMutable();
        await RelicCmd.Obtain(relic, Owner);
        SetEventFinished(L10NLookup(PageKey("GOLD.description")));
    }

    /// <summary>`GiveRelic`: the named relic out, TWO off the front in.</summary>
    private async Task GiveRelic(RelicModel relic)
    {
        await RelicCmd.Remove(relic);
        for (int i = 0; i < 2; i++)
        {
            await RelicCmd.Obtain(RelicFactory.PullNextRelicFromFront(Owner).ToMutable(), Owner);
        }

        SetEventFinished(L10NLookup(PageKey("RELIC.description")));
    }
}
