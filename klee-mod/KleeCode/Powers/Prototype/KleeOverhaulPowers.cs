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
        ("title", "Witches' Circle"),
        ("description",
            "Whenever you play a [gold]Companion[/gold] card, place a "
          + "[gold]Bomb[/gold] [blue]{Amount}[/blue] on a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled || Owner == null) return;
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
/// Grounded: "At the start of your turn, if you played no Set off card last
/// turn, gain 4 Block and 1 Spark." The card that pays for the QUIET turn --
/// the cook half of the contested thing, with Run Away! paying for the loud
/// one.
///
/// `EB-749` (R271 sec.5.1) IS THE CONDITION IT HAS NOW, and it is the brief's
/// quiet-turn rule with the round-18 trap taken out. The history is two moves,
/// not one. It first read "if NONE OF YOUR BOMBS WENT OFF last turn", and two
/// seats in two rounds read that as a trap in its own deck: under this relic
/// something goes off on most turns even in a Cook deck, because Mines fire on
/// the ENEMY's beat, so the card paid once in five fights. `EB-516` answered
/// that by keying the payout to COOKING instead ("if you have a Bomb on the
/// field"), which was payable but paid a deck for a board state it was holding
/// anyway. R271 keys it to the PLAYER'S OWN ACT instead, and the two
/// interactions that made the first version a trap are excepted BY
/// CONSTRUCTION rather than by a clause:
///
///   * A MINE going off because its enemy attacked is not a Set off CARD, so
///     Cook's Mines no longer switch Grounded off.
///   * SPARKS 'N' SPLASH is not a Set off card either, so a turn on which only
///     it fired is still paid next turn -- the pairing the brief calls either
///     an enjoyable Rare engine or "watch it rise".
///
/// THE READ IS <see cref="KleeOverhaulLedger.SetOffCardsLastTurn"/>, whose one
/// write site is <c>NoteSetOffCardPlayed</c> -- the three card-facing Set off
/// entry points, which a Mine reaches with a null card and which a Power's
/// end-of-turn hit never reaches at all. So neither exception is a special
/// case here and neither can drift from Once More!'s reading of the same act.
///
/// BEFORE GROWTH IS IMMATERIAL, and it is said rather than relied on: the
/// growth hook GROWS and neither places nor removes a charge (rule 7), and
/// nothing between the two hooks plays a card.
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
            "At the start of your turn, if you played no [gold]Set off[/gold] "
          + "card last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and [blue]" + KleeOverhaulLaw.GroundedSpark + "[/blue] "
          + "[gold]Spark[/gold]."),
        // `EB-533`. THE ANSWER, EITHER WAY, AND IT IS A ROW PER ANSWER for
        // `ProtoBombPower.SmartDescriptionLocKey`'s reason: loc is registered
        // once at boot and the board changes every turn, so the LIVE choice is
        // a key and both faces have to exist before it can be made.
        //
        // THE KEYS ARE LITERALS HERE and constants below, and the pair is
        // pinned equal rather than trusted: `tools/lint_text_conventions.py`
        // reads these rows out of the SOURCE by the literal key, so a row
        // written as `(PaidKey, ...)` is a player-facing string invisible to
        // its own ceiling -- the same silence `EB-343` found on `MineKey`.
        ("smartDescriptionPaid",
            "You played no [gold]Set off[/gold] card last turn: paid "
          + "[blue]{Amount}[/blue] [gold]Block[/gold] and [blue]"
          + KleeOverhaulLaw.GroundedSpark + "[/blue] [gold]Spark[/gold]."),
        ("smartDescriptionUnpaid",
            "You played a [gold]Set off[/gold] card last turn, so no "
          + "[gold]Block[/gold] or [gold]Spark[/gold] this turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// `EB-533`. GROUNDED FAILED SILENTLY, and the seat caught it by autopsy.
    ///
    /// THE FIND (Klee r19 lane 1). The card was logged every turn: paid three
    /// times, failed twice, and both failures were the turn after the seat had
    /// detonated everything -- which is the card's price rather than its trap,
    /// and the seat named the turn it resolved as the round's best decision.
    /// What was missing was a line: "the two failures printed no near-miss
    /// line, I caught it only by diffing my own Block".
    ///
    /// A LATCH AND NOT A LIVE BOARD READ, which is the whole of why this field
    /// exists. The badge is read at RENDER time and the condition is answered
    /// at TURN START, and the seat's own failing turn is exactly the turn
    /// those two disagree on: detonate everything, Grounded pays nothing, then
    /// place a fresh Bomb. A badge that re-read the board would say "a Bomb is
    /// on the field" over a turn that paid nothing, which is a second silent
    /// failure rather than a fix. So the power records the answer it gave and
    /// the face prints THAT.
    ///
    /// A `bool?` AND NOT A `bool`: null is "this power has not been asked yet"
    /// -- the turn it is played, before any turn start -- and the face falls
    /// back to the static rule there, because a badge that claimed a failure
    /// the power never had is the same defect pointing the other way. A value
    /// type, so `MutableClone`'s shallow copy carries it correctly and
    /// `DeepCloneFields` has nothing to do (`SwirlChargePower.SwirledElement`'s
    /// own note).
    /// </summary>
    private bool? _paid;

    /// <summary>The loc suffixes <see cref="SmartDescriptionLocKey"/> selects.
    /// BaseLib registers every pair this model returns under
    /// `{Id.Entry}.{key}`, so a second face costs a row and nothing else.
    /// </summary>
    private const string PaidKey = "smartDescriptionPaid";
    private const string UnpaidKey = "smartDescriptionUnpaid";

    /// <summary>The face follows the answer the power last gave (`EB-533`).
    /// A key with no row behind it falls back to the static description
    /// (`PowerModel.HasSmartDescription` is a `LocString.Exists` probe), which
    /// is what the unasked state wants and what it gets.</summary>
    protected override string SmartDescriptionLocKey => _paid switch
    {
        true => Id.Entry + "." + PaidKey,
        false => Id.Entry + "." + UnpaidKey,
        null => Id.Entry + ".smartDescriptionUnasked",
    };

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        var ledger = KleeOverhaulLedger.For(Owner);
        // `EB-749`: the LEDGER, not the board. `SetOffCardsLastTurn` counts
        // CARDS the player played whose Set off resolved, which is exactly what
        // R271 sec.5.1 asks for -- and it is why a Mine answering an attack and
        // Sparks 'n' Splash's end-of-turn hit are both silent here.
        // KAEYA'S COVER STORY, the only line the companion stand-in seam adds
        // to this arm: Cold-Blooded Strike forces Grounded to pay this turn
        // whatever its condition says. The WIRING never moves -- it did not
        // move for `EB-516` and it did not move for `EB-749` -- and what moves
        // instead is the stand-in's printed clause, which now reads "Next
        // turn, Grounded pays even if you played a Set off card." False on
        // every build with the companion arm off.
        if (ledger.SetOffCardsLastTurn > 0
            && !CompanionStandIns.GroundedBlind(Owner))
        {
            // `EB-533`: the answer is recorded BEFORE the return, which is the
            // only line of this method the row moves.
            _paid = false;
            return;
        }

        _paid = true;
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
          + "[gold]Elemental Reaction[/gold], the Attack that "
          + "[gold]Set it off[/gold] triggers one too."),
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
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Energy[/gold] and draw that many cards."),
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
