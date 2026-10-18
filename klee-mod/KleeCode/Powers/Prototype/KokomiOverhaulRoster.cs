using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
using MegaCrit.Sts2.Core.Models.Relics;

namespace KleeMod.Powers;

/// <summary>
/// THE FOUR WIRING SEAMS, and there are exactly four: what Kokomi OPENS
/// with, what she OPENS HOLDING, what she can be OFFERED, and WHICH PAIR OF
/// BASICS IS HERS when a base-game effect asks the CHARACTER for "your Strike
/// and your Defend" (<see cref="ArmStarterBasics"/>, the seam `EB-351` had to
/// add). Sim twins: <c>tier0.content.loader._starter_ids</c> and
/// <c>tier0.content.loader.pool_replacement</c>, which exist for the same
/// reason -- both readers of a starter and all five offer surfaces go through
/// one door each, so the two engines cannot disagree about what a run is. (The
/// relic seams have no sim twin, because tier 0.5 gives no character a starting
/// relic it did not draft and models nothing that grants a basic.)
///
/// WHY THE STARTER IS A REPLACEMENT AND NOT A SUBSTITUTION. The Kurage's-memory
/// arm swaps one of the twelve slots and leaves eleven standing, because its
/// rule is an addition. This arm's rule change is total: there is no shipped
/// starter card draft 6's rules leave meaning what it printed. All ten move, and
/// the deck shrinks from TWELVE to TEN on FOUR ids -- which is the slice's own
/// sec.3 count, and is a real consequence rather than an oversight: the twelve
/// card shape was ruled for a deck that mills itself, and nothing in this arm
/// exhausts for profit.
///
/// WHY THE RELIC MOVES TOO. The Pearl of Wisdom's printed body IS the exhaust
/// funnel ("Whenever a card is Exhausted, gain Charge and Burst Energy"), which
/// is the first thing the brief retires, so a run holding it would print a rule
/// the arm has turned off. Tamakushi Casket takes the slot (since 2026-10-12:
/// Block at the start of her turn while a Plan is waiting). THE COMPANION REWARD SLOT SURVIVES THE SWAP,
/// because it rides the relic in this mod purely for lifetime reasons and the
/// slice's Commander loop draws its whole army from it.
///
/// WHY THE POOL IS A REPLACEMENT TOO. Same argument, one screen over: a reward
/// screen that could still offer the shipped 76 would be offering cards written
/// against rules the run is no longer playing -- an Exhaust that pays Charge, a
/// Muster that transforms, a Burst that gates. Slice one's own scope statement
/// is that the 26 rows are her only reward pool for the prototype run; R246
/// pick 2 added the two defensive rows `EB-335` builds, making it 28, and
/// round 9 pick 1's tempo shelf added two more, making it 30, and the pool
/// passes since have made it 39, and the Casket pass (2026-09-28) 46, and the
/// cleanup pass (2026-09-29) 44, and the feed pass (2026-09-29) 48; it has been
/// 78 since pool completion (2026-10-01), re-founded on 2026-10-12.
/// </summary>
internal static class KokomiOverhaulRoster
{
    /// <summary>
    /// Kokomi's ten opening cards under the arm: Strike x4, Defend x4,
    /// Kurage's Oath, Slack Water (slice sec.3, in its order).
    ///
    /// THE BASICS ARE THE BASE GAME's (R242, ruled in the same breath as Klee's
    /// draft-4 starter): "where a character's basics are a renamed Strike or
    /// Defend with the same stat line, the base game's Strike and Defend
    /// replace them." Water's Edge and Coral Guard were exactly that -- 1
    /// energy for 6 damage and 1 energy for 5 Block, byte for byte the base
    /// line -- so <c>ProtoKkWatersEdge</c> and <c>ProtoKkCoralGuard</c> are
    /// DELETED from the surface rather than re-priced (R213 B).
    ///
    /// THE SILENT PAIR, not the Ironclad one. The base game ships one Strike
    /// and one Defend PER CHARACTER (five of each, all <c>public sealed</c>,
    /// all 6 damage / 5 Block with <c>OnUpgrade</c> +3), and the only
    /// difference between them is portrait, attack vfx and colour. A card's
    /// visual identity comes from <c>CardModel.Pool</c>, which resolves by
    /// scanning <c>ModelDb.AllCardPools</c> -- so a Silent basic renders with
    /// <c>card_frame_green</c> and the <c>silent</c> energy colour, which is
    /// exactly what <c>KokomiCardPool</c> already borrows. Her deck screen
    /// shows them in the Silent pool's <c>5EBD00</c> rather than her
    /// <c>6FC8D6</c>; that is the one seam and it is reported, not hidden.
    ///
    /// HER OWN ATTACKS APPLY HYDRO, THE BASE STRIKE DOES NOT. A base Strike
    /// cannot implement <c>IElementalCard</c> (it is sealed), so it applies
    /// nothing, which is the ruled reading for the basics. The element is the
    /// CARD's, written onto her rows by the codegen; since 2026-10-05 nothing
    /// falls back on the character (<see cref="CatalystCadence"/>).
    ///
    /// THE COMPANION ROLL FINDS NO SLOT, by construction and reported rather
    /// than hidden. <c>KokomiStartingCompanionsPatch</c> matches on the shipped
    /// <c>SayuDarumaGift</c> type to roll Sayu-or-Shinobu, and none of these ten
    /// is that type -- so under this arm she opens with NO companions at all.
    /// That is a real consequence: the slice's Commander loop draws its whole
    /// army from the reward slot instead, which is what its sec.4 says it does
    /// ("Companions are the Inazuma Universals (R236) already in the pool").
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<StrikeSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<DefendSilent>(),
        ModelDb.Card<ProtoKkKuragesOath>(),
        ModelDb.Card<ProtoKkSlackWater>(),
    };

    /// <summary>
    /// THE PAIR ABOVE, NAMED ONCE MORE FOR THE FOURTH SEAM (`EB-351`). Klee's
    /// twin, <c>KleeOverhaulRoster.StarterStrike</c>, carries the argument for
    /// why the pair is stated a second time instead of being factored out of
    /// <see cref="StartingDeck"/>; the seam itself is
    /// <see cref="ArmStarterBasics"/>.
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeSilent>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendSilent>();

    /// <summary>
    /// Kokomi's WHOLE offerable pool under the arm: the slice's 78 rows and
    /// nothing else.
    ///
    /// LISTED BY TYPE, not filtered by id prefix. A prefix match would be a
    /// second, softer definition of "which rows are the slice" living next to
    /// the sheet's own, and it would fail silently the day a row is renamed.
    /// These are the same 78 ids as <c>C.KOKOMI_OVERHAUL_POOL_IDS</c>, in the
    /// same order; the compiler holds the correspondence, because a deleted row
    /// takes its type with it and this file stops building.
    ///
    /// THE ANCIENTS ARE HERE, AND THEY HAVE TO BE (`EB-284`), for the reason
    /// <c>KleeOverhaulRoster.OfferablePool</c> states at length: this list is
    /// what `KokomiCardPool.FilterThroughEpochs` returns under the arm, which
    /// IS `GetUnlockedCards`, and `DustyTome.SetupForPlayer` draws its Ancient
    /// from that set. Without them Darv's Tome roll draws nothing and the
    /// act-two door NREs. Ancient rarity never rolls anywhere else, so this
    /// costs the arm's "her only reward pool" nothing.
    /// </summary>
    internal static IEnumerable<CardModel> OfferablePool() =>
        Slice().Concat(RosterAncientCards.Kokomi).Concat(MultiplayerSlice());

    /// <summary>
    /// THE MULTIPLAYER TIER (the co-op set): three cards offered only in
    /// co-op, outside the slice's count, on
    /// <c>KleeOverhaulRoster.MultiplayerSlice</c>'s terms -- each declares
    /// <c>CardMultiplayerConstraint.MultiplayerOnly</c>, and
    /// <c>GetUnlockedCards</c> drops it from a one-player run. Sim mirror:
    /// <c>C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS</c>.
    /// </summary>
    private static CardModel[] MultiplayerSlice() => new CardModel[]
    {
        ModelDb.Card<ProtoKkJointOrders>(),
        ModelDb.Card<ProtoKkCoordinatedStrike>(),
        ModelDb.Card<ProtoKkSangonomiyasCounsel>(),
        // POOL COMPLETION (2026-10-01): her fourth and fifth -- three
        // Uncommons and two Rares, the base game's shape.
        ModelDb.Card<ProtoKkTacticalRelay>(),
        ModelDb.Card<ProtoKkKuragesMercy>(),
    };

    /// <summary>The slice's own 78 rows, without the Ancient tail
    /// <see cref="OfferablePool"/> adds: 21 / 37 / 20 since the jellyfish
    /// build (2026-10-12), in the sheet's own order, then Gorou's four. The pool's
    /// history is in git (tag <c>kokomi-casket-frozen-2026-10-12</c>).</summary>
    private static CardModel[] Slice() => new CardModel[]
    {
        ModelDb.Card<ProtoKkFeint>(),
        ModelDb.Card<ProtoKkAmbush>(),
        ModelDb.Card<ProtoKkReadTheField>(),
        ModelDb.Card<ProtoKkTreatise>(),
        ModelDb.Card<ProtoKkWarCouncil>(),
        ModelDb.Card<ProtoKkNereidsAscension>(),
        ModelDb.Card<ProtoKkCoralBulwark>(),
        ModelDb.Card<ProtoKkTideWall>(),
        ModelDb.Card<ProtoKkTheMoonAShip>(),
        ModelDb.Card<ProtoKkSangoIsshin>(),
        ModelDb.Card<ProtoKkChangeOfPlans>(),
        ModelDb.Card<ProtoKkUndertow>(),
        ModelDb.Card<ProtoKkPreparedRetreat>(),
        ModelDb.Card<ProtoKkRiptide>(),
        ModelDb.Card<ProtoKkPincer>(),
        ModelDb.Card<ProtoKkFlank>(),
        ModelDb.Card<ProtoKkOpeningGambit>(),
        ModelDb.Card<ProtoKkSecondWave>(),
        ModelDb.Card<ProtoKkBreakwater>(),
        ModelDb.Card<ProtoKkSurgingShoal>(),
        ModelDb.Card<ProtoKkPressTheAdvantage>(),
        ModelDb.Card<ProtoKkDraftTheOrders>(),
        ModelDb.Card<ProtoKkTideturn>(),
        ModelDb.Card<ProtoKkPearlCurrent>(),
        ModelDb.Card<ProtoKkBubbleWard>(),
        ModelDb.Card<ProtoKkJellyfishDrift>(),
        ModelDb.Card<ProtoKkBrineSting>(),
        ModelDb.Card<ProtoKkUndertideLance>(),
        ModelDb.Card<ProtoKkGrandDesign>(),
        ModelDb.Card<ProtoKkMasterstroke>(),
        ModelDb.Card<ProtoKkDrowningPressure>(),
        ModelDb.Card<ProtoKkUndercurrentSnare>(),
        ModelDb.Card<ProtoKkAtWatersEdge>(),
        ModelDb.Card<ProtoKkBattleFormation>(),
        ModelDb.Card<ProtoKkSuffocatingDeep>(),
        ModelDb.Card<ProtoKkCoralCrash>(),
        ModelDb.Card<ProtoKkEveningWatch>(),
        ModelDb.Card<ProtoKkKurageVanguard>(),
        ModelDb.Card<ProtoKkWatatsumisGrace>(),
        ModelDb.Card<ProtoKkTidalRiposte>(),
        ModelDb.Card<ProtoKkShoalCall>(),
        ModelDb.Card<ProtoKkKurageCanopy>(),
        ModelDb.Card<ProtoKkTidalScreen>(),
        ModelDb.Card<ProtoKkShoalOfSpears>(),
        ModelDb.Card<ProtoKkSeasReproach>(),
        ModelDb.Card<ProtoKkTidalRebuke>(),
        ModelDb.Card<ProtoKkTurnabout>(),
        ModelDb.Card<ProtoKkKelpWall>(),
        ModelDb.Card<ProtoKkTidecleanse>(),
        ModelDb.Card<ProtoKkSeaGlassHarvest>(),
        ModelDb.Card<ProtoKkFlotsamSurge>(),
        ModelDb.Card<ProtoKkRiptideRuin>(),
        // THE RE-FOUNDING (2026-10-12, review/active/kokomi-card-paper-
        // 2026-10-12.md sec.2): twenty new rows, LAST, in the sheet's own
        // order (Grand Design keeps its old slot and id).
        ModelDb.Card<ProtoKkTidalSurge>(),
        ModelDb.Card<ProtoKkTurningTideChain>(),
        ModelDb.Card<ProtoKkWatatsumiDrill>(),
        ModelDb.Card<ProtoKkOrdersFromTheShrine>(),
        ModelDb.Card<ProtoKkKuragesWake>(),
        ModelDb.Card<ProtoKkWatatsumiMuster>(),
        ModelDb.Card<ProtoKkSangonomiyasOrders>(),
        ModelDb.Card<ProtoKkKurageBloom>(),
        ModelDb.Card<ProtoKkKurageBarrage>(),
        ModelDb.Card<ProtoKkWatchfulShoal>(),
        ModelDb.Card<ProtoKkFollowingCurrent>(),
        ModelDb.Card<ProtoKkBrineSpray>(),
        ModelDb.Card<ProtoKkSpearhead>(),
        ModelDb.Card<ProtoKkSteadyTide>(),
        ModelDb.Card<ProtoKkResolveOfWatatsumi>(),
        ModelDb.Card<ProtoKkGrandStrategist>(),
        ModelDb.Card<ProtoKkCallTheGenerals>(),
        ModelDb.Card<ProtoKkEndlessShoal>(),
        ModelDb.Card<ProtoKkDawnTide>(),
        ModelDb.Card<ProtoKkTamakushisWrath>(),
        // THE JELLYFISH BUILD (2026-10-12, review/active/kokomi-jellyfish-
        // growth-2026-10-12.md sec.3): two growth cards, LAST, in the sheet's
        // own order (`C.KOKOMI_JELLYFISH_IDS`). Measured Breath and Spring
        // Tide are cut.
        ModelDb.Card<ProtoKkAllStreamsFlow>(),
        ModelDb.Card<ProtoKkTheShapeOfWater>(),
        // KOKOMI V3 (2026-10-18, review/active/kokomi-cards-2026-10-18.md
        // sec.6): Unbroken Tide, LAST in the sheet's own order
        // (`C.KOKOMI_V3_IDS`). The pool becomes 79.
        ModelDb.Card<ProtoKkUnbrokenTide>(),
        // GOROU'S FOUR, her own cards since the re-founding (the ruling's
        // pick 3), ids kept: `C.KOKOMI_OWN_COMPANION_IDS`, LAST.
        ModelDb.Card<ProtoMiGorouInuzaka>(),
        ModelDb.Card<ProtoMiGorouWarBanner>(),
        ModelDb.Card<ProtoMiGorouJuuga>(),
        ModelDb.Card<ProtoMiGorouCrystalCollapse>(),
    };

    /// <summary>Her one starting relic under the arm. A list of one, so the
    /// seam in <c>Kokomi.StartingRelics</c> is one return rather than a
    /// conditional inside a collection initializer.</summary>
    internal static IReadOnlyList<RelicModel> StartingRelics() =>
        new RelicModel[]
        {
            ModelDb.Relic<Relics.TamakushiCasket>(),
        };
}
