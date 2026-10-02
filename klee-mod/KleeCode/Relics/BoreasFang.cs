using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
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
///
/// THE STARTING ELEMENT (<c>review/active/varka-defence-2026-10-01.md</c>
/// sec.4, ruled 2026-10-01): "At the start of each combat, your starting
/// Knight's element becomes your current element." Knight's Commission's
/// door and moment (<see cref="AfterPlayerTurnStart"/>, his first turn, after
/// the draw) and its element: the one this Fang recorded for the run, else
/// the starter Knight in the deck. It gains no Oath, so the Ascension still
/// waits for his first gain. It is a change (Windblume Garland pays). The
/// badge shows it at once. Knight's Commission, which used to set this
/// element, now only gains 2 Oath in it (re-aimed, main session, 2026-10-01).
///
/// NOT SEALED: <see cref="WolfsGravestone"/>, the Touch of Orobas upgrade,
/// IS a Fang, so <see cref="HeldBy"/> (the game's <c>GetRelic&lt;T&gt;</c> is
/// an <c>is T</c> test) finds it and the Oath rule's one call site serves
/// both relics unchanged.
/// </summary>
public class BoreasFang : CustomRelicModel
{
    public BoreasFang() : base(autoAdd: false)
    {
    }

    /// <summary>Touch of Orobas: Wolf's Gravestone (2026-09-30).</summary>
    public override RelicModel? GetUpgradeReplacement()
    {
        var upgrade = ModelDb.Relic<WolfsGravestone>().ToMutable();
        // The run's starter Knight element rides along (Knight's Commission).
        if (upgrade is BoreasFang fang)
        {
            VarkaStarterKnight.Record(fang, VarkaStarterKnight.Of(this));
        }
        return upgrade;
    }

    /// <summary>Does this relic hand Ascension over upgraded and free this
    /// turn? The Fang no; <see cref="WolfsGravestone"/> yes.</summary>
    public virtual bool AscensionUpgraded => false;

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Boreas's Fang"),
        ("description",
            "At the start of each combat, your starting Knight's element "
          + "becomes your [gold]current element[/gold]. The first time each "
          + "combat you gain [gold]Oath[/gold], add Four Winds' Ascension to "
          + "your hand."),
    };

    /// <summary>The word the face leans on.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForCurrentElement(
            ArmKeywordTips.ForOath(System.Array.Empty<IHoverTip>(), null), null);

    /// <summary>The element the Fang makes current at combat start: the run's
    /// recorded starter Knight element, else the starter Knight in the deck
    /// (Knight's Commission's reading). PURE.</summary>
    public static Element StartingElement(Player player) =>
        KnightsCommission.StartingElement(VarkaStarterKnight.Of(player),
                                          player.Deck.Cards);

    /// <summary>Sec.4 of the Varka defence paper: his first turn, after the
    /// draw, the starter Knight's element becomes current.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!VarkaArmRelics.FirstTurnOf(this, player)) return;
        var element = StartingElement(player);
        if (element == Element.None) return;
        Flash();
        await VarkaOath.SetCurrent(choiceContext, player.Creature, element,
                                   knight: false);
    }

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
        if (AscensionUpgraded && card.IsUpgradable && !card.IsUpgraded)
        {
            card.UpgradeInternal();
        }
        Flash();
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, player);
        // Wolf's Gravestone: "It costs 0 this turn." Set once the card is in
        // play.
        if (AscensionUpgraded) card.EnergyCost.SetThisTurn(0);
    }

    /// <summary>
    /// A new run: the starter Knight becomes the run's random one. Only the
    /// first starter Knight in the deck is rolled, and only while the deck
    /// still holds the listed one, so a second call (none today) changes
    /// nothing.
    /// </summary>
    public override async Task AfterObtained()
    {
        if (Owner is not { } player) return;
        var listed = player.Deck.Cards.FirstOrDefault(
            c => c is ProtoVkAmberFieryRain && c.FloorAddedToDeck <= 1);
        if (listed == null) return;
        var pick = player.PlayerRng.Transformations.NextItem(
            VarkaRules.StarterKnights().ToList());
        // Recorded for the run (Knight's Commission reads it after the card
        // is gone): the rolled Knight's element, or the listed one's.
        VarkaStarterKnight.Record(this, VarkaOath.KnightElement(pick ?? listed));
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

/// <summary>
/// WOLF'S GRAVESTONE -- Boreas's Fang upgraded, Touch of Orobas's hand-over
/// (main-session design, 2026-09-30, from [USER]'s co-op playtest: "Varka and
/// Kokomi need Ancient relics for Orobas"). "The first time each combat you
/// gain Oath, add an upgraded Four Winds' Ascension to your hand. It costs 0
/// this turn." Same trigger as the Fang, which it IS (the subclass is how
/// <c>VarkaOath.Gain</c>'s <see cref="BoreasFang.HeldBy"/> finds it, so the
/// per-combat latch is the one the Fang uses); the card comes upgraded and
/// free this turn. The companion reward slot rides along by inheritance.
///
/// ANCIENT, NEVER STARTER (see <c>ExplosiveFrags</c>): a second Orobas finds
/// its target by Starter rarity. It does not re-roll the starter Knight: that
/// is a new-run rule, and <c>AfterObtained</c> runs on the mid-run grant.
///
/// ICON: the Fang's own (the same fallback chain), as Pearl of Insight and
/// The Curtain Never Falls reuse their starters'. Sim twin: tier0
/// <c>varka_oath.FANG_UPGRADED</c>.
/// </summary>
public sealed class WolfsGravestone : BoreasFang
{
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Wolf's Gravestone"),
        ("description",
            "At the start of each combat, your starting Knight's element "
          + "becomes your [gold]current element[/gold]. The first time each "
          + "combat you gain [gold]Oath[/gold], add an upgraded [gold]Four "
          + "Winds' Ascension[/gold] to your hand. It costs 0 this turn."),
    };

    public override bool AscensionUpgraded => true;

    /// <summary>Already the upgrade: nothing further for Orobas.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;

    /// <summary>The starter Knight is rolled once, at the run's start, by the
    /// Fang. The Gravestone arrives mid-run and rolls nothing.</summary>
    public override Task AfterObtained() => Task.CompletedTask;
}
