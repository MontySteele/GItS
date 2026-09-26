using System.Collections.Generic;
using System.Linq;
using FurinaGen = KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
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
/// pair for pair: <c>furina_stage.STARTER_SUBS</c> and
/// <c>furina_stage.POOL_SUBS</c>, read C#-side at the seams the reframe's were.
/// The sheet is the authority for which shipped row each prototype row
/// replaces (`replaces:` on the row itself); these tables are that authority
/// in the language the mod's pools speak, which is classes.
/// </summary>
public static class FurinaStageRoster
{
    /// <summary>
    /// THE STARTER (brief sec.7's named deck, sec.12's first table): the base
    /// game's seven basics untouched, and her three kit slots replaced.
    ///
    /// THE BASICS ARE THE SHIPPED SEVEN, and that is a standing rule rather
    /// than a choice made here: a starter change is an A pick, never an E
    /// default, and the six/seven passes that moved a character's basics were
    /// reverted on 2026-09-08 for exactly that. Soloist's Solicitation x3,
    /// Stage Presence x3 and Regal Bearing, in the shipped order. They ARRIVE
    /// as printed only since R276's hygiene: the shipped starting-companion
    /// roll (<c>KleeStartingCompanionsPatch.ResolveFurina</c>) used to swap a
    /// Solicitation and a Presence for two Fontaine companions in every Stage
    /// run, and it now stands down under the arm.
    ///
    /// THREE KIT SLOTS FOR THREE, which is why this replaces the deck rather
    /// than a slot in it: the shipped Furina's three kit cards are <i>Aria of
    /// Recompense</i>, <i>Salon Début</i> and <i>An Invitation</i>, and the
    /// arm's are the sheet's three basics -- one summon, one Spend and one
    /// Raise, the three verbs sec.7's fight-one script needs to have a turn
    /// one worth arguing about. The pairing is
    /// <c>furina_stage.STARTER_SUBS</c> row for row.
    /// </summary>
    public static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<SoloistsSolicitation>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<StagePresence>(),
        ModelDb.Card<RegalBearing>(),
        // aria_of_recompense -> proto_fs_curtain_rise
        ModelDb.Card<ProtoFsCurtainRise>(),
        // salon_debut -> proto_fs_salon_debut
        ModelDb.Card<ProtoFsSalonDebut>(),
        // an_invitation -> proto_fs_standing_ovation
        ModelDb.Card<ProtoFsStandingOvation>(),
    };

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
    /// THE POOL SEAM. Named shipped rows leave the offer and the arm's rows
    /// are appended: batch one's fourteen (its seventeen minus the three
    /// starters above -- eight Commons, five Uncommons, one Rare) and R276's
    /// batch two, fifteen more (six Commons, seven Uncommons, two Rares). The
    /// pairing is the sheet's own `replaces:` and the sim's
    /// <c>furina_stage.POOL_SUBS</c>.
    ///
    /// NOT A ONE-FOR-ONE SWAP ANY MORE, and the offer odds DO move.
    /// <see cref="DropRetiredRows"/> (`EB-736`) runs first and drops every
    /// shipped row printing a retired word -- 65 of them, which include
    /// every batch-two replacement -- so the arm's pool is the 29 Stage rows
    /// plus the dozen shipped rows that survive the filter, about 41 cards,
    /// not the ~76 a one-for-one swap would leave. The sim does not model the
    /// filter, so its pool is the swap's.
    ///
    /// THE DOOR IS <c>FurinaCardPool.FilterThroughEpochs</c>, the same one the
    /// reframe's swap used and for its reason: it feeds
    /// <c>GetUnlockedCards</c>, which is the SOLE path into reward rolls, the
    /// shop and card transforms, so a substitution made there reaches every
    /// surface that can offer her a card and no list of surfaces has to be
    /// kept in step.
    ///
    /// WHAT SURVIVES THE FILTER is a dozen plain shipped rows (Commanding
    /// Gaze, Undercurrent, the Companion feeders and so on); they stay in the
    /// offer until the Stage's own pool passes replace them.
    /// </summary>
    public static IEnumerable<CardModel> SwapOfferedRows(
        IEnumerable<CardModel> offered)
    {
        if (!FurinaStage.Enabled) return offered;
        return DropRetiredRows(offered)
            .Where(card => card is not FurinaGen.GentilhommeUsher
                        && card is not FurinaGen.SurintendanteChevalmarin
                        && card is not FurinaGen.MademoiselleCrabaletta
                        && card is not FurinaGen.SufferingForArt
                        && card is not FurinaGen.BlockingNotes
                        && card is not FurinaGen.UsherTheWaves
                        && card is not FurinaGen.StageLights
                        && card is not FurinaGen.HeldBreath
                        && card is not FurinaGen.TorrentialTurn
                        && card is not FurinaGen.Crescendo
                        && card is not FurinaGen.ManyWatersMelody
                        && card is not FurinaGen.ChangeTheBill
                        && card is not FurinaGen.TakeYourBow
                        && card is not FurinaGen.UniversalRevelry
                        // R276 batch two's fifteen `replaces:` -- every one
                        // already dropped by the text filter above, named here
                        // so the sheet's pairing and this list stay one table.
                        && card is not FurinaGen.Breathless
                        && card is not FurinaGen.GracefulRetreat
                        && card is not FurinaGen.HouseCall
                        && card is not FurinaGen.LastingImpression
                        && card is not FurinaGen.ApplauseLine
                        && card is not FurinaGen.SwellingOverture
                        && card is not FurinaGen.DressRehearsal
                        && card is not FurinaGen.MatineePerformance
                        && card is not FurinaGen.FullEnsemble
                        && card is not FurinaGen.DramaticEntrance
                        && card is not FurinaGen.FortissimoGuard
                        && card is not FurinaGen.StandingOvation
                        && card is not FurinaGen.CrowdWork
                        && card is not FurinaGen.EndlessWaltz
                        && card is not FurinaGen.PrimaDonna
                        // THE GUEST CAST (2026-09-25): the eight `replaces:`,
                        // each already dropped by the text filter too.
                        && card is not FurinaGen.ReginasMercy
                        && card is not FurinaGen.ThunderousOvation
                        && card is not FurinaGen.EncorePerformance
                        && card is not FurinaGen.AudienceParticipation
                        && card is not FurinaGen.DeepBreath
                        && card is not FurinaGen.StandingRoomOnly
                        && card is not FurinaGen.Limelight
                        && card is not FurinaGen.TakeItFromTheTop
                        // THE SUPPORTING POOL'S SOLD OUT (2026-09-26): its
                        // `replaces:`, dropped by the text filter too.
                        && card is not FurinaGen.UnheardConfession)
            .Concat(new CardModel[]
            {
                // Commons (eight).
                ModelDb.Card<ProtoFsGentilhommeUsher>(),
                ModelDb.Card<ProtoFsSurintendanteChevalmarin>(),
                ModelDb.Card<ProtoFsMademoiselleCrabaletta>(),
                ModelDb.Card<ProtoFsUnderstudy>(),
                ModelDb.Card<ProtoFsWarmReception>(),
                ModelDb.Card<ProtoFsTidalFlourish>(),
                ModelDb.Card<ProtoFsInterposition>(),
                ModelDb.Card<ProtoFsSceneChange>(),
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
                // Uncommons (seven).
                ModelDb.Card<ProtoFsGalaDinner>(),
                ModelDb.Card<ProtoFsDoubleCasting>(),
                ModelDb.Card<ProtoFsTutti>(),
                ModelDb.Card<ProtoFsBravura>(),
                ModelDb.Card<ProtoFsFullHouse>(),
                ModelDb.Card<ProtoFsThunderousApplause>(),
                ModelDb.Card<ProtoFsRaptAudience>(),
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
                // THE SUPPORTING POOL (2026-09-26). Rare (one): the fourth
                // seat.
                ModelDb.Card<ProtoFsSoldOut>(),
            })
            .Concat(MultiplayerRows());
    }

    /// <summary>
    /// THE MULTIPLAYER TIER (the co-op set, review/records/coop-set-2026-09-25.md):
    /// three cards offered only in co-op, outside the pool's count, on
    /// <c>KleeOverhaulRoster.MultiplayerSlice</c>'s terms -- each declares
    /// <c>CardMultiplayerConstraint.MultiplayerOnly</c>, and
    /// <c>CardPoolModel.GetUnlockedCards</c> drops it from a one-player run.
    /// A method of its own so the arm's substitution table above, and every
    /// pin that reads it, is untouched. They replace no shipped row. Sim
    /// mirror: <c>C.FURINA_STAGE_MULTIPLAYER_IDS</c>.
    /// </summary>
    public static IEnumerable<CardModel> MultiplayerRows() => new CardModel[]
    {
        ModelDb.Card<ProtoFsGuestOfHonor>(),
        ModelDb.Card<ProtoFsShareTheSpotlight>(),
        ModelDb.Card<ProtoFsPeopleOfFontaine>(),
    };

    /// <summary>
    /// `EB-736`. THE WORDS A SHIPPED ROW PRINTS WHEN IT READS A SYSTEM THE
    /// STAGE RETIRED.
    ///
    /// The brief's sec.2 retires Encore, the Spotlight in both modes, the
    /// Fanfare COUNTER, the shipped Salon members and the Burst bar. Batch one
    /// swaps fourteen rows and no more, so a round-one draft was mixed by
    /// construction: three seats were offered Encore cards they could never
    /// pay, a Fortissimo Guard that never fired on a summon, and a Casting
    /// Call whose gloss describes the old three-member Salon, beside a
    /// glossary calling Fanfare the bar. One word, two resources, the shown one
    /// dead.
    ///
    /// BY TEXT AND NOT BY A HAND LIST, which is the row's own instruction and
    /// the only shape that stays true: a hand list is a second copy of the
    /// sheet that goes stale the next time a row is authored, and what makes a
    /// row unplayable here is exactly that it PRINTS one of these words. So
    /// the question asked of every shipped row is the question a seat asks of
    /// its face.
    ///
    /// SIX WORDS AND NOT FIVE. The row names Encore, Spotlight/Spotlighted,
    /// Center Stage, Salon Member and the Fanfare meter. `Spotlight` is a
    /// prefix of `Spotlighted` so one entry covers both; `Salon` is entered
    /// bare rather than as `Salon Member`, because <i>House Call</i>,
    /// <i>Dinner Service</i> and <i>Full Ensemble</i> read the shipped Salon
    /// without printing the word "member" and are just as dead; and `Burst` is
    /// the sixth, because sec.2 retires that bar too and the header hides its
    /// line.
    ///
    /// THE SHIPPED SHEET IS UNTOUCHED. This is an OFFER filter under a flag,
    /// not a sheet edit: `EB-726` retires those rows properly, and with
    /// <see cref="FurinaStage.Enabled"/> off nothing here runs.
    /// </summary>
    public static readonly string[] RetiredSystemWords =
    {
        "Encore", "Spotlight", "Center Stage", "Salon", "Fanfare", "Burst",
    };

    /// <summary>How many shipped rows the last filter pass dropped. An
    /// INSTRUMENT and nothing reads it back to decide anything -- the same
    /// fence the arm's turn census carries -- but the count is what the row
    /// asks be printed, and a number nobody can read is not printed.</summary>
    public static int LastRetiredCount { get; private set; }

    /// <summary>
    /// Does this row print a word the Stage retired?
    ///
    /// ARM ROWS ARE NEVER ASKED. Every `proto_fs_` face prints `Fanfare` --
    /// it is the bar's name (rule 1) -- so the question is only ever put to a
    /// SHIPPED row, and the namespace is what tells them apart: the generated
    /// prototype rows are the only cards in
    /// <c>KleeMod.Cards.Prototype.Generated</c>, and a release build compiles
    /// none of them.
    /// </summary>
    public static bool ReadsARetiredSystem(CardModel? card)
    {
        if (card == null) return false;
        if (card.GetType().Namespace == "KleeMod.Cards.Prototype.Generated")
        {
            return false;
        }
        var text = PrintedText(card);
        if (text.Length == 0) return false;
        return RetiredSystemWords.Any(
            word => text.Contains(word,
                                  System.StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// What a row PRINTS, off the model's own loc rows.
    ///
    /// <c>ILocalizationProvider.Localization</c> and not the localized string,
    /// deliberately: the loc table is what this list FEEDS
    /// (<c>KleeMod.InjectLocStrings</c>), so it is the same words a beat
    /// earlier and it can be read with no <c>LocManager</c>, no combat and no
    /// scene tree -- which is what lets a headless pin ask the same question
    /// the pool asks. A row that provides none answers the empty string and is
    /// kept, because a filter must never drop a card it could not read.
    /// </summary>
    public static string PrintedText(CardModel card) =>
        card is BaseLib.Abstracts.ILocalizationProvider provider
        && provider.Localization is { } rows
            ? string.Join(" ", rows.Select(row => row.Item2))
            : string.Empty;

    /// <summary>The offer, less every shipped row that reads a retired system,
    /// with the count printed once per pass. PUBLIC so a headless pin can ask
    /// the question: <see cref="SwapOfferedRows"/> reaches <c>ModelDb</c> for
    /// the fourteen it concatenates on, which the test harness has no
    /// registration for (KleeTests/README.md), and this half needs none.
    ///
    /// EXCEPT AN ANCIENT ROW, WHICH IS NEVER DROPPED (`EB-363`). Furina's one
    /// Ancient, <i>All the World's a Stage</i>, prints a retired word and the
    /// filter was taking it -- so under this arm her pool held no Ancient card
    /// at all, and that is `EB-284`'s defect exactly: `DustyTome.SetupForPlayer`
    /// draws a random <c>CardRarity.Ancient</c> card from <c>GetUnlockedCards</c>
    /// and nothing else in the game does, so an empty Ancient cell makes
    /// <c>NextItem(...).Id</c> throw inside <c>Darv.GenerateInitialOptions</c>
    /// and the run ends at the act-two door. The whole argument is in
    /// <c>RosterAncientCards</c>, and the trade it names is the one taken here:
    /// an Ancient is reachable through Dusty Tome and through NOTHING else --
    /// reward rolls, transforms and shop inventory all filter the rarity
    /// upstream -- so keeping it costs the arm no offer it was trying to
    /// protect, and the alternative costs the run. A row printing a retired
    /// word in a place the player reaches once is the smaller defect.
    /// </summary>
    public static IEnumerable<CardModel> DropRetiredRows(
        IEnumerable<CardModel> offered)
    {
        var kept = new List<CardModel>();
        var dropped = 0;
        foreach (var card in offered)
        {
            if (card.Rarity != CardRarity.Ancient && ReadsARetiredSystem(card))
            {
                dropped++;
            }
            else
            {
                kept.Add(card);
            }
        }
        LastRetiredCount = dropped;
        MegaCrit.Sts2.Core.Logging.Log.Info(
            $"[{KleeMod.ModId}] stage: the arm's offer filter dropped "
            + $"{dropped} shipped row(s) reading a retired system; "
            + $"{kept.Count} row(s) left before the fourteen swaps.");
        return kept;
    }
}
