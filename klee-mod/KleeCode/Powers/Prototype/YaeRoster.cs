using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// YAE'S DECK, RELIC AND POOL (<c>review/active/yae-card-paper-2026-10-13.md</c>
/// sec.3 and sec.5). LISTED BY TYPE, not filtered by id prefix, for
/// <c>VarkaRoster</c>'s reason: a deleted row takes its type with it and this
/// file stops building.
/// </summary>
internal static class YaeRoster
{
    /// <summary>
    /// The starter (sec.3): "Strike x4, Defend x4 (base game), and: Yakan
    /// Evocation, Proofread". The base pair is the Defect's, because her pool
    /// borrows his blue frame (the arrangement every kit makes with the
    /// character whose frame it wears).
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<StrikeDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<DefendDefect>(),
        ModelDb.Card<ProtoYmYakanEvocation>(),
        ModelDb.Card<ProtoYmProofread>(),
    };

    /// <summary>The Strike a base-game effect is handed when it asks the
    /// character for one (Large Capsule, <see cref="ArmStarterBasics"/>).
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeDefect>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendDefect>();

    /// <summary>Her starting relic, Meditations of a Yako (sec.3).</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.MeditationsOfAYako>(),
        };

    /// <summary>
    /// The pool: batch one's thirty (sec.5) realigned, batch two's ten
    /// (<c>review/active/yae-design-axes-2026-10-14.md</c> sec.5 and its
    /// Ruled section) and review r3's three signature cards
    /// (<c>review/active/yae-review-r3-2026-10-14.md</c> sec.3), and the
    /// pool to 78's thirty-five (<c>review/active/yae-pool-to-78-2026-10-15.md</c>
    /// sec.2, ruled 2026-10-15; Sakura Grove and Fox's Mooncall swapped
    /// rarities, sec.3): SEVENTY-EIGHT, twenty Commons, thirty-eight
    /// Uncommons and twenty Rares, in the sheet's order. No Ancients and no
    /// co-op tier yet.
    /// </summary>
    internal static IReadOnlyList<CardModel> Pool() => new CardModel[]
    {
        // Common (20)
        ModelDb.Card<ProtoYmKitsuneFlash>(),
        ModelDb.Card<ProtoYmThunderRite>(),
        ModelDb.Card<ProtoYmShrineOffering>(),
        ModelDb.Card<ProtoYmTwinSakura>(),
        ModelDb.Card<ProtoYmDeadline>(),
        ModelDb.Card<ProtoYmFoxFireDraft>(),
        ModelDb.Card<ProtoYmSlyStrike>(),
        ModelDb.Card<ProtoYmFoxTrick>(),
        ModelDb.Card<ProtoYmShrineMaidensGuard>(),
        ModelDb.Card<ProtoYmShrineBell>(),
        ModelDb.Card<ProtoYmGraftedBranch>(),
        ModelDb.Card<ProtoYmMarginNote>(),
        ModelDb.Card<ProtoYmKitsunePounce>(),
        ModelDb.Card<ProtoYmFoxfireSweep>(),
        ModelDb.Card<ProtoYmEvergreenCharm>(),
        ModelDb.Card<ProtoYmThunderPetal>(),
        ModelDb.Card<ProtoYmKitsuneFlick>(),
        ModelDb.Card<ProtoYmSacredSpark>(),
        ModelDb.Card<ProtoYmCliffhanger>(),
        ModelDb.Card<ProtoYmShrineLantern>(),
        // Uncommon (38)
        ModelDb.Card<ProtoYmKitsuneRite>(),
        ModelDb.Card<ProtoYmThunderboltTithe>(),
        ModelDb.Card<ProtoYmRootedShrine>(),
        ModelDb.Card<ProtoYmEdictOfCleansing>(),
        ModelDb.Card<ProtoYmBestseller>(),
        ModelDb.Card<ProtoYmPrintRun>(),
        ModelDb.Card<ProtoYmFootnote>(),
        ModelDb.Card<ProtoYmSakuraSeal>(),
        ModelDb.Card<ProtoYmSerialization>(),
        ModelDb.Card<ProtoYmManuscriptPile>(),
        ModelDb.Card<ProtoYmKitsuneGuile>(),
        ModelDb.Card<ProtoYmFoxfireLure>(),
        ModelDb.Card<ProtoYmFallenPetals>(),
        ModelDb.Card<ProtoYmMikageThunder>(),
        ModelDb.Card<ProtoYmInkedBranches>(),
        ModelDb.Card<ProtoYmSecondPrinting>(),
        ModelDb.Card<ProtoYmAuthorsCopy>(),
        ModelDb.Card<ProtoYmFoxsMooncall>(),
        ModelDb.Card<ProtoYmNarukamiRay>(),
        ModelDb.Card<ProtoYmGalleyProof>(),
        ModelDb.Card<ProtoYmPetalStorm>(),
        ModelDb.Card<ProtoYmFoxsBargain>(),
        ModelDb.Card<ProtoYmSpiritfoxPrank>(),
        ModelDb.Card<ProtoYmGenreShift>(),
        ModelDb.Card<ProtoYmNarukamiJudgment>(),
        ModelDb.Card<ProtoYmKitsunesShelter>(),
        ModelDb.Card<ProtoYmOmikuji>(),
        ModelDb.Card<ProtoYmToriiWard>(),
        ModelDb.Card<ProtoYmKitsuneVeil>(),
        ModelDb.Card<ProtoYmHoldThePresses>(),
        ModelDb.Card<ProtoYmSakuraCanopy>(),
        ModelDb.Card<ProtoYmDisarmingSmile>(),
        ModelDb.Card<ProtoYmReplanting>(),
        ModelDb.Card<ProtoYmLateNightReading>(),
        ModelDb.Card<ProtoYmEnlightenedBlessing>(),
        ModelDb.Card<ProtoYmSaiguusLesson>(),
        ModelDb.Card<ProtoYmShrinesSacredShade>(),
        ModelDb.Card<ProtoYmEditorialPriority>(),
        // Rare (20)
        ModelDb.Card<ProtoYmTenkoKenshin>(),
        ModelDb.Card<ProtoYmYakanOffering>(),
        ModelDb.Card<ProtoYmTheSevenGlamours>(),
        ModelDb.Card<ProtoYmSakuraChanneling>(),
        ModelDb.Card<ProtoYmMischievousTeasing>(),
        ModelDb.Card<ProtoYmRebornAsGuujiYae>(),
        ModelDb.Card<ProtoYmEditorInChief>(),
        ModelDb.Card<ProtoYmRoyalties>(),
        ModelDb.Card<ProtoYmSerialNovel>(),
        ModelDb.Card<ProtoYmSakuraGrove>(),
        ModelDb.Card<ProtoYmForbiddenArtDaisesshou>(),
        ModelDb.Card<ProtoYmKagurasVerity>(),
        ModelDb.Card<ProtoYmNarukamiBloom>(),
        ModelDb.Card<ProtoYmSacredThunderbolt>(),
        ModelDb.Card<ProtoYmOffertoryBox>(),
        ModelDb.Card<ProtoYmAfterword>(),
        ModelDb.Card<ProtoYmFoxsVerdict>(),
        ModelDb.Card<ProtoYmGuardianOfNarukami>(),
        ModelDb.Card<ProtoYmStellarConduct>(),
        ModelDb.Card<ProtoYmEternity>(),
    };

    /// <summary>THE OFFER (<c>YaeCardPool.FilterThroughEpochs</c>): the pool.
    /// No Ancients and no co-op tier yet (the paper's "next batch").</summary>
    internal static IEnumerable<CardModel> OfferablePool() => Pool();

    /// <summary>Every card of hers that must resolve <c>CardModel.Pool</c> to
    /// her pool: her generated rows. The five Annotation faces ride
    /// <see cref="YaeModalOptions.All"/> beside this.</summary>
    internal static IReadOnlyList<CardModel> Members() =>
        PrototypeCards.For(YaePrototype.CharacterId).ToList();
}
