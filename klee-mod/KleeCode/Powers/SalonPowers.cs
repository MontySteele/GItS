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
using MegaCrit.Sts2.Core.Models;
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

    // Member tick / bow numbers — PROPOSED pending red-pen; the sim's
    // C.SALON_MEMBERS table is the source of truth.
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
    // member-identity half the counter cannot carry. Entries are reset on
    // the first deploy of a combat (queue outliving the power is harmless:
    // a fresh combat's first Deploy clears a stale list).
    private static readonly Dictionary<Creature, List<SalonMember>> Company =
        new();

    public List<(string, string)>? Localization => new()
    {
        ("title", "Salon Member"),
        ("description",
            "At the start of your turn, each [gold]Salon Member[/gold] "
          + "spends 1 Encore for its act: Crabaletta deals 6 Hydro damage, "
          + "the Usher gains 3 Block, Chevalmarin deals 2 Hydro damage. "
          + "Dry members act at three-quarters. Member numbers gain +1 per "
          + "10 [gold]Fanfare[/gold]. Maximum 3; a full stage bows its "
          + "OLDEST member out: Crabaletta deals 14, the Usher gains 9 "
          + "Block, Chevalmarin applies Hydro to ALL enemies and grants "
          + "3 Encore."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

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

    private static List<SalonMember> CompanyFor(Creature owner)
    {
        if (!Company.TryGetValue(owner, out var list))
        {
            list = new List<SalonMember>();
            Company[owner] = list;
        }
        // Stale list from a previous combat: the counter power died with
        // that combat, so a nonempty list with a zero counter is garbage.
        if (Count(owner) == 0 && list.Count > 0) list.Clear();
        return list;
    }

    private static int Scaled(Creature owner, int baseAmount) =>
        baseAmount
        + FurinaResources.ReadableFanfare(owner) / SalonConstants.FocusPerFanfare
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
    public static int TickValue(Creature owner, SalonMember member, bool paid)
    {
        var amt = Scaled(owner, BaseTick(member));
        return paid ? amt : (int)(amt * SalonConstants.DryDamageMultiplier);
    }

    private static async Task Bow(
        PlayerChoiceContext choiceContext, Creature owner, SalonMember member)
    {
        switch (member)
        {
            case SalonMember.Crabaletta:
            {
                var targets = owner.CombatState?.HittableEnemies.ToList();
                if (targets == null || targets.Count == 0) break;
                var target = owner.Player?.RunState.Rng.CombatTargets
                    .NextItem(targets);
                if (target == null) break;
                await ElementalHit.Deal(
                    choiceContext, target, Elements.Element.Hydro,
                    Scaled(owner, SalonConstants.CrabalettaBow), owner);
                break;
            }
            case SalonMember.Usher:
                await CreatureCmd.GainBlock(
                    owner, Scaled(owner, SalonConstants.UsherBow),
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
    public static async Task<int> Deploy(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        CardModel cardSource, SalonMember? member)
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
    public static async Task BowLeftmost(
        PlayerChoiceContext choiceContext, Creature owner, int amount)
    {
        if (!FurinaResources.IsFurina(owner)) return;
        var company = CompanyFor(owner);
        for (var i = 0; i < amount && company.Count > 0; i++)
        {
            var leaving = company[0];
            company.RemoveAt(0);
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
        Vfx.SalonVisualsBridge.Refresh(owner);
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        foreach (var member in CompanyFor(Owner).ToList())
        {
            if (Owner.IsDead) break;
            var targets = CombatState?.HittableEnemies.ToList();
            if (targets == null || targets.Count == 0) break;

            var paid = FurinaResources.Encore(Owner)
                       >= SalonConstants.TickEncoreCost;
            if (paid)
            {
                FurinaResources.SpendEncore(
                    Owner, SalonConstants.TickEncoreCost);
            }

            // The SAME expression D1's role chip renders -- see TickValue.
            var amount = TickValue(Owner, member, paid);

            switch (member)
            {
                case SalonMember.Crabaletta:
                case SalonMember.Chevalmarin:
                {
                    var target = CombatState!.RunState.Rng.CombatTargets
                        .NextItem(targets);
                    if (target == null) break;
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        amount, Owner);
                    break;
                }
                case SalonMember.Usher:
                    await CreatureCmd.GainBlock(
                        Owner, amount, ValueProp.Unpowered, null, fast: true);
                    break;
            }
            FurinaResources.GainBurst(
                Owner, FurinaResourceConstants.BurstPerSalonTick);
        }
    }

    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not SalonMemberPower || target != Owner)
        {
            return false;
        }
        modifiedAmount = Math.Max(
            0m, Math.Min(amount, SlotsFor(target) - Amount));
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
            "Your [gold]Salon[/gold] has room for {Amount} more "
          + "[gold]Salon Member(s)[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonCapUpPower>().FirstOrDefault()?.Amount ?? 0;
}
