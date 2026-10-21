using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// KOKOMI POOL COMPLETION (2026-10-01, the Kokomi arm):
/// the now-line verbs of paper sec.4's new rows
/// (<c>review/active/pool-completion-2026-10-01.md</c>), one awaited call per
/// `kind:` of the `kokomi` op. Sim twin: <c>tier0/engine/kokomi_plan.kind</c>.
/// </summary>
public static partial class KokomiCards
{
    /// <summary>
    /// Kurage's Mercy (multiplayer): "Each player Mends 8 [12]." Every living
    /// player in the fight, Kokomi included, through the one Mend rule
    /// (<see cref="KokomiRules.Mend"/>: never above the HP each walked in
    /// with, captured for every seat at combat start). Sim twin:
    /// <c>kokomi_plan.kurages_mercy</c>.
    /// </summary>
    public static async Task KuragesMercy(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) return;
        var amount = card.DynamicVars["KkAmount"].IntValue;
        foreach (var each in KokomiPlan.EachPlayer(kokomi).ToList())
        {
            await KokomiRules.Mend(choiceContext, each, amount);
        }
    }
}

/// <summary>The pool completion's constants. (The hand limit Kurage School
/// stopped at left with the card, the re-founding, 2026-10-12.)</summary>
public static class KokomiPoolCompletion
{
    /// <summary>Divine Strategy's once-per-turn latch key.</summary>
    public const string DivineStrategyKey = nameof(DivineStrategyPower);
}

/// <summary>
/// Sea's Reproach. THE KOKOMI TASTE AUDIT (2026-10-21, review/active/kokomi-
/// taste-audit-2026-10-21.md, pick 3 (a)): "At the start of your turn, apply
/// 1 Weak to each enemy that intends to attack [and deal 5 damage to it]."
/// A Read the Tide power (was "Whenever you apply Weak or Vulnerable to an
/// enemy, deal 5 [7] damage to it", Sadistic Nature). Read ONCE, at the
/// start of her turn AFTER that turn's Plans are carried out
/// (<see cref="Signal"/>, from <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c>
/// after Dawn Tide), so the intents are the coming enemy turn's. One power
/// for both versions (<see cref="UpgradeTwinPower"/>): every copy applies
/// <see cref="Weak"/>, each upgraded copy also deals <see cref="Damage"/>,
/// unelemented and unpowered (Grand Strategist's hit). Sim twin:
/// <c>kokomi_plan.seas_reproach</c>.
/// </summary>
public sealed class SeasReproachPower : UpgradeTwinPower, ILocalizationProvider
{
    /// <summary>Weak per copy. Mirrors <c>C.KOKOMI_SEAS_REPROACH_WEAK</c>.</summary>
    public const int Weak = 1;

    /// <summary>Damage per upgraded copy. Mirrors
    /// <c>C.KOKOMI_SEAS_REPROACH_DAMAGE</c>.</summary>
    public const int Damage = 5;

    /// <summary>The badge prints the plain card's sentence; the damage is on
    /// the upgraded card (Battle Formation's reason).</summary>
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sea's Reproach"),
        ("description",
            "At the start of your turn, apply [blue]{Amount}[/blue] "
          + "[gold]Weak[/gold] to each enemy that intends to attack."),
    };

    /// <summary>What the copies apply and deal to each attacker: (Weak,
    /// damage). PURE.</summary>
    public static (int Weak, int Damage) Payout(int copies, int upgradedCopies) =>
        (System.Math.Max(0, copies) * Weak,
         System.Math.Max(0, upgradedCopies) * Damage);

    public static async Task Signal(PlayerChoiceContext choiceContext,
                                    Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var powers = kokomi!.Powers.OfType<SeasReproachPower>().ToList();
        var copies = (int)powers.Sum(p => p.Amount);
        if (copies <= 0 || kokomi.CombatState is not { } combat) return;
        var (weak, damage) = Payout(copies, powers.Sum(p => p.UpgradedCopies));
        var attackers = combat.HittableEnemies
            .Where(e => !e.IsDead)
            .Where(CurtainCallHooks.IntendsAttack)
            .ToList();
        foreach (var enemy in attackers)
        {
            if (enemy.IsDead) continue;
            if (weak > 0)
            {
                await PowerCmd.Apply<WeakPower>(choiceContext, enemy, weak,
                                                applier: kokomi,
                                                cardSource: null);
            }
            if (damage > 0 && !enemy.IsDead)
            {
                await ElementalHit.DealUnelemented(choiceContext, enemy,
                                                   damage, kokomi,
                                                   powered: false);
            }
        }
    }
}

/// <summary>
/// DIVINE STRATEGY, Kokomi's second Ancient (pool completion, 2026-10-01;
/// <c>Cards/Kokomi/DivineStrategy.cs</c>): "The first time each turn you play
/// a card on the Bake-Kurage, the line above its Plan happens now too."
/// (Worded so on 2026-10-05, the Kokomi kit review.) Bends rule 2, under
/// which a card does one half or the other.
///
/// THE GENERATED PLAN BRANCH ASKS <see cref="NowLine"/> once the Plan is
/// written (<c>gen_klee_cards</c>, the `plan:` emission). Only a row with a
/// now-line emits the ask, so a Plan-only card (Masterstroke) never spends the
/// once, and neither does a written Companion with no Plan line of its own:
/// it prints no line above a Plan (the re-founding, 2026-10-12).
/// The answer is the play re-aimed where the now-line aims -- the front enemy
/// for a row that aims at an enemy (a planned hit's own reader), the Plan's
/// ally for one that aims at a player -- or null: no Power, the once already
/// spent, the kit not live, or nobody to aim at (then the once is NOT spent).
/// Game-side only, like every Ancient (the sim models no events).
/// </summary>
public sealed class DivineStrategyPower : PowerModel, ILocalizationProvider
{
    /// <summary>Where the now-line aims once it is off the jellyfish.</summary>
    public enum Aim
    {
        None,
        FrontEnemy,
        Ally,
    }

    public List<(string, string)>? Localization => new()
    {
        ("title", "Divine Strategy"),
        ("description",
            "The first time each turn you plan a card, its first line "
          + "also happens now."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static CardPlay? NowLine(CardPlay cardPlay, Creature? kokomi,
                                    Aim aim)
    {
        if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) return null;
        if (!kokomi.Powers.OfType<DivineStrategyPower>().Any()) return null;
        Creature? target = aim switch
        {
            Aim.FrontEnemy => KokomiPlan.FrontEnemy(kokomi),
            Aim.Ally => CoopSet.PlanAlly(kokomi),
            _ => null,
        };
        if (aim != Aim.None && target == null) return null;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(
                kokomi, KokomiPoolCompletion.DivineStrategyKey))
        {
            return null;
        }
        return new CardPlay
        {
            Card = cardPlay.Card,
            Player = cardPlay.Player,
            Target = target,
            ResultPile = cardPlay.ResultPile,
            Resources = cardPlay.Resources,
            IsAutoPlay = cardPlay.IsAutoPlay,
            PlayIndex = cardPlay.PlayIndex,
            PlayCount = cardPlay.PlayCount,
        };
    }
}
