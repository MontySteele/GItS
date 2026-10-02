using System.Collections.Generic;
using System.Linq;
using Godot;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Klee's card pool. C1 contains only the four starter stubs; the slice list
/// (31 cards + companions, spec C2) lands via codegen from the YAML sheet.
///
/// C1 STUB: EnergyColorName / CardFrameMaterialPath borrow Ironclad's red
/// assets because we ship no .pck yet (has_pck: false). Custom frame + energy
/// art is an art-pass item, not a boot blocker.
/// </summary>
public sealed class KleeCardPool : CardPoolModel
{
    public override string Title => "klee";

    public override string EnergyColorName => "ironclad";

    public override string CardFrameMaterialPath => "card_frame_red";

    // Klee red, per spec C1.4 (artist's final call later).
    public override Color DeckEntryCardColor => new Color("E85A4F");

    public override Color EnergyOutlineColor => new Color("7A2418");

    public override bool IsColorless => false;

    /// <summary>
    /// THE OFFER. <c>GetUnlockedCards</c> is the only path into reward rolls
    /// (<c>CardCreationOptions.GetPossibleCards</c>) and card transforms
    /// (<c>CardFactory</c>), and this feeds it.
    ///
    /// THE CURRENT KIT (legacy cleanup stage 4, 2026-10-01): the overhaul's
    /// pool, her Ancients and the co-op tier, <c>KleeOverhaulRoster.OfferablePool</c>.
    /// With the arm off (the <c>-p:ShippedKits=true</c> gate only) the shipped
    /// offer: the shipped rows less the never-generated ones
    /// (<see cref="KleeOffPoolCards"/>) and less every prototype row.
    /// </summary>
    protected override IEnumerable<CardModel> FilterThroughEpochs(
        UnlockState unlockState, IEnumerable<CardModel> cards)
    {
#if PROTOTYPE_CARDS
        if (Powers.KleeOverhaul.Enabled)
        {
            return Powers.KleeOverhaulRoster.OfferablePool();
        }
#endif
        var current = PrototypeCards.Ids("klee");
        return base.FilterThroughEpochs(unlockState, cards)
            .Where(c => !KleeOffPoolCards.Ids.Contains(c.Id)
                        && !current.Contains(c.Id));
    }

    /// <summary>
    /// MEMBERSHIP: every card whose <c>CardModel.Pool</c> is Klee's. A card in
    /// no pool throws "You monster!" the moment it is drawn
    /// (<see cref="KleeOffPoolCards"/>, <c>tools/lint_pool_membership.py</c>).
    ///
    /// THE PROTOTYPE ROWS FIRST AND AS THE POOL (legacy cleanup stage 4): every
    /// `proto_` row she owns -- her kit, its starter and tokens, and the
    /// companion roster (Mondstadt, Inazuma and Fontaine) -- then her
    /// Ancients. The shipped rows follow as members only, never offered while
    /// the arm is on, until stage 5 deletes them (<see cref="ShippedRows"/>).
    /// </summary>
    protected override CardModel[] GenerateAllCards() =>
        PrototypeCards.For("klee")
            .Concat(RosterAncientCards.Klee)
            .Concat(ShippedRows())
            .Concat(KleeOffPoolCards.All)
            .Distinct()
            .ToArray();

    /// <summary>The shipped kit's rows (legacy cleanup stage 5 deletes them).
    /// Members so a shipped card still resolves its pool; offered only with
    /// the arm off.</summary>
    private static CardModel[] ShippedRows() => new CardModel[]
    {
        // Starters (hand-written).
        ModelDb.Card<Kaboom>(),
        ModelDb.Card<DuckAndCover>(),
        ModelDb.Card<Pop>(),

        // Aura-application batch (R23, hand-written): conditional and
        // per-target aura/bomb bonuses are not codegen ops.
        ModelDb.Card<Sizzle>(),
        ModelDb.Card<FlameDance>(),
        ModelDb.Card<KaboomBeetleSwarm>(),
        ModelDb.Card<ElementalEcstasy>(),

        // Generated from docs/klee-cards.yaml by tools/gen_klee_cards.py.
        // Mechanical subset: damage/block/draw/place_bomb/gain_spark.
        // Cards needing powers, burst energy, auras or conditionals are
        // blocked in Generated/manifest.json until those systems land.
        //
        // These carry the pool's rarity coverage: reward and transform
        // generation draws Common/Uncommon/Rare, and a pool with none of
        // those soft locks the reward screen after every combat (finding 17).
        ModelDb.Card<AlchemicalCuriosity>(),
        ModelDb.Card<AllMyTreasures>(),
        ModelDb.Card<AmmoScavenging>(),
        // Companion-op batch: the four cards that read the companion
        // system (cost mod / copy / replay / played-ledger).
        ModelDb.Card<BestFriendsForever>(),
        ModelDb.Card<BigBaddaBoom>(),
        ModelDb.Card<BlastRadius>(),
        // Power-card pass: unblocked by the apply_power op.
        ModelDb.Card<BlazingDelight>(),
        ModelDb.Card<BombVoyage>(),
        ModelDb.Card<BombsAway>(),
        // Conditional batch: predicate reads verified against the sim
        // (this_cost_zero / has_spark / reaction_triggered_by_this /
        // killed_target) plus the repeat tail (sim resolve_card).
        ModelDb.Card<BoomGoesTheDynamite>(),
        ModelDb.Card<BorrowedBrilliance>(),
        // R36 batch: unblocked by the discard op (random victim,
        // kit-exempt pool).
        ModelDb.Card<BrightIdea>(),
        ModelDb.Card<CantCatchMe>(),
        // Bomb-op batch: unblocked by detonate/modify_bombs/move_bombs/
        // chance_bomb_per_detonation riding the new BombPower surface.
        ModelDb.Card<CarefulArrangement>(),
        ModelDb.Card<CatalyticConversion>(),
        ModelDb.Card<ChainFuse>(),
        ModelDb.Card<ChainedReactions>(),
        // Burst spike: unblocked by the burst_energy op.
        ModelDb.Card<ClockworkToy>(),
        ModelDb.Card<ClusterCharge>(),
        ModelDb.Card<CombustionStudy>(),
        // X-cost batch (R34): HasEnergyCostX + ResolveEnergyXValue.
        ModelDb.Card<ControlledDemolition>(),
        ModelDb.Card<Crackle>(),
        ModelDb.Card<DaDaDa>(),
        // Small-ops batch: energy / scry_discard / add_card /
        // exhaust_from. Confiscated (Fish Blasting's Status token) is
        // deliberately NOT pooled -- Status rarity, created at play.
        ModelDb.Card<DodgeRoll>(),
        ModelDb.Card<DoublePop>(),
        ModelDb.Card<EagerToHelp>(),
        ModelDb.Card<EndlessFireworks>(),
        ModelDb.Card<ExplosiveFrags>(),
        ModelDb.Card<ExplosivesWorkshop>(),
        ModelDb.Card<FishBlasting>(),
        ModelDb.Card<FishFlavoredBait>(),
        ModelDb.Card<FlameOnTheWick>(),
        ModelDb.Card<FriendlyVisit>(),
        // Formula batch: 2+Sparks hit count (SparksAsResolved -- the
        // post-spend bank) and per-detonation damage rider
        // (BombPower.DetonationsThisCombat).
        ModelDb.Card<GleefulBarrage>(),
        ModelDb.Card<GrandFinale>(),
        ModelDb.Card<HideAndSeek>(),
        // W3 Spark sinks (EB-118 Phase 3, R211): the first three cards on
        // any sheet to print `spend_spark`. SparkPower.Spend has been in
        // the mod since Phase 2 and no card called it until these.
        ModelDb.Card<HoldTheLine>(),
        ModelDb.Card<HotHands>(),
        ModelDb.Card<JumpyDumpty>(),
        ModelDb.Card<JumpyDumptyMk2>(),
        ModelDb.Card<MineToss>(),
        ModelDb.Card<NoHoldingBack>(),
        ModelDb.Card<PatchedDress>(),
        ModelDb.Card<PerfectTiming>(),
        ModelDb.Card<PlaytimeForever>(),
        ModelDb.Card<PocketFireworks>(),
        ModelDb.Card<PowderCharge>(),          // W3 sink (see HoldTheLine)
        // Bomb-op batch.
        ModelDb.Card<QuickFuse>(),
        ModelDb.Card<RapidFire>(),
        ModelDb.Card<RemoteDetonator>(),
        ModelDb.Card<RunAway>(),
        ModelDb.Card<SecretStash>(),
        ModelDb.Card<SkipAndHop>(),
        ModelDb.Card<SmokeAndSparks>(),        // W3 sink (see HoldTheLine)
        ModelDb.Card<Snap>(),
        ModelDb.Card<SorryJean>(),
        ModelDb.Card<SparkCollection>(),
        ModelDb.Card<SparkKnightStyle>(),
        ModelDb.Card<SparklyExplosion>(),
        ModelDb.Card<SparklyTreasure>(),
        ModelDb.Card<SpiritedAway>(),
        // Weak/Vulnerable batch: native core debuff PowerModels
        // (WeakPower/VulnerablePower), semantics verified == tier0.
        ModelDb.Card<Spooked>(),
        ModelDb.Card<StudyBuddy>(),
        ModelDb.Card<StudyOfExplosions>(),
        ModelDb.Card<SugarRush>(),
        ModelDb.Card<SurpriseVisit>(),
        ModelDb.Card<TailOfFlame>(),
        ModelDb.Card<TripWire>(),
        ModelDb.Card<TrueSparkKnight>(),
        ModelDb.Card<VermillionPact>(),
        ModelDb.Card<WarmGlow>(),
    };
}
