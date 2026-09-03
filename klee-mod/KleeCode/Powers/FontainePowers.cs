using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
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
/// The four Fontaine 5-star Rares (R64, 2026-07-25). Sim is LAW: each of these
/// mirrors a tier0 power by name, and the amounts live on the card, not here,
/// so there is nothing for the constant-parity lint to drift on.
/// </summary>

/// <summary>
/// Navia, Cannon Fire Support: whenever you play a Companion card, gain Block.
///
/// The only trigger in the game keyed on a CARD TYPE rather than an element,
/// which is deliberate -- it is what keeps her clear of the Crystallize
/// archetype Zhongli's slot-4 deep dive owns.
///
/// ORDERING DIVERGENCE, recorded rather than hidden. tier0 grants the Block in
/// combat.play_card BEFORE resolve_card runs; this fires AfterCardPlayed,
/// because BeforeCardPlayed on PowerModel is not an async/choiceContext hook
/// and cannot award Block. The two orders differ only for a companion card
/// that READS the player's Block during its own resolution, and no companion
/// card in any sheet does (the pool's Block cards all write). If one is ever
/// written, this is the note that says where to look.
///
/// SELF-PAYMENT, closed EB-19/M5. That divergence had a second consequence the
/// note above missed: NAVIA'S OWN PLAY paid itself. The sim says explicitly
/// that it must not -- combat.py play_card reads
/// `p.powers.get("cannon_fire_support")` beside the companions_played record
/// site, ahead of resolve_card, with the comment "Sitting before resolve_card
/// also means Navia's own play does not pay itself: the power is not up yet."
/// The C# read is a LISTENER ENUMERATION, not a power read, and the decompile
/// says that enumeration happens too late to agree:
///
///   CardModel.PlayInternal  ->  Hook.BeforeCardPlayed(combatState, cardPlay)
///                           ->  OnPlay(...)          // the power is ADDED here
///                           ->  Hook.AfterCardPlayed(combatState, ...)
///
/// and both Hook methods `foreach` over `CombatState.IterateHookListeners()`,
/// an ITERATOR that materializes its `List&lt;AbstractModel&gt;` (creature
/// Powers, relics, potions, piles, modifiers) inside its first MoveNext --
/// i.e. at the moment the foreach starts, not when the play started. So a
/// power added during OnPlay is absent from the BeforeCardPlayed list and
/// PRESENT in the AfterCardPlayed one. (Hook.BeforeCardPlayed goes through
/// IterateCombatHookListeners, which is the same enumeration behind a
/// combat-is-over guard.)
///
/// The fix uses exactly that asymmetry as the signal. BeforeCardPlayed records
/// the CardPlay it saw; AfterCardPlayed pays only for a CardPlay in that set.
/// Navia's own play never entered it, so it never pays -- while every LATER
/// companion play does. A set rather than a field because card plays nest (a
/// card that plays a card), and CardPlay is a class with reference identity,
/// one fresh instance per play index (CardPlay.cs, `new CardPlay { ... }` per
/// `i` in the playCount loop), so entries can never collide or go stale.
///
/// IsFirstInSeries: one grant per card PLAY, not per replay. Study Buddy's
/// replay is one card resolved twice; paying it twice would make those two
/// cards a combo instead of each doing its own job -- the same line tier0
/// draws by granting once beside its companions_played record site, outside
/// the replay loop.
/// </summary>
public sealed class CannonFireSupportPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Cannon Fire Support"),
        ("description",
            "Whenever you play a [gold]Companion[/gold] card, gain {Amount} "
          + "[gold]Block[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// The plays this power was already installed for, snapshotted at the one
    /// broadcast that runs before the card resolves. Reference identity on
    /// CardPlay; every entry is removed by the AfterCardPlayed of the same
    /// play, so this holds only the plays currently open (normally one).
    /// </summary>
    private readonly HashSet<CardPlay> _presentAtPlayStart = new();

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (Eligible(cardPlay)) _presentAtPlayStart.Add(cardPlay);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Remove unconditionally: a play that resolved is closed whether or
        // not it pays, and an entry left behind would outlive its CardPlay.
        var wasPresent = _presentAtPlayStart.Remove(cardPlay);
        if (!wasPresent) return;
        if (!Eligible(cardPlay)) return;

        await CreatureCmd.GainBlock(
            Owner, Amount, ValueProp.Unpowered, null, fast: true);
    }

    /// <summary>
    /// Asked at both ends so the snapshot and the settle agree. Re-asked at
    /// AfterCardPlayed because ownership can change mid-play (a card handed
    /// to another player), and the sim's read is of the player who played it.
    /// </summary>
    private bool Eligible(CardPlay cardPlay) =>
        cardPlay.Card is ICompanionCard
        && cardPlay.Card.Owner?.Creature == Owner
        && cardPlay.IsFirstInSeries;
}

/// <summary>
/// Clorinde, Night Vigil: your Attacks against enemies holding an aura deal
/// +Amount.
///
/// DELIBERATE MIRROR of <see cref="SolarIsotomaPower"/>: same trigger ("my
/// attack lands on an aura'd enemy"), opposite currency -- Albedo pays Block,
/// Clorinde pays damage. Recorded here and on the sheet so the pairing reads
/// as design rather than as one being a copy of the other.
///
/// Read in ModifyDamageAdditive, which runs before the hit resolves and so
/// before the aura it keys on is consumed -- the identical ordering constraint
/// Solar Isotoma has, for the identical reason.
/// </summary>
public sealed class NightVigilPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Night Vigil"),
        ("description",
            "Your Attacks against enemies holding an elemental aura deal "
          + "[blue]{Amount}[/blue] additional damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner || target == null) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        if (AuraCmd.Find(target) == null) return 0m;
        return Amount;
    }
}

/// <summary>
/// Neuvillette, Heir to the Ancient Sea's Authority: auras you apply last
/// Amount extra turns.
///
/// A marker power with no hook of its own -- AuraCmd.Duration reads it at the
/// one place aura duration is decided, which is why that helper exists. It is
/// authority over water, not more water: it applies no element itself, and
/// must not, or it would re-open the mass-Frozen watchlist that the Guest Star
/// judgment card deliberately priced with self-damage.
/// </summary>
public sealed class AncientSeaAuthorityPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Heir to the Ancient Sea's Authority"),
        ("description",
            "Elemental auras you apply last [blue]{Amount}[/blue] extra "
          + "{Amount:plural:turn|turns}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Extra aura turns this creature grants, 0 if none.</summary>
    public static int ExtraTurnsFrom(Creature? applier) =>
        applier?.Powers.OfType<AncientSeaAuthorityPower>()
            .FirstOrDefault()?.Amount ?? 0;
}

/// <summary>
/// Arlecchino, Masque of the Red Death: at the start of each turn gain Amount
/// Strength, and each turn your Bond of Life eats the first
/// <see cref="CompanionConstants.MasqueBondBlock"/> Block you gain.
///
/// Both halves are PER TURN. Amount is Strength per turn -- a ratchet, like
/// Nicole's celestial_gift -- and the Bond is a flat constant that does not
/// scale with it.
///
/// THE BOND IS PAID AT TURN END, NOT AT THE GAIN SITE, mirroring tier0
/// exactly. Eating the first N at the moment Block is gained would need a
/// funnel neither layer has, and the arithmetic is identical either way:
/// eating the first N leaves max(0, gained - N), and so does subtracting N at
/// the end and clamping at zero. Paying at the end is also universal, so Block
/// from a power (Navia, Crystallize, Metallicize) cannot dodge the Bond the
/// way a card-only funnel would let it.
///
/// The two orders differ only for a card that READS current Block mid-turn
/// (the sim's `player_block` token -- Body Slam). That is reference-pool only
/// and the refs take no companions, so the divergence is unreachable; the note
/// exists so a future Block-reading roster card knows to revisit this.
///
/// Strength is granted through the ordinary power path, which is what makes
/// Kokomi's LAW 3 chokepoint convert it to Charge for her without a
/// special case anywhere.
/// </summary>
public sealed class MasqueRedDeathPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Masque of the Red Death"),
        ("description",
            "At the start of your turn, gain [blue]{Amount}[/blue] "
          + "[gold]Strength[/gold]. Your [gold]Bond of Life[/gold] eats the "
          + $"first [blue]{CompanionConstants.MasqueBondBlock}[/blue] "
          + "[gold]Block[/gold] you gain each turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await PowerCmd.Apply<StrengthPower>(
            choiceContext, Owner, Amount, applier: Owner, cardSource: null);
    }

    /// <summary>
    /// NOT A BROADCAST OVERRIDE ANY MORE (EB-19/races-a). Driven by
    /// TurnEndSequencer, which fires the four end-of-turn tenants that share
    /// the player's Block and the enemy reaction board in the sim's fixed
    /// order. The Bond is paid FIRST, strictly before the Kurage pulse's
    /// Block grant: tier0 `effects.player_turn_end_triggers` deducts
    /// MASQUE_BOND_BLOCK at the top of the function and only reaches
    /// `kurage_summon` afterwards, so on a Kokomi+Arlecchino board the Bond
    /// eats what the turn actually produced rather than the jellyfish's
    /// mending -- a 5-Block-per-turn swing when the two race.
    /// </summary>
    /// v0.111.0 (`EB-171`): `CreatureCmd.LoseBlock` now takes the choice
    /// context and the REMOVER. `remover: null` is the game's own documented
    /// "removed by a power" case, which is exactly what the Bond is; the
    /// context is the turn-end sequencer's, previously discarded at the
    /// `Resolve` delegate and now passed down.
    public async Task PayBondOfLife(PlayerChoiceContext choiceContext)
    {
        if (Owner == null || Owner.Block <= 0) return;
        var paid = System.Math.Min(
            Owner.Block, CompanionConstants.MasqueBondBlock);
        await CreatureCmd.LoseBlock(choiceContext, Owner, paid, remover: null);
    }
}
