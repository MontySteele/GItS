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
    ///     the back holding the front's Fanfare (<see cref="RecastFromFront"/>,
    ///     "like any summon");
    ///   * otherwise: the back-most empty seat, holding <paramref name="fanfare"/>.
    ///
    /// It does not act on arrival (`EB-738`): it acts at the end of the turn
    /// with everyone else.
    /// </summary>
    public static async Task GuestStar(PlayerChoiceContext choiceContext,
                                       Creature? owner, string member,
                                       int fanfare)
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
            await RecastFromFront(choiceContext, owner!, who);
            return;
        }
        else
        {
            ledger.GuestArrives(who, fanfare);
        }
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
                hit = await HitRandom(choiceContext, owner, Element.Electro,
                                      FurinaStageLaw.ActClorindeDamage * dmg);
                break;
            case StagePerformer.Navia:
            {
                var bar = seat?.Fanfare ?? exit?.Held ?? 0;
                if (bar > 0)
                {
                    hit = await HitRandom(choiceContext, owner, Element.Geo,
                                          bar * dmg);
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
                    hit = await HitRandom(
                        choiceContext, owner, Element.Cryo,
                        FurinaStageLaw.ActWriothesleyRate * lost * dmg);
                }
                break;
            }
            case StagePerformer.Lynette:
            {
                var wearing = Enemies(owner)
                    .Where(e => AuraCmd.Find(e) != null).ToList();
                if (wearing.Count > 0)
                {
                    var rng = owner.Player?.RunState.Rng.CombatTargets;
                    var target = rng == null ? wearing[0]
                                             : rng.NextItem(wearing);
                    if (target != null)
                    {
                        hit = target;
                        await ElementalHit.ApplyOnly(
                            choiceContext, target, Element.Anemo, owner);
                    }
                }
                break;
            }
            // Sigewinne and Charlotte move Fanfare only: the ledger did it.
        }
        // Rule 6: every act resets the reading, so a repeat reads 0.
        if (seat != null) seat.LostSinceAct = 0;
        FurinaStagePets.SyncBars(owner);
        NoteBeat(owner, beat, who, before, hit, each, struck, seat);
    }

    /// <summary>One elemental hit on a random living enemy, unpowered (an act
    /// carries no Strength, `EB-495` D3). The body it picked, or null.</summary>
    private static async Task<Creature?> HitRandom(
        PlayerChoiceContext choiceContext, Creature owner, Element element,
        int amount)
    {
        if (amount <= 0 || RandomEnemy(owner) is not { } target) return null;
        await ElementalHit.Deal(choiceContext, target, element, amount, owner,
                                powered: false);
        return target;
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
    /// </summary>
    public static StageForecast Forecast(Creature owner,
                                         IReadOnlyList<int>? hits)
    {
        var real = FurinaStageLedger.For(owner);
        var clone = real.CloneForForecast();
        var seats = clone.Seats.ToList();
        var now = seats.Select(s => s.Fanfare).ToList();
        var applause = owner.Powers.OfType<ThunderousApplausePower>()
            .Select(p => (int)p.Amount).ToList();
        var returns = owner.Powers.OfType<FiveCenturyActPower>().Any();
        var run = new ForecastRun(clone, applause, returns);

        // The sweep, in the sweep's order (`EndOfTurnActs`).
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
        // on her Block, the front performer's bar, then her (rule 6). A hit's
        // Bow is paid right after the hit (rule 7), so a front Usher emptied
        // by one gives his Block to the next.
        var block = (int)owner.Block + run.Block;
        var afterActs = block;
        var front = 0;
        var furina = 0;
        var rapt = owner.Powers.OfType<RaptAudiencePower>()
            .Select(p => (int)p.Amount).ToList();
        foreach (var hit in hits ?? System.Array.Empty<int>())
        {
            var through = System.Math.Max(0, hit - block);
            block = System.Math.Max(0, block - hit);
            if (through <= 0) continue;
            if (clone.Lead is not { } lead)
            {
                furina += through;
                continue;
            }
            var twoOrMore = clone.Seats.Count >= 2;
            var taken = System.Math.Min(through, lead.Fanfare);
            front += taken;
            furina += through - taken;
            var exit = clone.Absorb(taken);
            // A Rapt Audience, as `AbsorbHit` pays it.
            if (twoOrMore && taken > 0)
            {
                foreach (var pct in rapt)
                {
                    clone.Raise((int)System.Math.Ceiling(taken * pct / 100m));
                }
            }
            run.Block = 0;
            if (exit.Exit is { } gone) run.Bow(gone);
            block += run.Block;
        }
        return new StageForecast(rows, arrivals, afterActs, hits != null,
                                 front, furina, run.Unknown);
    }

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
    /// ledger's own Fanfare moves, Usher's Block, and each Bow's readers.
    /// </summary>
    private sealed class ForecastRun
    {
        private readonly FurinaStageLedger _stage;
        private readonly List<int> _applause;
        private readonly bool _returns;

        internal ForecastRun(FurinaStageLedger stage, List<int> applause,
                             bool returns)
        {
            _stage = stage;
            _applause = applause;
            _returns = returns;
        }

        /// <summary>Block the replayed acts gave her.</summary>
        internal int Block;

        /// <summary>True where a Bow reader's Raise met an empty stage: the
        /// game then summons a RANDOM performer, which no forecast can name.
        /// </summary>
        internal bool Unknown;

        internal void Act(StagePerformer who, StageSeat? seat, StageExit? exit)
        {
            var owed = new List<StageExit>();
            if (!_stage.ActFanfare(who, seat, exit, owed)) return;
            if (who == StagePerformer.Usher)
            {
                Block += FurinaStageLaw.ActUsherBlock
                         * _stage.ActBlockMultiplier;
            }
            if (seat != null) seat.LostSinceAct = 0;
            foreach (var gone in owed) Bow(gone);
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
/// RULE 7's whole forecast. <see cref="Seats"/> is the stage as it stands, in
/// seat order; <see cref="Arrivals"/> is anyone a Bow brings back before the
/// turn ends (A Five-Century Act). <see cref="BlockAfterActs"/> is her Block
/// once the acts have given theirs. <see cref="FrontTakes"/> and
/// <see cref="ReachesFurina"/> are the posted attacks' split, known only
/// where <see cref="IntentKnown"/>. <see cref="Unknown"/> says a Bow reader
/// will summon a random performer the forecast cannot name.
/// </summary>
public sealed record StageForecast(
    IReadOnlyList<StageForecastSeat> Seats,
    IReadOnlyList<StageForecastSeat> Arrivals,
    int BlockAfterActs, bool IntentKnown, int FrontTakes, int ReachesFurina,
    bool Unknown);
