using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Powers;

/// <summary>
/// Conscript -- the Commander verb (kickoff §2.3).
///
/// A card in hand becomes a random same-nation Companion, costing
/// <see cref="KokomiConstants.ConscriptCostDelta"/> less (floor 0) and gaining
/// Exhaust. Net deck delta is ZERO, which is what makes the verb legal at
/// Common under her deck-size law (LAW 4: Commons never create cards).
///
/// `create` mode is the same grammar with the recruit added to hand instead of
/// replacing anything -- net POSITIVE, therefore Uncommon+ only, which her
/// sheet lint enforces upstream.
///
/// VOICE LAW (R55): this is a MUSTER, never a sacrifice. Units rotate off the
/// line rested and whole. Display text uses the Muster/Enlist/Rally family;
/// only the internal op name stays `conscript`.
///
/// ------------------------------------------------------------------
/// DELIBERATE SIM DIVERGENCE -- flagged, not silent.
///
/// The sim conscripts `_worst_card` in hand. Its own comment calls that
/// "pilot judgement, not law": the auto-pick exists because the sim has no
/// human at the table. Here there is one, so the player chooses. Taking the
/// choice away to match a heuristic that was only ever a stand-in for choice
/// would be parity with the instrument rather than with the design.
///
/// The consequence is real and belongs on the record: a human will conscript
/// better than `_worst_card` does, so the mod's Commander lane should run at
/// or above the sim's numbers rather than at them. That is a thing to WATCH in
/// playtest (protocol item 3), and it is why the parity fixture scripts the
/// selection rather than asserting the auto-pick.
/// ------------------------------------------------------------------
/// </summary>
public static class KokomiConscript
{
    /// <summary>
    /// Her home nation. The pool is deliberately the Inazuma roster and not
    /// "any companion": the resistance she musters is her own.
    /// </summary>
    public const string Nation = "inazuma";

    public static async Task Run(
        PlayerChoiceContext choiceContext, Player owner, CardModel source,
        int amount, bool createMode, int? costOverride)
    {
        for (var i = 0; i < amount; i++)
        {
            var recruit = RollRecruit(owner, costOverride);
            if (recruit == null) return;        // no pool: whiff, not a crash

            if (createMode)
            {
                await CardPileCmd.AddGeneratedCardToCombat(
                    recruit, PileType.Hand, owner);
                continue;
            }

            var hand = CardPile.Get(PileType.Hand, owner);
            if (hand == null) return;

            // Kit cards are never fodder (the v1.9 invariant the Burst has
            // carried since the kit sprint), and an already-conscripted
            // recruit is excluded too -- re-mustering the same unit is
            // rules-legal and pointless, and offering it just adds noise to
            // the prompt.
            bool Eligible(CardModel card) =>
                KitGrant.NotKitCard(card) && card is not ICompanionCard;

            if (!hand.Cards.Any(Eligible)) return;   // conscript whiffed

            var picked = (await CardSelectCmd.FromHand(
                choiceContext, owner,
                // The game's OWN transform prompt, not a hand-rolled string.
                // It is already localized, and it says "transform" -- which is
                // the R55 voice law's word anyway (the unit rotates, it is not
                // spent). A custom LocString here would be an unlocalized
                // English literal shipped into every language.
                new CardSelectorPrefs(
                    CardSelectorPrefs.TransformSelectionPrompt, 1),
                Eligible, source)).ToList();
            if (picked.Count == 0) return;

            await CardCmd.Transform(
                picked[0], recruit, CardPreviewStyle.None);
        }
    }

    /// <summary>
    /// One recruit: a random Inazuma companion, discounted and Exhausting.
    /// The discount is applied to the INSTANCE, never to the canonical model
    /// -- mutating the model would discount every future copy in the run.
    /// </summary>
    private static CardModel? RollRecruit(Player owner, int? costOverride)
    {
        var pool = CompanionRoster.All
            .Where(card => (card as ICompanionCard)?.Nation == Nation)
            .ToList();
        if (pool.Count == 0) return null;

        var pick = owner.PlayerRng.Rewards.NextItem<CardModel>(pool);
        if (pick == null) return null;

        // COMBAT scope, not run scope. A recruit is a combat-local instance:
        // the sim's `_op_conscript` deepcopies into `state.player.hand` and
        // never touches the deck, the discount is AddThisCombat, and the
        // Exhaust is per-instance -- all three are combat-lifetime.
        //
        // This read `((ICardScope)owner.RunState).CreateCard(pick, owner)`,
        // copied from CompanionSlot, where run scope IS right because that
        // recruit is a REWARD and goes into the deck. Here it produced a card
        // the CombatState had never seen, and the base game rejects those at
        // both doors: `AddGeneratedCardToCombat` throws "must be added to a
        // CombatState before adding it to this pile" (create mode, dies on
        // play of the conscript card), and `AddDuringManualCardPlay` throws
        // "...before playing it" (transform mode -- the transform LOOKS fine
        // and the recruit sits in hand, then playing it throws inside
        // PlayCardAction, which leaves the action queue stuck: a soft lock,
        // not a crash). Playtest 2026-07-26: Honor Guard -> Gorou, General's
        // War Banner. CombatState.CreateCard is the pattern every other
        // generated card in the mod already uses.
        var combatState = owner.Creature?.CombatState;
        if (combatState == null) return null;    // out of combat: whiff

        var recruit = combatState.CreateCard(pick, owner);
        if (recruit == null) return null;

        // Cost is a MODIFIER on the instance, applied for the rest of the
        // combat. There is no settable base cost on CardModel, and mutating
        // the canonical model would discount every future copy in the run.
        // cost_override lands as the delta that reaches the target absolutely;
        // the ordinary case is the flat CONSCRIPT_COST_DELTA. Floor 0 is the
        // sim's rule, so an override of 0 on an already-0 card is a no-op
        // rather than a negative cost.
        var canonical = recruit.EnergyCost.Canonical;
        var target = costOverride ?? System.Math.Max(
            0, canonical + KokomiConstants.ConscriptCostDelta);
        var delta = System.Math.Max(0, target) - canonical;
        if (delta != 0)
        {
            recruit.EnergyCost.AddThisCombat(delta, reduceOnly: false);
        }

        // "Gains Exhaust". CardKeyword.Exhaust is declared per MODEL and is
        // not settable per instance; ExhaustOnNextPlay is the instance-level
        // equivalent and is exactly right here -- a recruit is mustered, used
        // once, and rotates off the line.
        recruit.ExhaustOnNextPlay = true;
        return recruit;
    }
}
