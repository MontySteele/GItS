using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// DRAFT 6's ONE RULE: <b>Plan</b>. A card with a Plan line can be played on
/// the Bake-Kurage instead of where it would normally go; its cost is paid now,
/// and at the start of her next turn the jellyfish carries out the Plan line.
///
/// THE QUEUE IS TYPED, NOT A CLOSURE, and that is still the load-bearing
/// decision in this file. A Plan has to survive the play that wrote it, cross a
/// turn boundary and then resolve with a live <c>PlayerChoiceContext</c> it did
/// not have when it was written -- so a captured lambda over the writing card's
/// context would be a use-after-free waiting to happen. Instead every Plan is a
/// <see cref="Entry"/>: the card that wrote it, plus the <see cref="Planned"/>
/// clauses off its own <see cref="IPlannedCard.PlanClauses"/>. The
/// <see cref="Kind"/>s below are exactly the clauses draft 6 prints; a body the
/// emitter does not understand is a build failure, never an approximation.
///
/// ONE ENTRY IS ONE PLAN, and that is the unit everything downstream counts in:
/// the pending badge, the strip on the jellyfish, Change of Plans' "your front
/// Plan", Nereid's Ascension's "carries out every Plan twice" and the
/// whenever-a-Plan-is-carried-out payoffs (Treatise, Song of Pearls). War
/// Council prints two clauses and is ONE Plan, which is what its face says --
/// "Deal 4 damage to every enemy AND apply 1 Weak to each" is one sentence.
///
/// IN ORDER, and the order is the writing order (slice sec.2 rule 3: "Plans are
/// carried out in the order they were written").
/// <see cref="ProtoBakeKuragePower.AfterPlayerTurnStart"/> is the resolution
/// point and its header says why that hook and not the one the packet's prose
/// names.
///
/// KOKOMI IS THE DEALER, THE JELLYFISH IS THE SOURCE (slice sec.5). Rule 3 says
/// "Your Strength and Dexterity count, and planned damage from an Attack
/// applies Hydro the way her Attacks do", so a planned hit goes out through
/// <see cref="ElementalHit"/> with HER as the applier -- which is what makes
/// Strength, Weak, the aura and the reaction all behave exactly as they do on a
/// card she played. The pet is where the plan was SENT, not who is fighting.
///
/// PER PLAYER, for the reason every other per-seat table in this mod is per
/// player (R205): in co-op the other seat's plans are not hers.
///
/// THE BADGE IS <see cref="PendingPlansPower"/>, a plain Counter power carrying
/// the queue's length, kept in step by <see cref="Sync"/> -- the existing badge
/// rendering, nothing new drawn.
/// </summary>
public static class KokomiPlan
{
    /// <summary>
    /// The clauses draft 6's Plan lines print, and nothing else.
    ///
    /// Stolen Chapter draws, Battle Plan pays energy and draws, Read the Field
    /// blocks, The Moon (A Ship O'er the Seas) Mends, Feint and Ambush and
    /// Kurage's Oath and War Council hit, Sango Isshin hits for a quarter of
    /// her Max HP, Chain of Command hits per Companion she played last turn,
    /// Slack Water and Exposed Flank and Vanguard and Coral Bulwark debuff,
    /// Nereid's Ascension doubles, and Moon's Reflection replays a card out of
    /// the exhaust pile that had no Plan line of its own.
    /// </summary>
    public enum Kind
    {
        Draw,
        Energy,
        Block,
        Mend,
        Damage,
        DamageQuarterMaxHp,
        DamagePerCompanionLastTurn,
        ApplyWeak,
        ApplyVulnerable,
        PlanTwice,
        ReplayExhausted,
    }

    /// <summary>
    /// Where a clause lands. Rule 3: "A planned hit lands on the front enemy
    /// (leftmost alive) unless the line says every enemy." A self-facing clause
    /// (draw, energy, block, Mend, the doubling) takes <see cref="Self"/> and
    /// prints no target at all.
    ///
    /// NO STORED CREATURE, deliberately, and that is the difference from draft
    /// 2's queue: a Plan written last turn cannot hold a reference to an enemy
    /// that may be dead, escaped or replaced by the time it resolves, so the
    /// target is a RULE resolved at carry-out rather than a pointer captured at
    /// writing. It also makes the strip honest -- what it draws is what will
    /// happen, not what was true when the card was played.
    /// </summary>
    public enum Aim
    {
        Self,
        FrontEnemy,
        AllEnemies,
    }

    /// <summary>
    /// One scheduled clause. <paramref name="Card"/> is only ever set for
    /// <see cref="Kind.ReplayExhausted"/> -- Moon's Reflection's chosen card --
    /// and is the one place a Plan holds an object rather than a number.
    /// </summary>
    public readonly record struct Planned(
        Kind Kind, int Amount, Aim Aim, CardModel? Card = null);

    /// <summary>
    /// ONE PLAN: the card that wrote it and the clauses it wrote. The card is
    /// kept for the DISPLAY -- the strip draws pending Plans face up, in order,
    /// on the jellyfish -- and for nothing else; the clauses are the whole of
    /// what will happen.
    /// </summary>
    public sealed record Entry(CardModel? Source, IReadOnlyList<Planned> Clauses)
    {
        /// <summary>What the strip prints for this Plan.</summary>
        public string Title => Source?.Title.ToString() ?? "Plan";
    }

    private static object? _combat;
    private static readonly Dictionary<Player, List<Entry>> _queues = new();

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
    public static IReadOnlyList<Entry> Pending(Player? player) =>
        player != null && _queues.TryGetValue(player, out var q)
            ? q
            : (IReadOnlyList<Entry>)System.Array.Empty<Entry>();

    /// <summary>
    /// WAS THIS PLAY AIMED AT THE JELLYFISH? The one question the generated
    /// branch asks, and the decompile read is what makes it one line: the play
    /// pipeline hands <c>OnPlay</c> the <c>Creature</c> that was targeted
    /// (<c>CardPlay.Target</c>), so "played on the Bake-Kurage" is a property
    /// of the play rather than of a mode, a keyword or a second card.
    /// </summary>
    public static bool PlayedOnPet(CardPlay cardPlay) =>
        BakeKuragePet.Is(cardPlay.Target);

    /// <summary>
    /// Write one Plan down: rule 2's whole engine side.
    ///
    /// THE MOON OVERLOOKS THE WATERS IS RESOLVED HERE, and "also" is taken at
    /// its word: the Rare's face is "Plans also happen now", so the Plan
    /// happens NOW and is STILL queued for the start of her next turn. Reading
    /// it as "instead" would delete rule 2 rather than break it.
    /// </summary>
    public static async Task Schedule(
        PlayerChoiceContext choiceContext, Creature? kokomi, CardModel? source,
        IReadOnlyList<Planned> clauses)
    {
        if (!KokomiOverhaul.LiveFor(kokomi)) return;
        var player = kokomi!.Player;
        if (player == null || clauses.Count == 0) return;

        Rebase(kokomi);
        if (!_queues.TryGetValue(player, out var queue))
        {
            queue = new List<Entry>();
            _queues[player] = queue;
        }
        var entry = new Entry(source, clauses.ToList());
        queue.Add(entry);
        await Sync(choiceContext, kokomi);

        if (kokomi.Powers.OfType<PlansAlsoNowPower>().Any())
        {
            await ResolveEntry(choiceContext, kokomi, entry);
        }
    }

    /// <summary>
    /// Moon's Reflection: "Choose a card in your exhaust pile: Plan: the
    /// jellyfish carries out its Plan line, or the card itself if it has none."
    ///
    /// TWO CLAUSE SHAPES OUT OF ONE SCREEN, and the card's own face is what
    /// splits them: a chosen card that HAS a Plan line contributes that line
    /// verbatim -- the same typed clauses it would have written itself -- and
    /// one that has none is replayed whole through the game's own free-play
    /// door as a single <see cref="Kind.ReplayExhausted"/> clause. Nothing is
    /// re-derived: an <see cref="IPlannedCard"/> is asked for its own list.
    ///
    /// AN EMPTY EXHAUST PILE IS A NO-OP and not a screen. A selection over
    /// nothing is a click the player cannot answer.
    /// </summary>
    public static async Task ScheduleFromExhaust(
        PlayerChoiceContext choiceContext, Player? owner, CardModel source)
    {
        if (owner == null) return;
        if (!KokomiOverhaul.LiveFor(owner.Creature)) return;
        var pile = CardPile.Get(PileType.Exhaust, owner);
        if (pile == null || pile.Cards.Count == 0) return;

        var pick = (await CardSelectCmd.FromCombatPile(
            choiceContext, pile, owner,
            new CardSelectorPrefs(ReflectionPrompt, 1))).FirstOrDefault();
        if (pick == null) return;

        var clauses = pick is IPlannedCard { PlanClauses.Count: > 0 } planned
            ? planned.PlanClauses
            : new[] { new Planned(Kind.ReplayExhausted, 1, Aim.Self, pick) };
        await Schedule(choiceContext, owner.Creature, pick, clauses);
    }

    /// <summary>Keyed on the VERB, the way Rally's search screen was: one
    /// screen, one string, however many carriers eventually print it.</summary>
    public const string ReflectionPromptKey =
        "KLEEMOD-KOKOMI_EXHAUST_PLAN.selectionScreenPrompt";

    /// <summary>The prompt text. Merged into the `cards` table by
    /// <c>KleeMod.InjectLocStrings</c>, which is its only source.</summary>
    public const string ReflectionPromptText =
        "Choose a card. The Bake-Kurage carries out its Plan line, or the "
      + "card if it has none.";

    private static LocString ReflectionPrompt =>
        new LocString("cards", ReflectionPromptKey);

    /// <summary>
    /// The start of her turn: every Plan she wrote resolves, in order, and the
    /// queue is empty afterwards.
    ///
    /// THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS. A Plan whose body
    /// schedules another Plan would otherwise resolve its own child in the same
    /// turn, which is a rule nothing printed; taking the list first means a
    /// Plan written DURING resolution waits for the next turn like every other.
    /// (Moon's Reflection's replay can reach a card that writes one, so this is
    /// no longer only a discipline.)
    ///
    /// NEREID'S ASCENSION IS READ PER ENTRY, not once for the morning, and that
    /// is a reading: its own clause is what installs the doubling, so reading
    /// the power before each Plan is carried out means the Rare does not double
    /// itself and every Plan written after it in the same morning is doubled --
    /// which is what "the jellyfish carries out every Plan twice" says.
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
        var due = new List<Entry>(queue);
        queue.Clear();
        await Sync(choiceContext, kokomi);

        foreach (var entry in due)
        {
            var times = CarryOutTimes(kokomi);
            for (var i = 0; i < times; i++)
            {
                await ResolveEntry(choiceContext, kokomi, entry);
            }
        }
    }

    /// <summary>
    /// How many times ONE Plan is carried out right now: two while Nereid's
    /// Ascension's window is up, one otherwise.
    ///
    /// A NAMED READ rather than an inline predicate, because WHERE it is asked
    /// is the rule: <see cref="ResolveAll"/> calls it inside the drain loop,
    /// before each entry, so the Rare's own clause does not double itself and
    /// every Plan written after it in the same morning is doubled.
    /// </summary>
    private static int CarryOutTimes(Creature kokomi) =>
        kokomi.Powers.OfType<PlanTwicePower>().Any() ? 2 : 1;

    /// <summary>
    /// Change of Plans: "The jellyfish carries out your front Plan now."
    ///
    /// IT LEAVES THE QUEUE, which is what "carries out" means everywhere else
    /// in the arm -- one resolution moved forward, not a copy. An empty queue
    /// is a printed no-op, the way a Surge on an empty Tide was.
    /// </summary>
    public static async Task ResolveFront(
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
        var front = queue[0];
        queue.RemoveAt(0);
        await Sync(choiceContext, kokomi);
        await ResolveEntry(choiceContext, kokomi, front);
    }

    /// <summary>
    /// ONE PLAN CARRIED OUT, which is the unit Treatise and Song of Pearls are
    /// priced in: "Whenever the jellyfish carries out a Plan" is once per
    /// ENTRY, and the notify at the bottom is the only place that fires -- so
    /// The Moon Overlooks the Waters' extra resolution pays them too, which is
    /// what "also happen now" says.
    /// </summary>
    private static async Task ResolveEntry(
        PlayerChoiceContext choiceContext, Creature kokomi, Entry entry)
    {
        foreach (var clause in entry.Clauses)
        {
            await ResolveOne(choiceContext, kokomi, clause);
        }

        foreach (var power in kokomi.Powers.ToList())
        {
            if (power is IKokomiPlanListener listener)
            {
                await listener.OnPlanResolved(choiceContext, kokomi);
            }
        }
    }

    private static async Task ResolveOne(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
    {
        var player = kokomi.Player;
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
                // POWERED, and rule 3 is why: "your Strength and Dexterity
                // count, since the plans are hers". Draft 2's Plan Block was
                // `Unpowered` on the NC-11 power-sourced-Block line; draft 6
                // states the opposite rule in the brief itself, so a planned
                // Block is `ValueProp.Move` -- the same prop a card's own Block
                // carries, and the same one Dexterity reads.
                await CreatureCmd.GainBlock(
                    kokomi, plan.Amount, ValueProp.Move, null);
                break;

            case Kind.Mend:
                await KokomiRules.Mend(choiceContext, kokomi, plan.Amount);
                break;

            case Kind.Damage:
                await Hit(choiceContext, kokomi, plan.Aim, plan.Amount);
                break;

            case Kind.DamageQuarterMaxHp:
                await Hit(choiceContext, kokomi, plan.Aim,
                          KokomiRules.QuarterOfMaxHp(kokomi));
                break;

            case Kind.DamagePerCompanionLastTurn:
                // Chain of Command. "Last turn" is read at CARRY-OUT: the Plan
                // was written on turn N and resolves at the top of N+1, and the
                // ledger has rolled by then, so the count it holds is turn N's
                // -- the turn the player was looking at when they wrote it.
                await Hit(choiceContext, kokomi, plan.Aim,
                          plan.Amount * KokomiOverhaulLedger.For(kokomi)
                                            .CompanionsPlayedLastTurn);
                break;

            case Kind.ApplyWeak:
                await Debuff<WeakPower>(choiceContext, kokomi, plan);
                break;

            case Kind.ApplyVulnerable:
                await Debuff<VulnerablePower>(choiceContext, kokomi, plan);
                break;

            case Kind.PlanTwice:
                await PlanTwicePower.Wear(choiceContext, kokomi, plan.Amount);
                break;

            case Kind.ReplayExhausted:
                await Replay(choiceContext, player, plan.Card);
                break;
        }
    }

    /// <summary>The front enemy: leftmost alive. <c>CombatState.Enemies</c> is
    /// board order (it is sorted by encounter slot), so "leftmost" is the first
    /// hittable one and needs no second definition.</summary>
    public static Creature? FrontEnemy(Creature? kokomi) =>
        kokomi?.CombatState?.HittableEnemies.FirstOrDefault(e => !e.IsDead);

    private static IEnumerable<Creature> Aimed(Creature kokomi, Aim aim)
    {
        var combat = kokomi.CombatState;
        if (combat == null) yield break;
        if (aim == Aim.AllEnemies)
        {
            foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead)
                                        .ToList())
            {
                yield return enemy;
            }
            yield break;
        }
        var front = FrontEnemy(kokomi);
        if (front != null) yield return front;
    }

    /// <summary>
    /// A Plan's damage, and it is HYDRO with KOKOMI as the applier.
    ///
    /// Rule 3 settles both halves in one sentence: "Your Strength and Dexterity
    /// count, and planned damage from an Attack applies Hydro the way her
    /// Attacks do." <see cref="ElementalHit.Deal"/> is the funnel that makes
    /// both true at once -- it runs the dealer's Strength and Weak, resolves
    /// the aura and its reaction, then the target's Vulnerable -- so a planned
    /// hit and a played one differ in nothing but when they land.
    /// </summary>
    private static async Task Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, Aim aim, int amount)
    {
        if (amount <= 0) return;
        foreach (var target in Aimed(kokomi, aim))
        {
            if (target.IsDead) continue;
            await ElementalHit.Deal(
                choiceContext, target, Element.Hydro, amount, kokomi);
        }
    }

    private static async Task Debuff<T>(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
        where T : PowerModel
    {
        foreach (var target in Aimed(kokomi, plan.Aim))
        {
            if (target.IsDead) continue;
            await PowerCmd.Apply<T>(
                choiceContext, target, plan.Amount, applier: kokomi,
                cardSource: null);
        }
    }

    /// <summary>
    /// Moon's Reflection's second shape: replay a card that had no Plan line.
    ///
    /// THE CARD IS MOVED TO HAND AND THEN AUTO-PLAYED, in that order, and the
    /// argument is <c>KurageMemory.Fire</c>'s: a card resolving out of a pile
    /// it is still a member of is a class of bug this mod has already paid for
    /// once, and <c>CardCmd.AutoPlay</c> -- the game's own free-play door -- is
    /// documented against a card that belongs to no pile. Routing through the
    /// hand borrows the game's own membership handling on both sides, so the
    /// play leaves the card wherever its printed keywords say.
    /// </summary>
    private static async Task Replay(
        PlayerChoiceContext choiceContext, Player player, CardModel? card)
    {
        if (card == null) return;
        await CardPileCmd.Add(card, PileType.Hand, CardPilePosition.Top);
        await CardCmd.AutoPlay(choiceContext, card, null);
    }

    /// <summary>
    /// THE WIRE'S VIEW of the queue (`EB-216`, the draft-6 half).
    ///
    /// A PLAIN DICTIONARY OF PRIMITIVES, and the shape is
    /// <c>KurageMemory.Snapshot</c>'s for the reason that one is: the bridge
    /// (<c>vendor/STS2_MCP/gits/GitsKokomiPlan.cs</c>) reaches it by
    /// REFLECTION, because the whole arm is Compile Remove'd from a release
    /// build and a compile-time reference would make the bridge refuse to load
    /// without it. The field names here ARE the contract, and
    /// <c>understudy/blindplay.kokomi_plans</c> reads them.
    ///
    /// THREE STATES, NOT TWO. An ABSENT key means "no Plan rule in this build";
    /// an EMPTY map means "the rule is here and this seat is not playing it";
    /// a populated map is her queue. A reader is entitled to tell those apart,
    /// which is why this returns an empty map rather than null for a Klee.
    /// </summary>
    public static Dictionary<string, object?> Snapshot(Player? player)
    {
        var snapshot = new Dictionary<string, object?>();
        var creature = player?.Creature;
        if (player == null || !KokomiOverhaul.LiveFor(creature))
        {
            return snapshot;
        }

        var pending = Pending(player);
        var pet = BakeKuragePet.Of(creature);
        snapshot["pet"] = pet != null;
        snapshot["pet_name"] = "Bake-Kurage";
        // THE ID THE SEAT AIMS AT. `CombatId` is what
        // `ICombatState.GetCreature` resolves, so a Plan is sent through
        // exactly the door an attack aims through -- no second targeting
        // channel and nothing for the two to disagree about.
        snapshot["pet_entity_id"] = pet == null ? null : pet.CombatId.ToString();
        snapshot["pending"] = pending.Count;
        // A DOUBLED MORNING IS A FACT ABOUT THE NEXT TURN, so it rides the
        // snapshot rather than being inferred from a Power's amount: Nereid's
        // Ascension is the one card that makes the queue's LENGTH stop being
        // the number of things that will happen.
        snapshot["twice"] = creature!.Powers.OfType<PlanTwicePower>().Any();
        snapshot["also_now"] =
            creature.Powers.OfType<PlansAlsoNowPower>().Any();
        snapshot["queue"] = pending
            .Select(entry => (object?)new Dictionary<string, object?>
            {
                ["name"] = entry.Title,
                ["clauses"] = entry.Clauses.Count,
            })
            .ToList();
        return snapshot;
    }

    /// <summary>
    /// Keep the pending-Plans badge AND the strip in step with the queue.
    ///
    /// ONE FUNNEL, called from every site that moves the queue, which is what
    /// makes the badge, the strip and the list that will resolve the same three
    /// views of one number by construction -- the arrangement
    /// `KurageMemory.RefreshStrip` already makes for the memory arm.
    /// </summary>
    private static async Task Sync(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        Vfx.KokomiPlanStrip.Refresh(kokomi);
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
/// A card that prints a <b>Plan</b> line, and the line itself.
///
/// EMITTED, NOT WRITTEN. `gen_klee_cards` builds this member from the row's
/// top-level `plan:` list, so the clauses the queue stores and the clauses the
/// sheet declares are the same declaration.
///
/// PUBLIC because Moon's Reflection asks a card it was handed for its own Plan
/// line, which a private member could not answer.
/// </summary>
public interface IPlannedCard
{
    /// <summary>The card's printed Plan line, in the order it was written.</summary>
    IReadOnlyList<KokomiPlan.Planned> PlanClauses { get; }
}

/// <summary>
/// Treatise's and Song of Pearls' hook: "Whenever the jellyfish carries out a
/// Plan, ...".
///
/// An interface rather than a type test, the same shape
/// <c>IProtoExplosionListener</c> takes and for the same reason: a listener
/// discovered by interface cannot be forgotten at wire-up.
/// </summary>
public interface IKokomiPlanListener
{
    /// <param name="choiceContext">Live context; a listener may draw or deal.</param>
    /// <param name="kokomi">The seat whose Plan was carried out.</param>
    Task OnPlanResolved(PlayerChoiceContext choiceContext, Creature kokomi);
}

/// <summary>
/// The pending-Plans badge (slice sec.5's UI list). It carries no rule at all:
/// <see cref="KokomiPlan"/> owns the queue and this is its display, so the
/// number on screen and the number that will be carried out are the same number
/// by construction. What each of them IS lives on the strip
/// (<c>Vfx/Prototype/KurageMemoryCard.cs</c>), drawn on the jellyfish.
/// </summary>
public sealed class PendingPlansPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Plan"),
        ("description",
            "Carries out [blue]{Amount}[/blue] "
          + "[gold]Plan{Amount:plural:|s}[/gold] at the start of your next "
          + "turn, in order."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Nereid's Ascension (Rare, her Burst): "Plan: for 2 turns, the jellyfish
/// carries out every Plan twice."
///
/// THE DURATION IS THE AMOUNT, so a second Ascension extends the window and
/// never doubles the doubling -- the same construction every other windowed
/// power in this mod takes, and a tick-down at the end of her turn.
///
/// IT IS INSTALLED BY A PLAN, which is why the window starts one morning late
/// and covers the NEXT two: the card is played on turn N, the clause is carried
/// out at the top of N+1 and the power ticks at the end of N+1 and N+2.
/// </summary>
public sealed class PlanTwicePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Nereid's Ascension"),
        ("description",
            "The [gold]Bake-Kurage[/gold] carries out every [gold]Plan[/gold] "
          + "twice. Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Wear the window, or extend it to <paramref name="turns"/>.</summary>
    public static async Task Wear(
        PlayerChoiceContext choiceContext, Creature kokomi, int turns)
    {
        var worn = kokomi.Powers.OfType<PlanTwicePower>().FirstOrDefault();
        if (worn == null)
        {
            await PowerCmd.Apply<PlanTwicePower>(
                choiceContext, kokomi, turns, applier: kokomi,
                cardSource: null);
            return;
        }
        if (worn.Amount >= turns) return;
        await PowerCmd.ModifyAmount(
            choiceContext, worn, turns - worn.Amount, applier: kokomi,
            cardSource: null);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}
