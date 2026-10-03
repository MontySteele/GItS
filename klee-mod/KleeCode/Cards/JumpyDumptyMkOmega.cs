using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
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
/// (basic -> Mk.III -> this; Mk.II under the old shipped kits). Dusty Tome is
/// its only door: reward, transform and shop generation all filter
/// CardRarity.Ancient upstream (decompiled
/// CardFactory), so membership in RosterAncientCards.Klee does not make it
/// rollable. DustyTome.AfterObtained upgrades the grant, so the card is
/// designed to be READ at its upgraded numbers -- the base line exists for
/// smith-less acquisition paths (e.g. a future transform-to-ancient effect).
///
/// User ruling 2026-07-23 (act-2 Darv softlock fix): "an upscaled Jumpty
/// Dumpty ... scaled to the rest of the Ancient rewards". Hand-written and
/// outside the ratified sheets: the sim models neither events nor relics,
/// so Ancient cards are game-side-only content (DECISIONS entry 2026-07-23).
///
/// It places the Klee overhaul's Bomb (a plain <see cref="ProtoBombPower"/>
/// charge of the same size on every enemy), which never goes off by itself
/// (rule 7). R276 hygiene; its shipped Bomb went with the shipped kits.
/// </summary>
public sealed class JumpyDumptyMkOmega : CustomCardModel, IElementalCard
{
    /// <summary>Family trait: all Klee attacks apply Pyro.</summary>
    public Element Element => Element.Pyro;

    /// <summary>Applies Pyro alone: Klee has no Burst meter, so the
    /// <c>Elemental Skill</c> keyword went (2026-09-26, wave-3 Klee lane 2b).
    /// </summary>
    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.AppliesPyro };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForBomb(
            KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro,
                                     includesBombRules: false), this);

    // Art: deliberate family reuse of the Mk.II portrait until the art pass
    // assigns the ancient its own crop (look-pass item, not a blocker).
    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("jumpy_dumpty_mk2");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Jumpy Dumpty Mk.Omega"),
        ("description", "Deal {Damage:diff()} [gold]Pyro[/gold] damage to a random enemy 3 times. Place a [gold]Bomb[/gold] {BombDamage:diff()} on ALL enemies."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(12m, ValueProp.Move),
            // EB-230: the bomb payload is a plain var, not an attack var --
            // BombPower banks it literally, so the face must not resolve it
            // against live attack modifiers.
            new DynamicVar("BombDamage", 12m)
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
            .FromCard(this, cardPlay)
            .TargetingRandomOpponents(CombatState!)
            .WithElementHitFx(this)
            .Execute(choiceContext);
        // The arm's Bomb, the arm's placer: a plain charge on every living
        // enemy, which never goes off by itself (rule 7).
        await ProtoBombPower.PlaceOnAll(
            choiceContext, Owner.Creature,
            (int)DynamicVars["BombDamage"].BaseValue, isMine: false,
            payloadMineAll: 0, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(4m);
        DynamicVars["BombDamage"].UpgradeValueBy(4m);
    }
}
