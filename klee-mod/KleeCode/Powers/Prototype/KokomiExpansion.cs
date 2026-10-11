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
public static partial class KokomiCards
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
            await CardPileCmd.AddGeneratedCardToCombat(
                Exhausting(nip), PileType.Hand, owner);
        }
    }

    /// <summary>The Rare pass (2026-10-04): a card she is HANDED Exhausts
    /// when it is played, as a Shiv does -- Shoal Call's and Watatsumi
    /// Resistance's Nips and Kurage School's copies. A drafted Nip is
    /// unchanged. Sim twin: <c>kokomi_plan._exhausting</c>.</summary>
    public static T Exhausting<T>(T card) where T : CardModel
    {
        card.AddKeyword(CardKeyword.Exhaust);
        return card;
    }
}

/// <summary>
/// At Water's Edge (the Kokomi card pass, 2026-10-11): "The first time each
/// turn you deal Hydro damage to an enemy, apply 1 Weak and 1 Vulnerable to
/// it." HER Hydro damage only (the wearer's), once a turn on the ledger's
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

/// <summary>Grand Design, bent (the growth Powers, 2026-10-10, ruled):
/// "Open the Casket no longer empties the Casket. At the start of your turn,
/// put it into your hand." The stack means nothing:
/// <see cref="KokomiOverhaulKit.OpenCasket"/> reads only whether it is worn,
/// and the Strength stays the whole count. The second sentence (Kokomi
/// whole-run round 2, 2026-10-10) is <see cref="Signal"/>, paid from
/// <see cref="ProtoBakeKuragePower"/>'s morning beside Flood Tide. Sim twins:
/// <c>kokomi_plan.open_casket</c>, <c>kokomi_plan.grand_design_fetch</c>.
/// </summary>
public sealed class GrandDesignPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Design"),
        ("description",
            "[gold]Open the Casket[/gold] no longer empties the "
          + "[gold]Casket[/gold]. At the start of your turn, put it into "
          + "your hand."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Is Grand Design worn? The one read the Open makes.</summary>
    public static bool Keeps(Creature? kokomi) =>
        kokomi != null
        && kokomi.Powers.OfType<GrandDesignPower>().Any(p => p.Amount > 0);

    /// <summary>"At the start of your turn, put it into your hand." One Open
    /// in hand is enough: if one is already there nothing moves (no second
    /// copy is made, and copies of the Power do not fetch twice). Otherwise
    /// <see cref="KokomiOverhaulKit.FetchOpenCasket"/> moves the first one
    /// from the draw pile, then the discard pile; an exhausted Open stays
    /// gone.</summary>
    public static async Task Signal(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi) || !Keeps(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;
        if (HoldsOpen(CardPile.Get(PileType.Hand, player)?.Cards)) return;
        await KokomiOverhaulKit.FetchOpenCasket(choiceContext, kokomi);
    }

    /// <summary>Is an Open the Casket already in this pile (the hand)?</summary>
    public static bool HoldsOpen(IEnumerable<CardModel>? hand) =>
        KokomiOverhaulKit.FindOpenCasket(hand) != null;
}

/// <summary>Flood Tide (the growth Powers, 2026-10-10, ruled): "At the start
/// of your turn, the Casket gains 1." Copies add. Paid from
/// <see cref="ProtoBakeKuragePower"/>'s morning, after the hand draw and
/// before the Plans, The Long Game's site. Sim twin:
/// <c>kokomi_plan.rising_tide</c>.</summary>
public sealed class FloodTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Flood Tide"),
        ("description",
            "At the start of your turn, the [gold]Casket[/gold] gains "
          + "[blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static void Signal(Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var n = (int)kokomi!.Powers.OfType<FloodTidePower>()
            .Sum(p => p.Amount);
        if (n <= 0) return;
        KokomiOverhaulKit.GainCasket(kokomi, n);
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
            "The first time each turn you deal [gold]Hydro[/gold] damage to "
          + "an enemy, apply "
          + "[blue]{Amount}[/blue] [gold]Weak[/gold] and [blue]{Amount}[/blue] "
          + "[gold]Vulnerable[/gold] to it."),
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
          + "[gold]Casket[/gold] gains [blue]{Amount}[/blue] more."),
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
