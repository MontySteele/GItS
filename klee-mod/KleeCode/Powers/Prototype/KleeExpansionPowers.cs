using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// THE POOL EXPANSION's Powers (R276), QUARANTINED with the rest of
// `Powers/Prototype/`. Every one is applied by an ordinary `apply_power` row
// (or, for Alice's Detonator, by the one install call its row makes), and every
// one reads the arm's existing primitives -- the ledger, `ProtoBombPower`'s
// reads and verbs, the Spark chokepoint -- so no rule is re-expressed here.
// Sim twins: `tier0/engine/klee_overhaul.py`, the R276 block.

/// <summary>
/// Playdate: "The next Companion card you play this turn costs 1 less."
/// <c>NextCompanionDiscountPower</c>'s construction (Kokomi's Rally), under
/// Klee's own name and Klee's own reading of a Companion card
/// (<see cref="KleeExpansion.IsCompanionCard"/>). EACH COPY IS 1 OFF THE SAME
/// NEXT CARD: two Playdates are two sentences about one card, so the discount
/// is the stack and the whole stack is spent on it. Expires at the end of the
/// turn it was played on.
/// </summary>
public sealed class PlaydatePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Playdate"),
        ("description",
            "The next [gold]Companion[/gold] card you play this turn costs "
          + "[blue]{Amount}[/blue] less."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The cost this power takes off <paramref name="card"/>, 0 if
    /// it does not apply. PURE -- the rule, readable without a combat.</summary>
    public static decimal Discounted(decimal originalCost, int discount) =>
        System.Math.Max(0m, originalCost - discount);

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (!KleeExpansion.IsCompanionCard(card)) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = Discounted(originalCost, Amount);
        return true;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeExpansion.IsCompanionCard(cardPlay.Card)) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        await PowerCmd.Remove(this);
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
/// Boom Badge: "Your next Set off card this turn is played twice."
/// <c>ReplayNextCompanionPower</c>'s construction (Study Buddy), keyed on a
/// Set off card (<see cref="ISetOffCard"/>) rather than a Companion one: the
/// game's own replay surface (<c>ModifyCardPlayCount</c>), so the second play
/// is a real second resolution of the whole card -- and, as the spec says,
/// usually finds the Bombs already gone and is the card's own effect again.
///
/// EACH COPY DOUBLES ONE CARD: the stack is how many Set off cards are still
/// owed a second play, and each doubled card spends one. Expires at the end of
/// the turn it was played on.
/// </summary>
public sealed class BoomBadgePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Boom Badge"),
        ("description",
            "Your next [blue]{Amount}[/blue] [gold]Set off[/gold] "
          + "{Amount:plural:card|cards} this turn {Amount:plural:is|are} "
          + "played twice."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (Amount <= 0 || !KleeExpansion.IsSetOffCard(card)) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        return playCount + 1;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeExpansion.IsSetOffCard(cardPlay.Card)) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        if (Amount > 1)
        {
            await PowerCmd.ModifyAmount(choiceContext, this, -1,
                                        applier: Owner, cardSource: null,
                                        silent: true);
        }
        else
        {
            await PowerCmd.Remove(this);
        }
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
/// Wait For It...: "This turn, the next time one of your Bombs triggers an
/// Elemental Reaction, draw 2 cards and gain 1 Energy." A ONE-SHOT: the first
/// reacting explosion of hers spends the whole power, and the end of the turn
/// removes it unspent. Each copy is one payout, so two copies waiting on the
/// same explosion pay twice. The card's Retain keeps the CARD; the window this
/// power is lasts the turn the card was played.
/// </summary>
public sealed class WaitForItPower
    : PowerModel, ILocalizationProvider, IProtoChargeListener
{
    /// <summary>The printed payout, per copy.</summary>
    public const int PayoutHand = 2;

    public const int ReactionEnergy = 1;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Wait For It..."),
        ("description",
            "This turn, the next time one of your [gold]Bombs[/gold] triggers "
          + "an [gold]Elemental Reaction[/gold], draw [blue]" + PayoutHand
          + "[/blue] cards and gain [blue]" + ReactionEnergy + "[/blue] "
          + "[gold]Energy[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted)
    {
        if (applier != Owner || !reacted || Amount <= 0) return;
        var player = Owner.Player;
        var copies = Amount;
        await PowerCmd.Remove(this);
        if (player == null) return;
        await PlayerCmd.GainEnergy(ReactionEnergy * copies, player);
        await CardPileCmd.Draw(choiceContext, PayoutHand * copies, player);
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
/// Party Poppers: "Whenever you play a card that costs Sparks, place a Bomb 2
/// on a random enemy." "Costs Sparks" is the cost BADGE
/// (<see cref="KleeExpansion.CostsSparks"/>), so Fireworks Finale and Stoke
/// the Fuse count. <c>WitchesCirclePower</c>'s shape, one trigger over: the
/// stack is the Bomb size, and a replayed play is a play.
/// </summary>
public sealed class PartyPoppersPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Party Poppers"),
        ("description",
            "Whenever you play a card that costs [gold]Sparks[/gold], place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled || Owner == null) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        if (!KleeExpansion.CostsSparks(cardPlay.Card)) return;
        await ProtoBombPower.PlaceOnRandom(choiceContext, Owner, Amount,
                                           isMine: false, payloadMineAll: 0,
                                           cardSource: null);
    }
}

/// <summary>
/// Look Out!: "Whenever one of your Mines goes off, gain 3 Block." Answering
/// an attack or Set off by a card, it is the same Mine going off. A Power's
/// Block, so it takes no card-Block modifier (<c>GroundedPower</c>'s line).
/// </summary>
public sealed class LookOutPower
    : PowerModel, ILocalizationProvider, IProtoChargeListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Look Out!"),
        ("description",
            "Whenever one of your [gold]Mines[/gold] goes off, gain "
          + "[blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted)
    {
        if (applier != Owner || !charge.IsMine || Amount <= 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
    }
}

/// <summary>
/// Patience, Klee!: "At the end of your turn, if you played no Set off card
/// this turn, your largest Bomb grows by 4." The question is the one Grounded
/// asks of LAST turn, asked of THIS one
/// (<see cref="KleeOverhaulLedger.SetOffCardsThisTurn"/>): a card whose Set off
/// resolved, so a Mine answering an attack and Sparks 'n' Splash's echo do not
/// switch it off.
/// </summary>
public sealed class PatienceKleePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Patience, Klee!"),
        ("description",
            "At the end of your turn, if you played no [gold]Set off[/gold] "
          + "card this turn, your largest [gold]Bomb[/gold] grows by "
          + "[blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Does the quiet turn pay? PURE, off the ledger.</summary>
    public static bool Pays(KleeOverhaulLedger ledger) =>
        ledger.SetOffCardsThisTurn == 0;

    /// <summary>
    /// <c>AfterSideTurnEnd</c> and not <c>BeforeSideTurnEnd</c>, and the
    /// difference is the ORDER: Sparks 'n' Splash's echo reads the largest
    /// Bomb at <c>BeforeSideTurnEnd</c>, and two co-tenants of one broadcast
    /// have no guaranteed order -- so the growth lands strictly after the echo
    /// has paid, on both engines (<c>klee_overhaul.turn_end</c>). Still the
    /// end of HER turn: the side ending is the player's.
    /// </summary>
    public override Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player || Owner == null)
        {
            return Task.CompletedTask;
        }
        if (Pays(KleeOverhaulLedger.For(Owner)))
        {
            ProtoBombPower.GrowLargest(Owner, Amount);
        }
        return Task.CompletedTask;
    }
}

/// <summary>
/// Friendship Bracelet: "Whenever you play a Companion card, your largest Bomb
/// grows by 3." One growth per play, on the one reading of "your largest
/// Bomb" the arm has (<see cref="ProtoBombPower.GrowLargest"/>).
/// </summary>
public sealed class FriendshipBraceletPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Friendship Bracelet"),
        ("description",
            "Whenever you play a [gold]Companion[/gold] card, your largest "
          + "[gold]Bomb[/gold] grows by [blue]{Amount}[/blue]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled || Owner == null) return Task.CompletedTask;
        if (cardPlay.Card?.Owner?.Creature != Owner) return Task.CompletedTask;
        if (!KleeExpansion.IsCompanionCard(cardPlay.Card))
        {
            return Task.CompletedTask;
        }
        ProtoBombPower.GrowLargest(Owner, Amount);
        return Task.CompletedTask;
    }
}

/// <summary>
/// Klee's Secret Base: "At the start of your turn, if no enemy has a Bomb of
/// yours, place a Bomb 5 on a random enemy." <c>AfterPlayerTurnStart</c>, which
/// runs after the growth hook (<c>BeforeSideTurnStart</c>) -- the spec's "after
/// Bombs grow" -- so the fresh Bomb does not grow on the turn it arrives. Two
/// copies check in turn, so the second sees the first one's Bomb.
/// </summary>
public sealed class SecretBasePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Klee's Secret Base"),
        ("description",
            "At the start of your turn, if no enemy has a [gold]Bomb[/gold] of "
          + "yours, place a [gold]Bomb[/gold] [blue]{Amount}[/blue] on a "
          + "random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The check and the Bomb, in the one fixed order the
    /// expansion's start-of-turn placements take
    /// (<see cref="KleeExpansion.RunTurnStartPlacements"/>): this Power's
    /// question is asked before Dodoco's Mine lands.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        await KleeExpansion.RunTurnStartPlacements(choiceContext, player);
    }
}

/// <summary>
/// Dodoco: "At the start of your turn, place a Mine 4 on a random enemy." The
/// Mine joins any pile of hers already on that enemy, which is what
/// <see cref="ProtoBombPower.Place"/> always does; the pile then answers the
/// enemy's attack for the Mine's share, rule 6.
/// </summary>
public sealed class DodocoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Dodoco"),
        ("description",
            "At the start of your turn, place a [gold]Mine[/gold] "
          + "[blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Through the same sequencer as Klee's Secret Base, so the
    /// Mine lands AFTER that Power has read the board.</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        await KleeExpansion.RunTurnStartPlacements(choiceContext, player);
    }
}

/// <summary>
/// Aftershock: "The first time each turn a Bomb of yours triggers an Elemental
/// Reaction, place a Bomb that size on a random enemy." The size is the
/// CHARGE's (what the Bomb was, not what a multiplier made its hit), the new
/// Bomb is placed after the reacting explosion has resolved and is a plain
/// placement -- nothing about placing it sets it off. Once per turn per Klee,
/// on the ledger's latch; a second copy places a second Bomb off the same
/// reaction.
/// </summary>
public sealed class AftershockPower
    : PowerModel, ILocalizationProvider, IProtoChargeListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Aftershock"),
        ("description",
            "The first time each turn a [gold]Bomb[/gold] of yours triggers an "
          + "[gold]Elemental Reaction[/gold], place a [gold]Bomb[/gold] that "
          + "size on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted)
    {
        if (applier != Owner || !reacted || charge.Size <= 0) return;
        var ledger = KleeOverhaulLedger.For(Owner);
        if (!ledger.TakeAftershock()) return;
        for (var copy = 0; copy < Amount; copy++)
        {
            await ProtoBombPower.PlaceOnRandom(choiceContext, Owner,
                                               charge.Size, isMine: false,
                                               payloadMineAll: 0,
                                               cardSource: null);
        }
    }
}

/// <summary>
/// Second Surprise: "Whenever one of your Mines goes off, place a Bomb half its
/// size, rounded down, on that enemy." Answering an attack or Set off by a
/// card, it is the same Mine. A PLAIN Bomb; nothing when the half is 0; and if
/// the Mine's explosion killed the enemy, the half jumps to a survivor, rule 3
/// (<see cref="ProtoBombPower.PlaceOrJump"/>). The Bomb lands after the Mine's
/// explosion, so the Set off already in progress does not take it.
/// </summary>
public sealed class SecondSurprisePower
    : PowerModel, ILocalizationProvider, IProtoChargeListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Second Surprise"),
        ("description",
            "Whenever one of your [gold]Mines[/gold] goes off, place a "
          + "[gold]Bomb[/gold] half its size on that enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task AfterChargeExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, bool reacted)
    {
        if (applier != Owner || !charge.IsMine) return;
        var half = ProtoBombPower.HalfOf(charge.Size);
        if (half <= 0) return;
        for (var copy = 0; copy < Amount; copy++)
        {
            await ProtoBombPower.PlaceOrJump(choiceContext, target, half,
                                             isMine: false, Owner,
                                             cardSource: null);
        }
    }
}

/// <summary>
/// Spark Knight: "Whenever you gain a Spark, deal 2 Pyro damage to a random
/// enemy." EACH SPARK IS ITS OWN HIT (the spec's note): a gain of 3 is three
/// rolls and three Pyro hits. Fired from the Spark chokepoint
/// (<c>SparkPower.Gain</c>) with the Sparks that LANDED, so every source --
/// an explosion, the companion rule, Grounded, the opening Spark -- counts.
/// PYRO THROUGH <c>ElementalHit.Deal</c>, Sparks 'n' Splash's door, so it
/// reacts with an aura and carries her Strength; it is not an Attack.
/// </summary>
public sealed class SparkKnightPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Spark Knight"),
        ("description",
            "Whenever you gain a [gold]Spark[/gold], deal [blue]{Amount}[/blue] "
          + "[gold]Pyro[/gold] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The hits a gain of <paramref name="landed"/> Sparks pays:
    /// one per Spark, none for a gain that moved nothing. PURE.</summary>
    public static int HitsFor(int landed) => landed > 0 ? landed : 0;

    /// <summary>Called by <c>SparkPower.Gain</c> after the bank moved.</summary>
    internal static async Task AfterSparksGained(
        PlayerChoiceContext choiceContext, Creature? klee, int landed)
    {
        if (klee == null || !KleeOverhaul.Enabled) return;
        var hits = HitsFor(landed);
        if (hits == 0) return;
        foreach (var knight in klee.Powers.OfType<SparkKnightPower>().ToList())
        {
            for (var i = 0; i < hits; i++)
            {
                var combat = klee.CombatState;
                if (combat == null) return;
                var living = combat.HittableEnemies
                    .Where(e => !e.IsDead).ToList();
                if (living.Count == 0) return;
                var target = combat.RunState.Rng.CombatTargets.NextItem(living);
                if (target == null) return;
                await ElementalHit.Deal(choiceContext, target, Element.Pyro,
                                        knight.Amount, klee);
            }
        }
    }
}

/// <summary>
/// Alice's Detonator: "At the start of your turn, add a Ka-pow! to your hand."
/// The starter's own card (<see cref="ProtoKoKapow"/>: 0, Retain, Set off,
/// Deal 4), one per copy, added AFTER the turn's draw
/// (<c>AfterPlayerTurnStart</c>, Blazing Delight's site and reason). No prompt
/// of any kind.
///
/// TWO POWERS AND ONE RULE: the upgraded card's copies arrive upgraded, and a
/// Power has no upgrade of its own and a copy count cannot also carry a flag,
/// so the card installs one twin or the other (<see cref="Install"/>) and both
/// twins are this class with a different answer to <see cref="Upgraded"/>.
/// ABSTRACT so that neither twin's lookup (`OfType`) can find the other.
/// </summary>
public abstract class AlicesDetonatorBasePower : PowerModel, ILocalizationProvider
{
    /// <summary>Do this Power's Ka-pow!s arrive upgraded?</summary>
    public abstract bool Upgraded { get; }

    public abstract List<(string, string)>? Localization { get; }

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The card's play: install the twin its upgrade names.</summary>
    public static async Task Install(
        PlayerChoiceContext choiceContext, Creature? klee, bool upgraded,
        CardModel? cardSource)
    {
        if (klee == null) return;
        if (upgraded)
        {
            await PowerCmd.Apply<AlicesDetonatorPlusPower>(
                choiceContext, klee, 1, applier: klee, cardSource: cardSource);
        }
        else
        {
            await PowerCmd.Apply<AlicesDetonatorPower>(
                choiceContext, klee, 1, applier: klee, cardSource: cardSource);
        }
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        var combat = Owner.CombatState;
        if (combat == null) return;
        for (var copy = 0; copy < Amount; copy++)
        {
            var card = combat.CreateCard(ModelDb.Card<ProtoKoKapow>(), player);
            if (card == null) continue;
            if (Upgraded && card.IsUpgradable && !card.IsUpgraded)
            {
                card.UpgradeInternal();
            }
            await CardPileCmd.AddGeneratedCardToCombat(
                card, PileType.Hand, player);
        }
    }
}

/// <summary>Alice's Detonator, as the base card installs it.</summary>
public sealed class AlicesDetonatorPower : AlicesDetonatorBasePower
{
    public override bool Upgraded => false;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Detonator"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] "
          + "[gold]Ka-pow![/gold] to your hand."),
    };
}

/// <summary>The upgraded Alice's Detonator: the same rule, and each Ka-pow! it
/// adds arrives upgraded.</summary>
public sealed class AlicesDetonatorPlusPower : AlicesDetonatorBasePower
{
    public override bool Upgraded => true;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Detonator+"),
        ("description",
            "At the start of your turn, add [blue]{Amount}[/blue] upgraded "
          + "[gold]Ka-pow![/gold] to your hand."),
    };
}
