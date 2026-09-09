using System.Collections.Generic;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Prototype;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// THE ARM'S TWO WIRING SEAMS, and there are only two: what she starts the run
/// with, and what she starts the run holding.
///
/// ONE SEAM EACH, on the terms every arm before this one took: the swap is
/// made at the one place the game asks the CHARACTER, so no list of surfaces
/// has to be kept in step, and with <see cref="FurinaStage.Enabled"/> off both
/// methods return the shipped answer byte for byte -- which is the acceptance
/// condition the quarantine rests on and is pinned rather than intended.
///
/// NO POOL SEAM YET, and its absence is disclosed rather than forgotten. The
/// arm's OFFERABLE rows are the batch-one faces being authored as `proto_fs_`
/// sheet rows on `stage-sim`; until they land the arm's pool is the shipped
/// Furina pool, which is wrong for a kit whose every rule has moved. The
/// substitution goes in <c>FurinaCardPool.FilterThroughEpochs</c> beside the
/// reframe's, at the same door and for its reason.
/// </summary>
public static class FurinaStageRoster
{
    /// <summary>
    /// THE STARTER (brief sec.7's named deck): the base game's basics
    /// untouched, plus THREE kit cards where the shipped Furina carries two.
    ///
    /// THE BASICS DO NOT MOVE, and that is a standing rule rather than a
    /// choice made here: a starter change is an A pick, never an E default,
    /// and the six/seven passes that moved a character's basics were reverted
    /// on 2026-09-08 for exactly that. Soloist's Solicitation x3, Stage
    /// Presence x3 and Regal Bearing are the shipped seven, in the shipped
    /// order, and this method copies them rather than editing them.
    ///
    /// THREE KIT SLOTS AND NOT TWO, which IS a change to the shape of her
    /// starter and is the brief's own (sec.7 lists the deck card by card:
    /// "plus Salon Début, Curtain Rise, Standing Ovation"). The three are one
    /// summon, one Spend and one Raise -- the three verbs sec.7's fight-one
    /// script needs to have a turn one worth arguing about -- and dropping any
    /// one of them makes that script unplayable rather than merely weaker.
    /// <i>An Invitation</i> leaves the starter with the Salon it deployed
    /// into.
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
        ModelDb.Card<StageSalonDebut>(),
        ModelDb.Card<StageCurtainRise>(),
        ModelDb.Card<StageStandingOvation>(),
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
}
