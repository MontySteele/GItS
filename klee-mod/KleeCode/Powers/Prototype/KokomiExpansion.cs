using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
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
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// KOKOMI EXPANSION, BATCH ONE (2026-09-29, QUARANTINED under the Kokomi arm):
/// the now-line verbs of the 22 new rows, one awaited call per `kind:` of the
/// `kokomi` op (<c>tools/gen_klee_cards.KOKOMI_KINDS</c>). Paper
/// <c>review/active/kokomi-expansion-2026-09-29.md</c>. Every damaging card of
/// hers applies Hydro through the arm's cadence; the verbs here deal none.
/// Sim twin: <c>tier0/engine/kokomi_plan.kind</c>.
/// </summary>
public static class KokomiCards
{
    private static int Amount(CardModel card) =>
        card.DynamicVars["KkAmount"].IntValue;

    /// <summary>Measured Breath: "If no Plan is waiting, draw 2 cards."
    /// </summary>
    public static async Task DrawIfNoPlan(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner?.Creature == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        if (KokomiPlan.PlansHeld(owner.Creature) > 0) return;
        await CardPileCmd.Draw(choiceContext, Amount(card), owner);
    }

    /// <summary>Salt in the Wound: "If the enemy has Weak, draw 1 card."
    /// </summary>
    public static async Task DrawIfTargetWeak(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        if (owner?.Creature == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var target = cardPlay.Target;
        if (target == null || !target.Powers.OfType<WeakPower>().Any()) return;
        await CardPileCmd.Draw(choiceContext, Amount(card), owner);
    }

    /// <summary>Tidal Resonance: "Apply Hydro to ALL enemies. Draw 1 card for
    /// each enemy that already had an element." Counted before the Hydro
    /// lands; "an element" is a standing aura.</summary>
    public static async Task Resonance(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var kokomi = owner?.Creature;
        var combat = kokomi?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var living = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        var had = living.Count(e => e.Powers.OfType<AuraPower>().Any());
        foreach (var enemy in living)
        {
            if (enemy.IsDead) continue;
            await ElementalHit.ApplyOnly(choiceContext, enemy, Element.Hydro,
                                         kokomi);
        }
        var cards = had * Amount(card);
        if (cards > 0) await CardPileCmd.Draw(choiceContext, cards, owner);
    }

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

    /// <summary>All Streams Flow to the Sea (<see
    /// cref="KokomiPlan.CancelAllForNext"/>).</summary>
    public static Task AllStreams(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay) =>
        KokomiPlan.CancelAllForNext(choiceContext, card.Owner?.Creature);

    /// <summary>Coral Tithe (the payoff pass, 2026-10-01): "Empty the Casket.
    /// Gain 1 Energy and draw 1 card for every 3 in it." Only while she holds
    /// a Casket, found the way the relic's own carry-out add finds it
    /// (<c>GetRelic&lt;TamakushiCasket&gt;</c>, which also finds the Orobas
    /// upgrade <see cref="Relics.WatatsumiCasket"/>); without one, nothing.
    /// Rounds down. Sim twin: <c>kokomi_plan.coral_tithe</c>.</summary>
    public static async Task CoralTithe(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var kokomi = owner?.Creature;
        if (owner == null || kokomi == null) return;
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (owner.GetRelic<Relics.TamakushiCasket>() == null) return;
        var per = Amount(card);
        var points = KokomiOverhaulLedger.For(kokomi).EmptyCasket();
        Relics.TamakushiCasket.Refresh(kokomi);
        var n = CoralTithePaid(points, per);
        if (n <= 0) return;
        await PlayerCmd.GainEnergy(n, owner);
        await CardPileCmd.Draw(choiceContext, n, owner);
    }

    /// <summary>Coral Tithe's arithmetic: one Energy and one card for every
    /// <paramref name="per"/> points, rounded down (7 at every 3 pays 2).
    /// </summary>
    public static int CoralTithePaid(int points, int per) =>
        per <= 0 || points <= 0 ? 0 : points / per;

    /// <summary>Shoal Call: "Add 2 Nips to your hand. [They are upgraded.]"
    /// The Nip is the feed pass's pool row itself.</summary>
    public static async Task ShoalCall(
        PlayerChoiceContext choiceContext, CardModel card, CardPlay cardPlay)
    {
        var owner = card.Owner;
        var combat = owner?.Creature?.CombatState;
        if (owner == null || combat == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        for (var i = 0; i < Amount(card); i++)
        {
            var nip = combat.CreateCard<ProtoKkNip>(owner);
            if (card.IsUpgraded) nip.UpgradeInternal();
            await CardPileCmd.AddGeneratedCardToCombat(nip, PileType.Hand,
                                                        owner);
        }
    }
}

/// <summary>
/// The expansion's reaction reader: At Water's Edge, "Whenever a reaction
/// happens on an enemy, apply 1 Weak and 1 Vulnerable to it." ANY reaction,
/// whoever caused it -- every seat wearing the Power pays, off the one site
/// the mod resolves a reaction (<c>ReactionEffects</c>). Sim twin:
/// <c>kokomi_plan.note_reaction</c>.
/// </summary>
public static class KokomiExpansion
{
    internal static async Task OnReaction(
        PlayerChoiceContext choiceContext, Creature target)
    {
        if (target == null || target.IsDead || !target.IsEnemy) return;
        var players = target.CombatState?.PlayerCreatures;
        if (players == null) return;
        foreach (var kokomi in players.ToList())
        {
            if (kokomi == null || !KokomiOverhaul.LiveFor(kokomi)) continue;
            var edge = kokomi.Powers.OfType<AtWatersEdgePower>()
                             .FirstOrDefault();
            if (edge == null || edge.Amount <= 0 || target.IsDead) continue;
            var n = (int)edge.Amount;
            await PowerCmd.Apply<WeakPower>(
                choiceContext, target, n, applier: kokomi, cardSource: null);
            await PowerCmd.Apply<VulnerablePower>(
                choiceContext, target, n, applier: kokomi, cardSource: null);
        }
    }
}

/// <summary>Grand Design: "Whenever the Bake-Kurage carries out a Plan, the
/// Casket gains 1 more for each Energy paid for it" (main session,
/// 2026-09-29). The Energy paid for the writing card
/// (<see cref="KokomiPlan.Entry.Paid"/>); per carry-out, so a doubled one
/// pays twice. Sim twin: <c>kokomi_plan._note_plan_resolved</c>.
/// </summary>
public sealed class GrandDesignPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Design"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], the [gold]Casket[/gold] gains "
          + "[blue]{Amount}[/blue] more for each [gold]Energy[/gold] paid "
          + "for it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static void Note(Creature? kokomi, KokomiPlan.Entry entry)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        if (entry.Paid <= 0) return;
        var design = kokomi!.Powers.OfType<GrandDesignPower>().FirstOrDefault();
        if (design == null || design.Amount <= 0) return;
        KokomiOverhaulKit.GainCasket(kokomi, (int)design.Amount * entry.Paid);
    }
}

/// <summary>Kurage Canopy (the payoff pass, 2026-10-01): "Whenever the
/// Bake-Kurage carries out a Plan, gain 2 Block." On the plan bus
/// (<see cref="IKokomiPlanListener"/>), which <c>KokomiPlan.ResolveEntry</c>
/// calls once per CARRY-OUT, so a Plan carried out twice (Second Wave,
/// Nereid's Ascension, All Streams) pays twice. POWERED Block, as her
/// Ancient's (<see cref="PrincessOfWatatsumiPlanPower"/>). Sim twin:
/// <c>kokomi_plan._note_plan_resolved</c>.</summary>
public sealed class KurageCanopyPower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Canopy"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (kokomi != Owner) return;                 // co-op: your plans only
        if (Owner == null || Amount <= 0) return;
        if (!KokomiOverhaul.LiveFor(Owner)) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Move, null);
    }
}

/// <summary>The Long Game: "At the start of your turn, if exactly one Plan is
/// waiting, gain 1 Energy." The queue is read before the morning drains it,
/// Moon Signal's read (<see cref="ProtoBakeKuragePower"/>). Sim twin:
/// <c>kokomi_plan.long_game</c>.</summary>
public sealed class TheLongGamePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Long Game"),
        ("description",
            "At the start of your turn, if exactly one [gold]Plan[/gold] is "
          + "waiting, gain [blue]{Amount}[/blue] [gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Both twins at once: the base power's Energy, and
    /// <see cref="TheLongGamePlusPower"/>'s Energy and draw (power cost
    /// sweep, 2026-09-30). The draw needs <paramref name="choiceContext"/>.
    /// </summary>
    public static async Task Signal(Creature? kokomi, int waiting,
                                    PlayerChoiceContext? choiceContext = null)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;
        if (waiting != KokomiOverhaulLaw.LongGameWaiting) return;
        var energy = (int)kokomi.Powers.OfType<TheLongGamePower>()
            .Sum(p => p.Amount);
        var plus = (int)kokomi.Powers.OfType<TheLongGamePlusPower>()
            .Sum(p => p.Amount);
        if (energy + plus > 0)
        {
            await PlayerCmd.GainEnergy(energy + plus, player);
        }
        if (plus > 0 && choiceContext != null)
        {
            await CardPileCmd.Draw(choiceContext, plus, player);
        }
    }
}

/// <summary>The Long Game+ (power cost sweep, 2026-09-30): "At the start of
/// your turn, if exactly one Plan is waiting, gain 1 Energy and draw 1 card."
/// The upgraded card installs this twin instead of
/// <see cref="TheLongGamePower"/>, whose <c>Signal</c> pays both. Sim twin:
/// <c>kokomi_plan.long_game</c>.</summary>
public sealed class TheLongGamePlusPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Long Game+"),
        ("description",
            "At the start of your turn, if exactly one [gold]Plan[/gold] is "
          + "waiting, gain [blue]{Amount}[/blue] [gold]Energy[/gold] and draw "
          + "[blue]{Amount}[/blue] {Amount:plural:card|cards}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>At Water's Edge (her C1). The Power hooks nothing; the reaction
/// site reads it (<see cref="KokomiExpansion.OnReaction"/>).</summary>
public sealed class AtWatersEdgePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "At Water's Edge"),
        ("description",
            "Whenever an [gold]Elemental Reaction[/gold] happens on an "
          + "enemy, apply "
          + "[blue]{Amount}[/blue] [gold]Weak[/gold] and [blue]{Amount}[/blue] "
          + "[gold]Vulnerable[/gold] to it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Ceremonial Garment: "Your Attacks deal 1 more damage for each
/// debuff on their target." Per hit of an Attack card she plays face-up, off
/// the body it lands on; a debuff is a <see cref="PowerType.Debuff"/> power
/// (an aura is a Buff and does not count). Sim twin:
/// <c>kokomi_plan.garment_bonus</c>.</summary>
public sealed class ProtoCeremonialGarmentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Your Attacks deal [blue]{Amount}[/blue] additional damage for "
          + "each "
          + "debuff on their target."),
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
        return Amount * KokomiOverhaulKit.DebuffCount(target);
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

/// <summary>Tidal Riposte: "Whenever an enemy's attack is fully Blocked, deal
/// 5 damage to it." A hit of an enemy's powered attack that Block absorbed
/// whole -- Block took some and no HP was lost -- once per hit, Hydro. Sim
/// twin: <c>kokomi_plan.tidal_riposte</c>.</summary>
public sealed class TidalRipostePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tidal Riposte"),
        ("description",
            "Whenever an enemy's attack is fully [gold]Blocked[/gold], deal "
          + "[blue]{Amount}[/blue] damage to it."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (Owner == null || target != Owner || Amount <= 0) return;
        if (dealer == null || !dealer.IsEnemy || dealer.IsDead) return;
        if (!props.IsPoweredAttack()) return;
        if (result.BlockedDamage <= 0 || result.UnblockedDamage > 0) return;
        await ElementalHit.Deal(choiceContext, dealer, Element.Hydro,
                                (int)Amount, Owner, powered: false);
    }
}

/// <summary>Kurage Swarm: "Whenever you write a Plan that costs 0, the Casket
/// gains 1." The cost paid, after reductions (<see
/// cref="KokomiPlan.Entry.Paid"/>). Sim twin: <c>kokomi_plan.schedule</c>.
/// </summary>
public sealed class KurageSwarmPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage Swarm"),
        ("description",
            "Whenever you write a [gold]Plan[/gold] that costs 0, the "
          + "[gold]Casket[/gold] gains [blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static void Note(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var swarm = kokomi!.Powers.OfType<KurageSwarmPower>().FirstOrDefault();
        if (swarm == null || swarm.Amount <= 0) return;
        KokomiOverhaulKit.GainCasket(kokomi, (int)swarm.Amount);
    }
}
