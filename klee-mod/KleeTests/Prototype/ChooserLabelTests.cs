using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE CHOOSER PRINTS WORDS, NEVER A TEMPLATE (Furina v2 seat round,
/// 2026-10-04). Interval Bell's Spend mode was titled by the part of its label
/// before the first colon, and its label was
/// "Spend {IfUpgraded:show:2|3}: ..." -- so the chooser offered an option
/// named "Spend {IfUpgraded". A card title carries no SmartFormat, and the
/// bridge prints <c>ModeLabels</c> verbatim, so neither may hold a brace.
/// </summary>
public class ChooserLabelTests
{
    private static IEnumerable<Type> Concrete<T>() =>
        typeof(ModalOptionCard).Assembly.GetTypes()
            .Where(t => typeof(T).IsAssignableFrom(t) && !t.IsAbstract
                        && t.GetConstructor(Type.EmptyTypes) != null);

    private static CardModel Upgraded(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel)
            .GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, null);
        return card;
    }

    [Fact]
    public void No_mode_option_title_contains_a_brace()
    {
        var options = Concrete<ModalOptionCard>().ToList();
        Assert.NotEmpty(options);
        foreach (var type in options)
        {
            var card = (ModalOptionCard)Activator.CreateInstance(type)!;
            // A hand-written option that registers its rows elsewhere
            // carries no Localization of its own.
            foreach (var (key, title) in card.Localization
                     ?? new List<(string, string)>())
            {
                if (key != "title") continue;
                Assert.False(title.Contains('{'), $"{type.Name} title: {title}");
            }
        }
    }

    [Fact]
    public void No_mode_label_contains_a_brace_upgraded_or_not()
    {
        var modal = Concrete<IModalCard>().Where(t => typeof(CardModel)
            .IsAssignableFrom(t)).ToList();
        Assert.NotEmpty(modal);
        foreach (var type in modal)
        {
            foreach (var upgraded in new[] { false, true })
            {
                var card = (CardModel)Activator.CreateInstance(type)!;
                if (upgraded && card.IsUpgradable) Upgraded(card);
                foreach (var label in ((IModalCard)card).ModeLabels)
                {
                    Assert.False(label.Contains('{'),
                        $"{type.Name} (upgraded={upgraded}) label: {label}");
                }
            }
        }
    }

    [Fact]
    public void Interval_Bell_spend_option_reads_its_price_on_both_sides()
    {
        var plain = new ProtoFsIntervalBellModeB();
        Assert.Equal("Spend 3",
            plain.Localization!.Single(r => r.Item1 == "title").Item2);
        Assert.Equal("Spend 2+", Upgraded(new ProtoFsIntervalBellModeB()).Title);

        Assert.Contains(new ProtoFsIntervalBell().ModeLabels,
            l => l.StartsWith("[gold]Spend[/gold] 3:"));
        Assert.Contains(
            ((IModalCard)Upgraded(new ProtoFsIntervalBell())).ModeLabels,
            l => l.StartsWith("[gold]Spend[/gold] 2:"));
    }
}
