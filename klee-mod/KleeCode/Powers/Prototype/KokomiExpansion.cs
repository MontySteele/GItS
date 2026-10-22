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
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
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
        // The Kokomi upgrade pass (2026-10-19, finish round item 5): the
        // badge flashes when the turn's trigger is spent, and says so.
        foreach (var power in kokomi.Powers.OfType<AtWatersEdgePower>().ToList())
        {
            power.ShowSpent(true, flash: true);
        }
        await PowerCmd.Apply<WeakPower>(
            choiceContext, target, n, applier: kokomi, cardSource: null);
        await PowerCmd.Apply<VulnerablePower>(
            choiceContext, target, n, applier: kokomi, cardSource: null);
    }
}

/// <summary>Kurage Canopy (the payoff pass, 2026-10-01; Kokomi round 3
/// A-list, 2026-10-13). KOKOMI DEFENCE PASS (2026-10-22, [USER]: "Let's try
/// 1a, 3a, and reducing the Casket to 1 again"): "At the start of your turn,
/// if 2 or more of your Plans were carried out, add a Ward. Stings and Wards
/// don't count." (The ruled "to your Hand" is cut: 126 of the card ceiling's
/// 120. The Ward still goes to the Hand.) Battle Formation's condition, timing and
/// wording (<see cref="BattleFormationPower"/>): read ONCE, at the start of
/// her turn, right after the morning's Plans (<see cref="Signal"/>, from
/// <c>ProtoBakeKuragePower.AfterPlayerTurnStart</c> after Battle Formation),
/// off <see cref="KokomiOverhaulLedger.ChainPlansThisTurn"/>. It replaces the
/// per-carry-out Ward (it was on the plan bus). Copies add one Ward each; a
/// copy the upgraded card installed adds an upgraded Ward. A full hand sends
/// the Ward to the discard pile (<see cref="KokomiCards.AddJellyfish"/>). ONE
/// BADGE for both versions (<see cref="UpgradeTwinPower.Batches()"/>). Sim
/// twin: <c>kokomi_plan.kurage_canopy</c>.</summary>
public sealed class KurageCanopyPower
    : UpgradeTwinPower, ILocalizationProvider
{
    /// <summary>The Plans, not Stings or Wards, it waits for: Battle
    /// Formation's.</summary>
    public const int Threshold = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Canopy"),
        ("description",
            $"At the start of your turn, if {Threshold} or more "
          + "[gold]Plans[/gold] were carried out, add [blue]{Amount}[/blue] "
          + "{Amount:plural:[gold]Ward[/gold]|[gold]Wards[/gold]} to your "
          + "[gold]Hand[/gold]. Stings and Wards don't count."),
    };

    /// <summary>The badge previews the Ward it adds: the plain one, and the
    /// upgraded one when an upgraded card installed a copy. (The face keeps
    /// its one sentence: a count of each would pass the power ceiling.)
    /// </summary>
    protected override IEnumerable<IHoverTip> ExtraHoverTips
    {
        get
        {
            var tips = new List<IHoverTip>();
            if (!IsMutable || PlainCopies > 0)
            {
                tips.Add(HoverTipFactory.FromCard<ProtoKkWard>(false));
            }
            if (IsMutable && UpgradedCopies > 0)
            {
                tips.Add(HoverTipFactory.FromCard<ProtoKkWard>(true));
            }
            return tips;
        }
    }

    /// <summary>Does this morning's count pay? PURE over its inputs.</summary>
    public static bool Pays(int plansCarriedOut) =>
        plansCarriedOut >= Threshold;

    public static async Task Signal(PlayerChoiceContext choiceContext,
                                    Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (kokomi!.Player is not { } player) return;
        var powers = kokomi.Powers.OfType<KurageCanopyPower>().ToList();
        if (powers.Sum(p => (int)p.Amount) <= 0) return;
        if (!Pays(KokomiOverhaulLedger.For(kokomi).ChainPlansThisTurn)) return;
        foreach (var power in powers)
        {
            foreach (var (count, upgraded) in power.Batches())
            {
                await KokomiCards.AddJellyfish(player,
                    KokomiCards.Jellyfish.Ward, count, upgraded);
            }
        }
    }
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
          // Kokomi text audit (2026-10-22, item 9): "Plans count." goes; a
          // Plan hit is Hydro damage you deal, and the Plan tip says so.
          + "[gold]Vulnerable[/gold] to the enemy hit."),
        // The Kokomi upgrade pass (2026-10-19, finish round item 5): in
        // combat the badge says when this turn's trigger is spent.
        ("smartDescription",
            "The first time each turn you deal [gold]Hydro[/gold] damage, apply "
          + "[blue]{Amount}[/blue] [gold]Weak[/gold] and [blue]{Amount}[/blue] "
          + "[gold]Vulnerable[/gold] to the enemy hit."
          + "{Spent:cond:>0? (Used this turn.)|}"),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars => new List<DynamicVar>
    {
        new("Spent", 0m),
    };

    /// <summary>Has this turn's trigger been spent? Read off the ledger's
    /// latch, the one thing that knows what turn it is. Display only.</summary>
    public bool Spent =>
        Owner != null
        && KokomiOverhaulLedger.For(Owner).IsClaimed(nameof(AtWatersEdgePower));

    /// <summary>Set the badge's spent line (and flash it when the trigger
    /// fires). Display only.</summary>
    public void ShowSpent(bool spent, bool flash = false)
    {
        if (flash) Flash();
        if (!IsMutable) return;
        DynamicVars["Spent"].BaseValue = spent ? 1m : 0m;
    }

    /// <summary>A new turn: the badge reads the latch again, so a trigger a
    /// morning Plan already spent stays shown spent.</summary>
    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner != null && player.Creature == Owner) ShowSpent(Spent);
        return Task.CompletedTask;
    }

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

/// <summary>Watatsumi's Grace. THE KOKOMI TASTE AUDIT (2026-10-21,
/// review/active/kokomi-taste-audit-2026-10-21.md, pick 2 (a)): "At the end
/// of your turn, gain 3 [4] Block for each Plan waiting." It protects the
/// preparation (was "keep up to 10 [15] of your Block", the Sturdy Clamp
/// shape Thoma's Crimson Ooyoroi shares). Amount is the rate, so copies add.
/// Raw power Block (NC-11). Paid from <see cref="KokomiTasteAudit.TurnEnd"/>,
/// after Kurage Bloom's Sting. KOKOMI DEFENCE PASS (2026-10-22, [USER]:
/// "Otherwise agreed"): "Stings and Wards don't count", so it reads
/// <see cref="KokomiPlan.ChainPlansHeld"/> (Tideturn's count), not
/// <see cref="KokomiPlan.PlansHeld"/>. Sim twin: <c>kokomi_plan.turn_end</c>.</summary>
public sealed class WatatsumisGracePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watatsumi's Grace"),
        ("description",
            "At the end of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold] for each [gold]Plan[/gold] waiting. "
          + "Stings and Wards don't count."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The Block for <paramref name="plansWaiting"/> at
    /// <paramref name="rate"/> a Plan. PURE.</summary>
    public static int BlockFor(int rate, int plansWaiting) =>
        System.Math.Max(0, rate) * System.Math.Max(0, plansWaiting);
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
