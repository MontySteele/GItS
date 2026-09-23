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
/// THE COMPANION READERS AND THE WITCH FAMILY STAND-INS (QUARANTINED, two arms).
///
/// Four stand-ins on the seam <see cref="CompanionStandIns"/> opened, and this
/// file exists for that file's reason: a quarantined arm's whole behaviour
/// should be greppable in one place. That one holds the SEAM (the pair table,
/// the hand-off) and the four CARETAKERS' rules; this one holds the four FAMILY
/// stand-ins' rules and the one question every reader of a Companion play
/// asks.
///
/// WHAT A FAMILY STAND-IN IS. The caretakers read the Klee overhaul's explosion
/// ledger, which is what a caretaker is for. These four read the REACTION,
/// because the witches are the reaction family (the approved Mondstadt
/// workshop sec.1; R236 sec.3). Each is handed to Klee in place of one
/// Universal and wears its art.
///
/// R276 PICK 2 RETIRED THE HEXEREI MARK. The printed word and the
/// <c>hexerei:</c> sheet key are gone; every reader that paid for a "Hexerei
/// card" -- Klee's Spark, Coven Errand, Witches' Circle, Nicole's Ladder --
/// now pays for ANY Companion card, and Alice's Introduction Magic makes a
/// hand count as Companion cards for a turn. The file keeps its name because
/// the four family stand-ins still live here.
///
/// THE QUESTION IS SHARED AND THE READERS ARE NOT (R244). Nicole's Ladder is on
/// <c>COMPANION_OVERHAUL</c> and Klee's readers on <c>KLEE_OVERHAUL</c>, so
/// "does this play count as a Companion card?" is a question two arms ask --
/// and <see cref="CountsAsCompanion"/> is where it is answered, once, with each
/// reader gated on its own flag afterwards. <see cref="IntroductionMagicPower"/>
/// is the one rule that WIDENS the answer, and it lives here for the same
/// reason.
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
    /// DOES THIS CARD COUNT AS A COMPANION CARD RIGHT NOW? The one reader, and
    /// every rule that pays for a Companion play asks it (R244, R276).
    ///
    /// TWO WAYS IN, and they are deliberately different kinds of thing: the
    /// card IS a Companion (<see cref="ICompanionCard"/>, which the codegen
    /// puts on every companion row), or it is in
    /// <see cref="IntroductionMagicPower"/>'s this-turn set of card INSTANCES
    /// -- so a second copy of the same card drawn after the spell is not
    /// counted, which is the ruling's own derived reading and the reason its
    /// upgrade is Retain.
    ///
    /// UNGATED BY EITHER ARM'S FLAG, because it is a question about a card
    /// rather than a rule that pays out: every reader below is gated on its
    /// own flag. Sim twin:
    /// <c>tier0.engine.companion_hexerei.counts_as_companion</c>.
    /// </summary>
    internal static bool CountsAsCompanion(CardModel? card)
    {
        if (card == null) return false;
        if (card is ICompanionCard) return true;
        var owner = card.Owner?.Creature;
        if (owner == null) return false;
        return owner.Powers.OfType<IntroductionMagicPower>()
                    .Any(power => power.Marks(card));
    }

    /// <summary>
    /// Alice's Introduction Magic (R244, R276): every card in hand counts as a
    /// Companion card for this turn.
    ///
    /// THE CARDS IN HAND WHEN IT RESOLVES, and no others. The card marks the
    /// hand it was played from, so the way to hold it for a big hand is the
    /// upgrade's Retain and not a later draw.
    ///
    /// THE SPELL NO LONGER COUNTS ITSELF (R276). R244's derived reading rode
    /// the Hexerei key its row carried; the key is retired, the face says
    /// "all cards in your hand", and a card being played has already left the
    /// hand, so the literal reading is the one built.
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
    /// A card was played: if it counts as a Companion card, the arm's ledger
    /// counts it (Coven Errand's "if you played a Companion card this turn").
    ///
    /// Called from <c>KleeOverhaulSweepHooks.AfterCardPlayed</c>, which is this
    /// arm's ONE standing card-play listener -- a second
    /// <c>AbstractModel</c> subscription for one counter would be a second
    /// thing to keep registered, for no rule the first one cannot carry. The
    /// PAYOUTS are not here: <see cref="LadderOfAscentPower"/> and
    /// <see cref="WitchesCirclePower"/> each hook themselves, which is this
    /// mod's idiom and what keeps a power that is not on the board from being
    /// asked about. The sim has one sequential site and does both there
    /// (<c>klee_overhaul.note_companion_played</c>), the same arrangement its
    /// explosion bus already has.
    /// </summary>
    internal static void NoteCardPlayed(CardPlay cardPlay)
    {
        if (!KleeOverhaul.Enabled) return;
        if (!CountsAsCompanion(cardPlay.Card)) return;
        var owner = cardPlay.Card?.Owner?.Creature;
        if (owner == null) return;
        KleeOverhaulLedger.For(owner).NoteCompanionPlayed();
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
/// Nicole, Ladder of Divine Ascent: "Whenever you play a Companion card, deal
/// 6 damage of that card's element to a random enemy." (R276 pick 2 retired
/// the Hexerei mark it used to read; it reads the Companion question every
/// other reader asks.)
///
/// A CARD WITH NO ELEMENT DEALS PLAIN DAMAGE (R236 pick 6), which is
/// <c>Element.None</c> here and <c>element=None</c> in the sim -- a Klee card
/// Alice's Introduction Magic marked, for one.
///
/// NICOLE'S OWN CARD IS A COMPANION, so playing it pays once for itself. That is
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
            "Whenever you play a [gold]Companion[/gold] card, deal "
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
        // THROUGH THE ONE READER, not the interface: Alice's Introduction
        // Magic widens the set for a turn, and a Ladder that tested the type
        // itself would be a second definition of "a Companion card".
        if (!CompanionHexerei.CountsAsCompanion(cardPlay.Card)) return;
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
/// Alice's Introduction Magic (R244, R276): "All cards in your hand count as
/// Companion cards this turn."
///
/// KLEE'S OWN RARE, not a companion stand-in, and it is the enabler the three
/// readers are priced against: played first, every card that was in hand is a
/// Companion card for the turn, so <see cref="WitchesCirclePower"/> plants a
/// Bomb per play, Coven Errand goes wide, Klee's Spark pays, and Nicole's
/// Ladder fires per card.
///
/// THE WINDOW IS OVER CARD INSTANCES, WHICH IS WHY THE POWER HOLDS A SET: the
/// window covers the cards that WERE in hand when it resolved (a card drawn
/// later this turn is not counted, so Retain on the upgrade is the way to hold
/// it for the big hand). A SET AND NOT A LIST OF IDS: two copies of one card
/// in hand are two instances, and only the ones the spell saw count.
///
/// THE WINDOW ENDS WITH THE POWER, at <c>AfterSideTurnEnd</c>. Removing the
/// power drops the set, so no mark can outlive the turn that wrote it. Sim
/// twin: <c>CombatState.ko_companion_marked</c>, dropped at
/// <c>klee_overhaul.turn_end</c>.
/// </summary>
public sealed class IntroductionMagicPower : PowerModel, ILocalizationProvider
{
    private readonly HashSet<CardModel> _marked = new();

    public List<(string, string)>? Localization => new()
    {
        ("title", "Introduction Magic"),
        ("description",
            "The cards that were in your hand count as [gold]Companion[/gold] "
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
