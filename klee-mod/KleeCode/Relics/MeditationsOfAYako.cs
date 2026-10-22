using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.TestSupport;

namespace KleeMod.Relics;

/// <summary>
/// MEDITATIONS OF A YAKO -- Yae's starting relic: "After an elite or boss
/// fight, you may Publish an Annotation." (Publish after elites and bosses,
/// ruled 2026-10-14, <c>review/active/yae-design-axes-2026-10-14.md</c>; it
/// was a rest-site option, which competed with Smith.)
///
/// HOW. At the end of every fight (<see cref="AfterCombatEnd"/>, while the
/// combat piles still exist) each deck card's draft is rewritten to the
/// Annotation its combat copy carries at that moment
/// (<see cref="YaeEditing.SnapshotDrafts"/>), so the drafts are that fight's
/// evidence and the run save keeps them across a reload on the reward
/// screen. After an elite or boss win the relic adds one
/// <see cref="YaePublishReward"/> to the combat reward screen
/// (<see cref="TryModifyRewards"/>, the hook Prayer Wheel uses), only when
/// the fight left some card a temporary layer to Publish. Review r3 (ruled
/// 2026-10-14): a Published card may be offered again, and the pick joins
/// its permanent stack (the Masterpiece).
///
/// No free setup ([USER]'s rule): fight one opens with an empty shrine and
/// an unedited deck, and the relic holds no state of its own, so its Orobas
/// upgrade inherits every draft.
///
/// NOT SEALED: <see cref="EnlightenedBlessing"/> IS one, so
/// <c>GetRelic&lt;MeditationsOfAYako&gt;</c> finds either.
/// </summary>
public class MeditationsOfAYako : CustomRelicModel
{
    public MeditationsOfAYako() : base(autoAdd: false)
    {
    }

    /// <summary>Touch of Orobas: Enlightened Blessing (her A4).</summary>
    public override RelicModel? GetUpgradeReplacement() =>
        ModelDb.Relic<EnlightenedBlessing>().ToMutable();

    public override RelicRarity Rarity => RelicRarity.Starter;

    /// <summary>How many Annotations one reward may Publish.</summary>
    public virtual int PublishCount => 1;

    public const string DescriptionText =
        "After an elite or boss fight, you may [gold]Publish[/gold] an "
      + "Annotation you made that fight.";

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Meditations of a Yako"),
        // Yae review r5, item 6: the reward is offered only when the fight
        // left an Annotation to Publish, so the text says whose.
        ("description", DescriptionText),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(System.Array.Empty<IHoverTip>(), null);

    /// <summary>Yae review r6, item 3: this fight was one that offers a
    /// Publish and left no Annotation to Publish, so the relic flashed and
    /// said "Nothing to Publish". Not saved; cleared when a fight ends and
    /// when a room is entered. The seat page reads it through
    /// <see cref="YaeShrine.Snapshot"/>.</summary>
    public bool NothingToPublish { get; private set; }

    /// <summary>The fight's evidence: every deck card's draft becomes the
    /// Annotation its combat copy carries now.</summary>
    public override Task AfterCombatEnd(CombatRoom room)
    {
        NothingToPublish = false;
        YaeEditing.SnapshotDrafts(Owner);
        return Task.CompletedTask;
    }

    public override Task AfterRoomEntered(AbstractRoom room)
    {
        NothingToPublish = false;
        return Task.CompletedTask;
    }

    public override bool TryModifyRewards(Player player, List<Reward> rewards,
                                          AbstractRoom? room)
    {
        if (player != Owner || room is not CombatRoom combat) return false;
        NothingToPublish = false;
        var runState = player.RunState;
        var finalBoss = room.RoomType == RoomType.Boss
            && runState.CurrentActIndex >= runState.Acts.Count - 1;
        if (!YaeEditing.OffersPublish(room.RoomType,
                combat.Encounter?.ShouldGiveRewards ?? false, finalBoss))
        {
            return false;
        }
        if (!YaeEditing.PublishChoices(player).Any())
        {
            // Yae review r6, item 3: say why no Publish came.
            NothingToPublish = true;
            Flash();
            YaeEditing.SayNothing(player.Creature, YaeEditing.NothingToPublishKey);
            return false;
        }
        rewards.Add(new YaePublishReward(player, this));
        return true;
    }

    /// <summary>Whether this relic adds the companion slot to the reward
    /// being built for <paramref name="player"/>: only its own owner's,
    /// once (see <see cref="CompanionSlot.OffersTo"/>).</summary>
    public bool OffersCompanionTo(Player player, CardCreationOptions creationOptions) =>
        CompanionSlot.OffersTo(this, player, creationOptions, player.Character is IYaeCharacter);

    /// <summary>
    /// Yae's companion reward slot: the starter relic is where every roster
    /// character's fourth reward choice lives. It was left off when this
    /// relic was written, so Yae drafted no companions at all; [USER]'s
    /// co-op run caught it (2026-10-17), as it caught Furina's (2026-09-27).
    /// Enlightened Blessing inherits it.
    /// </summary>
    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (!OffersCompanionTo(player, creationOptions)) return false;
        var offer = CompanionSlot.Roll(player, creationOptions);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }

    /// <summary>The outline atlas sprite (see SalonSolitaire): without an
    /// override it derives from the mod id, which the atlas lacks.</summary>
    protected override string IconBaseName => "ring_of_the_snake";

    /// <summary>Her own icon since the power and relic icon pass
    /// (2026-10-18, art/plan.tsv relic_meditations_of_a_yako): an Inazuma
    /// Electro Vision. Kokomi's Pearl of Wisdom, which it borrowed before,
    /// stays the fallback for a pck built before the art.</summary>
    public override string PackedIconPath =>
        KleePck.Path("yae/relics/meditations_of_a_yako.png")
        ?? KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("yae/relics/meditations_of_a_yako.png")
        ?? KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}

/// <summary>
/// ENLIGHTENED BLESSING -- the Touch of Orobas upgrade (her A4). It was
/// "Publish and then Rest or Smith"; with the rest-site option gone it
/// Publishes up to two (Claude's reading of the upgrade, 2026-10-14, open to
/// change). ANCIENT, never Starter (a second Orobas finds its target by
/// Starter rarity).
/// </summary>
public sealed class EnlightenedBlessing : MeditationsOfAYako
{
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override int PublishCount => 2;

    public new const string DescriptionText =
        "After an elite or boss fight, you may [gold]Publish[/gold] up to "
      + "2 Annotations you made that fight.";

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Enlightened Blessing"),
        ("description", DescriptionText),
    };

    /// <summary>Already the upgrade.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;

    /// <summary>Its own icon since 2026-10-22 (art/plan.tsv
    /// relic_enlightened_blessing): the golden magatama of Narukami's Valor,
    /// gold Inazuma Electro against the base's silver Vision. The base's
    /// chain is the fallback.</summary>
    public override string PackedIconPath =>
        KleePck.Path("yae/relics/enlightened_blessing.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("yae/relics/enlightened_blessing.png") ?? base.BigIconPath;
}

/// <summary>
/// PUBLISH, THE REWARD-SCREEN ROW. Claiming it opens a grid of the cards the
/// fight left a temporary layer on, each shown as a copy wearing its stack
/// and that layer; the one picked is that exact deck card, and the layer
/// joins the deck card's permanent stack, which the run save keeps. The grid can be closed
/// without a pick (the row stays, as a full-belt potion's does), and leaving
/// the reward screen skips it. Not serialised: the reward screen is rebuilt
/// from the room and the hooks on a reload, and the drafts it reads are
/// saved on the deck cards.
/// </summary>
public sealed class YaePublishReward : Reward
{
    /// <summary>The reward row's text, merged into `gameplay_ui` by
    /// <c>KleeMod.InjectLocStrings</c>.</summary>
    public const string DescriptionKey = "KLEEMOD_YAE_PUBLISH_REWARD";

    public const string DescriptionText = "Publish an Annotation";

    private readonly MeditationsOfAYako? _relic;

    public YaePublishReward(Player player, MeditationsOfAYako? relic = null)
        : base(player)
    {
        _relic = relic;
    }

    /// <summary>No base type fits; nothing serialises it (above).</summary>
    protected override RewardType RewardType => RewardType.None;

    /// <summary>After the card reward (5), before a card removal (7).</summary>
    public override int RewardsSetIndex => 6;

    public override LocString Description => new("gameplay_ui", DescriptionKey);

    public override bool IsPopulated => true;

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(System.Array.Empty<IHoverTip>(), null);

    public override void Populate()
    {
    }

    /// <summary>The relic's own icon.</summary>
    public override Control? CreateIcon()
    {
        if (TestMode.IsOn || _relic == null) return null;
        var rect = new TextureRect
        {
            Texture = _relic.BigIcon,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
        };
        rect.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        return rect;
    }

    /// <summary>The grid's terms: up to `max` picks (one, or two under
    /// Enlightened Blessing), confirmed by hand, and it may be closed without
    /// one. The minimum is ZERO even for one pick: a grid that must pick one
    /// of exactly one card is auto-answered by the game, which published a card
    /// nobody chose (Yae review r4, item 1). PURE.</summary>
    public static CardSelectorPrefs Prefs(int max) =>
        new CardSelectorPrefs(new LocString("cards", YaeEditing.PublishPromptKey), 0, max)
        {
            Cancelable = true,
            RequireManualConfirmation = true,
        };

    protected override async Task<bool> OnSelect()
    {
        var decks = YaeEditing.PublishChoices(Player).ToList();
        if (decks.Count == 0) return false;
        var previews = decks.Select(YaeEditing.PublishPreview).ToList();
        var max = System.Math.Min(_relic?.PublishCount ?? 1, decks.Count);
        List<CardModel> picked;
        try
        {
            picked = (await CardSelectCmd.FromSimpleGrid(
                new BlockingPlayerChoiceContext(), previews, Player, Prefs(max))).ToList();
        }
        finally
        {
            foreach (var preview in previews) Player.RunState.RemoveCard(preview);
        }
        var n = 0;
        foreach (var deck in YaeEditing.ResolvePicks(previews, decks, picked).Take(max))
        {
            if (YaeEditing.PublishToDeck(deck, YaeEditing.Draft(deck))) n++;
        }
        if (n == 0) return false;
        YaeEditing.ClearDrafts(Player);
        _relic?.Flash();
        return true;
    }

    public override void MarkContentAsSeen()
    {
    }
}
