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
        Vfx.FurinaStageCues.Refresh(owner);
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
        // The seat it left is the back one of a full stage: with it gone,
        // the count standing IS that seat's index (2 on three seats, 3 under
        // Sold Out), read rather than assumed.
        await Bow(choiceContext, owner,
                  new StageExit(leaver.Who, StageDeparture.Spent,
                                leaver.Fanfare, ledger.Seats.Count,
                                leaver.LostSinceAct),
                  mayReturn: false);
        ledger.ArriveAtFront(who, leaver.Fanfare + arrival);
        await FurinaStagePets.Sync(owner);
        Vfx.FurinaStageCues.Refresh(owner);
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
                                  foes.Any(e => e.Aura), seats);

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
        // 2026-09-26 (the cues): what the acts' payments and taxes took off
        // each bar, and then what the fade took, read off the clone's own
        // beats -- the ledger's `pay` and `fade` moves, filed by seat key.
        var paid = TallyBeats(clone.Beats, 0, clone.Beats.Count,
                              FurinaStageLedger.PayEvent);
        var sweepEnd = clone.Beats.Count;
        clone.EndRest();
        clone.ResetActMultipliers();
        clone.Fade();
        var faded = TallyBeats(clone.Beats, sweepEnd, clone.Beats.Count,
                               FurinaStageLedger.FadeEvent);

        var rows = new List<StageForecastSeat>();
        for (var i = 0; i < seats.Count; i++)
        {
            var stays = clone.Holds(seats[i]);
            var key = seats[i].Key;
            rows.Add(new StageForecastSeat(
                seats[i].Who, now[i], stays ? seats[i].Fanfare : 0, !stays,
                key, paid.GetValueOrDefault(key),
                faded.GetValueOrDefault(key)));
        }
        var arrivals = clone.Seats.Where(s => !seats.Contains(s))
            .Select(s => new StageForecastSeat(s.Who, 0, s.Fanfare, false,
                                               s.Key))
            .ToList();
        var cues = run.Cues(rows);

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
                                                   t.Leaves, t.Seat.Key))
                .ToList(),
            Cues = cues,
        };
    }

    /// <summary>What beats of <paramref name="kind"/> in
    /// <c>[from, to)</c> moved, summed per seat key. A beat whose seat the
    /// ledger could not name (key -1) is left out.</summary>
    private static Dictionary<int, int> TallyBeats(
        IReadOnlyList<StageBeat> beats, int from, int to, string kind)
    {
        var sums = new Dictionary<int, int>();
        for (var i = from; i < to; i++)
        {
            var beat = beats[i];
            if (beat.Event != kind || beat.SeatKey < 0) continue;
            sums[beat.SeatKey] = sums.GetValueOrDefault(beat.SeatKey)
                                 + beat.Moved;
        }
        return sums;
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

        /// <summary>The stage as the sweep found it, front first: the seats
        /// a cue is drawn over.</summary>
        private readonly IReadOnlyList<StageSeat> _company;

        /// <summary>Per seat, what its acts in the sweep did (the cues).
        /// </summary>
        private readonly Dictionary<StageSeat, CueTally> _tally =
            new(ReferenceEqualityComparer.Instance);

        /// <summary>Seats whose sweep Bow has been put down to them.</summary>
        private readonly HashSet<StageSeat> _bowed =
            new(ReferenceEqualityComparer.Instance);

        internal ForecastRun(FurinaStageLedger stage, List<int> applause,
                             bool returns, bool aura,
                             IReadOnlyList<StageSeat> company)
        {
            _stage = stage;
            _applause = applause;
            _returns = returns;
            _aura = aura;
            _company = company;
            // Read now: the sweep's end clears it (`EndRest`) before the
            // cues are made.
            _resting = new HashSet<StageSeat>(
                company.Where(s => s.Resting), ReferenceEqualityComparer.Instance);
        }

        /// <summary>The seats resting through this sweep.</summary>
        private readonly HashSet<StageSeat> _resting;

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
            var mark = _stage.Beats.Count;
            // 2026-09-26 (the cues): the seat this act is drawn over -- the
            // actor, or, for a Bow the sweep's own payment earned, the seat
            // it has just left. Only the sweep's acts are cues.
            var over = !Sweep ? null
                : seat ?? (exit is { } left ? BowedFrom(left) : null);
            // An act that cannot pay does nothing, and has no damage line.
            if (!_stage.ActFanfare(who, seat, exit, owed))
            {
                if (over != null) Tally(over, who).Refused(this, seat, exit);
                return;
            }
            var block = 0;
            if (who == StagePerformer.Usher)
            {
                block = System.Math.Max(0,
                    FurinaStageLaw.ActUsherBlock * _stage.ActBlockMultiplier
                    - (exit?.Caught ?? 0));
                Block += block;
            }
            var line = Sweep ? Damage(who, seat, exit) : null;
            if (line is { } dealt) Acts.Add(dealt);
            if (over != null)
            {
                Tally(over, who).Performed(
                    Effect(who, block, line, mark), line,
                    PaidSince(who, mark));
            }
            if (seat != null) seat.LostSinceAct = 0;
            foreach (var gone in owed) Bow(gone);
        }

        // ---- THE CUES (2026-09-26, the Furina balance review, pick 2a) ----
        //
        // [USER]: "each performer shows its act over its head the way an
        // enemy shows its intent". Every number a cue prints is recorded
        // here, off the same replay that makes the rest of the forecast: the
        // act's damage line, Usher's Block as the forecast adds it, a gift
        // or a payment as the ledger's own beat files it.

        /// <summary>What one act did, as its cue prints it: the Block, the
        /// damage, the Energy, or the Fanfare a gift moved.</summary>
        private int Effect(StagePerformer who, int block,
                           StageForecastAct? line, int mark)
        {
            switch (StageForecastCue.KindOf(who))
            {
                case StageCueKind.Block:
                    return block;
                case StageCueKind.Energy:
                    return FurinaStageLaw.ActChevreuseEnergy;
                case StageCueKind.Gift:
                {
                    // Sigewinne's gift is the whole raise she made; Charlotte's
                    // is what EACH other performer gained.
                    var raises = BeatsSince(mark, "raise").ToList();
                    if (raises.Count == 0) return 0;
                    return who == StagePerformer.Charlotte
                        ? raises[0].Moved
                        : raises.Sum(b => b.Moved);
                }
                default:
                    return line?.Amount ?? 0;
            }
        }

        /// <summary>The price the performer's cue carries: what this act's
        /// payment took, for the two guests whose act is PRICED (Neuvillette
        /// pays his own, Chevreuse spends the back performer's). Clorinde's
        /// tax and Sigewinne's gift are Fanfare too, but their cue does not
        /// carry them: the tax shows on the bars it takes from, and the gift
        /// IS her number.</summary>
        private int PaidSince(StagePerformer who, int mark) =>
            StageForecastCue.Priced(who)
                ? BeatsSince(mark, FurinaStageLedger.PayEvent).Sum(b => b.Moved)
                : 0;

        private IEnumerable<StageBeat> BeatsSince(int mark, string kind)
        {
            for (var i = mark; i < _stage.Beats.Count; i++)
            {
                if (_stage.Beats[i].Event == kind) yield return _stage.Beats[i];
            }
        }

        /// <summary>The seat a sweep Bow is drawn over: the first seat of
        /// that performer the sweep found and the stage no longer holds, and
        /// only once.</summary>
        private StageSeat? BowedFrom(StageExit exit)
        {
            foreach (var seat in _company)
            {
                if (seat.Who != exit.Who || _stage.Holds(seat)
                    || _bowed.Contains(seat))
                {
                    continue;
                }
                _bowed.Add(seat);
                return seat;
            }
            return null;
        }

        private CueTally Tally(StageSeat seat, StagePerformer who)
        {
            if (!_tally.TryGetValue(seat, out var tally))
            {
                tally = new CueTally(who);
                _tally[seat] = tally;
            }
            return tally;
        }

        /// <summary>The cues, one per seat the sweep found, in seat order.
        /// </summary>
        internal IReadOnlyList<StageForecastCue> Cues(
            IReadOnlyList<StageForecastSeat> rows)
        {
            var cues = new List<StageForecastCue>(_company.Count);
            for (var i = 0; i < _company.Count; i++)
            {
                var seat = _company[i];
                var leaves = i < rows.Count && rows[i].Leaves;
                if (_resting.Contains(seat))
                {
                    // A Five-Century Act's returnee sits this sweep out.
                    cues.Add(new StageForecastCue(
                        seat.Who, seat.Key, StageForecastCue.KindOf(seat.Who),
                        -1, "", "", 0, 0, false, true, leaves));
                    continue;
                }
                var tally = _tally.GetValueOrDefault(seat)
                            ?? new CueTally(seat.Who);
                cues.Add(tally.Cue(seat, leaves));
            }
            return cues;
        }

        /// <summary>One seat's acts in the sweep.</summary>
        private sealed class CueTally
        {
            private readonly StagePerformer _who;
            private readonly List<int> _amounts = new();
            private string _element = "";
            private string _target = "";
            private int _price;
            private bool _refused;
            private int _wouldBe = -1;
            private int _wouldPay;

            internal CueTally(StagePerformer who) => _who = who;

            /// <summary>An act that paid, and what it did.</summary>
            internal void Performed(int amount, StageForecastAct? line,
                                    int paid)
            {
                _amounts.Add(amount);
                if (line is { } act)
                {
                    _element = act.Element;
                    _target = act.Target;
                }
                if (_price == 0) _price = paid;
            }

            /// <summary>An act that could not pay (rule 4): nothing
            /// happened, and the cue shows what it would have done, greyed.
            /// </summary>
            internal void Refused(ForecastRun run, StageSeat? seat,
                                  StageExit? exit)
            {
                _refused = true;
                if (_wouldBe >= 0) return;
                var line = run.Damage(_who, seat, exit);
                _wouldBe = StageForecastCue.KindOf(_who) switch
                {
                    StageCueKind.Energy => FurinaStageLaw.ActChevreuseEnergy,
                    _ => line?.Amount ?? 0,
                };
                if (line is { } act)
                {
                    _element = act.Element;
                    _target = act.Target;
                }
                _wouldPay = StageForecastCue.PriceOf(_who);
            }

            internal StageForecastCue Cue(StageSeat seat, bool leaves)
            {
                var kind = StageForecastCue.KindOf(_who);
                var landed = _amounts.Where(a => a > 0).ToList();
                if (landed.Count > 0)
                {
                    // Every act alike: its number and the count. Acts that
                    // differ (a gift that ran short, then a free Bow): their
                    // sum, once.
                    var alike = landed.All(a => a == landed[0]);
                    return new StageForecastCue(
                        _who, seat.Key, kind,
                        alike ? landed[0] : landed.Sum(), _element, _target,
                        alike ? landed.Count : 1, _price, false, false,
                        leaves);
                }
                // Nothing landed: it could not pay, or its act came to 0
                // (Wriothesley on a turn nothing hit him).
                var unpaid = _refused && _amounts.Count == 0;
                return new StageForecastCue(
                    _who, seat.Key, kind, unpaid ? _wouldBe : 0, _element,
                    _target, 0, unpaid ? _wouldPay : _price, unpaid, false,
                    leaves);
            }
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
/// turn's end, and whether it leaves. Since 2026-09-26 (the cues) also the
/// seat's <see cref="StageSeat.Key"/>, what the acts' payments and taxes take
/// off it (<paramref name="Paid"/>, the ledger's `pay` beats) and what the
/// fade then takes (<paramref name="Faded"/>, its `fade` beats).</summary>
public readonly record struct StageForecastSeat(
    StagePerformer Who, int Now, int After, bool Leaves, int Key = -1,
    int Paid = 0, int Faded = 0);

/// <summary>What a performer's act is, as its cue draws it.</summary>
public enum StageCueKind
{
    /// <summary>Usher: Block for Furina.</summary>
    Block,

    /// <summary>Every damage act, one target, random or ALL.</summary>
    Damage,

    /// <summary>Chevreuse: Energy next turn.</summary>
    Energy,

    /// <summary>Sigewinne and Charlotte: Fanfare for other performers.</summary>
    Gift,
}

/// <summary>
/// 2026-09-26 (the Furina balance review, pick 2a): ONE PERFORMER'S CUE, what
/// it will do at the end of this turn, read off the forecast's own replay.
/// <see cref="Amount"/> is one act's number (-1 for a resting returnee, which
/// does not act); <see cref="Times"/> how many acts land (Full House, or a
/// payment that empties it and earns its Bow), 0 where none does --
/// <see cref="Unpaid"/> (rule 4: it cannot pay, and <see cref="Amount"/> and
/// <see cref="Price"/> are what it would have done) or an act that comes to 0
/// (Wriothesley on a turn nothing hit him). <see cref="Price"/> is what a
/// priced act pays (Neuvillette, Chevreuse). <see cref="Element"/> and
/// <see cref="Target"/> are its damage line's.
/// </summary>
public readonly record struct StageForecastCue(
    StagePerformer Who, int Key, StageCueKind Kind, int Amount,
    string Element, string Target, int Times, int Price, bool Unpaid,
    bool Resting, bool Leaves)
{
    /// <summary>The kind of act a performer has.</summary>
    public static StageCueKind KindOf(StagePerformer who) => who switch
    {
        StagePerformer.Usher => StageCueKind.Block,
        StagePerformer.Chevreuse => StageCueKind.Energy,
        StagePerformer.Sigewinne or StagePerformer.Charlotte =>
            StageCueKind.Gift,
        _ => StageCueKind.Damage,
    };

    /// <summary>Does this performer's cue carry a price?</summary>
    public static bool Priced(StagePerformer who) =>
        who is StagePerformer.Neuvillette or StagePerformer.Chevreuse;

    /// <summary>The printed price of a priced act, for the cue of one that
    /// cannot pay; 0 for every other performer.</summary>
    public static int PriceOf(StagePerformer who) => who switch
    {
        StagePerformer.Neuvillette => FurinaStageLaw.ActNeuvillettePrice,
        StagePerformer.Chevreuse => FurinaStageLaw.ActChevreusePrice,
        _ => 0,
    };
}

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
/// what it takes, and whether it leaves (and Bows). <paramref name="Key"/> is
/// its seat's (2026-09-26, the bar chips: two Ushers are two bars).</summary>
public readonly record struct StageForecastTake(
    StagePerformer Who, int Takes, bool Leaves, int Key = -1);

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

    /// <summary>2026-09-26: one cue per performer on the stage as it stands,
    /// in seat order (<see cref="StageForecastCue"/>).</summary>
    public IReadOnlyList<StageForecastCue> Cues { get; init; } =
        System.Array.Empty<StageForecastCue>();
}
