using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ======================================================================
// THE CO-OP SET (review/records/coop-set-2026-09-25.md; [USER], 2026-09-25,
// "Co-op interaction, pick 3a"). Nine multiplayer-only cards, three per
// character, marked `CardMultiplayerConstraint.MultiplayerOnly` exactly as the
// base game marks Tank, Demonic Shield, Flanking and Sneaky, so a
// single-player run never offers one (`CardPoolModel.GetUnlockedCards` and
// `CardFactory.FilterForPlayerCount` drop the constraint upstream of every
// reward, shop and transform).
//
// QUARANTINED: this folder is Compile Remove'd from a release build, so only
// `proto_` rows on the prototype surface can name anything here.
//
// "ANOTHER PLAYER" IS THE BASE GAME'S `TargetType.AnyAlly` (Lift, Believe In
// You, Intercept): a living PLAYER on your side who is not you. "EACH OTHER
// PLAYER" takes no target and is <see cref="CoopSet.OtherPlayers"/>, which is
// Rally's and Huddle Up's own walk.
// ======================================================================

/// <summary>The co-op set's shared reads, stated once.</summary>
public static class CoopSet
{
    /// <summary>
    /// "EACH OTHER PLAYER": every living player creature on
    /// <paramref name="owner"/>'s side other than <paramref name="owner"/>.
    ///
    /// THE BASE GAME'S OWN WALK, word for word: <c>Rally</c> and
    /// <c>HuddleUp</c> read <c>CombatState.GetTeammatesOf(Owner.Creature)
    /// .Where(c =&gt; c != null &amp;&amp; c.IsAlive &amp;&amp; c.IsPlayer)</c>;
    /// this adds the one clause "other" needs. A pet is on the side and is not
    /// a player (<c>Creature.IsPlayer</c> is <c>Player != null</c>), so the
    /// Bake-Kurage and the Stage's performers are never counted. Empty in a
    /// one-seat fight, which is the whole of why a single-player run could not
    /// use these cards even if one were offered.
    /// </summary>
    public static IReadOnlyList<Creature> OtherPlayers(Creature? owner)
    {
        if (owner?.CombatState is not { } combat)
        {
            return System.Array.Empty<Creature>();
        }
        return combat.GetTeammatesOf(owner)
            .Where(c => c != null && c != owner && c.IsAlive && c.IsPlayer)
            .ToList();
    }

    /// <summary>
    /// JOINT ORDERS' "THEY": the player a Plan written by
    /// <paramref name="kokomi"/> is for, fixed when the Plan is written.
    ///
    /// THE PLAN BRANCH IS PLAYED ON THE BAKE-KURAGE, not on a player (the
    /// arm's rule 2: a Plan line is what the card does when it is played on
    /// the jellyfish INSTEAD of where it would normally go), so the play
    /// itself names no player. With ONE other living player -- a two-seat
    /// run, the case the design was written for -- "they" is that player and
    /// nothing is chosen. With more, the base game's own answer for an ally
    /// card that reached play with no target is taken: a roll on the shared
    /// <c>CombatTargets</c> stream over the other living players
    /// (<c>CardCmd.AutoPlay</c>'s <c>TargetType.AnyAlly</c> branch), which
    /// every seat computes identically. Null with nobody else alive.
    /// </summary>
    public static Creature? PlanAlly(Creature? kokomi)
    {
        var others = OtherPlayers(kokomi);
        if (others.Count == 0) return null;
        if (others.Count == 1) return others[0];
        var rng = kokomi?.Player?.RunState?.Rng?.CombatTargets;
        return rng != null ? rng.NextItem(others) : others[0];
    }

    /// <summary>The player a Joint Orders Plan captured, found again on the
    /// live board at carry-out, or null when they are dead or gone -- "If
    /// that player is dead when the Plan is carried out, the Plan does
    /// nothing."</summary>
    public static Creature? PlanAllyFor(Creature? kokomi,
                                        KokomiPlan.Planned plan)
    {
        if (plan.Targets is not { Count: > 0 } ids) return null;
        return OtherPlayers(kokomi)
            .FirstOrDefault(c => ids.Contains(c.CombatId.ToString()));
    }

    /// <summary>
    /// Is <paramref name="play"/> an Attack played by a player who is not
    /// <paramref name="owner"/>? The trigger of Knights of Favonius and The
    /// People of Fontaine, and the base game's own <c>SneakyPower</c> test:
    /// <c>cardPlay.Card.Owner.Creature != base.Owner &amp;&amp; Type ==
    /// Attack</c>. A played Attack is a CARD play, so a Plan carry-out, a
    /// performer's act and a Bomb going off are none of them.
    /// </summary>
    public static bool IsAnotherPlayersAttack(CardPlay? play, Creature? owner)
    {
        if (owner == null || play?.Card is not { Type: CardType.Attack } card)
        {
            return false;
        }
        return card.Owner?.Creature is { IsPlayer: true } who && who != owner;
    }

    /// <summary>
    /// "IT SETS OFF YOUR BOMBS ON EACH ENEMY IT HITS": every enemy in
    /// <paramref name="hit"/> still alive has <paramref name="klee"/>'s Bombs
    /// set off, one enemy at a time, in the order the Attack hit them.
    ///
    /// THE BOMBS ARE KLEE'S (the design's own words), so this is
    /// <see cref="ProtoBombPower.SetOff"/> with HER as the applier -- her
    /// pile only (R205), her Sparks, her jumps, her Mine readers, her ledger
    /// and The Big One's armed multiplier, exactly as if she had set them off.
    /// And it is NOT a Set off CARD: no card source is handed down, so Once
    /// More!'s note, Boom Badge's doubling and every other reader of "a Set
    /// off card you played" never see it -- the three card-facing entry points
    /// take those, and this is not one of them.
    ///
    /// A BODY THE ATTACK KILLED IS SKIPPED, and nothing is lost by it: a dead
    /// enemy's charges are already owed a jump (rule 3), and
    /// <see cref="ProtoBombPower.SweepJumps"/> lands them on a survivor.
    /// </summary>
    public static async Task<int> SetOffOn(
        PlayerChoiceContext choiceContext, IReadOnlyList<Creature> hit,
        Creature? klee)
    {
        if (klee == null || hit.Count == 0) return 0;
        var exploded = 0;
        foreach (var enemy in hit)
        {
            if (enemy.IsDead) continue;
            exploded += await ProtoBombPower.SetOff(
                choiceContext, enemy, klee, cardSource: null);
        }
        await ProtoBombPower.SweepJumps(choiceContext, klee.CombatState);
        return exploded;
    }

    /// <summary>
    /// WHICH ENEMIES ONE ATTACK HIT, recorded while it resolves.
    ///
    /// THE HOOK IS <c>AfterDamageReceived</c> with the play's own card as its
    /// <c>cardSource</c>, which catches every hit the Attack lands whatever
    /// pipeline it went through -- a base-game <c>DamageCmd.Attack</c>, a
    /// multi-hit, an all-enemies swing, or this mod's elemental funnel -- and
    /// a hit Block stopped in full is still a hit. Nothing else is counted: a
    /// Bomb going off, a Mine answering, a performer's act, a Plan carry-out
    /// and a thorns reply carry no card source, or another card's.
    ///
    /// THE SET OFF HAPPENS AFTER THE ATTACK'S HITS RESOLVE (the design's own
    /// words): the record is opened by <c>BeforeCardPlayed</c>, filled while
    /// the card resolves, and taken by <c>AfterCardPlayed</c>. Each enemy is
    /// named once, in the order it was first hit.
    /// </summary>
    public sealed class HitRecord
    {
        private readonly List<Creature> _hit = new();

        /// <summary>The Attack being watched, or null.</summary>
        public CardModel? Card { get; private set; }

        public IReadOnlyList<Creature> Hit => _hit;

        public void Begin(CardModel card)
        {
            Card = card;
            _hit.Clear();
        }

        public bool Watching(CardModel? card) =>
            Card != null && ReferenceEquals(Card, card);

        public void Note(Creature target, CardModel? cardSource)
        {
            if (!Watching(cardSource) || !target.IsEnemy) return;
            if (!_hit.Contains(target)) _hit.Add(target);
        }

        /// <summary>What was hit, emptied. The watch stays open.</summary>
        public List<Creature> Take()
        {
            var taken = _hit.ToList();
            _hit.Clear();
            return taken;
        }

        public void End()
        {
            Card = null;
            _hit.Clear();
        }
    }
}

// ---------------------------------------------------------------------------
// KLEE
// ---------------------------------------------------------------------------

/// <summary>
/// <i>Pass the Match</i>: "Choose another player. This turn, their next
/// Attack Sets off your Bombs on each enemy it hits." ON THE ALLY, placed by
/// Klee, so the ally sees what their next Attack does and the Bombs are the
/// applier's (<see cref="CoopSet.SetOffOn"/>).
///
/// ONE ATTACK PER STACK: the next Attack the ally plays takes a stack and sets
/// off after EACH of its plays (an Attack played twice is still that one
/// Attack), and the stack is spent when its series ends. Gone at the end of the
/// turn either way ("This turn"). Instanced per applier (R205's rule for a
/// pile): two Klees' matches are two powers, each setting off its own Bombs.
/// </summary>
public sealed class PassTheMatchPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Pass the Match"),
        ("description",
            "This turn, your next Attack [gold]Sets off[/gold] Klee's "
          + "[gold]Bombs[/gold] on each enemy it hits."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

    protected override object? InitInternalData() => new CoopSet.HitRecord();

    private CoopSet.HitRecord Record => GetInternalData<CoopSet.HitRecord>();

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (Owner == null || Amount <= 0) return Task.CompletedTask;
        if (cardPlay.Card is not { Type: CardType.Attack } card) return Task.CompletedTask;
        if (card.Owner?.Creature != Owner) return Task.CompletedTask;
        // The FIRST play of the next Attack opens the watch; a later play of
        // the same series keeps it open and starts a fresh record.
        if (cardPlay.PlayIndex == 0 || Record.Watching(card))
        {
            Record.Begin(card);
        }
        return Task.CompletedTask;
    }

    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        Record.Note(target, cardSource);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!Record.Watching(cardPlay.Card)) return;
        var hit = Record.Take();
        await CoopSet.SetOffOn(choiceContext, hit, Applier);
        if (!cardPlay.IsLastInSeries) return;
        Record.End();
        if (Amount <= 1) await PowerCmd.Remove(this);
        else await PowerCmd.Decrement(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// <i>Knights of Favonius</i>: "Whenever another player plays an Attack, it
/// Sets off your Bombs on each enemy it hits." On Klee. Each PLAY of another
/// player's Attack is watched on its own and sets off after it resolves -- the
/// base game's <c>SneakyPower</c> answers every play the same way. One copy is
/// the whole rule: a second would find the Bombs already gone.
/// </summary>
public sealed class KnightsOfFavoniusPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Knights of Favonius"),
        ("description",
            "Whenever another player plays an Attack, it [gold]Sets off[/gold] "
          + "your [gold]Bombs[/gold] on each enemy it hits."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    protected override object? InitInternalData() => new CoopSet.HitRecord();

    private CoopSet.HitRecord Record => GetInternalData<CoopSet.HitRecord>();

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled) return Task.CompletedTask;
        if (CoopSet.IsAnotherPlayersAttack(cardPlay, Owner))
        {
            Record.Begin(cardPlay.Card);
        }
        return Task.CompletedTask;
    }

    public override Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        Record.Note(target, cardSource);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!Record.Watching(cardPlay.Card)) return;
        var hit = Record.Take();
        Record.End();
        await CoopSet.SetOffOn(choiceContext, hit, Owner);
    }
}

// ---------------------------------------------------------------------------
// FURINA
// ---------------------------------------------------------------------------

/// <summary>
/// <i>Guest of Honor</i>: "Choose another player. Until your next turn,
/// attacks on them hit their Block, then your lead performer's Fanfare, then
/// them." ON THE ALLY, placed by Furina.
///
/// RULE 6, FOR THE ALLY, AND THE SAME RULE (<see cref="FurinaStage.AbsorbHit"/>).
/// <c>ModifyHpLostBeforeOsty</c> is handed what is left of a hit AFTER the
/// ally's Block -- <c>CreatureCmd.Damage</c> spends Block first -- so "their
/// Block, then the lead's Fanfare, then them" is this one call: the lead
/// takes what it can and the rest reaches the ally. A lead emptied by such a
/// hit leaves WITHOUT a Bow and the next performer steps forward, as any hit;
/// A Rapt Audience fires because an enemy hit the lead. The bodies catch up at
/// <c>AfterDamageReceived</c>, the flush Furina's own hits take.
///
/// THE MINE STILL FIRES FIRST. A Klee's Mine answers an enemy's attack on
/// ANY player in <c>BeforeDamageReceived</c>, which runs before Block; a
/// lethal Mine notes the pre-empted hit (<see cref="ProtoBombPower.Preempted"/>),
/// and this power then takes NOTHING off the lead for a hit that never
/// happened -- the Furina hook's own rule. A Mine that does not kill leaves
/// the hit to land, and it lands here, on the lead.
///
/// ATTACKS ONLY (the face's word): an unblockable or unpowered loss goes
/// straight to the ally. Gone at the start of the next player turn, or when
/// Furina dies.
/// </summary>
public sealed class GuestOfHonorPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Guest of Honor"),
        ("description",
            "Until Furina's next turn, hits on you land on your "
          + "[gold]Block[/gold], then her [gold]front performer[/gold]'s "
          + "[gold]Fanfare[/gold], then you."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

    /// <summary>
    /// The redirect, and the whole of it. PURE apart from the ledger move the
    /// Furina hook makes in the same slot (<c>FurinaResourceHooks
    /// .ModifyHpLostBeforeOsty</c>), which is the precedent this follows.
    /// </summary>
    public override decimal ModifyHpLostBeforeOsty(
        Creature target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!ReferenceEquals(target, Owner) || amount <= 0m) return amount;
        if (Applier is not { } furina || furina.IsDead) return amount;
        if (!FurinaStage.LiveFor(furina)) return amount;
        if ((props & ValueProp.Unblockable) != 0 || !props.IsPoweredAttack())
        {
            return amount;
        }
        // A hit a lethal Mine already answered is owed nothing -- not the
        // ally's HP (the Klee arm's sweep zeroes that) and not the lead's
        // Fanfare either.
        if (ProtoBombPower.Preempted.Covers(target, dealer)) return 0m;
        var incoming = (int)System.Math.Ceiling(amount);
        return FurinaStage.AbsorbHit(furina, incoming, dealer);
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!ReferenceEquals(target, Owner) || Applier == null) return;
        await FurinaStage.Flush(Applier);
    }

    public override async Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterDeath(
        PlayerChoiceContext choiceContext, Creature creature,
        bool wasRemovalPrevented, float deathAnimLength)
    {
        if (!wasRemovalPrevented && ReferenceEquals(creature, Applier))
        {
            await PowerCmd.Remove(this);
        }
    }
}

/// <summary>
/// <i>The People of Fontaine</i>: "Whenever another player plays an Attack,
/// Raise 1." On Furina. A bare Raise (<see cref="FurinaStage.Raise"/>): it
/// lands on the back performer, and on an empty stage a random performer
/// arrives holding it. The stack is the Raise, so the upgrade and a second
/// copy both add to it.
/// </summary>
public sealed class PeopleOfFontainePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The People of Fontaine"),
        ("description",
            "Whenever another player plays an Attack, your back performer "
          + "gains [blue]{Amount}[/blue] [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null || Amount <= 0) return;
        if (!FurinaStage.LiveFor(Owner)) return;
        if (!CoopSet.IsAnotherPlayersAttack(cardPlay, Owner)) return;
        await FurinaStage.Raise(Owner, (int)Amount);
    }
}

// ---------------------------------------------------------------------------
// KOKOMI
// ---------------------------------------------------------------------------

/// <summary>
/// <i>Sangonomiya's Counsel</i>: "Whenever the Bake-Kurage carries out a
/// Plan, each other player gains 3 Block." On Kokomi, on the Plan bus
/// (<see cref="IKokomiPlanListener"/>) Treatise and Song of Pearls ride --
/// EVERY Plan, not once a turn: the face says "Whenever" and prints no cap.
///
/// UNPOWERED, exactly the printed number: Block a power grants another
/// player on a trigger is the base game's <c>SneakyPower</c> shape, and a
/// <c>ValueProp.Move</c> grant with no card behind it would take the
/// RECEIVER's Dexterity rather than hers.
/// </summary>
public sealed class SangonomiyasCounselPower
    : PowerModel, ILocalizationProvider, IKokomiPlanListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sangonomiya's Counsel"),
        ("description",
            "Whenever the [gold]Bake-Kurage[/gold] carries out a "
          + "[gold]Plan[/gold], each other player gains [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnPlanResolved(
        PlayerChoiceContext choiceContext, Creature kokomi)
    {
        if (!ReferenceEquals(kokomi, Owner) || Amount <= 0) return;
        foreach (var ally in CoopSet.OtherPlayers(Owner))
        {
            await CreatureCmd.GainBlock(
                ally, Amount, ValueProp.Unpowered, null, fast: true);
        }
    }
}
