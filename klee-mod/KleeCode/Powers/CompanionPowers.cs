using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// tier0/constants.py mirrors for the companion powers. Numbers mirrored,
/// never re-derived (sim is LAW).
/// </summary>
public static class CompanionConstants
{
    public const int OzDamage = 3;             // OZ_DMG (applies electro)
    public const int WitchsFlameBurst = 3;     // WITCHS_FLAME_BURST per aura
    public const int SolarIsotomaBlock = 3;    // SOLAR_ISOTOMA_BLOCK per hit
    public const int CelestialGiftBlock = 4;   // CELESTIAL_GIFT_BLOCK per turn
    public const int MasqueBondBlock = 5;      // MASQUE_BOND_BLOCK owed per turn
}

/// <summary>
/// Which companions have been played this combat, PER OWNER, unique in
/// first-play order (tier0 companions_played + dict.fromkeys) -- Best Friends
/// Forever reads it. Keyed to the combat-state instance, the
/// DetonationsThisCombat pattern: a fresh combat starts empty with no
/// reset hook. Recorded from KleeElementalHooks.BeforeCardPlayed
/// (IsFirstInSeries = once per play, the sim's play_card append site).
///
/// OWNERSHIP, fixed 2026-07-25 (G-B1). This list used to be combat-wide and
/// unfiltered, so in co-op Best Friends Forever copied the PARTNER's
/// companions as well as your own -- reported from the 2026-07-25 A0 playtest
/// as "pulled the co-op partner's cards". The sheet text never meant that; the
/// yaml op `copy_companions_played_this_combat` always meant the owner's, and
/// tier 0.5 models a single seat so no sim run could ever have disagreed.
///
/// This is the shape of the whole bug class: a "this combat" tracker is
/// correct in solo and wrong in co-op, and solo is the only configuration the
/// instruments can see. See the G-B2 census in
/// docs/archive/ship-what-we-know-sprint-log.md for the other consumers.
///
/// Uniqueness is PER OWNER, not global: if both players play Oz, both should
/// get an Oz back. Deduplicating across owners would fix the leak by creating
/// a subtler one.
///
/// THE ENTRY CARRIES THE UPGRADE (R114/FLAG-2(i), BACKLOG BFF-copy). A
/// ModelId alone is the PRINTED card, and `ModelDb.GetById` rebuilds it
/// pristine -- so recording ids only replayed every companion unupgraded.
/// The sim expresses the same rule through the id itself: it records
/// `card.id`, which IS `foo+` for an upgraded companion, so the upgrade
/// travels with the copy the way the ruling requires. C# keeps the upgrade in
/// the entry beside the id and Best Friends Forever re-applies it, the same
/// repair SYS-4 made for the other copy ops (`UpgradeInternal`,
/// vendor/STS2_MCP/McpMod.Helpers.cs:54-66).
///
/// The DEDUPE KEY is `(Owner, Id)` -- a BASE ModelId, so `foo` and `foo+` are
/// ONE entry. RATIFIED by the owner's BFF-dedupe ruling (2026-08-06): an
/// upgraded companion IS the same pool entry as its base, and Best Friends
/// Forever replays each companion once with no surprise duplication. This
/// side was already correct; the sim changed to match, and now strips the
/// `+` suffix at ITS record site (combat.py `_finish_play`, `_base_card_id`)
/// so both ledgers dedupe on the same key at the same moment. With one entry,
/// the upgrade recorded is the FIRST play's -- which is what the entry has
/// always meant, and what the sim's first-play instance id now carries too.
/// </summary>
public static class CompanionPlays
{
    private static ICombatState? _combat;
    private static readonly List<(Player Owner, ModelId Id, bool IsUpgraded)>
        _played = new();

    public static void Record(ICombatState? combatState, CardModel card)
    {
        if (combatState == null) return;
        // No owner means nothing can ever read this entry back -- every reader
        // filters by owner -- so dropping it is the honest move rather than
        // filing it under a null that would match nobody.
        var owner = card.Owner;
        if (owner == null) return;
        if (!ReferenceEquals(combatState, _combat))
        {
            _combat = combatState;
            _played.Clear();
        }
        if (!_played.Any(entry => ReferenceEquals(entry.Owner, owner)
                                  && entry.Id == card.Id))
        {
            _played.Add((owner, card.Id, card.IsUpgraded));
        }
    }

    /// <summary>
    /// The companions <paramref name="owner"/> played this combat, in
    /// first-play order, each with the upgrade state its copy must carry
    /// (R114/FLAG-2(i)). Never another player's.
    /// </summary>
    public static IReadOnlyList<(ModelId Id, bool IsUpgraded)> PlayedThisCombat(
        ICombatState combatState, Player? owner)
    {
        if (!ReferenceEquals(combatState, _combat) || owner == null)
        {
            return System.Array.Empty<(ModelId Id, bool IsUpgraded)>();
        }
        return _played
            .Where(entry => ReferenceEquals(entry.Owner, owner))
            .Select(entry => (entry.Id, entry.IsUpgraded))
            .ToList();
    }
}

/// <summary>
/// Friendly Visit: Companion cards cost Amount less this turn (tier0
/// companion_cost_delta_this_turn). Rides the same
/// Hook.ModifyEnergyCostInCombat surface as SparkPower's zeroing; the game
/// clamps at 0 via GetAmountToSpend's Math.Max.
///
/// FLAG-1 (R114, Errata Batch 2 item 7): the discount SCOPES TO THE WRITING
/// TURN. It used to be removed at the next player turn's START, so a stack
/// written on turn N survived the whole enemy side and was still standing
/// when turn N+1 opened -- an additive, uncapped accumulator whose discount
/// outlived the turn that wrote it, and one half of the S13-X1 family.
/// Verbatim: "Limit the cost discount to the current turn? Yes."
///
/// One boundary idiom, now used twice: this is exactly what
/// `ReplayNextCompanionPower` below does for X11 (R110), and the sim's
/// mirror sits beside `state.in_player_turn = False` in
/// tier0/engine/combat.py. WRITE-SIDE scoping in both engines, for the same
/// reason it was chosen there: a `PowerStackType.Counter`'s stacks carry no
/// per-stack metadata, so neither engine can stamp a grant with its turn and
/// filter at spend time, but both can bound the counter's LIFETIME.
///
/// WHAT THIS DOES NOT CLOSE, stated because the fix invites the mistake:
/// the WITHIN-turn free-companion loop survives by design. A same-turn
/// bound does not touch a mechanism that accumulates and spends inside one
/// turn. That loop is governed by the X2 rarity law (R109).
/// </summary>
public sealed class CompanionCostThisTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Friendly Visit"),
        ("description",
            "[gold]Companion[/gold] cards cost {Amount} less this turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card is not ICompanionCard) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = System.Math.Max(0m, originalCost - Amount);
        return true;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        // Expires with the turn it was written on (FLAG-1, R114) -- not at
        // the next player turn's start, which let it ride the enemy side.
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Study Buddy: the next Companion card played this turn is played Amount
/// extra times (tier0 replay_next_companion: consumed whole by the next
/// companion play_card, expiring at the END of the turn it was granted on).
/// ModifyCardPlayCount is the game's replay surface -- the extra plays are a
/// series on one CardPlay, which is also what the sim's
/// `for _ in range(replays)` is.
///
/// SAME TURN ONLY (sitting 2026-08-06, family X11): "Cap those effects to
/// 'same turn only'". This side already had the ratified semantics --
/// AfterSideTurnEnd below bounds the grant's lifetime at the writing turn's
/// end -- and the sim was the divergent half (it cleared at the NEXT player
/// turn's open, so an unspent grant survived the enemy side). tier0
/// combat.py now clears at `in_player_turn = False`, matching this hook.
/// Write-side scoping was the only mechanism expressible identically in both
/// engines: a Counter power's stacks carry no per-stack metadata, so neither
/// side can stamp a grant with its turn number and filter at spend time.
/// Both parity twins -- Study Buddy (Klee) and Duet (Furina) -- apply THIS
/// power, so one boundary covers both.
/// </summary>
public sealed class ReplayNextCompanionPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Study Buddy"),
        ("description",
            "The next [gold]Companion[/gold] card you play this turn is "
          + "played {Amount} extra time{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (card is not ICompanionCard) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        return playCount + Amount;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Consumed by that one companion play (sim zeroes the counter as it
        // captures the replays); the play count was read at play creation,
        // so removing after the series cannot shorten it.
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        // Expires with the turn it was granted on -- the ratified "same turn
        // only" boundary (sitting 2026-08-06, family X11). The sim's mirror is
        // tier0/engine/combat.py, beside `state.in_player_turn = False`.
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Fischl: at the end of your turn, Oz makes one full-pipeline Electro hit
/// (tier0 player_turn_end_triggers: deal_damage_to_enemy(OZ_DMG,
/// element="electro") to a random living enemy), then the summon ticks down.
/// Sim order is hit THEN decrement, hence the manual TickDownDuration after
/// the volley -- the AuraPower own-decay idiom.
/// </summary>
public sealed class OzSummonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oz, at Your Side"),
        ("description",
            "At the end of your turn, Oz deals "
          + $"{CompanionConstants.OzDamage} damage and applies "
          + "[gold]Electro[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// NOT A BROADCAST OVERRIDE ANY MORE (EB-19/races-c). The ELECTRO leg of
    /// the three end-of-turn volleys, fired SECOND by TurnEndSequencer --
    /// tier0 `effects.player_turn_end_triggers` orders them Pyro -> Electro ->
    /// Hydro.
    /// </summary>
    public async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;

        var candidates = CombatState.HittableEnemies.ToList();
        if (candidates.Count > 0)
        {
            var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target != null)
            {
                await ElementalHit.Deal(
                    choiceContext, target, Element.Electro,
                    CompanionConstants.OzDamage, Owner);
            }
        }

        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Durin: PERMANENT. At end of turn, consumes every enemy Pyro aura; each
/// consumed aura deals Amount unpowered damage and grants 3 Burst Energy.
/// This turns Klee's Pyro saturation into value while clearing the board for
/// Hydro/Cryo to establish the next reaction. No tick-down.
/// </summary>
public sealed class WitchsFlamePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Witch's Flame"),
        ("description",
            "At the end of your turn, consume [gold]Pyro[/gold] from each "
          + "enemy. For each aura consumed, deal {Amount} damage and gain "
          + $"{CompanionConstants.WitchsFlameBurst} [gold]Burst Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner.Player == null) return;

        foreach (var target in CombatState.HittableEnemies.ToList())
        {
            var aura = AuraCmd.Find(target);
            if (aura?.Element != Element.Pyro) continue;

            await PowerCmd.Remove(aura);
            // NC-1 (R116, Errata Batch 2 item 3): companion/power damage
            // scales with the player. The sim deals this through
            // `deal_damage_to_enemy` (effects.py, `witchs_flame`), which is
            // the full pipeline -- Strength and Weak x0.75 on the dealer,
            // Vulnerable x1.5 on the target. This hit is Unpowered, so the
            // game's native powers gate themselves out of it and the sim's
            // modifiers have to be mirrored explicitly, exactly as
            // `ElementalHit.Deal` does for the summon pulses. It cannot USE
            // `ElementalHit.Deal`: the sim passes `element=None` here (the
            // aura is consumed, not re-applied), so there is no element to
            // hit with and no reaction to amplify. Truncate ONCE at the end,
            // the sim's single `int()`.
            //
            // Note the register this ruling half-belongs to: power-sourced
            // DAMAGE runs the pipeline (NC-1); power-sourced BLOCK stays raw
            // (NC-11). Adjacent, opposite, and both are the base game's shape.
            var dealt = SimDamagePipeline.DealerMods(Owner, Amount);
            await CreatureCmd.Damage(
                choiceContext, target, (int)SimDamagePipeline.TargetMods(target, dealt),
                ValueProp.Unpowered, dealer: null, cardSource: null);
            await KleeBurstResource.Gain(
                choiceContext, Owner, CompanionConstants.WitchsFlameBurst,
                cardSource: null);
        }
    }
}

/// <summary>
/// Albedo, 3 turns: every powered-attack hit you deal to an enemy holding an
/// aura grants Block (tier0 deal_damage_to_enemy: the Solar Isotoma check
/// runs BEFORE the hit resolves, so the hit that consumes the aura still
/// pays out -- hence BeforeDamageReceived, which fires before the damage and
/// before AuraPower's AfterDamageReceived consumption). Ticks down at the
/// player's turn end (sim player_turn_end_triggers).
/// </summary>
public sealed class SolarIsotomaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Solar Isotoma"),
        ("description",
            "Your Attacks against enemies holding an elemental aura grant "
          + $"{CompanionConstants.SolarIsotomaBlock} [gold]Block[/gold] per "
          + "hit. Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return;
        if (!props.IsPoweredAttack()) return;
        if (AuraCmd.Find(target) == null) return;

        await CreatureCmd.GainBlock(
            Owner, CompanionConstants.SolarIsotomaBlock,
            ValueProp.Unpowered, null, fast: true);
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Nicole: your attack cards deal +Amount per hit (tier0 resolve_card adds
/// celestial_gift into current_attack_bonus, which lands on every hit's
/// base), and you gain Block at the start of your turn
/// (player_turn_start_triggers).
/// </summary>
public sealed class CelestialGiftPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Celestial Gift"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Strength[/gold] "
          + $"and {CompanionConstants.CelestialGiftBlock} [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    // ModifyDamageAdditive is GONE, and its absence is the redesign. This power
    // used to add a static flat bonus to attacks here; it now grants real
    // Strength below, which the damage pipeline folds in on its own. Keeping
    // both would pay the buff twice -- once flat, once as Strength -- and the
    // sim's flat_attack_bonus dropped its celestial_gift term in the same
    // change for exactly that reason.

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        // Sim order (effects.py player turn-start triggers): Strength first,
        // then Block. Nothing here reads the other, so the order is parity
        // bookkeeping rather than a dependency -- but a trace diff would show
        // it, so it matches.
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, Owner, Amount, applier: Owner, cardSource: null);
        await CreatureCmd.GainBlock(
            Owner, CompanionConstants.CelestialGiftBlock,
            ValueProp.Unpowered, null, fast: true);
    }
}

/// <summary>
/// Bennett burst (Fantastic Voyage): attacks +Amount for the REST OF THIS
/// TURN; the sim pops attack_up_this_turn at player_turn_end_triggers.
/// </summary>
public sealed class AttackUpThisTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fantastic Voyage"),
        ("description", "Your Attacks deal {Amount} more damage this turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount;
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
/// Bennett Passion's rider (buff_next_attack): your NEXT attack card deals
/// +Amount per hit, then the whole stack is consumed. tier0 resolve_card
/// pops next_attack_up into the play's attack bonus, so the bonus covers
/// every hit of that one card (its repeat tail included -- same CardPlay)
/// and is gone afterwards; here the modify hook pays out during the play
/// and AfterCardPlayed removes the power once the attack's series ends.
/// </summary>
public sealed class NextAttackUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Passion Overload"),
        ("description", "Your next Attack deals {Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount;
    }

    /// <summary>
    /// Consumed by the FIRST resolution of an attack card, not the last.
    ///
    /// CORRECTION (bug hunt 2026-07-21). This gated on IsLastInSeries, which
    /// let the bonus ride every replay of a Study Buddy series: Passion
    /// Overload (+4) -> Study Buddy -> Kaeya dealt 18 where the sim deals 14.
    /// tier0 resolve_card POPS next_attack_up (its siblings celestial_gift and
    /// attack_up_this_turn deliberately use .get(), which is what makes the pop
    /// load-bearing rather than incidental), and combat.py's replay loop issues
    /// N separate resolve_card calls -- so replay #2 sees nothing.
    ///
    /// The repeat tail is unaffected and must be: repeat_this re-runs
    /// _resolve_effects INSIDE one resolve_card, after current_attack_bonus is
    /// already snapshotted, so the tail keeps the bonus. A series is the replay
    /// loop; the tail is an in-OnPlay for-loop. Removing at IsFirstInSeries
    /// draws the line in exactly the same place the sim does.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card.Type != CardType.Attack) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!cardPlay.IsFirstInSeries) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Charlotte, Enduring Frosthelm (tier0 op block_next_turn) uses the game's
/// OWN BlockNextTurnPower -- no mod power needed. Verified by decompile
/// against the sim: it grants Amount Block from AfterBlockCleared (the hook
/// that fires right after the turn's block reset, which is exactly where
/// tier0 grants it -- combat.py zeroes p.block, then player_turn_start_
/// triggers pops block_next_turn) and then removes itself, which IS the sim's
/// `powers.pop`. Unpowered, with a Block hover tip already wired.
/// Same house rule as WeakPower / VulnerablePower / PoisonPower: when the
/// core already ships the exact semantics, mirror by USING it.
/// </summary>

/// <summary>
/// Freminet, Shattering Pressure (tier0 power shatter_bonus): your Shatters
/// deal +Amount damage.
///
/// Read by FrozenPower, which is where the Shatter is dealt. The sim adds it
/// to SHATTER_DAMAGE inside the same raw `enemy.hp -=` (effects.py), so the
/// rider is unblockable and unamplified exactly like the base Shatter.
/// Permanent for the combat -- a power card, no duration tick.
/// </summary>
public sealed class ShatterBonusPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Shattering Pressure"),
        ("description", "Your [gold]Shatters[/gold] deal {Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Total bonus on a Shatter dealt by this creature, 0 if none.</summary>
    public static int BonusFor(Creature? dealer) =>
        dealer?.Powers.OfType<ShatterBonusPower>().FirstOrDefault()?.Amount ?? 0;
}

/// <summary>
/// Metallicize -- Gorou, Heart of the Clan (Inazuma roster, playtest sprint).
///
/// TIMING IS THE SIM'S, NOT THE TABLETOP CONVENTION. Slay the Spire's
/// Metallicize grants Block at END of turn; tier0's grants it at turn START
/// (engine/powers.py on_turn_start). Parity with the sim is the contract here,
/// so this fires at turn start, and the difference is deliberate rather than
/// an oversight -- start-of-turn Block survives the block-reset and is
/// therefore strictly better, which is priced into every number her sheet was
/// measured with. Changing it to end-of-turn is a BALANCE change and needs a
/// re-measure, not a bugfix.
///
/// No native equivalent exists in the game assembly (there is no
/// MetallicizePower and no PlatedArmor), so this is ours.
/// </summary>
public sealed class MetallicizePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Metallicize"),
        ("description", "At the start of your turn, gain {Amount} Block."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        // NC-11 (R116, Errata Batch 2 item 4): power-sourced block is RAW.
        // Unpowered, not Move -- StS applies Frail to CARD block via
        // AbstractCard.applyPowersToBlock, and Dexterity's additive hook
        // carries the same `IsPoweredCardOrMonsterMoveBlock` predicate, so
        // passive block (Metallicize, Crystallize, Solar Isotoma) is exempt
        // from both. tier0 writes `fighter.block +=` at
        // `powers.on_turn_start` for exactly that reason, and R116 ruled the
        // exemption canonical.
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
    }
}
