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
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
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
// KOKOMI
// ---------------------------------------------------------------------------

/// <summary>
/// <i>Sangonomiya's Counsel</i>: "Whenever the Bake-Kurage carries out a
/// Plan, each other player gains 3 Block." On Kokomi, on the Plan bus
/// (<see cref="IKokomiPlanListener"/>) her Ancient under the arm rides --
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

// ======================================================================
// THE CO-OP SET, SECOND BATCH (review/active/coop-concepts-2026-09-27.md;
// [USER], 2026-09-27, all four picks at their defaults). Each character's
// Genshin team role: Furina turns her stage into an ally's damage and is
// charged by the party's HP swings; Klee's Mines shred for her allies and her
// Bombs give them energy. Same terms as the first nine above: multiplayer
// only, outside every pool count, quarantined with this folder.
// ======================================================================

// ---------------------------------------------------------------------------
// KLEE
// ---------------------------------------------------------------------------

/// <summary>
/// <i>Shrapnel</i>: "Place a Mine 4. While an enemy holds your Mine, other
/// players' Attacks deal 50% more damage to it." ON THE ENEMY the Mine went
/// on, placed by Klee.
///
/// THE BASE GAME'S <c>FlankingPower</c>, WITH ONE MORE CONDITION. Flanking's
/// three tests, verbatim: the hit is on this power's owner, it is a powered
/// attack (<c>props.IsPoweredAttack()</c>), and its dealer is not the applier
/// -- so Klee's own hits, and her Bombs going off, never take it. The fourth is
/// the face's "while an enemy holds your Mine": the enemy must hold a Mine
/// Klee placed (<see cref="ProtoBombPower.HoldsMineFrom"/>), read LIVE at the
/// hit, so the shred ends the moment her last Mine there leaves, whatever
/// took it. MULTIPLICATIVE, x1.5, where Flanking is x2.
///
/// ONE SHRED PER KLEE, NOT PER CARD. The face ties the shred to "your Mine",
/// and a second Shrapnel on the same enemy adds to the Mine there rather than
/// making a second shred, so it is <see cref="PowerStackType.Single"/> and
/// <see cref="PowerInstanceType.InstancedPerApplier"/>: two Klees' Mines are
/// two shreds, one Klee's two Shrapnels are one. (Flanking is Instanced, and
/// two of them stack to x4; that is a Flanking rule and not this card's.)
///
/// THE BADGE LEAVES WITH THE MINE: when one of her Mines goes off here and
/// she holds none on this enemy after it, <see cref="AfterMineWentOff"/>
/// removes the power, so the enemy does not wear a shred that no longer
/// applies. A Mine set off by an ally's Attack (Pass the Match, Knights of
/// Favonius) goes off AFTER that Attack's hits resolve
/// (<see cref="CoopSet.SetOffOn"/> runs at <c>AfterCardPlayed</c>), so that
/// Attack is still shredded.
/// </summary>
public sealed class ShrapnelPower : PowerModel, ILocalizationProvider
{
    /// <summary>The printed 50% more.</summary>
    public const decimal Shred = 1.5m;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Shrapnel"),
        ("description",
            "While this enemy holds Klee's [gold]Mine[/gold], other players' "
          + "Attacks deal 50% more damage to it."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Single;

    public override PowerInstanceType InstanceType =>
        PowerInstanceType.InstancedPerApplier;

    /// <summary>The multiplier a hit takes. PURE, so a headless pin can ask
    /// it.</summary>
    public override decimal ModifyDamageMultiplicative(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (target == null || target != Owner) return 1m;
        if (!props.IsPoweredAttack()) return 1m;
        if (Applier is not { } klee || dealer == klee) return 1m;
        if (!ProtoBombPower.HoldsMineFrom(target, klee)) return 1m;
        return Shred;
    }

    /// <summary>One of <paramref name="applier"/>'s Mines just went off on
    /// <paramref name="target"/>: if she holds no Mine there any more, her
    /// shred on it is removed.</summary>
    public static async Task AfterMineWentOff(
        PlayerChoiceContext choiceContext, Creature applier, Creature target)
    {
        if (ProtoBombPower.HoldsMineFrom(target, applier)) return;
        foreach (var shred in target.Powers.OfType<ShrapnelPower>().ToList())
        {
            if (shred.Applier == applier) await PowerCmd.Remove(shred);
        }
    }
}

/// <summary>
/// <i>Sparks for Everyone</i>: "The first time each turn one of your Bombs
/// goes off, each other player gains 1 energy." On Klee, on the explosion bus
/// (<see cref="IProtoExplosionListener"/>) Chained Reactions rides, so every
/// Bomb counts however it went off: a Set off card, an ally's Attack through
/// Pass the Match or Knights of Favonius, or a Mine answering an attack (a
/// Mine is a Bomb).
///
/// ONLY ON THE PLAYERS' TURN (designer ruling, 2026-09-27): a Bomb that goes
/// off while the enemies act -- a Mine answering an attack -- gives nothing
/// and does NOT use up the turn's trigger, so the next explosion on the
/// players' turn still pays (<see cref="Counts"/>).
///
/// ONCE PER TURN, on the ledger's latch
/// (<see cref="KleeOverhaulLedger.TakeSparksForEveryone"/>, Aftershock's
/// shape), and only for HER Bombs. "Each other player" is
/// <see cref="CoopSet.OtherPlayers"/>, the living players who are not her; the
/// energy is Believe In You's command, <c>PlayerCmd.GainEnergy</c>. The stack
/// is the energy, so a second copy gives 2.
/// </summary>
public sealed class SparksForEveryonePower
    : PowerModel, ILocalizationProvider, IProtoExplosionListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks for Everyone"),
        ("description",
            "The first time each turn one of your [gold]Bombs[/gold] goes off, "
          + "each other player gains [blue]{Amount}[/blue] [gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does this explosion count? PURE: one of HER Bombs, on the
    /// players' turn. Asked before the latch, so an explosion that does not
    /// count never spends it.</summary>
    public static bool Counts(Creature? owner, Creature? applier) =>
        owner != null && applier == owner
        && owner.CombatState?.CurrentSide == CombatSide.Player;

    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (Owner == null || Amount <= 0 || !Counts(Owner, applier)) return;
        var others = CoopSet.OtherPlayers(Owner);
        if (others.Count == 0) return;
        if (!KleeOverhaulLedger.For(Owner).TakeSparksForEveryone()) return;
        foreach (var ally in others)
        {
            if (ally.Player is { } player)
            {
                await PlayerCmd.GainEnergy((int)Amount, player);
            }
        }
    }
}

