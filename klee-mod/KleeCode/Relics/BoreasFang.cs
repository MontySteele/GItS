#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// BOREAS'S FANG -- Varka's starting relic (sec.10.1, as built): "Once each
/// turn, the first non-Anemo Attack that hits a fresh aura Absorbs it. It
/// reads Absorb's rule, so on a held Wind it Swirls. The choice lives in which
/// card you aim at an aura: a Strike collects, an Anemo Attack Swirls. This
/// drops sec.9.3's in-hit prompt for the prototype; a prompt comes back only
/// if play asks for it."
///
/// THE RULE IS NOT HERE. The aura lifecycle asks
/// <see cref="VarkaAbsorb.FangTakes"/> on the hit and marks the relic used
/// through <see cref="Use"/>; this class holds the once-a-turn latch, shows
/// it on its icon, and clears it at the start of each of his turns.
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
            "Once each turn, the first non-[gold]Anemo[/gold] Attack that hits "
          + "a fresh aura [gold]Absorbs[/gold] it."),
    };

    /// <summary>The two words the face leans on: what an Absorb does, and
    /// what it collects.</summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForWind(ArmKeywordTips.ForAbsorb(
            System.Array.Empty<IHoverTip>(), null), null);

    /// <summary>Has the Fang taken a hit this turn?</summary>
    public bool UsedThisTurn { get; private set; }

    /// <summary>The Fang took this turn's hit.</summary>
    public void Use()
    {
        if (UsedThisTurn) return;
        UsedThisTurn = true;
        Flash();
        InvokeDisplayAmountChanged();
    }

    /// <summary>1 while the Fang is ready this turn, 0 once it has taken its
    /// hit: the base game's counter idiom (Kunai), in combat only.</summary>
    public override bool ShowCounter =>
        Owner?.Creature?.CombatState != null
        && VarkaPrototype.LiveFor(Owner.Creature);

    public override int DisplayAmount => UsedThisTurn ? 0 : 1;

    public override Task BeforeCombatStart()
    {
        UsedThisTurn = false;
        InvokeDisplayAmountChanged();
        return Task.CompletedTask;
    }

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner) return Task.CompletedTask;
        UsedThisTurn = false;
        InvokeDisplayAmountChanged();
        return Task.CompletedTask;
    }

    /// <summary>
    /// His companion reward slot, the fourth card choice every roster
    /// character's starting relic carries (Salon Solitaire, the Tamakushi
    /// Casket): the Mondstadt Universals reach him here, which is where the
    /// paper kit's delete-test looks for them (sec.7).
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
