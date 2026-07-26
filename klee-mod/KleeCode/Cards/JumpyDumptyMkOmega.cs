using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Cards.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Klee's Ancient-rarity card, the top of the Jumpy Dumpty family
/// (basic -> Mk.II -> this). Dusty Tome is its only door: reward, transform
/// and shop generation all filter CardRarity.Ancient upstream (decompiled
/// CardFactory), so membership in RosterAncientCards.Klee does not make it
/// rollable. DustyTome.AfterObtained upgrades the grant, so the card is
/// designed to be READ at its upgraded numbers -- the base line exists for
/// smith-less acquisition paths (e.g. a future transform-to-ancient effect).
///
/// User ruling 2026-07-23 (act-2 Darv softlock fix): "an upscaled Jumpty
/// Dumpty ... scaled to the rest of the Ancient rewards". Hand-written and
/// outside the ratified sheets: the sim models neither events nor relics,
/// so Ancient cards are game-side-only content (DECISIONS entry 2026-07-23).
/// Title pending the naming/lore audit.
/// </summary>
public sealed class JumpyDumptyMkOmega : CustomCardModel, IElementalCard, ISkillTagCard
{
    /// <summary>Family trait: all Klee attacks apply Pyro.</summary>
    public Element Element => Element.Pyro;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.ElementalSkill, KleeKeywords.AppliesPyro };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro, includesBombRules: true);

    // Art: deliberate family reuse of the Mk.II portrait until the art pass
    // assigns the ancient its own crop (look-pass item, not a blocker).
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("jumpy_dumpty_mk2");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Jumpy Dumpty Mk.Omega"),
        ("description", "Deal {Damage:diff()} damage to random enemies 3 times. Place a [gold]Bomb[/gold] on EVERY enemy dealing {ExtraDamage:diff()} damage."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(12m, ValueProp.Move),
            new ExtraDamageVar(12m)
        };

    // autoAdd: false -- RosterAncientCards.Klee owns membership (concat into
    // KleeCardPool.GenerateAllCards), same discipline as every pool card.
    public JumpyDumptyMkOmega()
        : base(2, CardType.Attack, CardRarity.Ancient, TargetType.AllEnemies, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .WithHitCount(3)
            .FromCard(this)
            .TargetingRandomOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
        foreach (var enemy in CombatState!.HittableEnemies.ToList())
        {
            await BombPower.Place(
                choiceContext, enemy, (int)DynamicVars.ExtraDamage.BaseValue,
                Owner.Creature, this);
        }
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(4m);
        DynamicVars.ExtraDamage.UpgradeValueBy(4m);
    }
}
