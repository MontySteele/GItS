using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SLIPPERY BRIDGE, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SlipperyBridge.cs` and cross-checked
/// against the frozen harvest (2 options: Overcome, Hold On).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same 3 + hold-ons HP price, the
/// same unblockable unpowered damage, the same reroll rules (never a Basic
/// on the FIRST pick unless the deck is all Basic, never a card already
/// skipped, never one of the same TYPE as the card just refused, and a
/// fall-back to the whole removable deck when those leave nothing), the same
/// rain VFX on room entry, and the same two options offered again and again
/// until Overcome is taken.
///
/// THIS IS THE FIRST MULTI-PAGE MIRROR, and its pages are the reason the
/// mirror ledger grew a `pages` list. The base event builds its later keys by
/// CONCATENATION -- `"SLIPPERY_BRIDGE.pages.HOLD_ON_" + suffix` -- so the
/// index's literal scrape can only see the stub `pages.HOLD_ON_`, which is a
/// key nothing ever looks up. The eight pages a run can actually reach are
/// enumerated in <see cref="HoldOnPages"/> instead, spelled out one literal per
/// key so the pin that compares a mirror's literals to its shape can see
/// them.
///
/// THE SUFFIX RULE IS THE BASE EVENT'S: `GetHoldOnSuffix` answers the
/// hold-on ordinal below seven and `LOOP` at seven or above, so the pages run
/// 0, 1, ... 6, LOOP and then LOOP for ever. The option on each page carries
/// the NEXT ordinal, which is what lets its title print the next price.
/// </summary>
public abstract class SlipperyBridgeMirror : TeyvatEventMirror
{
    /// <summary>
    /// The eight reachable Hold On pages, in order: the page's own
    /// description key and the Hold On option key that page offers.
    ///
    /// WRITTEN OUT RATHER THAN BUILT. The base event concatenates; a mirror
    /// that did the same would carry the literals `HOLD_ON_` and `LOOP`,
    /// which are not loc keys and which
    /// `A_mirrors_key_literals_are_exactly_its_shape` would read as keys the
    /// shape does not have. One literal per key is the same eight keys with
    /// nothing for that pin to trip on.
    ///
    /// AN INSTANCE PROPERTY AND NOT A STATIC FIELD, because that pin reads
    /// the mirror's INSTANCE methods: a static field initialiser compiles
    /// into the type initialiser, which `Type.GetMethods` does not return at
    /// all, and eight page keys the pin cannot see would read as eight keys
    /// the mirror never asks for.
    /// </summary>
    private (string Description, string Option)[] HoldOnPages => new[]
    {
        ("HOLD_ON_0.description", "HOLD_ON_0.options.HOLD_ON_1"),
        ("HOLD_ON_1.description", "HOLD_ON_1.options.HOLD_ON_2"),
        ("HOLD_ON_2.description", "HOLD_ON_2.options.HOLD_ON_3"),
        ("HOLD_ON_3.description", "HOLD_ON_3.options.HOLD_ON_4"),
        ("HOLD_ON_4.description", "HOLD_ON_4.options.HOLD_ON_5"),
        ("HOLD_ON_5.description", "HOLD_ON_5.options.HOLD_ON_6"),
        ("HOLD_ON_6.description", "HOLD_ON_6.options.HOLD_ON_LOOP"),
        ("HOLD_ON_LOOP.description", "HOLD_ON_LOOP.options.HOLD_ON_LOOP"),
    };

    private int _numberOfHoldOns;

    private CardModel _randomCardToLose;

    private HashSet<CardModel> _skippedRemovals;

    private int NumberOfHoldOns
    {
        get => _numberOfHoldOns;
        set
        {
            AssertMutable();
            _numberOfHoldOns = value;
        }
    }

    private CardModel RandomCardToLose
    {
        get => _randomCardToLose;
        set
        {
            AssertMutable();
            _randomCardToLose = value;
        }
    }

    private HashSet<CardModel> SkippedRemovals
    {
        get => _skippedRemovals;
        set
        {
            AssertMutable();
            _skippedRemovals = value;
        }
    }

    /// <summary>`SlipperyBridge.cs`: 3, plus one per Hold On already
    /// taken.</summary>
    private int CurrentHpLoss => 3 + NumberOfHoldOns;

    /// <summary>The base event's two vars: the card about to fall, named, and
    /// the live HP price.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new StringVar("RandomCard"),
            new DynamicVar("HpLoss", CurrentHpLoss),
        };

    /// <summary>
    /// The base event's gate, both clauses: past floor 6, and every player
    /// holding at least one REMOVABLE card -- the event's whole premise being
    /// that something goes over the rail.
    /// </summary>
    public override bool IsAllowed(IRunState runState)
    {
        if (runState.TotalFloor > 6)
        {
            return runState.Players.All((Player p) => p.Deck.Cards.Any((CardModel c) => c.IsRemovable));
        }

        return false;
    }

    /// <summary>
    /// Two options, in the base event's order, under its names. The first
    /// card is rolled here, before the options are built, because the Overcome
    /// option's hover tip IS that card.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        GetNewRandomCard();
        return new List<EventOption>
        {
            new EventOption(this, Overcome, InitialOptionKey("OVERCOME"),
                HoverTipFactory.FromCard(RandomCardToLose)),
            new EventOption(this, HoldOn, InitialOptionKey("HOLD_ON_0"))
                .ThatDoesDamage(CurrentHpLoss),
        };
    }

    /// <summary>The base event's rain, on the base event's hook.</summary>
    public override void OnRoomEnter()
    {
        NEventRoom.Instance?.VfxContainer?.AddChildSafely(NRainVfx.Create());
    }

    /// <summary>
    /// The base event's reroll, clause for clause. The FIRST pick excludes
    /// Basic rarity; every later one excludes the type just refused and every
    /// card already skipped; and when either leaves nothing the whole
    /// removable deck comes back.
    /// </summary>
    private void GetNewRandomCard()
    {
        List<CardModel> candidates;
        if (RandomCardToLose == null)
        {
            candidates = Owner.Deck.Cards.Where((CardModel c) => c.Rarity != CardRarity.Basic).ToList();
        }
        else
        {
            if (SkippedRemovals == null)
            {
                SkippedRemovals = new HashSet<CardModel>();
            }

            SkippedRemovals.Add(RandomCardToLose);
            candidates = Owner.Deck.Cards
                .Where((CardModel c) => c.GetType() != RandomCardToLose.GetType()).ToList();
        }

        candidates.RemoveAll((CardModel c) => !c.IsRemovable || (SkippedRemovals?.Contains(c) ?? false));
        if (candidates.Count == 0)
        {
            candidates = Owner.Deck.Cards.Where((CardModel c) => c.IsRemovable).ToList();
        }

        RandomCardToLose = Rng.NextItem(candidates);
        StringVar named = (StringVar)DynamicVars["RandomCard"];
        named.StringValue = RandomCardToLose.Title;
    }

    /// <summary>`Overcome`: the named card leaves the deck and the event
    /// ends.</summary>
    private async Task Overcome()
    {
        await CardPileCmd.RemoveFromDeck(RandomCardToLose);
        SetEventFinished(L10NLookup(PageKey("OVERCOME.description")));
    }

    /// <summary>
    /// `HoldOn`: the price, then the reroll, then the SAME two options again
    /// on the next page. The page and its option are read out of
    /// <see cref="HoldOnPages"/> at the ordinal the base event's
    /// `GetHoldOnSuffix` would have produced -- the last row standing in for
    /// every hold-on past the seventh, which is what `LOOP` means.
    /// </summary>
    private async Task HoldOn()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, CurrentHpLoss,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null);
        NumberOfHoldOns++;
        DynamicVars["HpLoss"].BaseValue = CurrentHpLoss;
        GetNewRandomCard();

        (string Description, string Option)[] pages = HoldOnPages;
        int index = NumberOfHoldOns - 1;
        if (index >= pages.Length)
        {
            index = pages.Length - 1;
        }

        (string Description, string Option) page = pages[index];

        SetEventState(L10NLookup(PageKey(page.Description)), new List<EventOption>
        {
            new EventOption(this, Overcome, InitialOptionKey("OVERCOME"),
                HoverTipFactory.FromCard(RandomCardToLose)),
            new EventOption(this, HoldOn, PageKey(page.Option))
                .ThatDoesDamage(CurrentHpLoss),
        });
    }
}
