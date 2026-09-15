using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// ZEN WEAVER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/ZenWeaver.cs` and cross-checked against
/// the harvest (3 options: Breathing Techniques, Emotional Awareness,
/// Arachnid Acupuncture).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three price vars (50, 125,
/// 250), the same gate -- every player holding at least the MIDDLE price --
/// Enlightenment's card hover tip on the first option, the same `_LOCKED`
/// substitution on the second and third when the purse is short, the same two
/// Enlightenments into the deck on the first, and the same remove-then-pay on
/// the other two, one card for the middle price and two for the top.
///
/// THE ORDER INSIDE `RemoveCardsAndProceed` IS LOAD-BEARING: the removal grid
/// opens FIRST and the gold is spent after it, so a player who backs out of
/// the grid has still paid nothing until the selection resolves. The base
/// event's order, kept.
///
/// ONE LOCKED KEY SERVES TWO OPTIONS. `CreateLockedOption` returns
/// `ZEN_WEAVER.pages.INITIAL.options.LOCKED` for BOTH the second and the third
/// -- not `EMOTIONAL_AWARENESS_LOCKED` and `ARACHNID_ACUPUNCTURE_LOCKED` the
/// way Self-Help Book and Tea Master name theirs. So the greyed-out row reads
/// the same whichever option is unaffordable, and the mirror's spec has to
/// pick ONE face line for it. It takes Emotional Awareness's, the cheaper of
/// the two, because that is the one a player sees locked first and most often;
/// this is the same one-source-for-a-shared-key call `TeaMasterMirror`'s
/// `DONE` page makes, and it is a text choice, not a mechanical one.
///
/// THE GATE READS THE MIDDLE PRICE FROM THE VAR, not from a literal, so a
/// change to `EmotionalAwarenessCost` moves the gate with it. Kept as a var
/// read for exactly that reason.
/// </summary>
public abstract class ZenWeaverMirror : TeyvatEventMirror
{
    /// <summary>The base event's own key names.</summary>
    private const string BreathingTechniquesCostKey = "BreathingTechniquesCost";

    private const string EmotionalAwarenessCostKey = "EmotionalAwarenessCost";

    private const string ArachnidAcupunctureCostKey = "ArachnidAcupunctureCost";

    /// <summary>`ZenWeaver.cs:24-29`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar(BreathingTechniquesCostKey, 50m),
            new DynamicVar(EmotionalAwarenessCostKey, 125m),
            new DynamicVar(ArachnidAcupunctureCostKey, 250m),
        };

    /// <summary>The base event's gate: every player at the middle price or
    /// better.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) =>
            (decimal)p.Gold >= DynamicVars[EmotionalAwarenessCostKey].BaseValue);

    /// <summary>Three options, in the base event's order. The second and third
    /// become the SAME locked row when the purse is short.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        int gold = Owner.Gold;
        EventOption breathing = new EventOption(
            this, BreathingTechniques, InitialOptionKey("BREATHING_TECHNIQUES"),
            HoverTipFactory.FromCardWithCardHoverTips<Enlightenment>());
        EventOption emotional = gold < DynamicVars[EmotionalAwarenessCostKey].IntValue
            ? CreateLockedOption()
            : new EventOption(this, EmotionalAwareness, InitialOptionKey("EMOTIONAL_AWARENESS"));
        EventOption arachnid = gold < DynamicVars[ArachnidAcupunctureCostKey].IntValue
            ? CreateLockedOption()
            : new EventOption(this, ArachnidAcupuncture, InitialOptionKey("ARACHNID_ACUPUNCTURE"));

        return new List<EventOption> { breathing, emotional, arachnid };
    }

    /// <summary>`BreathingTechniques`: the 50 is spent FIRST, then two
    /// Enlightenments enter the deck as one add.</summary>
    private async Task BreathingTechniques()
    {
        await PlayerCmd.LoseGold(
            DynamicVars[BreathingTechniquesCostKey].IntValue, Owner, GoldLossType.Spent);
        CardModel[] cards = new CardModel[2];
        for (int i = 0; i < cards.Length; i++)
        {
            cards[i] = Owner.RunState.CreateCard<Enlightenment>(Owner);
        }

        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(cards, PileType.Deck));
        SetEventFinished(L10NLookup(PageKey("BREATHING_TECHNIQUES.description")));
    }

    /// <summary>`EmotionalAwareness`: one card removed for 125.</summary>
    private async Task EmotionalAwareness()
    {
        await RemoveCardsAndProceed(DynamicVars[EmotionalAwarenessCostKey].IntValue, 1);
        SetEventFinished(L10NLookup(PageKey("EMOTIONAL_AWARENESS.description")));
    }

    /// <summary>`ArachnidAcupuncture`: two cards removed for 250.</summary>
    private async Task ArachnidAcupuncture()
    {
        await RemoveCardsAndProceed(DynamicVars[ArachnidAcupunctureCostKey].IntValue, 2);
        SetEventFinished(L10NLookup(PageKey("ARACHNID_ACUPUNCTURE.description")));
    }

    /// <summary>The base event's own helper: the grid FIRST, the gold
    /// after.</summary>
    private async Task RemoveCardsAndProceed(int cost, int count)
    {
        await CardPileCmd.RemoveFromDeck((await CardSelectCmd.FromDeckForRemoval(
            Owner, new CardSelectorPrefs(CardSelectorPrefs.RemoveSelectionPrompt, count)))
            .ToList());
        await PlayerCmd.LoseGold(cost, Owner, GoldLossType.Spent);
    }

    /// <summary>The base event's own: ONE locked key, shared by the second and
    /// third options.</summary>
    private EventOption CreateLockedOption() =>
        new EventOption(this, null, InitialOptionKey("LOCKED"));
}
