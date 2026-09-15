using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// TABLET OF TRUTH, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TabletOfTruth.cs` and cross-checked
/// against the frozen harvest (Smash, Decipher, and a Give Up the wiki lists
/// beside them).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two vars (20 heal, 3 Max HP),
/// the same escalating price ladder 3 / 6 / 12 / 24 / all-but-one, the same
/// single random upgrade on stages one to four and the whole deck on five, the
/// same `ThatWillKillPlayerIf` on every Decipher, and the same kill when the
/// price is not less than the Max HP left.
///
/// GIVE UP IS A LATER PAGE'S OPTION, AND IT IS WHY THIS EVENT WAS PARKED. The
/// INITIAL page offers two options; the face writes three lines, because the
/// wiki lists Give Up inline with them and so did the curation. The third line
/// now pairs with `pages.DECIPHER.options.GIVE_UP` -- a full-suffix key in the
/// mirror ledger's `options` list -- which is the same device Dense
/// Vegetation's `REST.options.FIGHT` uses, except that here the later option
/// HAS a line of its own rather than borrowing one.
///
/// THE DECIPHER PAGES ARE WRITTEN OUT, NOT BUILT. The base event interpolates
/// `$"TABLET_OF_TRUTH.pages.DECIPHER_{DecipherCount}.description"`, which
/// leaves the index a stub nothing looks up and would leave this mirror
/// carrying the fragment `DECIPHER_` as a literal. Five description keys and
/// four option keys, one literal each, is the same set with nothing for
/// `A_mirrors_key_literals_are_exactly_its_shape` to trip on -- the same
/// choice <see cref="SlipperyBridgeMirror"/> makes and for the same reason,
/// and an INSTANCE property for the same one too.
/// </summary>
public abstract class TabletOfTruthMirror : TeyvatEventMirror
{
    /// <summary>
    /// The five reachable Decipher pages: the page's own description key, and
    /// the Decipher option that page offers. The fifth page offers nothing --
    /// `DecipherCount == 5` finishes the event -- which is why its option
    /// entry is null and why the base game ships no
    /// `DECIPHER_5.options.DECIPHER` row.
    /// </summary>
    private (string Description, string Option)[] DecipherPages => new[]
    {
        ("DECIPHER_1.description", "DECIPHER_1.options.DECIPHER"),
        ("DECIPHER_2.description", "DECIPHER_2.options.DECIPHER"),
        ("DECIPHER_3.description", "DECIPHER_3.options.DECIPHER"),
        ("DECIPHER_4.description", "DECIPHER_4.options.DECIPHER"),
        ("DECIPHER_5.description", (string)null),
    };

    private int _decipherCount;

    private int DecipherCount
    {
        get => _decipherCount;
        set
        {
            AssertMutable();
            _decipherCount = value;
        }
    }

    /// <summary>`TabletOfTruth.cs:33-37`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("SmashHPGain", 20m),
            new DynamicVar("DecipherMaxHpLoss", 3m),
        };

    /// <summary>Two options, in the base event's order, under its names. The
    /// first Decipher is already lethal-marked: the price is checked against
    /// MAX HP, not current, because that is what the stone takes.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Decipher, InitialOptionKey("DECIPHER_1"))
                .ThatWillKillPlayerIf((Player p) =>
                    (decimal)p.Creature.MaxHp <= DynamicVars["DecipherMaxHpLoss"].BaseValue),
            new EventOption(this, Smash, InitialOptionKey("SMASH")),
        };

    /// <summary>`Smash`: the heal, and the end of it.</summary>
    private async Task Smash()
    {
        Creature creature = Owner.Creature;
        await CreatureCmd.Heal(creature, DynamicVars["SmashHPGain"].BaseValue);
        SetEventFinished(L10NLookup(PageKey("SMASH.description")));
    }

    /// <summary>
    /// `Decipher`: pay, upgrade, then either finish on the fifth page or
    /// re-price and offer the pair again. The counter is incremented BEFORE
    /// the page is chosen, which is what makes the first press land on
    /// `DECIPHER_1` and the fifth on `DECIPHER_5`.
    /// </summary>
    private async Task Decipher()
    {
        await LoseMaxHpAndUpgrade(DynamicVars["DecipherMaxHpLoss"].BaseValue);
        DecipherCount++;
        (string description, string option) = DecipherPages[DecipherCount - 1];
        if (DecipherCount == 5)
        {
            SetEventFinished(L10NLookup(PageKey(description)));
            return;
        }

        DynamicVars["DecipherMaxHpLoss"].BaseValue = GetDecipherCost();
        SetEventState(L10NLookup(PageKey(description)), new List<EventOption>
        {
            new EventOption(this, Decipher, PageKey(option))
                .ThatWillKillPlayerIf((Player p) =>
                    (decimal)p.Creature.MaxHp <= DynamicVars["DecipherMaxHpLoss"].BaseValue),
            new EventOption(this, GiveUp, PageKey("DECIPHER.options.GIVE_UP")),
        });
    }

    /// <summary>The base event's ladder: 6, 12, 24, then everything but one.
    /// The default arm logs and answers an absurd number, which is the base
    /// event's own way of making an impossible count loud.</summary>
    public int GetDecipherCost()
    {
        Player owner = Owner;
        switch (DecipherCount)
        {
            case 1:
                return 6;
            case 2:
                return 12;
            case 3:
                return 24;
            case 4:
                return owner.Creature.MaxHp - 1;
            default:
                Log.Error($"DecipherCount: {DecipherCount} should not be called.");
                return 999999999;
        }
    }

    /// <summary>`GiveUp`: its own page, and nothing paid for it.</summary>
    private Task GiveUp()
    {
        SetEventFinished(L10NLookup(PageKey("GIVE_UP.description")));
        return Task.CompletedTask;
    }

    /// <summary>
    /// The base event's payment, both branches. A price that is not LESS than
    /// the Max HP left takes all but one and then kills -- the order matters,
    /// because the run history reads the Max HP the tablet took. Below that,
    /// the fourth press upgrades the whole deck one card at a time with the
    /// base event's own waits; every other press upgrades one random
    /// upgradable card.
    /// </summary>
    private async Task LoseMaxHpAndUpgrade(decimal hp)
    {
        if (!(hp < (decimal)Owner.Creature.MaxHp))
        {
            await CreatureCmd.LoseMaxHp(new ThrowingPlayerChoiceContext(), Owner.Creature,
                Owner.Creature.MaxHp - 1, isFromCard: false);
            await CreatureCmd.Kill(Owner.Creature);
            return;
        }

        await CreatureCmd.LoseMaxHp(new ThrowingPlayerChoiceContext(), Owner.Creature, hp,
            isFromCard: false);
        List<CardModel> upgradable = PileType.Deck.GetPile(Owner).Cards
            .Where((CardModel c) => c.IsUpgradable).ToList();
        if (_decipherCount == 4)
        {
            foreach (CardModel card in upgradable)
            {
                CardCmd.Upgrade(card, CardPreviewStyle.MessyLayout);
                await Cmd.CustomScaledWait(0.1f, 0.2f);
            }

            await Cmd.CustomScaledWait(0.6f, 1.2f);
        }
        else if (upgradable.Count != 0)
        {
            CardModel card = Rng.NextItem(upgradable);
            CardCmd.Upgrade(card, CardPreviewStyle.EventLayout);
        }
    }
}
