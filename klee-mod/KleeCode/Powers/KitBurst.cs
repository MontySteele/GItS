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
/// Kit-Burst constants. LAW from tier0/constants.py -- mirrored verbatim,
/// never re-derived (R23 note, same discipline as BurstConstants).
/// </summary>
public static class KitBurstConstants
{
    /// <summary>tier0 SPARKS_N_SPLASH_HITS = 4 (end of turn: N hits...).</summary>
    public const int VolleyHits = 4;

    /// <summary>tier0 SPARKS_N_SPLASH_HIT_DMG = 5 (...of this damage, each applies pyro).</summary>
    public const int VolleyHitDamage = 5;
}

/// <summary>
/// Sparks 'n' Splash -- Klee's Elemental Burst as a power (v1.9: the Burst is
/// kit, not loot). Amount is turns remaining (sheet: 3).
///
/// Port of tier0 player_turn_end_triggers (effects.py): while active, at the
/// END of the player turn, 4 hits of 5 damage, each to a RANDOM living enemy,
/// each a full Pyro hit. The volley runs in BeforeSideTurnEnd, which maps to
/// Hook.BeforeTurnEnd -- fired before the hand flush (CombatManager), exactly
/// the sim's end-triggers-before-discard phase.
///
/// Each hit takes the SAME elemental pipeline as a bomb detonation
/// (BombPower.Detonate, R23): resolve the element FIRST (apply / refresh /
/// react -- Vaporize and Melt amplify the hit), then deal the damage
/// Unpowered with no card source. Unpowered + no source is also what keeps a
/// volley hit from early-detonating bombs: the sim's _detonate_bombs_on_hit
/// gates on source == "attack", and BombPower's early-pop listener demands a
/// powered attack from an Attack card. Reactions raised by the volley run the
/// normal funnel, so they grant burst energy and Catalytic bonuses -- the sim
/// routes volley hits through the very same resolve_hit.
///
/// Volley first, THEN tick down -- the sim decrements after the hits, so a
/// 3-stack power volleys exactly 3 times.
/// </summary>
public sealed class SparksNSplashPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "At the end of your turn, deal "
          + "5 damage to a random enemy 4 times, applying [gold]Pyro[/gold]. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    /// <summary>Counter with a manual end-of-turn tick, the AuraPower idiom:
    /// the tick must run AFTER the volley, so the power owns its own decay.</summary>
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner.Player == null) return;

        for (var i = 0; i < KitBurstConstants.VolleyHits; i++)
        {
            // Re-snapshot per hit: a hit can kill, and the sim re-picks from
            // living_enemies each iteration (break when none remain).
            var candidates = CombatState.HittableEnemies.ToList();
            if (candidates.Count == 0) break;
            var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target == null) break;

            // Sim parity: volley hits go through deal_damage_to_enemy, and
            // ElementalHit.Deal IS that pipeline (Strength/Weak pre-amp,
            // element resolve, Vulnerable post-amp, single truncation).
            await ElementalHit.Deal(
                choiceContext, target, Element.Pyro,
                KitBurstConstants.VolleyHitDamage, Owner);
        }

        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// The kit-grant machinery, port of tier0 grant_charged_kit (combat.py v1.9):
/// when the Burst meter is full, the kit card is granted to hand; casting
/// empties the meter, so a refill re-grants it.
///
/// Rules, verbatim from the sim:
///   - grant only at a full meter (resource >= 60; accrual is uncapped, the
///     check is >=);
///   - never a duplicate: a copy already in hand blocks the grant;
///   - a full hand DEFERS the grant to the next check, never drops it -- the
///     meter stays full, so the grant cannot be lost (the game's own
///     full-hand behavior for AddGeneratedCardToCombat is redirect-to-
///     discard, which for a kit card would recirculate the Burst as loot;
///     that is why the hand-size check lives HERE, before the add);
///   - the granted copy is fresh each time ("returns to the kit, no pile":
///     a played Power leaves combat entirely, and the next grant creates a
///     new instance).
///
/// Check sites (KleeElementalHooks): after the turn-start draw, after every
/// card played, and at turn end before the flush -- the sim's three
/// grant_charged_kit call sites. The sim's own argument for exhaustiveness
/// holds here too: every Klee-reachable gain fires inside those windows
/// (turn-start detonations land in BeforeSideTurnStart, card-driven gains
/// inside plays, the volley's reactions in BeforeSideTurnEnd), and mod-model
/// hooks run AFTER power hooks in the same broadcast, so a same-phase gain
/// is always visible to the check that follows it.
/// </summary>
public static class KitGrant
{
    /// <summary>
    /// Victim-pool filter for discard/exhaust-from-hand effects: kit cards
    /// are NEVER fodder (tier0 _op_discard/_op_exhaust_from, the v1.9
    /// invariant -- the Burst never enters a pile; a discarded kit card
    /// would recirculate as loot on reshuffle and defeat the hand-only
    /// dedup above). This discharges the forward obligation recorded in
    /// DECISIONS when the kit sprint landed: the FIRST discard op to ship
    /// C#-side carries the exemption (R36 Crackle / bright_idea unblock).
    /// </summary>
    public static bool NotKitCard(CardModel card) => card is not SparksNSplash;

    public static async Task GrantIfCharged(PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Character is not Klee) return;
        var playerCombatState = owner.PlayerCombatState;
        var combatState = owner.Creature.CombatState;
        if (playerCombatState == null || combatState == null) return;

        // Rules read the RESOURCE, never the badge (BurstResource invariant).
        var resource = CustomResources<KleeBurstResource>.Get(playerCombatState);
        if (resource.Amount < BurstConstants.KleeMax) return;

        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null) return;
        if (hand.Cards.Any(c => c is SparksNSplash)) return;
        if (hand.Cards.Count >= CardPile.MaxCardsInHand) return;  // defer, never drop

        var card = combatState.CreateCard<SparksNSplash>(owner);
        await CardPileCmd.AddGeneratedCardToCombat(card, PileType.Hand, owner);
    }
}
