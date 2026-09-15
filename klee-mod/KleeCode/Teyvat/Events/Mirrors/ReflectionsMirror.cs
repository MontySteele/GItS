using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// REFLECTIONS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Reflections.cs` and cross-checked against
/// the harvest (2 options: Touch a Mirror, Shatter).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `NMirrorVfx` on room entry,
/// the same two-then-four on Touch a Mirror -- up to two UPGRADED cards
/// downgraded, then up to four UPGRADABLE ones upgraded, each picked off the
/// event's own `Rng` and removed from the working list so no card is picked
/// twice -- and the same whole-deck clone plus one Bad Luck on Shatter.
///
/// THE TWO LOOPS READ THE DECK TWICE, AND THAT IS THE BASE EVENT'S ORDER, not
/// an accident of transcription: `upgradableCards` is built AFTER the
/// downgrades, so a card the first loop downgraded is a candidate for the
/// second. Building both lists up front would quietly change the outcome, and
/// this is the clause a mirror is most likely to smooth over.
///
/// SHATTER SNAPSHOTS THE DECK SIZE BEFORE IT ADDS. `originalDeckSize` is read
/// once and the loop indexes the LIVE deck, so the clones the loop adds are
/// not themselves cloned -- without the snapshot this is an infinite deck.
///
/// THE CLONE IS `RunState.CloneCard`, not `CreateCard`, which is why this
/// mirror is not on `test_card_scope`'s run-scope allowlist: the lint reads
/// creation, and a clone of a card already in the deck is the base event's own
/// call for the same reason every other event-page add is -- an event room has
/// no combat state.
///
/// THE TITLE'S MIRROR-WRITING IS THE WIKI'S, NOT A KEY'S. The face heading is
/// `Reflections snoitcelfeR`; the class, the entry and every key are plain
/// `REFLECTIONS`, and `HEADING_ALIASES` in `gen_teyvat_events.py` is what
/// carries one to the other.
/// </summary>
public abstract class ReflectionsMirror : TeyvatEventMirror
{
    /// <summary>The base event's own: the mirror VFX, added safely because
    /// the room may already be tearing down.</summary>
    public override void OnRoomEnter()
    {
        NEventRoom.Instance?.VfxContainer?.AddChildSafely(NMirrorVfx.Create());
    }

    /// <summary>Two options, in the base event's order, with Bad Luck's card
    /// hover tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, TouchAMirror, InitialOptionKey("TOUCH_A_MIRROR")),
            new EventOption(this, Shatter, InitialOptionKey("SHATTER"),
                HoverTipFactory.FromCardWithCardHoverTips<BadLuck>()),
        };

    /// <summary>`TouchAMirror`: up to two downgrades, THEN a freshly read list
    /// of upgradable cards and up to four upgrades, with the base event's own
    /// waits between each.</summary>
    private async Task TouchAMirror()
    {
        List<CardModel> upgradedCards = Owner.Deck.Cards.Where((CardModel c) => c.IsUpgraded).ToList();
        for (int i = 0; i < 2; i++)
        {
            if (upgradedCards.Count <= 0)
            {
                break;
            }

            CardModel card = Rng.NextItem(upgradedCards);
            upgradedCards.Remove(card);
            CardCmd.Downgrade(card);
            CardCmd.Preview(card, 1.2f, CardPreviewStyle.MessyLayout);
            await Cmd.CustomScaledWait(0.3f, 0.5f);
        }

        List<CardModel> upgradableCards = Owner.Deck.Cards.Where((CardModel c) => c.IsUpgradable).ToList();
        for (int i = 0; i < 4; i++)
        {
            if (upgradableCards.Count <= 0)
            {
                break;
            }

            CardModel card = Rng.NextItem(upgradableCards);
            upgradableCards.Remove(card);
            CardCmd.Upgrade(card, CardPreviewStyle.MessyLayout);
            await Cmd.CustomScaledWait(0.3f, 0.5f);
        }

        await Cmd.CustomScaledWait(0.6f, 1.2f);
        SetEventFinished(L10NLookup(PageKey("TOUCH_A_MIRROR.description")));
    }

    /// <summary>`Shatter`: one clone of every card the deck held WHEN THE
    /// OPTION WAS TAKEN, then one Bad Luck.</summary>
    private async Task Shatter()
    {
        int originalDeckSize = Owner.Deck.Cards.Count;
        for (int i = 0; i < originalDeckSize; i++)
        {
            CardModel card = Owner.RunState.CloneCard(Owner.Deck.Cards[i]);
            CardCmd.PreviewCardPileAdd(
                await CardPileCmd.Add(card, PileType.Deck), 1.2f, CardPreviewStyle.MessyLayout);
            await Cmd.CustomScaledWait(0.1f, 0.2f);
        }

        await Cmd.CustomScaledWait(0.6f, 1.2f);
        await CardPileCmd.AddCurseToDeck<BadLuck>(Owner);
        SetEventFinished(L10NLookup(PageKey("SHATTER.description")));
    }
}
