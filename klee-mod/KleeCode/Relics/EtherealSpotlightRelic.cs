using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// Furina's starter talent. After the normal turn draw, it adds the one-use
/// Spotlight selector to hand. It also hosts Furina's fourth companion reward
/// option, mirroring Klee's always-present starter-relic hook.
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
        ("description",
            "At the start of each turn, add an [gold]Ethereal Spotlight[/gold] "
          + "to your hand. " + CompanionSlot.RewardSlotDescription),
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

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner || player.Character is not Furina) return;
        var hand = CardPile.Get(PileType.Hand, player);
        if (hand == null || hand.Cards.Any(card => card is EtherealSpotlight))
        {
            return;
        }

        // HAND-FULL FALLBACK (sitting 2026-08-06, family X14 leg (b)):
        // "if the hand is full, one random card is discarded before the
        // spotlight is added." Before this the grant was simply skipped, so
        // the relic that exists to guarantee Furina a play was exactly what a
        // jammed hand starved.
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
