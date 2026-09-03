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
/// enemy equal to the Bombs on it."
///
/// [USER]'s OWN DESIGN, 2026-09-02: "I think auto-detonation on Sparks n'
/// Splash completely bricks the growth build. How about instead 'a random
/// enemy takes damage equal to the amount of Bomb on them'?" The row printed
/// an automatic Set off before this -- first at the end of the turn, then at
/// the start of it -- and either way the Rare that the growth deck most wants
/// was the one card that cashed its pile without being asked.
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
/// </summary>
public sealed class BombEchoPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "At the end of your turn, deal [gold]Pyro[/gold] damage to a "
          + "random enemy equal to the [gold]Bombs[/gold] on it."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner?.CombatState == null) return;

        // An explicit walk rather than a `Where` lambda: the candidate rule is
        // the card's own printed one ("a random enemy ... equal to the Bombs
        // on it" -- so, an enemy that has some), and a closure would hide it
        // from the IL pin that reads this method.
        var candidates = new List<Creature>();
        foreach (var enemy in Owner.CombatState.HittableEnemies)
        {
            if (enemy.IsDead) continue;
            if (!ProtoBombPower.HoldsChargeFrom(enemy, Owner)) continue;
            candidates.Add(enemy);
        }
        if (candidates.Count == 0) return;
        var target = Owner.CombatState.RunState.Rng.CombatTargets
            .NextItem(candidates);
        if (target == null) return;

        var size = ProtoBombPower.TotalPlacedBy(target, Owner);
        if (size <= 0) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Pyro, size, Owner);
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
/// Vermillion Pact: "When a Bomb reacts, the Attack that set it off reacts
/// too." NOT BUILT IN SLICE ONE, and the slice packet's sec.5 names this row as
/// the one that may drop out: "Vermillion Pact is the one item on this list
/// that touches shared reaction code; if it costs more than a day it drops out
/// of slice one and is tested in slice two."
///
/// WHY IT COSTS MORE THAN A DAY. The rule is not "react twice"; it is "the aura
/// the explosion CONSUMED is still there for the Attack behind it". Every
/// reaction in the mod runs through one funnel -- <c>ElementalHit.Deal</c>
/// removes the aura and calls <c>ReactionEffects.Resolve</c>, which is also
/// where Burst income, Courtroom Drama, Catalytic Converter and the amplifier
/// multiplier all hang. Making the aura survive one hit means either
/// re-applying it between the explosion and the card's own damage (which would
/// change what a THIRD hit in the same play sees, and would re-trigger every
/// on-apply hook) or threading a "do not consume" flag through the shared
/// funnel (which every character's reaction would then have to be re-checked
/// against). Both are shared-layer changes, and neither belongs in a build
/// whose job is to find out whether the seven rules are fun.
///
/// THE ROW IS OFF THE SURFACE. This type is not a stand-in and there is no card
/// pointing at it: an unbuilt rule that shipped as a live card would be a face
/// that lies, which is the defect D4 already names. The type stays as
/// the written record of the decision and its reason.
/// </summary>
internal static class VermillionPactNotBuilt
{
}
