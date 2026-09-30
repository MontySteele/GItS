#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// BOREAS'S FANG -- Varka's starting relic (the Oath rework, sec.4): "The
/// first time each combat you gain Oath, add Four Winds' Ascension to your
/// hand." Regent's Forge is the model: <c>ForgeCmd.Forge</c> "adds Sovereign
/// Blade to their hand if they haven't forged this combat" -- a card created
/// in combat (<c>CombatState.CreateCard</c>) and added through
/// <c>CardPileCmd.AddGeneratedCardToCombat</c>, never in the deck (0.111.0
/// decompile). Played, Ascension goes to the discard pile and comes back
/// when he draws it.
///
/// THE RULE IS NOT HERE. The first gain is <c>VarkaOath.Gain</c>'s question
/// (the per-combat latch lives in the Oath ledger); this class is the relic
/// and the one method that makes the card.
///
/// IT ALSO ROLLS HIS STARTER KNIGHT (sec.5: "One starting Knight, at random
/// each run"). The deck lists Amber: Precise Shot; <see cref="AfterObtained"/>,
/// which the game runs for starting relics when a NEW run is made and never
/// on a load (<c>RunManager.FinalizeStartingRelics</c>), transforms it into
/// one of the four starter Knights off the player's own seeded
/// Transformations stream, so every client of a co-op run rolls the same one.
///
/// QUARANTINED by <c>#if PROTOTYPE_CARDS</c> and living in <c>Relics/</c>,
/// <c>TamakushiCasket</c>'s reason: <c>tools/lint_unique_names.py</c> reads
/// relic titles out of this directory only.
/// </summary>
public sealed class BoreasFang : CustomRelicModel
{
    public BoreasFang() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Boreas's Fang"),
        ("description",
            "The first time each combat you gain [gold]Oath[/gold], add Four "
          + "Winds' Ascension to your hand."),
    };

    /// <summary>The word the face leans on.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForOath(System.Array.Empty<IHoverTip>(), null);

    /// <summary>The Fang this player holds, or null. PURE.</summary>
    public static BoreasFang? HeldBy(Player? player) =>
        player?.GetRelic<BoreasFang>();

    /// <summary>
    /// Four Winds' Ascension into his hand, created for this combat, the
    /// Forge's call. The hand's own limit sends it where the game sends any
    /// generated card that does not fit.
    /// </summary>
    internal async Task AddAscension(Player player)
    {
        var combat = player.Creature?.CombatState;
        if (combat == null) return;
        var card = combat.CreateCard<ProtoVkFourWindsAscension>(player);
        if (card == null) return;
        Flash();
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, player);
    }

    /// <summary>
    /// A new run: the starter Knight becomes the run's random one. Only the
    /// first starter Knight in the deck is rolled, and only while the deck
    /// still holds the listed one, so a second call (none today) changes
    /// nothing.
    /// </summary>
    public override async Task AfterObtained()
    {
        if (!VarkaPrototype.Enabled || Owner is not { } player) return;
        var listed = player.Deck.Cards.FirstOrDefault(
            c => c is ProtoVkAmberFieryRain && c.FloorAddedToDeck <= 1);
        if (listed == null) return;
        var pick = player.PlayerRng.Transformations.NextItem(
            VarkaRules.StarterKnights().ToList());
        if (pick == null || pick is ProtoVkAmberFieryRain) return;
        var rolled = player.RunState.CreateCard(pick, player);
        await CardCmd.Transform(listed, rolled, CardPreviewStyle.None);
    }

    /// <summary>
    /// His companion reward slot, the fourth card choice every roster
    /// character's starting relic carries (Salon Solitaire, the Tamakushi
    /// Casket): the Mondstadt Universals reach him here.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not IVarkaCharacter)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>FALLBACK ICON: the base game's Ring of the Snake until the
    /// art pass's own file is in the pack.</summary>
    protected override string IconBaseName => "snake_ring";

    public override string PackedIconPath =>
        KleePck.Path("varka/relics/boreas_fang.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("varka/relics/boreas_fang.png") ?? base.BigIconPath;
}
#endif
