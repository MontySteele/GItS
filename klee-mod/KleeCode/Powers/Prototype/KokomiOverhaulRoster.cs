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
/// the arm has turned off. Tamakushi Casket takes the slot and carries the
/// jellyfish's strike instead. THE COMPANION REWARD SLOT SURVIVES THE SWAP,
/// because it rides the relic in this mod purely for lifetime reasons and the
/// slice's Commander loop draws its whole army from it.
///
/// WHY THE POOL IS A REPLACEMENT TOO. Same argument, one screen over: a reward
/// screen that could still offer the shipped 76 would be offering cards written
/// against rules the run is no longer playing -- an Exhaust that pays Charge, a
/// Muster that transforms, a Burst that gates. Slice one's own scope statement
/// is that the 26 rows are her only reward pool for the prototype run; R246
/// pick 2 added the two defensive rows `EB-335` builds, making it 28, and
/// round 9 pick 1's tempo shelf added two more, making it 30.
///
/// THE OVERHAUL WINS WHERE IT MEETS THE KURAGE'S MEMORY. A dev build compiles
/// this arm AND that one, and both want her starter. They are alternatives, not
/// layers -- the memory is priced inside the Charge bank this arm retires -- so
/// with <c>KokomiOverhaul.Enabled</c> the memory's starter substitution is not
/// reached and its rules are switched off at the funnel. With it off, nothing
/// here runs and the memory arm owns the starter exactly as before, which is
/// the acceptance condition.
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
    /// HER ATTACKS STILL APPLY HYDRO. A base Strike cannot implement
    /// <c>IElementalCard</c> (it is sealed), so the mod's per-card element read
    /// would have given it none. The catalyst cadence is a fact about the
    /// CHARACTER -- tier0's <c>effects._element_for</c> has always said so --
    /// and <see cref="CatalystCadence"/> now says it on this side too.
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
    /// Kokomi's WHOLE offerable pool under the arm: the slice's 30 rows and
    /// nothing else.
    ///
    /// LISTED BY TYPE, not filtered by id prefix. A prefix match would be a
    /// second, softer definition of "which rows are the slice" living next to
    /// the sheet's own, and it would fail silently the day a row is renamed.
    /// These are the same 30 ids as <c>C.KOKOMI_OVERHAUL_POOL_IDS</c>, in the
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
        Slice().Concat(RosterAncientCards.Kokomi);

    /// <summary>The slice's own 35 rows, without the Ancient tail
    /// <see cref="OfferablePool"/> adds.</summary>
    private static CardModel[] Slice() => new CardModel[]
    {
        // The Tactician -- Plans, and the cards that pay per Plan (9)
        ModelDb.Card<ProtoKkFeint>(),
        ModelDb.Card<ProtoKkAmbush>(),
        ModelDb.Card<ProtoKkReadTheField>(),
        ModelDb.Card<ProtoKkExposedFlank>(),
        ModelDb.Card<ProtoKkTreatise>(),
        ModelDb.Card<ProtoKkSongOfPearls>(),
        ModelDb.Card<ProtoKkWarCouncil>(),
        ModelDb.Card<ProtoKkNereidsAscension>(),
        ModelDb.Card<ProtoKkTheMoonOverlooksTheWaters>(),
        // The Priestess -- Block through the jellyfish, Mend at Rare (9)
        ModelDb.Card<ProtoKkSeaSaltPrayer>(),
        ModelDb.Card<ProtoKkDeepCurrent>(),
        ModelDb.Card<ProtoKkCoralBulwark>(),
        ModelDb.Card<ProtoKkCleansingWave>(),
        // `EB-335`, R246 pick 2: the kit's own defence in act 2.
        ModelDb.Card<ProtoKkTideWall>(),
        ModelDb.Card<ProtoKkShellGuard>(),
        ModelDb.Card<ProtoKkTheCloudsLikeWaves>(),
        ModelDb.Card<ProtoKkTheMoonAShip>(),
        ModelDb.Card<ProtoKkSangoIsshin>(),
        // The Commander -- Gorou, go (4)
        ModelDb.Card<ProtoKkRally>(),
        ModelDb.Card<ProtoKkVanguard>(),
        ModelDb.Card<ProtoKkTheGeneralsBanner>(),
        ModelDb.Card<ProtoKkChainOfCommand>(),
        // Currencies, tempo, and the one replay (6)
        ModelDb.Card<ProtoKkStolenChapter>(),
        ModelDb.Card<ProtoKkChangeOfPlans>(),
        ModelDb.Card<ProtoKkUndertow>(),
        ModelDb.Card<ProtoKkSaltLine>(),
        ModelDb.Card<ProtoKkBattlePlan>(),
        ModelDb.Card<ProtoKkMoonsReflection>(),
        // THE TEMPO SHELF (round 9 pick 1 at its default, 2026-09-04): the
        // two rows that let a Plan be held or hurried. Held Tide and Tidal
        // Rhythm, the drafted other two, were withdrawn on the R253 charter
        // audit and are not built. LAST, in the sheet's
        // own order, because `tools/lint_arm_pool_parity.py` compares this
        // list to the sheet and to `C.KOKOMI_OVERHAUL_POOL_IDS` BY ORDER --
        // the gate that exists because R252's defence shelf shipped
        // unofferable when a `Slice()` was forgotten.
        ModelDb.Card<ProtoKkTideChart>(),
        ModelDb.Card<ProtoKkRipple>(),
        // POOL PASS ONE (`EB-492`,
        // `review/active/kokomi-pool-pass-2026-09-05.md`): Plan density in the
        // OFFER rather than in the starter. Three Attacks with a Plan line,
        // the morning's payoff on a Common Attack, and a Skill that does both
        // halves only when planned. LAST, in the sheet's own order, for the
        // ordering reason the shelf above states.
        ModelDb.Card<ProtoKkRiptide>(),
        ModelDb.Card<ProtoKkPincer>(),
        ModelDb.Card<ProtoKkFlank>(),
        ModelDb.Card<ProtoKkWellLaid>(),
        ModelDb.Card<ProtoKkFeignedRetreat>(),
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
