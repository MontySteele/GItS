using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using BaseLib.Abstracts;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE OVERHAUL, ROUND THREE: [USER]'s own run, and the five things it broke.
///
///   * The STARTER, draft 3 (slice packet sec.3). Draft 2 put <i>Set off</i> on
///     every starter Attack, so attacking and cashing were one act and nothing
///     ever grew.
///   * <c>EB-279</c> -- rule 3's Jump is a SWEEP, and every moment it ran was a
///     moment the arm itself caused, so a kill by anything else left the Bombs
///     in the register and off the board. [USER] saw them "not move".
///   * <c>EB-280</c> -- every Set off Attack printed its damage as a literal,
///     so Strength, Vulnerable and the Effigy's mark moved the hit and not the
///     face.
///   * <c>EB-282</c> -- seven Spark-priced rows restated their price in the
///     body while the cost slot already showed the badge.
///   * <c>EB-283</c> / <c>EB-277</c> -- no prototype row upgraded, so a run
///     under either arm had no campfire choice at all.
///   * <c>EB-284</c> -- the arm pools omitted the Ancient tail, so Darv's
///     Dusty Tome roll drew nothing and the act-two door NRE'd.
///
/// THE COLLECTION IS LOAD-BEARING, for the reason
/// <c>KleeOverhaulRoundOneFixTests</c> gives: <c>KleeOverhaul.Enabled</c> is
/// one static for the whole process and <c>KleeOverhaulRuleTests.The_arm_ships_off</c>
/// reads it.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulRoundThreeTests
{
    private static IReadOnlyList<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card")).ToList();

    // ---- the starter, draft 3 --------------------------------------------

    [Fact]
    public void Dig_in_and_pop_are_back_in_the_offer_pool_at_draft_four()
    {
        // DRAFT 3 moved Dig In OUT of the offer pool and into the starter, and
        // this pin was the half that would otherwise go unnoticed: a card in
        // both lists is a starter the reward screen also sells. R242's
        // canonical starter has room for neither, so both are back and the
        // disjointness still has to hold -- which the draft-4 starter pin in
        // `BaseBasicsTests` asserts from the other end.
        // THIRTY-ONE SINCE R244: the ruled packet
        // `review/ruled/klee-hexerei-readers-2026-09-02.md` adds Klee's three
        // Hexerei readers as a SECOND slice, which is why the count moved
        // without anything in draft 4 being redrafted.
        var slice = Cards("KleeOverhaulRoster", "Slice");
        Assert.Equal(31, slice.Count);
        Assert.Contains(slice, c => c.Contains("ProtoKoDigIn"));
        Assert.Contains(slice, c => c.Contains("ProtoKoPop"));
        // OFFERABLE means not Basic: a Basic row cannot be rolled.
        Assert.Equal(CardRarity.Common, new ProtoKoDigIn().Rarity);
        Assert.Equal(CardRarity.Common, new ProtoKoPop().Rarity);
    }

    // ---- EB-284: the Ancient tail ----------------------------------------

    [Fact]
    public void The_arm_pool_carries_her_ancient_card()
    {
        // The arm's `FilterThroughEpochs` RETURNS this list and never reaches
        // the shipped pool, so under the flag this list IS `GetUnlockedCards`
        // -- and `DustyTome.SetupForPlayer` draws its `CardRarity.Ancient` card
        // from exactly that set. Structural, because building the models needs
        // `ModelDb`; `tools/lint_ancient_coverage.py` owns the other half (the
        // ledger is non-empty and everything in it really is Ancient).
        var pool = Il.Calls(Il.Method("KleeOverhaulRoster", "OfferablePool"));
        Assert.Contains("RosterAncientCards.get_Klee", pool);
        Assert.Contains("KleeOverhaulRoster.Slice", pool);
    }

    // ---- EB-280: the Set off's own hit is the printed number --------------

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>`CanonicalVars` is protected, so it is read the way every
    /// other internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", HeadlessGame.All)!
            .GetValue(card)!).ToList();

    [Fact]
    public void A_set_off_attack_declares_a_damage_var_and_prints_its_token()
    {
        // The acceptance, on the card the tester read wrong: Ka-pow! declares
        // the same `DamageVar` an `op: damage` row declares, and its face
        // renders that var rather than a literal -- so Strength moves the two
        // together, which is what "printed 10, dealt 14" was not.
        var card = new ProtoKoKapow();
        var damage = Vars(card).OfType<DamageVar>().Single();
        Assert.Equal(4m, damage.BaseValue);          // R242: 0 energy for 4
        Assert.Contains("{Damage:diff()}", Face(card));
        Assert.DoesNotContain("4", Face(card));
    }

    [Fact]
    public void Every_set_off_attack_on_the_surface_carries_the_var()
    {
        // Class-wide, so a future Set off row cannot quietly go back to a
        // literal: every generated prototype card whose play calls a SetOff*
        // verb AND deals damage of its own declares a Damage var and prints
        // its token. The nine the row names are exactly this set.
        var carriers = ProtoTypes()
            .Where(t => Il.Calls(Play(t)).Any(
                c => c.StartsWith("ProtoBombPower.SetOff")))
            .Select(t => (CardModel)Activator.CreateInstance(t)!)
            .Where(c => Vars(c).OfType<DamageVar>().Any())
            .ToList();

        // NINE. Flame Dance is in: its Damage var is its AoE hit's rather
        // than its Set off's (its Set off deals nothing of its own), and what
        // is being pinned is that a Set off row's printed number is a var,
        // whichever clause owns it. The Big One is OUT since R243 ([USER]:
        // "move The Big One to 4x with no flat number"): it calls SetOffAimed
        // with no hit of its own, declares no Damage var, and the filter
        // above drops it -- a card with no number has no number to print.
        Assert.Equal(9, carriers.Count);
        foreach (var card in carriers)
        {
            Assert.Contains("{Damage:diff()}", Face(card));
        }
    }

    [Fact]
    public void The_set_off_verbs_take_the_var_and_not_a_literal()
    {
        // The other end of the same wire. A `decimal` parameter is what lets a
        // generated card hand in `DynamicVars.Damage.BaseValue`; an `int` one
        // would force the emitter back to a literal, which is the defect.
        foreach (var name in new[] { "SetOffAimed", "SetOffAll", "SetOffRandom" })
        {
            var method = typeof(ProtoBombPower)
                .GetMethod(name, HeadlessGame.All)!;
            var damage = method.GetParameters()
                .Single(p => p.Name == "damage");
            Assert.Equal(typeof(decimal), damage.ParameterType);
        }
    }

    // ---- EB-282: the price is on the badge, not in the body ---------------

    [Fact]
    public void A_spark_priced_row_does_not_restate_its_price_in_the_body()
    {
        // The seven rows the row names. The price is not GONE -- it is on
        // `PrintedSparkPrice`, which is what the cost badge and the playability
        // gate both read, and what `understudy.qa_packet` now prints in the
        // blind page's cost slot.
        foreach (var card in new CardModel[]
                 {
                     new ProtoKoFwoosh(), new ProtoKoTinderToss(),
                     new ProtoKoQuickFuse(), new ProtoKoBangBang(),
                     new ProtoKoPowderCharge(), new ProtoKoDigIn(),
                     new ProtoKoSugarRush(),
                 })
        {
            Assert.DoesNotContain("Spend", Face(card));
            Assert.True(((ISparkPricedCard)card).PrintedSparkPrice > 0,
                        card.GetType().Name);
        }
    }

    // ---- EB-261, round three's shape: Quick Fuse still refuses -------------

    [Fact]
    public void Quick_fuse_still_refuses_on_a_bomb_less_board_after_the_grow()
    {
        // Draft 3 gave Quick Fuse a `grow_bombs` AHEAD of its Set off, and the
        // gate is DERIVED from the row -- so the naive derivation would have
        // seen a second effect and dropped the gate, handing back the exact
        // defect EB-261 closed: a card that spends the Spark and does nothing.
        // Growing a pile that is not there does as little as setting one off.
        var klee = Seat.Klee().WithPower<SparkPower>(3);
        var enemy = Seat.Klee(30).Creature;
        ProtoBombs.Board(klee.Creature, enemy);

        var card = new ProtoKoQuickFuse();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", klee.Player);

        Assert.Contains("grow", Face(card), StringComparison.OrdinalIgnoreCase);
        Assert.Equal("no enemy is holding a Bomb",
                     KleeUnplayableReason.For(card));

        ProtoBombs.Place(enemy, klee.Creature, new ProtoBombs.Charge(4));
        Assert.Null(KleeUnplayableReason.For(card));
    }

    // ---- EB-279: the sweep runs on a death the arm did not cause ----------

    [Fact]
    public void A_bomb_orphaned_by_a_plain_kill_is_owed_a_jump()
    {
        // REAL, and it is the half that was broken: the register still holds
        // the pile of an enemy killed by anything at all, and `Register.Claim`
        // hands its charges over the moment that enemy is dead. Before EB-279
        // nothing ASKED between the kill and the next Set off or turn start.
        // The placing half of the jump needs a live CombatState and is pinned
        // structurally below.
        ProtoBombPower.Register.Rebase(null);
        var klee = Seat.Klee();
        var victim = Seat.Klee(30).Creature;
        var survivor = Seat.Klee(30).Creature;
        var combat = ProtoBombs.Board(klee.Creature, victim, survivor);

        var pile = ProtoBombs.Place(victim, klee.Creature,
                                    new ProtoBombs.Charge(4),
                                    new ProtoBombs.Charge(6, IsMine: true));
        ProtoBombPower.Register.Note(pile);

        // Alive: nothing owed, whatever else is going on.
        Assert.Empty(ProtoBombPower.Register.Claim(combat));

        Seat.Set(victim, "CurrentHp", 0);          // a plain Attack killed it
        var owed = ProtoBombPower.Register.Claim(combat);
        var claimed = Assert.Single(owed);
        Assert.Equal(victim, claimed.Owner);
        Assert.Equal(klee.Creature, claimed.Applier);
        Assert.Equal(new[] { 4, 6 },
                     claimed.Charges.Select(c => c.Size).ToArray());
        // And the charges left the pile with it, so a second sweep in the same
        // beat cannot place them twice.
        Assert.Equal(0, pile.TotalSize);
        Assert.Empty(ProtoBombPower.Register.Claim(combat));
        ProtoBombPower.Register.Rebase(null);
    }

    [Fact]
    public void The_sweep_is_asked_after_every_death_and_every_card_play()
    {
        // Structural, because a jump PLACES a power and that needs a live
        // CombatState. What is pinned is the wiring the row asks for: the two
        // moments the arm does not cause both reach the same sweep.
        var hooks = typeof(KleeOverhaulSweepHooks);
        foreach (var name in new[] { "AfterDeath", "AfterCardPlayed" })
        {
            var calls = Il.Calls(hooks.GetMethod(name, HeadlessGame.All)!);
            Assert.Contains("ProtoBombPower.SweepJumps", calls);
            Assert.Contains("KleeOverhaul.get_Enabled", calls);
        }

        // A BROADCAST listener, not a power on the dying enemy: the corpse's
        // powers are stripped inside the kill and cannot be trusted to fire.
        Assert.True(new KleeOverhaulSweepHooks().ShouldReceiveCombatHooks);
        // The subscription is made inside the one lambda KleeMod.Initialize
        // hands to `ModHelper.SubscribeForCombatStateHooks`, which the C#
        // compiler lifts into a nested closure type -- so the call sets of
        // KleeMod AND of its nested types are what carry it.
        var modType = typeof(global::KleeMod.KleeMod);
        var wiring = modType.GetMethods(HeadlessGame.All)
            .Concat(modType.GetNestedTypes(HeadlessGame.All)
                .SelectMany(t => t.GetMethods(HeadlessGame.All)
                    .Cast<MethodBase>()))
            .Where(m => m.DeclaringType == modType
                        || m.DeclaringType?.DeclaringType == modType)
            .SelectMany(Il.Calls)
            .ToList();
        Assert.Contains("KleeOverhaulSweepHooks.Subscribe", wiring);

        // The three sweeps that were already there are KEPT, each being the
        // earliest moment for the death IT is about.
        Assert.Contains("ProtoBombPower.SweepJumps",
                        Il.Calls(typeof(ProtoBombPower).GetMethod(
                            "BeforeSideTurnStart", HeadlessGame.All)!));
        Assert.Contains("ProtoBombPower.SweepJumps",
                        Il.Calls(typeof(ProtoBombPower).GetMethod(
                            "SetOff", HeadlessGame.All)!));
        Assert.Contains("ProtoBombPower.SweepJumps",
                        Il.Calls(typeof(ProtoBombPower).GetMethod(
                            "BeforeDamageReceived", HeadlessGame.All)!));
    }

    // ---- EB-283 / EB-277: every prototype row upgrades ---------------------

    private static IEnumerable<Type> ProtoTypes() =>
        typeof(ProtoKoKapow).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && typeof(CardModel).IsAssignableFrom(t)
                        && !t.IsAbstract
                        && t.GetConstructor(Type.EmptyTypes) != null);

    private static MethodBase Play(Type card) =>
        card.GetMethod("OnPlay", HeadlessGame.All)!;

    /// <summary>The four prefixes the Prototype-stage rule covers, as class
    /// name prefixes (`tier0.content.upgrades.PROTOTYPE_DEFAULT_PREFIXES`).</summary>
    private static readonly string[] RuleClasses =
        { "ProtoKo", "ProtoKk", "ProtoMc", "ProtoMi" };

    [Fact]
    public void Every_overhaul_row_that_the_rule_reaches_has_an_upgrade_body()
    {
        // `EB-283`'s acceptance, and `EB-277`'s close from the other side:
        // before this, `OnUpgrade` was an empty body carrying R24's "no
        // ratified delta" comment on EVERY prototype row, so Kokomi's cards
        // upgraded into copies of themselves and Klee's offered no campfire at
        // all. The rule's own last clause leaves a 0- or 1-cost row with no
        // printed number base-only, so this asserts a MAJORITY rather than
        // totality -- and names the exceptions below so a silent regression
        // cannot hide inside them.
        var rows = ProtoTypes()
            .Where(t => RuleClasses.Any(p => t.Name.StartsWith(p)))
            .ToList();
        Assert.True(rows.Count > 100, $"only {rows.Count} rows in the rule's set");

        // TWO THIRDS, not three quarters, and draft 6 is why the bar moved.
        // The Prototype-stage rule reads a row's `effects:` -- its NOW-line --
        // and Kokomi's rewrite put sixteen rows' numbers in a `plan:` list
        // instead, seven of them with no now-line at all. Those numbers are
        // deliberately NOT upgradeable: a planned clause is emitted as a
        // literal on `PlanClauses`, so a `plan`-derived delta would be a
        // declared upgrade the emitter cannot express, which stops the run by
        // name. So the rule's coverage of HER rows fell honestly, and the two
        // assertions that carry the weight are unchanged: a majority upgrade,
        // and every exception is a row the rule's own last clause allows.
        var upgraded = rows.Where(HasUpgradeBody).ToList();
        Assert.True(upgraded.Count * 3 >= rows.Count * 2,
                    $"only {upgraded.Count} of {rows.Count} rows upgrade");

        // AND THE EXCEPTIONS ARE EXACTLY THE ONES THE RULE ALLOWS, which is
        // the assertion that makes the ratio above mean something. The rule's
        // last clause is "a card of cost 2 or more WITH NO NUMBER costs 1
        // less", so a row of cost 2 or more ALWAYS has an answer -- either a
        // number to bump or that clause. Every row without an upgrade must
        // therefore be a 0- or 1-cost row with nothing printed to move.
        var expensiveAndUnupgraded = rows
            .Where(t => !HasUpgradeBody(t) && CanonicalCost(t) >= 2)
            .Select(t => t.Name)
            .ToList();
        Assert.Empty(expensiveAndUnupgraded);
    }

    [Fact]
    public void An_upgraded_row_is_not_a_copy_of_the_base_row()
    {
        // `EB-277` verbatim: *Coral Bulwark+* and *Water's Edge (proto)+*
        // printed and dealt the base numbers, so the Light Door's "Upgrade 2
        // random cards" had no visible effect. Through the game's OWN
        // `UpgradeInternal`, so this is the smith's result and not the
        // emitter's intention.
        // Water's Edge, the row `EB-277` was found on, is GONE (R242): her
        // basics are the base game's Strike and Defend, whose +3 the base game
        // owns. Coral Bulwark carries the Block half of the same pin.
        AssertUpgradeMoves<ProtoKkCoralBulwark>("Block", 6m, 9m);
        // Ka-pow! carries the `set_off`-hit clause again: round 5 pick 1 moved
        // Retain onto the BASE card, which handed its upgrade back to the
        // default rule. Fwoosh! prints the same clause beside it: aimed and
        // 6 since R243's card-audit ruling ("default looks good").
        AssertUpgradeMoves<ProtoKoKapow>("Damage", 4m, 7m);
        AssertUpgradeMoves<ProtoKoFwoosh>("Damage", 6m, 9m);
        AssertUpgradeMoves<ProtoKoPop>("BombSize", 5m, 7m);
        // Chain Fuse grows by 6 since the 2026-09-02 balance pass. Its
        // upgrade is the row's OWN `grow: +3` (the Klee card audit of the
        // same day, `review/active/klee-card-audit-2026-09-02.md`): a grow is
        // damage to be and takes a Strike's +3, where the rule's default +1
        // was an upgrade nobody could see.
        AssertUpgradeMoves<ProtoKoChainFuse>("Grow", 6m, 9m);
        // The same audit's other three levers, one pin each. A power whose
        // printed number IS 1 moves that number (the rule read it as a
        // switch and appended a draw); an `energy:` delta moves the Energy
        // var the authored face now prints; Sorry, Jean...'s upgrade is a
        // keyword, not a number.
        AssertUpgradeMoves<ProtoKoExplosivesWorkshop>("PowerAmount", 1m, 2m);
        AssertUpgradeMoves<ProtoKoSugarRush>("Energy", 2m, 3m);
        var sorryJean = new ProtoKoSorryJean();
        Assert.False(sorryJean.Keywords.Contains(CardKeyword.Retain));
        Upgrade(sorryJean);
        Assert.True(sorryJean.Keywords.Contains(CardKeyword.Retain));
        // The Mend clause, on draft 6's carrier. `Tide` left this pin with the
        // verb it read: the rule's key list is written over OPS, so retiring
        // `gain_tide` retired the delta and nothing here had to be re-decided.
        // Mend 3 since 2026-09-02 ([USER]: "15 is a lot. Maybe 3 (6 on
        // Plan)"), and the +2 rides the new base like every other delta in
        // this pass.
        AssertUpgradeMoves<ProtoKkTheMoonAShip>("Mend", 3m, 5m);
        // The multi-hit clause: +1 PER HIT rather than +3 once.
        AssertUpgradeMoves<ProtoKoRapidFire>("Damage", 3m, 4m);
    }

    [Fact]
    public void A_spark_price_is_not_what_the_upgrade_moves()
    {
        // "Spark costs unchanged" is the rule's own last words, and it is the
        // one number a campfire must not touch: the Spark price IS the card.
        var card = new ProtoKoDigIn();
        var before = ((ISparkPricedCard)card).PrintedSparkPrice;
        Upgrade(card);
        Assert.Equal(before, ((ISparkPricedCard)card).PrintedSparkPrice);
        // Block 8 -> 11 is what the campfire DID move, so this is not passing
        // by nothing having happened.
        Assert.Equal(11m, card.DynamicVars["Block"].BaseValue);
    }

    private static int CanonicalCost(Type card)
    {
        var instance = Activator.CreateInstance(card)!;
        return (int)typeof(CardModel)
            .GetProperty("CanonicalEnergyCost", HeadlessGame.All)!
            .GetValue(instance)!;
    }

    private static bool HasUpgradeBody(Type card)
    {
        var body = card.GetMethod("OnUpgrade", HeadlessGame.All)!
            .GetMethodBody()?.GetILAsByteArray();
        // An empty `OnUpgrade` compiles to `ret` alone (or `nop; ret` in a
        // debug build), so anything longer is a delta being applied.
        return body != null && body.Length > 2;
    }

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
    }

    private static void AssertUpgradeMoves<T>(string var, decimal from,
                                              decimal to)
        where T : CardModel, new()
    {
        var baseCard = new T();
        Assert.Equal(from, baseCard.DynamicVars[var].BaseValue);
        var upgraded = new T();
        Upgrade(upgraded);
        Assert.Equal(to, upgraded.DynamicVars[var].BaseValue);
    }
}
