using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
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
/// THE FAMILY MARK, AS A TYPE. A generated card whose sheet row carries
/// <c>hexerei: true</c> implements this and nothing else does.
///
/// A MARKER WITH NO MEMBERS, because the mark decides exactly one question --
/// "is the card you just played in the family" -- and three readers now ask
/// it: Nicole's <see cref="LadderOfAscentPower"/>, R244's
/// <see cref="WitchesCirclePower"/> and R244's Coven Errand (through the
/// ledger). Its element comes off
/// <see cref="ICompanionCard.CompanionElement"/>, which every Hexerei row
/// already carries as a Universal or a stand-in; a Klee pool row that joins
/// the family carries none and deals plain damage (R236 pick 6).
///
/// THE TYPE IS THE PRINTED HALF OF THE ANSWER AND NOT THE WHOLE OF IT since
/// R244: Alice's Introduction Magic widens the family to a hand for one turn,
/// so every reader asks <see cref="CompanionHexerei.IsHexerei"/> rather than
/// testing this interface itself.
///
/// BY INTERFACE RATHER THAN BY A LIST OF IDS, for
/// <see cref="CompanionStandIns"/>' reason: the compiler owns the
/// correspondence, so a row deleted from the surface takes its class with it
/// and this arm stops building, where a table of id strings would fail
/// silently. The sim answers the same question with <c>Card.hexerei</c>, off
/// the same sheet key, and `tier0/tests/test_companion_overhaul.py` names the
/// one module allowed to read it.
///
/// IT LIVES UNDER Powers/Prototype, which a release build removes -- and every
/// row carrying the mark is a `proto_` row compiled under the same switch, so a
/// shipped card can never implement it.
/// </summary>
public interface IHexereiCard
{
}

/// <summary>
/// THE HEXEREI MARK AND ITS READERS (QUARANTINED, two arms).
///
/// Four stand-ins on the seam <see cref="CompanionStandIns"/> opened, and this
/// file exists for that file's reason: a quarantined arm's whole behaviour
/// should be greppable in one place. That one holds the SEAM (the pair table,
/// the hand-off) and the four CARETAKERS' rules; this one holds the four FAMILY
/// stand-ins' rules, THE FAMILY MARK ITSELF, and nothing else.
///
/// WHAT A FAMILY STAND-IN IS. The caretakers read the Klee overhaul's explosion
/// ledger, which is what a caretaker is for. These four read the REACTION,
/// because Hexerei is the reaction family (the approved Mondstadt workshop
/// sec.1; R236 sec.3). Each is handed to Klee in place of one Hexerei Universal
/// and wears its art; each is Hexerei-tagged itself, which is why Nicole's
/// power pays for the other three.
///
/// THE MARK IS SHARED AND THE READERS ARE NOT (R244). Until the ruled packet
/// `review/ruled/klee-hexerei-readers-2026-09-02.md` the family had exactly one
/// reader, Nicole's Ladder, on <c>COMPANION_OVERHAUL</c>. Its three Klee
/// readers sit on <c>KLEE_OVERHAUL</c> instead, so "is this play a Hexerei
/// card?" is a question two arms ask -- and <see cref="IsHexerei"/> is where it
/// is answered, once, with each reader gated on its own flag afterwards.
/// <see cref="IntroductionMagicPower"/> is the one rule that WIDENS the answer,
/// and it lives here for the same reason.
///
/// SIM TWIN: <c>tier0.engine.companion_hexerei</c>, called from the same two
/// mouths -- the one site a reaction resolves, and the card-played site.
/// </summary>
internal static class CompanionHexerei
{
    /// <summary>The three reactions Electro can be the TRIGGER of. Every other
    /// way Electro takes part is as the aura that was standing, which the
    /// caller hands over -- Anemo and Geo never stick as an aura, so the pair
    /// (reaction, consumed aura) names both elements and no signature had to
    /// widen for this slice. Sim twin: <c>_ELECTRO_REACTIONS</c>.</summary>
    private static readonly Reaction[] ElectroReactions =
    {
        Reaction.Overload, Reaction.Superconduct, Reaction.ElectroCharged,
    };

    /// <summary>The reactions that deal damage OF THEIR OWN: the two
    /// amplifiers and the Overload splash. This is
    /// <see cref="CompanionOverhaulReactions.DamageMultiplier"/>'s own
    /// boundary, cited rather than re-derived -- Sucrose's card ADDS to the
    /// quantity Durin's White MULTIPLIES, so the two must reach the same
    /// reactions or they stop being about one thing.</summary>
    private static readonly Reaction[] DamagingReactions =
    {
        Reaction.Vaporize, Reaction.Melt, Reaction.Overload,
    };

    /// <summary>"An Electro reaction is any reaction with Electro as either
    /// element" (R236 sec.3), answered from the reaction and the consumed
    /// aura.</summary>
    internal static bool IsElectroReaction(Reaction reaction, Element aura) =>
        ElectroReactions.Contains(reaction) || aura == Element.Electro;

    /// <summary>
    /// IS THIS CARD IN THE HEXEREI FAMILY RIGHT NOW? The mark's ONE reader,
    /// and every rule that pays for a witch asks it (R244).
    ///
    /// TWO WAYS IN, and they are deliberately different kinds of thing: the
    /// PRINTED mark is the <see cref="IHexereiCard"/> interface the codegen
    /// puts on a row carrying <c>hexerei: true</c>, and the this-turn window is
    /// <see cref="IntroductionMagicPower"/>'s set of card INSTANCES -- so a
    /// second copy of the same card drawn after the spell is not counted, which
    /// is the ruling's own derived reading and the reason its upgrade is
    /// Retain.
    ///
    /// UNGATED BY EITHER ARM'S FLAG, because it is a question about a card
    /// rather than a rule that pays out: with the arms off no row implements
    /// the interface and no power grants the window, so the answer is false by
    /// construction. Every reader below is gated on its own flag. Sim twin:
    /// <c>tier0.engine.companion_hexerei.is_hexerei</c>.
    /// </summary>
    internal static bool IsHexerei(CardModel? card)
    {
        if (card == null) return false;
        if (card is IHexereiCard) return true;
        var owner = card.Owner?.Creature;
        if (owner == null) return false;
        return owner.Powers.OfType<IntroductionMagicPower>()
                    .Any(power => power.Marks(card));
    }

    /// <summary>
    /// Alice's Introduction Magic (R244): every card in hand joins the family
    /// for this turn.
    ///
    /// THE CARDS IN HAND WHEN IT RESOLVES, and no others. The card marks the
    /// hand it was played from, so the way to hold it for a big hand is the
    /// upgrade's Retain and not a later draw.
    ///
    /// THE SPELL COUNTS ITSELF, which is the ruling's second derived reading,
    /// and it needs no line here: its row carries <c>hexerei: true</c>, so it
    /// is in the family printed rather than by this set -- and a card being
    /// played has already left the hand, so marking the hand could not reach
    /// it.
    ///
    /// ONE POWER, RE-ENTERED: <see cref="PowerCmd.Apply"/> stacks onto the
    /// standing instance, so a second cast adds its hand to the same set rather
    /// than opening a second window with its own expiry.
    /// Sim twin: <c>companion_hexerei.mark_hand</c>.
    /// </summary>
    internal static async Task MarkHand(
        PlayerChoiceContext choiceContext, Player owner)
    {
        // THE PLAYER, not the Creature, and the pile is why: `CardPile.Get`
        // is keyed on the seat that holds the cards, exactly as every other
        // hand-reading card in this mod calls it. The power lands on the
        // creature underneath.
        var hand = CardPile.Get(PileType.Hand, owner);
        var klee = owner.Creature;
        if (hand == null || klee == null) return;
        var applied = await PowerCmd.Apply<IntroductionMagicPower>(
            choiceContext, klee, 1, applier: klee, cardSource: null);
        var window = applied as IntroductionMagicPower
                     ?? klee.Powers.OfType<IntroductionMagicPower>()
                            .FirstOrDefault();
        if (window == null) return;
        foreach (var card in hand.Cards) window.Mark(card);
    }

    /// <summary>
    /// A card was played: if it is Hexerei, the arm's ledger counts it.
    ///
    /// Called from <c>KleeOverhaulSweepHooks.AfterCardPlayed</c>, which is this
    /// arm's ONE standing card-play listener -- a second
    /// <c>AbstractModel</c> subscription for one counter would be a second
    /// thing to keep registered, for no rule the first one cannot carry. The
    /// PAYOUTS are not here: <see cref="LadderOfAscentPower"/> and
    /// <see cref="WitchesCirclePower"/> each hook themselves, which is this
    /// mod's idiom and what keeps a power that is not on the board from being
    /// asked about. The sim has one sequential site and does both there
    /// (<c>klee_overhaul.note_hexerei_played</c>), the same arrangement its
    /// explosion bus already has.
    /// </summary>
    internal static void NoteCardPlayed(CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled) return;
        if (!IsHexerei(cardPlay.Card)) return;
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null) return;
        KleeOverhaulLedger.For(owner).NoteHexereiPlayed();
    }

    /// <summary>
    /// A reaction has just resolved: pay Albedo, then Sucrose, then Fischl.
    ///
    /// Called from <see cref="CompanionOverhaulReactions.Note"/>, which is the
    /// ONE place the mod resolves a reaction
    /// (<c>ReactionEffects.Resolve</c>) -- so "a reaction happened" keeps one
    /// definition in this engine too, and these three readers cannot disagree
    /// with the arm's other two about it.
    ///
    /// THE UNELEMENTED TWO FIRST, and the order is stated rather than
    /// incidental: Albedo's and Sucrose's hits carry no element and cannot
    /// chain, so paying them first means the board Fischl's volley draws from
    /// is the one they left. The sim pays in the same order at its own single
    /// sequential site.
    ///
    /// FISCHL'S VOLLEY MAY FIRE FROM INSIDE THE REACTION SITE even though it
    /// deals ELECTRO and can therefore react again: each chained firing spends
    /// one standing aura and creates none, and a volley that instead APPLIES
    /// Electro to a bare enemy causes no reaction, so the chain is bounded by
    /// the enemies on the board. The sim's module header argues the same bound
    /// plus the one hazard that is the sim's alone (its reaction event is
    /// emitted after this call).
    /// </summary>
    internal static async Task OnReaction(
        PlayerChoiceContext choiceContext, Reaction reaction, Creature target,
        Creature? dealer, Element consumedAura)
    {
        if (!CompanionOverhaul.Enabled || dealer == null) return;

        // NC-1 for all three: power-sourced DAMAGE runs the pipeline.
        foreach (var tide in dealer.Powers.OfType<TectonicTidePower>().ToList())
        {
            if (target.IsDead) break;
            // NO ELEMENT -- the card names none, the same call Solar Isotoma
            // (the Universal this stands in for) already made, so it can
            // neither consume an aura nor start a second reaction.
            await InazumaCompanion.DealUnelemented(
                choiceContext, target, (int)tide.Amount, dealer);
        }

        if (DamagingReactions.Contains(reaction))
        {
            foreach (var gust in
                     dealer.Powers.OfType<MollisFavoniusPower>().ToList())
            {
                if (target.IsDead) break;
                // ON THE REACTED ENEMY, ONCE -- including Overload, whose
                // splash is spread over the board: "the reaction deals 4
                // additional damage" is one promise about one reaction, not
                // one per body it splashed.
                await InazumaCompanion.DealUnelemented(
                    choiceContext, target, (int)gust.Amount, dealer);
            }
        }

        if (!IsElectroReaction(reaction, consumedAura)) return;
        var combat = dealer.CombatState;
        if (combat == null) return;
        foreach (var hex in dealer.Powers.OfType<SinfulHexPower>().ToList())
        {
            var victim = CompanionOverhaulTargeting.RandomEnemy(combat);
            if (victim == null) break;
            await ElementalHit.Deal(
                choiceContext, victim, Element.Electro, hex.Amount, dealer);
        }
    }
}

/// <summary>
/// Albedo, Tectonic Tide: "Whenever a reaction happens, deal 4 damage to that
/// enemy."
///
/// ANY reaction, exactly as Dahlia's Favonian Favor counts any; the card names
/// none. The stack is the DAMAGE, so a second copy pays twice, and the printed
/// number is the row's -- which is what lets the Prototype-stage upgrade rule
/// move it.
///
/// THE POWER HOOKS NOTHING. It is read at the one reaction site
/// (<see cref="CompanionHexerei.OnReaction"/>), which is
/// <see cref="BinaryFormWhitePower"/>'s argument for its own shape: a power
/// whose whole job is to be present and countable does not need a broadcast.
/// </summary>
public sealed class TectonicTidePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Tectonic Tide"),
        ("description",
            "Whenever an [gold]Elemental Reaction[/gold] happens, deal "
          + "[blue]{Amount}[/blue] damage to that enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

/// <summary>
/// Fischl, Undone Be Thy Sinful Hex: "Whenever an Electro reaction happens this
/// turn, deal 5 Electro damage to a random enemy."
///
/// REPEATING and THIS TURN, which puts it in Favonian Favor's shape rather than
/// in the caretakers': "this turn" ends in <c>AfterSideTurnEnd</c>, the shipped
/// <c>AttackUpThisTurnPower</c>'s own window. The caretakers close at the turn
/// START instead, because a Mine goes off when an ENEMY attacks and their
/// promises have to survive the enemy's half; a reaction card's does not -- the
/// player is the only side that makes reactions happen.
/// </summary>
public sealed class SinfulHexPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Sinful Hex"),
        ("description",
            "Whenever an [gold]Electro[/gold] [gold]Elemental Reaction[/gold] "
          + "happens this turn, deal [blue]{Amount}[/blue] [gold]Electro[/gold] "
          + "damage to a random enemy."),
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
/// Sucrose, Mollis Favonius: "This turn, reactions deal 4 additional damage."
///
/// THE ADDITIVE HALF OF DURIN'S WHITE SENTENCE, and it is delivered at the
/// reaction site rather than folded into the amplifier. White is a MULTIPLIER
/// and this engine's amplifier is a multiplier too
/// (<c>AuraPower.ModifyDamageMultiplicative</c> returns a factor, with no
/// damage to add a constant to), while the additive phase runs BEFORE the
/// amplifier -- so a flat 4 put there would be scaled by the Vaporize and the
/// sim's own 4 would not. Beside the reaction is the one place both engines
/// land on the same number.
///
/// THE ORDER, since the two stack: MULTIPLY FIRST, ADD AFTER. White scales the
/// reaction's own contribution inside the pipeline; this adds its 4 afterwards,
/// so White never scales the 4 and the 4 never enters an amplifier.
///
/// IT REACHES THE REACTIONS THAT DEAL DAMAGE, which is White's boundary --
/// see <see cref="CompanionHexerei"/>'s table.
/// </summary>
public sealed class MollisFavoniusPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Mollis Favonius"),
        ("description",
            "This turn, [gold]Elemental Reactions[/gold] deal "
          + "[blue]{Amount}[/blue] additional damage."),
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
/// Nicole, Ladder of Divine Ascent: "Whenever you play a Hexerei card, deal 6
/// damage of that card's element to a random enemy."
///
/// THE FAMILY MARK'S FIRST READER IN THIS ENGINE, and it reads a TYPE
/// (<see cref="IHexereiCard"/>) rather than a list of ids -- see that
/// interface for why. The sim reads <c>Card.hexerei</c> off the same sheet key.
///
/// A HEXEREI CARD WITH NO ELEMENT DEALS PLAIN DAMAGE (R236 pick 6), which is
/// <c>Element.None</c> here and <c>element=None</c> in the sim.
///
/// NICOLE'S OWN CARD IS HEXEREI, so playing it pays once for itself. That is
/// not a special case: <c>AfterCardPlayed</c> reaches a power the card just
/// applied -- the contract Diona's stand-in already leans on
/// (<c>ShakenNotPurredPower.AfterCardPlayed</c>) -- and the sim's site runs
/// after the card's effects for the same reason.
/// </summary>
public sealed class LadderOfAscentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ladder of Divine Ascent"),
        ("description",
            "Whenever you play a [gold]Hexerei[/gold] card, deal "
          + "[blue]{Amount}[/blue] damage of that card's element to a random "
          + "enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (Owner == null) return;
        if (cardPlay.Card?.Owner?.Creature != Owner) return;
        // THROUGH THE MARK'S ONE READER since R244, not the interface: Alice's
        // Introduction Magic widens the family for a turn, and a Ladder that
        // tested the type itself would be the second definition of "Hexerei"
        // this file exists to prevent.
        if (!CompanionHexerei.IsHexerei(cardPlay.Card)) return;
        var element = (cardPlay.Card as ICompanionCard)?.CompanionElement
                      ?? Element.None;
        var target = CompanionOverhaulTargeting.RandomEnemy(CombatState);
        if (target == null) return;
        if (element == Element.None)
        {
            await InazumaCompanion.DealUnelemented(
                choiceContext, target, (int)Amount, Owner);
            return;
        }
        await ElementalHit.Deal(choiceContext, target, element, Amount, Owner);
    }
}

/// <summary>
/// Alice's Introduction Magic (R244, the ruled packet's sec.2): "All cards in
/// your hand count as Hexerei cards this turn."
///
/// KLEE'S OWN RARE, not a companion stand-in, and it is the enabler the three
/// readers are priced against: played first, every card after it this turn is a
/// witch's card, so <see cref="WitchesCirclePower"/> plants a Bomb per play,
/// Coven Errand goes wide, Nicole's Ladder fires per card, and the coven bonus
/// lines on the Personals read as met.
///
/// THE WINDOW IS OVER CARD INSTANCES, WHICH IS WHY THE POWER HOLDS A SET. The
/// ruling's two derived readings are exactly the two things this shape gives:
/// the window covers the cards that WERE in hand when it resolved (a card drawn
/// later this turn is not counted, so Retain on the upgrade is the way to hold
/// it for the big hand), and the spell counts as Hexerei itself -- which its
/// row's own <c>hexerei: true</c> says, so it does not need a second witch to
/// start a circle.
///
/// A SET AND NOT A LIST OF IDS: two copies of one card in hand are two
/// instances, and only the ones the spell saw are in the family. Reference
/// identity is the right comparison and the default one.
///
/// THE WINDOW ENDS WITH THE POWER, at <c>AfterSideTurnEnd</c> -- the shipped
/// <c>AttackUpThisTurnPower</c>'s own window, and the same one the two Hexerei
/// stand-ins above take. Removing the power drops the set, so no mark can
/// outlive the turn that wrote it on a card sitting in the discard pile. Sim
/// twin: <c>CombatState.ko_hexerei_marked</c>, dropped at
/// <c>klee_overhaul.turn_end</c>.
/// </summary>
public sealed class IntroductionMagicPower : PowerModel, ILocalizationProvider
{
    private readonly HashSet<CardModel> _marked = new();

    public List<(string, string)>? Localization => new()
    {
        ("title", "Introduction Magic"),
        ("description",
            "The cards that were in your hand count as [gold]Hexerei[/gold] "
          + "cards this turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>This card joins the family for the rest of the turn.</summary>
    internal void Mark(CardModel card) => _marked.Add(card);

    /// <summary>Is this card INSTANCE inside the window?</summary>
    internal bool Marks(CardModel card) => _marked.Contains(card);

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        _marked.Clear();
        await PowerCmd.Remove(this);
    }
}
