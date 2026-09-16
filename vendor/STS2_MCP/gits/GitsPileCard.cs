// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-789`: A CARD IN A PILE AND THE SAME CARD IN HAND WERE TWO DIFFERENT
// CARDS.
//
// THE FIND (live-looks-8c, `#575`). An enchanted card sat in the draw pile
// reading *Gain 5 Block*, was drawn, and read *Gain 7 Block* in hand a turn
// later. Nothing had changed but the pile it was in. A reader planning a turn
// off the draw pile was planning off a face the card will never present.
//
// TWO CAUSES, ONE SITE. `BuildPileCardList` built its own row --
//
//     { name, cost, star_cost, description }
//
// -- "lightweight", where a hand row comes off `BuildCardInfo` and carries
// `id`, `type`, `rarity`, `is_upgraded`, `keywords` and (since `EB-181`)
// `enchantment`. So (1) the pile row carried no enchantment field at all, and
// (2) its `description` was `GetDescriptionForPile(<that pile>)` while the
// hand's is `GetDescriptionForPile(PileType.Hand)`, and only the hand face
// folds the enchantment's number into the printed sentence.
//
// The four piles feed `understudy/blindplay_faces.remember_deck` and
// `deck_elements`, so both defects rode into every deck list and every
// reachability read the page makes off a fight. `_deck_card` was already
// asking each pile row for `id` and `is_upgraded` -- fields no pile row has
// ever carried -- and silently falling back to the `+` on the title.
//
// WHAT THIS DOES. One row builder for every pile, going through the hand's own
// `BuildCardInfo`, so a pile face and a hand face are the same face by
// construction rather than by two lists of keys kept in step by hand.
//
// `description` IS THE HAND FACE, DELIBERATELY. It is the face the card will
// present when it is played, which is the only face a reader planning with it
// can use, and it is the one the acceptance asks for: pile and hand print one
// face. The pile-CONTEXTUAL text is not thrown away -- a card whose rule reads
// differently where it is sitting (*while this is in your discard pile ...*)
// keeps that sentence as `pile_description`, and the key is EMITTED ONLY WHEN
// THE TWO DIFFER, so an absent key is the positive statement "this card reads
// the same wherever it is" and no ordinary board grew.
//
// BACKWARD COMPATIBLE BY ADDITION. Every key the old row carried is still
// here, spelled the same and meaning the same thing bar the enchantment fold;
// everything else is new. A page older than this row reads `name`, `cost`,
// `star_cost` and `description` exactly as before.
//
// COSTS, STATED. A pile row is no longer lightweight: `keywords` and the
// enchantment block ride on every card of four piles plus `master_deck`. That
// is the price of one face, and the alternative -- a second list of fields
// maintained beside `BuildCardInfo` -- is the defect this row was filed
// against.
//
// READ-ONLY. Nothing here plays, moves or mutates a card.

using System;
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>
    /// One pile row: the hand's `BuildCardInfo` face, plus the pile's own
    /// text where that differs from it (`EB-789`).
    /// </summary>
    private static Dictionary<string, object?> GitsPileCardRow(
        CardModel card, PileType pile)
    {
        // `BuildCardInfo`'s default pile is `PileType.None`; the hand's own
        // call takes the default and then overwrites `description` with the
        // `PileType.Hand` face. Asking for the hand face here directly is the
        // same question with the same answer, and it is asked in ONE place.
        var info = BuildCardInfo(card);
        info["description"] = SafeGetCardDescription(card);

        // The pile's own sentence, kept only where it says something the hand
        // face does not. `SafeGetCardDescription` never throws; a null on
        // either side is simply "no text", and two nulls are not a difference.
        var pileText = SafeGetCardDescription(card, pile);
        if (!string.Equals(pileText, (string?)info["description"],
                           StringComparison.Ordinal))
        {
            info["pile_description"] = pileText;
        }

        // Which pile this row came out of, in the game's own word. The lists
        // are already keyed by pile on the payload, but `master_deck` and the
        // three combat piles reach the page through ONE reader
        // (`_deck_card`), and a row that cannot name its own pile cannot be
        // told apart once the lists are concatenated.
        info["pile"] = pile.ToString();
        return info;
    }
}
