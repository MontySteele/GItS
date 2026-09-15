using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE RELIC TRADER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/RelicTrader.cs` and cross-checked against
/// the harvest (3 options: Top, Middle, Bottom).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same six `StringVar`s, the same
/// two lazily-built lists -- three of the player's tradable relics, stably
/// shuffled on the event's `Rng`, against three pulled off the FRONT of the
/// run's relic queue -- the same not-act-1-and-five-tradable-relics gate, the
/// same three options built only as far as the owned list reaches, the same
/// paired hover tips (the relic going out, then the one coming in), and the
/// same remove-then-obtain-then-finish on each.
///
/// THE LISTS ARE LAZY AND CACHED ON PURPOSE. `OwnedRelics` and `NewRelics`
/// build once and are read again by `CalculateVars` and by `Trade`, so the
/// relic an option NAMES is the relic it trades. Re-rolling either in the
/// handler would show one relic and give another, and the `AssertMutable` on
/// each getter is the base event's guard that neither is built on a canonical
/// model.
///
/// THE FALLBACK OPTION'S KEY IS NOT THIS EVENT'S. When nothing tradable
/// survives, the base event adds `new EventOption(this, Done, "PROCEED")` --
/// a BARE key, not one under the event's entry, pointing at the shipped
/// game's shared `PROCEED` row. A dressing must not re-key it: prefixing it
/// with the dressed entry would ask for a row nobody writes, and writing one
/// would be a dressed copy of a word the whole game already shares. It is
/// kept verbatim, and the key-literal pin's table records that this literal
/// is deliberately not a dressed key.
/// </summary>
public abstract class RelicTraderMirror : TeyvatEventMirror
{
    /// <summary>The base event's own var key names.</summary>
    private const string TopRelicOwnedKey = "TopRelicOwned";

    private const string TopRelicNewKey = "TopRelicNew";

    private const string MiddleRelicOwnedKey = "MiddleRelicOwned";

    private const string MiddleRelicNewKey = "MiddleRelicNew";

    private const string BottomRelicOwnedKey = "BottomRelicOwned";

    private const string BottomRelicNewKey = "BottomRelicNew";

    private IReadOnlyList<RelicModel> _ownedRelics;

    private IReadOnlyList<RelicModel> _newRelics;

    /// <summary>`RelicTrader.cs:33-41`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar(TopRelicOwnedKey),
            new StringVar(TopRelicNewKey),
            new StringVar(MiddleRelicOwnedKey),
            new StringVar(MiddleRelicNewKey),
            new StringVar(BottomRelicOwnedKey),
            new StringVar(BottomRelicNewKey),
        };

    /// <summary>Three of the player's tradable relics, stably shuffled on the
    /// event's `Rng`. Built ONCE.</summary>
    private IReadOnlyList<RelicModel> OwnedRelics
    {
        get
        {
            AssertMutable();
            if (_ownedRelics == null)
            {
                _ownedRelics = GetValidRelics(Owner).ToList().StableShuffle(Rng).Take(3).ToList();
            }

            return _ownedRelics;
        }
    }

    /// <summary>Three relics off the FRONT of the run's queue -- not a fresh
    /// roll, so they are the relics the run would have given anyway. Built
    /// ONCE.</summary>
    private IReadOnlyList<RelicModel> NewRelics
    {
        get
        {
            AssertMutable();
            if (_newRelics == null)
            {
                RelicModel[] pulled = new RelicModel[3];
                for (int i = 0; i < pulled.Length; i++)
                {
                    pulled[i] = RelicFactory.PullNextRelicFromFront(Owner);
                }

                _newRelics = pulled;
            }

            return _newRelics;
        }
    }

    /// <summary>One option per owned relic, in the base event's order, and the
    /// shared `PROCEED` fallback when there are none.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();
        if (OwnedRelics.Count >= 1)
        {
            options.Add(new EventOption(this, Top, InitialOptionKey("TOP"), GetRelicHoverTips(0)));
        }

        if (OwnedRelics.Count >= 2)
        {
            options.Add(new EventOption(this, Middle, InitialOptionKey("MIDDLE"), GetRelicHoverTips(1)));
        }

        if (OwnedRelics.Count >= 3)
        {
            options.Add(new EventOption(this, Bottom, InitialOptionKey("BOTTOM"), GetRelicHoverTips(2)));
        }

        if (options.Count == 0)
        {
            // The shipped game's SHARED key, kept bare -- see the class comment.
            options.Add(new EventOption(this, Done, "PROCEED"));
        }

        return options;
    }

    /// <summary>The base event's gate: not act 1, and every player holding at
    /// least five tradable relics.</summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.CurrentActIndex == 0)
        {
            return false;
        }

        return runState.Players.All((Player p) => GetValidRelics(p).Count() >= 5);
    }

    private IEnumerable<RelicModel> GetValidRelics(Player player) =>
        player.Relics.Where((RelicModel r) => r.IsTradable);

    /// <summary>The base event's three guarded pairs: a slot's two names are
    /// written only when BOTH lists reach it.</summary>
    public override void CalculateVars()
    {
        if (OwnedRelics.Count > 0 && NewRelics.Count > 0)
        {
            ((StringVar)DynamicVars[TopRelicOwnedKey]).StringValue =
                OwnedRelics[0].Title.GetFormattedText();
            ((StringVar)DynamicVars[TopRelicNewKey]).StringValue =
                NewRelics[0].Title.GetFormattedText();
        }

        if (OwnedRelics.Count > 1 && NewRelics.Count > 1)
        {
            ((StringVar)DynamicVars[MiddleRelicOwnedKey]).StringValue =
                OwnedRelics[1].Title.GetFormattedText();
            ((StringVar)DynamicVars[MiddleRelicNewKey]).StringValue =
                NewRelics[1].Title.GetFormattedText();
        }

        if (OwnedRelics.Count > 2 && NewRelics.Count > 2)
        {
            ((StringVar)DynamicVars[BottomRelicOwnedKey]).StringValue =
                OwnedRelics[2].Title.GetFormattedText();
            ((StringVar)DynamicVars[BottomRelicNewKey]).StringValue =
                NewRelics[2].Title.GetFormattedText();
        }
    }

    private async Task Top() => await Trade(0);

    private async Task Middle() => await Trade(1);

    private async Task Bottom() => await Trade(2);

    /// <summary>The trade: the owned relic out, the queued one in, then the
    /// shared DONE page.</summary>
    private async Task Trade(int index)
    {
        await RelicCmd.Remove(OwnedRelics[index]);
        await RelicCmd.Obtain(NewRelics[index].ToMutable(), Owner);
        await Done();
    }

    private Task Done()
    {
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
        return Task.CompletedTask;
    }

    /// <summary>The relic going OUT's tips, then the one coming IN's, and
    /// nothing at all when either list is short.</summary>
    private IEnumerable<IHoverTip> GetRelicHoverTips(int index)
    {
        if (OwnedRelics.Count <= index || NewRelics.Count <= index)
        {
            return Array.Empty<IHoverTip>();
        }

        List<IHoverTip> tips = new List<IHoverTip>();
        tips.AddRange(OwnedRelics.ElementAt(index).HoverTips);
        tips.AddRange(NewRelics.ElementAt(index).HoverTips);
        return tips;
    }
}
