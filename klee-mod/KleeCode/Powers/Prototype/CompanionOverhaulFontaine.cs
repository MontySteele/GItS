using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// THE FONTAINE POOL REWORK -- ITS POWERS AND ITS HELPERS (2026-10-19,
/// <c>review/active/fontaine-companions-2026-10-19.md</c>). The pool went from
/// sixteen cards to thirty (8 / 13 / 9): five kept, eleven rebuilt in place,
/// fourteen new, and five characters added (Wriothesley, Lyney, Sigewinne,
/// Escoffier, Emilie). Navia's rebuilt Cannon Fire Support stays in
/// <c>Powers/FontainePowers.cs</c> beside the other kept Rares.
///
/// EVERY POWER HERE WORKS FOR WHOEVER DRAFTS IT. None reads a character: each
/// asks only about its own owner (the creature it sits on), the board and the
/// owner's piles, so Klee, Kokomi, Varka, Furina and Yae hold the same card.
/// <c>FontaineCompanionReworkTests</c> sweeps every new card's closure for an
/// identity read, the off-character sweeps' question.
///
/// Sim twins: the `fontaine_*` readers in <c>tier0/engine/effects.py</c>.
/// </summary>
public static class FontaineCompanion
{
    /// <summary>
    /// Freminet, Shattering Pressure: "Each time you Retain this, it deals 5
    /// additional damage this combat." The flush names the cards it kept
    /// (<c>Hook.AfterFlush</c>'s <paramref name="retained"/>), so the card asks
    /// about itself. The var is the one the card's damage reads and its
    /// upgrade raises, so growth and upgrade add (`grow_damage`'s idiom), and
    /// the combat copy is what grows, so the deck card is untouched. Sim twin:
    /// `Card.retain_grow`, read at the flush in `combat._end_player_turn`.
    /// </summary>
    public static bool GrowOnRetain(
        CardModel card, DynamicVar damage,
        IReadOnlyCollection<CardModel> retained, int amount)
    {
        if (amount <= 0 || !retained.Contains(card)) return false;
        damage.BaseValue += amount;
        return true;
    }

    /// <summary>Sigewinne's Block: <paramref name="per"/> for each enemy the
    /// play reached. Pure, so the arithmetic is asserted headlessly.</summary>
    public static int BlockForHits(int per, int enemiesHit) =>
        per <= 0 || enemiesHit <= 0 ? 0 : per * enemiesHit;

    /// <summary>
    /// Sigewinne, Super-Saturated Syringing: "Gain 4 Block for each enemy
    /// hit." The enemies are the play's own
    /// (<see cref="CompanionOverhaulLedger.EnemiesHitThisPlay"/>, opened at the
    /// top of the card's body), so a kill counts and an enemy behind full Block
    /// counts. A card's own Block line, so it takes the printed-Block funnel
    /// (Dexterity, Frail), Gorou's <c>BlockHalfDamage</c> shape. Sim twin:
    /// `effects._op_block_per_enemy_hit`.
    /// </summary>
    public static async Task BlockPerEnemyHit(
        PlayerChoiceContext choiceContext, Creature owner, int per,
        CardPlay cardPlay)
    {
        var amount = BlockForHits(
            per, CompanionOverhaulLedger.For(owner).EnemiesHitThisPlay);
        if (amount <= 0) return;
        await CreatureCmd.GainBlock(
            owner, new BlockVar(amount, ValueProp.Move), cardPlay);
    }

    /// <summary>A random living, hittable enemy on <paramref name="owner"/>'s
    /// board, or null. One roll off the combat-targets stream, Neuvillette's.
    /// </summary>
    public static Creature? RandomEnemy(Creature owner)
    {
        var enemies = owner.CombatState?.HittableEnemies
            .Where(e => e.IsAlive).ToList();
        if (enemies == null || enemies.Count == 0) return null;
        var player = owner.Player;
        if (player == null) return enemies[0];
        return player.RunState.Rng.CombatTargets.NextItem(enemies);
    }

    /// <summary>
    /// Emilie's choice of victim: the Hand's Statuses and Curses first, then
    /// the Draw Pile's, and a random one of whichever is not empty. Pure over
    /// the two lists, so the order is asserted headlessly.
    /// </summary>
    public static IReadOnlyList<CardModel> JunkPool(
        IEnumerable<CardModel>? hand, IEnumerable<CardModel>? drawPile)
    {
        var inHand = (hand ?? Enumerable.Empty<CardModel>())
            .Where(KokomiResources.IsJunk).ToList();
        if (inHand.Count > 0) return inHand;
        return (drawPile ?? Enumerable.Empty<CardModel>())
            .Where(KokomiResources.IsJunk).ToList();
    }
}

/// <summary>
/// Lyney, Grin-Malkin Hat (Uncommon Power, 1): "Whenever you Exhaust a card,
/// deal 4 [6] Pyro damage to a random enemy." Any card of the owner's that
/// is Exhausted, by a card, by the Exhaust keyword or by Ethereal: Feel No
/// Pain's reading of the same verb. Amount IS the damage, so copies add. The
/// hit is the arm's power-sourced Pyro hit (<see cref="ElementalHit.Deal"/>),
/// so it lays Pyro and reacts. Sim twin: `mf_grin_malkin_hat` in
/// `refpowers.exhaust_card`.
/// </summary>
public sealed class GrinMalkinHatPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grin-Malkin Hat"),
        ("description",
            "Whenever you [gold]Exhaust[/gold] a card, deal "
          + "[blue]{Amount}[/blue] [gold]Pyro[/gold] damage to a random "
          + "enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Is <paramref name="card"/> one this power answers? Pure.
    /// </summary>
    public static bool Answers(Creature owner, CardModel? card) =>
        card?.Owner?.Creature == owner;

    public override async Task AfterCardExhausted(
        PlayerChoiceContext choiceContext, CardModel card,
        bool causedByEthereal)
    {
        if (Owner == null || Owner.IsDead || Amount <= 0) return;
        if (!Answers(Owner, card)) return;
        var target = FontaineCompanion.RandomEnemy(Owner);
        if (target == null) return;
        Flash();
        await ElementalHit.Deal(
            choiceContext, target, Element.Pyro, Amount, Owner);
    }
}

/// <summary>
/// Sigewinne, Rebound Hydrotherapy (Uncommon Power, 1): "At the start of your
/// turn, gain 3 [4] Block and apply Hydro to a random enemy." Amount IS the
/// Block, so copies add; the Hydro is one application a turn, whatever the
/// stack (a second application of the same aura only refreshes it). Raw
/// Block, as every power-sourced Block in the arm (NC-11). The Hydro is
/// <see cref="ElementalHit.ApplyOnly"/>, Barbara's Melody Loop's door, so it
/// reacts with an aura already there. Sim twin: `mf_rebound_hydrotherapy`
/// in `effects.player_turn_start_triggers`.
/// </summary>
public sealed class ReboundHydrotherapyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Rebound Hydrotherapy"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Block[/gold] and apply [gold]Hydro[/gold] to a random "
          + "enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner || Amount <= 0) return;
        Flash();
        await CreatureCmd.GainBlock(
            Owner, Amount, ValueProp.Unpowered, null, fast: true);
        var target = FontaineCompanion.RandomEnemy(Owner);
        if (target == null) return;
        await ElementalHit.ApplyOnly(
            choiceContext, target, Element.Hydro, Owner);
    }
}

/// <summary>
/// Wriothesley, Chilling Penalty (Rare Power, 1): "Whenever you lose HP, deal
/// 5 [7] Cryo damage to a random enemy." Any HP its owner loses, to an enemy's
/// attack, to a card's own price (Balemoon Rising, Miracle Parade) or to a
/// power (Masque of the Red Death): <c>AfterDamageReceived</c> with HP gone,
/// Rupture's read without Rupture's card-play deferral. Once per loss, not per
/// HP. Amount IS the damage, so copies add. Sim twin: `mf_chilling_penalty`
/// in `resources.note_player_hp_loss`, the one HP-loss funnel there.
/// </summary>
public sealed class ChillingPenaltyPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Chilling Penalty"),
        ("description",
            "Whenever you lose HP, deal [blue]{Amount}[/blue] "
          + "[gold]Cryo[/gold] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does this hit pay? Pure: the owner lost HP and lives.</summary>
    public static bool Pays(Creature owner, Creature target, int hpLost) =>
        ReferenceEquals(owner, target) && hpLost > 0 && owner.IsAlive;

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (Owner == null || Amount <= 0) return;
        if (!Pays(Owner, target, result.UnblockedDamage)) return;
        var enemy = FontaineCompanion.RandomEnemy(Owner);
        if (enemy == null) return;
        Flash();
        await ElementalHit.Deal(
            choiceContext, enemy, Element.Cryo, Amount, Owner);
    }
}

/// <summary>
/// Emilie, Aromatic Explication (Rare Power, 1 [0]): "At the start of your
/// turn, Exhaust a Status or Curse from your Hand or Draw Pile. If you did,
/// gain 1 Energy." After the turn's draw (<c>AfterPlayerTurnStart</c>), so a
/// Wound just drawn is in the Hand. The Hand first, then the Draw Pile, a
/// random one of the first that holds any
/// (<see cref="FontaineCompanion.JunkPool"/>). Amount counts copies; each
/// copy takes one and pays one Energy. Sim twin: `mf_aromatic_explication`
/// in `effects.fontaine_turn_start_late`, at the same post-draw site.
/// </summary>
public sealed class AromaticExplicationPower : PowerModel, ILocalizationProvider
{
    public const int EnergyPerExhaust = 1;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Aromatic Explication"),
        ("description",
            "At the start of your turn, [gold]Exhaust[/gold] a Status or "
          + "Curse from your [gold]Hand[/gold] or [gold]Draw Pile[/gold]. If "
          + "you did, gain {energyPrefix:energyIcons(" + EnergyPerExhaust
          + ")}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner || Amount <= 0) return;
        for (var i = 0; i < (int)Amount; i++)
        {
            var pool = FontaineCompanion.JunkPool(
                CardPile.Get(PileType.Hand, player)?.Cards,
                CardPile.Get(PileType.Draw, player)?.Cards);
            if (pool.Count == 0) return;
            var victim = player.RunState.Rng.CombatTargets.NextItem(pool);
            if (victim == null) return;
            Flash();
            await CardCmd.Exhaust(choiceContext, victim);
            await PlayerCmd.GainEnergy(EnergyPerExhaust, player);
        }
    }
}
