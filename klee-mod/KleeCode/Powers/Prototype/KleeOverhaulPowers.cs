using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
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
/// Alice's Recipe: "Your Bombs grow by 4 instead of 3." The brief's own gloss
/// is "Breaks rule 1", and it breaks it by REPLACING the base rather than
/// adding to it -- see <c>ProtoBombPower.GrowthFor</c>, which is the one place
/// the two modifiers compose.
/// </summary>
public sealed class AlicesRecipePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Recipe"),
        ("description",
            "Your [gold]Bombs[/gold] grow by [blue]" + KleeOverhaulLaw.AliceGrowth
          + "[/blue] instead of [blue]" + KleeOverhaulLaw.BombGrowth + "[/blue]."),
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
/// Sparks 'n' Splash: "At the end of your turn, Set off a random enemy's
/// Bombs." The brief's gloss is "Breaks rule 7", and this is the one power in
/// the slice that fires without a card saying so -- which is exactly why it is
/// a Rare and why it is the ONLY such hook here.
///
/// A RANDOM ENEMY, not a random BOMBED enemy: the card says what it says, and
/// picking only from bombed enemies would make it strictly better than printed
/// on a board where one enemy is loaded and three are not.
/// </summary>
public sealed class EndOfTurnSetOffPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sparks 'n' Splash"),
        ("description",
            "At the end of your turn, [gold]Set off[/gold] a random enemy's "
          + "[gold]Bombs[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner?.CombatState == null) return;

        var candidates = Owner.CombatState.HittableEnemies
            .Where(e => !e.IsDead).ToList();
        if (candidates.Count == 0) return;
        var target = Owner.CombatState.RunState.Rng.CombatTargets
            .NextItem(candidates);
        if (target == null) return;

        await ProtoBombPower.SetOff(choiceContext, target, Owner, cardSource: null);
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
/// turn, gain 6 Block." The card that pays for the quiet turn -- the cook half
/// of the contested thing, with Run Away! paying for the loud one.
///
/// LAST turn, not this one, and that is the whole design: the decision it pays
/// for was made a turn ago, so the Block arrives before this turn's decision
/// rather than as a reward for one already taken. <c>SetOffLastTurn</c> is the
/// ledger's own read, rolled on the round stamp.
/// </summary>
public sealed class GroundedPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Grounded"),
        ("description",
            "At the start of your turn, if none of your [gold]Bombs[/gold] "
          + "went off last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
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
        if (KleeOverhaulLedger.For(Owner).SetOffLastTurn > 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
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
