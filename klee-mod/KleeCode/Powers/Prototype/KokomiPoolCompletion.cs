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
/// KOKOMI POOL COMPLETION (2026-10-01, QUARANTINED under the Kokomi arm):
/// the now-line verbs of paper sec.4's new rows
/// (<c>review/active/pool-completion-2026-10-01.md</c>), one awaited call per
/// `kind:` of the `kokomi` op. Sim twin: <c>tier0/engine/kokomi_plan.kind</c>.
/// </summary>
public static partial class KokomiCards
{
    /// <summary>Spring Tide: "The Bake-Kurage carries out all your Plans now."
    /// <see cref="KokomiPlan.ResolveAllNow"/>.</summary>
    public static Task SpringTide(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        KokomiPlan.ResolveAllNow(choiceContext, card.Owner?.Creature);

    /// <summary>
    /// Kurage School: "Add a copy of each 0-cost card with a Plan line in your
    /// hand to your hand."
    ///
    /// "0-COST" IS THE COST IT HAS IN HAND NOW (<c>EnergyCost.GetResolved</c>,
    /// the game's own read), and an X card is never 0-cost. "A Plan line" is
    /// <see cref="IPlannedCard"/> with a clause. The hand is read ONCE, before
    /// the first copy arrives, so a copy is never copied; the copies are
    /// <c>CloneCard</c>'s (the original's upgrade state, Crystal Collapse's
    /// door), and a full hand stops them. Sim twin:
    /// <c>kokomi_plan.kurage_school</c>.
    /// </summary>
    public static async Task KurageSchool(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var hand = CardPile.Get(PileType.Hand, owner)?.Cards.ToList();
        if (hand == null) return;
        foreach (var held in hand.Where(c => c != card && IsZeroCostPlan(c)))
        {
            if (CardPile.Get(PileType.Hand, owner) is { } now
                && now.Cards.Count >= KokomiPoolCompletion.MaxHandSize)
            {
                break;
            }
            var copy = combat.CloneCard(held);
            await CardPileCmd.AddGeneratedCardToCombat(copy, PileType.Hand,
                                                        owner);
        }
    }

    /// <summary>Kurage School's test: a card in hand that costs 0 right now
    /// and prints a Plan line.</summary>
    public static bool IsZeroCostPlan(CardModel? card) =>
        card is IPlannedCard { PlanClauses.Count: > 0 }
        && !card.EnergyCost.CostsX
        && card.EnergyCost.GetResolved() == 0;

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

/// <summary>The pool completion's constants, mirrored by value.</summary>
public static class KokomiPoolCompletion
{
    /// <summary>The base game's hand limit (the sim's
    /// <c>C.MAX_HAND_SIZE</c>).</summary>
    public const int MaxHandSize = 10;

    /// <summary>Divine Strategy's once-per-turn latch key.</summary>
    public const string DivineStrategyKey = nameof(DivineStrategyPower);
}

/// <summary>
/// Patient Tide (pool completion): "At the end of your turn, keep up to 2 [3]
/// unspent Energy." What is left at her turn's end, up to the cap, is banked
/// (<see cref="BeforeSideTurnEnd"/>) and handed back once the next turn's
/// refill has happened (<see cref="AfterPlayerTurnStart"/>, which the game
/// broadcasts after the energy reset). Copies add to the cap. Sim twin:
/// <c>kokomi_plan.patient_tide_bank</c> / <c>patient_tide_kept</c>.
/// </summary>
public sealed class PatientTidePower : PowerModel, ILocalizationProvider
{
    private int _kept;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Patient Tide"),
        ("description",
            "At the end of your turn, keep up to [blue]{Amount}[/blue] unspent "
          + "[gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>What is kept: the unspent Energy, up to the cap.</summary>
    public static int Kept(int unspent, int cap) =>
        cap <= 0 || unspent <= 0 ? 0 : System.Math.Min(unspent, cap);

    public override Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        _kept = 0;
        if (side != CombatSide.Player) return Task.CompletedTask;
        if (Owner?.Player is not { } player) return Task.CompletedTask;
        if (!KokomiOverhaul.LiveFor(Owner)) return Task.CompletedTask;
        _kept = Kept(player.PlayerCombatState?.Energy ?? 0, (int)Amount);
        return Task.CompletedTask;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, MegaCrit.Sts2.Core.Entities.Players.Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        var kept = _kept;
        _kept = 0;
        if (kept <= 0 || !KokomiOverhaul.LiveFor(Owner)) return;
        await PlayerCmd.GainEnergy(kept, player);
    }
}

/// <summary>
/// Sea's Reproach (pool completion): "Whenever you apply Weak or Vulnerable to
/// an enemy, deal 3 damage to it." Silent's Sadistic Nature at her pace: a
/// POSITIVE application she made (<c>applier == Owner</c>), once per enemy it
/// lands on, Hydro and unpowered (Tidal Riposte's hit). The hook fans to every
/// model, so the power asks whose application it was. Sim twin:
/// <c>kokomi_plan.seas_reproach</c>, from <c>refpowers.on_power_applied</c>.
/// </summary>
public sealed class SeasReproachPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sea's Reproach"),
        ("description",
            "Whenever you apply [gold]Weak[/gold] or [gold]Vulnerable[/gold] "
          + "to an enemy, deal [blue]{Amount}[/blue] damage to it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does this change pay? Weak or Vulnerable, gained, on a living
    /// enemy, put there by <paramref name="owner"/>.</summary>
    public static bool Pays(PowerModel? power, decimal amount,
                            Creature? applier, Creature? owner) =>
        power is WeakPower or VulnerablePower
        && amount > 0m
        && owner != null && applier == owner
        && power.Owner is { IsEnemy: true, IsDead: false };

    public override async Task AfterPowerAmountChanged(
        PlayerChoiceContext choiceContext, PowerModel power, decimal amount,
        Creature? applier, CardModel? cardSource)
    {
        if (!Pays(power, amount, applier, Owner) || Amount <= 0) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        await ElementalHit.Deal(choiceContext, power.Owner!, Element.Hydro,
                                (int)Amount, Owner!, powered: false);
    }
}

/// <summary>
/// Watatsumi Resistance (pool completion): "Whenever you play a Companion
/// card, add a Nip to your hand." Every Companion play of hers, one Nip per
/// copy -- The General's Banner's test without its once-per-turn latch. The
/// Nip is the feed pass's pool row itself (Shoal Call's). Sim twin:
/// <c>kokomi_plan.watatsumi_resistance</c>.
/// </summary>
public sealed class WatatsumiResistancePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Watatsumi Resistance"),
        ("description",
            "Whenever you play a [gold]Companion[/gold] card, add "
          + "[blue]{Amount}[/blue] {Amount:plural:Nip|Nips} to your hand."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (Owner?.Player is not { } player || Amount <= 0) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        var combat = Owner.CombatState;
        if (combat == null) return;
        for (var i = 0; i < (int)Amount; i++)
        {
            var nip = combat.CreateCard<ProtoKkNip>(player);
            await CardPileCmd.AddGeneratedCardToCombat(nip, PileType.Hand,
                                                        player);
        }
    }
}

/// <summary>
/// DIVINE STRATEGY, Kokomi's second Ancient (pool completion, 2026-10-01;
/// <c>Cards/Kokomi/DivineStrategy.cs</c>): "The first time each turn you play
/// a card on the Bake-Kurage, its now-line happens too." Bends rule 2, under
/// which a card does one half or the other.
///
/// THE GENERATED PLAN BRANCH ASKS <see cref="NowLine"/> once the Plan is
/// written (<c>gen_klee_cards</c>, the `plan:` emission). Only a row with a
/// now-line emits the ask, so a Plan-only card (Nip) never spends the once.
/// The answer is the play re-aimed where the now-line aims -- the front enemy
/// for a row that aims at an enemy (a planned hit's own reader), the Plan's
/// ally for one that aims at a player -- or null: no Power, the once already
/// spent, the arm off, or nobody to aim at (then the once is NOT spent).
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
            "The first time each turn you play a card on the "
          + "[gold]Bake-Kurage[/gold], its now-line happens too."),
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
