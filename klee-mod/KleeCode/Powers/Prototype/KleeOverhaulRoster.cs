using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE TWO WIRING SEAMS, and there are exactly two: what Klee OPENS with and
/// what she can be OFFERED. Sim twins: <c>tier0.content.loader._starter_ids</c>
/// and <c>tier0.content.loader.pool_replacement</c>, which exist for the same
/// reason -- both readers of a starter and all five offer surfaces go through
/// one door each, so the two engines cannot disagree about what a run is.
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
    /// Klee's ten opening cards under the arm, DRAFT 3 (slice packet sec.3, in
    /// its order): Kaboom! x2, Ka-pow! x2, Duck and Cover x3, Dig In, Pop!,
    /// Jumpy Dumpty. Ten cards, SIX ids.
    ///
    /// WHAT DRAFT 3 MOVED, after [USER]'s first run: draft 2 put <i>Set off</i>
    /// on every starter Attack, so attacking and cashing were one act and
    /// nothing ever grew. The plain hit (Kaboom!) and the cash button (Ka-pow!)
    /// are now two cards at two copies each, and <c>ProtoKoDigIn</c> moves IN
    /// from the pool as the starter's one Spark sink -- which is why its row is
    /// <c>rarity: basic</c> on the surface and why it is no longer in
    /// <see cref="OfferablePool"/>.
    ///
    /// COMPOSES WITH THE COMPANION ROLL by construction, the same way the Sparks
    /// starter does: <c>KleeStartingCompanionsPatch.ReplaceFirst</c> matches on
    /// <c>card.GetType() == typeof(Kaboom)</c> and on
    /// <c>typeof(DuckAndCover)</c>, and none of these ten is either type -- so
    /// under this arm the companion roll finds no slot to take. That is a REAL
    /// consequence and it is reported, not hidden: her two starting companions
    /// do not arrive, and the slice's React loop draws its appliers from the
    /// reward slot instead.
    /// </summary>
    internal static IEnumerable<CardModel> StartingDeck() => new CardModel[]
    {
        ModelDb.Card<ProtoKoKaboom>(),
        ModelDb.Card<ProtoKoKaboom>(),
        ModelDb.Card<ProtoKoKapow>(),
        ModelDb.Card<ProtoKoKapow>(),
        ModelDb.Card<ProtoKoDuckAndCover>(),
        ModelDb.Card<ProtoKoDuckAndCover>(),
        ModelDb.Card<ProtoKoDuckAndCover>(),
        ModelDb.Card<ProtoKoDigIn>(),
        ModelDb.Card<ProtoKoPop>(),
        ModelDb.Card<ProtoKoJumpyDumpty>(),
    };

    /// <summary>
    /// Klee's WHOLE offerable pool under the arm: the slice's pool rows and
    /// nothing else.
    ///
    /// LISTED BY TYPE, not filtered by id prefix. A prefix match would be a
    /// second, softer definition of "which rows are the slice" living next to
    /// the sheet's own, and it would fail silently the day a row is renamed.
    /// These are the same 26 ids as <c>C.KLEE_OVERHAUL_POOL_IDS</c>, in the
    /// same order; the compiler holds the correspondence, because a deleted row
    /// takes its type with it and this file stops building.
    ///
    /// TWENTY-SIX, NOT THE PACKET'S TWENTY-SEVEN, and two rows are absent for
    /// two different reasons. Dig In left the OFFER pool at draft 3 because it
    /// joined the starter above (sec.3), which is also what took the packet's
    /// sec.4 table from 28 offerable rows to 27. Vermillion Pact is the other:
    /// it is out on the packet's own sec.5 escape (see
    /// <c>VermillionPactNotBuilt</c>), so there is no row and no type to name.
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
        // Spray (8)
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
        // Currencies and defence (6 of 7; Dig In is in the starter since draft 3)
        ModelDb.Card<ProtoKoAmmoScavenging>(),
        ModelDb.Card<ProtoKoPowderCharge>(),
        ModelDb.Card<ProtoKoSugarRush>(),
        ModelDb.Card<ProtoKoRunAway>(),
        ModelDb.Card<ProtoKoGrounded>(),
        ModelDb.Card<ProtoKoSorryJean>(),
    };
}
