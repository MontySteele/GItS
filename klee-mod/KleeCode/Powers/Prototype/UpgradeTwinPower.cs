using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// ONE BADGE FOR A POWER CARD AND ITS UPGRADE (the icon declutter, 2026-10-19,
/// [USER]: "can we do a search over all of the things in each kit that still
/// print a status icon and see if they're 'really' needed? I've noticed that
/// our characters tend to make a lot of icons.").
///
/// Alice's Detonator, Prima Donna and Kurage Canopy each installed one of two
/// powers, the plain one or a "+" twin, so a deck holding both versions showed
/// two badges for one rule. Each is now ONE power: its Amount is every copy
/// installed, and <see cref="UpgradedCopies"/> counts the copies an upgraded
/// card installed. Together they say exactly what the two powers' Amounts
/// said, so every rule that read the pair reads the same numbers.
///
/// <see cref="UpgradedFirst"/> keeps the one thing the pair also carried:
/// ORDER. Two powers acted in the order they landed on the creature, so a
/// rule that adds cards one batch after the other (Alice's Mines, Kurage
/// Canopy's Wards) still adds the batch whose card was played first, first.
///
/// The count is a plain field (a value type, so <c>MutableClone</c>'s shallow
/// copy carries it) mirrored into the <c>Upgraded</c> dynamic var for the
/// hover text.
/// </summary>
public abstract class UpgradeTwinPower : PowerModel
{
    private int _upgraded;

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Upgraded", 0m), new("Plain", 0m),
    };

    /// <summary>Copies an upgraded card installed, never more than the
    /// Amount.</summary>
    public int UpgradedCopies => Math.Clamp(_upgraded, 0, Math.Max(0, (int)Amount));

    /// <summary>Copies a plain card installed.</summary>
    public int PlainCopies => Math.Max(0, (int)Amount - UpgradedCopies);

    /// <summary>Did an upgraded card install this power first? Then its
    /// batch acts before the plain one, as the "+" twin did when it landed
    /// first.</summary>
    public bool UpgradedFirst { get; private set; }

    /// <summary>
    /// Record what one play added. <paramref name="added"/> is the Amount the
    /// play actually moved (whatever the modifier chain made of the printed
    /// number, as the twin's own Amount would have been);
    /// <paramref name="fresh"/> says this play created the power.
    /// </summary>
    public void NoteCopies(int added, bool upgraded, bool fresh)
    {
        if (fresh)
        {
            _upgraded = 0;
            UpgradedFirst = upgraded;
        }
        if (upgraded && added > 0) _upgraded += added;
        if (!IsMutable) return;
        DynamicVars["Upgraded"].BaseValue = UpgradedCopies;
        DynamicVars["Plain"].BaseValue = PlainCopies;
    }

    /// <summary>The copies in the order they act: (count, upgraded) per
    /// batch, empty batches left out. PURE.</summary>
    public static IReadOnlyList<(int Count, bool Upgraded)> Batches(
        int plain, int upgraded, bool upgradedFirst)
    {
        var batches = upgradedFirst
            ? new[] { (upgraded, true), (plain, false) }
            : new[] { (plain, false), (upgraded, true) };
        return batches.Where(b => b.Item1 > 0).ToList();
    }

    /// <summary>This power's batches, in order.</summary>
    public IReadOnlyList<(int Count, bool Upgraded)> Batches() =>
        Batches(PlainCopies, UpgradedCopies, UpgradedFirst);

    /// <summary>
    /// The card's play: apply <typeparamref name="T"/> and note whether the
    /// card was upgraded. What each twin's own <c>PowerCmd.Apply</c> did,
    /// into one power.
    /// </summary>
    public static async Task Install<T>(
        PlayerChoiceContext choiceContext, Creature? target, decimal amount,
        bool upgraded, Creature? applier, CardModel? cardSource)
        where T : UpgradeTwinPower
    {
        if (target == null) return;
        var before = target.Powers.OfType<T>().FirstOrDefault();
        var was = before?.Amount ?? 0m;
        await PowerCmd.Apply<T>(choiceContext, target, amount,
                                applier: applier, cardSource: cardSource);
        var now = target.Powers.OfType<T>().FirstOrDefault();
        if (now == null) return;
        var fresh = !ReferenceEquals(now, before);
        now.NoteCopies((int)(now.Amount - (fresh ? 0m : was)), upgraded, fresh);
    }
}
