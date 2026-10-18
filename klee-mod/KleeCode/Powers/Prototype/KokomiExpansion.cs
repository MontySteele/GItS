using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// KOKOMI EXPANSION, BATCH ONE (2026-09-29, the Kokomi arm):
/// the now-line verbs of the 22 new rows, one awaited call per `kind:` of the
/// `kokomi` op (<c>tools/gen_klee_cards.KOKOMI_KINDS</c>). Paper
/// <c>review/active/kokomi-expansion-2026-09-29.md</c>. Every damaging card of
/// hers applies Hydro through the arm's cadence; the verbs here deal none.
/// Sim twin: <c>tier0/engine/kokomi_plan.kind</c>.
/// </summary>
public static partial class KokomiCards
{
    private static int Amount(CardModel card) =>
        card.DynamicVars["KkAmount"].IntValue;

    /// <summary>Suffocating Deep: "Double each enemy's Weak and Vulnerable."
    /// </summary>
    public static async Task DoubleWeakVulnerable(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var kokomi = card.Owner?.Creature;
        var combat = kokomi?.CombatState;
        if (kokomi == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            var weak = (int)(enemy.Powers.OfType<WeakPower>()
                                  .FirstOrDefault()?.Amount ?? 0);
            if (weak > 0)
            {
                await PowerCmd.Apply<WeakPower>(
                    choiceContext, enemy, weak, applier: kokomi,
                    cardSource: card);
            }
            var vulnerable = (int)(enemy.Powers.OfType<VulnerablePower>()
                                        .FirstOrDefault()?.Amount ?? 0);
            if (vulnerable > 0)
            {
                await PowerCmd.Apply<VulnerablePower>(
                    choiceContext, enemy, vulnerable, applier: kokomi,
                    cardSource: card);
            }
        }
    }
}

/// <summary>
/// At Water's Edge (the Kokomi card pass, 2026-10-11; worded 2026-10-18):
/// "The first time each turn you deal Hydro damage, apply 1 Weak and 1
/// Vulnerable to the enemy hit." HER Hydro damage only (the wearer's), once a turn on the ledger's
/// shared latch (<see cref="KokomiOverhaulLedger.ClaimOncePerTurn"/>), claimed
/// by the first Hydro hit that lands on an enemy (fully blocked included) and
/// leaves it alive: a killing hit neither pays nor spends the turn's trigger.
/// Fed from two doors: a powered hit
/// whose element is Hydro (<see cref="AtWatersEdgePower.AfterDamageGiven"/>)
/// and an element-tagged hit she is the applier of
/// (<see cref="ElementalHit.Deal"/>: Plans, the Casket, Sea's Reproach). It
/// read "Whenever an Elemental Reaction happens on an enemy" before the pass.
/// Copies stack the amount, still once a turn. Sim twin:
/// <c>kokomi_plan.note_hydro_damage</c>.
/// </summary>
public static class KokomiExpansion
{
    internal static async Task OnHydroDamage(
        PlayerChoiceContext choiceContext, Creature? kokomi, Creature? target)
    {
        if (kokomi == null || target == null || !target.IsEnemy) return;
        if (target.IsDead || !KokomiOverhaul.LiveFor(kokomi)) return;
        var n = (int)kokomi.Powers.OfType<AtWatersEdgePower>()
                           .Sum(p => p.Amount);
        if (n <= 0) return;
        if (!KokomiOverhaulLedger.ClaimOncePerTurn(
                kokomi, nameof(AtWatersEdgePower)))
        {
            return;
        }
        await PowerCmd.Apply<WeakPower>(
            choiceContext, target, n, applier: kokomi, cardSource: null);
        await PowerCmd.Apply<VulnerablePower>(
            choiceContext, target, n, applier: kokomi, cardSource: null);
    }
}

/// <summary>Kurage Canopy (the payoff pass, 2026-10-01; Kokomi round 3
/// A-list, 2026-10-13): "Whenever the Bake-Kurage carries out a Plan that is
/// not a Sting or Ward, add a Ward to your Hand." Endless Shoal's Ward twin;
/// the Sting-or-Ward clause is the Kokomi card paper v2 (2026-10-18, sec.2
/// change 5). On the plan bus
/// (<see cref="IKokomiPlanListener"/>), which <c>KokomiPlan.ResolveEntry</c>
/// calls once per CARRY-OUT, so a Plan carried out twice (Second Wave,
/// Nereid's Ascension, All Streams) pays twice; copies add one each. A full
/// hand sends the Ward to the discard pile
/// (<see cref="KokomiCards.AddJellyfish"/>). The upgraded card installs
/// <see cref="KurageCanopyPlusPower"/>, whose Ward is upgraded. Sim twin:
/// <c>kokomi_plan._note_plan_resolved</c>.</summary>
public abstract class KurageCanopyBasePower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    protected abstract bool UpgradedWard { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", UpgradedWard ? "Kurage Canopy+" : "Kurage Canopy"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold] that is not a [gold]Sting[/gold] or "
          + "[gold]Ward[/gold], add [blue]{Amount}[/blue] "
          + (UpgradedWard ? "upgraded " : "")
          + "{Amount:plural:[gold]Ward[/gold]|[gold]Wards[/gold]} to your "
          + "[gold]Hand[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi, CardModel? line)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        if (Owner == null || Amount <= 0) return;
        if (KokomiRefounding.IsJellyfish(line)) return;  // a Sting or Ward
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        await KokomiCards.AddJellyfish(Owner.Player,
            KokomiCards.Jellyfish.Ward, (int)Amount, UpgradedWard);
    }
}

/// <summary>Kurage Canopy: a plain Ward per carry-out.</summary>
public sealed class KurageCanopyPower : KurageCanopyBasePower
{
    protected override bool UpgradedWard => false;
}

/// <summary>Kurage Canopy+: an upgraded Ward per carry-out.</summary>
public sealed class KurageCanopyPlusPower : KurageCanopyBasePower
{
    protected override bool UpgradedWard => true;
}

/// <summary>At Water's Edge (her C1; the Kokomi card pass, 2026-10-11). The
/// powered door: a hit she deals whose element is Hydro, read through the one
/// funnel (<see cref="AuraCmd.ElementOfPlay"/>), per body hit. An
/// element-tagged hit has no dealer and reaches
/// <see cref="KokomiExpansion.OnHydroDamage"/> from
/// <see cref="ElementalHit.Deal"/> instead, so no hit is counted twice.
/// </summary>
public sealed class AtWatersEdgePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "At Water's Edge"),
        ("description",
            "The first time each turn you deal [gold]Hydro[/gold] damage, apply "
          + "[blue]{Amount}[/blue] [gold]Weak[/gold] and [blue]{Amount}[/blue] "
          // Kokomi review r6 (2026-10-14, item 8): a Plan's hit counts.
          // 2026-10-18 wording: "to the enemy hit" (once per turn in all).
          + "[gold]Vulnerable[/gold] to the enemy hit. [gold]Plans[/gold] count."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterDamageGiven(
        PlayerChoiceContext choiceContext, Creature dealer, DamageResult result,
        ValueProp props, Creature target, CardModel? cardSource)
    {
        if (Owner == null || dealer != Owner) return;
        var hit = result.Receiver;
        if (hit == null || !hit.IsEnemy) return;
        if (AuraCmd.ElementOfPlay(cardSource, dealer) != Element.Hydro) return;
        await KokomiExpansion.OnHydroDamage(choiceContext, Owner, hit);
    }
}

/// <summary>Ceremonial Garment: "Your Attacks deal 1 more damage for each
/// Weak and Vulnerable on their target." Per hit of an Attack card she plays
/// face-up, off the body it lands on; STACKS of Weak plus stacks of
/// Vulnerable (the Kokomi card pass, 2026-10-11; it counted distinct debuffs
/// before). Sim twin: <c>kokomi_plan.garment_bonus</c>.</summary>
public sealed class ProtoCeremonialGarmentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Your Attacks deal [blue]{Amount}[/blue] additional damage for "
          + "each [gold]Weak[/gold] and [gold]Vulnerable[/gold] on their "
          + "target."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == null || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount * KokomiOverhaulKit.WeakVulnStacks(target);
    }
}

/// <summary>Watatsumi's Grace: "At the end of your turn, keep up to 10 of your
/// Block." The base game's Sturdy Clamp shape: the Block clear is prevented,
/// then everything above the cap is lost -- so a wall cannot grow without end
/// (paper sec.4 guard 1). Barricade, if also worn, keeps all (the first
/// preventer wins, as in the base game). Sim twin:
/// <c>kokomi_plan.grace_keeps</c>.</summary>
public sealed class WatatsumisGracePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watatsumi's Grace"),
        ("description",
            "At the end of your turn, keep up to [blue]{Amount}[/blue] of your "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool ShouldClearBlock(Creature creature) =>
        creature != Owner;

    public override async Task AfterPreventingBlockClear(
        AbstractModel preventer, Creature creature)
    {
        if (this != preventer || creature != Owner) return;
        var over = (int)creature.Block - (int)Amount;
        if (over > 0)
        {
            await CreatureCmd.LoseBlock(new BlockingPlayerChoiceContext(),
                                        creature, over, null);
        }
    }
}

/// <summary>
/// Tidal Riposte (Kokomi card paper v2, 2026-10-18, sec.2 change 4):
/// "Whenever you fully Block an enemy's attack, your next Attack deals 8 [11]
/// additional damage." It used to deal the 8 back at once, per hit; now the bonus is
/// STORED (<see cref="TidalRiposteChargePower"/>) until she chooses to strike.
///
/// ONCE PER ENEMY ATTACK, NOT PER HIT. <c>AfterAttack</c> fires once for the
/// enemy's whole <c>AttackCommand</c>, and its <c>Results</c> hold every hit:
/// it pays when at least one hit reached her, Block took some, and no hit on
/// her cost HP (<see cref="FullyBlocked(IEnumerable{ValueTuple{int,int}})"/>).
/// In co-op only the hits on her are read. Copies stack the stored amount.
/// Sim twin: <c>kokomi_plan.tidal_riposte</c>.
/// </summary>
public sealed class TidalRipostePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tidal Riposte"),
        ("description",
            "Whenever you fully [gold]Block[/gold] an enemy's attack, your "
          + "next Attack deals [blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The rule, readable without a combat: one attack's hits on
    /// her, as (blocked, unblocked). Fully blocked is "something was blocked
    /// and nothing got through".</summary>
    public static bool FullyBlocked(IEnumerable<(int Blocked, int Unblocked)> hits)
    {
        var any = false;
        foreach (var (blocked, unblocked) in hits)
        {
            if (unblocked > 0) return false;
            if (blocked > 0) any = true;
        }
        return any;
    }

    public override async Task AfterAttack(
        PlayerChoiceContext choiceContext, AttackCommand command)
    {
        if (Owner == null || Owner.IsDead || Amount <= 0) return;
        if (command.Attacker is not { IsEnemy: true }) return;
        if (!command.DamageProps.IsPoweredAttack()) return;
        var me = Owner;
        var hits = command.Results
            .SelectMany(r => r)
            .Where(r => r.Receiver == me)
            .Select(r => (r.BlockedDamage, r.UnblockedDamage));
        if (!FullyBlocked(hits)) return;
        await PowerCmd.Apply<TidalRiposteChargePower>(
            choiceContext, me, Amount, applier: me, cardSource: null);
    }
}
