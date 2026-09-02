using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// RULE 8: <b>Plan</b> -- an effect that happens at the START of her next turn
/// instead of now.
///
/// THE QUEUE IS TYPED, NOT A CLOSURE, and that is the load-bearing decision in
/// this file. A Plan has to survive the play that wrote it, cross a turn
/// boundary and then resolve with a live <c>PlayerChoiceContext</c> it did not
/// have when it was written -- so a captured lambda over the writing card's
/// context would be a use-after-free waiting to happen. Instead each Plan is a
/// <see cref="Planned"/> record of a <see cref="Kind"/>, an amount and an
/// optional body, and the SEVEN kinds below are exactly the seven clauses slice
/// one prints. A card cannot schedule anything else, which is the same
/// UNPARSEABLE discipline the codegen's field whitelists keep: a Plan body the
/// emitter does not understand is a build failure, never an approximation.
///
/// IN ORDER, and the order is the writing order (slice sec.5: "effects stored
/// on play, resolved IN ORDER at the start of her next turn, before draw").
/// <see cref="ProtoBakeKuragePower.BeforeSideTurnStart"/> is the resolution
/// point and its header says why that hook and not the one the shipped funnel
/// uses.
///
/// PER PLAYER, for the reason every other per-seat table in this mod is per
/// player (R205): in co-op the other seat's plans are not hers.
///
/// THE BADGE IS <see cref="PendingPlansPower"/>, the slice's "pending Plans"
/// UI item. It is a plain Counter power carrying the queue's length, kept in
/// step by <see cref="Sync"/> -- the existing badge rendering, nothing new
/// drawn, which is what the packet asks for one line above it.
/// </summary>
public static class KokomiPlan
{
    /// <summary>
    /// The seven clauses slice one's Plan cards print, and nothing else.
    ///
    /// Stolen Chapter draws, Battle Plan pays energy, Ambush hits a random
    /// enemy, Read the Field blocks, Feint hits the SAME enemy, Contingency
    /// Mends, War Council plays the top of the draw pile.
    /// </summary>
    public enum Kind
    {
        Draw,
        Energy,
        DamageRandomEnemy,
        DamageStoredTarget,
        Block,
        Mend,
        PlayTopOfDraw,
    }

    /// <summary>
    /// One scheduled clause. <paramref name="Target"/> is only ever set for
    /// <see cref="Kind.DamageStoredTarget"/> -- Feint's "the same enemy" -- and
    /// may be dead by the time it resolves, which rule 8's own sentence
    /// answers: "A Plan whose target is dead retargets randomly."
    /// </summary>
    public readonly record struct Planned(Kind Kind, int Amount, Creature? Target);

    private static object? _combat;
    private static readonly Dictionary<Player, List<Planned>> _queues = new();

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _queues.Clear();
    }

    private static void Rebase(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (ReferenceEquals(_combat, combat)) return;
        _combat = combat;
        _queues.Clear();
    }

    /// <summary>This seat's queue, front first. Never null.</summary>
    public static IReadOnlyList<Planned> Pending(Player? player) =>
        player != null && _queues.TryGetValue(player, out var q)
            ? q
            : (IReadOnlyList<Planned>)System.Array.Empty<Planned>();

    /// <summary>
    /// Write one Plan down.
    ///
    /// THE ART OF WAR IS RESOLVED HERE, and "also" is taken at its word: the
    /// Rare's face is "Plans also happen now", so the clause happens NOW and is
    /// STILL queued for the start of her next turn. Reading it as "instead"
    /// would delete rule 8 rather than break it, and the brief's gloss is
    /// "Rule 8's delay is gone", not "the Plan is gone".
    /// </summary>
    public static async Task Schedule(
        PlayerChoiceContext choiceContext, Creature? kokomi, Kind kind,
        int amount, Creature? target, CardModel? cardSource)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue))
        {
            queue = new List<Planned>();
            _queues[player] = queue;
        }
        queue.Add(new Planned(kind, amount, target));
        await Sync(choiceContext, kokomi);

        if (kokomi.Powers.OfType<TheArtOfWarPower>().Any())
        {
            await ResolveOne(choiceContext, kokomi,
                             new Planned(kind, amount, target));
        }
    }

    /// <summary>
    /// The start of her turn: every Plan she wrote resolves, in order, and the
    /// queue is empty afterwards.
    ///
    /// THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS. A Plan whose body
    /// schedules another Plan would otherwise resolve its own child in the same
    /// turn, which is a rule nothing printed; taking the list first means a
    /// Plan written DURING resolution waits for the next turn like every other.
    /// (No slice-one card can do this. The discipline is here anyway, because
    /// it costs one line and the alternative is a loop that a future card turns
    /// infinite.)
    /// </summary>
    public static async Task ResolveAll(
        PlayerChoiceContext choiceContext, Creature? kokomi)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue) || queue.Count == 0)
        {
            return;
        }
        var due = new List<Planned>(queue);
        queue.Clear();
        await Sync(choiceContext, kokomi);

        foreach (var plan in due)
        {
            await ResolveOne(choiceContext, kokomi, plan);
        }
    }

    /// <summary>
    /// ONE clause, which is the unit Treatise is priced in: "Whenever a Plan
    /// RESOLVES, draw 1" is once per clause, and the notify below is the only
    /// place that fires -- so the Art of War's extra resolution pays Treatise
    /// too, which is what "also happen now" says.
    /// </summary>
    private static async Task ResolveOne(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
    {
        var player = kokomi.Player;
        var combat = kokomi.CombatState;
        if (player == null) return;

        switch (plan.Kind)
        {
            case Kind.Draw:
                await CardPileCmd.Draw(choiceContext, plan.Amount, player);
                break;

            case Kind.Energy:
                await PlayerCmd.GainEnergy(plan.Amount, player);
                break;

            case Kind.Block:
                // Power-sourced Block is RAW (NC-11, R116): the Plan is not a
                // card resolving, so neither Frail nor Dexterity sees it --
                // the same line every other power-sourced Block in this mod
                // takes.
                await CreatureCmd.GainBlock(
                    kokomi, plan.Amount, ValueProp.Unpowered, null);
                break;

            case Kind.Mend:
                await KokomiTide.Mend(choiceContext, kokomi, plan.Amount);
                break;

            case Kind.DamageRandomEnemy:
                await Hit(choiceContext, kokomi, Roll(combat), plan.Amount);
                break;

            case Kind.DamageStoredTarget:
                // RULE 8's own sentence: "A Plan whose target is dead retargets
                // randomly." Absence and death are the same thing to a clause
                // that has to hit something, so both take the roll.
                var aim = plan.Target is { IsDead: false } stored
                          && combat != null
                          && combat.HittableEnemies.Contains(stored)
                    ? stored
                    : Roll(combat);
                await Hit(choiceContext, kokomi, aim, plan.Amount);
                break;

            case Kind.PlayTopOfDraw:
                await PlayTopOfDraw(choiceContext, player, plan.Amount);
                break;
        }

        foreach (var power in kokomi.Powers.ToList())
        {
            if (power is IKokomiPlanListener listener)
            {
                await listener.OnPlanResolved(choiceContext, kokomi);
            }
        }
    }

    private static Creature? Roll(MegaCrit.Sts2.Core.Combat.ICombatState? combat)
    {
        if (combat == null) return null;
        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        return candidates.Count == 0
            ? null
            : combat.RunState.Rng.CombatTargets.NextItem(candidates);
    }

    /// <summary>
    /// A Plan's damage, and it is HYDRO through the shared elemental pipeline.
    ///
    /// A READING, recorded because the card text does not settle it: "deal 10
    /// to a random enemy" names no element. Hydro is taken because it is the
    /// only choice that leaves the arm coherent -- every other non-card hit
    /// this arm makes (the Surge, Sango Isshin's overflow) is Hydro through
    /// this same funnel, and Feint's two halves would otherwise behave
    /// differently from each other, the delayed one applying no element where
    /// the printed one does.
    /// </summary>
    private static async Task Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, Creature? target,
        int amount)
    {
        if (target == null || target.IsDead || amount <= 0) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Hydro, amount, kokomi);
    }

    /// <summary>
    /// War Council's clause: "play the top N cards of your draw pile for free".
    ///
    /// THE CARD IS MOVED TO HAND AND THEN AUTO-PLAYED, in that order. A card
    /// resolving out of a pile it is still a member of is the class of bug the
    /// mod has already paid for once, and <c>CardCmd.AutoPlay</c> -- the game's
    /// own free-play door, which is what makes "for free" true without touching
    /// energy -- is documented (<c>KurageMemory.Fire</c>) against a card that
    /// belongs to no pile. Routing through the hand borrows the game's own
    /// membership handling on both sides: the play leaves the card wherever its
    /// printed keywords say, discard or exhaust, with nothing here to remember.
    ///
    /// THE TOP IS RE-READ EACH TIME, so a card the previous play drew or
    /// shuffled is the one the next iteration takes -- which is what "the top
    /// of your draw pile" means at the moment each play happens.
    /// </summary>
    private static async Task PlayTopOfDraw(
        PlayerChoiceContext choiceContext, Player player, int count)
    {
        for (var i = 0; i < count; i++)
        {
            var pile = CardPile.Get(PileType.Draw, player);
            var card = pile?.Cards.FirstOrDefault();
            if (card == null) return;
            await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);
            await CardCmd.AutoPlay(choiceContext, card, null);
        }
    }

    /// <summary>Keep the pending-Plans badge in step with the queue.</summary>
    private static async Task Sync(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        var count = Pending(kokomi.Player).Count;
        var badge = kokomi.Powers.OfType<PendingPlansPower>().FirstOrDefault();
        if (count == 0)
        {
            if (badge != null) await PowerCmd.Remove(badge);
            return;
        }
        if (badge == null)
        {
            await PowerCmd.Apply<PendingPlansPower>(
                choiceContext, kokomi, count, applier: kokomi,
                cardSource: null, silent: true);
            return;
        }
        await PowerCmd.ModifyAmount(
            choiceContext, badge, count - badge.Amount, applier: kokomi,
            cardSource: null, silent: true);
    }
}

/// <summary>
/// Treatise's hook: "Whenever a Plan resolves, draw 1."
///
/// An interface rather than a type test, the same shape
/// <c>IProtoExplosionListener</c> takes and for the same reason: a listener
/// discovered by interface cannot be forgotten at wire-up.
/// </summary>
public interface IKokomiPlanListener
{
    /// <param name="choiceContext">Live context; a listener may draw or deal.</param>
    /// <param name="kokomi">The seat whose Plan resolved.</param>
    Task OnPlanResolved(PlayerChoiceContext choiceContext, Creature kokomi);
}

/// <summary>
/// The pending-Plans badge (slice sec.5's UI list, item four). It carries no
/// rule at all: <see cref="KokomiPlan"/> owns the queue and this is its
/// display, so the number on screen and the number that will resolve are the
/// same number by construction.
/// </summary>
public sealed class PendingPlansPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Plan"),
        ("description",
            "{Amount} planned effect{Amount:plural:|s} will happen at the "
          + "start of your next turn, in the order you wrote them."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
