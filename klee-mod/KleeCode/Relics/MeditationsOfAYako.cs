using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Relics;

/// <summary>
/// MEDITATIONS OF A YAKO -- Yae's starting relic (paper sec.3): "At a rest
/// site you may Publish: a card you Edited this run keeps its last
/// Annotation for the rest of the run." In place of Rest or Smith, the way
/// the base game's Shovel adds Dig (<c>Shovel.TryModifyRestSiteOptions</c>,
/// 0.111.0 decompile): the relic adds <see cref="PublishRestSiteOption"/> to
/// its owner's rest-site options, and choosing it spends the site's choice
/// as any option does (<c>RestSiteSynchronizer.ChooseOption</c> clears the
/// rest unless a listener says otherwise).
///
/// No free setup ([USER]'s rule): fight one opens with an empty shrine and
/// an unedited deck. The draft each Edit writes lives on the deck card
/// (<see cref="YaeEditing.Draft"/>), so the relic holds no state and its
/// Orobas upgrade inherits every draft.
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

    /// <summary>Does Publishing leave the site's other options open
    /// (Enlightened Blessing: "You may Publish and then Rest or Smith")?
    /// </summary>
    public virtual bool PublishKeepsTheSite => false;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Meditations of a Yako"),
        ("description",
            "At a [gold]Rest Site[/gold], you may [gold]Publish[/gold]: a card "
          + "you [gold]Edited[/gold] this run keeps its last Annotation for "
          + "the rest of the run."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForEdit(System.Array.Empty<IHoverTip>(), null);

    /// <summary>Set by <see cref="PublishRestSiteOption.OnSelect"/> for the
    /// one ask that follows it.</summary>
    private bool _justPublished;

    internal void NotePublished() => _justPublished = true;

    public override bool TryModifyRestSiteOptions(Player player,
                                                  ICollection<RestSiteOption> options)
    {
        if (player != Owner) return false;
        options.Add(new PublishRestSiteOption(player, this));
        return true;
    }

    /// <summary>
    /// Enlightened Blessing's rule: right after a Publish, the remaining
    /// options stay (MiniatureTent's hook, 0.111.0 decompile). Every other
    /// choice, and every choice under the plain relic, closes the site.
    /// </summary>
    public override bool ShouldDisableRemainingRestSiteOptions(Player player)
    {
        if (player != Owner) return true;
        var keep = _justPublished && PublishKeepsTheSite;
        _justPublished = false;
        if (keep) Flash();
        return !keep;
    }

    /// <summary>Placeholder art: Kokomi's Pearl of Wisdom icon, borrowed
    /// until her art pass plans her own.</summary>
    public override string PackedIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.PackedIconPath;

    protected override string BigIconPath =>
        KleePck.Path("kokomi/relics/pearl_of_wisdom.png") ?? base.BigIconPath;
}

/// <summary>
/// ENLIGHTENED BLESSING -- the Touch of Orobas upgrade (her A4): "You may
/// Publish and then Rest or Smith." ANCIENT, never Starter (a second Orobas
/// finds its target by Starter rarity).
/// </summary>
public sealed class EnlightenedBlessing : MeditationsOfAYako
{
    public override RelicRarity Rarity => RelicRarity.Ancient;

    public override bool PublishKeepsTheSite => true;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Enlightened Blessing"),
        ("description",
            "At a [gold]Rest Site[/gold], you may [gold]Publish[/gold] and then "
          + "Rest or Smith: a card you [gold]Edited[/gold] this run keeps its "
          + "last Annotation for the rest of the run."),
    };

    /// <summary>Already the upgrade.</summary>
    public override RelicModel? GetUpgradeReplacement() => null;
}

/// <summary>
/// PUBLISH, THE REST-SITE OPTION (pick 2 (a), ruled): choose a deck card that
/// holds a draft; its draft becomes its Published Annotation, the deck card's
/// Enchantment, which the run save keeps. A Published card can be Published
/// again later (the new one replaces it). Disabled, with the reason, when no
/// card holds a draft. Shovel's <c>DigRestSiteOption</c> is the shape.
/// </summary>
public sealed class PublishRestSiteOption : CustomRestSiteOption
{
    /// <summary>The rest_site_ui rows, merged by
    /// <c>KleeMod.InjectLocStrings</c> (the option's Title and Description
    /// are the base game's table lookups).</summary>
    public const string Id = "KLEEMOD_PUBLISH";

    public const string Name = "Publish";

    public const string DescriptionText =
        "A card you [gold]Edited[/gold] this run keeps its last Annotation "
      + "for the rest of the run.";

    public const string DisabledText =
        "No card has been [gold]Edited[/gold] this run.";

    public const string PromptKey = "KLEEMOD-YAE_REST_PUBLISH.selectionScreenPrompt";

    public const string PromptText = "Choose a card to Publish.";

    private readonly MeditationsOfAYako? _relic;

    public PublishRestSiteOption(Player owner, MeditationsOfAYako? relic = null)
        : base(owner)
    {
        _relic = relic;
    }

    public override string OptionId => Id;

    /// <summary>The Dig icon, borrowed (placeholder art).</summary>
    public override string? CustomIconPath => "res://images/ui/rest_site/option_dig.png";

    public override bool IsEnabled => YaeEditing.Publishable(Owner).Any();

    public override LocString Description => new(
        "rest_site_ui",
        "OPTION_" + OptionId + (IsEnabled ? ".description" : ".descriptionDisabled"));

    public override async Task<bool> OnSelect()
    {
        var cards = YaeEditing.Publishable(Owner).ToList();
        if (cards.Count == 0) return false;
        var prefs = new CardSelectorPrefs(new LocString("cards", PromptKey), 1)
        {
            Cancelable = true,
            RequireManualConfirmation = true,
        };
        var picked = (await CardSelectCmd.FromDeckGeneric(
            Owner, prefs, c => YaeEditing.Draft(c) != YaeAnnotation.None)).FirstOrDefault();
        if (picked == null) return false;
        if (!YaeEditing.PublishToDeck(picked, YaeEditing.Draft(picked))) return false;
        _relic?.NotePublished();
        return true;
    }
}
