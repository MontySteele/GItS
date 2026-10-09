using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// THE KIT'S THREE WIRING SEAMS: what she starts the run holding, what she
/// starts it carrying, and what the game may offer her. Every row is the
/// sheet's, and both tables mirror the sim's
/// (<c>furina_stage.STARTER_IDS</c>, <c>furina_stage.POOL_IDS</c>).
/// </summary>
public static class FurinaStageRoster
{
    /// <summary>
    /// THE STARTER: the base game's Strike x4 and Defend x4 ([USER],
    /// 2026-09-28: "The characters' kits should all use basic Strike and
    /// Defend.") and the two kit cards that teach the Salon's Tab -- Curtain
    /// Rise (the Drain) and Rising Applause (the Spend). Silent's pair, for
    /// <c>KokomiOverhaulRoster</c>'s reason: <c>FurinaCardPool</c> borrows
    /// <c>card_frame_green</c> and the <c>silent</c> energy colour. Sim twin:
    /// <c>furina_stage.STARTER_IDS</c>.
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
        ModelDb.Card<ProtoFsCurtainRise>(),
        ModelDb.Card<ProtoFsStandingOvation>(),
    };

    /// <summary>The pair above, named once more for the relic seam
    /// (`EB-351`): Large Capsule and Fasten ask for "your Strike".</summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeSilent>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendSilent>();

    /// <summary>THE STARTING RELIC: Salon Solitaire, "At the end of your
    /// turn, Repay 2."</summary>
    public static IReadOnlyList<RelicModel> StartingRelics() => new RelicModel[]
    {
        ModelDb.Relic<Relics.SalonSolitaire>(),
    };

    /// <summary>
    /// HER WHOLE OFFER: <see cref="Pool"/>'s 75 and her two Ancients. What
    /// <c>FurinaCardPool.FilterThroughEpochs</c> returns, which IS
    /// <c>GetUnlockedCards</c> -- the sole door into reward rolls, the shop
    /// and transforms. No co-op tier: the v2 Stage's five went with it.
    /// </summary>
    public static IReadOnlyList<CardModel> OfferablePool() =>
        Pool().Concat(RosterAncientCards.Furina).ToList();

    /// <summary>
    /// THE SLICE'S 24 (proposal sec.16), THE POOL TO 39's ten
    /// (<c>review/active/furina-pool-40-2026-10-05.md</c> sec.3) and THE POOL
    /// TO 75's 41 (<c>review/active/furina-pool-growth-2026-10-09.md</c>
    /// sec.5), every one a `proto_fs_` row, less Endless Waltz (cut
    /// 2026-10-09, with Standing Ovation moved to Uncommon), and THE BLOCK
    /// GAP's four (ruled 2026-10-09): 20 Commons, 37 Uncommons and 21 Rares,
    /// 78 (pinned by `PoolCountTests`). Sim twin:
    /// <c>furina_stage.POOL_IDS</c>, same order.
    /// </summary>
    public static CardModel[] Pool() => new CardModel[]
    {
        // Drain (five).
        ModelDb.Card<ProtoFsMademoiselleCrabaletta>(),
        ModelDb.Card<ProtoFsSoloistsSolicitation>(),
        ModelDb.Card<ProtoFsSurintendanteChevalmarin>(),
        ModelDb.Card<ProtoFsLeadingLady>(),
        ModelDb.Card<ProtoFsSalonsTab>(),
        // Repay (four).
        ModelDb.Card<ProtoFsSurgingWaters>(),
        ModelDb.Card<ProtoFsHymnOfManyWaters>(),
        ModelDb.Card<ProtoFsPneumaRefrain>(),
        ModelDb.Card<ProtoFsSingerOfManyWaters>(),
        // Fanfare outlets (six).
        ModelDb.Card<ProtoFsTidalFlourish>(),
        ModelDb.Card<ProtoFsSpiritedAria>(),
        ModelDb.Card<ProtoFsQuickCue>(),
        ModelDb.Card<ProtoFsStandingOvationAll>(),
        ModelDb.Card<ProtoFsIntervalBell>(),
        ModelDb.Card<ProtoFsBravura>(),
        // The two Powers (Uncommon; Endless Waltz was cut 2026-10-09).
        ModelDb.Card<ProtoFsSalonsEncore>(),
        ModelDb.Card<ProtoFsThunderousApplause>(),
        // The four guests.
        ModelDb.Card<ProtoFsGuestStarCharlotte>(),
        ModelDb.Card<ProtoFsGuestStarWriothesley>(),
        ModelDb.Card<ProtoFsGuestStarLynette>(),
        ModelDb.Card<ProtoFsGuestStarClorinde>(),
        // The two Rares.
        ModelDb.Card<ProtoFsUniversalRevelry>(),
        ModelDb.Card<ProtoFsLetThePeopleRejoice>(),
        // The pool to 39 (2026-10-05). Ousia.
        ModelDb.Card<ProtoFsGrandDeluge>(),
        ModelDb.Card<ProtoFsOusiaSurge>(),
        ModelDb.Card<ProtoFsGuestStarLyney>(),
        ModelDb.Card<ProtoFsAFiveCenturyAct>(),
        // Pneuma.
        ModelDb.Card<ProtoFsGuestStarSigewinne>(),
        ModelDb.Card<ProtoFsFountainOfLucine>(),
        ModelDb.Card<ProtoFsCriticsDarling>(),
        // The Crowd.
        ModelDb.Card<ProtoFsHoldTheStage>(),
        ModelDb.Card<ProtoFsGuestStarChevreuse>(),
        ModelDb.Card<ProtoFsBis>(),
        // THE POOL TO 75 (review/active/furina-pool-growth-2026-10-09.md
        // sec.5, ruled 2026-10-09): 41 rows. Guests and stage (11).
        ModelDb.Card<ProtoFsCastingCall>(),
        ModelDb.Card<ProtoFsEncore>(),
        ModelDb.Card<ProtoFsTutti>(),
        ModelDb.Card<ProtoFsFinalBow>(),
        ModelDb.Card<ProtoFsGrandEntrance>(),
        ModelDb.Card<ProtoFsGuestStarFreminet>(),
        ModelDb.Card<ProtoFsShowstopper>(),
        ModelDb.Card<ProtoFsEnsembleCast>(),
        ModelDb.Card<ProtoFsGuestStarNavia>(),
        ModelDb.Card<ProtoFsGuestStarNeuvillette>(),
        ModelDb.Card<ProtoFsGuestStarEscoffier>(),
        // The Crowd (9).
        ModelDb.Card<ProtoFsCrashingWaves>(),
        ModelDb.Card<ProtoFsBubbleAria>(),
        ModelDb.Card<ProtoFsCommandingGaze>(),
        ModelDb.Card<ProtoFsStarTurn>(),
        ModelDb.Card<ProtoFsSoldOut>(),
        ModelDb.Card<ProtoFsCrescendo>(),
        ModelDb.Card<ProtoFsPrimaDonna>(),
        ModelDb.Card<ProtoFsStandingRoomOnly>(),
        ModelDb.Card<ProtoFsBringTheHouseDown>(),
        // Ousia, Drain (10).
        ModelDb.Card<ProtoFsUndercurrent>(),
        ModelDb.Card<ProtoFsOverdraft>(),
        ModelDb.Card<ProtoFsOusiaPledge>(),
        ModelDb.Card<ProtoFsAgainstTheTide>(),
        ModelDb.Card<ProtoFsPayTheTab>(),
        ModelDb.Card<ProtoFsRiptideLunge>(),
        ModelDb.Card<ProtoFsHighStakes>(),
        ModelDb.Card<ProtoFsReginaOfAllWaters>(),
        ModelDb.Card<ProtoFsTheDeluge>(),
        ModelDb.Card<ProtoFsAllIn>(),
        // Pneuma, Repay (10).
        ModelDb.Card<ProtoFsSoothingWaters>(),
        ModelDb.Card<ProtoFsGentleCurrent>(),
        ModelDb.Card<ProtoFsCleanSlate>(),
        ModelDb.Card<ProtoFsHydroLance>(),
        ModelDb.Card<ProtoFsCleansingTorrent>(),
        ModelDb.Card<ProtoFsBalanceTheBooks>(),
        ModelDb.Card<ProtoFsRisingTide>(),
        ModelDb.Card<ProtoFsPneumaTides>(),
        ModelDb.Card<ProtoFsHymnOfRenewal>(),
        ModelDb.Card<ProtoFsGrandAbsolution>(),
        // The bridge (1).
        ModelDb.Card<ProtoFsEbbAndFlow>(),
        // THE BLOCK GAP (review/records/furina-drain-line-round-2026-10-09.md
        // pick 2, ruled 2026-10-09): 1 Common, 2 Uncommon, 1 Rare.
        ModelDb.Card<ProtoFsVelvetCurtain>(),
        ModelDb.Card<ProtoFsPrivateBox>(),
        ModelDb.Card<ProtoFsTheMasquerade>(),
        ModelDb.Card<ProtoFsTheShowMustGoOn>(),
    };
}
