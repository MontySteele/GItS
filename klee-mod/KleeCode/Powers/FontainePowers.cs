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

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner?.Creature != Owner) return;
        if (!cardPlay.IsFirstInSeries) return;

        await CreatureCmd.GainBlock(
            Owner, Amount, ValueProp.Unpowered, null, fast: true);
    }
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
          + "{Amount} more damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
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
            "Elemental auras you apply last {Amount} extra "
          + "turn{Amount:plural:|s}."),
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
            "At the start of each turn, gain {Amount} [gold]Strength[/gold]. "
          + "Each turn your [gold]Bond of Life[/gold] consumes the first "
          + $"{CompanionConstants.MasqueBondBlock} [gold]Block[/gold] you "
          + "gain."),
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

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner == null || Owner.Block <= 0) return;
        var paid = System.Math.Min(
            Owner.Block, CompanionConstants.MasqueBondBlock);
        await CreatureCmd.LoseBlock(Owner, paid);
    }
}
