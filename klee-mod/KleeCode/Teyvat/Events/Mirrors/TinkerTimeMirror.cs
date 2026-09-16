using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// TINKER TIME, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TinkerTime.cs` and cross-checked against
/// the frozen harvest (a two-step chooser: a card TYPE, then a RIDER, each
/// step offering two of three).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same twelve dynamic vars at the
/// same values (12 damage, 8 block, Weak 2 / Vulnerable 2, three extra hits,
/// Strangle 6, 2 energy, 3 cards, Strength 2 / Dexterity 2, 1 cost reduction,
/// the 1-energy prefix), the same `TakeRandom(2, Rng)` on both steps, the same
/// three riders per type, the same live `MadScience` hover tip built at every
/// step so the card on the tooltip IS the card the option makes, and the same
/// finish: one Mad Science card added to the deck and previewed for three
/// seconds.
///
/// THE RIDER ENUM IS THE BASE EVENT'S, not a copy. `MadScience.TinkerTimeRider`
/// is typed `TinkerTime.RiderEffect`, so the mirror hands the card the base
/// event's own enum values; there is nothing here to drift.
///
/// WHY IT WAS PARKED, AND WHAT UNPARKED IT. Nine riders are offered two at a
/// time and every one of them is a different effect, so no borrowed line could
/// stand in for the other eight -- and none of the nine had a key a face line
/// could pair with by position. The faces carry a KEYED line per rider now,
/// and the same for the three chassis, the two chooser pages, the INITIAL
/// option and the DONE page: sixteen keys, sixteen lines, checked by name.
/// </summary>
public abstract class TinkerTimeMirror : TeyvatEventMirror
{
    private CardType _chosenCardType;

    private CardType ChosenCardType
    {
        get => _chosenCardType;
        set
        {
            AssertMutable();
            _chosenCardType = value;
        }
    }

    /// <summary>`TinkerTime.cs`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(12m, ValueProp.Move),
            new BlockVar(8m, ValueProp.Move),
            new PowerVar<WeakPower>("SappingWeak", 2m),
            new PowerVar<VulnerablePower>("SappingVulnerable", 2m),
            new DynamicVar("ViolenceHits", 3m),
            new PowerVar<StranglePower>("ChokingDamage", 6m),
            new EnergyVar("EnergizedEnergy", 2),
            new CardsVar("WisdomCards", 3),
            new PowerVar<StrengthPower>("ExpertiseStrength", 2m),
            new PowerVar<DexterityPower>("ExpertiseDexterity", 2m),
            new DynamicVar("CuriousReduction", 1m),
            new EnergyVar("energyPrefix", 1),
        };

    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ChooseCardType, InitialOptionKey("CHOOSE_CARD_TYPE")),
        };

    /// <summary>Step one: two of the three chassis, on the event's
    /// `Rng`.</summary>
    private Task ChooseCardType()
    {
        IEnumerable<EventOption> options = new List<EventOption>
        {
            new EventOption(this, Attack, PageKey("CHOOSE_CARD_TYPE.options.ATTACK"),
                GetCardTypeHoverTip(CardType.Attack)),
            new EventOption(this, Skill, PageKey("CHOOSE_CARD_TYPE.options.SKILL"),
                GetCardTypeHoverTip(CardType.Skill)),
            new EventOption(this, Power, PageKey("CHOOSE_CARD_TYPE.options.POWER"),
                GetCardTypeHoverTip(CardType.Power)),
        };
        SetEventState(L10NLookup(PageKey("CHOOSE_CARD_TYPE.description")),
            options.TakeRandom(2, Rng));
        return Task.CompletedTask;
    }

    /// <summary>The tooltip IS the card: a live Mad Science with the type set
    /// and no rider yet, exactly as the base event builds it.</summary>
    private CardHoverTip GetCardTypeHoverTip(CardType cardType)
    {
        MadScience preview = Owner.RunState.CreateCard<MadScience>(Owner);
        preview.TinkerTimeType = cardType;
        preview.TinkerTimeRider = TinkerTime.RiderEffect.None;
        return new CardHoverTip(preview);
    }

    private Task Attack()
    {
        ChosenCardType = CardType.Attack;
        return ChooseRiderEffect();
    }

    private Task Skill()
    {
        ChosenCardType = CardType.Skill;
        return ChooseRiderEffect();
    }

    private Task Power()
    {
        ChosenCardType = CardType.Power;
        return ChooseRiderEffect();
    }

    /// <summary>Step two: the chosen chassis's three riders, two of them,
    /// on the same `Rng`.</summary>
    private Task ChooseRiderEffect()
    {
        List<TinkerTime.RiderEffect> riders = (ChosenCardType switch
        {
            CardType.Attack => new List<TinkerTime.RiderEffect>
            {
                TinkerTime.RiderEffect.Sapping,
                TinkerTime.RiderEffect.Violence,
                TinkerTime.RiderEffect.Choking,
            },
            CardType.Skill => new List<TinkerTime.RiderEffect>
            {
                TinkerTime.RiderEffect.Energized,
                TinkerTime.RiderEffect.Wisdom,
                TinkerTime.RiderEffect.Chaos,
            },
            CardType.Power => new List<TinkerTime.RiderEffect>
            {
                TinkerTime.RiderEffect.Expertise,
                TinkerTime.RiderEffect.Curious,
                TinkerTime.RiderEffect.Improvement,
            },
            _ => throw new ArgumentOutOfRangeException(),
        }).TakeRandom(2, Rng).ToList();

        SetEventState(L10NLookup(PageKey("CHOOSE_RIDER.description")), new List<EventOption>
        {
            new EventOption(this, () => RiderChosen(riders[0]), GetRiderLocKey(riders[0]),
                GetRiderHoverTip(riders[0])),
            new EventOption(this, () => RiderChosen(riders[1]), GetRiderLocKey(riders[1]),
                GetRiderHoverTip(riders[1])),
        });
        return Task.CompletedTask;
    }

    private CardHoverTip GetRiderHoverTip(TinkerTime.RiderEffect rider)
    {
        MadScience preview = Owner.RunState.CreateCard<MadScience>(Owner);
        preview.TinkerTimeType = ChosenCardType;
        preview.TinkerTimeRider = rider;
        return new CardHoverTip(preview);
    }

    private async Task RiderChosen(TinkerTime.RiderEffect rider)
    {
        MadScience made = Owner.RunState.CreateCard<MadScience>(Owner);
        made.TinkerTimeType = ChosenCardType;
        made.TinkerTimeRider = rider;
        CardCmd.PreviewCardPileAdd(await CardPileCmd.Add(made, PileType.Deck), 3f);
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
    }

    /// <summary>
    /// The rider's loc key, re-keyed for THIS dressing. The base event's
    /// switch returns a `TINKER_TIME.` literal per arm; this one returns the
    /// same nine suffixes through <see cref="TeyvatEventMirror.PageKey"/>, so
    /// the nine rows a face writes are the nine the page asks for.
    ///
    /// NOT STATIC, unlike the base's, because `PageKey` reads `Id.Entry`.
    /// </summary>
    private string GetRiderLocKey(TinkerTime.RiderEffect rider) => rider switch
    {
        TinkerTime.RiderEffect.None =>
            throw new ArgumentOutOfRangeException(nameof(rider), rider,
                "None is not a valid rider"),
        TinkerTime.RiderEffect.Sapping => PageKey("CHOOSE_RIDER.options.SAPPING"),
        TinkerTime.RiderEffect.Violence => PageKey("CHOOSE_RIDER.options.VIOLENCE"),
        TinkerTime.RiderEffect.Choking => PageKey("CHOOSE_RIDER.options.CHOKING"),
        TinkerTime.RiderEffect.Energized => PageKey("CHOOSE_RIDER.options.ENERGIZED"),
        TinkerTime.RiderEffect.Wisdom => PageKey("CHOOSE_RIDER.options.WISDOM"),
        TinkerTime.RiderEffect.Chaos => PageKey("CHOOSE_RIDER.options.CHAOS"),
        TinkerTime.RiderEffect.Expertise => PageKey("CHOOSE_RIDER.options.EXPERTISE"),
        TinkerTime.RiderEffect.Curious => PageKey("CHOOSE_RIDER.options.CURIOUS"),
        TinkerTime.RiderEffect.Improvement => PageKey("CHOOSE_RIDER.options.IMPROVEMENT"),
        _ => throw new ArgumentOutOfRangeException(nameof(rider), rider, null),
    };
}
