using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S THREE WIRING SEAMS: what she starts the run holding, what she
/// starts it carrying, and what the game may offer her.
///
/// ONE SEAM EACH, on the terms every arm before this one took: the swap is
/// made at the one place the game asks the CHARACTER or rolls a reward, so no
/// list of surfaces has to be kept in step, and with
/// <see cref="FurinaStage.Enabled"/> off all three return the shipped answer
/// byte for byte -- the acceptance condition the quarantine rests on, pinned
/// rather than intended.
///
/// EVERY ROW IS THE SHEET'S, and both tables below are the sim's own mirrored
/// pair for pair: <c>furina_stage.STARTER_IDS</c> and
/// <c>furina_stage.POOL_SUBS</c> (with <c>POOL_ADDS</c> and
/// <c>PROMOTED_STARTERS</c> appended), read C#-side at the seams the
/// reframe's were.
/// The sheet is the authority for which shipped row each prototype row
/// replaces (`replaces:` on the row itself); these tables are that authority
/// in the language the mod's pools speak, which is classes.
/// </summary>
public static class FurinaStageRoster
{
    /// <summary>
    /// THE STARTER, rebuilt 2026-09-28 on the two overhaul arms' terms: the
    /// base game's Strike x4 and Defend x4 and two kit cards that teach the
    /// Stage. [USER]: "Typically we'd include 4 strikes, 4 defends and 2
    /// actually useful cards that teach the character's core mechanics - this
    /// seems like an unnecessary power spike." "I agree with keeping Curtain
    /// Raise and Rising Applause." "We should really just replace Soloist's
    /// Solicitation and Stage Presence with the basic strike and defend." And
    /// "The characters' kits should all use basic Strike and Defend."
    ///
    /// SILENT'S PAIR, for <c>KokomiOverhaulRoster</c>'s reason:
    /// <c>FurinaCardPool</c> borrows <c>card_frame_green</c> and the
    /// <c>silent</c> energy colour, so the base pair sits in her hand in her
    /// own frame, and <c>CardModel.Pool</c> resolves them to Silent's pool
    /// without a throw. The base Strike applies no element (a base card is
    /// not an <c>IElementalCard</c>, and [USER] ruled the basics apply
    /// nothing; <c>CatalystCadence</c> answers None for it).
    ///
    /// WHAT LEFT: Soloist's Solicitation, Stage Presence (both basics, never
    /// offered), Regal Bearing and Take the Stage -- the last two re-authored
    /// as Commons and offered in <see cref="Pool"/>. The shipped
    /// Furina's starter (<c>Furina.StartingDeck</c>'s own list) is unmoved.
    /// Sim twin: <c>furina_stage.STARTER_IDS</c>. The relic seam names the
    /// same pair once more (<see cref="StarterStrike"/>).
    /// </summary>
    public static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        // aria_of_recompense -> proto_fs_curtain_rise
        ModelDb.Card<ProtoFsCurtainRise>(),
        // an_invitation -> proto_fs_standing_ovation
        ModelDb.Card<ProtoFsStandingOvation>(),
    };

    /// <summary>
    /// THE PAIR ABOVE, NAMED ONCE MORE FOR THE RELIC SEAM (`EB-351`), on
    /// <c>KleeOverhaulRoster.StarterStrike</c>'s terms: Large Capsule and
    /// Fasten ask the character for "your Strike", and under the Stage the
    /// honest answer is the pair the starter opens with, not the shipped
    /// Soloist's Solicitation / Stage Presence. The seam is
    /// <see cref="ArmStarterBasics"/>; the correspondence is pinned by
    /// `ArmStarterBasicsTests.The_relic_pair_is_the_pair_the_starter_opens_with`.
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeSilent>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendSilent>();

    /// <summary>
    /// THE STARTING RELIC: Salon Solitaire replaces the Ethereal Spotlight.
    /// A replacement and not an addition -- the Spotlight in both modes is
    /// retired by this brief (sec.2), so a run carrying it would print a rule
    /// the arm has turned off.
    /// </summary>
    public static IReadOnlyList<RelicModel> StartingRelics() => new RelicModel[]
    {
        ModelDb.Relic<Relics.SalonSolitaire>(),
    };

    /// <summary>
    /// HER WHOLE OFFER under the Stage: <see cref="Pool"/>'s seventy-eight,
    /// her two Ancients and the co-op tier. What
    /// <c>FurinaCardPool.FilterThroughEpochs</c> returns, which IS
    /// <c>GetUnlockedCards</c> -- the sole door into reward rolls, the shop
    /// and transforms -- on <c>KleeOverhaulRoster.OfferablePool</c>'s terms.
    ///
    /// A LIST AND NOT A SWAP since legacy cleanup stage 4 (2026-10-01). The
    /// Stage used to offer the shipped sheet with every row printing a retired
    /// word dropped and named rows swapped for `proto_fs_` twins; by the rules
    /// pass nothing shipped survived that, so the pool is stated as what it
    /// is. Sim twin: <c>furina_stage.POOL_SUBS</c> / <c>POOL_ADDS</c>.
    /// </summary>
    public static IReadOnlyList<CardModel> OfferablePool() =>
        Pool().Concat(RosterAncientCards.Furina).Concat(MultiplayerRows())
            .ToList();

    /// <summary>
    /// THE SEVENTY-EIGHT, every one a `proto_fs_` row: 23 Commons, 35
    /// Uncommons and 20 Rares (pinned by `PoolCountTests`). In the order the
    /// batches arrived.
    /// </summary>
    public static CardModel[] Pool() => new CardModel[]
    {
        // Commons (five). The 2026-09-28 balance review cut
        // Gentilhomme Usher and Understudy (80 -> 78), and the
        // 2026-09-29 audit pass Scene Change. Sim twin:
        // `furina_stage.POOL_DROPS`.
        ModelDb.Card<ProtoFsSurintendanteChevalmarin>(),
        ModelDb.Card<ProtoFsMademoiselleCrabaletta>(),
        ModelDb.Card<ProtoFsWarmReception>(),
        ModelDb.Card<ProtoFsTidalFlourish>(),
        ModelDb.Card<ProtoFsInterposition>(),
        // Uncommons (five).
        ModelDb.Card<ProtoFsGrandEntrance>(),
        ModelDb.Card<ProtoFsOusiaSurge>(),
        ModelDb.Card<ProtoFsPneumaRefrain>(),
        ModelDb.Card<ProtoFsBis>(),
        ModelDb.Card<ProtoFsFinalBow>(),
        // Rare (one).
        ModelDb.Card<ProtoFsLetThePeopleRejoice>(),
        // R276 BATCH TWO. Commons (six).
        ModelDb.Card<ProtoFsImprovisedNumber>(),
        ModelDb.Card<ProtoFsBetweenActs>(),
        ModelDb.Card<ProtoFsEnsemblePiece>(),
        ModelDb.Card<ProtoFsHoldYourPlaces>(),
        ModelDb.Card<ProtoFsQuickCue>(),
        ModelDb.Card<ProtoFsStepForward>(),
        // Uncommons (five; the 2026-09-29 audit pass cut Gala Dinner
        // and A Rapt Audience).
        ModelDb.Card<ProtoFsDoubleCasting>(),
        ModelDb.Card<ProtoFsTutti>(),
        ModelDb.Card<ProtoFsBravura>(),
        ModelDb.Card<ProtoFsFullHouse>(),
        ModelDb.Card<ProtoFsThunderousApplause>(),
        // Rares (two).
        ModelDb.Card<ProtoFsArkheAlignment>(),
        ModelDb.Card<ProtoFsFiveCenturyAct>(),
        // THE GUEST CAST (2026-09-25). Rares (three).
        ModelDb.Card<ProtoFsGuestStarNeuvillette>(),
        ModelDb.Card<ProtoFsGuestStarClorinde>(),
        ModelDb.Card<ProtoFsGuestStarNavia>(),
        // Uncommons (five).
        ModelDb.Card<ProtoFsGuestStarChevreuse>(),
        ModelDb.Card<ProtoFsGuestStarWriothesley>(),
        ModelDb.Card<ProtoFsGuestStarSigewinne>(),
        ModelDb.Card<ProtoFsGuestStarCharlotte>(),
        ModelDb.Card<ProtoFsGuestStarLynette>(),
        // THE SUPPORTING POOL (2026-09-26,
        // review/active/furina-supporting-pool-2026-09-26.md): 28 of
        // its 29, in the paper's family order. Commons (six).
        ModelDb.Card<ProtoFsPlotTwist>(),
        ModelDb.Card<ProtoFsStageWhisper>(),
        ModelDb.Card<ProtoFsCheeredOn>(),
        ModelDb.Card<ProtoFsSpiritedAria>(),
        ModelDb.Card<ProtoFsBubbleAria>(),
        ModelDb.Card<ProtoFsSoloVerse>(),
        // Uncommons (eleven; the 2026-09-29 fade pass cut Held
        // Applause and Echoing Hall).
        ModelDb.Card<ProtoFsRevolvingStage>(),
        ModelDb.Card<ProtoFsOratricesVerdict>(),
        ModelDb.Card<ProtoFsSeasonTickets>(),
        ModelDb.Card<ProtoFsStarBilling>(),
        ModelDb.Card<ProtoFsIntermission>(),
        ModelDb.Card<ProtoFsCounterclaim>(),
        ModelDb.Card<ProtoFsDaCapo>(),
        ModelDb.Card<ProtoFsGroundswell>(),
        ModelDb.Card<ProtoFsTideOfApplause>(),
        ModelDb.Card<ProtoFsSoliloquy>(),
        ModelDb.Card<ProtoFsDualNature>(),
        // Rares (eight; the fade pass cut Eternal Applause).
        ModelDb.Card<ProtoFsGuestStarLyney>(),
        ModelDb.Card<ProtoFsGuestStarEscoffier>(),
        ModelDb.Card<ProtoFsBringTheHouseDown>(),
        ModelDb.Card<ProtoFsGrandFinale>(),
        ModelDb.Card<ProtoFsGalaPremiere>(),
        ModelDb.Card<ProtoFsGrandDeluge>(),
        ModelDb.Card<ProtoFsReginaOfAllWaters>(),
        ModelDb.Card<ProtoFsOneWomanShow>(),
        // THE SUPPORTING POOL (2026-09-26). Rare (one): the fourth
        // seat.
        ModelDb.Card<ProtoFsSoldOut>(),
        // THE STARTER RULING (2026-09-28): out of the starter, offered
        // as Commons (two). Sim twin:
        // `furina_stage.PROMOTED_STARTERS`. Take the Stage is
        // tentative, audited in the balance pass's dedupe.
        ModelDb.Card<ProtoFsSalonDebut>(),
        ModelDb.Card<ProtoFsRegalBearing>(),
        // POOL COMPLETION (2026-10-01, review/active/pool-completion-
        // 2026-10-01.md sec.5): three Uncommons and three Rares,
        // appended (sim twin: `furina_stage.POOL_ADDS`). The pool is
        // 78 (23 / 35 / 20).
        ModelDb.Card<ProtoFsAriaForOne>(),
        ModelDb.Card<ProtoFsIntervalBell>(),
        ModelDb.Card<ProtoFsCastingAgent>(),
        ModelDb.Card<ProtoFsTheLastAct>(),
        ModelDb.Card<ProtoFsCriticsDarling>(),
        ModelDb.Card<ProtoFsStarTurn>(),
        // THE RULES PASS (2026-10-01, sec.3): the twelve old-kit rows,
        // ported. Commons (four).
        ModelDb.Card<ProtoFsOpeningNumber>(),
        ModelDb.Card<ProtoFsCommandingGaze>(),
        ModelDb.Card<ProtoFsUndercurrent>(),
        ModelDb.Card<ProtoFsWarmupAct>(),
        // Uncommons (six).
        ModelDb.Card<ProtoFsLeadingLady>(),
        ModelDb.Card<ProtoFsCourtroomDrama>(),
        ModelDb.Card<ProtoFsCrashingWaves>(),
        ModelDb.Card<ProtoFsDuet>(),
        ModelDb.Card<ProtoFsQuickChange>(),
        ModelDb.Card<ProtoFsWitnessStand>(),
        // Rares (two). The pool stays 78 (23 / 35 / 20), all of it
        // `proto_fs_` rows.
        ModelDb.Card<ProtoFsSingerOfManyWaters>(),
        ModelDb.Card<ProtoFsEndlessWaltz>(),
    };

    /// <summary>
    /// THE GUEST CAST'S TEN CARDS, one per guest (pool completion,
    /// 2026-10-01): what <i>Casting Agent</i> offers three of
    /// (<see cref="FurinaStage.CastingAgent"/>). Sim twin:
    /// <c>furina_stage.GUEST_STAR_CARD_IDS</c>, same order.
    /// </summary>
    public static IReadOnlyList<CardModel> GuestStarCards() => new CardModel[]
    {
        ModelDb.Card<ProtoFsGuestStarNeuvillette>(),
        ModelDb.Card<ProtoFsGuestStarClorinde>(),
        ModelDb.Card<ProtoFsGuestStarNavia>(),
        ModelDb.Card<ProtoFsGuestStarChevreuse>(),
        ModelDb.Card<ProtoFsGuestStarWriothesley>(),
        ModelDb.Card<ProtoFsGuestStarSigewinne>(),
        ModelDb.Card<ProtoFsGuestStarCharlotte>(),
        ModelDb.Card<ProtoFsGuestStarLynette>(),
        ModelDb.Card<ProtoFsGuestStarLyney>(),
        ModelDb.Card<ProtoFsGuestStarEscoffier>(),
    };

    /// <summary>
    /// THE MULTIPLAYER TIER (the co-op set, review/records/coop-set-2026-09-25.md):
    /// five cards offered only in co-op, outside the pool's count, on
    /// <c>KleeOverhaulRoster.MultiplayerSlice</c>'s terms -- each declares
    /// <c>CardMultiplayerConstraint.MultiplayerOnly</c>, and
    /// <c>CardPoolModel.GetUnlockedCards</c> drops it from a one-player run.
    /// A method of its own so <see cref="Pool"/>'s count does not move.
    /// Sim mirror: <c>C.FURINA_STAGE_MULTIPLAYER_IDS</c>.
    /// </summary>
    public static IEnumerable<CardModel> MultiplayerRows() => new CardModel[]
    {
        ModelDb.Card<ProtoFsGuestOfHonor>(),
        ModelDb.Card<ProtoFsShareTheSpotlight>(),
        ModelDb.Card<ProtoFsPeopleOfFontaine>(),
        // The second batch (review/active/coop-concepts-2026-09-27.md).
        ModelDb.Card<ProtoFsRaiseAToast>(),
        ModelDb.Card<ProtoFsTheCrowdRoars>(),
    };
}
