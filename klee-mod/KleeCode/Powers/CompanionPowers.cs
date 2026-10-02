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
/// correct in solo and wrong in co-op, and the sim sees only solo. Since
/// EB-105 the mod has a PARTIAL second instrument: `klee-mod/KleeTests`
/// allocates two seats headlessly and `CoopSeamTests` covers per-seat
/// ownership -- but not a card being played, so this tracker's own defect
/// would still have to be found by playing. See the G-B2 census in
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
        // `EB-420` PUT AN ARM FACE HERE AND `EB-464` TOOK IT AWAY. It read
        // "Your Salon performs on the first play only", printing a rule this
        // code kept: `SalonMemberPower.CompanionPlayTrigger` was gated on
        // `IsFirstInSeries`, on LAW:145 read through `KleeCompanionSpark` ("a
        // per-play bound a replay can double is not a bound"). The r8 ruling
        // reversed the rule -- that clause is about a resource MINT and a
        // performance is not one -- so a replayed Companion card performs, and
        // the arm sentence would now be the only thing on any screen saying
        // otherwise. The shipped face is true on every arm again, which is why
        // there is no replacement clause and no `SmartDescriptionLocKey`
        // override below.
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
/// Attacks +Amount for the REST OF THIS TURN; the sim pops
/// attack_up_this_turn at player_turn_end_triggers.
///
/// `EB-699`. TITLED AFTER ITS EFFECT, BECAUSE NO ONE CARD OWNS IT. It read
/// "Fantastic Voyage" from when Bennett's burst was the only thing that made
/// it, and that card stopped making it in the redesign a few lines up
/// (<c>CelestialGiftPower</c> (retired)'s note: the burst grants real
/// <c>StrengthPower</c> now). What applies it today is Kujou Sara's Tengu
/// Stormcall, paying in at the start of the turn it promised -- so the buff on
/// the player's bar wore another companion's card name and nothing on the
/// screen connected the two (Kokomi r30 lane 1). A power more than one card
/// can make is named for what it does.
/// </summary>
public sealed class AttackUpThisTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Attack Up"),
        ("description",
            "Your Attacks deal [blue]{Amount}[/blue] additional damage this "
          + "turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
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
/// The buff_next_attack rider (Chevreuse, Vanguard's Valor, since the shipped
/// Bennett card left at legacy cleanup stage 5): your NEXT attack card deals
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
        ("title", "Vanguard's Valor"),
        ("description",
            "Your next Attack deals [blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
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
/// Charlotte, First-Person Shutter (tier0 op block_next_turn) uses the game's
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
        ("description",
            "Your [gold]Shatters[/gold] deal [blue]{Amount}[/blue] additional "
          + "damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Total bonus on a Shatter dealt by this creature, 0 if none.</summary>
    public static int BonusFor(Creature? dealer) =>
        dealer?.Powers.OfType<ShatterBonusPower>().FirstOrDefault()?.Amount ?? 0;
}

