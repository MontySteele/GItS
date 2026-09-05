using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// Furina's starter talent. BEFORE the normal turn draw (R123, sitting
/// 2026-08-07), it adds the one-use Spotlight selector to hand -- matching
/// the sim's pre-draw grant site (`effects.py`, turn-start triggers). The
/// earlier form granted post-draw, which made the X14(b) hand-full discard
/// fire on ordinary jam turns; ruled as a safety measure for softlock edge
/// cases, it should almost never fire, and pre-draw (a hand of retained
/// cards only) is what makes it rare. It also hosts Furina's fourth
/// companion reward option, mirroring Klee's always-present starter-relic
/// hook.
/// </summary>
public sealed class EtherealSpotlightRelic : CustomRelicModel
{
    public EtherealSpotlightRelic() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>
    /// G-C3 / red-pen R2. Without this, BaseLib's StarterUpgradePatches prefix
    /// falls through to vanilla's hardcoded table and Touch of Orobas replaces
    /// her talent relic with the no-effect Circlet.
    ///
    /// The upgraded form makes BOTH Spotlight modes permanent and stops adding
    /// the selector card -- see <see cref="CurtainNeverFalls"/>, including the
    /// Funnel Contract §3 note that landed before it.
    /// </summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<CurtainNeverFalls>().ToMutable();

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ethereal Spotlight"),
#if PROTOTYPE_CARDS && FURINA_REFRAME
        // `EB-406`. THE COPY THIS RELIC KEEPS HANDING BACK IS DEAD ONCE THE
        // SPOTLIGHT IS OUT, and under the arm that is permanent for the fight:
        // R228 (1) retires Center Stage, so Guest Cast is the only target and
        // there is no second aim to re-take. The card refuses itself now
        // (`SpotlightSystem.DesignateOneModeIsRedundant`), and this is the
        // sentence a reader gets BEFORE spending a turn finding out.
        //
        // ARM-ONLY, and chosen by the COMPILE constant for the reason the
        // card's own face is (`SpotlightCards.cs`): a Localization is read
        // once at registration. On a release build the selector has two modes
        // and a second play RE-AIMS, so the sentence would be false there.
        //
        // `EB-485` PUT THE DURATION IN IT, and the duration is the half a
        // seat cannot infer. "It does nothing once your Companion cards are
        // lit" reads as permanent; the lighting is a POWER and dies with the
        // fight, so the 2 Encore is paid again every combat. The r10 seat
        // weighed the Spotlight as a one-time purchase and met Chevreuse
        // printing 7 again in fight 2 ((c) 1).
        //
        // "EACH TURN" PAID FOR IT, at the same 117 rendered characters as
        // before and under the 120 relic ceiling. What went is the exact SITE
        // of the grant, which the player sees anyway -- the card is in hand
        // when the turn opens. What arrived is a rule no other surface stated.
        // The card's own tip says it too (`FurinaRiderTips
        // .ForSpotlightDuration`), because a relic is read once at the top of
        // a run and the card is read on the turn the Encore is spent.
        ("description",
            "Each turn, add an [gold]Ethereal Spotlight[/gold] to your "
          + "[gold]Hand[/gold]. It does nothing once your "
          + "[gold]Companion[/gold] cards are lit for this combat."),
#else
        ("description",
            "At the start of your turn, add an [gold]Ethereal Spotlight[/gold] "
          + "to your [gold]Hand[/gold]."),
#endif
    };

    /// <summary>
    /// FALLBACK ICON, and the OUTLINE atlas entry we ship no asset for --
    /// same arrangement as Klee's Pounding Surprise. Unlike hers there is no
    /// in-run collision to worry about: snake_ring belongs to the Silent, and
    /// Furina borrows the Silent relic pool, so this slug CAN co-occur with
    /// the real relic. That is exactly why the packed paths below matter --
    /// until they resolve, two different relics draw the same icon.
    /// </summary>
    protected override string IconBaseName => "snake_ring";

    /// <summary>
    /// The real icon, mirroring PoundingSurprise: RelicModel's icon-path
    /// getters are virtual, so the pck texture wires in directly and
    /// KleePck.Path falls through to the slug above while the asset is
    /// absent (logging the miss by name once).
    /// </summary>
    public override string PackedIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("furina/relics/ethereal_spotlight.png") ?? base.BigIconPath;

    /// <summary>
    /// Name of the derived rng stream for the hand-full fallback below.
    /// Rng(seed, name) mixes a deterministic hash of this string into the
    /// seed, giving the fallback its own stream -- the same reason
    /// <see cref="CompanionBanner"/> does it, and the same reason the sim
    /// draws from CombatState.selector_rng (seed + 4e9) rather than the
    /// fight's main rng. Drawing from Rng.CombatTargets would advance the
    /// stream every jammed-hand turn and silently renumber every combat roll
    /// taken after it.
    /// </summary>
    private const string HandFullRngStream = "furina_spotlight_hand_full";

    /// <summary>
    /// PRE-DRAW SITE (R123): BeforeSideTurnStart is the game's site A --
    /// before the block clear and before the draw -- so the hand here holds
    /// only retained cards, the same hand the sim's grant sees. The
    /// selector must be in hand before the draw resolves, not after.
    /// </summary>
    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        if (Owner is not { } player || player.Character is not Furina) return;
        var hand = CardPile.Get(PileType.Hand, player);
        if (hand == null || hand.Cards.Any(card => card is EtherealSpotlight))
        {
            return;
        }

        // HAND-FULL FALLBACK (sitting 2026-08-06, family X14 leg (b)):
        // "if the hand is full, one random card is discarded before the
        // spotlight is added." Ruled as a softlock safety measure, and under
        // the pre-draw site that is all it is: it needs a 10-card RETAINED
        // hand to fire, which is the edge case, not the jam-turn norm the
        // post-draw site made it.
        //
        // The victim pool is the sim's _op_discard pool rule -- KitGrant
        // .NotKitCard, because kit cards are never fodder (the v1.9
        // invariant). The seed is mixed with the 1-based turn number so a
        // multi-turn jam does not discard the same hand slot every turn, and
        // stays seed-replayable.
        if (hand.Cards.Count >= CardPile.MaxCardsInHand)
        {
            var pool = hand.Cards.Where(KitGrant.NotKitCard).ToList();
            if (pool.Count == 0) return;    // kit-only hand: no legal victim
            var turn = (uint)(player.PlayerCombatState?.TurnNumber ?? 0);
            var rng = new Rng(
                unchecked(player.PlayerRng.Seed + turn), HandFullRngStream);
            var victim = rng.NextItem(pool);
            if (victim == null) return;
            await CardCmd.Discard(choiceContext, victim);
        }
        if (hand.Cards.Count >= CardPile.MaxCardsInHand) return;

        var selector = player.Creature.CombatState!
            .CreateCard<EtherealSpotlight>(player);
        await CardPileCmd.AddGeneratedCardToCombat(
            selector, PileType.Hand, player);
    }

    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Furina)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds
                     == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }
}
