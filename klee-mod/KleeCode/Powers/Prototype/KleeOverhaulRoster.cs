using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Powers;

/// <summary>
/// THE THREE WIRING SEAMS, and there are exactly three: what Klee OPENS with,
/// what she can be OFFERED, and WHICH PAIR OF BASICS IS HERS when a base-game
/// effect asks the CHARACTER for "your Strike and your Defend"
/// (<see cref="ArmStarterBasics"/>, the seam `EB-351` had to add). Sim twins
/// for the first two: <c>tier0.content.loader._starter_ids</c> and
/// <c>tier0.content.loader.pool_replacement</c>, which exist for the same
/// reason -- both readers of a starter and all five offer surfaces go through
/// one door each, so the two engines cannot disagree about what a run is. The
/// third has no sim twin: tier 0.5 models no relic that grants a basic.
///
/// WHY THE STARTER IS A REPLACEMENT AND NOT A SUBSTITUTION. The Sparks arm swaps
/// two of the ten slots and leaves eight standing, because its rule is a price
/// change. This arm's rule change is total: the shipped Ka-boom! has no
/// <i>Set off</i> clause and the shipped Pop! plants a Bomb that detonates
/// itself, so there is no shipped starter card the new rules leave meaning what
/// it printed. All ten move (the brief's sec.8 prints all ten).
///
/// WHY THE POOL IS A REPLACEMENT TOO. Same argument, one screen over: a reward
/// screen that could still offer the shipped 79 would be offering cards written
/// against rules the run is no longer playing. Slice one's own scope statement
/// is that the 28 rows are "Klee's only reward pool" for the prototype run.
///
/// THE OVERHAUL WINS WHERE THE TWO ARMS OVERLAP. A dev build compiles this arm
/// AND the Sparks arm, and both want Klee's starter. They are alternatives, not
/// layers -- the Sparks substitutions are priced inside the rules this arm
/// retires -- so with <c>KleeOverhaul.Enabled</c> the Sparks starter is not
/// reached. With it off, nothing here runs and the Sparks arm owns the starter
/// exactly as before, which is the acceptance condition.
/// </summary>
internal static class KleeOverhaulRoster
{
    /// <summary>
    /// Klee's ten opening cards under the arm, DRAFT 4 (slice packet sec.3,
    /// ruled R242 pick 3, in its order): Strike x4, Defend x4, Jumpy Dumpty,
    /// Ka-pow!.
    ///
    /// WHY THE CANONICAL SHAPE. [USER], R242: "the starting deck already does
    /// too much; base characters open with four Strikes, four Defends and two
    /// good cards of their own, and Klee had three, two and five." Draft 3's
    /// six ids are down to two of her own -- the plant (Jumpy Dumpty) and the
    /// cash button (Ka-pow!, now 0 energy with Retain on the upgrade). Kaboom!
    /// and Duck and Cover LEFT THE SHEET (R213 B: a rejected row is deleted,
    /// not commented out); Pop! and Dig In went back to
    /// <see cref="OfferablePool"/> as Commons.
    ///
    /// THESE ARE THE BASE GAME's STRIKE AND DEFEND, not renamed twins, and that
    /// is the ruling's own word. The base game ships ONE PER CHARACTER, not one
    /// shared pair -- <c>StrikeIronclad</c>, <c>StrikeSilent</c>,
    /// <c>StrikeDefect</c>, <c>StrikeRegent</c>, <c>StrikeNecrobinder</c> and
    /// the five matching Defends, all <c>public sealed</c>, all
    /// <c>CardRarity.Basic</c>, all 1 energy for 6 damage / 5 Block with
    /// <c>OnUpgrade</c> +3 (so Strike+ 9 and Defend+ 8 come for free). The
    /// decompiled source says why there are five: "The only difference between
    /// the starting Strike cards are portrait, attack vfx, and color."
    ///
    /// A MODDED CHARACTER CAN HOLD ONE. <c>CardModel.Pool</c> resolves by
    /// scanning <c>ModelDb.AllCardPools</c> for the pool whose
    /// <c>AllCardIds</c> contains the id, so an Ironclad basic in Klee's deck
    /// resolves to <c>IroncladCardPool</c> and nothing throws; its portrait
    /// path, its energy icon and its frame material all come off that pool,
    /// which is why the IRONCLAD pair is the right one for Klee: her own
    /// <c>KleeCardPool</c> already borrows <c>card_frame_red</c> and the
    /// <c>ironclad</c> energy colour, so the four Strikes sit in her hand in
    /// her own frame. The one visible seam is the deck screen's
    /// <c>DeckEntryCardColor</c>, which is the base pool's <c>D62000</c> rather
    /// than her <c>E85A4F</c> -- two reds a hair apart, reported not hidden.
    ///
    /// THE ELEMENT COMES FROM THE CHARACTER, NOT THE CARD. A base Strike is not
    /// an <c>IElementalCard</c> and never can be (it is sealed), so under the
    /// old per-card read it would have applied no Pyro at all. Rule 5 says her
    /// Attacks ARE ordinary Pyro hits, and tier0 has always answered that from
    /// the PLAYER's cadence (<c>effects._element_for</c>); the mod now does the
    /// same through <see cref="CatalystCadence"/>.
    ///
    /// COMPOSES WITH THE COMPANION ROLL by construction, the same way draft 3
    /// did: <c>KleeStartingCompanionsPatch.ReplaceFirst</c> matches on
    /// <c>card.GetType() == typeof(Kaboom)</c> and on
    /// <c>typeof(DuckAndCover)</c> -- her SHIPPED basics, which are different
    /// types from these -- so under this arm the companion roll finds no slot
    /// to take. That is a REAL consequence and it is reported, not hidden: her
    /// two starting companions do not arrive, and the slice's React loop draws
    /// its appliers from the reward slot instead.
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<StrikeIronclad>(),
        ModelDb.Card<StrikeIronclad>(),
        ModelDb.Card<StrikeIronclad>(),
        ModelDb.Card<StrikeIronclad>(),
        ModelDb.Card<DefendIronclad>(),
        ModelDb.Card<DefendIronclad>(),
        ModelDb.Card<DefendIronclad>(),
        ModelDb.Card<DefendIronclad>(),
        ModelDb.Card<ProtoKoJumpyDumpty>(),
        ModelDb.Card<ProtoKoKapow>(),
    };

    /// <summary>
    /// THE PAIR ABOVE, NAMED ONCE MORE FOR THE THIRD SEAM (`EB-351`).
    ///
    /// The base game lets a relic ask the CHARACTER for "your Strike" rather
    /// than reading the deck it is adding to, and under this arm the honest
    /// answer is the pair the starter opens with. <see cref="ArmStarterBasics"/>
    /// is the one place that answer is given and this is the one place it is
    /// stated, so the relic and the starter cannot drift apart.
    ///
    /// NOT FACTORED OUT OF <see cref="StartingDeck"/>, deliberately. That list
    /// is the ruled artifact (R242 pick 3 prints all ten in order) and its pin
    /// reads the ten <c>ModelDb.Card</c> calls straight off the compiled
    /// method; routing them through a helper would leave the pin reading the
    /// helper's name instead of the card's. The correspondence is held by a
    /// pin that reads BOTH bodies rather than by the compiler --
    /// `ArmStarterBasicsTests.The_relic_pair_is_the_pair_the_starter_opens_with`.
    /// </summary>
    internal static CardModel StarterStrike() => ModelDb.Card<StrikeIronclad>();

    /// <summary>The Defend half of <see cref="StarterStrike"/>'s pair.</summary>
    internal static CardModel StarterDefend() => ModelDb.Card<DefendIronclad>();

    /// <summary>
    /// Klee's WHOLE offerable pool under the arm: the slice's pool rows and
    /// nothing else.
    ///
    /// LISTED BY TYPE, not filtered by id prefix. A prefix match would be a
    /// second, softer definition of "which rows are the slice" living next to
    /// the sheet's own, and it would fail silently the day a row is renamed.
    /// These are the same ids as <c>C.KLEE_OVERHAUL_POOL_IDS</c>, in the
    /// same order; the compiler holds the correspondence, because a deleted row
    /// takes its type with it and this file stops building.
    ///
    /// FORTY-FIVE SINCE THE POOL PASS (2026-09-05, `EB-491`), and the TEN that
    /// arrived are the readings of rounds 13 to 16 made into cards: three for
    /// Cook, three for Spray, three for React and one bridge between Cook and
    /// Spray. Their own block at the end, in the sim's order. The pool is 8
    /// Rares, which is the brief's count.
    ///
    /// THIRTY-FIVE BEFORE THAT (the round-11 pool pass, 2026-09-04), and the
    /// one that arrived is <c>ProtoKoStokeTheFuse</c>: the arm's Spark SINK, the
    /// other half of the deadlock round 10 answered with Countdown. The
    /// round-11 and round-12 seats ended fights holding 4 to 9 unspent
    /// Sparks; this is where the bank goes. Its own block at the end, in the
    /// sim's order.
    ///
    /// THIRTY-FOUR BEFORE THAT (round 10), and the one that arrived is
    /// <c>ProtoKoCountdown</c>: the arm's only detonator priced in ENERGY
    /// that asks nothing else of the board. Its own block, in the sim's order.
    ///
    /// THIRTY-THREE BEFORE THAT (R252), and the two that arrived are the
    /// DEFENCE SHELF, a THIRD slice on the same terms as the second: Klee
    /// round 9's pick 1, taken at its default
    /// (`review/ruled/klee-overhaul-round-9-2026-09-04.md`). Every new row is
    /// keyed to the Bomb state and none is a plain Block. The pick drafted
    /// four and the R253 charter audit withdrew two, so the shelf ships as
    /// two. They are listed in their own block, in the sim's order.
    ///
    /// AND THE PIN THAT NOW HOLDS THIS LIST TO THE SHEET. R252 shipped the four
    /// rows -- sim ops, powers, codegen, tests, all green -- and did not add
    /// them HERE, so they compiled into `PrototypeRoster` (which is why nothing
    /// went red: `lint_pool_membership` only asks that a class be in SOME pool)
    /// and were never OFFERED. A live seat played eight fights on the deployed
    /// build and saw none of them. `tools/lint_arm_pool_parity.py` is the gate
    /// that would have caught it: every non-`basic` row on the sheet with this
    /// arm's id prefix must be named in this method, and the ids this method
    /// names must equal `C.KLEE_OVERHAUL_POOL_IDS` exactly, in order.
    ///
    /// THIRTY-ONE BEFORE THAT (R244), and the three that arrived are a SECOND
    /// slice rather than a redraft of this one: the ruled packet
    /// `review/ruled/klee-hexerei-readers-2026-09-02.md` adds Klee's three
    /// Hexerei readers, the cards in her own pool that pay for the coven's
    /// one-word mark. They are listed in their own block at the end.
    ///
    /// TWENTY-EIGHT AT DRAFT 4, and only ONE row is absent now. Dig In had left
    /// the OFFER pool at draft 3 to be the starter's Spark sink; the canonical
    /// starter has no room for it, so it comes back, and Pop! comes with it as
    /// a Common. Vermillion Pact is the one that stays out, on the packet's own
    /// sec.5 escape (see <c>VermillionPactNotBuilt</c>), so there is no row and
    /// no type to name.
    ///
    /// THE ANCIENTS ARE HERE, AND THEY HAVE TO BE (`EB-284`). This list is
    /// what `KleeCardPool.FilterThroughEpochs` returns under the arm, which IS
    /// `GetUnlockedCards` -- and `DustyTome.SetupForPlayer` draws a random
    /// `CardRarity.Ancient` card from exactly that set. The arm's first reading
    /// of "her only reward pool" left them out, so Darv's Dusty Tome roll drew
    /// nothing, `NextItem(...).Id` NRE'd inside
    /// `Darv.GenerateInitialOptions`, and [USER]'s Klee run ended at the act-two
    /// door. Including them costs the arm nothing it was trying to protect:
    /// reward rolls, transforms and shop inventory all filter Ancient rarity
    /// upstream (decompiled `CardFactory`), so an Ancient here is reachable
    /// through Dusty Tome and through nothing else. The whole argument, and the
    /// same defect on the shipped pools, is in `RosterAncientCards`;
    /// `tools/lint_ancient_coverage.py` gates both.
    /// </summary>
    internal static IReadOnlyList<CardModel> OfferablePool() =>
        Slice().Concat(RosterAncientCards.Klee).ToList();

    /// <summary>The slice's own rows, without the Ancient tail
    /// <see cref="OfferablePool"/> adds. Separate so the count the sim mirrors
    /// (`C.KLEE_OVERHAUL_POOL_IDS`) is a list this file states rather than a
    /// subtraction a reader has to do.</summary>
    private static CardModel[] Slice() => new CardModel[]
    {
        // Cook (8)
        ModelDb.Card<ProtoKoFishFlavoredBait>(),
        ModelDb.Card<ProtoKoPocketFireworks>(),
        ModelDb.Card<ProtoKoChainFuse>(),
        ModelDb.Card<ProtoKoExplosivesWorkshop>(),
        ModelDb.Card<ProtoKoCarefulArrangement>(),
        ModelDb.Card<ProtoKoBigBaddaBoom>(),
        ModelDb.Card<ProtoKoTheBigOne>(),
        ModelDb.Card<ProtoKoAlicesRecipe>(),
        // Spray (9 -- Pop! is the packet sec.4 table's first Spray row and it
        // OFFERS from draft 4)
        ModelDb.Card<ProtoKoPop>(),
        ModelDb.Card<ProtoKoMineToss>(),
        ModelDb.Card<ProtoKoFwoosh>(),
        ModelDb.Card<ProtoKoTinderToss>(),
        ModelDb.Card<ProtoKoQuickFuse>(),
        ModelDb.Card<ProtoKoBangBang>(),
        ModelDb.Card<ProtoKoRapidFire>(),
        ModelDb.Card<ProtoKoChainedReactions>(),
        ModelDb.Card<ProtoKoSparksNSplash>(),
        // React (4)
        ModelDb.Card<ProtoKoSizzle>(),
        ModelDb.Card<ProtoKoPerfectTiming>(),
        ModelDb.Card<ProtoKoFlameDance>(),
        ModelDb.Card<ProtoKoCatalyticConverter>(),
        // Currencies and defence (7 of 7; Dig In is back in the pool at draft 4)
        ModelDb.Card<ProtoKoAmmoScavenging>(),
        ModelDb.Card<ProtoKoPowderCharge>(),
        ModelDb.Card<ProtoKoDigIn>(),
        ModelDb.Card<ProtoKoSugarRush>(),
        ModelDb.Card<ProtoKoRunAway>(),
        ModelDb.Card<ProtoKoGrounded>(),
        ModelDb.Card<ProtoKoSorryJean>(),
        // THE DEFENCE SHELF (2 -- R252, Klee round 9 pick 1 at its default).
        // The pick drafted four; the R253 charter audit withdrew Fire Safety
        // and Safety Lesson, and they are on no surface. What is left is the
        // placer with a Block half a starting hand needs and the capped read
        // of the pile that asks for a deck around it. In
        // `C.KLEE_OVERHAUL_POOL_IDS`'s order, which is the sheet's.
        ModelDb.Card<ProtoKoDodocoCover>(),
        ModelDb.Card<ProtoKoCarefulNow>(),
        // The Hexerei readers (3 -- R244, the ruled packet's sec.2). One per
        // rarity, which is the ruling's own shape: a Common that reads the
        // turn, an Uncommon Power that is DEAD ALONE by ruling, and a Rare
        // that makes the hand a coven for one turn.
        ModelDb.Card<ProtoKoCovenErrand>(),
        ModelDb.Card<ProtoKoWitchesCircle>(),
        ModelDb.Card<ProtoKoAlicesIntroductionMagic>(),
        // THE POOL PASS (1 -- round 10, 2026-09-04). The energy-priced plain
        // detonator: 1 energy, Set off, draw a card, no Spark and no
        // condition. Three round-10 seats held Spark-priced detonators at 0
        // Spark with a fat Bomb on the enemy and nothing in hand that could
        // cash it; Ka-pow! is the starter's one card in ten.
        ModelDb.Card<ProtoKoCountdown>(),
        // THE POOL PASS (1 -- round 11, 2026-09-04). The Spark sink: 0
        // energy, X Sparks, and the whole bank goes into the largest Bomb at
        // 3 apiece. Round 10 gave the hand a detonator it could always fire;
        // this gives the bank somewhere to go, and it pays only if a Bomb is
        // already cooking.
        ModelDb.Card<ProtoKoStokeTheFuse>(),
        // THE POOL PASS (2026-09-05, `EB-491`). TEN rows off the readings of
        // rounds 13 to 16, in the sim's order: Cook's three (a Retained
        // detonator whose price rises while it waits, a second pile the size
        // of the first, and the lore card's AoE with a cost), Spray's three
        // (the Spark-paid Retained detonator, the Attack placer the Smoggy
        // reading asked for, and the board-wide Set off), React's three (an
        // aura-keyed grow with a floor, a tempo rider on the reaction, and the
        // Pact that breaks the one-aura rule for her chain), and the bridge
        // that splits a cooked pile in two.
        ModelDb.Card<ProtoKoLongFuse>(),
        ModelDb.Card<ProtoKoAllOfMyTreasures>(),
        ModelDb.Card<ProtoKoFishBlasting>(),
        ModelDb.Card<ProtoKoPocketMatch>(),
        ModelDb.Card<ProtoKoBombsAway>(),
        ModelDb.Card<ProtoKoFireworksShow>(),
        ModelDb.Card<ProtoKoKindling>(),
        ModelDb.Card<ProtoKoFlashPoint>(),
        ModelDb.Card<ProtoKoVermillionPact>(),
        ModelDb.Card<ProtoKoSplitCharge>(),
    };
}
