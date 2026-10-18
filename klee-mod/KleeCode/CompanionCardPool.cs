using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// THE SHARED COMPANIONS' OWN POOL, with the base game's Colorless look
/// (legacy review pick 4, [USER] 2026-10-18: "Shared companions move to their
/// own pool with a neutral frame, out of Klee's"). Until this, every Universal
/// sat in <see cref="KleeCardPool"/> and so wore Klee's red frame and
/// Ironclad's energy orb in every character's run, because
/// <c>CardModel.Pool</c> supplies the frame, the orb and the deck-entry colour.
///
/// MEMBERSHIP is the generated <c>PrototypeRoster.For("companion")</c>: every
/// Companion row with no <c>personal_pool:</c> that no kit claims
/// (<c>tier0.content.loader.is_shared_companion_row</c>). Kit-own companions
/// stay in their kit's pool and frame -- Klee's three
/// (<c>C.KLEE_OWN_COMPANION_IDS</c>), Gorou's four in Kokomi's
/// (<c>C.KOKOMI_OWN_COMPANION_IDS</c>), Varka's Knights (his PersonalPool).
///
/// VISIBLE TO THE ENGINE through BaseLib: a <see cref="CustomCardPoolModel"/>
/// whose <see cref="IsShared"/> is true registers itself from its constructor
/// with <c>ModelDbSharedCardPoolsPatch</c>, a postfix on
/// <c>ModelDb.AllSharedCardPools</c>. The constructor runs in
/// <c>ModelDb.Init</c>, after mods load and before <c>ModelDb.Preload</c> makes
/// the first (cached) <c>AllCardPools</c> read, so <c>CardModel.Pool</c>
/// resolves here (a poolless card throws "You monster!" on draw).
///
/// THE LOOK IS COLORLESS'S, by name: <c>card_frame_colorless</c>, the
/// <c>colorless</c> energy orb, its grey deck-entry colour. A frame path other
/// than <c>card_frame_red</c> makes BaseLib's HSV material patch stand aside,
/// so the base material loads as it does for the base Colorless cards.
///
/// NOT <see cref="IsColorless"/>. The base game reads that flag as a rule, not
/// a look: Heirloom Hammer copies only a Colorless card in hand. Companions
/// were never Colorless to it and this move changes their frame, not their
/// rules. Shop pricing reads <c>card.Pool is ColorlessCardPool</c> (a type
/// test), so the companion slots' prices do not move either.
///
/// THE OFFER (<see cref="FilterThroughEpochs"/>) is the companion roster
/// (<see cref="CompanionPool.All"/>). Nothing rolls rewards from a shared pool
/// unless it names it, so this reaches two places only: the card library's
/// unlocked set, and a TRANSFORM of a companion, which the base game draws from
/// the original card's pool -- so a companion now transforms into another
/// companion, as a Colorless card transforms into a Colorless card (it used to
/// become a card of Klee's pool, in anyone's run).
/// </summary>
public sealed class CompanionCardPool : CustomCardPoolModel
{
    public override string Title => "companion";

    public override bool IsShared => true;

    public override string EnergyColorName => "colorless";

    public override string CardFrameMaterialPath => "card_frame_colorless";

    // ColorlessCardPool's own deck-entry grey.
    public override Color DeckEntryCardColor => new Color("A3A3A3FF");

    public override bool IsColorless => false;

    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
        return CompanionPool.All;
    }

    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("companion").Distinct().ToArray();
}
