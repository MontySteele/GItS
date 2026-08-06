using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// The Curtain Call sweep's ACTIVITY-TRIGGERED powers (R85), ported to C# by
/// the "Take a Bow" consolidation sprint.
///
/// All six share one design law, stated in the sheet header and enforced by
/// their trigger sites rather than by any number here: they pay on an EVENT
/// the player caused, never on a per-turn tick. A turn that deploys nothing,
/// bows nobody, spends no Encore, plays no Attack and triggers no reaction
/// pays exactly zero. That is what makes them safe to leave uncapped -- the
/// player has to keep doing the thing.
///
/// Each one mirrors a named tier0 site; the sim is the reference implementation
/// and this file copies FROM it. The mirrors are:
///   salon_deploy_block  -> effects.py _deploy_salon_members (per deploy event)
///   salon_bow_block     -> effects.py _salon_bow
///   salon_bow_encore    -> effects.py _salon_bow
///   cross_examination   -> reactions.py resolve_hit (first reaction each turn)
///   encore_spend_draw   -> resources.py spend_encore (first spend each turn)
///   first_attack_draw   -> refpowers.py after_card_played (first Attack)
/// </summary>
public static class CurtainCallHooks
{
    // Per-turn windows, keyed by owner. The same static-dictionary shape
    // SalonMemberPower.Company uses, and stale entries are handled the same
    // way: everything here is cleared at the top of every player turn, so a
    // key that outlives its combat is overwritten before it can be read.
    private static readonly Dictionary<Creature, int> AttacksPlayed = new();
    private static readonly Dictionary<Creature, int> EncoreSpendDraws = new();
    private static readonly Dictionary<Creature, int> PendingDraws = new();
    private static readonly Dictionary<Creature, int> HpLost = new();
    // Fanfare rework Track C.3 (2026-07-28): Blocking Notes' slope.
    // Mirrors the sim's state.companion_plays_this_turn.
    private static readonly Dictionary<Creature, int> CompanionPlays = new();

    private static int Get(Dictionary<Creature, int> map, Creature creature) =>
        map.TryGetValue(creature, out var value) ? value : 0;

    private static int PowerAmount<T>(Creature creature) where T : PowerModel =>
        creature.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;

    /// <summary>
    /// Clear every per-turn window.
    ///
    /// Called from BeforeSideTurnStart(Player), NOT from AfterPlayerTurnStart.
    /// The sim zeroes these at the very top of the player turn (combat.py),
    /// strictly before Salon upkeep -- and Salon upkeep is itself an
    /// AfterPlayerTurnStart hook that SPENDS Encore. Resetting in the same
    /// broadcast as the thing that feeds the latch would make the Gallery
    /// Stirs draw depend on undefined intra-broadcast power ordering.
    /// BeforeSideTurnStart is a strictly earlier broadcast, so the ordering
    /// is guaranteed rather than assumed.
    /// </summary>
    public static void ResetTurn(Creature creature)
    {
        AttacksPlayed.Remove(creature);
        EncoreSpendDraws.Remove(creature);
        PendingDraws.Remove(creature);
        HpLost.Remove(creature);
        CompanionPlays.Remove(creature);
        Purge();
    }

    /// <summary>Record true HP loss for the Slip Backstage predicate. Called
    /// from AfterCurrentHpChanged, the same funnel that mints Fanfare from HP
    /// loss, so the two readings of "she got hurt" cannot disagree.</summary>
    public static void NoteHpLost(Creature creature, int amount)
    {
        if (amount <= 0) return;
        HpLost[creature] = Get(HpLost, creature) + amount;
    }

    /// <summary>tier0 predicate `hp_lost_this_turn`: has she taken any true HP
    /// damage this turn?</summary>
    public static bool HpLostThisTurn(Creature creature) =>
        Get(HpLost, creature) > 0;

    /// <summary>Blocking Notes' slope (Track C.3, 2026-07-28): how many
    /// Companion cards have been played this turn, Guest Star tokens
    /// included. Mirrors the sim's state.companion_plays_this_turn.</summary>
    public static int CompanionPlaysThisTurn(Creature creature) =>
        Get(CompanionPlays, creature);

    /// <summary>
    /// tier0 predicate `enemy_intends_attack`: is any living enemy telegraphing
    /// an attack?
    ///
    /// The sim spells this "intent kind is attack AND sleep_turns == 0". Only
    /// the first clause needs writing here: nothing in the game SETS sleep --
    /// it is an enemy-spec field -- and an enemy that is skipping its turn
    /// telegraphs a SleepIntent rather than an AttackIntent, so it fails the
    /// intent test on its own. IsStunned is checked too, being the host's own
    /// "this creature will not act" flag.
    /// </summary>
    public static bool EnemyIntendsAttack(Creature owner)
    {
        var enemies = owner.CombatState?.HittableEnemies;
        if (enemies == null) return false;
        return enemies.Any(enemy =>
            enemy.Monster != null
            && !enemy.IsStunned
            && enemy.Monster.NextMove.Intents.Any(
                intent => intent.IntentType == IntentType.Attack));
    }

    /// <summary>Drop keys whose combat is gone, so these maps cannot grow
    /// across a run. Cheap: they hold one entry per player, not per card.
    ///
    /// EVERY map above must be listed here, in both halves. CompanionPlays was
    /// added to the class (Track C.3) and to <see cref="ResetTurn"/> but not
    /// to this sweep, and it is the one map a NON-Furina player can key:
    /// <see cref="NoteCardPlayed"/> records any owner's Companion play, while
    /// ResetTurn is only ever called for Furina (FurinaResourceHooks'
    /// BeforeSideTurnStart). A co-op partner's key therefore had no clearing
    /// path at all. Fixed 2026-07-29.</summary>
    private static void Purge()
    {
        foreach (var stale in AttacksPlayed.Keys
                     .Concat(EncoreSpendDraws.Keys)
                     .Concat(PendingDraws.Keys)
                     .Concat(HpLost.Keys)
                     .Concat(CompanionPlays.Keys)
                     .Where(creature => creature.CombatState == null)
                     .Distinct()
                     .ToList())
        {
            AttacksPlayed.Remove(stale);
            EncoreSpendDraws.Remove(stale);
            PendingDraws.Remove(stale);
            HpLost.Remove(stale);
            CompanionPlays.Remove(stale);
        }
    }

    /// <summary>
    /// The Gallery Stirs, spend half. Mirrors resources.py spend_encore: the
    /// FIRST spend event each turn draws, and only the first.
    ///
    /// The draw itself is DEFERRED rather than done here, because SpendEncore
    /// is synchronous and holds no PlayerChoiceContext -- it is called from
    /// BeforeCardPlayed (cost settle) and from Salon upkeep. The same deferral
    /// SpotlightSystem already uses for its first-play draw, for the same
    /// reason. <see cref="FlushPendingDraws"/> is called from every async
    /// Furina hook that follows a spend, so a pending draw cannot strand
    /// inside the turn that earned it.
    /// </summary>
    public static void NoteEncoreSpent(Creature creature)
    {
        var draw = PowerAmount<EncoreSpendDrawPower>(creature);
        if (draw <= 0) return;
        if (Get(EncoreSpendDraws, creature) != 0) return;
        EncoreSpendDraws[creature] = 1;
        PendingDraws[creature] = Get(PendingDraws, creature) + draw;
    }

    /// <summary>Resolve any draw a spend deferred. Idempotent: the counter is
    /// taken and cleared, so extra calls are free.</summary>
    public static async Task FlushPendingDraws(
        PlayerChoiceContext choiceContext, Creature creature)
    {
        var pending = Get(PendingDraws, creature);
        if (pending <= 0) return;
        PendingDraws.Remove(creature);
        if (creature.Player is not { } player) return;
        await CardPileCmd.Draw(choiceContext, pending, player);
    }

    /// <summary>
    /// Quick Change. Mirrors refpowers.py after_card_played: the first Attack
    /// PLAY of the turn draws. Counted per play, not per series -- a doubled
    /// Attack is two plays and only the first of the turn pays, which is the
    /// same index rule Juggling uses in the sim.
    /// </summary>
    public static async Task NoteCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null) return;

        // Blocking Notes' slope (Track C.3, 2026-07-28). Counted here rather
        // than in a Companion-specific hook so it shares the sim's site: the
        // sim increments in combat._finish_play, which is the same "a card
        // resolved" moment this method is. Guest Star TOKEN plays count --
        // they are Companion cards and this is a payoff, not a discount.
        //
        // IsFirstInSeries is NOT tested, deliberately, and this differs from
        // the floor grant's once-per-series rule: a Study Buddy'd Companion
        // really is two Companion cards hitting the table, and the tempo
        // payoff is about how busy the turn was.
        if (cardPlay.Card is ICompanionCard)
        {
            CompanionPlays[owner] = Get(CompanionPlays, owner) + 1;
        }

        if (cardPlay.Card!.Type != CardType.Attack) return;

        var played = Get(AttacksPlayed, owner) + 1;
        AttacksPlayed[owner] = played;
        if (played != 1) return;

        var draw = PowerAmount<FirstAttackDrawPower>(owner);
        if (draw <= 0) return;
        if (owner.Player is not { } player) return;
        await CardPileCmd.Draw(choiceContext, draw, player);
    }

    /// <summary>
    /// The `refresh_all_auras` op (Torrential Turn). Mirrors effects.py
    /// _op_refresh_all_auras: every LIVING enemy holding an aura has its
    /// remaining duration set back to full.
    ///
    /// Reuses AuraPower's own same-element refresh path -- PowerCmd.ModifyAmount
    /// by the difference up to AuraCmd.Duration -- so the number an aura
    /// refreshes TO is defined in exactly one place, and any relic or power
    /// that extends aura duration is honoured here for free.
    /// </summary>
    public static async Task RefreshAllAuras(
        PlayerChoiceContext choiceContext, Creature owner, CardModel? cardSource)
    {
        var enemies = owner.CombatState?.HittableEnemies.ToList();
        if (enemies == null) return;
        foreach (var aura in enemies
                     .SelectMany(enemy => enemy.Powers.OfType<AuraPower>())
                     .ToList())
        {
            var full = AuraCmd.Duration(owner);
            if (aura.Amount >= full) continue;
            await PowerCmd.ModifyAmount(
                choiceContext, aura, full - aura.Amount,
                applier: owner, cardSource: cardSource, silent: true);
        }
    }

    /// <summary>
    /// Courtroom Drama. Mirrors reactions.py resolve_hit: the FIRST reaction
    /// each turn puts its target on the stand for Vulnerable + Weak per stack.
    ///
    /// Read off the DEALER, not off some global "the player". ReactionEffects'
    /// own counters are deliberately global (red-pen R1: a Reaction is a fact
    /// about the shared board), but a POWER is owned by a creature, so the
    /// question "does Courtroom Drama fire" can only be asked of whoever
    /// actually caused the reaction. In solo -- the only configuration the sim
    /// models -- the dealer IS the player, so this is byte-for-byte the sim's
    /// read; in co-op it means your partner's reaction does not spend your
    /// once-per-turn window, which is the Best Friends Forever lesson.
    /// </summary>
    public static async Task NoteFirstReaction(
        PlayerChoiceContext choiceContext, Creature target, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer == null) return;
        var amount = PowerAmount<CrossExaminationPower>(dealer);
        if (amount <= 0) return;

        await PowerCmd.Apply<VulnerablePower>(
            choiceContext, target, amount, applier: dealer,
            cardSource: cardSource);
        await PowerCmd.Apply<WeakPower>(
            choiceContext, target, amount, applier: dealer,
            cardSource: cardSource);
    }
}

/// <summary>Fortissimo Guard: Block per DEPLOY EVENT, so Full Ensemble's three
/// deploys are three cues. Deliberately NOT Fanfare/Grand-Salon scaled -- the
/// printed number is the whole payout, matching the sim, where this add sits
/// outside _salon_amount.</summary>
public sealed class SalonDeployBlockPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fortissimo Guard"),
        ("description",
            "Whenever you deploy a [gold]Salon Member[/gold], gain "
          + "{Amount} Block."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonDeployBlockPower>()
            .FirstOrDefault()?.Amount ?? 0;
}

/// <summary>Stagehands, Block half: the crew strikes the set behind every
/// bow. Unscaled for the same reason as <see cref="SalonDeployBlockPower"/>.</summary>
public sealed class SalonBowBlockPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stagehands"),
        ("description",
            "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
          + "{Amount} Block."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonBowBlockPower>()
            .FirstOrDefault()?.Amount ?? 0;
}

/// <summary>Stagehands, Encore half. Its own power because the sim keeps its
/// own power key, and because the card's upgrade binds to the FIRST
/// apply_power only -- one var, one effect (the reward-screen softlock rule).</summary>
public sealed class SalonBowEncorePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stagehands (Encore)"),
        ("description",
            "Whenever a [gold]Salon Member[/gold] takes its final bow, gain "
          + "{Amount} Encore."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonBowEncorePower>()
            .FirstOrDefault()?.Amount ?? 0;
}

/// <summary>Courtroom Drama: the first reaction each turn applies Vulnerable
/// and Weak to its target. Activity-gated on the reaction, so a silent turn
/// pays nothing and a reaction storm pays once.</summary>
public sealed class CrossExaminationPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Courtroom Drama"),
        ("description",
            "The first [gold]Elemental Reaction[/gold] you trigger each turn "
          + "applies {Amount} [gold]Vulnerable[/gold] and {Amount} "
          + "[gold]Weak[/gold] to its target."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>The Gallery Stirs: the first Encore spend each turn draws. Once
/// per turn rather than per event, so it cannot be looped into a draw engine
/// the way a per-spend rate could.</summary>
public sealed class EncoreSpendDrawPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "The Gallery Stirs"),
        ("description",
            "The first time you spend Encore each turn, draw "
          + "{Amount} card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>Quick Change: the first Attack you play each turn draws.</summary>
public sealed class FirstAttackDrawPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Quick Change"),
        ("description",
            "The first Attack you play each turn draws "
          + "{Amount} card{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}
