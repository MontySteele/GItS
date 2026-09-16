using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Assets;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Random;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE TRIAL, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/Trial.cs` and cross-checked against the
/// frozen harvest (6 options: the three cases x Guilty / Innocent).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same juror number rolled once on
/// the chaotic stream, the same three-way `Rng.NextInt(3)` case roll, the same
/// six verdicts (Regret + two relics; Shame + two upgrades; heal 10; Regret +
/// 300 gold; Doubt + two card rewards; Doubt + two transforms), the same
/// hover tips on the curse-bearing options, the same Reject page with its
/// Accept and its Double Down, and the same portrait swap and per-case VFX.
///
/// DOUBLE DOWN OPENS THE ABANDON-RUN POPUP, and it is the one option in this
/// surface where wrong text is dangerous -- the button ends the run. It is
/// built with the base event's own two flags (`isDisabled: false`,
/// `isDangerous: true`) and its own `ThatWillKillPlayerIf(_ =&gt; true)`, so
/// the confirm popup and the red styling both arrive the way they do in the
/// base game, and the words on it are the face's own keyed line rather than a
/// neighbour's borrowed outcome. That borrowing is why this event was parked.
///
/// `trialFormat` AND `trialResult` ARE BORROWED FROM THE BASE, NOT DRESSED.
/// They are the two WRAPPER rows this event prints everything else inside:
/// `SetEventState` is handed `TRIAL.trialFormat` with the chosen story page's
/// raw text injected as `{TrialStory}`, and `SetEventFinished` is handed
/// `TRIAL.trialResult` with the verdict page's raw text as `{TrialResult}`.
/// Neither carries a word that belongs to a nation -- the dressed prose is
/// the injected page, which IS keyed per face -- so there is nothing for a
/// face to write and the mirror looks both up under the BASE entry, the same
/// borrowing `TeyvatGeneratedEvents.Portraits` makes for the portrait. The
/// two literals are declared to `A_mirrors_key_literals_are_exactly_its_shape`
/// as foreign keys for exactly that reason.
///
/// THE STORY AND RESULT PAGES ARE READ WITH `GetRawText`, not formatted, and
/// that is the base event's own call: the page is injected into the wrapper
/// as a `StringVar` and the wrapper is what SmartFormat then runs over.
/// </summary>
public abstract class TrialMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names.</summary>
    private const string EntrantNumberKey = "EntrantNumber";

    private const string TrialResultKey = "TrialResult";

    private const string TrialStoryKey = "TrialStory";

    /// <summary>
    /// The base event's two wrapper rows, under the BASE entry.
    ///
    /// A dressing does not own these: they are the frame the juror number and
    /// the chosen page are printed inside, and every word in them is the
    /// courtroom's, not Fontaine's or Sumeru's. See the class comment.
    /// </summary>
    private const string TrialFormatKey = "TRIAL.trialFormat";

    private const string TrialResultFormatKey = "TRIAL.trialResult";

    private static readonly string TrialMerchantVfx =
        SceneHelper.GetScenePath("vfx/events/trial_merchant_vfx");

    private static readonly string TrialNobleVfx =
        SceneHelper.GetScenePath("vfx/events/trial_noble_vfx");

    private static readonly string TrialNondescriptVfx =
        SceneHelper.GetScenePath("vfx/events/trial_nondescript_vfx");

    /// <summary>`Trial.cs`: the juror number the summons prints, rolled once
    /// in <see cref="CalculateVars"/> and -1 until it is.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DynamicVar(EntrantNumberKey, -1m) };

    /// <summary>The BASE event's own image, as the portrait borrow is. The
    /// docket-open portrait is swapped in when a case is called.</summary>
    private static string TrialStartedPath => ImageHelper.GetImagePath("events/trial_started.png");

    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Accept, InitialOptionKey("ACCEPT")),
            new EventOption(this, Reject, InitialOptionKey("REJECT")),
        };

    /// <summary>The base event's preload list, plus the four assets it names
    /// itself.</summary>
    public override IEnumerable<string> GetAssetPaths(IRunState runState)
    {
        List<string> paths = new List<string>();
        paths.AddRange(base.GetAssetPaths(runState));
        paths.Add(TrialStartedPath);
        paths.Add(TrialMerchantVfx);
        paths.Add(TrialNobleVfx);
        paths.Add(TrialNondescriptVfx);
        return paths;
    }

    /// <summary>
    /// One case, rolled three ways on the event's own `Rng`, exactly as the
    /// base event rolls it. The page's own description becomes the
    /// `{TrialStory}` inside the borrowed wrapper.
    /// </summary>
    private Task Accept()
    {
        if (LocalContext.IsMe(Owner))
        {
            NEventRoom.Instance.Layout.RemoveNodesOnPortrait();
        }

        string portraitPath;
        string entryName;
        EventOption[] options;
        switch (Rng.NextInt(3))
        {
            case 0:
                portraitPath = TrialMerchantVfx;
                entryName = PageKey("MERCHANT.description");
                options = new EventOption[]
                {
                    new EventOption(this, MerchantGuilty, PageKey("MERCHANT.options.GUILTY"),
                        HoverTipFactory.FromCardWithCardHoverTips<Regret>()),
                    new EventOption(this, MerchantInnocent, PageKey("MERCHANT.options.INNOCENT"),
                        HoverTipFactory.FromCardWithCardHoverTips<Shame>()),
                };
                break;
            case 1:
                portraitPath = TrialNobleVfx;
                entryName = PageKey("NOBLE.description");
                options = new EventOption[]
                {
                    new EventOption(this, NobleGuilty, PageKey("NOBLE.options.GUILTY")),
                    new EventOption(this, NobleInnocent, PageKey("NOBLE.options.INNOCENT"),
                        HoverTipFactory.FromCardWithCardHoverTips<Regret>()),
                };
                break;
            case 2:
                portraitPath = TrialNondescriptVfx;
                entryName = PageKey("NONDESCRIPT.description");
                options = new EventOption[]
                {
                    new EventOption(this, NondescriptGuilty,
                        PageKey("NONDESCRIPT.options.GUILTY"),
                        HoverTipFactory.FromCardWithCardHoverTips<Doubt>()),
                    new EventOption(this, NondescriptInnocent,
                        PageKey("NONDESCRIPT.options.INNOCENT"),
                        HoverTipFactory.FromCardWithCardHoverTips<Doubt>()
                            .Concat(new List<IHoverTip>
                                { HoverTipFactory.Static(StaticHoverTip.Transform) })),
                };
                break;
            default:
                throw new ArgumentOutOfRangeException();
        }

        AddVfxAnchoredToPortrait(portraitPath);
        if (LocalContext.IsMe(Owner))
        {
            NEventRoom.Instance.SetPortrait(PreloadManager.Cache.GetTexture2D(TrialStartedPath));
        }

        LocString framed = L10NLookup(TrialFormatKey);
        framed.Add(new StringVar(TrialStoryKey, L10NLookup(entryName).GetRawText()));
        SetEventState(framed, options);
        return Task.CompletedTask;
    }

    /// <summary>
    /// The Reject page: take the seat after all, or walk out. The second is
    /// the abandon-run flow, and the two flags and the lethality predicate are
    /// the base event's.
    /// </summary>
    private Task Reject()
    {
        EventOption[] options = new EventOption[]
        {
            new EventOption(this, Accept, PageKey("REJECT.options.ACCEPT")),
            new EventOption(this, DoubleDown, PageKey("REJECT.options.DOUBLE_DOWN"),
                false, true).ThatWillKillPlayerIf(_ => true),
        };
        LocString description = L10NLookup(PageKey("REJECT.description"));
        SetEventState(description, options);
        return Task.CompletedTask;
    }

    /// <summary>`Trial.DoubleDown`, whole: the abandon-run confirm popup, and
    /// nothing else. The event does NOT finish here -- the popup owns what
    /// happens next, including the player declining it.</summary>
    private Task DoubleDown()
    {
        NModalContainer.Instance.Add(NAbandonRunConfirmPopup.Create(null));
        return Task.CompletedTask;
    }

    private void AddVfxAnchoredToPortrait(string portraitPath)
    {
        if (LocalContext.IsMe(Owner))
        {
            Node2D vfx = PreloadManager.Cache.GetScene(portraitPath)
                .Instantiate<Node2D>(PackedScene.GenEditState.Disabled);
            vfx.Position = new Vector2(292f, 68f);
            NEventRoom.Instance.Layout.AddVfxAnchoredToPortrait(vfx);
        }
    }

    private async Task MerchantGuilty()
    {
        await CardPileCmd.AddCurseToDeck<Regret>(Owner);
        for (int i = 0; i < 2; i++)
        {
            await RelicCmd.Obtain(RelicFactory.PullNextRelicFromFront(Owner).ToMutable(), Owner);
        }

        SetTrialFinished(PageKey("MERCHANT_GUILTY.description"));
    }

    private async Task MerchantInnocent()
    {
        await CardPileCmd.AddCurseToDeck<Shame>(Owner);
        foreach (CardModel card in await CardSelectCmd.FromDeckForUpgrade(
            prefs: new CardSelectorPrefs(CardSelectorPrefs.UpgradeSelectionPrompt, 2),
            player: Owner))
        {
            CardCmd.Upgrade(card);
        }

        SetTrialFinished(PageKey("MERCHANT_INNOCENT.description"));
    }

    private async Task NobleGuilty()
    {
        await CreatureCmd.Heal(Owner.Creature, 10m);
        SetTrialFinished(PageKey("NOBLE_GUILTY.description"));
    }

    private async Task NobleInnocent()
    {
        await CardPileCmd.AddCurseToDeck<Regret>(Owner);
        await PlayerCmd.GainGold(300m, Owner);
        SetTrialFinished(PageKey("NOBLE_INNOCENT.description"));
    }

    private async Task NondescriptGuilty()
    {
        await CardPileCmd.AddCurseToDeck<Doubt>(Owner);
        List<Reward> rewards = new List<Reward>();
        for (int i = 0; i < 2; i++)
        {
            rewards.Add(new CardReward(
                CardCreationOptions.ForNonCombatWithDefaultOdds(
                    new List<CardPoolModel> { Owner.Character.CardPool }),
                3, Owner));
        }

        await RewardsCmd.OfferCustom(Owner, rewards);
        SetTrialFinished(PageKey("NONDESCRIPT_GUILTY.description"));
    }

    private async Task NondescriptInnocent()
    {
        await CardPileCmd.AddCurseToDeck<Doubt>(Owner);
        List<CardModel> chosen = (await CardSelectCmd.FromDeckForTransformation(
            prefs: new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 2),
            player: Owner)).ToList();
        foreach (CardModel card in chosen)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }

        SetTrialFinished(PageKey("NONDESCRIPT_INNOCENT.description"));
    }

    /// <summary>The base event's own helper, and its comment's reason: this
    /// event's finished description is BUILT, not looked up -- the verdict
    /// page goes inside the borrowed `trialResult` wrapper.</summary>
    private void SetTrialFinished(string trialResultLoc)
    {
        LocString framed = L10NLookup(TrialResultFormatKey);
        framed.Add(new StringVar(TrialResultKey, L10NLookup(trialResultLoc).GetRawText()));
        SetEventFinished(framed);
    }

    /// <summary>The juror number, rolled once off the chaotic stream -- the
    /// base event's stream, not the event's own `Rng`, so two players see the
    /// same summons read differently.</summary>
    public override void CalculateVars()
    {
        if (DynamicVars[EntrantNumberKey].BaseValue == -1m)
        {
            // Fully qualified because `EventModel.Rng` shadows the type name,
            // which is the base event's own reason for spelling it out.
            DynamicVars[EntrantNumberKey].BaseValue =
                MegaCrit.Sts2.Core.Random.Rng.Chaotic.NextInt(101, 999);
        }
    }
}
