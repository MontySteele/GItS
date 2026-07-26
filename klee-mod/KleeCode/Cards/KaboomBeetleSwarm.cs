using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: uncommon attack, cost 2, 5 damage x3 at random enemies, +3 per hit
/// vs Bombed enemies. Hand-written (R23 batch -- the bonus needs the bomb
/// system, and ModifyDamageAdditive is the verified per-target idiom).
///
/// The bonus is SNAPSHOTTED at cast (R72, 2026-07-26), the Sizzle idiom:
/// an enemy that is Bombed when the card is played pays the bonus on every
/// hit of the series. Previously the bonus read live bomb state per hit, so
/// hit 1's own detonation stripped the bonus from hits 2-3 and the rider
/// could never be paid more than once vs a single target (playtest finding
/// 2026-07-20, ruled 2026-07-26). Mirrors tier0 effects.py `_op_damage`,
/// which snapshots the same way.
/// </summary>
public sealed class KaboomBeetleSwarm : CustomCardModel, IElementalCard
{
    /// <summary>All of Klee's attacks apply Pyro (sheet: catalyst-grade cadence).</summary>
    public Element Element => Element.Pyro;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.AppliesPyro };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro);

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("kaboom_beetle_swarm");

    // WORDING FLAGGED FOR [USER] (R72 item 4, 2026-07-26), deliberately NOT
    // changed here: "Bombed enemies take ... more per hit" reads as live
    // state, and under the snapshot the enemy stops being Bombed after hit 1
    // while still paying the bonus on hits 2-3. The sheet is ratified, so the
    // rewording is a red-pen call, not an executor's; queued in
    // docs/open-playtest-items.md 6.2.
    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kaboom Beetle Swarm"),
        ("description",
            "Deal {Damage:diff()} damage to random enemies 3 times. "
          + "[gold]Bombed[/gold] enemies take {ExtraDamage:diff()} more per hit."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(5m, ValueProp.Move),
            new ExtraDamageVar(3m),
        };

    // autoAdd: false -- KleeCardPool declares pool membership itself (see Kaboom).
    public KaboomBeetleSwarm()
        : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies, autoAdd: false)
    {
    }

    /// <summary>
    /// Who was Bombed when this card was cast. Non-null only between the top
    /// of <see cref="OnPlay"/> and the end of its damage series -- one card
    /// resolves at a time, the same scoping SparkPower's pending-spend state
    /// relies on. Reference identity, not a comparer: Creature does not
    /// override Equals, and a list of at most a handful of enemies makes the
    /// lookup cost irrelevant.
    /// </summary>
    private List<Creature>? _bombedAtCast;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (cardSource != this || target == null) return 0m;

        // Inside our own series, the snapshot is the authority (R72). Outside
        // it -- damage previews and any other caller that asks what this card
        // would do right now -- fall back to the live read, which is the right
        // answer for a question about the CURRENT board rather than about a
        // cast in progress. Returning 0m here instead would blank the bonus
        // out of the preview.
        var bombed = _bombedAtCast is { } snap
            ? snap.Any(c => ReferenceEquals(c, target))
            : target.Powers.OfType<BombPower>().Any();

        return bombed ? DynamicVars.ExtraDamage.BaseValue : 0m;
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Taken before the first hit resolves: the sim's snapshot sits at the
        // top of the damage op, i.e. after any earlier effect of the same card
        // has run and before any hit lands. This card has no earlier effect,
        // so the two coincide exactly.
        // HittableEnemies is the verified live-enemy accessor (the sim
        // iterates living_enemies); TargetingRandomOpponents draws from the
        // same population, so nothing can be hit that the snapshot never saw.
        _bombedAtCast = CombatState!.HittableEnemies
            .Where(c => c.Powers.OfType<BombPower>().Any())
            .ToList<Creature>();
        try
        {
            await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
                .WithHitCount(3)
                .FromCard(this)
                .TargetingRandomOpponents(CombatState!)
                .WithHitFx("vfx/vfx_attack_slash")
                .Execute(choiceContext);
        }
        finally
        {
            // Cleared even if the series throws, so a failed play can never
            // leave a stale snapshot to be consulted by the next one.
            _bombedAtCast = null;
        }
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: bonus_vs_bombed +2 (3 -> 5).
        DynamicVars.ExtraDamage.UpgradeValueBy(2m);
    }
}
