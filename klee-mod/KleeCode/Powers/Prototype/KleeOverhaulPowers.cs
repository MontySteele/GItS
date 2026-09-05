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
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Explosives Workshop: "At the start of your turn, your Bombs grow by 1 more."
///
/// The power stores nothing and does nothing on a hook. Growth is ONE number
/// and it is computed in ONE place (<c>ProtoBombPower.GrowthFor</c>), so this
/// power's whole job is to be present and countable -- which is what keeps a
/// Bomb armed before the Workshop and one armed after it growing at the same
/// rate, the identical argument the shipped <c>bomb_damage_up</c> makes for
/// having one bomb-damage stat.
/// </summary>
public sealed class ExplosivesWorkshopGrowthPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Explosives Workshop"),
        ("description",
            "At the start of your turn, your [gold]Bombs[/gold] grow by "
          + "[blue]{Amount}[/blue] more."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Alice's Recipe: "Your Bombs grow twice each turn." The brief's own gloss is
/// "Breaks rule 1", and it breaks it by MULTIPLYING the turn's growth rather
/// than adding to it -- see <c>ProtoBombPower.GrowthFor</c>, which is the one
/// place the two modifiers compose.
///
/// THE ROW USED TO READ "grow by 4 instead of 3" (balance pass 2026-09-02).
/// That made a Rare strictly weaker than the Uncommon beside it: a second
/// Explosives Workshop reaches 5 and a second Recipe still read 4. Doubling is
/// the Rare; the Workshop stays the stacking +1, and one of each is 8.
/// </summary>
public sealed class AlicesRecipePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Recipe"),
        ("description", "Your [gold]Bombs[/gold] grow twice each turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Chained Reactions: "Whenever one of your Bombs goes off, Bomb 3 on a random
/// enemy." The Rare that makes the Spray loop never run dry.
///
/// It rides the explosion bus rather than the card, which is what "whenever"
/// has to mean under rule 2: one Set off on a three-Bomb pile is three
/// explosions, so it is three new Bombs.
///
/// THE RE-BOMB IS PLACED THROUGH THE SAME <c>Place</c> EVERY OTHER SOURCE USES,
/// so it registers, it can be set off, and it can jump -- and, being a plain
/// Bomb rather than a Mine, it cannot answer an attack by itself. Nothing fires
/// by itself (rule 7): this places, it does not detonate.
/// </summary>
public sealed class ChainedReactionsPower
    : PowerModel, ILocalizationProvider, IProtoExplosionListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Chained Reactions"),
        ("description",
            "Whenever one of your [gold]Bombs[/gold] goes off, place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (applier != Owner) return;                 // co-op: your bombs only
        var combat = applier.CombatState;
        if (combat == null) return;

        var candidates = combat.HittableEnemies.Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var dest = combat.RunState.Rng.CombatTargets.NextItem(candidates);
        if (dest == null) return;

        await ProtoBombPower.Place(choiceContext, dest, Amount, isMine: false,
                                   payloadMineAll: 0, applier, cardSource: null);
    }
}

/// <summary>
/// Witches' Circle (R244): "Whenever you play a Hexerei card, place a Bomb 3
/// on a random enemy."
///
/// CHAINED REACTIONS' SHAPE WITH A RARER TRIGGER, which is why the ruled packet
/// files it one rarity down. The stack is the Bomb SIZE, so a second copy is a
/// second Bomb per witch, and the printed number is the row's -- which is what
/// lets its declared <c>power_amount</c> delta move it.
///
/// DEAD ALONE, AND THAT IS THE CARD. The packet's pick 2 was taken at its
/// default: a deck with no Hexerei card in it never sets this off, and it is
/// drafted only by a deck that already holds witches. Klee is herself Hexerei
/// (the brief's sec.7.4), so "two witches make a circle" is her plus any one
/// Hexerei card -- and Alice's Introduction Magic can make a whole hand one.
///
/// IT HOOKS ITSELF, like <see cref="LadderOfAscentPower"/> and unlike this
/// arm's explosion listeners: <c>AfterCardPlayed</c> reaches a power the card
/// just applied, and asking the mark's one reader
/// (<c>CompanionHexerei.IsHexerei</c>) is what lets the this-turn window widen
/// the family without this power learning about it.
///
/// THE BOMB IS PLACED THROUGH THE SAME <c>Place</c> every other source uses, so
/// it registers, can be set off and can jump -- and, being a plain Bomb rather
/// than a Mine, it cannot answer an attack by itself. Nothing fires by itself
/// (rule 7): this places, it does not detonate. Sim twin:
/// <c>klee_overhaul.note_hexerei_played</c>.
/// </summary>
public sealed class WitchesCirclePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Witches' Circle"),
        ("description",
            "Whenever you play a [gold]Hexerei[/gold] card, place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled || Owner == null) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;   // co-op: yours
        if (!CompanionHexerei.IsHexerei(cardPlay.Card)) return;
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
/// Sparks 'n' Splash: "At the end of your turn, deal Pyro damage to a random
/// enemy equal to its largest Bomb."
///
/// R250 (2026-09-04), replacing the SUM this row paid before: round 8's seats
/// found that once the echo lands the sum makes banking always right and
/// every Set off card "deletes my engine" -- the largest single charge keeps
/// hold-or-cash a decision after the Power lands, since a Set off still
/// cashes the WHOLE pile (<c>ProtoBombPower.SetOff</c>) and a reaction
/// still multiplies whichever one hit is dealt.
///
/// Before that, [USER]'s OWN DESIGN, 2026-09-02: "I think auto-detonation on
/// Sparks n' Splash completely bricks the growth build. How about instead 'a
/// random enemy takes damage equal to the amount of Bomb on them'?" The row
/// printed an automatic Set off before this -- first at the end of the turn,
/// then at the start of it -- and either way the Rare that the growth deck
/// most wants was the one card that cashed its pile without being asked.
///
/// IT READS THE PILE AND DOES NOT SPEND IT, which is the whole card. Nothing
/// is taken, so:
///   * the Bombs stay and keep growing -- the echo pays again next turn, and
///     bigger;
///   * NO SPARK, because rule 4 pays one per EXPLOSION and nothing exploded;
///   * no Mine answers, no explosion bus, no per-turn counters move. This is
///     not a Set off, and rule 2's "only a card that says Set off" is
///     untouched by it.
///
/// PYRO THROUGH <c>ElementalHit.Deal</c>, the same funnel an explosion and any
/// of Klee's own hits use, so the echo reacts with an aura exactly as they do
/// and carries her Strength the same way. It is NOT an Attack: no card is
/// being played, so nothing that keys off attacks sees it.
///
/// A RANDOM BOMBED ENEMY, unlike the auto-detonation it replaces: an echo of
/// nothing is not a printed effect, so the roll is over the enemies that
/// actually hold one of her charges, and a board with none does nothing at
/// all.
///
/// EACH COPY IS ITS OWN HIT (<c>EB-358</c>, default applied): a second Sparks
/// 'n' Splash used to badge <c>Amount</c> 2 (this power's own
/// <see cref="StackType"/> is <c>Counter</c>, one stack per copy played) and
/// pay the pile ONCE. The badge and the payout now read the same number: the
/// loop below runs <see cref="PowerModel.Amount"/> times, one per stack, each
/// iteration rolling its OWN random target -- so two copies can land on the
/// same enemy twice or on two different ones -- and paying that target's
/// largest Bomb, independently of every other iteration.
/// </summary>
public sealed class BombEchoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "At the end of your turn, deal [gold]Pyro[/gold] damage to a "
          + "random enemy equal to its largest [gold]Bomb[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner?.CombatState == null) return;

        for (var copy = 0; copy < Amount; copy++)
        {
            // An explicit walk rather than a `Where` lambda: the candidate
            // rule is the card's own printed one ("a random enemy ... equal
            // to its largest Bomb" -- so, an enemy that has some), and a
            // closure would hide it from the IL pin that reads this method.
            // Rolled FRESH per copy (EB-358): each hit is its own random
            // enemy, not one roll shared by every stack.
            var candidates = new List<Creature>();
            foreach (var enemy in Owner.CombatState.HittableEnemies)
            {
                if (enemy.IsDead) continue;
                if (!ProtoBombPower.HoldsChargeFrom(enemy, Owner)) continue;
                candidates.Add(enemy);
            }
            if (candidates.Count == 0) break;
            var target = Owner.CombatState.RunState.Rng.CombatTargets
                .NextItem(candidates);
            if (target == null) continue;

            var size = ProtoBombPower.LargestPlacedBy(target, Owner);
            if (size <= 0) continue;
            await ElementalHit.Deal(
                choiceContext, target, Element.Pyro, size, Owner);
        }
    }
}

/// <summary>
/// Catalytic Converter: "Whenever a Bomb reacts, gain 1 extra Spark." The card
/// that makes React feed Spray.
///
/// EXTRA, on top of the explosion's own Spark, and only when the explosion
/// REACTED -- which is a fact only the bus carries, because by the time a
/// listener could look, the aura it consumed is gone.
///
/// A SEPARATE POWER FROM THE SHIPPED <c>ReactionBonusSparkEnergyPower</c> of
/// the same name, deliberately: the shipped one pays on EVERY reaction and also
/// grants Burst Energy, and this one pays only on a BOMB's reaction and grants
/// only the Spark. Re-using it would have re-priced the card without saying so.
/// </summary>
public sealed class BombReactionSparkPower
    : PowerModel, ILocalizationProvider, IProtoExplosionListener
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Catalytic Converter"),
        ("description",
            "Whenever one of your [gold]Bombs[/gold] triggers an "
          + "[gold]Elemental Reaction[/gold], gain [blue]{Amount}[/blue] "
          + "additional [gold]Spark[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public async Task OnBombExploded(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        int size, bool reacted)
    {
        if (applier != Owner || !reacted) return;
        await SparkPower.Gain(choiceContext, Owner, Amount, cardSource: null,
                              source: "power:catalytic_converter/bomb_reaction");
    }
}

/// <summary>
/// Grounded: "At the start of your turn, if none of your Bombs went off last
/// turn, gain 6 Block and 1 Spark." The card that pays for the quiet turn --
/// the cook half of the contested thing, with Run Away! paying for the loud
/// one.
///
/// LAST turn, not this one, and that is the whole design: the decision it pays
/// for was made a turn ago, so the Block arrives before this turn's decision
/// rather than as a reward for one already taken. <c>SetOffLastTurn</c> is the
/// ledger's own read, rolled on the round stamp.
///
/// THE SPARK IS `EB-344` (ruled R248). Rule 4 mints a Spark per EXPLOSION, so
/// the turn this card is written for -- the one where nothing went off -- is by
/// construction the turn that mints none, and the cook half of the loop paid
/// for itself in Block alone. A Spark on the held turn is what makes holding a
/// PLAY rather than a pause. It is a flat
/// <see cref="KleeOverhaulLaw.GroundedSpark"/> and NOT <c>Amount</c>, because
/// the upgrade is <c>{power_amount: +2}</c> -- that is the Block, 6 to 8 -- and
/// the Spark is 1 at both levels.
/// </summary>
public sealed class GroundedPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grounded"),
        ("description",
            "At the start of your turn, if none of your [gold]Bombs[/gold] "
          + "went off last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and [blue]" + KleeOverhaulLaw.GroundedSpark + "[/blue] "
          + "[gold]Spark[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        // Read BEFORE the roll would be wrong and read after it is the point:
        // `For` rolls the ledger to this round, so `SetOffLastTurn` is exactly
        // the count that stood when the player last passed.
        // KAEYA'S COVER STORY, and the only line the companion stand-in seam
        // adds to this arm: Cold-Blooded Strike prints "This turn, Grounded
        // counts nothing as having gone off" and it names GROUNDED -- so the
        // blind is read HERE rather than written into the counter above, which
        // Jean's stand-in also reads. False on every build with the companion
        // arm off.
        if (KleeOverhaulLedger.For(Owner).SetOffLastTurn > 0
            && !CompanionStandIns.GroundedBlind(Owner)) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
        // `EB-344`. ONE CONDITION, TWO PAYOUTS: both are behind the same test,
        // so a turn that grants no Block grants no Spark either and there is no
        // second reading of "held" to keep in step.
        await SparkPower.Gain(
            choiceContext, Owner, KleeOverhaulLaw.GroundedSpark,
            cardSource: null, source: "power:grounded/held_turn");
    }
}

/// <summary>
/// Vermillion Pact (the pool pass, `EB-491`): "Whenever one of your Bombs
/// triggers an Elemental Reaction, the Attack that set it off triggers one
/// too." The brief's sec.5.3 rule-breaker, and the third of its three
/// rule-breaking Rares: the shared "one aura, consumed by the first hit" rule
/// is broken, for her chain and nowhere else.
///
/// DEFERRED FROM SLICE ONE, AND ON WHICH OF THE TWO ROADS. The slice packet's
/// sec.5 named this row as the one that might drop out -- "the one item on this
/// list that touches shared reaction code" -- and set out the two shapes it
/// could take: RE-APPLYING the consumed aura between the explosion and the
/// card's own hit, or threading a "do not consume" flag through
/// <c>ElementalHit.Deal</c>. This is the FIRST, and the reason is that the
/// second is a shared-layer change every character's reactions would then have
/// to be re-read against, while this one is a Klee power writing to a Klee
/// enemy through the ordinary front door (<see cref="AuraCmd.Apply"/>).
///
/// THE PRICE OF THAT ROAD, stated rather than hidden: the aura really is back
/// on the board, so a THIRD hit in the same play sees it too, and every
/// on-apply hook fires again for it. On a multi-charge pile that is the card
/// compounding -- each reacting explosion hands the aura back, so the next
/// charge reacts as well and the Attack behind them all still finds it
/// standing. That is what a 2-energy Rare printed as a rule-breaker buys, and
/// it is the reading the face states: the aura the Bomb ate is still there.
///
/// ATTACKS ONLY, AND ONLY A SET OFF THE CARD ITSELF MADE. The trigger is read
/// off <c>cardSource</c> at <c>ProtoBombPower.Explode</c>: a Mine answering an
/// enemy intent carries no card at all, and Quick Fuse, Countdown and Fireworks
/// Show are Skills with no hit behind the explosion for the aura to feed. "The
/// Attack that Set it off" is exactly the scope of the rule.
///
/// DEAD ALONE, like Witches' Circle beside it (R244 pick 2): a deck with no
/// applier in it never puts a foreign aura up, and this Power then never fires.
/// That is the card, not a defect.
///
/// STACKS DO NOTHING. The rule is a fact about the board, not a number, so a
/// second copy adds no second aura -- the Counter is how the badge counts
/// copies, exactly as <c>AlicesRecipePower</c>'s is. Sim twin:
/// <c>klee_overhaul.VERMILLION_PACT</c> and its two reads at
/// <c>klee_overhaul._explode</c>.
/// </summary>
public sealed class VermillionPactPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Vermillion Pact"),
        ("description",
            "Whenever one of your [gold]Bombs[/gold] triggers an "
          + "[gold]Elemental Reaction[/gold], the Attack that set it off "
          + "triggers one too."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// The aura this explosion is ABOUT TO CONSUME, or <c>Element.None</c>.
    ///
    /// Read BEFORE the hit, because the hit is what eats it: after
    /// <c>ElementalHit</c> has run there is nothing left to ask, which is the
    /// same fact <c>IProtoExplosionListener.reacted</c> exists for. PURE -- it
    /// answers None on every board with no Pact, on a Skill's Set off and on a
    /// Mine, so the caller pays one interface walk and nothing else.
    /// </summary>
    public static Element AuraToRestore(
        Creature applier, CardModel? cardSource, Creature target)
    {
        if (cardSource is not { Type: CardType.Attack }) return Element.None;
        if (!applier.Powers.OfType<VermillionPactPower>().Any())
        {
            return Element.None;
        }
        return AuraCmd.Find(target)?.Element ?? Element.None;
    }

    /// <summary>
    /// Hand the consumed aura back, if the explosion really did react with it.
    ///
    /// <paramref name="reacted"/> IS THE WHOLE GATE and not a convenience: an
    /// explosion into a Pyro aura refreshes rather than reacts and consumes
    /// nothing, so there is nothing owed back -- and re-applying there would be
    /// the Pact silently topping up an aura it never spent.
    ///
    /// IT REFUSES A BOARD THAT ALREADY HOLDS ONE (the one-aura invariant
    /// <see cref="AuraCmd.Apply"/>'s own doc states) and a corpse: a dead enemy
    /// takes no hit behind the explosion, so there is no second reaction for
    /// the aura to make.
    /// </summary>
    public static async Task Restore(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        Element aura, bool reacted)
    {
        if (!reacted || aura == Element.None || target.IsDead) return;
        if (AuraCmd.Find(target) != null) return;
        await AuraCmd.Apply(choiceContext, target, aura, applier,
                            cardSource: null);
    }
}
