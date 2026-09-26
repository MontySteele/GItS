using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;

namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE -- THE GUEST CAST (2026-09-25).
///
/// The design is <c>review/active/furina-guest-batch-2026-09-25.md</c>, ruled
/// the same evening ("Guest Star: &lt;name&gt;", two kinds of guest, the LAW
/// amendment), with two rulings after it that this file follows:
///
///   * NO GUEST CAP. [USER]: "why not just let the Stage be filled with guest
///     stars if the player wants?" A guest takes any empty seat, up to all
///     three; on a full stage its card recasts like any summon.
///   * ONE OF EACH GUEST. "only one Neuvillette allowed - repeats trigger a
///     Bow and then resummon them, carrying over unused Fanfare". A Guest Star
///     for a guest already on stage makes it Bow (free) and return to the same
///     seat holding its unused Fanfare plus the card's.
///
/// THE FRAME'S RULES, and where each lives:
///
///   * rule 2, arrival: <see cref="GuestStar"/>;
///   * rule 3, a guest is a performer in every other way: nothing here, which
///     is the point -- the damage order, the fade, Full House, Tutti!, Bis!
///     and the hit's Bow all walk seats and never ask who is in one;
///   * rule 4, every act pays, and an act that cannot pay does nothing: the
///     Fanfare half is <see cref="FurinaStageLedger.ActFanfare"/>, the board
///     half <see cref="GuestAct"/>;
///   * rule 5, the Bow is free: <see cref="FurinaStageLedger.ActFanfare"/> is
///     handed no seat on a Bow and takes no payment;
///   * rule 6, a reading resets: <see cref="StageSeat.LostSinceAct"/>;
///   * rule 7, the forecast: <see cref="Forecast"/>.
///
/// A GUEST CARRIES ITS ELEMENT (the Guest Cast's LAW amendment, pick 5):
/// every elemental act goes out through <see cref="ElementalHit.Deal"/>, so
/// it applies its aura and reactions fire. The trio's acts stay unelemented.
/// </summary>
public static partial class FurinaStage
{
    /// <summary>The eight guests' sheet names, in the table's order.</summary>
    public static readonly string[] Guests =
    {
        "neuvillette", "clorinde", "navia", "chevreuse", "wriothesley",
        "sigewinne", "charlotte", "lynette",
    };

    /// <summary>Is this performer a guest? Every performer after the trio in
    /// <see cref="StagePerformer"/> is.</summary>
    public static bool IsGuest(StagePerformer who) =>
        who >= StagePerformer.Neuvillette;

    /// <summary>
    /// A GUEST STAR CARD: "&lt;Name&gt; joins the stage with N Fanfare."
    ///
    ///   * already on stage (one of each): it Bows -- its act, free -- with
    ///     every Bow reader but no Five-Century return, and comes back to the
    ///     same seat holding its unused Fanfare plus <paramref name="fanfare"/>;
    ///   * a full stage: the front Bows and leaves, and the guest arrives at
    ///     the back holding <paramref name="fanfare"/> plus the front's
    ///     remaining Fanfare (<see cref="RecastFromFront"/>, "like any
    ///     summon"; the recast adds, 2026-09-25);
    ///   * otherwise: the back-most empty seat, holding <paramref name="fanfare"/>.
    ///
    /// <para>AT THE FRONT (<paramref name="atFront"/>, the guest seat round,
    /// 2026-09-25): Wriothesley's card puts him in the FRONT seat and the
    /// others shift back one -- at the back no hit reaches him (rule 6) and
    /// his act landed nothing. On a full stage the recast's leaver is then
    /// the BACK performer (<see cref="RecastFromBack"/>): it Bows and leaves,
    /// and he arrives at the front holding his Fanfare plus its remaining
    /// Fanfare. A repeat copy is unchanged: he Bows and returns to his own
    /// seat.</para>
    ///
    /// It does not act on arrival (`EB-738`): it acts at the end of the turn
    /// with everyone else.
    /// </summary>
    public static async Task GuestStar(PlayerChoiceContext choiceContext,
                                       Creature? owner, string member,
                                       int fanfare, bool atFront = false)
    {
        if (!LiveFor(owner)) return;
        var who = Parse(member);
        var ledger = FurinaStageLedger.For(owner!);
        if (ledger.SeatOf(who) is { } seat)
        {
            var index = ledger.IndexOf(seat);
            if (ledger.GuestSteps(seat) is { } exit)
            {
                await Bow(choiceContext, owner!, exit, mayReturn: false);
                ledger.GuestReturns(seat, index, fanfare);
            }
        }
        else if (ledger.IsFull)
        {
            if (atFront)
            {
                await RecastFromBack(choiceContext, owner!, who, fanfare);
            }
            else
            {
                await RecastFromFront(choiceContext, owner!, who, fanfare);
            }
            return;
        }
        else
        {
            ledger.GuestArrives(who, fanfare, atFront);
        }
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// A FRONT-SEAT GUEST ON A FULL STAGE (the guest seat round, 2026-09-25):
    /// the recast rule with the leaver at the other end. The BACK performer
    /// Bows (a real Bow: its act and every Bow reader, but no Five-Century
    /// return, <see cref="RecastFromFront"/>'s reason) and leaves, and the
    /// guest arrives at the front holding <paramref name="arrival"/> plus the
    /// leaver's remaining Fanfare. Bow, readers, arrival, in that order.
    /// </summary>
    private static async Task RecastFromBack(
        PlayerChoiceContext choiceContext, Creature owner, StagePerformer who,
        int arrival)
    {
        var ledger = FurinaStageLedger.For(owner);
        if (ledger.BowFromBack() is not { } leaver) return;
        await Bow(choiceContext, owner,
                  new StageExit(leaver.Who, StageDeparture.Spent,
                                leaver.Fanfare, FurinaStageLaw.Seats - 1,
                                leaver.LostSinceAct),
                  mayReturn: false);
        ledger.ArriveAtFront(who, leaver.Fanfare + arrival);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageStrip.Refresh(owner);
    }

    /// <summary>
    /// A GUEST'S ACT, ITS BOARD HALF: what the act does once the ledger has
    /// taken its payment. <paramref name="seat"/> is the live seat for an act;
    /// a Bow has none and reads its <paramref name="exit"/>. Filed as
    /// <paramref name="beat"/>, what the board lost or gained measured across
    /// it, as every act is (`EB-735`).
    ///
    /// ARKHE ALIGNMENT'S OUSIA doubles the DAMAGE number (8 to 16, Navia's
    /// Fanfare, Wriothesley's twice-lost) and never the payment (rule 4);
    /// Pneuma doubles Block, which no guest gives.
    /// </summary>
    private static async Task GuestAct(PlayerChoiceContext choiceContext,
                                       Creature owner, StagePerformer who,
                                       string beat, StageSeat? seat,
                                       StageExit? exit)
    {
        var before = Ledger(owner);
        var stage = FurinaStageLedger.For(owner);
        var dmg = stage.ActDamageMultiplier;
        Creature? hit = null;
        var each = -1;
        var struck = -1;
        var shot = HitShot.None;
        switch (who)
        {
            case StagePerformer.Neuvillette:
            {
                var targets = Enemies(owner).ToList();
                var dealt = new List<int>(targets.Count);
                foreach (var enemy in targets)
                {
                    dealt.Add(await ElementalHit.Deal(
                        choiceContext, enemy, Element.Hydro,
                        FurinaStageLaw.ActNeuvilletteDamage * dmg, owner,
                        powered: false));
                }
                each = Even(dealt);
                struck = targets.Count;
                break;
            }
            case StagePerformer.Clorinde:
                (hit, shot) = await HitRandom(
                    choiceContext, owner, Element.Electro,
                    FurinaStageLaw.ActClorindeDamage * dmg);
                break;
            case StagePerformer.Navia:
            {
                var bar = seat?.Fanfare ?? exit?.Held ?? 0;
                if (bar > 0)
                {
                    (hit, shot) = await HitRandom(
                        choiceContext, owner, Element.Geo, bar * dmg);
                }
                break;
            }
            case StagePerformer.Chevreuse:
                await PowerCmd.Apply<EnergyNextTurnPower>(
                    choiceContext, owner, FurinaStageLaw.ActChevreuseEnergy,
                    applier: owner, cardSource: null);
                break;
            case StagePerformer.Wriothesley:
            {
                var lost = seat?.LostSinceAct ?? exit?.Lost ?? 0;
                if (lost > 0)
                {
                    (hit, shot) = await HitRandom(
                        choiceContext, owner, Element.Cryo,
                        FurinaStageLaw.ActWriothesleyRate * lost * dmg);
                }
                break;
            }
            case StagePerformer.Lynette:
            {
                // 2026-09-25 night (the granted-guest seat round; both seats
                // never played her: "nothing reliably leaves an aura for her
                // Swirl"): "deal 3 Anemo damage to a random enemy, one with an
                // aura if any". The act always lands. Anemo damage on an aura
                // Swirls through `ElementalHit.Deal`'s own reaction step; on
                // none, Anemo never sticks, so it is plain damage.
                var targets = Enemies(owner).ToList();
                var wearing = targets
                    .Where(e => AuraCmd.Find(e) != null).ToList();
                var pool = wearing.Count > 0 ? wearing : targets;
                if (pool.Count > 0)
                {
                    var rng = owner.Player?.RunState.Rng.CombatTargets;
                    var target = rng == null ? pool[0] : rng.NextItem(pool);
                    if (target != null)
                    {
                        hit = target;
                        shot = HitShot.Before(target);
                        shot = shot.Dealt(await ElementalHit.Deal(
                            choiceContext, target, Element.Anemo,
                            FurinaStageLaw.ActLynetteDamage * dmg, owner,
                            powered: false));
                    }
                }
                break;
            }
            // Sigewinne and Charlotte move Fanfare only: the ledger did it.
        }
        // Rule 6: every act resets the reading, so a repeat reads 0.
        if (seat != null) seat.LostSinceAct = 0;
        FurinaStagePets.SyncBars(owner);
        NoteBeat(owner, beat, who, before, hit, each, struck, seat, shot);
    }

    /// <summary>One elemental hit on a random living enemy, unpowered (an act
    /// carries no Strength, `EB-495` D3). The body it picked, or null, and
    /// the hit as dealt with the body's HP and Block before it.</summary>
    private static async Task<(Creature?, HitShot)> HitRandom(
        PlayerChoiceContext choiceContext, Creature owner, Element element,
        int amount)
    {
        if (amount <= 0 || RandomEnemy(owner) is not { } target)
        {
            return (null, HitShot.None);
        }
        var shot = HitShot.Before(target);
        shot = shot.Dealt(await ElementalHit.Deal(
            choiceContext, target, element, amount, owner, powered: false));
        return (target, shot);
    }

    /// <summary>The Bows a payment earned, after the act's effect, oldest
    /// first -- each the ordinary <see cref="Bow"/>, readers and A
    /// Five-Century Act included.</summary>
    private static async Task BowTheOwed(PlayerChoiceContext choiceContext,
                                         Creature owner,
                                         IReadOnlyList<StageExit> owed)
    {
        foreach (var exit in owed)
        {
            if (owner.IsDead || CombatOver()) break;
            await Bow(choiceContext, owner, exit);
        }
        if (owed.Count > 0) await FurinaStagePets.Sync(owner);
    }

    // ==================================================================
    // RULE 7, THE FORECAST. "You can see the end of the turn before you end
    // it." GPT, quoted in the batch: "A report helps the designer; a visible
    // forecast helps the player." Both seat rounds of the day misjudged the
    // damage that reached her, and guests add two more moving parts.
    //
    // PURE: it runs the ledger's own moves on a CLONE of the seats and never
    // touches the stage, the log or the bodies. The acts' Fanfare halves are
    // the very methods the sweep calls (`FurinaStageLedger.ActFanfare`, the
    // fade), so a forecast and a turn end cannot disagree about a payment.
    // ==================================================================

    /// <summary>
    /// The end of this turn, forecast: each performer's Fanfare after the
    /// acts, the payments and the fade; the Block the acts give; and the
    /// posted attacks split between the front performer and Furina, given her
    /// Block after the acts. Null with the arm off.
    /// </summary>
    public static StageForecast? Forecast(Creature? owner)
    {
        if (!LiveFor(owner)) return null;
        var hits = IntentHits(owner!);
        return Forecast(owner!, hits);
    }

    /// <summary>
    /// The forecast against a given list of hits (per hit, after the
    /// attacker's own modifiers): what the headless pins script.
    /// <paramref name="enemies"/> is the hittable enemies the acts can land
    /// on, by name and whether each wears an aura; null reads the combat's.
    /// </summary>
    public static StageForecast Forecast(Creature owner,
                                         IReadOnlyList<int>? hits,
                                         IReadOnlyList<StageForecastEnemy>? enemies = null)
    {
        var real = FurinaStageLedger.For(owner);
        var clone = real.CloneForForecast();
        var seats = clone.Seats.ToList();
        var now = seats.Select(s => s.Fanfare).ToList();
        var applause = owner.Powers.OfType<ThunderousApplausePower>()
            .Select(p => (int)p.Amount).ToList();
        var returns = owner.Powers.OfType<FiveCenturyActPower>().Any();
        var foes = enemies ?? ForecastEnemies(owner);
        var run = new ForecastRun(clone, applause, returns,
                                  foes.Any(e => e.Aura));

        // The sweep, in the sweep's order (`EndOfTurnActs`). What the acts
        // DEAL is recorded here and only here: a Bow on the enemy's turn is
        // not the end of this turn.
        run.Sweep = true;
        var times = 1 + (clone.IsFull ? FullHouseActs(owner) : 0);
        foreach (var seat in seats)
        {
            if (seat.Resting) continue;
            for (var i = 0; i < times; i++)
            {
                if (!clone.Holds(seat)) break;
                run.Act(seat.Who, seat, null);
            }
        }
        run.Sweep = false;
        clone.EndRest();
        clone.ResetActMultipliers();
        clone.Fade();

        var rows = new List<StageForecastSeat>();
        for (var i = 0; i < seats.Count; i++)
        {
            var stays = clone.Holds(seats[i]);
            rows.Add(new StageForecastSeat(
                seats[i].Who, now[i], stays ? seats[i].Fanfare : 0, !stays));
        }
        var arrivals = clone.Seats.Where(s => !seats.Contains(s))
            .Select(s => new StageForecastSeat(s.Who, 0, s.Fanfare, false))
            .ToList();

        // The enemy's turn: her Block after the acts, then each hit in turn
        // on her Block, the front performer's bar, then her (rule 6). HIT BY
        // HIT (2026-09-25 night, the granted-guest seat round: "the split
        // ignored the next performer"): a front a hit empties Bows before the
        // rest of that hit reaches her -- the ledger's own `Absorb` spends
        // Usher's Bow Block on it -- and the next performer steps up and
        // takes the later hits. Each performer's share is its own row.
        var block = (int)owner.Block + run.Block;
        var afterActs = block;
        var front = 0;
        var furina = 0;
        var takers = new List<(StageSeat Seat, int Takes, bool Leaves)>();
        var rapt = owner.Powers.OfType<RaptAudiencePower>()
            .Select(p => (int)p.Amount).ToList();
        foreach (var hit in hits ?? System.Array.Empty<int>())
        {
            var through = System.Math.Max(0, hit - block);
            block = System.Math.Max(0, block - hit);
            if (through <= 0) continue;
            var lead = clone.Lead;
            var twoOrMore = clone.Seats.Count >= 2;
            var result = clone.Absorb(through);
            front += result.Absorbed;
            furina += result.ReachedFurina;
            if (lead != null && result.Absorbed > 0)
            {
                var at = takers.FindIndex(t => ReferenceEquals(t.Seat, lead));
                if (at < 0)
                {
                    takers.Add((lead, result.Absorbed, result.Exit != null));
                }
                else
                {
                    takers[at] = (lead, takers[at].Takes + result.Absorbed,
                                  result.Exit != null);
                }
            }
            // A Rapt Audience, as `AbsorbHit` pays it.
            if (twoOrMore && result.Absorbed > 0)
            {
                foreach (var amount in rapt)
                {
                    clone.Raise(amount);
                }
            }
            run.Block = 0;
            if (result.Exit is { } gone) run.Bow(gone);
            block += run.Block;
        }

        // What the acts deal in all, where every act lands on the same one
        // body (a board of one) or on ALL of them.
        var total = -1;
        var totalTarget = "";
        if (run.Acts.Count > 0)
        {
            if (foes.Count == 1)
            {
                total = run.Acts.Sum(a => a.Amount);
                totalTarget = foes[0].Name;
            }
            else if (run.Acts.All(a => a.Target == StageForecastAct.All))
            {
                total = run.Acts.Sum(a => a.Amount);
                totalTarget = StageForecastAct.All;
            }
        }
        return new StageForecast(
            rows, arrivals, afterActs, hits != null, front, furina,
            run.Unknown)
        {
            Acts = run.Acts,
            ActTotal = total,
            ActTotalTarget = totalTarget,
            Takers = takers
                .Select(t => new StageForecastTake(t.Seat.Who, t.Takes,
                                                   t.Leaves))
                .ToList(),
        };
    }

    /// <summary>The combat's hittable enemies, by printed name and whether
    /// each wears an aura, for the forecast's act lines. Empty where there is
    /// no combat.</summary>
    private static IReadOnlyList<StageForecastEnemy> ForecastEnemies(
        Creature owner) =>
        Enemies(owner)
            .Select(e => new StageForecastEnemy(
                e.Monster?.Title.ToString() ?? e.Name ?? "",
                AuraCmd.Find(e) != null))
            .ToList();

    /// <summary>
    /// The posted attacks, one entry per hit, each the number the game's own
    /// intent draws (`AttackIntent`'s folded damage), or null where there is
    /// no combat to read. A read that throws is skipped, never guessed.
    /// </summary>
    private static IReadOnlyList<int>? IntentHits(Creature owner)
    {
        var combat = owner.CombatState;
        if (combat == null) return null;
        var hits = new List<int>();
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy.Monster?.NextMove is not { } move) continue;
            foreach (var intent in move.Intents)
            {
                if (intent is not AttackIntent attack) continue;
                try
                {
                    var per = attack.GetSingleDamage(
                        combat.PlayerCreatures, enemy);
                    for (var i = 0; i < System.Math.Max(1, attack.Repeats); i++)
                    {
                        hits.Add(per);
                    }
                }
                catch (System.Exception)
                {
                    // An intent the game cannot price here is left out.
                }
            }
        }
        return hits;
    }

    /// <summary>The forecast's replay of acts and Bows on the clone: the
    /// ledger's own Fanfare moves, Usher's Block, each Bow's readers, and --
    /// during the sweep -- what each act deals and to whom.
    /// </summary>
    private sealed class ForecastRun
    {
        private readonly FurinaStageLedger _stage;
        private readonly List<int> _applause;
        private readonly bool _returns;
        private readonly bool _aura;

        internal ForecastRun(FurinaStageLedger stage, List<int> applause,
                             bool returns, bool aura)
        {
            _stage = stage;
            _applause = applause;
            _returns = returns;
            _aura = aura;
        }

        /// <summary>Block the replayed acts gave her.</summary>
        internal int Block;

        /// <summary>True where a Bow reader's Raise met an empty stage: the
        /// game then summons a RANDOM performer, which no forecast can name.
        /// </summary>
        internal bool Unknown;

        /// <summary>True while the end-of-turn sweep is replayed: only then
        /// is an act's damage a line of the forecast.</summary>
        internal bool Sweep;

        /// <summary>What the sweep's acts and Bows deal, in order.</summary>
        internal readonly List<StageForecastAct> Acts = new();

        internal void Act(StagePerformer who, StageSeat? seat, StageExit? exit)
        {
            var owed = new List<StageExit>();
            // An act that cannot pay does nothing, and has no damage line.
            if (!_stage.ActFanfare(who, seat, exit, owed)) return;
            if (who == StagePerformer.Usher)
            {
                Block += System.Math.Max(0,
                    FurinaStageLaw.ActUsherBlock * _stage.ActBlockMultiplier
                    - (exit?.Caught ?? 0));
            }
            if (Sweep && Damage(who, seat, exit) is { } line) Acts.Add(line);
            if (seat != null) seat.LostSinceAct = 0;
            foreach (var gone in owed) Bow(gone);
        }

        /// <summary>One act's damage as its tip prints it, at this turn's
        /// Ousia multiple, or null for an act that deals none. Read before
        /// the act resets Wriothesley's reading, as the act itself does.
        /// </summary>
        private StageForecastAct? Damage(StagePerformer who, StageSeat? seat,
                                         StageExit? exit)
        {
            var dmg = _stage.ActDamageMultiplier;
            var bow = seat == null;
            StageForecastAct Line(int amount, string element, string target) =>
                new(who, amount * dmg, element, target, bow);
            switch (who)
            {
                case StagePerformer.Chevalmarin:
                    return Line(FurinaStageLaw.ActChevalmarinDamage, "",
                                StageForecastAct.All);
                case StagePerformer.Crabaletta:
                    return Line(FurinaStageLaw.ActCrabalettaDamage, "",
                                StageForecastAct.Random);
                case StagePerformer.Neuvillette:
                    return Line(FurinaStageLaw.ActNeuvilletteDamage, "Hydro",
                                StageForecastAct.All);
                case StagePerformer.Clorinde:
                    return Line(FurinaStageLaw.ActClorindeDamage, "Electro",
                                StageForecastAct.Random);
                case StagePerformer.Navia:
                {
                    var bar = seat?.Fanfare ?? exit?.Held ?? 0;
                    return bar > 0
                        ? Line(bar, "Geo", StageForecastAct.Random)
                        : null;
                }
                case StagePerformer.Wriothesley:
                {
                    var lost = seat?.LostSinceAct ?? exit?.Lost ?? 0;
                    return lost > 0
                        ? Line(FurinaStageLaw.ActWriothesleyRate * lost, "Cryo",
                               StageForecastAct.Random)
                        : null;
                }
                case StagePerformer.Lynette:
                    return Line(FurinaStageLaw.ActLynetteDamage, "Anemo",
                                _aura ? StageForecastAct.RandomAura
                                      : StageForecastAct.Random);
                default:
                    return null;
            }
        }

        internal void Bow(StageExit exit)
        {
            Act(exit.Who, null, exit);
            foreach (var amount in _applause)
            {
                if (_stage.IsEmpty)
                {
                    Unknown = true;
                    continue;
                }
                _stage.Raise(amount);
            }
            if (_returns) _stage.ReturnToBack(exit.Who);
        }
    }
}

/// <summary>One performer's line of the forecast: its bar now and after the
/// turn's end, and whether it leaves.</summary>
public readonly record struct StageForecastSeat(
    StagePerformer Who, int Now, int After, bool Leaves);

/// <summary>
/// 2026-09-25 night (the granted-guest seat round): ONE ACT'S DAMAGE in the
/// end-of-turn forecast. Lane 2 left a Beetle on 1 HP because the forecast
/// printed Block and Fanfare and never what the acts deal. The act's own
/// number at this turn's Ousia multiple, before the target's modifiers;
/// <see cref="Element"/> is empty for the trio's plain damage;
/// <see cref="Target"/> is <see cref="All"/>, <see cref="Random"/> or
/// <see cref="RandomAura"/> (Lynette's "one with an aura if any", where one
/// wears an aura). <see cref="Bow"/> marks a performer's Bow inside the sweep
/// (a guest whose payment emptied it).
/// </summary>
public readonly record struct StageForecastAct(
    StagePerformer Who, int Amount, string Element, string Target, bool Bow)
{
    public const string All = "all";
    public const string Random = "random";
    public const string RandomAura = "random_aura";
}

/// <summary>One performer's share of the posted attacks, walked hit by hit:
/// what it takes, and whether it leaves (and Bows).</summary>
public readonly record struct StageForecastTake(
    StagePerformer Who, int Takes, bool Leaves);

/// <summary>A body the acts can land on: its printed name, and whether it
/// wears an aura.</summary>
public readonly record struct StageForecastEnemy(string Name, bool Aura);

/// <summary>
/// RULE 7's whole forecast. <see cref="Seats"/> is the stage as it stands, in
/// seat order; <see cref="Arrivals"/> is anyone a Bow brings back before the
/// turn ends (A Five-Century Act). <see cref="BlockAfterActs"/> is her Block
/// once the acts have given theirs. <see cref="FrontTakes"/> and
/// <see cref="ReachesFurina"/> are the posted attacks' split, known only
/// where <see cref="IntentKnown"/>, and <see cref="Takers"/> is the same
/// split performer by performer. <see cref="Unknown"/> says a Bow reader
/// will summon a random performer the forecast cannot name.
/// <see cref="Acts"/> is what the sweep's acts deal; <see cref="ActTotal"/>
/// their sum where every act lands on one body or on ALL (-1 otherwise), and
/// <see cref="ActTotalTarget"/> that body's name or
/// <see cref="StageForecastAct.All"/>.
/// </summary>
public sealed record StageForecast(
    IReadOnlyList<StageForecastSeat> Seats,
    IReadOnlyList<StageForecastSeat> Arrivals,
    int BlockAfterActs, bool IntentKnown, int FrontTakes, int ReachesFurina,
    bool Unknown)
{
    public IReadOnlyList<StageForecastAct> Acts { get; init; } =
        System.Array.Empty<StageForecastAct>();

    public int ActTotal { get; init; } = -1;

    public string ActTotalTarget { get; init; } = "";

    public IReadOnlyList<StageForecastTake> Takers { get; init; } =
        System.Array.Empty<StageForecastTake>();
}
