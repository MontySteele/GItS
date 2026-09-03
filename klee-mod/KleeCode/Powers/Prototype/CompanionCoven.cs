using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
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
/// KLEE'S FOUR COVEN PERSONALS, C# side (QUARANTINED, R213 B / R236). Twin of
/// <c>tier0/engine/companion_coven.py</c>, function for function.
///
/// The approved Mondstadt workshop's sec.4 and its sec.3 Prune entry give Klee
/// four PERSONAL companions. A Personal is not a Universal: it rides the
/// channel <c>prune_witch_hunt</c> already rides -- <c>ICompanionCard
/// .PersonalPool</c>, filtered at every offer site by
/// <see cref="CompanionPool.IsOfferable"/> -- so the four join
/// <see cref="CompanionOverhaulRoster"/>'s replacement roster without joining
/// either nation's Universal pool, and neither nation's count moves.
///
/// NO NEW SWITCH. This is the SAME arm as the two nation workshops:
/// <c>-p:PrototypeCards=true</c> is the quarantine and
/// <c>-p:CompanionOverhaul=true</c> moves <see cref="CompanionOverhaul"/>'s
/// default. A fifth property would let a build offer Klee's coven beside the
/// shipped Mondstadt rows the coven's own Prune row supersedes, which is a
/// state no document describes.
///
/// TWO ARMS MEET HERE, and this file is the only place in the mod where they
/// do. Two of the four speak about BOMBS, which are the KLEE overhaul's rule --
/// so <see cref="YueguiPower"/> and <see cref="CompanionCovenBombs"/> each test
/// that arm as well as this one, the same pair of gates the sim's
/// <c>companion_coven</c> takes. A Yuegui thrown by a seat that is not running
/// the Bomb rules plants nothing and its clock still ticks.
/// </summary>
public static class CompanionCovenLaw
{
    /// <summary>Qiqi, Herald of Frost: Block at the start of each turn.
    /// Mirrors <c>C.CVN_HERALD_BLOCK</c>.</summary>
    public const int HeraldBlock = 3;

    /// <summary>Qiqi, Herald of Frost: "apply Cryo twice".
    /// Mirrors <c>C.CVN_HERALD_APPLICATIONS</c>.</summary>
    public const int HeraldApplications = 2;

    /// <summary>Yaoyao, Yuegui: the Bomb it throws.
    /// Mirrors <c>C.CVN_YUEGUI_BOMB_SIZE</c>.</summary>
    public const int YueguiBombSize = 3;
}

/// <summary>
/// Prune, Ring-A-Ding-Ding! Hexhunter Chime: "The next Bomb you set off this
/// turn deals the swirled element instead of Pyro."
///
/// A MARKER, NOT AN AMOUNT. The stack is 1 and nothing reads it: what the
/// power says is "armed", and the element it hands over is the one the LEDGER
/// remembers (<see cref="CompanionOverhaulLedger.LastSwirlElement"/>), not one
/// carried here. That is the difference between this and Varka's
/// <see cref="SwirlChargePower"/>, and the card is the reason: Sturm und Drang
/// is a Power that is already standing when a Swirl happens, so its own latch
/// can be written at the Swirl; the Chime is an ATTACK whose printed order is
/// "Deal 8 damage. Swirl. The next Bomb ...", so the Swirl it names resolves
/// BEFORE the rider it arms and a latch on the power would always be empty.
///
/// "THIS TURN" IS THE REMOVAL, the shape <see cref="PassionOverloadPower"/>
/// takes for the same clause and the shipped <c>AttackUpThisTurnPower</c>
/// before it. Order-independent, so it keeps its own broadcast.
/// </summary>
public sealed class HexhunterChimePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Hexhunter Chime"),
        ("description",
            "The next [gold]Bomb[/gold] you set off this turn deals the "
          + "swirled element instead of [gold]Pyro[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// WHICH ELEMENT AN EXPLOSION DEALS, and it is Pyro unless Prune's Chime says
/// otherwise. Called from <c>ProtoBombPower.Explode</c>, the ONE place a charge
/// deals its damage, so the override cannot reach a hit that is not a Bomb's
/// and cannot miss one that is. Sim twin: <c>companion_coven.bomb_element</c>,
/// called from <c>klee_overhaul._explode</c>, that engine's same one place.
///
/// "THE NEXT BOMB", SINGULAR, so the rider is CONSUMED here rather than read.
/// A three-charge Set off is three explosions (rule 2's "one at a time") and
/// the card promises the element to the first of them. Consumed even when no
/// Swirl landed, because the card spent its rider on that Bomb either way.
/// </summary>
public static class CompanionCovenBombs
{
    /// <summary>Rule 5's element for the explosion about to resolve.</summary>
    public static async Task<Element> ElementFor(
        PlayerChoiceContext choiceContext, Creature applier)
    {
        if (!CompanionOverhaul.Enabled) return Element.Pyro;
        var chime = applier.Powers.OfType<HexhunterChimePower>().FirstOrDefault();
        if (chime == null) return Element.Pyro;
        await PowerCmd.Remove(chime);
        var swirled = CompanionOverhaulLedger.For(applier).LastSwirlElement;
        return swirled == Element.None ? Element.Pyro : swirled;
    }
}

/// <summary>
/// Qiqi, Herald of Frost: "For 3 turns, at the start of your turn apply Cryo
/// twice to a random enemy and gain 3 Block."
///
/// Amount is TURNS REMAINING -- the <see cref="SignatureMixPower"/> grammar
/// every timed row on this surface uses. PAY, THEN TICK.
///
/// TWICE MEANS TWO APPLICATIONS AT ONE BODY, not two rolls: the printed words
/// aim once ("to a random enemy") and then say how many times. The second
/// application is what makes the card its own reaction -- the first Cryo meets
/// whatever is standing, the second lands on the Cryo the first left. The
/// target is RE-ROLLED per application anyway, because the first one can kill
/// (a Cryo that Vaporizes is damage) and a corpse is not "a random enemy";
/// the sim re-rolls in the same loop for the same reason.
///
/// IT KEEPS ITS OWN <c>AfterPlayerTurnStart</c> broadcast, like the arm's other
/// three start-of-turn powers, and the sim runs it LAST of the four. The order
/// is not ceremony here: Mona's omen applies Vulnerable to ALL enemies at the
/// start of the turn and the Cryo below can resolve a reaction that Vulnerable
/// amplifies. It is the only rng-drawing power on that broadcast, so no other
/// tenant's roll can move under it, and two copies of this one are identical.
/// </summary>
public sealed class HeraldOfFrostPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Herald of Frost"),
        ("description",
            "At the start of your turn, apply [gold]Cryo[/gold] twice to a "
          + "random enemy and gain "
          + $"[blue]{CompanionCovenLaw.HeraldBlock}[/blue] [gold]Block[/gold]. "
          + "Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        for (var i = 0; i < CompanionCovenLaw.HeraldApplications; i++)
        {
            var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
            if (target == null) break;
            await ElementalHit.ApplyOnly(
                choiceContext, target, Element.Cryo, Owner);
        }
        // NC-11: power-sourced BLOCK stays raw, like every other Block in this
        // arm; only power-sourced DAMAGE runs the pipeline (NC-1).
        await CreatureCmd.GainBlock(
            Owner, CompanionCovenLaw.HeraldBlock,
            ValueProp.Unpowered, null, fast: true);
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Yaoyao, Yuegui: Throwing Mode: "For 3 turns, at the end of your turn place
/// a Bomb 3 on a random enemy."
///
/// Amount is TURNS REMAINING; FIRE, THEN TICK, the idiom the arm's other
/// volleys use, so a stack count still means "this many more turns, including
/// this one".
///
/// FIRED BY <see cref="CompanionOverhaulTurnEnd"/>, not by a broadcast of its
/// own, and for the reason the six volleys before it are: the throw draws a
/// target from <c>Rng.CombatTargets</c>, so its position in the sequence
/// decides every later roll in the fight. It sits before Nicole's latch because
/// a Bomb grants no Block and cannot change the answer that latch records.
///
/// THE CLOCK TICKS EVEN WHERE THE BOMB CANNOT LAND -- the Klee arm off, a seat
/// that is not Klee, or an empty board. Three turns pass either way, which is
/// what keeps the power from becoming permanent on a board it could not reach.
/// </summary>
public sealed class YueguiPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Yuegui: Throwing Mode"),
        ("description",
            "At the end of your turn, place a [gold]Bomb[/gold] "
          + $"[blue]{CompanionCovenLaw.YueguiBombSize}[/blue] on a random "
          + "enemy. Lasts for [blue]{Amount}[/blue] {Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task FireVolley(PlayerChoiceContext choiceContext)
    {
        if (Owner.Player == null) return;
        // BOTH ARMS, and the second one is the KLEE overhaul's own gate --
        // `KleeOverhaul.Enabled` plus the identity test every seam in the mod
        // carries beside it. Sim twin: `klee_overhaul.live`.
        if (KleeOverhaul.Enabled && Owner.Player.Character is IKleeCharacter)
        {
            await ProtoBombPower.PlaceOnRandom(
                choiceContext, Owner, CompanionCovenLaw.YueguiBombSize,
                isMine: false, payloadMineAll: 0, cardSource: null);
        }
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// THE COVEN'S FOUR ROWS, listed by TYPE for the reason
/// <see cref="CompanionOverhaulRoster"/> lists its Universals that way: a
/// deleted row takes its class with it and this file stops building, which puts
/// the correspondence in the compiler's hands rather than in a prefix match.
///
/// PRUNE'S SHIPPED ROW NEEDS NO EXCLUSION. <c>prune_witch_hunt</c> is a
/// MONDSTADT companion, and the kept half of the replacement drops every row of
/// a replaced nation -- so the Chime supersedes it by the rule that was already
/// there, and with the arm off the shipped row is untouched.
/// </summary>
internal static class CompanionCovenRoster
{
    internal static IEnumerable<CardModel> Personals() => new CardModel[]
    {
        ModelDb.Card<ProtoMcPruneHexhunterChime>(),
        ModelDb.Card<ProtoMcSayuSilencersSecret>(),
        ModelDb.Card<ProtoMcQiqiHeraldOfFrost>(),
        ModelDb.Card<ProtoMcYaoyaoYueguiThrowingMode>(),
    };
}
