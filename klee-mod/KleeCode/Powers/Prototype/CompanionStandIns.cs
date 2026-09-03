using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
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
/// THE COMPANION STAND-IN SEAM (QUARANTINED, <c>COMPANION_OVERHAUL</c>).
///
/// A STAND-IN IS NOT A POOL MEMBER. It is a whole Klee-only card, with its own
/// unique name, handed to Klee IN PLACE of one named Universal (Klee brief pick
/// 6; the approved Mondstadt workshop sec.1; R236 sec.3). Everything below
/// follows from that one sentence:
///
///   * it never enters ANY pool on its own. The four types are absent from
///     <see cref="CompanionOverhaulRoster"/>, which is the ONE door
///     <see cref="CompanionPool.All"/> opens, so the reward slot, the shop and
///     the Featured Banner are all structurally unable to see one;
///   * it is reached at the HAND-OFF and nowhere else. Each offer surface calls
///     <see cref="HandOff"/> on the card it has already PICKED, so the
///     eligibility lists, the rarity roll and the weighted draw are the
///     Universal's own and THE OFFER ODDS DO NOT MOVE;
///   * every other character is handed the Universal, because the swap is
///     keyed on the stand-in's own <c>PersonalPool</c>.
///
/// SIM TWIN: <c>tier0.engine.companion_standins</c>, called from the same two
/// mouths (<c>tier05.rewards.roll_rewards</c> and
/// <c>tier05.shop.companion_offers</c>).
///
/// THE PAIR TABLE IS LISTED BY TYPE, the same asymmetry
/// <see cref="CompanionOverhaulRoster"/> argues for its own list: a deleted row
/// takes its class with it and this file stops building, where a table of id
/// strings would fail silently the day a row is renamed. The sim derives the
/// same map from the sheet's <c>replaces:</c> key, and
/// <c>tier0/tests/test_companion_standins.py</c> pins the two against each
/// other by id.
///
/// PUBLIC rather than internal, for the reason <c>ProtoBombPower.Charges</c>
/// gives: KleeTests is a separate assembly, the decision <see cref="HandOffTo"/>
/// takes is the whole of this seam, and the alternative was an
/// <c>InternalsVisibleTo</c> nothing else in this mod needs or an IL-shape
/// assertion standing in for the decision itself -- which is exactly the
/// substitution that let the defect below ship.
/// </summary>
public static class CompanionStandIns
{
    /// <summary>
    /// The pairs, Universal -> stand-in, in the sheet's own order. Klee's four
    /// caretakers (R236 sec.3): Diona, Noelle, Kaeya, Jean.
    ///
    /// CACHED LAZILY for <see cref="CompanionOverhaulRoster"/>'s reason, which
    /// is the EB-194 lesson: <c>ModelDb.Card&lt;T&gt;()</c> throws until the
    /// models are built, and a static constructor that throws poisons its type
    /// for the life of the process.
    /// </summary>
    private static IReadOnlyList<(CardModel Universal, CardModel StandIn)>? _pairs;

    private static IReadOnlyList<(CardModel, CardModel)> Pairs() =>
        _pairs ??= new (CardModel, CardModel)[]
        {
            (ModelDb.Card<ProtoMcDionaIcyPaws>(),
             ModelDb.Card<ProtoMcDionaShakenNotPurred>()),
            (ModelDb.Card<ProtoMcNoelleBreastplate>(),
             ModelDb.Card<ProtoMcNoelleIGotYourBack>()),
            (ModelDb.Card<ProtoMcKaeyaFrostgnaw>(),
             ModelDb.Card<ProtoMcKaeyaColdBloodedStrike>()),
            (ModelDb.Card<ProtoMcJeanDandelionBreeze>(),
             ModelDb.Card<ProtoMcJeanLionsFang>()),
        };

    /// <summary>Test seam: forget the cache. The mod never calls it.</summary>
    internal static void ResetAll() => _pairs = null;

    /// <summary>
    /// THE HAND-OFF, and the whole seam in this engine.
    ///
    /// Called on a card a surface has already picked, immediately before it is
    /// instantiated for the player: <see cref="CompanionSlot.Roll"/> (the
    /// fourth reward slot) and <c>MerchantCompanionSlots.AddSlot</c> (both shop
    /// slots). Returns <paramref name="picked"/> unchanged for every character
    /// but the stand-in's own, and with the arm off.
    ///
    /// THE BANNER IS NOT A MOUTH, deliberately. It decides WHICH five-stars are
    /// featured, and it decides that about Universals; a stand-in carries a
    /// <c>PersonalPool</c>, which the banner's roster excludes by the same rule
    /// that keeps Klee's Personals off it.
    /// </summary>
    internal static CardModel HandOff(CardModel picked, Player player)
    {
        if (!CompanionOverhaul.Enabled) return picked;
        return HandOffTo(picked, CompanionPool.CharacterId(player), Pairs());
    }

    /// <summary>
    /// THE DECISION, with the pair table handed in instead of resolved, and
    /// the only reason it is a second method is that the PINS could not reach
    /// the first: <see cref="Pairs"/> goes through <c>ModelDb</c> and
    /// <see cref="HandOff"/> takes a <c>Player</c>, both outside the headless
    /// boundary (KleeTests/README), so the seam's own rule had no C# pin at all
    /// -- which is how it shipped broken. `CompanionStandInHandOffTests` calls
    /// THIS with two cards it constructed itself.
    ///
    /// THE COMPARISON IS THE WHOLE RULE, and it is a STRING one: the stand-in's
    /// <c>PersonalPool</c> must BE the character id
    /// <see cref="CompanionPool.CharacterId"/> returns. It was not. The codegen
    /// emitted a Python list repr (<c>"['klee']"</c>) for a row that spells
    /// `personal_pool:` as a one-member list, so this loop matched the pair,
    /// failed the second test and handed Klee the Universal at both mouths --
    /// silently, and in the engine the player plays, while the sim swapped
    /// correctly the whole time (`tools/gen_klee_cards.personal_pool_id` is the
    /// fix and `tier0.engine.state.Card.from_dict` the twin it was missing).
    /// </summary>
    public static CardModel HandOffTo(
        CardModel picked, string? characterId,
        IReadOnlyList<(CardModel Universal, CardModel StandIn)> pairs)
    {
        if (!CompanionOverhaul.Enabled) return picked;
        if (characterId == null) return picked;
        foreach (var (universal, standIn) in pairs)
        {
            if (!ReferenceEquals(universal, picked)) continue;
            if ((standIn as ICompanionCard)?.PersonalPool != characterId)
            {
                continue;
            }
            return standIn;
        }
        return picked;
    }

    // ---- the four caretakers' rules -------------------------------------

    /// <summary>
    /// One explosion landed: pay whichever this-turn watcher is armed.
    /// <c>companion_standins.note_explosion</c>'s twin, called from
    /// <c>ProtoBombPower.Explode</c> beside <c>NoteExplosion</c>.
    ///
    /// NOT ON THE EXPLOSION BUS (<c>IProtoExplosionListener</c>), and that is
    /// the one design note here: the bus carries no Mine flag, and Noelle's
    /// card is about Mines. Widening the Klee arm's own interface for one
    /// companion stand-in would put this arm's rule inside that one.
    /// </summary>
    internal static async Task OnExplosion(
        PlayerChoiceContext choiceContext, Creature applier, bool isMine)
    {
        if (!CompanionOverhaul.Enabled) return;
        foreach (var power in applier.Powers.ToList())
        {
            switch (power)
            {
                case ShakenNotPurredPower shaken:
                    await shaken.Pay();
                    break;
                case IGotYourBackPower back when isMine:
                    await back.Pay();
                    break;
            }
        }
    }

    /// <summary>
    /// Does Grounded see nothing this turn? Kaeya's Cold-Blooded Strike, read
    /// by <c>GroundedPower</c> and by nothing else -- the card names Grounded,
    /// so the blind is a READ here rather than a write to the explosion
    /// counter, which Jean's stand-in also reads.
    /// </summary>
    internal static bool GroundedBlind(Creature owner) =>
        CompanionOverhaul.Enabled && StandInLedger.For(owner).GroundedBlind;
}

/// <summary>
/// THE STAND-INS' TURN BOUNDARY, and it holds exactly one fact: whether
/// Grounded is blind this turn.
///
/// A SECOND LEDGER BESIDE <see cref="KleeOverhaulLedger"/>, not a field on it,
/// because the two arms ship independently: the Klee overhaul's counters are
/// rule 7's and exist with the companion arm off, and a companion stand-in's
/// marker must not be a field the Klee arm carries in a build that cannot
/// reach one. Same shape, same argument, same self-correcting round stamp --
/// see that class's header for why the roll is on READ rather than on a hook.
///
/// THE ROLL IS THE SPEND. Kaeya's card is played during round N and Grounded
/// asks at the start of round N+1, so the marker has to survive the enemy's
/// half; the roll reads it once at the boundary and caches the answer for the
/// round, which is what makes the read order-independent among the powers that
/// fire on one broadcast.
/// </summary>
internal sealed class StandInLedger
{
    private static object? _combat;
    private static readonly Dictionary<Creature, StandInLedger> _byOwner = new();

    private int _round = -1;

    /// <summary>Grounded's blind, for the round this ledger is rolled to.</summary>
    public bool GroundedBlind { get; private set; }

    public static StandInLedger For(Creature owner)
    {
        var combat = (object?)owner.CombatState;
        if (!ReferenceEquals(_combat, combat))
        {
            _combat = combat;
            _byOwner.Clear();
        }
        if (!_byOwner.TryGetValue(owner, out var ledger))
        {
            ledger = new StandInLedger();
            _byOwner[owner] = ledger;
        }
        ledger.RollTo(owner.CombatState?.RoundNumber ?? 0, owner);
        return ledger;
    }

    /// <summary>Test seam: forget everything. The mod never calls it.</summary>
    public static void ResetAll()
    {
        _combat = null;
        _byOwner.Clear();
    }

    /// <summary>Roll to <paramref name="round"/>. Public to the pins so a turn
    /// boundary can be exercised without a combat.</summary>
    public void RollTo(int round, Creature owner)
    {
        if (round == _round) return;
        // The marker is READ off the creature here rather than pushed by the
        // card, so the answer does not depend on an apply-time hook firing --
        // and a jump of more than one round means the owner had no turn in
        // between, which is honestly not blind.
        GroundedBlind = round == _round + 1
                        && owner.Powers.Any(p => p is ColdBloodedPower);
        _round = round;
    }
}

/// <summary>
/// Diona, Shaken, Not Purred: "Gain 6 Block. Apply Cryo twice. If a Bomb goes
/// off this turn, gain 5 Block."
///
/// ONE-SHOT, and the stack is the BLOCK it pays -- the row's own printed
/// number, so the Prototype-stage upgrade rule moves it like any other.
///
/// A CONDITIONAL WITH NO ORDERING WORD IS TRUE BOTH WAYS. "If a Bomb goes off
/// this turn" says nothing about before or after, so the generated card pays at
/// once when one already has (<c>KleeOverhaulLedger.SetOffThisTurn</c>, read in
/// <see cref="AfterCardPlayed"/>) and otherwise waits for the first explosion of
/// the turn. Either way the promise is kept once.
/// </summary>
public sealed class ShakenNotPurredPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Shaken, Not Purred"),
        ("description",
            "The next time one of your [gold]Bombs[/gold] goes off this turn, "
          + "gain [blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Pay and go. Called by <see cref="CompanionStandIns.OnExplosion"/>
    /// on any explosion, Mine or not -- a Mine is a Bomb.</summary>
    internal async Task Pay()
    {
        if (Owner == null || Amount <= 0) return;
        // NC-11: power-sourced BLOCK stays raw; only power-sourced DAMAGE runs
        // the pipeline (NC-1).
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null,
                                    fast: true);
        await PowerCmd.Remove(this);
    }

    /// <summary>The card was played on a turn a Bomb had ALREADY gone off: the
    /// condition is about the turn, so it is already true.</summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null) return;
        if (KleeOverhaulLedger.For(Owner).SetOffThisTurn <= 0) return;
        await Pay();
    }

    /// <summary>"This turn" ends where the arm's counters roll -- the start of
    /// the owner's next turn, which leaves the enemy's half inside the window
    /// on purpose (a Mine goes off when an ENEMY attacks).</summary>
    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Noelle, I Got Your Back: "Gain 6 Block. Whenever a Mine goes off this turn,
/// gain 4 Block."
///
/// REPEATING, and MINES ONLY. "Whenever" is forward-looking and pays per Mine,
/// which is the one place this card differs from Diona's above it.
/// </summary>
public sealed class IGotYourBackPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "I Got Your Back"),
        ("description",
            "Whenever one of your [gold]Mines[/gold] goes off this turn, gain "
          + "[blue]{Amount}[/blue] [gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    internal async Task Pay()
    {
        if (Owner == null || Amount <= 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null,
                                    fast: true);
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Kaeya, Cold-Blooded Strike: "Deal 8 damage. Apply Cryo. This turn, Grounded
/// counts nothing as having gone off."
///
/// A MARKER, and its stack is a flag rather than a number -- which is why the
/// sheet row states its own upgrade instead of letting the Prototype-stage
/// rule move an amount nothing reads.
///
/// IT ROLLS THE LEDGER BEFORE IT LEAVES, and that is the whole of why the read
/// is race-free. Both this power and <c>GroundedPower</c> fire on
/// <c>AfterPlayerTurnStart</c>, whose listener order is not guaranteed; asking
/// <see cref="CompanionStandIns.GroundedBlind"/> first forces
/// <see cref="StandInLedger"/> to roll and CACHE the answer for the round while
/// this power is still on the creature, so Grounded reads the same true
/// whichever of the two ran first.
/// </summary>
public sealed class ColdBloodedPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Cold-Blooded"),
        ("description", "This turn, Grounded counts nothing as having gone off."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        CompanionStandIns.GroundedBlind(Owner);      // roll, and cache, first
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Jean, Lion's Fang, Fair Protector: "At the start of your turn, if none of
/// your Bombs went off last turn, gain 8 Block and draw 1 card."
///
/// GROUNDED'S SHAPE WITH A CARD ON IT, and it reads the ledger the same way for
/// the same reason: <c>For</c> rolls to this round, so <c>SetOffLastTurn</c> is
/// exactly the count that stood when the player last passed.
///
/// IT DOES NOT READ KAEYA'S BLIND. That card names Grounded, and a marker that
/// quietly paid a second power would be a rule the player was never shown.
/// </summary>
public sealed class LionsFangPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lion's Fang, Fair Protector"),
        ("description",
            "At the start of your turn, if none of your [gold]Bombs[/gold] "
          + "went off last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and draw 1 card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        if (Amount <= 0) return;
        if (KleeOverhaulLedger.For(Owner).SetOffLastTurn > 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
        // A LITERAL 1, in both engines and for the reason tier0's
        // `MC_LIONS_FANG_DRAW` comment gives: naming it would make
        // `lint_prose_constants` read every "Draw 1 card" in the mod as an
        // un-interpolated copy of this slice's constant. The row's own
        // `description:` is what both engines print.
        await CardPileCmd.Draw(choiceContext, 1, player);
    }
}
