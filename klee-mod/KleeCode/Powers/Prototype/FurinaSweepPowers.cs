using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ======================================================================
// FURINA, THE SWEEP, SECOND SET (review/active/furina-sweep-2026-10-14.md
// sec.3, ruled 2026-10-14): the rules her fifteen new cards need that the
// sheet's grammar cannot spell. Sim twin: `tier0/engine/furina_stage.py`
// (the sweep's section) and the hooks it names.
// ======================================================================

/// <summary>
/// Ousia / Pneuma's two faces. A card starts on Ousia; <see cref="Turn"/>
/// turns it over. The face lives beside the card instance, never on the deck
/// card, so every combat (whose cards are fresh clones of the deck's) starts
/// on Ousia. Sim twin: <c>Card.flipped</c>.
/// </summary>
public static class FurinaFlip
{
    public const string FirstFace = "Ousia";
    public const string SecondFace = "Pneuma";

    private static readonly ConditionalWeakTable<CardModel, object> Flipped = new();

    /// <summary>Is this card on its Pneuma face?</summary>
    public static bool OnPneuma(CardModel card) =>
        Flipped.TryGetValue(card, out _);

    /// <summary>Turn the card to its other face.</summary>
    public static void Turn(CardModel card)
    {
        if (!Flipped.Remove(card)) Flipped.Add(card, new object());
    }

    /// <summary>The face's name in combat; the row's two-faced name (and its
    /// "+") everywhere else.</summary>
    public static string TitleOf(CardModel card, string baseTitle)
    {
        var inCombat = card.Pile?.IsCombatPile ?? false;
        if (!inCombat) return baseTitle;
        var face = OnPneuma(card) ? SecondFace : FirstFace;
        return card.IsUpgraded ? face + "+" : face;
    }
}

/// <summary>
/// The sweep's per-player reads, for ANY player (fed from
/// <see cref="FurinaSweepHooks"/>): HP lost this combat (Facade), HP lost
/// last turn (Tearful Monologue: the round before this one, which is the
/// player's last turn and the enemies' turn after it), the first turn of
/// combat (Opening Number), and Stage Directions' card that costs 0 next
/// turn. Any HP loss counts, a Drain included. Sim twins:
/// <c>state.hp_lost_this_combat</c>, <c>state.hp_lost_last_turn</c>,
/// <c>state.turn == 1</c>, <c>Card.free_next_turn</c>.
/// </summary>
public static class FurinaSweep
{
    private static readonly Dictionary<Creature, int> CombatLoss = new();
    private static readonly Dictionary<Creature, int> RoundLoss = new();
    private static readonly Dictionary<Creature, int> LastRoundLoss = new();
    private static readonly Dictionary<Creature, List<CardModel>> NextTurnFree = new();

    private static int Get(Dictionary<Creature, int> map, Creature c) =>
        map.TryGetValue(c, out var v) ? v : 0;

    /// <summary>True HP loss on a player creature.</summary>
    public static void NoteHpLoss(Creature creature, int amount)
    {
        if (amount <= 0 || creature.Player == null) return;
        CombatLoss[creature] = Get(CombatLoss, creature) + amount;
        RoundLoss[creature] = Get(RoundLoss, creature) + amount;
    }

    /// <summary>The top of a player's turn: this round's loss becomes last
    /// turn's.</summary>
    public static void RollTurn(Creature creature)
    {
        LastRoundLoss[creature] = Get(RoundLoss, creature);
        RoundLoss.Remove(creature);
    }

    /// <summary>A new combat: every count starts at nothing.</summary>
    public static void ClearAll()
    {
        CombatLoss.Clear();
        RoundLoss.Clear();
        LastRoundLoss.Clear();
        NextTurnFree.Clear();
    }

    /// <summary>Facade: the HP this creature has lost this combat.</summary>
    public static int LostThisCombat(Creature? creature) =>
        creature == null ? 0 : Get(CombatLoss, creature);

    /// <summary>Tearful Monologue: "If you lost HP last turn".</summary>
    public static bool LostHpLastTurn(Creature? creature) =>
        creature != null && Get(LastRoundLoss, creature) > 0;

    /// <summary>Opening Number: "On your first turn".</summary>
    public static bool FirstTurnOfCombat(Creature? creature) =>
        creature?.CombatState?.RoundNumber == 1;

    /// <summary>Stage Directions: this card costs 0 next turn.</summary>
    public static void CostZeroNextTurn(Creature? owner, CardModel card)
    {
        if (owner == null) return;
        if (!NextTurnFree.TryGetValue(owner, out var list))
        {
            NextTurnFree[owner] = list = new List<CardModel>();
        }
        list.Add(card);
    }

    /// <summary>The top of the owner's next turn: each card set aside costs
    /// 0 this turn (the base game's "this turn": this turn or until played).
    /// A card no longer in a combat pile is skipped.</summary>
    public static void ApplyNextTurnCosts(Creature owner)
    {
        if (!NextTurnFree.Remove(owner, out var list)) return;
        foreach (var card in list)
        {
            if (!(card.Pile?.IsCombatPile ?? false)) continue;
            if (card.EnergyCost.CostsX) continue;
            card.EnergyCost.SetThisTurnOrUntilPlayed(0, reduceOnly: true);
        }
    }
}

/// <summary>The listener that feeds <see cref="FurinaSweep"/> for every
/// seat. Subscribed in <c>KleeMod.Initialize</c>.</summary>
public sealed class FurinaSweepHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaSweepHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaSweepHooks>(
            ModelDb.GetId<FurinaSweepHooks>());
        yield return _instance;
    }

    public override Task BeforeCombatStart()
    {
        FurinaSweep.ClearAll();
        return Task.CompletedTask;
    }

    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && creature.Player != null)
        {
            FurinaSweep.NoteHpLoss(creature, (int)Math.Ceiling(-delta));
        }
        return Task.CompletedTask;
    }

    public override Task BeforeSideTurnStart(
        PlayerChoiceContext choiceContext, CombatSide side,
        IReadOnlyList<Creature> participants, ICombatState combatState)
    {
        if (side != CombatSide.Player) return Task.CompletedTask;
        foreach (var creature in participants)
        {
            if (creature.Player == null) continue;
            FurinaSweep.RollTurn(creature);
            FurinaSweep.ApplyNextTurnCosts(creature);
        }
        return Task.CompletedTask;
    }
}

/// <summary><i>Arkhe in Balance</i>: "Whenever you play an Attack, gain 2
/// Block. Whenever you play a Skill, deal 2 damage to a random enemy." [3]
/// Her own plays only; the Block and the hit are unpowered, as every Furina
/// Power's are. Copies add. Sim twin: <c>furina_stage.arkhe_in_balance</c>.
/// </summary>
public sealed class ArkheInBalancePower : PowerModel, ILocalizationProvider
{
    public const string Title = "Arkhe in Balance";

    public List<(string, string)>? Localization => new()
    {
        ("title", Title),
        ("description",
            "Whenever you play an Attack, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold]. Whenever you play a Skill, deal "
          + "[blue]{Amount}[/blue] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null || Owner.IsDead || Amount <= 0) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        var type = cardPlay.Card.Type;
        if (type == CardType.Attack)
        {
            Flash();
            await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered,
                                        null, fast: true);
        }
        else if (type == CardType.Skill)
        {
            var enemies = FurinaStage.Enemies(Owner).ToList();
            if (FurinaStage.RandomOf(Owner, enemies) is not { } body) return;
            Flash();
            using var credit = Diagnostics.DamageCredit.Open(
                Owner, Diagnostics.DamageCredit.Power, Title);
            await ElementalHit.DealUnelemented(
                choiceContext, body, Amount, Owner, powered: false);
        }
    }
}

/// <summary><i>Objection!</i>: "The next time an enemy's attack makes you
/// lose HP this turn, it takes twice that much." Flame Barrier's window (it
/// lasts through the enemies' turn) and Flame Barrier's answer (unpowered,
/// from her), once per stack. Sim twin: <c>furina_stage.objection</c>.
/// </summary>
public sealed class ObjectionPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Objection!"),
        ("description",
            "The next time an enemy's attack makes you lose HP this turn, "
          + "it takes twice that much."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != Owner || dealer == null || Amount <= 0) return;
        if (dealer.Side == Owner.Side || !props.IsPoweredAttack()) return;
        if (result.UnblockedDamage <= 0) return;
        Flash();
        var back = result.UnblockedDamage * 2;
        if (Amount <= 1)
        {
            await PowerCmd.Remove(this);
        }
        else
        {
            await PowerCmd.ModifyAmount(choiceContext, this, -1m, null, null,
                                        silent: true);
        }
        if (dealer.IsAlive)
        {
            await CreatureCmd.Damage(choiceContext, dealer, back,
                                     ValueProp.Unpowered, Owner);
        }
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (Owner.Side != side) await PowerCmd.Remove(this);
    }
}

/// <summary><i>Trial by Water</i>'s mark, ON the enemy: "Until end of
/// turn, whenever that enemy takes damage, gain 2 Fanfare." The Fanfare goes
/// to the player who applied it, through the ledger's gain
/// (<see cref="FurinaStage.Gain"/>, Velvet Curtain's path). Copies add.
/// Sim twin: <c>furina_stage.trial_by_water</c>.</summary>
public sealed class TrialByWaterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Trial by Water"),
        ("description",
            "This turn, whenever this enemy takes damage, Furina "
          + "gains [blue]{Amount}[/blue] [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (target != Owner || Amount <= 0 || result.UnblockedDamage <= 0) return;
        if (Applier is not { } accuser) return;
        Flash();
        await FurinaStage.Gain(choiceContext, accuser, Amount, "Trial by Water");
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) await PowerCmd.Remove(this);
    }
}

/// <summary><i>Rainfall Overture</i>: "Your next Attack this turn hits ALL
/// enemies." The next Attack she plays is marked, and while it resolves each
/// of its hits that aims at one enemy aims at every enemy instead
/// (<see cref="AttackCommand_Targeting_RainfallOverture_Patch"/>), each
/// enemy taking its own Vulnerable. An Attack that already hits ALL or
/// random enemies spends it unchanged. One Attack per stack. Sim twin:
/// <c>furina_stage.RAINFALL_OVERTURE</c>.</summary>
public sealed class RainfallOverturePower : PowerModel, ILocalizationProvider
{
    private static readonly HashSet<CardModel> Widened = new();

    public List<(string, string)>? Localization => new()
    {
        ("title", "Rainfall Overture"),
        ("description",
            "Your next Attack this turn hits ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Is this attack, aimed at <paramref name="target"/>, one a
    /// Rainfall Overture widens? PURE.</summary>
    public static bool Widens(AttackCommand attack, Creature? target) =>
        attack.ModelSource is CardModel card
        && Widened.Contains(card)
        && attack.Attacker is { } attacker
        && target != null
        && target.Side != attacker.Side;

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        var card = cardPlay.Card;
        if (Owner == null || Amount <= 0 || card == null) return Task.CompletedTask;
        if (card.Owner?.Creature != Owner || card.Type != CardType.Attack)
        {
            return Task.CompletedTask;
        }
        if (Widened.Contains(card)) return Task.CompletedTask;
        Widened.Add(card);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var card = cardPlay.Card;
        if (card == null || !Widened.Remove(card)) return;
        Flash();
        if (Amount <= 1)
        {
            await PowerCmd.Remove(this);
        }
        else
        {
            await PowerCmd.ModifyAmount(choiceContext, this, -1m, null, null,
                                        silent: true);
        }
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (Owner.Side == side)
        {
            Widened.Clear();
            await PowerCmd.Remove(this);
        }
    }
}

/// <summary><i>Crowd Favorite</i>: "At the start of your turn, if your HP is
/// below half, gain 1 Energy." Energy Next Turn's moment
/// (<c>AfterEnergyReset</c>); below half is <c>hp * 2 &lt; max</c>, the
/// sheet's <c>hp_pct_below_50</c>. Copies add. Sim twin:
/// <c>furina_stage.crowd_favorite</c>.</summary>
public sealed class CrowdFavoritePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Crowd Favorite"),
        ("description",
            "At the start of your turn, if your HP is below half, gain "
          + "{Amount:energyIcons()}."),
        // Release fixes (2026-10-14): in combat the tip prints the number
        // half is (`HalfHpFace`); a face takes no parentheses.
        ("smartDescription",
            "At the start of your turn, if your HP is below {HalfHp}, gain "
          + "{Amount:energyIcons()}."),
    };

    /// <summary>{HalfHp} in the smart tip: the HP "below half" is below.
    /// Synced when applied and at each turn start.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new[] { new DynamicVar("HalfHp", 0m) };

    private void SyncHalfHp()
    {
        if (Owner == null) return;
        var half = DynamicVars["HalfHp"];
        half.BaseValue = global::KleeMod.Cards.HalfHpFace.Threshold(Owner.MaxHp);
        half.ResetToBase();
    }

    public override Task AfterApplied(Creature? applier, CardModel? cardSource)
    {
        SyncHalfHp();
        return Task.CompletedTask;
    }

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterEnergyReset(Player player)
    {
        if (Owner == null || player != Owner.Player || Amount <= 0) return;
        SyncHalfHp();
        if (Owner.CurrentHp * 2 >= Owner.MaxHp) return;
        Flash();
        await PlayerCmd.GainEnergy(Amount, player);
    }
}

/// <summary><i>Plot Twist</i>'s mark, ON the enemy: "This turn its attack
/// hits itself instead of you." While it holds the mark, an attack the enemy
/// makes (<c>AttackCommand.FromMonster</c>) is aimed at the enemy itself
/// (<see cref="AttackCommand_FromMonster_PlotTwist_Patch"/>), so its
/// Strength and its own Vulnerable count. It lasts through the enemy's turn.
/// Sim twin: <c>furina_stage.PLOT_TWIST</c>.</summary>
public sealed class PlotTwistPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Plot Twist"),
        ("description", "This turn, this enemy's attacks hit itself."),
    };

    public override PowerType Type => PowerType.Debuff;

    public override PowerStackType StackType => PowerStackType.Single;

    private static System.Reflection.FieldInfo? Field(string name)
    {
        try
        {
            return AccessTools.Field(typeof(AttackCommand), name);
        }
        catch (Exception)
        {
            return null;
        }
    }

    /// <summary>Aim an enemy's attack at the enemy itself when it holds the
    /// mark. Returns whether it did.</summary>
    public static bool Redirect(AttackCommand attack, Creature? self)
    {
        if (self == null || !self.IsAlive) return false;
        if (!self.Powers.OfType<PlotTwistPower>().Any()) return false;
        var combatState = Field("_combatState");
        var singleTarget = Field("_singleTarget");
        var side = AccessTools.PropertySetter(typeof(AttackCommand),
                                              nameof(AttackCommand.TargetSide));
        if (combatState == null || singleTarget == null || side == null)
        {
            Log.Error($"[{KleeMod.ModId}] Plot Twist: AttackCommand's target "
                      + "fields are gone; the attack is not redirected.");
            return false;
        }
        combatState.SetValue(attack, null);
        singleTarget.SetValue(attack, self);
        side.Invoke(attack, new object[] { self.Side });
        return true;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (Owner.Side == side) await PowerCmd.Remove(this);
    }
}

/// <summary>Rainfall Overture's seam: a hit aimed at one enemy by a widened
/// Attack aims at every enemy instead (the base game's own
/// <c>TargetingAllOpponents</c>, so each enemy takes its own
/// modifiers).</summary>
// lint: no-seat: scoped by the card being played, which only a Rainfall
// Overture's owner can have marked (`RainfallOverturePower.Widens`); every
// other attack in the game passes through untouched. It must run on every
// seat because the power's owner may be anyone who played her card.
[HarmonyPatch(typeof(AttackCommand), nameof(AttackCommand.Targeting))]
internal static class AttackCommand_Targeting_RainfallOverture_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(AttackCommand __instance, Creature target,
                               ref AttackCommand __result)
    {
        try
        {
            if (!RainfallOverturePower.Widens(__instance, target)) return true;
            var state = target.CombatState ?? __instance.Attacker?.CombatState;
            if (state == null) return true;
            __result = __instance.TargetingAllOpponents(state);
            return false;
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Rainfall Overture widen failed: {e}");
            return true;
        }
    }
}

/// <summary>Plot Twist's seam: an enemy's attack, set up by
/// <c>FromMonster</c> to target its opponents, is aimed back at the enemy
/// while it holds the mark.</summary>
// lint: no-seat: scoped by the attacking enemy holding a Plot Twist mark,
// which only a played Plot Twist puts on it; no seat is resolved, and every
// other monster attack passes through untouched.
[HarmonyPatch(typeof(AttackCommand), nameof(AttackCommand.FromMonster))]
internal static class AttackCommand_FromMonster_PlotTwist_Patch
{
    [HarmonyPostfix]
    private static void Postfix(AttackCommand __instance, MonsterModel monster)
    {
        try
        {
            PlotTwistPower.Redirect(__instance, monster?.Creature);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] Plot Twist redirect failed: {e}");
        }
    }
}

/// <summary>Plot Twist's one crash (a friend's run, 2026-10-19): the
/// Entomancer's Personal Hive gives Dazed to whoever hit it, read off
/// <c>dealer.Player</c>. A Plot Twisted Entomancer hits itself, an enemy has
/// no player, and the null killed the enemy turn loop, so the combat hung.
/// With no player behind the hit, the Hive has no deck to shuffle into and
/// does nothing. Osty's hits still pay (the base method resolves him to his
/// owner).</summary>
// lint: no-seat: scoped to a hit whose dealer is a creature with neither a
// player nor a pet owner, which only a Plot Twisted enemy attacking itself
// makes; every other Personal Hive trigger runs the base method untouched.
[HarmonyPatch(typeof(PersonalHivePower), nameof(PersonalHivePower.AfterDamageReceived))]
internal static class PersonalHivePower_AfterDamageReceived_PlotTwist_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(Creature? dealer, ref Task __result)
    {
        if (dealer == null || dealer.Player != null || dealer.PetOwner != null)
            return true;
        __result = Task.CompletedTask;
        return false;
    }
}
