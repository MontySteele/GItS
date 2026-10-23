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
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Alice's Recipe (reworked 2026-10-11; [USER]: "Every bomb you place makes
/// every other bomb grow by 2 - an exponential ramp - upgrade raises the
/// effect to 3", then "let's make it affect both"): "Whenever you place a
/// Bomb or Mine, your other Bombs and Mines grow by 2." Stacks are the growth,
/// so two copies add.
///
/// PLACEMENT ONLY. <c>ProtoBombPower.Place</c> calls <see cref="GrowBeforePlacement"/>
/// unless the charge is <c>relocated</c> -- a jump, Exquisite Compound's move
/// and Alice's Masterpiece's remnant carry a charge that was already placed.
/// A card that places on ALL enemies reaches <c>Place</c> once per charge, so
/// it counts once per charge. The growth runs BEFORE the new charge lands,
/// which is what makes it "your OTHER Bombs" without having to find the new
/// one again. Growing places nothing, so it cannot re-trigger itself.
/// Sim twin: <c>klee_overhaul.place</c>'s <c>relocated</c> branch.
/// </summary>
public sealed class AlicesRecipePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Recipe"),
        ("description",
            "Whenever you place a [gold]Bomb[/gold], your other "
          + "[gold]Bombs[/gold] grow by [blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The growth one placement pays, 0 without the power.</summary>
    public static int GrowthFor(Creature? applier) =>
        applier?.Powers.OfType<AlicesRecipePower>().Sum(p => p.Amount) ?? 0;

    /// <summary>
    /// Grow every charge <paramref name="applier"/> already has out, on any
    /// enemy, Mines included, by the Recipe's stacks. PURE: no command, no
    /// placement, nothing that can go off. Called by <c>ProtoBombPower.Place</c>
    /// before a fresh (not relocated) charge lands.
    /// </summary>
    public static void GrowBeforePlacement(Creature applier)
    {
        var amount = GrowthFor(applier);
        var combat = applier.CombatState;
        if (amount <= 0 || combat == null) return;
        foreach (var enemy in combat.Enemies.ToList())
        {
            ProtoBombPower.GrowOn(enemy, applier, amount);
        }
    }
}

/// <summary>
/// Chained Reactions: "Whenever one of your Bombs goes off, your other Bombs
/// grow 3." The Rare that makes a Spray board feed itself.
///
/// REWORKED 2026-09-27 after [USER]'s co-op run ("very OP"). It used to place a
/// Bomb 3 per explosion, which replaced every Bomb it popped: the board never
/// drained, and every Set off paid a Spark per Bomb, run after run. Growing the
/// Bombs already down creates none, so a board empties as it is fired.
///
/// It rides the explosion bus rather than the card, so one Set off on a
/// three-Bomb pile is three growths. A Set off takes its whole pile before any
/// of it goes off, so the growth lands on Bombs elsewhere, never on the ones
/// firing with it. Nothing fires by itself (rule 7): this grows, it does not
/// detonate.
/// </summary>
public sealed class ChainedReactionsPower
    : PowerModel, ILocalizationProvider, IProtoExplosionListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Chained Reactions"),
        ("description",
            "Whenever one of your [gold]Bombs[/gold] goes off, your "
          + "[gold]Bombs[/gold] still waiting grow by [blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (applier != Owner) return Task.CompletedTask; // co-op: your bombs only
        var combat = applier.CombatState;
        if (combat == null) return Task.CompletedTask;

        foreach (var enemy in combat.HittableEnemies.Where(e => !e.IsDead).ToList())
        {
            ProtoBombPower.GrowOn(enemy, applier, Amount);
        }
        return Task.CompletedTask;
    }
}

/// <summary>
/// Witches' Circle (R244, R276): "Whenever you play a Companion card, place a
/// Bomb 3 on a random enemy."
///
/// CHAINED REACTIONS' SHAPE WITH A RARER TRIGGER. The stack is the Bomb SIZE,
/// so a second copy is a second Bomb per Companion play, and the printed
/// number is the row's -- which is what lets its declared
/// <c>power_amount</c> delta move it.
///
/// R276 pick 2 WIDENED THE TRIGGER from the retired Hexerei mark to any
/// Companion card, because under the arm Klee starts with no companion and a
/// reader that waited on two lucky offers rarely fired. Alice's Introduction
/// Magic still widens it for a turn, through the one question every reader
/// asks (<c>CompanionHexerei.CountsAsCompanion</c>).
///
/// IT HOOKS ITSELF, like <see cref="LadderOfAscentPower"/> and unlike this
/// arm's explosion listeners: <c>AfterCardPlayed</c> reaches a power the card
/// just applied.
///
/// THE BOMB IS PLACED THROUGH THE SAME <c>Place</c> every other source uses, so
/// it registers, can be set off and can jump -- and, being a plain Bomb rather
/// than a Mine, it cannot answer an attack by itself. Nothing fires by itself
/// (rule 7): this places, it does not detonate. Sim twin:
/// <c>klee_overhaul.note_companion_played</c>.
/// </summary>
public sealed class WitchesCirclePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Little Hexenzirkel"),
        ("description",
            "Whenever you play a [gold]Companion[/gold], place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;   // co-op: yours
        if (!CompanionHexerei.CountsAsCompanion(cardPlay.Card)) return;
        var combat = Owner.CombatState;
        if (combat == null) return;

        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (dest == null) return;

        await ProtoBombPower.Place(choiceContext, dest, Amount, isMine: false,
                                   payloadMineAll: 0, Owner, cardSource: null);
    }
}

/// <summary>
/// Explosive Frags (R276): "Whenever a Mine goes off, apply 2 Vulnerable to
/// that enemy."
///
/// READ AT THE ONE SITE A CHARGE GOES OFF (<c>ProtoBombPower.Explode</c>),
/// after the Mine's own hit, so the Vulnerable is on the enemy for whatever
/// comes next and never for the Mine that applied it. ANY Mine of hers, and
/// whatever set it off: the enemy's attack or a card's Set off. The stack is
/// the Vulnerable, so a second copy applies twice as much and the upgrade
/// moves it. A corpse takes nothing. Sim twin: <c>klee_overhaul.MINE_FRAGS</c>.
///
/// NOT THE SHIPPED <see cref="DetonationVulnPower"/>, which answers a shipped
/// Bomb's detonation; this one answers the arm's Mine and nothing else.
/// </summary>
public sealed class MineFragsPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosive Frags"),
        ("description",
            "Whenever a [gold]Mine[/gold] goes off, apply "
          + "[blue]{Amount}[/blue] [gold]Vulnerable[/gold] to that enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>One of <paramref name="applier"/>'s Mines just went off on
    /// <paramref name="target"/>: every copy of the power applies its
    /// stack.</summary>
    public static async Task OnMineWentOff(
        PlayerChoiceContext choiceContext, Creature applier, Creature target)
    {
        foreach (var frags in applier.Powers.OfType<MineFragsPower>().ToList())
        {
            if (target.IsDead || frags.Amount <= 0) return;
            await PowerCmd.Apply<VulnerablePower>(
                choiceContext, target, frags.Amount, applier: applier,
                cardSource: null);
        }
    }
}

/// <summary>
/// Sparks 'n' Splash: "At the start of your turn, your largest Bomb deals its
/// size in Pyro damage without going off."
///
/// RE-TIMED 2026-09-25 (the afternoon seat round, both seats). At the END of
/// the turn it fired after Klee had already set her Bombs off, so it hit for
/// nothing, and the Opus seat named it its never-again. At the START of the
/// turn, after rule 1's growth, the Bombs it reads are the ones she is about
/// to decide over. The history before this (the R250 largest-not-sum move,
/// [USER]'s 2026-09-02 "take damage equal to the Bomb on them" design, the
/// auto-detonation it replaced) is in git.
///
/// WHICH BOMB: her single largest charge on the living board, the FIRST one
/// found on a tie -- <see cref="ProtoBombPower.LargestBombFor"/>, which is the
/// one reading of "your largest Bomb" All of My Treasures!, Split Charge and
/// Stoke the Fuse share. It hits the enemy the Bomb is on.
///
/// IT READS THE PILE AND DOES NOT SPEND IT. The Bomb stays where it is and
/// keeps growing, and nothing goes off, so: no Spark (rule 4 pays per
/// explosion), no Mine answers, no explosion bus, no "whenever a Bomb goes
/// off" reader, and neither of rule 7's counters moves.
///
/// THE BOMB'S OWN DAMAGE TERMS (<see cref="ElementalHit.DealWithoutDealerMods"/>,
/// the door <c>Explode</c> uses): Pyro, the target's Vulnerable and HP cap,
/// the aura and the reaction -- and not Klee's Strength or Weak, because the
/// number it pays is a Bomb's size. Not an Attack: no card is being played.
///
/// WHEN: <c>AfterPlayerTurnStart</c>, strictly after the growth at
/// <c>BeforeSideTurnStart</c>, and through the arm's ONE turn-start sequencer
/// (<see cref="KleeExpansion.RunTurnStartPlacements"/>), which runs the echo
/// FIRST and only then Klee's Secret Base and Dodoco -- so it reads the board
/// as the growth left it, whatever order the broadcast visits the powers in.
///
/// EACH COPY IS ITS OWN HIT (`EB-358`): the sequencer loops
/// <see cref="PowerModel.Amount"/> times, re-reading the largest Bomb each
/// time, so a first hit that kills sends that enemy's Bombs jumping (the
/// death sweep) before the second copy looks.
///
/// Sim twin: <c>klee_overhaul.bomb_echo</c>, called first in
/// <c>_turn_start_expansion</c>.
/// </summary>
public sealed class BombEchoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "At the start of your turn, your largest [gold]Bomb[/gold] deals its "
          + "size in [gold]Pyro[/gold] damage without going off."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        await KleeExpansion.RunTurnStartPlacements(choiceContext, player);
    }

    /// <summary>
    /// The echo itself, <paramref name="copies"/> hits. Called by the
    /// sequencer, never by the broadcast. An explicit loop with ONE damage
    /// call site, read fresh each pass (`EB-358`).
    /// </summary>
    internal static async Task Fire(
        PlayerChoiceContext choiceContext, Creature klee, int copies)
    {
        // TELEMETRY ONLY: the echo pays a Bomb's size on a Bomb's terms.
        using var credit = Diagnostics.DamageCredit.Open(
            klee, Diagnostics.DamageCredit.Bomb, "Bomb");
        for (var copy = 0; copy < copies; copy++)
        {
            var (target, size) = ProtoBombPower.LargestBombFor(klee);
            if (target == null || size <= 0) return;
            await ElementalHit.DealWithoutDealerMods(
                choiceContext, target, Element.Pyro, size, klee);
            await ProtoBombPower.SweepJumps(choiceContext, klee.CombatState);
        }
    }
}

/// <summary>
/// Vermillion Pact (the pool pass, `EB-491`; reworked 2026-09-27): "When a Set
/// off makes one of your Bombs react, every other Bomb it sets off reacts with
/// the same aura." A rule-breaking Rare: the shared "one aura, consumed by the
/// first hit" rule is broken for one Set off's pile and nowhere else.
///
/// THE RULE LIVES IN <see cref="ProtoBombPower.SetOff"/>'s loop, and this class
/// holds its two halves: <see cref="Holds"/>, read once per take, and
/// <see cref="Restore"/>, which puts the first consumed aura back before each
/// later charge of the same take. The aura goes up through the ordinary front
/// door (<see cref="AuraCmd.Apply"/>), so each restored reaction is a real one
/// for every counter and listener. Nothing carries past the take, so the Set
/// off card's own hit finds the aura spent -- the pre-rework "the Attack that
/// Set it off reacts too" is gone. A Mine answering an intent is not a Set off
/// and never reaches the loop; Pocket Match's single charge has no later
/// charge to feed.
///
/// DEAD ALONE, like Witches' Circle beside it (R244 pick 2): a deck with no
/// applier in it never puts a foreign aura up, and this Power then never fires.
/// That is the card, not a defect.
///
/// STACKS DO NOTHING. The rule is a fact about the board, not a number, so a
/// second copy adds no second aura -- the Counter is how the badge counts
/// copies, exactly as <c>AlicesRecipePower</c>'s is. Sim twin:
/// <c>klee_overhaul.VERMILLION_PACT</c>, read in <c>klee_overhaul.set_off</c>.
/// </summary>
public sealed class VermillionPactPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparkborne Magic"),
        ("description",
            "Whenever a [gold]Set off[/gold] makes one of your [gold]Bombs[/gold] "
          + "react, every other [gold]Bomb[/gold] in that [gold]Set off[/gold] "
          + "reacts with the same aura."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// Does the Set off's owner hold the Pact? The pile a Set off takes is
    /// <paramref name="applier"/>'s own (R205), so in co-op only the Pact
    /// owner's Bombs are ever fed.
    /// </summary>
    public static bool Holds(Creature applier)
        => applier.Powers.OfType<VermillionPactPower>().Any();

    /// <summary>
    /// Put the Pact's aura back before the next charge of the same take goes
    /// off. IT REFUSES A BOARD THAT ALREADY HOLDS ONE (the one-aura invariant
    /// <see cref="AuraCmd.Apply"/>'s own doc states) and a corpse. Sim twin:
    /// <c>klee_overhaul._pact_restore</c>.
    /// </summary>
    public static async Task Restore(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        Element aura)
    {
        if (aura == Element.None || target.IsDead) return;
        if (AuraCmd.Find(target) != null) return;
        await AuraCmd.Apply(choiceContext, target, aura, applier,
                            cardSource: null);
    }
}

/// <summary>
/// POOL PASS TWO (`EB-732`). Return to Sender: "Gain 8 Block. This turn,
/// damage this Block absorbs is placed on the attacker as a Bomb."
///
/// AMOUNT IS A MARK ON THE BLOCK POOL, and this class is
/// <see cref="IcyPawsPower"/>'s construction with a charge on the attacker
/// instead of an aura. The engine has ONE Block pool, so "this Block" cannot be
/// a separate pile: the power records how much of the standing Block the card
/// put there, a hit that spends Block spends the mark with it, and the mark is
/// clamped to the standing Block on the way in. Marked-Block-eaten-FIRST, which
/// is the conservative reading (R212's one-way rule) -- the rider fires on
/// FEWER hits than marked-last would, and a single pool cannot say which coin
/// was spent.
///
/// THE CHARGE IS CAPPED AT THE ALLOWANCE (`EB-749`, R271 sec.5.2), and the
/// allowance is the Block THIS CARD granted -- 8, or 11 upgraded, and whatever
/// a Block modifier made of that grant. It is ONE allowance spent across every
/// hit of the turn and never an independent cap per hit: an 8-mark eating a 20
/// plants 8 and is spent, and two hits of 6 into the same 8-mark plant 6 and
/// then 2. The face keeps "this Block" and is now true, which is the whole of
/// what the repair is for.
///
/// "THIS TURN" NEEDS NO TIMER, and that is the point of riding the mark: Block
/// is cleared at the start of Klee's next turn and
/// <see cref="AfterPlayerTurnStart"/> removes a mark with nothing behind it, so
/// the rider lives exactly one enemy turn per play.
///
/// THE BOMB IS AN ORDINARY PLANT and mints nothing by itself. Rule 4 mints a
/// Spark per EXPLOSION and nothing has gone off here; the charge grows, jumps
/// and is Set off exactly as any other of hers does.
///
/// FIRED BY <see cref="CompanionOverhaulIncomingHit"/>, not by a broadcast of
/// its own -- the three incoming readers already share one listener, and
/// `blocked` exists nowhere else. Sim twin: <c>klee_overhaul.block_absorbed</c>,
/// called from <c>effects.companion_overhaul_block_absorbed</c>.
/// </summary>
public sealed class ReturnToSenderPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Return to Sender"),
        // THE STATIC (compendium) ROW CARRIES NO VAR TOKEN -- `EB-353`'s
        // finding on Thoma's twin, and this power is that construction:
        // `PowerModel.HoverTips` binds `DynamicVars` on the SMART branch alone,
        // so a token written here would reach the screen as a placeholder.
        // Text pass 2026-09-25: active voice, one sentence. The smart face
        // keeps its live `{Left}` ahead of it, the number the rider pays on.
        ("description",
            "This turn, damage your [gold]Block[/gold] absorbs becomes a "
          + "[gold]Bomb[/gold] on the attacker."),
        ("smartDescription",
            "[blue]{Left}[/blue] [gold]Block[/gold] left. This turn, damage "
          + "your [gold]Block[/gold] absorbs becomes a [gold]Bomb[/gold] on "
          + "the attacker."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[] { new BlockMarkVar() };

    /// <summary>The badge is the number the face prints (`EB-337`), which is
    /// the one the rider pays on.</summary>
    public override int DisplayAmount => BlockMark.Left(this);

    /// <summary>The housekeeping half, and the whole of the card's "this
    /// turn": <c>AfterPlayerTurnStart</c> runs after the block clear, so a mark
    /// with no Block behind it is gone before the player's first decision.
    /// Sim twin: the clamp at the head of
    /// <c>klee_overhaul.turn_start_late</c>.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await BlockMark.ClearIfSpent(this);
    }

    /// <summary>The hit is about to be absorbed. The caller owns the order;
    /// this owns the arithmetic.</summary>
    internal async Task Bounce(PlayerChoiceContext choiceContext,
                               Creature attacker, decimal amount)
    {
        // Block is NOT yet spent at BeforeDamageReceived (the Vigil's note in
        // KuragePowers.cs establishes it), so `Owner.Block` is the standing
        // Block and `min(Block, amount)` is exactly what will be absorbed --
        // the sim's `blocked = min(player.block, dmg)`.
        //
        // `payout: 0`, the paws' spelling: what this rider pays is a charge on
        // the attacker and not Block, so there is nothing to put back under the
        // mark and the spend is the marked-first one it always was.
        var standing = (int)Owner.Block;
        var absorbed = System.Math.Min(standing, (int)amount);
        var left = BlockMark.Absorb((int)Amount, standing, (int)amount,
                                    payout: 0);
        if (left == null) return;
        // `EB-749` (R271 sec.5.2). THE CHARGE IS CAPPED AT THE ALLOWANCE, and
        // the allowance is ONE, spent across every hit of the turn. The mark
        // already carried it -- `BlockMark.Absorb` shrinks it by whatever each
        // hit absorbed -- so the cap is the plant reading the mark instead of
        // the raw absorption: an 8-mark eating a 20 plants 8 and is spent, and
        // two hits of 6 into the same 8-mark plant 6 and then 2. The face's
        // "this Block" is now true, which is the repair the ruling names.
        //
        // `marked` AND NOT `Amount`: the mark is clamped to standing Block on
        // the way in (Block cleared under it leaves nothing to pay on), which
        // is `Absorb`'s own first line and the sim's `min(mark, block_before)`.
        var marked = System.Math.Min((int)Amount, standing);
        var charge = System.Math.Min(absorbed, marked);
        if (!attacker.IsDead && charge > 0)
        {
            await ProtoBombPower.Place(
                choiceContext, attacker, charge, isMine: false,
                payloadMineAll: 0, applier: Owner, cardSource: null);
        }
        if (left.Value > 0)
        {
            await PowerCmd.ModifyAmount(
                choiceContext, this, left.Value - (int)Amount,
                applier: Owner, cardSource: null, silent: true);
        }
        else
        {
            await PowerCmd.Remove(this);
        }
    }
}

/// <summary>
/// POOL PASS TWO (`EB-732`). Blazing Delight: "At the start of your turn, gain
/// 1 Energy and draw 1 card." The arm's first standing ENERGY engine.
///
/// THE SITE IS <c>AfterPlayerTurnStart</c>, which is <see cref="GroundedPower"/>
/// 's and for its reason: the energy reset and the turn's opening draw have
/// already happened there, so an Energy granted here survives the turn and a
/// card drawn here is drawn on TOP of the opening hand. At
/// <c>BeforeSideTurnStart</c> the reset would eat it.
///
/// AMOUNT IS A RATE, READ BY BOTH HALVES, so two copies pay 2 and 2 and the
/// upgrade's +1 moves both -- the face's own arithmetic and not a second rule.
/// A Counter, like every stacking Power in this arm.
///
/// UNCONDITIONAL, and rule 7 is not violated by it: rule 7 says nothing GOES
/// OFF by itself, which is about charges. A 2-energy Rare that cost 5 Sparks to
/// land pays every turn, and what it pays is tempo rather than an explosion.
///
/// Sim twin: the <c>BLAZING_DELIGHT</c> block in
/// <c>klee_overhaul.turn_start_late</c>, beside Grounded's.
/// </summary>
public sealed class BlazingDelightPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Blazing Delight"),
        ("description",
            "At the start of your turn, gain {Amount:energyIcons()} and draw "
          + "that many cards."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        var n = (int)Amount;
        if (n <= 0) return;
        await PlayerCmd.GainEnergy(n, player);
        await CardPileCmd.Draw(choiceContext, n, player);
    }
}
