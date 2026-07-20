using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Klee's basic attack. Sheet: cost 1, damage 6, single target.
/// Mechanically identical to StrikeSilent — this is the intended reskin.
/// </summary>
public sealed class Kaboom : CustomCardModel, IElementalCard
{
    /// <summary>All of Klee's attacks apply Pyro (sheet: catalyst-grade cadence).</summary>
    public Element Element => Element.Pyro;

    /// <summary>Loose-PNG art, no .pck. File is images/cards/kaboom.png.</summary>
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("kaboom");

    /// <summary>
    /// Loc MUST live here, not in KleeMod's hand-rolled dictionary. BaseLib
    /// prefixes custom model ids (KABOOM -> KLEEMOD-KABOOM), so a hardcoded
    /// "KABOOM.title" key silently targets an id that no longer exists and the
    /// UI renders the raw key. BaseLib writes these against Id.Entry itself
    /// (see AddModelLoc), so the key can never drift out of sync.
    ///
    /// Syntax is copied from the base game verbatim (STRIKE_SILENT reads
    /// "Deal {Damage:diff()} damage."): single braces, and :diff() renders the
    /// upgrade delta in green.
    /// </summary>
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kaboom!"),
        ("description", "Deal {Damage:diff()} damage."),
    };

    protected override HashSet<CardTag> CanonicalTags => new() { CardTag.Strike };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new DamageVar(6m, ValueProp.Move) };

    // autoAdd: false -- BaseLib's auto-registration demands a [Pool] attribute
    // and calls AddModelToPool itself. KleeCardPool already lists its own cards
    // in GenerateAllCards, so letting BaseLib register them too would double-add.
    // We want CustomCardModel purely for CustomPortrait. Boot crash 2026-07-20:
    // "must be marked with a PoolAttribute to determine which pool to add it to".
    public Kaboom()
        : base(1, CardType.Attack, CardRarity.Basic, TargetType.AnyEnemy, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .Targeting(cardPlay.Target)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(3m);
    }
}
