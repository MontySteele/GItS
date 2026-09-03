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
        // R236, Gorou's Crystal Collapse (the Inazuma workshop's one
        // Personal): "Plan: play a copy of the last other Companion card you
        // played this turn." The card it holds is captured when the Plan is
        // WRITTEN -- see <see cref="Schedule"/> -- and a copy of it is played
        // for free at the morning.
        PlayCopyOfCompanion,
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
    /// One scheduled clause. <paramref name="Card"/> is set for
    /// <see cref="Kind.ReplayExhausted"/> (Moon's Reflection's chosen card)
    /// and for <see cref="Kind.PlayCopyOfCompanion"/> (Crystal Collapse's
    /// captured Companion), and is the one place a Plan holds an object rather
    /// than a number. Both are filled in when the Plan is written, never read
    /// off the board at carry-out.
    /// </summary>
    public readonly record struct Planned(
        Kind Kind, int Amount, Aim Aim, CardModel? Card = null);

    /// <summary>
    /// ONE PLAN: the card that wrote it and the clauses it wrote. The card is
    /// kept for the DISPLAY -- the strip draws pending Plans face up, in order,
    /// on the jellyfish -- and for nothing else; the clauses are the whole of
    /// what will happen.
    /// </summary>
    public sealed record Entry(CardModel? Source, IReadOnlyList<Planned> Clauses,
                              string? Label = null)
    {
        /// <summary>What the strip prints for this Plan.
        ///
        /// <paramref name="Label"/> WINS WHERE ONE IS SET, and only a Plan
        /// that HOLDS a card sets one (R236): Crystal Collapse's face means a
        /// different thing every time it is written, so the strip has to say
        /// which card it caught -- "Crystal Collapse: Gorou &#8212; Juuga",
        /// or "Crystal Collapse: nothing" for a turn with no other Companion
        /// in it. Every other Plan is its own card's name, unchanged.</summary>
        public string Title => Label ?? Source?.Title.ToString() ?? "Plan";
    }

    /// <summary>
    /// ONE PLAN THAT HAS BEEN CARRIED OUT, as the screen said it (`EB-317`).
    ///
    /// THREE FIELDS AND ONE OF THEM IS THE OTHER TWO. <paramref name="Card"/>
    /// and <paramref name="Number"/> are the row's own shape -- the card that
    /// was carried out and the number its clause produced, null when the
    /// clause produced none. <paramref name="Line"/> is the string the
    /// jellyfish actually SAID, built by <c>Vfx.KurageBeat.Line</c>, and it
    /// rides the wire because the blind page's contract is that it prints the
    /// ON-SCREEN TEXT rather than a second composition of the same parts. Two
    /// composers in two languages is exactly how a page and a screen come to
    /// disagree about words; there is one, and it is C#.
    /// </summary>
    public readonly record struct CarriedOutPlan(
        string Card, int? Number, string Line);

    private static object? _combat;
    private static readonly Dictionary<Player, List<Entry>> _queues = new();

    /// <summary>
    /// WHAT THE STRIP SHOWS WHILE A MORNING IS RUNNING, and it exists only so
    /// the strip can empty ONE ENTRY AT A TIME IN VIEW (`EB-317`).
    ///
    /// THE QUEUE ITSELF STILL DRAINS IN ONE MOVE, which is the point of doing
    /// it this way rather than popping the real queue per entry. Two rules
    /// depend on the queue being empty for the whole drain -- a Plan written
    /// DURING resolution waits for the next turn, and Change of Plans reached
    /// through Moon's Reflection finds nothing to pull forward -- and the
    /// meter ledger's morning row is ONE note of the whole depth
    /// (`KokomiPlanLedgerTests`). Popping the real queue per entry would move
    /// both. So the DISPLAY gets its own list, and it is display-only:
    /// nothing reads it but <c>Vfx.KokomiPlanStrip</c> through
    /// <see cref="Showing"/>.
    /// </summary>
    private static readonly Dictionary<Player, List<Entry>> _showing = new();

    /// <summary>This turn's carry-out lines, in the order they were said.
    /// Cleared at the top of every morning, so a page never shows yesterday's.
    /// </summary>
    private static readonly
        Dictionary<Player, List<CarriedOutPlan>> _carriedOut = new();

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
    }

    private static void Rebase(Creature kokomi)
    {
        var combat = (object?)kokomi.CombatState;
        if (ReferenceEquals(_combat, combat)) return;
        _combat = combat;
        _queues.Clear();
        _showing.Clear();
        _carriedOut.Clear();
    }

    /// <summary>This seat's queue, front first. Never null.</summary>
    public static IReadOnlyList<Entry> Pending(Player? player) =>
        player != null && _queues.TryGetValue(player, out var q)
            ? q
            : (IReadOnlyList<Entry>)System.Array.Empty<Entry>();

    /// <summary>
    /// WHAT TO DRAW ON THE JELLYFISH RIGHT NOW: the morning's remaining Plans
    /// while one is running, and the pending queue every other moment.
    ///
    /// The badge is deliberately NOT switched over: `PendingPlansPower` says
    /// "carries out N Plans at the start of your NEXT turn", and during the
    /// drain that number really is zero. The strip says what is happening now.
    /// </summary>
    public static IReadOnlyList<Entry> Showing(Player? player) =>
        player != null && _showing.TryGetValue(player, out var drain)
            ? drain
            : Pending(player);

    /// <summary>This turn's carry-out lines. Never null.</summary>
    public static IReadOnlyList<CarriedOutPlan> CarriedOut(Player? player) =>
        player != null && _carriedOut.TryGetValue(player, out var said)
            ? said
            : (IReadOnlyList<CarriedOutPlan>)
              System.Array.Empty<CarriedOutPlan>();

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
        // R236, CRYSTAL COLLAPSE CAPTURES AT WRITING TIME. "The last other
        // Companion card you played THIS TURN" is a fact about the turn the
        // Plan was written on, and the Plan resolves on the next one -- so
        // asking at carry-out would read a turn the face never named and, on
        // the usual morning, find nothing at all.
        //
        // "OTHER" IS FREE HERE and is asserted anyway. This runs inside
        // `OnPlay`, and the ledger's own recorder is an `AfterCardPlayed`
        // listener, so the card writing the Plan has not been recorded yet;
        // the identity test below says so out loud rather than resting on
        // listener order, and it is the same guard the sim needs for real
        // (there the play is recorded BEFORE the body resolves).
        var body = clauses.ToList();
        string? label = null;
        CardModel? held = null;
        if (body.Any(c => c.Kind == Kind.PlayCopyOfCompanion))
        {
            held = KokomiOverhaulLedger.For(kokomi)
                                       .LastCompanionPlayedThisTurn;
            if (held == source) held = null;
            for (var i = 0; i < body.Count; i++)
            {
                if (body[i].Kind == Kind.PlayCopyOfCompanion)
                {
                    body[i] = body[i] with { Card = held };
                }
            }
            label = Label(source, held);
        }
        var entry = new Entry(source, body, label);
        int before = queue.Count;
        queue.Add(entry);
        await Sync(choiceContext, kokomi,
            SparkPower.SourceOf(source), before);

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

    /// <summary>
    /// What the strip prints for a Plan that HOLDS a card (R236).
    ///
    /// THE SHORT NAME IS THE HALF AFTER THE EM DASH. A companion row is named
    /// "&lt;Character&gt; &#8212; &lt;Card&gt;", so the line reads "Crystal
    /// Collapse: ..." rather than repeating Gorou twice inside one strip
    /// entry. The HELD card keeps its whole name, because that is the card the
    /// player will watch resolve. <c>kokomi_plan.plan_label</c> is the twin.
    /// </summary>
    private static string Label(CardModel? source, CardModel? held)
    {
        var name = source?.Title.ToString() ?? "Plan";
        var cut = name.LastIndexOf('—');
        var shortName = cut >= 0 ? name.Substring(cut + 1).Trim() : name;
        if (shortName.Length == 0) shortName = name;
        var what = held?.Title.ToString() ?? "nothing";
        return $"{shortName}: {what}";
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
        // `EB-317`: the morning's own record starts empty, and it starts empty
        // whether or not anything is due -- otherwise a turn with no Plans
        // would leave yesterday's lines on the blind page as if the jellyfish
        // had just said them.
        _carriedOut.Remove(player);
        if (!_queues.TryGetValue(player, out var queue) || queue.Count == 0)
        {
            return;
        }
        var due = new List<Entry>(queue);
        queue.Clear();
        // The display list is handed over BEFORE the sync, because `Sync`
        // refreshes the strip and the strip reads `Showing`: the badge goes
        // away in the same beat the column stays up, which is the true
        // statement (nothing is pending; four things are happening).
        _showing[player] = new List<Entry>(due);
        await Sync(choiceContext, kokomi, "rule:morning_drain", due.Count);

        try
        {
            foreach (var entry in due)
            {
                var times = CarryOutTimes(kokomi);
                for (var i = 0; i < times; i++)
                {
                    await ResolveEntry(choiceContext, kokomi, entry);
                }
                // ONE THUMBNAIL LEAVES, AFTER ITS PLAN HAS HAPPENED. Front
                // first, so the column shortens from the top in the order the
                // Plans were written -- the order the page prints.
                if (_showing.TryGetValue(player, out var shown)
                    && shown.Count > 0)
                {
                    shown.RemoveAt(0);
                }
                Vfx.KokomiPlanStrip.Refresh(kokomi);
            }
        }
        finally
        {
            // A throw inside a Plan must not leave the strip drawing a morning
            // that is over; the display list is torn down on every path.
            _showing.Remove(player);
            Vfx.KokomiPlanStrip.Refresh(kokomi);
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
        int before = queue.Count;
        queue.RemoveAt(0);
        await Sync(choiceContext, kokomi, "rule:carried_out_now", before);
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
        // `EB-317`, the first half of the beat: THE JELLYFISH ACTS BEFORE THE
        // PLAN LANDS. Awaited, so the clause's damage number arrives after the
        // lunge rather than inside it -- the same argument the casket's strike
        // makes one file over.
        await Vfx.KurageBeat.Act(BakeKuragePet.Of(kokomi));

        // THE NUMBER ON THE LINE IS THE FIRST ONE THE PLAN PRODUCED, and
        // "first" is a reading of a card face: War Council prints "Deal 4
        // damage to ALL enemies and apply 1 Weak to each" and is ONE Plan, so
        // the number a player is watching for is the hit, which is also the
        // clause the sheet wrote first. A Plan whose clauses produce nothing at
        // all (Moon's Reflection's replay, Nereid's window) says its name and
        // no number, which is what the row asks for.
        int? number = null;
        foreach (var clause in entry.Clauses)
        {
            var produced = await ResolveOne(choiceContext, kokomi, clause);
            number ??= produced;
        }

        Announce(kokomi, entry.Title, number);

        // SANGO ISSHIN's condition, written HERE because this is the one place
        // a Plan is carried out: the morning queue, Change of Plans' early
        // resolution and The Moon Overlooks the Waters' play-time one all pass
        // through, and all three are the card's printed "carried out a Plan
        // this turn".
        KokomiOverhaulLedger.For(kokomi).NotePlanCarriedOut();

        foreach (var power in kokomi.Powers.ToList())
        {
            if (power is IKokomiPlanListener listener)
            {
                await listener.OnPlanResolved(choiceContext, kokomi);
            }
        }
    }

    /// <summary>
    /// `EB-317`'s second half: SAY WHAT JUST HAPPENED, AND RECORD IT.
    ///
    /// ONE STRING, TWO SURFACES. <c>Vfx.KurageBeat.Line</c> builds the ruled
    /// format once; the bubble over the jellyfish shows it and the wire
    /// carries the same characters to the blind page. The pet says it when
    /// there is a pet -- and Kokomi says it when there is not, the same honest
    /// degradation the casket's dealer takes.
    ///
    /// NOT ON THE LEDGER, and that is `R101b` rather than an oversight: the
    /// meter ledger stays off the page, so what a seat is shown here is the
    /// on-screen line and nothing else.
    /// </summary>
    private static void Announce(Creature kokomi, string card, int? number)
    {
        var line = Vfx.KurageBeat.Line(card, number);
        Vfx.KurageBeat.Say(BakeKuragePet.Of(kokomi) ?? kokomi, line);

        var player = kokomi.Player;
        if (player == null) return;
        if (!_carriedOut.TryGetValue(player, out var said))
        {
            said = new List<CarriedOutPlan>();
            _carriedOut[player] = said;
        }
        said.Add(new CarriedOutPlan(card, number, line));
    }

    /// <summary>
    /// One clause, and THE NUMBER IT PRODUCED -- damage that landed, Block
    /// that stuck, HP that was Mended, cards drawn -- or null when the clause
    /// produces no number a player could read off the board.
    ///
    /// THE RETURN IS A DISPLAY VALUE AND NOTHING ELSE. Every call below is the
    /// call that was already here; what changed is that the number each one
    /// already computed is now handed back instead of dropped, so the line the
    /// jellyfish says is the number that LANDED rather than the number the
    /// sheet printed. `EB-270` makes the same argument for the Bomb badge, and
    /// <c>ElementalHit.Deal</c> returns its truncated total for exactly this.
    /// </summary>
    private static async Task<int?> ResolveOne(
        PlayerChoiceContext choiceContext, Creature kokomi, Planned plan)
    {
        var player = kokomi.Player;
        if (player == null) return null;

        switch (plan.Kind)
        {
            case Kind.Draw:
                await CardPileCmd.Draw(choiceContext, plan.Amount, player);
                return plan.Amount;

            case Kind.Energy:
                await PlayerCmd.GainEnergy(plan.Amount, player);
                return plan.Amount;

            case Kind.Block:
                // POWERED, and rule 3 is why: "your Strength and Dexterity
                // count, since the plans are hers". Draft 2's Plan Block was
                // `Unpowered` on the NC-11 power-sourced-Block line; draft 6
                // states the opposite rule in the brief itself, so a planned
                // Block is `ValueProp.Move` -- the same prop a card's own Block
                // carries, and the same one Dexterity reads.
                return (int)await CreatureCmd.GainBlock(
                    kokomi, plan.Amount, ValueProp.Move, null);

            case Kind.Mend:
                // Mend returns the HP that actually landed, which is the
                // honest number: "Mend 10" into 4 points of room says 4.
                return await KokomiRules.Mend(
                    choiceContext, kokomi, plan.Amount);

            case Kind.Damage:
                return await Hit(choiceContext, kokomi, plan.Aim, plan.Amount);

            case Kind.DamageQuarterMaxHp:
                return await Hit(choiceContext, kokomi, plan.Aim,
                                 KokomiRules.QuarterOfMaxHp(kokomi));

            case Kind.DamagePerCompanionLastTurn:
                // Chain of Command. "Last turn" is read at CARRY-OUT: the Plan
                // was written on turn N and resolves at the top of N+1, and the
                // ledger has rolled by then, so the count it holds is turn N's
                // -- the turn the player was looking at when they wrote it.
                return await Hit(choiceContext, kokomi, plan.Aim,
                                 plan.Amount * KokomiOverhaulLedger.For(kokomi)
                                                   .CompanionsPlayedLastTurn);

            case Kind.ApplyWeak:
                await Debuff<WeakPower>(choiceContext, kokomi, plan);
                return plan.Amount;

            case Kind.ApplyVulnerable:
                await Debuff<VulnerablePower>(choiceContext, kokomi, plan);
                return plan.Amount;

            case Kind.PlanTwice:
                // NO NUMBER. Nereid's Ascension's amount is a window in TURNS,
                // not something the Plan produced on the board, and printing it
                // beside a card name would read as damage.
                await PlanTwicePower.Wear(choiceContext, kokomi, plan.Amount);
                return null;

            case Kind.ReplayExhausted:
                // The replayed card prints its own numbers as it resolves; this
                // clause produced none of its own.
                await Replay(choiceContext, player, plan.Card);
                return null;

            case Kind.PlayCopyOfCompanion:
                // The copy prints its own numbers as it resolves; this
                // clause produced none of its own (`EB-317`'s line names
                // the card alone).
                await PlayCopy(choiceContext, kokomi, plan.Card);
                return null;
        }
        return null;
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
    /// <remarks>
    /// RETURNS THE FIRST TARGET'S LANDED NUMBER (`EB-317`). An ALL-enemies
    /// clause prints a different number over each enemy -- one aura reacts,
    /// another is Vulnerable -- and the line has room for one. The front
    /// enemy's is the one taken, because that is the enemy a single-target
    /// Plan would have hit and the one the player is looking at; every number
    /// is still on screen over its own enemy, drawn by the engine.
    /// </remarks>
    private static async Task<int?> Hit(
        PlayerChoiceContext choiceContext, Creature kokomi, Aim aim, int amount)
    {
        if (amount <= 0) return null;
        int? first = null;
        foreach (var target in Aimed(kokomi, aim))
        {
            if (target.IsDead) continue;
            var landed = await ElementalHit.Deal(
                choiceContext, target, Element.Hydro, amount, kokomi);
            first ??= landed;
        }
        return first;
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
    /// Crystal Collapse's morning (R236): play a free COPY of the Companion
    /// card it caught.
    ///
    /// A COPY, WHICH IS THE DIFFERENCE FROM <see cref="Replay"/> ABOVE. Moon's
    /// Reflection takes the chosen card OUT of the exhaust pile and plays that
    /// instance; this leaves the original wherever the first play sent it and
    /// plays a clone, so the deck is not quietly one card shorter for having
    /// used the Plan. <c>ICombatState.CloneCard</c> is the mod's own clone
    /// door and is what <c>KurageMemory.Fire</c> uses one file over, so the
    /// copy carries the original's upgrade state -- which is what "a copy of
    /// the card you played" says.
    ///
    /// EXHAUSTED AFTER, through the game's own pile rule rather than a special
    /// case: <c>ExhaustOnNextPlay</c> is the flag <c>CardCmd.AutoPlay</c>'s
    /// routing already reads, so the copy leaves play into the exhaust pile
    /// whatever its printed keywords say. A copy that landed in the discard
    /// pile would be a second permanent card in the deck for one Energy.
    ///
    /// THE AIM IS THE PLAN'S OWN, <see cref="FrontEnemy"/>, which is the
    /// reader every planned hit already uses -- so a copied Attack lands where
    /// a planned one would and the arm has one answer to "where does a Plan
    /// point".
    ///
    /// A PLAN THAT CAUGHT NOTHING IS A PRINTED NO-OP, the shape
    /// <see cref="ResolveFront"/>'s empty queue already has: the face says
    /// what it does when there was no other Companion.
    /// </summary>
    private static async Task PlayCopy(
        PlayerChoiceContext choiceContext, Creature kokomi, CardModel? card)
    {
        if (card == null) return;
        if (kokomi.CombatState is not { } combat) return;
        var copy = combat.CloneCard(card);
        copy.ExhaustOnNextPlay = true;
        await CardCmd.AutoPlay(choiceContext, copy, FrontEnemy(kokomi));
    }

    /// One carried-out Plan on the wire (`EB-317`).
    ///
    /// A NAMED METHOD RATHER THAN A LAMBDA INSIDE <see cref="Snapshot"/>, and
    /// the reason is the pin: these three key names are the contract with
    /// `understudy/blindplay.py`, and the only way a headless test can read
    /// them is <c>Il.Strings</c> over the method that holds them. A lambda
    /// compiles into a display class whose name a pin cannot ask for, so the
    /// literals would sit somewhere no test could see -- which is how a
    /// renamed key becomes a silent hole on a seat's page.
    /// </summary>
    private static object? CarriedOutRow(CarriedOutPlan said) =>
        new Dictionary<string, object?>
        {
            ["card"] = said.Card,
            ["number"] = said.Number,
            ["line"] = said.Line,
        };

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
        // `EB-317`. WHAT THE JELLYFISH HAS ALREADY DONE THIS TURN, in the
        // order it did it, and in the WORDS IT SAID: `line` is the very string
        // the speech bubble carried, so `understudy/blindplay.render` prints
        // the screen's text rather than recomposing it. `card` and `number`
        // ride alongside because a reader that wants the parts should not have
        // to parse the sentence back apart; `number` is null for a Plan whose
        // clauses produced none.
        //
        // PRESENT AND EMPTY ON A TURN WITH NO CARRY-OUT, which is the same
        // three-state discipline the whole snapshot takes: the key is here
        // because the rule is here, and its emptiness is a fact.
        snapshot["carried_out"] =
            CarriedOut(player).Select(CarriedOutRow).ToList();
        return snapshot;
    }

    /// <summary>
    /// Keep the pending-Plans badge AND the strip in step with the queue.
    ///
    /// ONE FUNNEL, called from every site that moves the queue, which is what
    /// makes the badge, the strip and the list that will resolve the same three
    /// views of one number by construction -- the arrangement
    /// `KurageMemory.RefreshStrip` already makes for the memory arm.
    ///
    /// AND THE METER LEDGER RIDES IT (`EB-273`), for that same reason and no
    /// other: a note written anywhere but the one funnel could be skipped by a
    /// future site that moved the queue and only refreshed the badge, and the
    /// ledger's whole claim is that its arithmetic and the number on screen
    /// cannot come from different reads. <c>SparkPower.Gain</c> makes the
    /// argument one file over.
    ///
    /// <paramref name="before"/> IS PASSED IN RATHER THAN READ HERE, and that
    /// is the difference from the Spark sites: by the time this runs the queue
    /// has already moved, and the badge's own amount is a display value the
    /// engine's modifier chain is entitled to have resized. Each caller knows
    /// the depth it started from exactly, so it hands it over.
    /// </summary>
    private static async Task Sync(
        PlayerChoiceContext choiceContext, Creature kokomi, string source,
        int before)
    {
        Vfx.KokomiPlanStrip.Refresh(kokomi);
        var count = Pending(kokomi.Player).Count;
        Diagnostics.MeterLedger.Note(
            Diagnostics.MeterLedger.Plan, source, count - before, before);
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
