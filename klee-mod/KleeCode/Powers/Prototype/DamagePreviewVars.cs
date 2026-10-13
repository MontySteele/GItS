using System;
using System.Linq;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE DAMAGE PREVIEWS PASS (2026-10-13). [USER]: "Are there any other cards,
/// in any pool, that don't show how much damage they actually do when
/// accounting for conditional modifiers?" Display only: every var in this
/// file prints an in-combat line (<c>{InCombat:\n(Deals N damage)|}</c>, the
/// base game's Body Slam shape) and nothing reads it in play -- each card's
/// <c>OnPlay</c> still reads its own vars and counts, unchanged.
///
/// ONE BODY RULE: the body a face folds against is
/// <see cref="FoldedPreview.Body"/>'s (the aimed enemy, else the front one;
/// on a Furina Stage board the base game's own convention), the one
/// <see cref="FrontFoldedDamageVar"/> and Varka's <c>{VkHit}</c> take.
///
/// QUARANTINED under <c>Powers/Prototype/</c>, emitted by codegen for
/// <c>proto_</c> rows only, and only where the face prints the token
/// (<c>gen_klee_cards.preview_token_vars</c>).
/// </summary>
public static class DamagePreview
{
    /// <summary>The body a face previews against, or null.</summary>
    public static Creature? Body(CardModel card, CardPreviewMode previewMode,
                                 Creature? target)
    {
        var owner = card.Owner?.Creature;
        return FoldedPreview.Body(
            FurinaStage.LiveFor(owner), card, previewMode, target,
            KokomiPlan.FrontEnemy(owner));
    }

    /// <summary>Is this a card in play with an owner to read?</summary>
    public static bool Live(CardModel card, bool runGlobalHooks) =>
        runGlobalHooks && card.IsMutable && card.Owner?.Creature != null;

    /// <summary>What a Set off of <paramref name="target"/> by
    /// <paramref name="applier"/> would deal now, under a Set off
    /// <paramref name="multiplier"/>: the sum of her piles' badge numbers
    /// (<see cref="ProtoBombPower.PredictedSetOffDamage(int)"/>). PURE.
    /// </summary>
    public static int SetOffOn(Creature? target, Creature? applier,
                               int multiplier = 1)
    {
        if (target == null || applier == null) return 0;
        var total = 0;
        foreach (var pile in target.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier == applier)
            {
                total += pile.PredictedSetOffDamage(multiplier);
            }
        }
        return total;
    }

    /// <summary>Is <paramref name="body"/> Vulnerable right now?</summary>
    public static bool Vulnerable(Creature? body) =>
        body != null
        && (body.Powers.OfType<VulnerablePower>().FirstOrDefault()?.Amount
            ?? 0) > 0;

    /// <summary>A total of <paramref name="hits"/> hits that each land
    /// <paramref name="perHit"/> (the folded preview of one): each hit
    /// truncates on its own, as the game deals them. PURE.</summary>
    public static decimal HitsTotal(decimal perHit, int hits) =>
        hits <= 0 ? 0m : decimal.Floor(Math.Max(0m, perHit)) * hits;

    /// <summary>Drowning Pressure's count after its own Weak 1 and
    /// Vulnerable 1: an Artifact stack negates the Weak first, a second one
    /// the Vulnerable. Returns (stacks, whether the Vulnerable lands). PURE.
    /// </summary>
    public static (int Stacks, bool VulnerableLands) AfterOwnDebuffs(
        int stacksNow, int artifact)
    {
        var weakLands = artifact < 1;
        var vulnerableLands = artifact < 2;
        return (stacksNow + (weakLands ? 1 : 0) + (vulnerableLands ? 1 : 0),
                vulnerableLands);
    }
}

/// <summary>
/// "(Deals N damage)" for a card that hits a counted number of times
/// (Fireworks Finale's Sparks, Shoal of Spears' Plans, Bravura's Fanfare):
/// one hit of the card's <c>Damage</c> folded the game's way, times the count
/// the play will take. Strength counts once per hit, as it is dealt.
/// </summary>
public sealed class HitsTotalDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "TotalDamage";

    private readonly Func<CardModel, int> _hits;

    public HitsTotalDamageVar(Func<CardModel, int> hits)
        : base(Token, 0m, ValueProp.Move)
    {
        _hits = hits;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        var perHit = card.DynamicVars.Damage.BaseValue;
        if (!DamagePreview.Live(card, runGlobalHooks))
        {
            BaseValue = perHit;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var hits = Math.Max(0, _hits(card));
        var body = DamagePreview.Body(card, previewMode, target);
        var one = new DamageVar(perHit, ValueProp.Move);
        one.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        BaseValue = perHit * hits;
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        PreviewValue = DamagePreview.HitsTotal(one.PreviewValue, hits);
    }
}

/// <summary>
/// Simmer and Taste Test: "(Deals N damage)", the hit
/// <see cref="ProtoBombPower.DealFromBombs"/> deals -- the printed flat part
/// (<c>Damage</c>, 0 where the row prints none) plus the Bomb read
/// (<see cref="ProtoBombPower.BombReadDamage"/>, the play's own arithmetic),
/// folded the game's way. A read of 0 deals nothing and prints 0.
/// </summary>
public sealed class BombReadDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "BombHit";

    public ProtoBombPower.BombRead Read { get; }

    public BombReadDamageVar(ProtoBombPower.BombRead read)
        : base(Token, 0m, ValueProp.Move)
    {
        Read = read;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        var flat = card.DynamicVars.TryGetValue("Damage", out var d)
            ? d.BaseValue
            : 0m;
        if (!DamagePreview.Live(card, runGlobalHooks))
        {
            BaseValue = flat;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var body = DamagePreview.Body(card, previewMode, target);
        BaseValue = ProtoBombPower.BombReadDamage(
            body, card.Owner!.Creature!, flat, Read);
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        if (BaseValue <= 0) PreviewValue = 0m;
    }
}

/// <summary>
/// Big Badda Boom's second hit: "(Then deals N damage)". What the Bombs on
/// the body would deal now (the badges' number,
/// <see cref="DamagePreview.SetOffOn"/>) with the body's Vulnerable taken back
/// out as <see cref="KleeOverhaulLedger.EchoBase"/> takes it, then folded as
/// the card's own hit, which lands after the Bombs and so meets no aura
/// (<see cref="AuraPower.PreviewWithoutReaction"/>). No Bombs, no hit: 0.
/// </summary>
public sealed class SetOffEchoDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "BombEcho";

    public SetOffEchoDamageVar() : base(Token, 0m, ValueProp.Move)
    {
    }

    /// <summary>The echo's number before the card's own fold. PURE.</summary>
    public static decimal EchoBase(int bombsDeal, bool vulnerable) =>
        bombsDeal <= 0 ? 0m : KleeOverhaulLedger.EchoBase(bombsDeal, vulnerable);

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        if (!DamagePreview.Live(card, runGlobalHooks))
        {
            BaseValue = 0m;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var body = DamagePreview.Body(card, previewMode, target);
        BaseValue = EchoBase(
            DamagePreview.SetOffOn(body, card.Owner!.Creature),
            DamagePreview.Vulnerable(body));
        using (AuraPower.PreviewWithoutReaction())
        {
            base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        }
        if (BaseValue <= 0) PreviewValue = 0m;
    }
}

/// <summary>
/// The Big One: "(Bombs deal N damage)", the badges' arithmetic under the
/// row's own multiplier (<see cref="ProtoBombPower.PredictedSetOffDamage(int)"/>).
/// A Bomb carries the target's terms and none of Klee's (R248), so this is a
/// plain var, not a damage var: no Strength or Weak is folded.
/// </summary>
public sealed class SetOffBombsVar : DynamicVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "SetOffBombs";

    public int Multiplier { get; }

    public SetOffBombsVar(int multiplier) : base(Token, 0m)
    {
        Multiplier = multiplier;
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        PreviewValue = BaseValue;
        if (!DamagePreview.Live(card, runGlobalHooks)) return;
        var body = DamagePreview.Body(card, previewMode, target);
        PreviewValue = DamagePreview.SetOffOn(
            body, card.Owner!.Creature, Multiplier);
    }
}

/// <summary>
/// Drowning Pressure: "(Deals N damage)". The play applies Weak 1 and
/// Vulnerable 1 and then counts, so the face counts them too (less any the
/// body's Artifact would negate) and folds the Vulnerable the hit will meet.
/// The per-stack number is the card's own <c>ExtraDamage</c>.
/// </summary>
public sealed class DebuffsAfterDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "PressureHit";

    public DebuffsAfterDamageVar() : base(Token, 0m, ValueProp.Move)
    {
    }

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        var per = card.DynamicVars["ExtraDamage"].BaseValue;
        if (!DamagePreview.Live(card, runGlobalHooks))
        {
            BaseValue = per * 2;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var body = DamagePreview.Body(card, previewMode, target);
        var artifact = (int)(body?.Powers.OfType<ArtifactPower>()
                                 .Sum(p => p.Amount) ?? 0);
        var (stacks, vulnerableLands) = DamagePreview.AfterOwnDebuffs(
            KokomiOverhaulKit.WeakVulnStacks(body), artifact);
        BaseValue = per * stacks;
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
        if (vulnerableLands && body != null && !DamagePreview.Vulnerable(body))
        {
            PreviewValue = decimal.Floor(
                PreviewValue * ReactionConstants.VulnerableTakenMult);
        }
    }
}

/// <summary>
/// Team Effort: "(Deals N damage)", its one hit -- <c>Damage</c> plus the
/// row's bonus while a Companion was played this turn
/// (<see cref="KleeOverhaulLedger.CompanionPlayedThisTurn"/>, the play's own
/// read) -- folded the game's way, so the bonus pays Vulnerable as it does.
/// </summary>
public sealed class CompanionBonusDamageVar : DamageVar
{
    /// <summary>The face's token.</summary>
    public const string Token = "BonusHit";

    public int Bonus { get; }

    public CompanionBonusDamageVar(int bonus) : base(Token, 0m, ValueProp.Move)
    {
        Bonus = bonus;
    }

    public static decimal Raw(decimal damage, int bonus, bool companion) =>
        damage + (companion ? bonus : 0);

    public override void UpdateCardPreview(
        CardModel card, CardPreviewMode previewMode, Creature? target,
        bool runGlobalHooks)
    {
        var damage = card.DynamicVars.Damage.BaseValue;
        if (!DamagePreview.Live(card, runGlobalHooks))
        {
            BaseValue = damage;
            base.UpdateCardPreview(card, previewMode, target, runGlobalHooks);
            return;
        }
        var companion = KleeOverhaulLedger.For(card.Owner!.Creature!)
            .CompanionPlayedThisTurn > 0;
        var body = DamagePreview.Body(card, previewMode, target);
        BaseValue = Raw(damage, Bonus, companion);
        base.UpdateCardPreview(card, previewMode, body, runGlobalHooks);
    }
}
