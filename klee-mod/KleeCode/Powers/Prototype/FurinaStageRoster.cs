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
    /// THE BASICS DO NOT MOVE, and that is a standing rule rather than a
    /// choice made here: a starter change is an A pick, never an E default,
    /// and the six/seven passes that moved a character's basics were reverted
    /// on 2026-09-08 for exactly that. Soloist's Solicitation x3, Stage
    /// Presence x3 and Regal Bearing are the shipped seven, in the shipped
    /// order.
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
    /// THE POOL SEAM. Fourteen shipped rows leave the offer and the arm's
    /// fourteen take their slots -- batch one minus the three starters above.
    ///
    /// ONE FOR ONE AT THE SAME RARITY, which is what keeps the offer odds
    /// untouched: eight Commons, five Uncommons and one Rare out, the same
    /// counts in. The pairing is the sheet's own `replaces:` and the sim's
    /// <c>furina_stage.POOL_SUBS</c>, and it is a D default disclosed rather
    /// than a design act -- same rarity always, same type and cost where her
    /// sheet had one to spare, and the three named summons landing on the
    /// three shipped rows of the same NAME, which is the cleanest swap on the
    /// sheet.
    ///
    /// THE DOOR IS <c>FurinaCardPool.FilterThroughEpochs</c>, the same one the
    /// reframe's swap used and for its reason: it feeds
    /// <c>GetUnlockedCards</c>, which is the SOLE path into reward rolls, the
    /// shop and card transforms, so a substitution made there reaches every
    /// surface that can offer her a card and no list of surfaces has to be
    /// kept in step.
    ///
    /// A PARTIAL SWAP, AND IT SAYS SO. Fourteen rows move; the rest of her
    /// pool still prints Encore, the shipped Fanfare meter and the shipped
    /// Salon, so a run under the arm drafts a MIXED sheet by construction.
    /// Batch one is "enough to play Preserve and Expend against each other"
    /// (sec.12) and not a whole pool. That is a known limitation of round one
    /// rather than an oversight, and it belongs in the round packet's own
    /// "what this round cannot see".
    /// </summary>
    public static IEnumerable<CardModel> SwapOfferedRows(
        IEnumerable<CardModel> offered)
    {
        if (!FurinaStage.Enabled) return offered;
        return offered
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
                        && card is not FurinaGen.UniversalRevelry)
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
            });
    }
}
