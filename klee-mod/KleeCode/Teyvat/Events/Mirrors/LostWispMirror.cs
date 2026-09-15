using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// LOST WISP, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/LostWisp.cs` and cross-checked against
/// the harvest (2 options: Claim, Search).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three canonical vars, the
/// same TWO hover tips on the first option -- the Lost Wisp relic's and
/// Decay's, concatenated in that order -- the same `Rng.NextInt(-15, 16)` swing
/// on the base 60 gold, the same curse-then-relic on Claim, and the same flat
/// gold on Search.
///
/// THE EVENT AND THE RELIC SHARE A NAME, and the mirror says which is which
/// the way the decompile does: the relic is
/// `MegaCrit.Sts2.Core.Models.Relics.LostWisp`, spelled out in full at each
/// use, because `LostWisp` unqualified in this file would bind to nothing
/// useful and in the base event's own file binds to the event.
///
/// THE GOLD IS ROLLED OFF THE EVENT'S OWN `Rng`, which is seeded from the run
/// seed plus `GetDeterministicHashCode(Id.Entry)` -- and a DRESSED entry hashes
/// differently, so a dressed Lost Wisp rolls a different number in the 45-75
/// band than the base event would on the same seed. `EventModel` says it does
/// not track a finished event's RNG state, so this moves no later roll and no
/// map; it is the same per-event divergence `ThisOrThatMirror` documents, and
/// the reason the calibration deploys keep the arm off.
///
/// THE ROLL IS `+=`, NOT `=`. `CalculateVars` adds the swing to the canonical
/// 60 rather than replacing it, so the band is 45 to 75 (`NextInt` is exclusive
/// at the top).
/// </summary>
public abstract class LostWispMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names and numbers.</summary>
    private const string RelicKey = "Relic";

    private const string CurseKey = "Curse";

    // The 60 and the 15 are inlined at their use sites, as every other
    // mirror's base-game numbers are: they are the shipped game's values, and
    // a named C# constant is one `lint_constant_parity` expects the sim to
    // have a counterpart for.

    /// <summary>`LostWisp.cs:21-26`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(60),
            new StringVar(RelicKey,
                ModelDb.Relic<MegaCrit.Sts2.Core.Models.Relics.LostWisp>().Title.GetFormattedText()),
            new StringVar(CurseKey, ModelDb.Card<Decay>().Title),
        };

    /// <summary>Two options, in the base event's order. The first carries the
    /// relic's tips and Decay's, in that order, as one list.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<IHoverTip> claimTips = new List<IHoverTip>();
        claimTips.AddRange(
            HoverTipFactory.FromRelic<MegaCrit.Sts2.Core.Models.Relics.LostWisp>());
        claimTips.AddRange(HoverTipFactory.FromCardWithCardHoverTips<Decay>());

        return new List<EventOption>
        {
            new EventOption(this, Claim, InitialOptionKey("CLAIM"), claimTips.ToArray()),
            new EventOption(this, Search, InitialOptionKey("SEARCH")),
        };
    }

    /// <summary>The base event's swing, ADDED to the canonical 60: 45-75.</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue += (decimal)Rng.NextInt(-15, 16);
    }

    /// <summary>`Claim`: the curse FIRST, then the relic.</summary>
    private async Task Claim()
    {
        await CardPileCmd.AddCursesToDeck(
            new List<CardModel> { ModelDb.Card<Decay>() }, Owner);
        await RelicCmd.Obtain<MegaCrit.Sts2.Core.Models.Relics.LostWisp>(Owner);
        SetEventFinished(L10NLookup(PageKey("CLAIM.description")));
    }

    /// <summary>`Search`: the rolled gold.</summary>
    private async Task Search()
    {
        await PlayerCmd.GainGold(DynamicVars.Gold.IntValue, Owner);
        SetEventFinished(L10NLookup(PageKey("SEARCH.description")));
    }
}
