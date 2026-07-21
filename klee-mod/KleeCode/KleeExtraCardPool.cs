using Godot;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using System.Collections.Generic;
using System.Linq;

namespace KleeMod;

/// <summary>
/// Klee's off-pool cards: the companion roster and the token statuses.
///
/// WHY THIS EXISTS (playtest crash 2026-07-21). Every card must belong to some
/// pool, whether or not it is ever rollable. CardModel.Pool walks
/// ModelDb.AllCardPools for a pool containing the card's id, and when nothing
/// matches it probes MockCardPool as a last resort -- whose GenerateAllCards
/// calls NeverEverCallThisOutsideOfTests_ClearOwner() and throws
/// InvalidOperationException("You monster!") in a shipped build.
///
/// Pool is read by NCard.Reload for the frame/energy visuals, i.e. on every
/// card NODE creation. So a poolless card did not fail when played -- it failed
/// the instant the game tried to DRAW it or PREVIEW it, taking down whatever
/// task owned that draw. Observed: the companion reward's take-animation threw
/// out of SpecialCardReward.OnSelect (the card was added to the deck, but the
/// click looked dead), and the next turn's CombatManager.SetupPlayerTurn draw
/// threw and softlocked the combat.
///
/// Companions were kept out of KleeCardPool deliberately -- the 4th reward slot
/// is their only door (tier05 character_pool excludes them), and pool
/// membership is what reward and transform generation draws from. That design
/// is unchanged: this is a SEPARATE pool, and Klee.CardPool still returns
/// KleeCardPool, so nothing here is ever rolled as a normal reward. It exists
/// only so Pool resolves.
///
/// Membership tracks CompanionRoster.All (regenerated from the sheet), so a new
/// companion cannot be added to the roster and forgotten here.
/// tools/lint_pool_membership.py fails the deploy if any card class escapes
/// both pools.
/// </summary>
public sealed class KleeExtraCardPool : CardPoolModel
{
    public override string Title => "klee_companion";

    // Mirrors KleeCardPool: companions read as Klee cards on the deck screen,
    // because that is what they are to the player.
    public override string EnergyColorName => "ironclad";

    public override string CardFrameMaterialPath => "card_frame_red";

    public override Color DeckEntryCardColor => new Color("E85A4F");

    public override Color EnergyOutlineColor => new Color("7A2418");

    /// <summary>False = "belongs to a character", same as KleeCardPool. Keeps
    /// these out of anything that generates colorless rewards.</summary>
    public override bool IsColorless => false;

    protected override CardModel[] GenerateAllCards()
    {
        var cards = new List<CardModel>(CompanionRoster.All);

        // The kit Burst card: granted to hand by KitGrant when the meter
        // fills, never draftable or transformable -- but granting builds a
        // card node, so it hit the same crash. (Found by
        // tools/lint_pool_membership.py on its very first run.)
        cards.Add(ModelDb.Card<SparksNSplash>());

        // Token statuses: created at play time (Fish Blasting), never rolled,
        // but they are still drawn -- which is exactly the crash path above.
        cards.Add(ModelDb.Card<Confiscated>());

        return cards.ToArray();
    }
}
