using System.Collections.Generic;
using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE'S THREE COMPANION READERS (R244, the ruled packet
/// `review/ruled/klee-hexerei-readers-2026-09-02.md`; R276 pick 2 made them
/// read any Companion card instead of the retired Hexerei mark).
///
///   * <b>Coven Errand</b> (Common Skill 1) -- "Place a Bomb 5. If you played a
///     Companion card this turn, place it on ALL enemies instead."
///   * <b>Witches' Circle</b> (Uncommon Power 1) -- "Whenever you play a
///     Companion card, place a Bomb 3 on a random enemy."
///   * <b>Alice's Introduction Magic</b> (Rare Skill 1) -- "All cards in your
///     hand count as Companion cards this turn." Upgrade: Retain.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, said once, on
/// <see cref="KleeOverhaulRuleTests"/>'s own terms. A card PLAY,
/// <c>PowerCmd</c> and <c>ElementalHit.Deal</c> are all outside the headless
/// boundary (README), so the placements themselves are labelled structural pins
/// read off the compiled method. Everything that is a DECISION -- the ledger's
/// arithmetic, the printed numbers, the campfire, and which card instances the
/// window covers -- is a real call on real objects. The sim twin plays all
/// three against a real board: `tier0/tests/test_klee_overhaul_rules.py`, its
/// R244 block.
///
/// NO NUMBER HERE IS QUOTABLE (R215 B). 5, 3, 7 and 5 are the packet's first
/// honest guess against her live pool, with no measurement attached.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class HexereiReaderTests
{
    // ---- helpers ---------------------------------------------------------

    /// <summary>Upgrade a card the way the campfire does -- the same helper
    /// shape <c>PrototypeUpgradeChannelTests</c> and
    /// <c>KleeOverhaulRoundThreeTests</c> use, and for their reason:
    /// <c>UpgradeInternal</c> raises the level, calls the card's own
    /// <c>OnUpgrade</c> and finalizes each DynamicVar's preview.</summary>
    private static T Upgraded<T>() where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
        return card;
    }

    private static string Face(CustomCardModel card) =>
        card.Localization!.Single(row => row.Item1 == "description").Item2;

    /// <summary>A ledger with no combat behind it. <c>For</c> needs a live
    /// CombatState to key on, so the pins construct one directly -- the class
    /// is plain state and its counters are pure. Same helper, same reason, as
    /// <c>KleeOverhaulRuleTests</c>'s.</summary>
    private static dynamic NewLedger()
    {
        var type = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Powers.KleeOverhaulLedger")!;
        return System.Activator.CreateInstance(type, nonPublic: true)!;
    }

    /// <summary><c>IntroductionMagicPower.Mark</c> / <c>Marks</c> are internal
    /// and this mod carries no <c>InternalsVisibleTo</c> -- the standing call,
    /// recorded in <c>ProtoBombPower</c> and three files beside it -- so the
    /// window is exercised through reflection rather than by widening the
    /// surface for a test.</summary>
    private static void Mark(IntroductionMagicPower power, CardModel card) =>
        typeof(IntroductionMagicPower)
            .GetMethod("Mark", HeadlessGame.All)!
            .Invoke(power, new object?[] { card });

    private static bool Marks(IntroductionMagicPower power, CardModel card) =>
        (bool)typeof(IntroductionMagicPower)
            .GetMethod("Marks", HeadlessGame.All)!
            .Invoke(power, new object?[] { card })!;

    // ---- the ledger's third counter --------------------------------------

    [Fact]
    public void The_companion_count_is_per_turn()
    {
        // REAL arithmetic: Coven Errand's whole read is this counter, and it
        // rolls on the same round stamp rule 7's two counters take.
        var ledger = NewLedger();
        ledger.RollTo(1);
        Assert.Equal(0, (int)ledger.CompanionPlayedThisTurn);

        ledger.NoteCompanionPlayed();
        ledger.NoteCompanionPlayed();
        Assert.Equal(2, (int)ledger.CompanionPlayedThisTurn);

        ledger.RollTo(2);
        Assert.Equal(0, (int)ledger.CompanionPlayedThisTurn);
    }

    [Fact]
    public void The_count_is_written_at_one_site_and_it_asks_the_one_question()
    {
        // STRUCTURAL, and labelled. The count has to be answerable whether or
        // not any power is on the board, so it cannot ride one -- it lands on
        // the arm's ONE standing card-play listener. What COUNTS is
        // `CompanionHexerei.CountsAsCompanion`'s answer and nobody else's,
        // which is what lets Alice widen the set without either reader
        // learning about her.
        var calls = Il.Calls(Il.Method("CompanionHexerei", "NoteCardPlayed"));
        Assert.Contains("CompanionHexerei.CountsAsCompanion", calls);
        Assert.Contains("KleeOverhaulLedger.NoteCompanionPlayed", calls);
        Assert.Contains("KleeOverhaul.get_Enabled", calls);

        var hook = typeof(KleeOverhaulSweepHooks)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        Assert.Contains("CompanionHexerei.NoteCardPlayed", Il.Calls(hook));
    }

    // ---- Coven Errand ----------------------------------------------------

    [Fact]
    public void The_errand_prints_one_bomb_and_the_campfire_moves_it()
    {
        // ONE printed number for both arms, which is why the widening is a
        // field on the op rather than two `plant_bomb`s in a conditional: only
        // a top-level effect owns a var, so the `+` card would have printed 7
        // in one clause and placed 5 in the other (`EB-288`'s defect class).
        Assert.Equal(
            5m, new ProtoKoCovenErrand().DynamicVars["BombSize"].BaseValue);
        Assert.Equal(
            7m,
            Upgraded<ProtoKoCovenErrand>().DynamicVars["BombSize"].BaseValue);
        Assert.Contains("{BombSize:diff()}", Face(new ProtoKoCovenErrand()));
    }

    [Fact]
    public void The_errand_reads_the_ledger_and_places_one_bomb_either_way()
    {
        // STRUCTURAL, and labelled: `ProtoBombPower.Place` applies a power, so
        // the placement itself is outside the headless boundary. What is
        // checkable is the SHAPE the ruling asks for -- the ledger decides,
        // both arms exist, and both read the same var.
        var calls = Il.Calls(Il.Method("ProtoKoCovenErrand", "OnPlay"));
        Assert.Contains("KleeOverhaulLedger.get_CompanionPlayedThisTurn", calls);
        Assert.Contains("ProtoBombPower.PlaceOnAll", calls);
        Assert.Contains("ProtoBombPower.Place", calls);
        Assert.Contains("DynamicVarSet.get_Item", calls);
        // It PLACES; it does not detonate (rule 7).
        Assert.DoesNotContain("ProtoBombPower.SetOffAimed", calls);
        Assert.DoesNotContain("ProtoBombPower.SetOffAll", calls);
    }

    // ---- Witches' Circle -------------------------------------------------

    [Fact]
    public void The_circle_prints_its_bomb_and_the_campfire_moves_it()
    {
        // The stack IS the Bomb size, Chained Reactions' grammar one trigger
        // over, so a second copy is a second Bomb per witch.
        Assert.Equal(
            3m,
            new ProtoKoWitchesCircle().DynamicVars["PowerAmount"].BaseValue);
        Assert.Equal(
            5m,
            Upgraded<ProtoKoWitchesCircle>()
                .DynamicVars["PowerAmount"].BaseValue);
        Assert.Contains("{PowerAmount:diff()}",
                        Face(new ProtoKoWitchesCircle()));
    }

    [Fact]
    public void The_circle_pays_only_for_a_companion_card_and_only_places()
    {
        // STRUCTURAL, and labelled, for `Place`'s reason above. The gate is
        // `CountsAsCompanion`. The co-op clause is the one every other reader
        // in the arm carries (R205): another Klee's plays are not hers.
        var hook = typeof(WitchesCirclePower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        var calls = Il.Calls(hook);
        Assert.Contains("CompanionHexerei.CountsAsCompanion", calls);
        Assert.Contains("KleeOverhaul.get_Enabled", calls);
        Assert.Contains("ProtoBombPower.Place", calls);
        // It places a plain Bomb and never sets one off.
        Assert.DoesNotContain("ProtoBombPower.TakeAll", calls);
        Assert.DoesNotContain(calls,
                              c => c.StartsWith("ProtoBombPower.SetOff"));
    }

    // ---- Alice's Introduction Magic --------------------------------------

    [Fact]
    public void The_spell_is_not_a_companion_and_upgrades_to_retain()
    {
        // R276: the spell is Klee's own card, not a Companion, and it marks
        // only the hand it was played from -- so it does not count itself any
        // more (the `hexerei: true` key that made it was retired). The
        // upgrade is the one the packet names.
        var card = new ProtoKoAlicesIntroductionMagic();
        Assert.IsNotAssignableFrom<ICompanionCard>(card);
        Assert.DoesNotContain(CardKeyword.Retain, card.Keywords);
        Assert.Contains("[gold]Companion[/gold]", Face(card));

        var upgraded = Upgraded<ProtoKoAlicesIntroductionMagic>();
        Assert.Contains(CardKeyword.Retain, upgraded.Keywords);
    }

    [Fact]
    public void The_window_covers_the_instances_it_saw_and_not_a_later_draw()
    {
        // REAL: the ruling's FIRST derived reading, and the reason the upgrade
        // is Retain -- "the window is this turn, over the cards in hand when it
        // is played (a card drawn later this turn is not counted)". A set of
        // INSTANCES is what makes that true of two copies of one card, which a
        // set of ids could not say.
        var power = new IntroductionMagicPower();
        var held = new ProtoKoPop();
        var alsoHeld = new ProtoKoPop();          // a SECOND copy, same id
        var drawnLater = new ProtoKoPop();

        Mark(power, held);
        Assert.True(Marks(power, held));
        Assert.False(Marks(power, alsoHeld));
        Assert.False(Marks(power, drawnLater));
    }

    [Fact]
    public void The_spell_marks_the_hand_and_the_window_shuts_at_turn_end()
    {
        // STRUCTURAL, and labelled: reading the hand pile and applying a power
        // are both outside the headless boundary. The shape is the rule --
        // OnPlay asks `CompanionHexerei` (the mark's home) rather than doing
        // its own marking, `MarkHand` reads the HAND, and the window is removed
        // at the boundary the arm's other this-turn promises close at.
        Assert.Contains(
            "CompanionHexerei.MarkHand",
            Il.Calls(Il.Method("ProtoKoAlicesIntroductionMagic", "OnPlay")));

        var mark = Il.Calls(Il.Method("CompanionHexerei", "MarkHand"));
        Assert.Contains("CardPile.Get", mark);
        Assert.Contains(mark, c => c.StartsWith("PowerCmd.Apply"));

        var close = typeof(IntroductionMagicPower)
            .GetMethod("AfterSideTurnEnd", HeadlessGame.All)!;
        Assert.Contains("PowerCmd.Remove", Il.Calls(close));
    }

    [Fact]
    public void Every_reader_asks_the_one_question_rather_than_the_interface()
    {
        // THE POINT OF HAVING ONE READER. Alice widens the set for a turn, so
        // a payoff that tested `is ICompanionCard` itself would be a second
        // definition of "a Companion card" -- and it would be the one that
        // disagreed.
        foreach (var hook in new[]
                 {
                     typeof(LadderOfAscentPower)
                         .GetMethod("AfterCardPlayed", HeadlessGame.All)!,
                     typeof(WitchesCirclePower)
                         .GetMethod("AfterCardPlayed", HeadlessGame.All)!,
                 })
        {
            Assert.Contains("CompanionHexerei.CountsAsCompanion",
                            Il.Calls(hook));
        }

        // And the reader itself consults BOTH halves: the card's own kind
        // (`is ICompanionCard`, an isinst rather than a call) and the this-turn
        // window, which it reaches through the owner's power list.
        var reader = Il.CallSequence(
            Il.Method("CompanionHexerei", "CountsAsCompanion"));
        Assert.Contains(reader, c => c.Contains("IntroductionMagicPower"));
        Assert.Contains("Creature.get_Powers", reader);
    }

    // ---- `EB-663`, R276: the Spark asks the readers' own question ---------

    /// <summary>Put an already-constructed power on a seat's creature. The
    /// harness's own <c>WithPower</c> allocates uninitialised -- correct for a
    /// <c>CustomPowerModel</c>, wrong here, because this power's window is a
    /// readonly <c>HashSet</c> its constructor builds.</summary>
    /// <summary>Hand a card to a seat. <c>CardModel.Owner</c>'s GETTER asserts
    /// mutability -- the canonical-model guard the game's <c>ToMutable</c>
    /// lifts -- so the flag goes up first, exactly as <c>Bombs</c> does it.
    /// </summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Force(card, "Owner", seat.Player);
        return card;
    }

    private static IntroductionMagicPower Window(Seat seat)
    {
        var power = new IntroductionMagicPower();
        var powers = (List<PowerModel>)typeof(Creature)
            .GetField("_powers", HeadlessGame.All)!
            .GetValue(seat.Creature)!;
        powers.Add(power);
        return power;
    }

    private static bool Counts(CardModel card) =>
        (bool)typeof(KleeCompanionSpark).Assembly
            .GetType("KleeMod.Powers.CompanionHexerei")!
            .GetMethod("CountsAsCompanion", HeadlessGame.All)!
            .Invoke(null, new object?[] { card })!;

    [Fact]
    public void Under_the_arm_no_companion_play_pays_a_spark_and_the_readers_still_count_it()
    {
        // 2026-09-23, [USER]: "It sounds like we've massively increased the
        // Spark generation and it's worth decreasing now to go back to the
        // old levels and then see if play is Spark-constrained." R276 pick 2
        // had paid Klee for any Companion play under the arm, Alice-marked
        // plays included; now none pays, while the readers' own question
        // (`CountsAsCompanion`, which Coven Errand, Witches' Circle and the
        // rest ask) still answers yes for both.
        //
        // REAL: `PaysKleesSpark` and `CountsAsCompanion` on real cards against
        // a real Klee seat. The MINT is `Settle`, which needs a
        // PlayerChoiceContext and is outside the boundary; what DECIDES is the
        // predicate. The sim twin plays it on a real board:
        // `test_a_companion_play_feeds_the_readers_and_mints_no_spark`.
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = true;
            var seat = Seat.Klee();
            var window = Window(seat);

            var companion = Held<ProtoMcDionaShakenNotPurred>(seat);
            Assert.IsAssignableFrom<ICompanionCard>(companion);
            Assert.True(Counts(companion));
            Assert.False(KleeCompanionSpark.PaysKleesSpark(companion));

            // Even one of her own Personal Companions, which pays off the arm.
            Assert.Equal("klee", ((ICompanionCard)companion).PersonalPool);
            Assert.False(KleeCompanionSpark.PaysKleesSpark(companion));

            var marked = Held<ProtoKoPop>(seat);
            Mark(window, marked);
            Assert.True(Counts(marked));
            Assert.False(KleeCompanionSpark.PaysKleesSpark(marked));

            // And the rider that promised the income is not attached.
            var inherited = System.Array.Empty<IHoverTip>();
            Assert.Same(inherited,
                        ArmKeywordTips.ForCovenSpark(inherited, companion));
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void Off_the_arm_the_shipped_personal_gate_still_pays()
    {
        // R213 B: the shipped Personal-Companion gate does not move for a
        // prototype arm. Off the arm one of Klee's own Personals pays; a
        // marked card does not, and nobody but Klee is paid (`EB-434`).
        var was = KleeOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;
            var seat = Seat.Klee();
            var window = Window(seat);
            var companion = Held<ProtoMcDionaShakenNotPurred>(seat);
            Assert.True(KleeCompanionSpark.PaysKleesSpark(companion));

            var marked = Held<ProtoKoPop>(seat);
            Mark(window, marked);
            Assert.False(KleeCompanionSpark.PaysKleesSpark(marked));

            var kokomi = Seat.Kokomi();
            Assert.False(KleeCompanionSpark.PaysKleesSpark(
                Held<ProtoMcDionaShakenNotPurred>(kokomi)));
        }
        finally
        {
            KleeOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void Under_the_arm_the_spark_gate_returns_before_any_companion_test()
    {
        // Structural: the arm branch asks nothing of the card; the
        // Personal-pool test is what remains below it for the off-arm world.
        var body = Il.CallSequence(
            Il.Method("KleeCompanionSpark", "PaysKleesSpark")).ToList();
        Assert.Contains(body, c => c.Contains("KleeOverhaul"));
        Assert.DoesNotContain(body, c => c.Contains("CompanionHexerei"));
    }

    // ---- the pool --------------------------------------------------------

    [Fact]
    public void The_three_readers_are_in_the_arms_offerable_pool()
    {
        // The C# roster is LISTED BY TYPE, so the compiler holds the
        // correspondence with `C.KLEE_OVERHAUL_POOL_IDS`; what a pin adds is
        // that the three types the ruling names are actually there and are not
        // in the starter (a card in both would quietly double as a reward).
        var slice = Il.CallSequence(Il.Method("KleeOverhaulRoster", "Slice"));
        foreach (var name in new[]
                 {
                     "ProtoKoCovenErrand", "ProtoKoWitchesCircle",
                     "ProtoKoAlicesIntroductionMagic",
                 })
        {
            Assert.Contains(slice, c => c.Contains(name));
        }

        var starter = Il.CallSequence(
            Il.Method("KleeOverhaulRoster", "StartingDeck"));
        Assert.DoesNotContain(starter, c => c.Contains("ProtoKoCovenErrand"));
    }
}
