using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE MONDSTADT COMPANION OVERHAUL'S POWERS (QUARANTINED, R213 B).
///
/// Nine powers, in two shapes the engine already runs: a START-OF-TURN payout
/// (<see cref="CelestialGiftPower"/>'s shape) and an END-OF-TURN volley
/// (<see cref="OzSummonPower"/>'s). Nothing here invents a hook; what is new
/// is the printed text each one carries, which comes verbatim from the
/// approved workshop's sec.3.
///
/// NO POWER BELOW OVERRIDES AN END-OF-TURN BROADCAST, and that is EB-19/races-c
/// applied a second time rather than a style choice. Six of them fire at the
/// end of the player's turn, four of the six put an ELEMENT on an enemy that
/// may already carry one, and five of the six draw a target from the shared
/// <c>Rng.CombatTargets</c> stream. Same-side co-tenants of one broadcast have
/// no guaranteed relative order, so a deck holding two of them would have had
/// its reactions -- and every later roll in the run -- decided by listener
/// iteration order. <see cref="CompanionOverhaulTurnEnd"/> is the one tenant,
/// and it drives all six in the sim's order.
///
/// The START-OF-TURN three DO override their broadcast, and the difference is
/// argued rather than inherited: they are COMMUTATIVE. Two grant the player
/// Block or Strength and the third applies Vulnerable to enemies; none reads a
/// value another writes, none draws from an rng stream, and the one power that
/// reads Block reads a value LATCHED at the previous turn's end (see
/// <see cref="RevelationPower"/>). Order among them cannot change an outcome,
/// so imposing one would be ceremony.
/// </summary>
internal static class CompanionOverhaulTargeting
{
    /// <summary>
    /// One random living enemy off the shared combat-target stream, or null.
    /// tier0 `_pick_targets("random_enemy")` -> `state.rng.choice(...)`. One
    /// helper so five volleys cannot each roll a slightly different way.
    /// </summary>
    internal static Creature? RandomEnemy(ICombatState combatState)
    {
        var candidates = combatState.HittableEnemies.ToList();
        if (candidates.Count == 0) return null;
        return combatState.RunState.Rng.CombatTargets.NextItem(candidates);
    }

    /// <summary>
    /// The enemy holding the most elemental auras, or null when no enemy holds
    /// one. Jean's Dandelion Breeze is the only reader.
    ///
    /// A creature in this engine holds AT MOST ONE aura (<c>AuraCmd.Find</c>
    /// returns a single power), so "the most" is a count over {0, 1} and this
    /// is really "the first aura-bearer in board order". It is written as a
    /// max anyway, and the sim's twin is written the same way, because the
    /// card's printed words are "the most" and an engine that grew a second
    /// aura slot must not silently keep answering the one-slot question.
    /// Board order breaks the tie in BOTH engines (`max` returns the first
    /// maximal element in Python; <c>OrderByDescending</c> is documented
    /// stable in .NET), so the two cannot disagree about which of two
    /// aura'd enemies is picked.
    /// </summary>
    internal static Creature? MostAuras(ICombatState combatState)
    {
        var best = combatState.HittableEnemies
            .OrderByDescending(e => e.Powers.OfType<AuraPower>().Count())
            .FirstOrDefault();
        if (best == null) return null;
        return AuraCmd.Find(best) == null ? null : best;
    }
}

/// <summary>
/// Diona, Signature Mix: "For 2 turns, at the start of your turn gain 4
/// Block." (The 2 Weak to all enemies is on the card, not here.)
///
/// Amount is TURNS REMAINING -- the <see cref="OzSummonPower"/> grammar, and
/// the reason a second copy makes the field last longer rather than pay twice
/// per turn: the number the card prints is the DURATION, so that is the number
/// the stack holds.
/// </summary>
public sealed class SignatureMixPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Signature Mix"),
        ("description",
            "At the start of your turn, gain "
          + $"{CompanionOverhaulLaw.SignatureMixBlock} [gold]Block[/gold]. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        // NC-11: power-sourced BLOCK stays raw (the sim adds it straight to
        // `p.block`); only power-sourced DAMAGE runs the pipeline (NC-1).
        await CreatureCmd.GainBlock(
            Owner, CompanionOverhaulLaw.SignatureMixBlock,
            ValueProp.Unpowered, null, fast: true);
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Nicole, Revelation, Uncreated Light: "At the start of your turn, gain 5
/// Block. If you had Block left at the end of your last turn, also gain 2
/// Strength." PERMANENT -- a Power has no turn limit (workshop sec.1).
///
/// THE LATCH IS THE CARD. "Had Block left at the end of your last turn" cannot
/// be read at the start of this one: the game clears Block on the turn tick,
/// which is exactly why <see cref="CelestialGiftPower"/> can grant Block from
/// this same hook and have it survive. So the answer is recorded at the END of
/// the turn, by <see cref="CompanionOverhaulTurnEnd"/>, after every other
/// overhaul effect has resolved -- two of which GRANT Block, and a latch taken
/// before them would have answered a question about a board the player never
/// saw.
///
/// It latches FALSE on the turn the card is played, because there is no
/// previous turn to have held Block through. That is the literal reading and
/// it is also the safe one: a fresh power that paid Strength immediately would
/// be paying for a line nobody held.
/// </summary>
public sealed class RevelationPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Revelation, Uncreated Light"),
        ("description",
            "At the start of your turn, gain "
          + $"{CompanionOverhaulLaw.RevelationBlock} [gold]Block[/gold]. If "
          + "you had [gold]Block[/gold] left at the end of your last turn, "
          + $"also gain {CompanionOverhaulLaw.RevelationStrength} "
          + "[gold]Strength[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Did the owner end their last turn with Block standing? Written
    /// once per turn by <see cref="CompanionOverhaulTurnEnd"/>.</summary>
    internal bool HeldTheLine { get; private set; }

    /// <summary>The end-of-turn latch. Sim twin: `state.player.block > 0`
    /// recorded at the tail of `player_turn_end_triggers`.</summary>
    internal void NoteEndOfTurn() => HeldTheLine = Owner.Block > 0;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        // Once per stack: a second copy of a Rare Power is a second copy, the
        // base game's norm for Powers, and the sim multiplies by the same
        // stack count.
        await CreatureCmd.GainBlock(
            Owner, CompanionOverhaulLaw.RevelationBlock * Amount,
            ValueProp.Unpowered, null, fast: true);
        if (HeldTheLine)
        {
            await PowerCmd.Apply<StrengthPower>(
                choiceContext, Owner,
                CompanionOverhaulLaw.RevelationStrength * (int)Amount,
                applier: Owner, cardSource: null);
        }
    }
}

/// <summary>
/// Mona, Stellaris Phantasm: "Next turn, enemies take 50% more damage."
///
/// Vulnerable IS that sentence in this engine -- <c>VULNERABLE_TAKEN_MULT</c>
/// is 1.50 and the C# <c>VulnerablePower</c> mirrors it -- so the card does not
/// get a private multiplier. What it needs is the DELAY: Vulnerable applied on
/// the turn the card is played would cover the rest of THIS turn, and the card
/// says next. So this power is a one-shot promise that resolves at the next
/// player turn start and then removes itself.
///
/// Amount is the number of COPIES, and each pays one Vulnerable -- one turn of
/// vulnerability apiece, since Vulnerable's stacks are its duration.
/// </summary>
public sealed class StellarisOmenPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stellaris Phantasm"),
        ("description",
            "At the start of your next turn, apply "
          + $"{CompanionOverhaulLaw.OmenVulnerable} [gold]Vulnerable[/gold] "
          + "to ALL enemies."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        foreach (var target in CombatState.HittableEnemies.ToList())
        {
            await PowerCmd.Apply<VulnerablePower>(
                choiceContext, target,
                CompanionOverhaulLaw.OmenVulnerable * (int)Amount,
                applier: Owner, cardSource: null);
        }
        // Removed WHOLE, not ticked: the promise is kept once however many
        // copies were played, so a two-stack omen must not stretch across two
        // turns. TickDownDuration would do exactly that.
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Kaeya, Glacial Waltz: "For 3 turns, at the end of your turn deal 6 Cryo
/// damage to a random enemy." Amount is TURNS REMAINING.
///
/// Fired by <see cref="CompanionOverhaulTurnEnd"/>, never by a broadcast of
/// its own -- see this file's header.
/// </summary>
public sealed class GlacialWaltzPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Glacial Waltz"),
        ("description",
            "At the end of your turn, deal "
          + $"{CompanionOverhaulLaw.GlacialWaltzDamage} damage and apply "
          + "[gold]Cryo[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target != null)
        {
            await ElementalHit.Deal(
                choiceContext, target, Element.Cryo,
                CompanionOverhaulLaw.GlacialWaltzDamage, Owner);
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Fischl, Oz at Your Side: "At the end of your turn, Oz deals 5 Electro
/// damage to a random enemy." NO TURN LIMIT -- the workshop's sec.1 rule, and
/// its sec.3 note: "a Power cannot be reapplied, so Oz stays out, which is his
/// C1." That is the whole difference from the shipped
/// <see cref="OzSummonPower"/>, which is a three-turn Counter, and it is why
/// this is a separate class rather than a retune of that one: the shipped row
/// has to keep meaning what it printed on a flag-off build.
///
/// Amount is the number of COPIES: two Ozes, two volleys.
/// </summary>
public sealed class MondstadtOzPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oz, at Your Side"),
        ("description",
            "At the end of your turn, Oz deals "
          + $"{CompanionOverhaulLaw.OzDamage} damage and applies "
          + "[gold]Electro[/gold] to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        for (var i = 0; i < Amount; i++)
        {
            // Re-rolled per volley: a hit can kill, and the sim re-picks from
            // living_enemies each time round.
            var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
            if (target == null) break;
            await ElementalHit.Deal(
                choiceContext, target, Element.Electro,
                CompanionOverhaulLaw.OzDamage, Owner);
        }
        // NO tick-down. The power is permanent by design.
    }
}

/// <summary>
/// Lisa, Lightning Rose: "For 3 turns, at the end of your turn deal 5 Electro
/// damage to a random enemy and apply 1 Vulnerable." Amount is TURNS
/// REMAINING.
///
/// The Vulnerable lands on the SAME enemy the damage hit, and after it: the
/// printed sentence is one clause about one enemy, and applying the debuff
/// first would amplify the card's own hit by 50% on a card that does not say
/// so.
/// </summary>
public sealed class LightningRosePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lightning Rose"),
        ("description",
            "At the end of your turn, deal "
          + $"{CompanionOverhaulLaw.LightningRoseDamage} damage, apply "
          + "[gold]Electro[/gold], and apply "
          + $"{CompanionOverhaulLaw.LightningRoseVulnerable} "
          + "[gold]Vulnerable[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target != null)
        {
            await ElementalHit.Deal(
                choiceContext, target, Element.Electro,
                CompanionOverhaulLaw.LightningRoseDamage, Owner);
            // The hit may have killed it. Vulnerable on a corpse is legal in
            // this engine (the aura door accepts one, R210 Q3) but pointless,
            // and the sim skips a dead body here, so this does too.
            if (!target.IsDead)
            {
                await PowerCmd.Apply<VulnerablePower>(
                    choiceContext, target,
                    CompanionOverhaulLaw.LightningRoseVulnerable,
                    applier: Owner, cardSource: null);
            }
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Venti, Wind's Grand Ode: "For 2 turns, at the end of your turn Swirl all
/// enemies." Amount is TURNS REMAINING. (The 8 damage to all enemies is the
/// card's own body.)
///
/// Swirl is <c>ElementalHit.ApplyOnly(..., Element.Anemo, ...)</c>, the same
/// call the generated Swirl cards make, so "what a Swirl is" has one
/// definition. Anemo never sticks, so a Swirl into an aura-less board is a
/// no-op in both engines.
/// </summary>
public sealed class GrandOdePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Wind's Grand Ode"),
        ("description",
            "At the end of your turn, [gold]Swirl[/gold] the aura of ALL "
          + "enemies. Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        foreach (var target in CombatState.HittableEnemies.ToList())
        {
            await ElementalHit.ApplyOnly(
                choiceContext, target, Element.Anemo, Owner);
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Jean, Dandelion Breeze: "At the end of your turn, Swirl the enemy with the
/// most auras and gain 6 Block." PERMANENT; Amount is the number of COPIES.
///
/// The Block is paid whether or not a Swirl landed -- the sentence is two
/// clauses joined by "and", not a consequence -- which is also the reading
/// that keeps a Rare Power from being dead against an aura-less board.
/// </summary>
public sealed class DandelionBreezePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Dandelion Breeze"),
        ("description",
            "At the end of your turn, [gold]Swirl[/gold] the enemy with the "
          + "most auras and gain "
          + $"{CompanionOverhaulLaw.DandelionBreezeBlock} [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        for (var i = 0; i < Amount; i++)
        {
            var target = CompanionOverhaulTargeting.MostAuras(CombatState);
            if (target != null)
            {
                await ElementalHit.ApplyOnly(
                    choiceContext, target, Element.Anemo, Owner);
            }
            await CreatureCmd.GainBlock(
                Owner, CompanionOverhaulLaw.DandelionBreezeBlock,
                ValueProp.Unpowered, null, fast: true);
        }
    }
}

/// <summary>
/// Albedo, Solar Isotoma: "At the end of your turn, if any enemy has an aura,
/// deal 8 damage to that enemy and gain 4 Block." PERMANENT; Amount is the
/// number of COPIES.
///
/// THE DAMAGE CARRIES NO ELEMENT, because the card's text names none. It runs
/// the sim's damage pipeline exactly as <see cref="WitchsFlamePower"/>'s does
/// (NC-1: power-sourced damage scales with the player) and the Block stays raw
/// (NC-11) -- adjacent, opposite, both the base game's shape.
///
/// "That enemy" is the aura-bearer the check found, which is the same
/// most-auras pick Jean's Breeze uses. One helper, so two Rares cannot
/// disagree about which enemy "the one with an aura" is.
///
/// Both halves are inside the condition: no aura on the board, no damage and
/// no Block. "If any enemy has an aura, deal 8 damage to that enemy AND gain 4
/// Block" reads as one guarded sentence -- unlike Jean's, whose two clauses are
/// joined by a bare "and" with no condition in front of them.
/// </summary>
public sealed class SolarIsotomaBloomPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Solar Isotoma"),
        ("description",
            "At the end of your turn, if any enemy has an aura, deal "
          + $"{CompanionOverhaulLaw.IsotomaDamage} damage to that enemy and "
          + $"gain {CompanionOverhaulLaw.IsotomaBlock} [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        for (var i = 0; i < Amount; i++)
        {
            var target = CompanionOverhaulTargeting.MostAuras(CombatState);
            if (target == null) return;

            var dealt = SimDamagePipeline.DealerMods(
                Owner, CompanionOverhaulLaw.IsotomaDamage);
            await CreatureCmd.Damage(
                choiceContext, target,
                (int)SimDamagePipeline.TargetMods(target, dealt),
                ValueProp.Unpowered, dealer: null, cardSource: null,
                cardPlay: null);
            await CreatureCmd.GainBlock(
                Owner, CompanionOverhaulLaw.IsotomaBlock,
                ValueProp.Unpowered, null, fast: true);
        }
    }
}

/// <summary>
/// THE OVERHAUL'S END-OF-TURN ORDER, made explicit -- EB-19/races-c applied to
/// this arm. One broadcast tenant drives all six end-of-turn powers in the
/// sim's sequence, so a deck holding two of them cannot have its reactions, or
/// every later roll off <c>Rng.CombatTargets</c>, decided by listener
/// iteration order.
///
/// THE SEQUENCE IS tier0 `effects.player_turn_end_triggers`, read top to
/// bottom, in the block this arm appends after the shipped chain:
///
///     mc_glacial_waltz     (Cryo volley, one target)
///     mc_oz                (Electro volley, one target per stack)
///     mc_lightning_rose    (Electro volley + Vulnerable, one target)
///     mc_grand_ode         (Anemo Swirl, every enemy)
///     mc_dandelion_breeze  (Anemo Swirl on the aura-bearer, then Block)
///     mc_isotoma_bloom     (unelemented damage on the aura-bearer, then Block)
///     mc_revelation        (the latch, LAST -- see RevelationPower)
///
/// The latch is last on purpose: two of the six GRANT Block, and Nicole's
/// question is whether the player ended the turn holding any.
///
/// AfterSideTurnEnd, NOT Before. <see cref="TurnEndSequencer"/> owns
/// BeforeSideTurnEnd and drives the four shipped tenants there, so running
/// here puts this arm's block strictly after the shipped chain -- which is
/// exactly where tier0 puts it. The one other AfterSideTurnEnd tenant is
/// <see cref="WitchsFlamePower"/>, and Durin's Witch's Flame is one of the
/// seventeen Mondstadt rows this arm takes out of the pool, so with the arm on
/// it cannot be drafted and the co-tenancy cannot arise. Stated rather than
/// assumed: if a later slice puts that row back, this comment is the note that
/// says the two now share a broadcast.
/// </summary>
public sealed class CompanionOverhaulTurnEnd : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static CompanionOverhaulTurnEnd? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<CompanionOverhaulTurnEnd>(
            ModelDb.GetId<CompanionOverhaulTurnEnd>());
        yield return _instance;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;

        // Per CREATURE, not per step: each player-side creature runs the whole
        // sequence before the next one does, the reading that makes a solo
        // table byte-identical to the one-seat sim (TurnEndSequencer's own
        // argument, made once more here).
        foreach (var creature in participants.ToList())
        {
            if (creature.Player == null) continue;

            foreach (var waltz in creature.Powers.OfType<GlacialWaltzPower>().ToList())
            {
                await waltz.FireVolley(choiceContext);
            }
            foreach (var oz in creature.Powers.OfType<MondstadtOzPower>().ToList())
            {
                await oz.FireVolley(choiceContext);
            }
            foreach (var rose in creature.Powers.OfType<LightningRosePower>().ToList())
            {
                await rose.FireVolley(choiceContext);
            }
            foreach (var ode in creature.Powers.OfType<GrandOdePower>().ToList())
            {
                await ode.FireVolley(choiceContext);
            }
            foreach (var breeze in creature.Powers.OfType<DandelionBreezePower>().ToList())
            {
                await breeze.FireVolley(choiceContext);
            }
            foreach (var bloom in creature.Powers.OfType<SolarIsotomaBloomPower>().ToList())
            {
                await bloom.FireVolley(choiceContext);
            }
            foreach (var rev in creature.Powers.OfType<RevelationPower>().ToList())
            {
                rev.NoteEndOfTurn();
            }
        }
    }
}
