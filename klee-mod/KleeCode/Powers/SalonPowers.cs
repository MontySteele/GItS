using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>Salon v2 member identities (rework plan §1 — the Defect-orb
/// grammar; mirrors tier0 constants.SALON_MEMBERS).</summary>
public enum SalonMember
{
    Crabaletta,
    Usher,
    Chevalmarin,
}

public static class SalonConstants
{
    public const int MemberSlots = 3;

    // Fanfare is the Focus analogue: +1 to member NUMERIC amounts per this
    // much held Fanfare, read live at resolution (rework plan §1).
    public const int FocusPerFanfare = 10;

    public const int ReplacementNumericMultiplier = 2;
    public const int ReplacementDamageMultiplier = 3;
    public const int TickEncoreCost = 1;
    public const decimal DryDamageMultiplier = 0.75m;

    // Member tick / bow numbers — RATIFIED 2026-08-13 (R187, QUEUE M24);
    // the sim's C.SALON_MEMBERS table is the source of truth and the parity
    // lint compares all six by value. These carried "PROPOSED pending
    // red-pen" from the 2026-07-23 rework until the countersign; no value
    // moved when the banner came off, so no world stamp moved either. The
    // derivation signed against is
    // review/ruled/eb77-salon-summon-damage-derivation.md, and the sim-side
    // half of this banner is tier0/constants.py above SALON_MEMBERS.
    public const int CrabalettaTick = 6;
    public const int CrabalettaBow = 14;
    public const int UsherTick = 3;
    public const int UsherBow = 9;
    public const int ChevalmarinTick = 2;
    public const int ChevalmarinBowEncore = 3;
}

/// <summary>
/// Furina's fixed three-slot Salon, v2 (rework 2026-07-23): the company is
/// a TYPED FIFO queue. Each member performs its unique slot passive at the
/// start of the player's turn (Crabaletta hits, Usher blocks, Chevalmarin
/// applies); deploying into a full stage bows the OLDEST member out — its
/// unique payoff — and the new member takes the vacated slot. Fanfare acts
/// as Focus: +1 to member numerics per 10 held.
/// </summary>
public sealed class SalonMemberPower : PowerModel, ILocalizationProvider
{
    // The typed company per owner. The counter power (Amount) mirrors the
    // queue length so every count read stays valid; this dictionary is the
    // member-identity half the counter cannot carry. A list outliving its
    // combat is dropped by <see cref="CompanyFor"/>, which asks the COMBAT
    // and not the counter -- see the banner there.
    private static readonly Dictionary<Creature, List<SalonMember>> Company =
        new();

    /// <summary>
    /// Which combat each live company list was built in. `EB-384`: this is the
    /// question the stale-list check has to ask, and asking the counter
    /// instead is what cost the round-two seat a member.
    /// </summary>
    private static readonly Dictionary<Creature, object?> CompanyCombat =
        new();

    public List<(string, string)>? Localization
    {
        get
        {
            var rows = ShippedLocalization();
            return rows;
        }
    }

    private static List<(string, string)> ShippedLocalization() => new()
    {
        ("title", "Salon Member"),
        // Numbers come from SalonConstants (SalonMemberTips.BodyFor's rule,
        // applied here): a repricing must not leave the power telling the
        // player a retired number, and lint_constant_parity cannot see prose.
        ("description",
            "At the start of your turn, each [gold]Salon Member[/gold] "
          + $"spends {SalonConstants.TickEncoreCost} Encore for its act: "
          + $"Crabaletta deals {SalonConstants.CrabalettaTick} Hydro damage, "
          + $"the Usher gains {SalonConstants.UsherTick} Block, Chevalmarin "
          + $"deals {SalonConstants.ChevalmarinTick} Hydro damage. "
          + "Dry members act at three-quarters. Member numbers gain +1 per "
          + $"{SalonConstants.FocusPerFanfare} [gold]Fanfare[/gold]. Maximum "
          + $"{SalonConstants.MemberSlots}; a full stage bows its "
          + $"OLDEST member out: Crabaletta deals {SalonConstants.CrabalettaBow}, "
          + $"the Usher gains {SalonConstants.UsherBow} "
          + "Block, Chevalmarin applies Hydro to ALL enemies and grants "
          + $"{SalonConstants.ChevalmarinBowEncore} Encore."),
        // The in-combat tooltip reads the LIVE cap. A12 (2026-07-28) made the
        // cap a per-player stat (SlotsFor: base plus Casting Call, which takes
        // it to 5), and until 2026-07-29 both tooltips said a flat "Maximum 3"
        // -- so a player who had paid for the bigger stage was told, by the
        // power itself, that the card they bought did nothing. The plain
        // description above still prints the BASE, because it renders with no
        // instance and therefore no owner to ask.
        // {Slots} is a DynamicVar token resolved by the localizer, not a C#
        // interpolation -- its fragment stays a plain literal.
        ("smartDescription",
            "At the start of your turn, each [gold]Salon Member[/gold] "
          + $"spends {SalonConstants.TickEncoreCost} Encore for its act: "
          + $"Crabaletta deals {SalonConstants.CrabalettaTick} Hydro damage, "
          + $"the Usher gains {SalonConstants.UsherTick} Block, Chevalmarin "
          + $"deals {SalonConstants.ChevalmarinTick} Hydro damage. "
          + "Dry members act at three-quarters. Member numbers gain +1 per "
          + $"{SalonConstants.FocusPerFanfare} [gold]Fanfare[/gold]. Maximum "
          + "{Slots}; a full stage bows its "
          + $"OLDEST member out: Crabaletta deals {SalonConstants.CrabalettaBow}, "
          + $"the Usher gains {SalonConstants.UsherBow} "
          + "Block, Chevalmarin applies Hydro to ALL enemies and grants "
          + $"{SalonConstants.ChevalmarinBowEncore} Encore."),
    };


    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>{Slots} in the smart tooltip. Kept in sync by
    /// <see cref="SyncSlotsDisplay"/>; the base value is the printed cap so a
    /// tooltip read before any sync still shows a true number.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new[] { new DynamicVar("Slots", SalonConstants.MemberSlots) };

    /// <summary>
    /// Push this player's live cap into {Slots}. Called from every site that
    /// already refreshes the salon surface -- <see cref="Deploy"/>,
    /// <see cref="BowLeftmost"/> and FurinaResources.SyncMeters (which runs
    /// after every card play, so Casting Call's raise is visible the instant
    /// it resolves). No-op for anyone without the power.
    /// </summary>
    public static void SyncSlotsDisplay(Creature owner)
    {
        var power = owner.Powers.OfType<SalonMemberPower>().FirstOrDefault();
        if (power == null) return;
        var slots = power.DynamicVars["Slots"];
        slots.BaseValue = SlotsFor(owner);
        slots.ResetToBase();
    }

    public static int Count(Creature creature) =>
        creature.Powers.OfType<SalonMemberPower>().FirstOrDefault()?.Amount ?? 0;

    /// <summary>
    /// The company in SLOT ORDER, for the visual layer only (animation sprint
    /// 2, Funnel Contract §1: the stage is slot-index-keyed and duplicates are
    /// legal, so the UI must read per-slot identity from state rather than
    /// assume a fixed member-to-slot mapping). Read-only by construction — a
    /// copy, so a display can never mutate the company.
    /// </summary>
    public static IReadOnlyList<SalonMember> CompanyOf(Creature owner) =>
        CompanyFor(owner).ToList();

    /// <summary>
    /// This owner's live company, dropping a list left over from an earlier
    /// combat.
    ///
    /// `EB-384`. THE STALENESS TEST IS THE COMBAT, NOT THE COUNTER, and the
    /// difference cost the round-two seat a member on a card that prints one.
    ///
    /// It used to read "a nonempty list with a zero counter is garbage",
    /// which is true BETWEEN combats and false for one window inside every
    /// deploy: <see cref="Deploy"/> adds the entering member to this list and
    /// applies the mirror counter AFTER the loop, so from the `company.Add`
    /// to the `PowerCmd.Apply` the stage legitimately holds a member the
    /// counter has never heard of. Nothing read the list inside that window
    /// until the arm's deploy-performs clause put <see cref="PerformMember"/>
    /// there -- and a member that can PAY its Encore reaches
    /// `FurinaResources.SpendEncore`, which refreshes the stage visuals, which
    /// read <see cref="CompanyOf"/>, which came back through here and wiped
    /// the company it had just been handed.
    ///
    /// That is the seat's whole finding, and it explains BOTH of its halves.
    /// Fight 1 the deploy went in at 0 Encore, so the member acted dry, no
    /// spend ran, no refresh ran, and the member stayed -- dealing 1, the
    /// three-quarters cut of a printed 2. Fight 2 it went in on a banked
    /// Encore, paid, dealt the full 2, and vanished. The reaction the record
    /// noticed was a coincidence of the same two turns.
    ///
    /// The combat identity answers the real question directly and cannot fire
    /// mid-deploy, because a deploy does not change combats. It is the same
    /// token `ProtoBombPower` keys its per-combat tables on.
    /// </summary>
    private static List<SalonMember> CompanyFor(Creature owner)
    {
        var combat = (object?)owner.CombatState;
        if (!Company.TryGetValue(owner, out var list))
        {
            list = new List<SalonMember>();
            Company[owner] = list;
        }
        else if (CompanyCombat.TryGetValue(owner, out var built)
                 && !ReferenceEquals(built, combat))
        {
            // A list built in a combat that is over. The Creature key can
            // outlive one (PurgeCompany sweeps only the keys whose combat has
            // already been torn down), so this is still the check that keeps a
            // dead stage out of a live fight.
            list.Clear();
        }
        CompanyCombat[owner] = combat;
        return list;
    }

    /// <summary>
    /// Drop keys whose combat is gone. The line-106 clear only empties a LIST
    /// -- the Creature key and its List object both survive, so a long run
    /// left one dead entry per combat behind forever (and every dead entry
    /// pins a whole combat's Creature). Same cheap sweep as
    /// <c>FurinaResources.PurgeDeltaBlock</c> and
    /// <see cref="CurtainCallHooks.Purge"/>, wired to the same lifecycle site
    /// those use: the top-of-player-turn reset in
    /// <c>FurinaResourceHooks.BeforeSideTurnStart</c>. Added 2026-07-29.
    /// </summary>
    public static void PurgeCompany()
    {
        foreach (var stale in Company.Keys
                     .Where(creature => creature.CombatState == null)
                     .ToList())
        {
            Company.Remove(stale);
            // `EB-384`: the sidecar leaves with the entry it describes. A
            // combat token outliving its list is the same leak one dictionary
            // over, and a stale token would answer the staleness question with
            // a lie the next time this Creature turned up.
            CompanyCombat.Remove(stale);
        }
    }

    /// <param name="focusMult">The Furina reframe's <c>F6</c> (1) shape, and
    /// it is 1 on every shipped path: an Evoke applies the SAME Focus term N
    /// times, so there is one divisor and one number on screen and a face can
    /// print "x N". The multiplier lands on the Focus term ALONE and never on
    /// the printed base -- that is what makes it "much stronger Fanfare
    /// scaling" rather than a bigger card. Mirrors tier0
    /// <c>effects._salon_amount</c>'s parameter of the same name, including
    /// the structural half of the prospective scaling invariant (packet §3.1
    /// amendment 4, countersigned PROSPECTIVE by R224): this method is reached
    /// only from a member's damage and Block, so Chevalmarin's Encore refund
    /// and an aura's stack count have no path to the Focus term, multiplied or
    /// not.</param>
    private static int Scaled(Creature owner, int baseAmount, int focusMult = 1) =>
        baseAmount
        + FurinaResources.ReadableFanfare(owner)
            / SalonConstants.FocusPerFanfare * focusMult
        + SalonDamageUpPower.AmountFor(owner);

    /// <summary>The member's PRINTED per-turn tick, before any scaling.</summary>
    public static int BaseTick(SalonMember member) => member switch
    {
        SalonMember.Crabaletta => SalonConstants.CrabalettaTick,
        SalonMember.Usher => SalonConstants.UsherTick,
        _ => SalonConstants.ChevalmarinTick,
    };

    /// <summary>
    /// What this member's tick is worth RIGHT NOW: the printed number plus
    /// the Fanfare Focus term and Grand Salon, then the dry reduction if the
    /// member cannot pay.
    ///
    /// D1's role chip renders this, and the upkeep loop resolves through it,
    /// so the number under a member and the number it deals are the same
    /// expression rather than two copies that agree until one is edited. A
    /// chip that computed its own scaling would be a fourth hand-maintained
    /// projection of the same arithmetic.
    /// </summary>
    public static int TickValue(Creature owner, SalonMember member, bool paid) =>
        Dry(Scaled(owner, BaseTick(member)), paid);

    /// <summary>
    /// THE DRY CUT, in ONE place (`EB-587`). A member that cannot pay its
    /// Encore acts at <see cref="SalonConstants.DryDamageMultiplier"/>, and
    /// since the Evoke pays like a performance there are now two callers of
    /// that arithmetic -- <see cref="TickValue"/> and <see cref="Bow"/> --
    /// which is one caller too many for a repeated cast. Mirrors tier0
    /// <c>effects._salon_dry</c>.
    /// </summary>
    private static int Dry(int amount, bool paid) =>
        paid ? amount : (int)(amount * SalonConstants.DryDamageMultiplier);

    /// <summary>
    /// THE BODIES A MEMBER'S ROLL MAY PICK -- every hittable enemy, SKIPPING A
    /// MINION while a non-Minion stands (`EB-451`).
    ///
    /// THE DEFECT. Furina r7 fight 7: the run's ONE paid performance -- every
    /// other member in every other fight had performed dry -- rolled the 6-HP
    /// Eye with Teeth, whose own status line says it revives at full. The rule
    /// was printed and the outcome still handed the Encore economy's payoff to
    /// the roll at the moment it was worth most.
    ///
    /// THE SAME SHAPE AS THE PLAN'S AIM, deliberately, and R250 is why: it
    /// ruled that a Plan aims a non-Minion unless it is aimed, over the same
    /// evidence (a decoy absorbing the one hit that mattered), and a member's
    /// roll is the same question with a different roller.
    /// <see cref="Prototype.KokomiPlan.FrontEnemy"/> is the twin, down to the
    /// fallback: when the board is Minions ALONE the whole list comes back,
    /// because a performance that lands on nothing is worse than one that
    /// lands on the decoy.
    ///
    /// <c>MinionPower</c> IS THE MARK, the base game's own "secondary enemy"
    /// flag, so this reads it rather than inventing a second one -- the Kin's
    /// Followers and Queen's Torch Head Amalgam already carry it.
    ///
    /// NOT ARM-SCOPED. <see cref="PerformMember"/> and <see cref="Bow"/> are
    /// the shipped kit's roll as well as the reframe's, and a rule that says
    /// "the roll does not throw your payoff at a decoy" is not a fork of the
    /// reframe's engine. Sim twin: <c>effects.salon_aim_pool</c>.
    /// </summary>
    public static List<Creature>? AimPool(IEnumerable<Creature>? hittable)
    {
        var all = hittable?.ToList();
        if (all == null || all.Count == 0) return all;
        var standing = all.Where(IsNotMinion).ToList();
        return standing.Count > 0 ? standing : all;
    }

    /// <summary>Named rather than inline so the Minion read is one call a
    /// structural pin can see directly -- `KokomiPlan.IsNotMinion`'s reason,
    /// and the same predicate.</summary>
    private static bool IsNotMinion(Creature enemy) =>
        !enemy.Powers.OfType<MinionPower>().Any();

    private static async Task Bow(
        PlayerChoiceContext choiceContext, Creature owner, SalonMember member)
    {
        const int mult = 1;
        switch (member)
        {
            case SalonMember.Crabaletta:
            {
                var targets = AimPool(owner.CombatState?.HittableEnemies);
                if (targets == null || targets.Count == 0) break;
                var target = owner.Player?.RunState.Rng.CombatTargets
                    .NextItem(targets);
                if (target == null) break;
                // THE NUMBER THAT LANDED and not the one the bow was worth,
                // `EB-511`'s rule one method over: `Deal` runs the dealer's
                // Weak, the reaction amplifier and the target's Vulnerable,
                // and it is the landed figure a seat reconciles HP against.
                await ElementalHit.Deal(
                    choiceContext, target, Elements.Element.Hydro,
                    Scaled(owner, SalonConstants.CrabalettaBow, mult),
                    owner);
                break;
            }
            case SalonMember.Usher:
                await CreatureCmd.GainBlock(
                    owner, Scaled(owner, SalonConstants.UsherBow, mult),
                    ValueProp.Unpowered, null, fast: true);
                break;
            case SalonMember.Chevalmarin:
            {
                var targets = owner.CombatState?.HittableEnemies.ToList();
                if (targets != null)
                {
                    foreach (var enemy in targets)
                    {
                        await ElementalHit.ApplyOnly(
                            choiceContext, enemy, Elements.Element.Hydro,
                            owner);
                    }
                }
                FurinaResources.GainEncore(
                    owner, SalonConstants.ChevalmarinBowEncore);
                break;
            }
        }
        FurinaResources.GainBurst(
            owner, FurinaResourceConstants.BurstPerSalonTick);

        // Stagehands (R85): the crew strikes the set behind every bow. Placed
        // after the burst credit to match the sim's _salon_bow ordering, and
        // unscaled -- the printed number is the whole payout.
        var bowBlock = SalonBowBlockPower.AmountFor(owner);
        if (bowBlock > 0)
        {
            await CreatureCmd.GainBlock(
                owner, bowBlock, ValueProp.Unpowered, null, fast: true);
        }
        var bowEncore = SalonBowEncorePower.AmountFor(owner);
        if (bowEncore > 0)
        {
            FurinaResources.GainEncore(owner, bowEncore);
        }
    }

    /// <summary>The replacement rule, in ONE place: a deploy that lands on a
    /// full stage bows the oldest member out. Both the loop in
    /// <see cref="Deploy"/> and the card face (via <see cref="WillReplace"/>)
    /// ask the question through here, so they cannot drift apart.</summary>
    /// <remarks>A12 (2026-07-28) promoted the cap from a constant to a
    /// per-player stat, so every reader must ask with an OWNER. The old
    /// count-only overload is deliberately gone rather than kept as a
    /// convenience: a caller that forgot to pass the owner would silently
    /// enforce the base cap of 3 on a player who had paid for 4, and that
    /// reads as "the card did nothing" -- the hardest kind of bug to see.
    /// SalonConstants.MemberSlots remains the BASE, which is what the
    /// constant-parity gate compares against tier0.</remarks>
    public static bool StageIsFull(Creature owner, int companyCount) =>
        companyCount >= SlotsFor(owner);

    /// <summary>The stage's size for this player: the base cap plus whatever
    /// cap-raise powers they hold.</summary>
    public static int SlotsFor(Creature owner) =>
        SalonConstants.MemberSlots + SalonCapUpPower.AmountFor(owner);

    /// <summary>Closed form of <see cref="Deploy"/>'s loop, for the card face:
    /// will any of a card's first <paramref name="deploys"/> deploys displace
    /// someone? Iteration i of that loop sees a company of
    /// <c>min(Count + i, MemberSlots)</c> -- each pass either grows the queue
    /// by one or replaces into a full one -- so <see cref="StageIsFull"/>
    /// first turns true at <c>i = MemberSlots - Count</c> and stays true.
    /// Testing the LAST iteration therefore answers for all of them; no
    /// simulation is needed. Reads pre-play state only, which is exactly the
    /// state the card's own resolution starts from -- hence card bodies
    /// capture their scaled value BEFORE the first Deploy runs.</summary>
    public static bool WillReplace(Creature owner, int deploys) =>
        deploys > 0 && StageIsFull(owner, Count(owner) + deploys - 1);

    /// <summary>Face/resolution delta for a number the replacement rule
    /// scales: the CalculatedVar computes <c>base + 1 x delta</c>, and this
    /// returns <c>base x (multiplier - 1)</c> when a bow is coming, so the
    /// result is <c>base x multiplier</c> -- the same number these cards
    /// already resolved, now also the number they print. Reading the base
    /// live off CalculationBase keeps it upgrade-safe.</summary>
    public static decimal ReplacementDelta(
        CardModel card, int deploys, int multiplier)
    {
        var owner = card.Owner?.Creature;
        if (owner == null) return 0m;
        var printed = card.DynamicVars.CalculationBase.BaseValue;
        return WillReplace(owner, deploys) ? printed * (multiplier - 1) : 0m;
    }

    /// <summary>Salon v2 deploy: into a full stage, the OLDEST member bows
    /// out and the new member enters. Returns the replacement count (the
    /// generated card bodies scale their later numerics off it).</summary>
    /// <summary>A11: one random member, drawn from the SHARED combat stream
    /// so both seats in a co-op run agree on who walked on.</summary>
    private static readonly SalonMember[] AllMembers =
    {
        SalonMember.Crabaletta, SalonMember.Usher, SalonMember.Chevalmarin,
    };

    private static SalonMember RollMember(Creature owner)
    {
        var rng = owner.Player?.RunState.Rng.CombatTargets;
        return rng == null ? SalonMember.Crabaletta : rng.NextItem(AllMembers);
    }

    /// <param name="member">Who takes the stage, or NULL for a random member
    /// (A11, 2026-07-28: the starter fields whoever turns up, so it no longer
    /// duplicates the Chevalmarin card). Rolled per deploy rather than once
    /// per card, so a multi-deploy card can field a mixed stage -- the sim
    /// rolls per iteration too.</param>
    /// <param name="cardSource">The card that deployed, or NULL where no card
    /// did. `EB-553` (R260) opened that second case: under the reframe the arm
    /// itself fields the opening member at combat start, and the mirror
    /// <c>PowerCmd.Apply</c> below has taken a null source since
    /// <see cref="BowLeftmost"/> was written.</param>
    public static async Task<int> Deploy(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        CardModel? cardSource, SalonMember? member)
    {
        var company = CompanyFor(owner);
        var replacements = 0;
        for (var i = 0; i < amount; i++)
        {
            // Drawn INSIDE the loop and from the shared combat stream, not
            // from a local Random. Co-op runs lockstep: a draw one seat makes
            // and the other does not poisons every later draw on that stream,
            // which is exactly how Vigil of the Deep desynced. If there is no
            // player to own a stream there is no run to desync either, so the
            // fallback is fixed rather than randomised.
            var entering = member ?? RollMember(owner);
            if (StageIsFull(owner, company.Count))
            {
                var displaced = company[0];
                company.RemoveAt(0);
                replacements++;
                await Bow(choiceContext, owner, displaced);
            }
            company.Add(entering);

            // Fortissimo Guard (R85): Block per DEPLOY, inside the loop, so a
            // three-deploy card pays three cues. Mirrors the sim, which adds
            // it per iteration after the member enters.
            var deployBlock = SalonDeployBlockPower.AmountFor(owner);
            if (deployBlock > 0)
            {
                await CreatureCmd.GainBlock(
                    owner, deployBlock, ValueProp.Unpowered, null, fast: true);
            }
        }

        var delta = company.Count - Count(owner);
        if (delta > 0)
        {
            await PowerCmd.Apply<SalonMemberPower>(
                choiceContext, owner, delta, applier: owner,
                cardSource: cardSource);
        }
        SyncSlotsDisplay(owner);
        Vfx.SalonVisualsBridge.Refresh(owner);
        return replacements;
    }

    /// <summary>
    /// The on-demand bow (Fanfare rework Track D, 2026-07-28), mirroring the
    /// sim's `salon_bow` op. The LEFTMOST members take their bows.
    ///
    /// Leftmost is deliberately the same end of the FIFO queue that
    /// <see cref="Deploy"/> displaces when the stage is full, so the card
    /// teaches the player no new targeting rule -- it reuses the one the
    /// deploy rule already taught. The company mutation here is byte-for-byte
    /// the displacement branch above (RemoveAt(0), then Bow), which is why
    /// this is a sibling method rather than its own notion of "which member".
    ///
    /// Inert on an empty stage, silently: a bow with no company is a no-op
    /// and not an error, matching the sim's `if not p.salon: break`.
    /// </summary>
    /// <param name="aim">The Furina reframe's AIMED EVOKE (the slot-6 ruling,
    /// 2026-08-30): the member the card NAMES. <c>null</c> -- which is what
    /// every shipped row passes, because none of them names one -- is the
    /// FRONT, so every row written before the ruling means exactly what it
    /// always meant. The aim is the EVOKE leg's to give: with the leg off it is
    /// ignored and this verb pops the front, which is the shipped bow. Mirrors
    /// the <c>member:</c> ARGUMENT tier0 put on the shipped <c>salon_bow</c>
    /// verb rather than on a new op.</param>
    public static async Task BowLeftmost(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        SalonMember? aim = null)
    {
        if (!FurinaResources.IsFurina(owner)) return;
        var company = CompanyFor(owner);
        for (var i = 0; i < amount && company.Count > 0; i++)
        {
            // The aim, or the front when the card names nobody -- and the
            // front again when it names a member who is not on the stage: an
            // aimed card that cannot find its member is an unaimed bow, never
            // a wasted one. Mirrors tier0 `effects._op_salon_bow`.
            var index = aim is { } who ? company.IndexOf(who) : 0;
            if (index < 0) index = 0;
            var leaving = company[index];
            company.RemoveAt(index);
            await Bow(choiceContext, owner, leaving);
        }

        // Negative delta: the mirror of Deploy's positive one. The
        // SalonMemberPower counter is a MIRROR of the company list, so it
        // follows the list rather than the list following it.
        var delta = company.Count - Count(owner);
        if (delta < 0)
        {
            await PowerCmd.Apply<SalonMemberPower>(
                choiceContext, owner, delta, applier: owner,
                cardSource: null);
        }
        SyncSlotsDisplay(owner);
        Vfx.SalonVisualsBridge.Refresh(owner);
    }

    /// <summary>
    /// ONE member's slot passive, with the full standard bill: the Encore
    /// upkeep, the dry three-quarters when it goes unpaid, the Focus/Grand
    /// Salon scaling (through <see cref="TickValue"/>) and the burst particle.
    ///
    /// THE ONLY implementation of a member acting.
    /// <see cref="AfterPlayerTurnStart"/> runs it once per member at the start
    /// of the player turn; <see cref="PerformLeftmost"/> runs it on demand for
    /// the leftmost member (EB-118 §5.5). A second copy of this body is the
    /// defect the shape exists to make impossible -- a card that performs a
    /// member must not be able to drift from the upkeep that performs the same
    /// member. Mirrors tier0 effects.salon_member_act.
    /// </summary>
    /// <returns>False when the stage cannot act at all (the owner is dead, or
    /// there is no hittable enemy left) -- the caller's break condition, kept
    /// here so the on-demand verb inherits it rather than restating it.
    /// </returns>
    /// <param name="free">`EB-558` (R260's arithmetic): THE ONE PERFORMANCE
    /// NOBODY BUYS -- the relic's opening arrival. It performs PAID (full
    /// value, not the dry three-quarters) and spends nothing, which is
    /// [USER]'s own analogy for the pick, "one free Osty". A PARAMETER here
    /// rather than a branch at the fielding site, for this method's standing
    /// reason: a member performing has ONE implementation, and a caller that
    /// wanted a free one by writing its own body would be exactly the drift
    /// the shape exists to prevent. Mirrors tier0 `salon_member_act`'s
    /// `free=`. The two decisions it moves are split out into
    /// <see cref="PerformancePays"/> and <see cref="PerformanceSpends"/>
    /// because this method resolves through `ElementalHit` and is outside the
    /// headless boundary, while "does this performance pay, and does it spend"
    /// is a pure read the pins can ask for real.</param>
    /// <summary>
    /// `EB-558`. Does this performance land at FULL value? True when the owner
    /// can afford the upkeep, and true unconditionally for the relic's free
    /// arrival -- which is the half of "one free Osty" that is about the
    /// number rather than about the price.
    /// </summary>
    public static bool PerformancePays(Creature owner, bool free) =>
        free
        || FurinaResources.Encore(owner) >= SalonConstants.TickEncoreCost;

    /// <summary>
    /// `EB-558`. Does this performance take the Encore? The other half, and
    /// the one the arithmetic turned on: a free arrival pays full value and
    /// spends nothing, so R258's opening bank is still whole when the player
    /// makes their first decision.
    /// </summary>
    public static bool PerformanceSpends(Creature owner, bool free) =>
        !free && PerformancePays(owner, free);

    public static async Task<bool> PerformMember(
        PlayerChoiceContext choiceContext, Creature owner, SalonMember member,
        bool free = false)
    {
        if (owner.IsDead) return false;
        var combat = owner.CombatState;
        // `EB-451`: the roll's pool, not the raw board. `AimPool` never empties
        // a board that had a body on it, so this is still the "can the stage
        // act at all" test it has always been.
        var targets = AimPool(combat?.HittableEnemies);
        if (targets == null || targets.Count == 0) return false;

        var paid = PerformancePays(owner, free);
        if (PerformanceSpends(owner, free))
        {
            FurinaResources.SpendEncore(owner, SalonConstants.TickEncoreCost);
        }

        // The SAME expression D1's role chip renders -- see TickValue.
        var amount = TickValue(owner, member, paid);

        // `EB-405`. The two facts the page had no way to print are decided
        // inside this switch and thrown away by it: WHICH body the member
        // picked, and WHAT that body is wearing afterwards. They are carried
        // out of the branches in these locals and filed once below, so there
        // is one recording site for the one implementation of a member acting.
        Creature? picked = null;
        Elements.Element? left = null;
        // `EB-511`. THE NUMBER THAT LANDED, not the number the tick was worth
        // before the pipeline touched it. Seeded with the tick so the Usher's
        // Block branch -- which has no pipeline -- files what it always filed.
        //
        // THE DEFECT. Furina r11 fight 3 turn 2 and fight 4 turn 6: the page's
        // Salon block reported a member's act at `TickValue`, which is read
        // BEFORE `ElementalHit.Deal` runs the reaction amplifier and the
        // target's Vulnerable. A Vaporizing Crabaletta logged at 4 landed for
        // 6 -- so a seat reconciling the fight's HP against the block
        // concluded that a reaction amplifier had been dropped by the CARD it
        // had just played (Chevreuse printed 7, previewed Vaporize 1.5x, and
        // was blamed for the 8 the arithmetic left over). Nothing was dropped
        // and the log was the only thing lying. `Deal` has RETURNED the
        // truncated landed amount since `EB-270`, for this exact reason.
        // (The Weak half of that finding is gone since `EB-588` below: the
        // dealer's terms no longer enter a performance at all.)
        var landed = amount;
        switch (member)
        {
            case SalonMember.Crabaletta:
            case SalonMember.Chevalmarin:
            {
                var target = combat!.RunState.Rng.CombatTargets
                    .NextItem(targets);
                if (target == null) break;
                // `EB-588`. `powered: false` -- THE DEALER'S TERMS DO NOT
                // ENTER A PERFORMANCE. THE FIND (Furina r15 lane 2 (c) 4):
                // Weak cut a member performance from 6 to 4 twice, while the
                // Salon paragraph directly above it says "a performance is not
                // an Attack and not a hit: Vulnerable moves it" and names no
                // Weak. The paragraph is the rule and the pipeline was the
                // defect: the hit already reaches `CreatureCmd.Damage` as
                // `ValueProp.Unpowered` with `dealer: null`, and the mirror
                // above it was still running `SimDamagePipeline.DealerMods`.
                //
                // ONE FLAG, so it takes STRENGTH with the Weak, and that is
                // the flag's stated meaning rather than a second decision:
                // `ElementalHit.Deal`'s own doc calls `powered: false` "the
                // dealer's Strength and Weak, and with them every flat attack
                // buff the mirror carries", and a second parameter meaning
                // "half of Unpowered" is exactly what that doc refuses. What
                // a member's number IS remains the member's own -- the printed
                // base, the Fanfare Focus term and Grand Salon -- which is
                // what `TickValue` and the Salon paragraph both say it is.
                // Mirrors tier0 `salon_member_act`'s `powered=False`.
                landed = await ElementalHit.Deal(
                    choiceContext, target, Elements.Element.Hydro,
                    amount, owner, powered: false);
                picked = target;
                // THE AURA IS READ AFTER THE HIT, not assumed from the element
                // supplied: `ElementalHit.Deal` applies Hydro to a bare body,
                // REFRESHES a Hydro one, and on any other element CONSUMES the
                // aura into a reaction and leaves the body bare. All three are
                // "what it left", and only the board knows which happened.
                left = AuraCmd.Find(target)?.Element;
                break;
            }
            case SalonMember.Usher:
                await CreatureCmd.GainBlock(
                    owner, amount, ValueProp.Unpowered, null, fast: true);
                break;
        }
        FurinaResources.GainBurst(
            owner, FurinaResourceConstants.BurstPerSalonTick);
        return true;
    }

    /// <summary>
    /// The leftmost member performs NOW (EB-118 §5.5): an extra slot passive,
    /// off-turn, at the standard price. Resolves through
    /// <see cref="PerformMember"/> -- the same method the turn-start upkeep
    /// calls -- so the upkeep, the dry reduction, the scaling and the particle
    /// are inherited rather than restated.
    ///
    /// The member STAYS on stage: this is a performance, not a bow and not a
    /// rotation, so the company and its mirror counter are untouched.
    /// <paramref name="amount"/> is therefore N acts by whoever is leftmost;
    /// pair it with <see cref="RotateLeftmost"/> to spread them.
    ///
    /// Inert on an empty stage, matching the sim's `salon_perform`.
    /// </summary>
    /// <param name="aim">Who performs, or NULL for the FRONT (`EB-493`). The
    /// aimed performance is an ARGUMENT on the shipped verb and not a second
    /// op, exactly as the aimed Evoke is on <see cref="BowLeftmost"/> and for
    /// the same reason: `tools/lint_op_parity.py` compares the KEY SET of the
    /// sim's op registry against the drafter's priced-op table, so an extra
    /// argument leaves the priced set identical while a `salon_perform_member`
    /// synonym would have bought a `DRAFTER_VERSION` stamp for a verb both
    /// engines already have.
    ///
    /// NOT FLAG-GATED, and that is the one place it differs from the Evoke's
    /// aim. The Evoke's is gated because a SHIPPED row could in principle name
    /// a member and must not become aimable in a release world; no shipped row
    /// carries `member:` on `salon_perform`, and the only row that does is a
    /// quarantined prototype that cannot be compiled into a release build at
    /// all. The gate is the field, not a switch.
    ///
    /// A NAMED MEMBER WHO IS NOT ON STAGE takes the FRONT, which is the ruled
    /// fallback the aimed Evoke already has (slot 6, 2026-08-30: "an aimed
    /// card that cannot find its member is an unaimed Evoke, never a wasted
    /// one"), and it is noted rather than silent for that verb's D4 reason.
    /// The one row that aims -- <i>Second Course</i> -- deploys her in the
    /// sentence before, so the state is unreachable from the sheet as it
    /// stands; the fallback is written down so it cannot be discovered later.
    /// Mirrors tier0 `effects._op_salon_perform`.</param>
    public static async Task PerformLeftmost(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        SalonMember? aim = null)
    {
        if (!FurinaResources.IsFurina(owner)) return;
        var company = CompanyFor(owner);
        var aimed = aim;
        if (aimed is { } named && !company.Contains(named))
        {
            aimed = null;
        }
        for (var i = 0; i < amount && company.Count > 0; i++)
        {
            // `aimed ?? company[0]` re-reads the front INSIDE the loop, so an
            // unaimed call is byte-identical to what this verb has always
            // done. A performance moves nobody, so the two readings agree
            // today -- the shape is kept because the loop's invariant is
            // "whoever is leftmost NOW", not "whoever was leftmost first".
            if (!await PerformMember(choiceContext, owner, aimed ?? company[0]))
            {
                break;
            }
        }
    }

    /// <summary>
    /// Rotate the leftmost member to the BACK of the queue (EB-118 §5.5).
    ///
    /// A pure reorder: the member keeps its identity, performs NO tick, drains
    /// NO Encore and triggers NO bow or replacement effect. It buys exactly
    /// one thing -- which performer the FIFO end offers next, to
    /// <see cref="BowLeftmost"/>, to a <see cref="Deploy"/> landing on a full
    /// stage, and to <see cref="LeftmostMember"/>.
    ///
    /// Synchronous, and no counter apply: nothing here is awaited and the
    /// queue's LENGTH cannot change, so the SalonMemberPower mirror is already
    /// correct. Only the visual layer, which is slot-index-keyed, has to be
    /// told (animation sprint 2, Funnel Contract §1).
    /// </summary>
    public static void RotateLeftmost(Creature owner, int amount)
    {
        if (!FurinaResources.IsFurina(owner)) return;
        var company = CompanyFor(owner);
        if (company.Count == 0) return;
        for (var i = 0; i < amount; i++)
        {
            var moving = company[0];
            company.RemoveAt(0);
            company.Add(moving);
        }
        Vfx.SalonVisualsBridge.Refresh(owner);
    }

    /// <summary>Who is NEXT to perform: the head of the FIFO queue -- the same
    /// end <see cref="BowLeftmost"/> pops, <see cref="PerformLeftmost"/> acts
    /// on and a full-stage <see cref="Deploy"/> displaces. Null on an empty
    /// stage. The read half of EB-118 §5.5, and the mirror of tier0's
    /// `leftmost_salon_member_<name>` predicate; the counter power carries the
    /// count and cannot carry identity, so this reads the company.</summary>
    public static SalonMember? LeftmostMember(Creature owner)
    {
        var company = CompanyFor(owner);
        return company.Count == 0 ? null : company[0];
    }

    /// <summary>What the NEXT performer's act is worth right now, at the price
    /// the stage can currently pay: the reward half of the leftmost read, and
    /// the mirror of tier0's `leftmost_salon_act` runtime count. 0 on an empty
    /// stage. Resolves through <see cref="TickValue"/>, the same expression
    /// <see cref="PerformMember"/> pays out.</summary>
    public static int LeftmostActValue(Creature owner)
    {
        var member = LeftmostMember(owner);
        if (member == null) return 0;
        var paid = FurinaResources.Encore(owner)
                   >= SalonConstants.TickEncoreCost;
        return TickValue(owner, member.Value, paid);
    }

#if PROTOTYPE_CARDS
    /// <summary>
    /// A card's printed title for a LEDGER row, and the id when it has none.
    ///
    /// `PlayTelemetry`'s `card.Title ?? card.Id.Entry` for the same question,
    /// plus the guard that idiom leaves to its caller: `CardModel.Title`
    /// resolves through `LocString.GetFormattedText`, which throws on a model
    /// whose loc table has not been built -- and this is reached from
    /// `AfterCardPlayed`, inside `CombatManager`'s async continuation, where a
    /// throw reaches the player as a black screen rather than an error
    /// (`KleeElementalHooks.BeforeCardPlayed` guards its own hook for exactly
    /// that reason). A record of what happened must never be able to end the
    /// run it is recording, so the id is the fallback for both cases.
    /// </summary>
    private static string PrintedTitle(CardModel card)
    {
        try
        {
            return card.Title ?? card.Id.Entry;
        }
        catch (System.Exception)
        {
            return card.Id.Entry;
        }
    }
#endif

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        foreach (var member in CompanyFor(Owner).ToList())
        {
            if (!await PerformMember(choiceContext, Owner, member)) break;
        }
    }

    /// <summary>
    /// The stage cannot hold more members than it has slots, and cannot hold
    /// fewer than none. Expressed as a clamp on the RESULTING COUNTER rather
    /// than on the delta, which is the bug this shape replaced (2026-07-29):
    /// <c>Math.Max(0m, Math.Min(amount, SlotsFor - Amount))</c> zeroed every
    /// NEGATIVE delta, so <see cref="BowLeftmost"/>'s (always-negative) mirror
    /// apply never landed. The company list shrank, the counter did not, and
    /// the badge, the stage and every per-member payer (Dinner Service, House
    /// Call) kept counting members who had already bowed out -- for the rest
    /// of the combat.
    /// </summary>
    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not SalonMemberPower || target != Owner)
        {
            return false;
        }
        var clamped = Math.Max(0m, Math.Min(Amount + amount, SlotsFor(target)));
        modifiedAmount = clamped - Amount;
        return modifiedAmount != amount;
    }
}

/// <summary>Grand Salon, v2 semantics: +N to every member NUMERIC tick and
/// bow amount (Block included), stacking with the Fanfare Focus term.
///
/// The six-point (two-stack) cap was dropped 2026-07-24 (uncap-all ruling):
/// +3/copy is a flat additive to member ticks, linear in copies, so uncapping
/// lets dupes stack like any base-StS Power. See <see cref="SpotlightPower"/>
/// for the A/B behind the whole uncap.</summary>
public sealed class SalonDamageUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Salon"),
        ("description",
            "[gold]Salon Member[/gold] numbers are {Amount} higher."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonDamageUpPower>().FirstOrDefault()?.Amount ?? 0;
}

/// <summary>A12 (ruled 2026-07-28): +N stage slots. The Salon's size was a
/// constant from the day it was built; this is the card that makes it a stat.
///
/// PRE-REGISTERED, from the ruling: the mild anti-synergy with bow payoffs is
/// INTENDED (a fuller stage bows less often, so cards that want bows want a
/// SMALLER salon). That is Capacitor's bargain in StS, and if playtesting
/// reads it as a trap rather than a choice, this note is the pre-registered
/// reason to revisit rather than a post-hoc rationalisation.</summary>
public sealed class SalonCapUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Casting Call"),
        ("description",
            "Your [gold]Salon[/gold] has room for [blue]{Amount}[/blue] more "
          + "[gold]{Amount:plural:Salon Member|Salon Members}[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonCapUpPower>().FirstOrDefault()?.Amount ?? 0;
}
