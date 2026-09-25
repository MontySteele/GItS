using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE POOL EXPANSION's Bomb verbs (R276), kept beside the arm's rules rather
/// than inside them: every method here is one card's clause, written on the
/// same primitives the rest of <see cref="ProtoBombPower"/> uses
/// (<see cref="Place"/>, <see cref="SetOff"/>, <see cref="LargestCharge"/>,
/// <see cref="DealCardDamage"/>), so a card cannot express a second reading of
/// "your largest Bomb" or of "a hit". Each command-issuing verb has a PURE
/// half a headless pin can read; the command half is structural, on the
/// README's terms. Sim twins: <c>tier0/engine/klee_overhaul.py</c>, the R276
/// block.
/// </summary>
public sealed partial class ProtoBombPower
{
    // ---- the pure reads -----------------------------------------------

    /// <summary>Does <paramref name="enemy"/> hold a MINE that
    /// <paramref name="applier"/> placed? Mine, All Mine!'s question, and
    /// <see cref="HoldsChargeFrom"/>'s twin one flag narrower. PURE.</summary>
    public static bool HoldsMineFrom(Creature enemy, Creature applier)
    {
        foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier == applier && pile.MineCount > 0) return true;
        }
        return false;
    }

    /// <summary>The living enemies holding one of her Mines, in board order:
    /// the bodies Mine, All Mine! hits. PURE.</summary>
    public static List<Creature> MinedEnemies(
        IEnumerable<Creature> enemies, Creature applier) =>
        enemies.Where(e => !e.IsDead && HoldsMineFrom(e, applier)).ToList();

    /// <summary>The living enemies holding one of her Bombs, read ONCE before
    /// the first hit -- Fish Fry's rider, the shipped `bonus_vs_bombed`
    /// snapshot rule (R72): a hit cannot change who is owed the bonus. PURE.
    /// </summary>
    public static HashSet<Creature> BombedEnemies(
        IEnumerable<Creature> enemies, Creature applier) =>
        enemies.Where(e => !e.IsDead && HoldsChargeFrom(e, applier))
               .ToHashSet();

    /// <summary>The size of her single largest Bomb on the living board, 0 if
    /// she has none -- <see cref="LargestCharge"/>'s read, exposed. PURE.
    /// </summary>
    public static int LargestSizeFor(Creature applier) =>
        LargestCharge(applier).Size;

    /// <summary>Sparks 'n' Splash's pick (2026-09-25): her single largest
    /// Bomb on the living board and the enemy it is on, (null, 0) if she has
    /// none. <see cref="LargestCharge"/>'s read, so the tie-break is the same
    /// first-found one every "your largest Bomb" card takes. PURE. Sim twin:
    /// <c>klee_overhaul.largest_charge</c>.</summary>
    public static (Creature? Enemy, int Size) LargestBombFor(Creature applier)
    {
        var (pile, _, size) = LargestCharge(applier);
        return pile == null || size <= 0 ? (null, 0) : (pile.Owner, size);
    }

    // ---- the pure mutations (no commands, nothing that can kill) -------

    /// <summary>
    /// Grow her single largest Bomb by <paramref name="amount"/> and return
    /// its NEW size, 0 if she has no Bomb. PURE.
    ///
    /// ONE READING OF "YOUR LARGEST BOMB": <see cref="LargestCharge"/>'s,
    /// which All of My Treasures!, Split Charge and Stoke the Fuse already
    /// share -- the largest single charge on the living board, the FIRST one
    /// found on a tie (enemies in board order, each pile in placement order,
    /// so the older of two equal charges in one pile). The growth lands
    /// through <see cref="GrowLargestChargeBy"/>, whose own tie-break is the
    /// same first-found one, so the charge measured is the charge grown.
    /// </summary>
    public static int GrowLargest(Creature applier, int amount)
    {
        var (pile, _, size) = LargestCharge(applier);
        if (pile == null || size <= 0) return 0;
        var index = pile.GrowLargestChargeBy(amount);
        return index < 0 ? 0 : pile._charges[index].Size;
    }

    /// <summary>
    /// Half a Mountain: her largest Bomb's CURRENT size, times
    /// <paramref name="factor"/>. Returns the new size, 0 if she has none.
    /// PURE, and repeatable -- a second copy doubles the doubled Bomb.
    /// </summary>
    public static int MultiplyLargest(Creature applier, int factor)
    {
        var size = LargestSizeFor(applier);
        if (size <= 0 || factor <= 1) return size;
        return GrowLargest(applier, size * (factor - 1));
    }

    /// <summary>
    /// Spinning Sparkler's per-hit growth: THIS enemy's largest charge of hers
    /// grows by <paramref name="amount"/>. "That Bomb" is the enemy's joined
    /// Bomb, so one charge takes the growth -- the largest, first on a tie --
    /// and the pile's total rises by exactly the printed number. Returns
    /// whether anything grew. PURE.
    /// </summary>
    public static bool GrowLargestOn(Creature? enemy, Creature applier, int amount)
    {
        if (enemy == null || amount <= 0) return false;
        ProtoBombPower? best = null;
        foreach (var pile in enemy.Powers.OfType<ProtoBombPower>())
        {
            if (pile.Applier != applier || pile._charges.Count == 0) continue;
            if (best == null || pile.LargestSize > best.LargestSize) best = pile;
        }
        if (best == null) return false;
        best.GrowLargestChargeBy(amount);
        return true;
    }

    /// <summary>Second Surprise's Bomb: half a Mine's size, rounded down.
    /// PURE, and 0 means "place nothing".</summary>
    public static int HalfOf(int size) => size <= 0 ? 0 : size / 2;

    // ---- the command halves -------------------------------------------

    /// <summary>
    /// Place a charge on <paramref name="target"/>, or -- if it has died --
    /// on a random OTHER living enemy, which is rule 3's jump applied to a
    /// charge that was on its way there. Nothing is placed when no enemy is
    /// left. The one door Mk.III's per-hit Bomb and Second Surprise's half
    /// both take, so a kill never parks a charge on a corpse.
    /// </summary>
    public static async Task PlaceOrJump(
        PlayerChoiceContext choiceContext, Creature target, int size,
        bool isMine, Creature applier, CardModel? cardSource)
    {
        if (size <= 0) return;
        if (!target.IsDead)
        {
            await Place(choiceContext, target, size, isMine, payloadMineAll: 0,
                        applier, cardSource);
            return;
        }
        var combat = applier.CombatState;
        if (combat == null) return;
        var candidates = combat.HittableEnemies
            .Where(e => e != target && !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (dest == null) return;
        await Place(choiceContext, dest, size, isMine, payloadMineAll: 0,
                    applier, cardSource);
    }

    /// <summary>
    /// Jumpy Dumpty Mk.III: "Deal N damage to a random enemy M times. Each hit
    /// places a Bomb S on that enemy." Each hit rolls a fresh random LIVING
    /// enemy, lands as her own Attack hit (<see cref="DealCardDamage"/>, so
    /// Strength, Vulnerable and the Pyro cadence apply), and then plants on
    /// the body it hit -- where the charge JOINS any pile of hers already
    /// there, which is what <see cref="Place"/> always does. A hit that kills
    /// sends its Bomb to a survivor (<see cref="PlaceOrJump"/>).
    /// </summary>
    public static async Task HitRandomAndPlant(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage, int hits,
        int size)
    {
        var combat = applier.CombatState;
        if (combat == null) return;
        for (var i = 0; i < hits; i++)
        {
            var living = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
            if (living.Count == 0) return;
            var target = combat.RunState.Rng.CombatTargets.NextItem(living);
            if (target == null) return;
            await DealCardDamage(choiceContext, target, damage, cardSource,
                                 cardPlay);
            await PlaceOrJump(choiceContext, target, size, isMine: false,
                              applier, cardSource);
        }
    }

    /// <summary>
    /// Spinning Sparkler: "Deal N damage twice. Each hit on an enemy with a
    /// Bomb grows that Bomb by G." A PLAIN Attack -- it never Sets off -- and
    /// the growth is read per hit, after the hit lands, off the enemy it hit
    /// (<see cref="GrowLargestOn"/>). A hit that kills grows nothing: the
    /// Bombs are about to jump, and they jump at the size they had.
    /// </summary>
    public static async Task HitAndGrow(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage, int hits,
        int grow)
    {
        if (target == null) return;
        for (var i = 0; i < hits; i++)
        {
            if (target.IsDead) return;
            await DealCardDamage(choiceContext, target, damage, cardSource,
                                 cardPlay);
            if (!target.IsDead) GrowLargestOn(target, applier, grow);
        }
    }

    /// <summary>Mine, All Mine!: "Deal N damage to each enemy with a Mine."
    /// The bodies are read ONCE, before the first hit (<see cref="MinedEnemies"/>),
    /// and a plain hit sets nothing off, so no hit can change who is hit.
    /// </summary>
    public static async Task HitMined(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage)
    {
        var combat = applier.CombatState;
        if (combat == null) return;
        foreach (var enemy in MinedEnemies(combat.HittableEnemies.ToList(),
                                           applier))
        {
            await DealCardDamage(choiceContext, enemy, damage, cardSource,
                                 cardPlay);
        }
    }

    /// <summary>Fish Fry: "Deal N damage to ALL enemies, and B more to each
    /// enemy with a Bomb." One hit per enemy, the bonus folded into that
    /// enemy's hit, the bombed set read ONCE before the first hit
    /// (<see cref="BombedEnemies"/>).</summary>
    public static async Task HitAllBombedBonus(
        PlayerChoiceContext choiceContext, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage, decimal bonus)
    {
        var combat = applier.CombatState;
        if (combat == null) return;
        var enemies = combat.HittableEnemies.ToList();
        var bombed = BombedEnemies(enemies, applier);
        foreach (var enemy in enemies)
        {
            if (enemy.IsDead) continue;
            var amount = damage + (bombed.Contains(enemy) ? bonus : 0m);
            await DealCardDamage(choiceContext, enemy, amount, cardSource,
                                 cardPlay);
        }
    }

    /// <summary>
    /// Team Effort's widened arm: "If you played a Companion card this turn,
    /// Set off ALL enemies instead." Every enemy's Bombs go off, one enemy at a
    /// time and before the damage (Tinder Toss's order), and the card's own
    /// hit then lands on the AIMED enemy only. One Set off CARD, noted once
    /// (<see cref="SetOffAimed"/>'s note, taken here for the same reason).
    /// </summary>
    public static async Task SetOffAllThenHit(
        PlayerChoiceContext choiceContext, Creature? target, Creature applier,
        CardModel cardSource, CardPlay cardPlay, decimal damage)
    {
        KleeOverhaulLedger.For(applier).NoteSetOffCardPlayed(cardSource);
        var badge = await BoomBadgePower.Spend(applier);
        var combat = applier.CombatState;
        if (combat == null) return;
        foreach (var enemy in combat.HittableEnemies.ToList())
        {
            if (enemy.IsDead) continue;
            await SetOff(choiceContext, enemy, applier, cardSource, badge: badge);
        }
        if (target == null) return;
        await DealCardDamage(choiceContext, target, damage, cardSource,
                             cardPlay);
    }

    /// <summary>
    /// One More Charge and Treasure Map: her largest Bomb grows by
    /// <paramref name="amount"/>; with a bar, the grown Bomb is measured
    /// AFTER the growth ("if it is NOW 20 or more") and a draw is paid. No
    /// Bomb, no growth and no draw.
    /// </summary>
    public static async Task GrowLargestBy(
        PlayerChoiceContext choiceContext, Player? player, int amount,
        int drawIfAtLeast, int draw)
    {
        var klee = player?.Creature;
        if (player == null || klee == null) return;
        var grown = GrowLargest(klee, amount);
        var cards = DrawsAfterGrowth(grown, drawIfAtLeast, draw);
        if (cards > 0) await CardPileCmd.Draw(choiceContext, cards, player);
    }

    /// <summary>One More Charge's bar: the cards a growth to
    /// <paramref name="grown"/> pays against a bar of
    /// <paramref name="drawIfAtLeast"/> -- "if it is now 20 or more, draw 1
    /// card". No Bomb grew (0) or no bar, no draw. PURE.</summary>
    public static int DrawsAfterGrowth(int grown, int drawIfAtLeast, int draw) =>
        drawIfAtLeast > 0 && draw > 0 && grown > 0 && grown >= drawIfAtLeast
            ? draw : 0;
}
