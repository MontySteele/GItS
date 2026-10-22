using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE KOKOMI TASTE AUDIT (2026-10-21, review/active/kokomi-taste-audit-
/// 2026-10-21.md; [USER]: "That's a lot of card changes, but we can do that
/// and rerun the balance suite to see how it feels." and "Agreed on all 5
/// defaults."). The now-line verbs of the changed rows, one awaited call per
/// `kind:` of the `kokomi` op (<c>tools/gen_klee_cards.KOKOMI_KINDS</c>), and
/// "Plan a Sting". Sim twin: <c>tier0/engine/kokomi_plan</c>, the same names.
/// </summary>
public static partial class KokomiCards
{
    /// <summary>
    /// "PLAN A STING" (pick 1 (a)): <paramref name="amount"/> generated
    /// Stings (or Wards), each written onto the Bake-Kurage exactly as one she
    /// Planned would be -- its own Plan line through
    /// <see cref="KokomiPlan.Schedule"/>, so Watchful Shoal and her Strength
    /// fold in at writing, the write payoffs and the telemetry see it, and
    /// its two lines stay open -- and each paying the Tamakushi Casket as a
    /// Sting she Planned does (<see cref="Relics.TamakushiCasket.PayForPlanned"/>),
    /// inside a carry-out too (Flotsam Surge's Plan). The card is in no pile,
    /// as a played Sting is spent (Crystal Collapse's copy is made the same
    /// way, <c>combat.CreateCard</c>). A Plan and not a card play: no
    /// card-played hook sees it. Returns how many were written. Sim twin:
    /// <c>kokomi_plan.plan_jellyfish</c>.
    /// </summary>
    public static async Task<int> PlanJellyfish(
        PlayerChoiceContext choiceContext, Player? owner, Jellyfish kind,
        int amount)
    {
        var kokomi = owner?.Creature;
        var combat = kokomi?.CombatState;
        if (owner == null || kokomi == null || combat == null || amount <= 0)
        {
            return 0;
        }
        if (!KokomiOverhaul.LiveFor(kokomi)) return 0;
        var written = 0;
        for (var i = 0; i < amount; i++)
        {
            CardModel card = kind == Jellyfish.Sting
                ? combat.CreateCard<ProtoKkSting>(owner)
                : combat.CreateCard<ProtoKkWard>(owner);
            if (card is not IPlannedCard planned) continue;
            await KokomiPlan.Schedule(choiceContext, kokomi, card,
                                      planned.PlanClauses);
            await Relics.TamakushiCasket.PayForPlanned(kokomi, card);
            written++;
        }
        return written;
    }

    /// <summary>Shoal Call (pick 1 (a)): "Plan 3 [4] Stings." (was "Add 3
    /// [4] Stings to your Hand", Blade Dance; Brine Spray keeps that verb,
    /// <see cref="ShoalCall"/>.)</summary>
    public static Task PlanStings(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        PlanJellyfish(choiceContext, card.Owner, Jellyfish.Sting, Amount(card));

    /// <summary>Suffocating Deep (pick 3 (a)): "Apply 2 Weak and 2
    /// Vulnerable to each enemy that intends to attack." Read when it is
    /// played (was "Apply 1 of each to every enemy, then double them").
    /// </summary>
    public static async Task WeakVulnAttackers(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        var combat = kokomi?.CombatState;
        if (kokomi == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var amount = Amount(card);
        if (amount <= 0) return;
        var attackers = combat.HittableEnemies
            .Where(e => !e.IsDead)
            .Where(CurtainCallHooks.IntendsAttack)
            .ToList();
        foreach (var enemy in attackers)
        {
            if (enemy.IsDead) continue;
            await PowerCmd.Apply<WeakPower>(choiceContext, enemy, amount,
                                            applier: kokomi, cardSource: card);
            await PowerCmd.Apply<VulnerablePower>(choiceContext, enemy, amount,
                                                  applier: kokomi,
                                                  cardSource: card);
        }
    }
}

/// <summary>
/// Resolve of Watatsumi (pick 2 (a)): "When a Plan is carried out, it deals 2
/// [3] additional damage and gains 2 [3] additional Block." (was "Gain 2 [3]
/// Strength", Inflame). Read by <c>KokomiPlan</c> at the carry-out: added to
/// each damage hit (<c>KokomiPlan.Hit</c>, before Opening Gambit's doubling)
/// and each Block clause (Block, Tide Wall's, Kelp Wall's) of a Plan carried
/// out, Stings and Wards included. Copies add. Sim twin:
/// <c>kokomi_plan.resolve_bonus</c>.
/// </summary>
public sealed class ResolveOfWatatsumiPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Resolve of Watatsumi"),
        ("description",
            "Whenever a [gold]Plan[/gold] is carried out, it deals "
          + "[blue]{Amount}[/blue] additional damage and gains "
          + "[blue]{Amount}[/blue] additional [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The bonus on <paramref name="kokomi"/>: the stack, 0
    /// without it. Never throws.</summary>
    public static int Bonus(Creature? kokomi)
    {
        if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) return 0;
        return System.Math.Max(0, (int)kokomi.Powers
            .OfType<ResolveOfWatatsumiPower>().Sum(p => p.Amount));
    }
}

/// <summary>
/// Her end of turn (the Kokomi taste audit, 2026-10-21), in this order,
/// from <c>ProtoBakeKuragePower.BeforeSideTurnEnd</c>:
///   * Kurage Bloom, "At the end of your turn, Plan a Sting." Copies Plan one
///     each; carried out the next morning.
///   * Watatsumi's Grace, "At the end of your turn, gain 3 [4] Block for each
///     Plan waiting. Stings and Wards don't count." The queue as it stands,
///     less its Sting and Ward Plans (Kokomi defence pass, 2026-10-22), so
///     Kurage Bloom's Sting adds nothing; raw power Block (NC-11).
/// Sim twin: <c>kokomi_plan.turn_end</c>, the same order.
/// </summary>
public static class KokomiTasteAudit
{
    public static async Task TurnEnd(PlayerChoiceContext choiceContext,
                                     Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var bloom = (int)kokomi!.Powers.OfType<KurageBloomPower>()
            .Sum(p => p.Amount);
        if (bloom > 0)
        {
            await KokomiCards.PlanJellyfish(choiceContext, kokomi.Player,
                                            KokomiCards.Jellyfish.Sting,
                                            bloom);
        }
        var rate = (int)kokomi.Powers.OfType<WatatsumisGracePower>()
            .Sum(p => p.Amount);
        var block = WatatsumisGracePower.BlockFor(
            rate, KokomiPlan.ChainPlansHeld(kokomi));
        if (block > 0)
        {
            await CreatureCmd.GainBlock(kokomi, block, ValueProp.Unpowered,
                                        null);
        }
    }
}
