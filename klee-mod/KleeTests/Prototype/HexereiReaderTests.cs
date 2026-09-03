using System.Linq;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE'S THREE HEXEREI READERS (R244, the ruled packet
/// `review/ruled/klee-hexerei-readers-2026-09-02.md`).
///
/// Hexerei is one word on a companion row with no effect of its own -- the
/// approved Mondstadt workshop's sec.1 pick 2 -- and the payoff was always
/// meant to live in Klee's own pool. Until this row it did not: eighteen faces
/// printed the word and exactly one card read it (Nicole's stand-in). These
/// three are the readers:
///
///   * <b>Coven Errand</b> (Common Skill 1) -- "Place a Bomb 5. If you played a
///     Hexerei card this turn, place it on ALL enemies instead."
///   * <b>Witches' Circle</b> (Uncommon Power 1) -- "Whenever you play a
///     Hexerei card, place a Bomb 3 on a random enemy." DEAD ALONE by the
///     packet's own pick 2, taken at its default; that is the card.
///   * <b>Alice's Introduction Magic</b> (Rare Skill 1) -- "All cards in your
///     hand count as Hexerei cards this turn." Upgrade: Retain.
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
    public void The_hexerei_count_is_per_turn()
    {
        // REAL arithmetic: Coven Errand's whole read is this counter, and it
        // rolls on the same round stamp rule 7's two counters take.
        var ledger = NewLedger();
        ledger.RollTo(1);
        Assert.Equal(0, (int)ledger.HexereiPlayedThisTurn);

        ledger.NoteHexereiPlayed();
        ledger.NoteHexereiPlayed();
        Assert.Equal(2, (int)ledger.HexereiPlayedThisTurn);

        ledger.RollTo(2);
        Assert.Equal(0, (int)ledger.HexereiPlayedThisTurn);
    }

    [Fact]
    public void The_count_is_written_at_one_site_and_it_asks_the_mark()
    {
        // STRUCTURAL, and labelled. The count has to be answerable whether or
        // not any power is on the board, so it cannot ride one -- it lands on
        // the arm's ONE standing card-play listener. What COUNTS is
        // `CompanionHexerei.IsHexerei`'s answer and nobody else's, which is
        // what lets Alice widen the family without either reader learning
        // about her.
        var calls = Il.Calls(Il.Method("CompanionHexerei", "NoteCardPlayed"));
        Assert.Contains("CompanionHexerei.IsHexerei", calls);
        Assert.Contains("KleeOverhaulLedger.NoteHexereiPlayed", calls);
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
        Assert.Contains("KleeOverhaulLedger.get_HexereiPlayedThisTurn", calls);
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
    public void The_circle_pays_only_for_a_hexerei_card_and_only_places()
    {
        // STRUCTURAL, and labelled, for `Place`'s reason above. THE DEAD-ALONE
        // HALF IS THE `IsHexerei` GATE: a deck with no witch in it never gets
        // past it, which is the packet's pick 2 taken at its default and the
        // card rather than a defect. The co-op clause is the one every other
        // reader in the arm carries (R205): another Klee's plays are not hers.
        var hook = typeof(WitchesCirclePower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        var calls = Il.Calls(hook);
        Assert.Contains("CompanionHexerei.IsHexerei", calls);
        Assert.Contains("KleeOverhaul.get_Enabled", calls);
        Assert.Contains("ProtoBombPower.Place", calls);
        // It places a plain Bomb and never sets one off.
        Assert.DoesNotContain("ProtoBombPower.TakeAll", calls);
        Assert.DoesNotContain(calls,
                              c => c.StartsWith("ProtoBombPower.SetOff"));
    }

    // ---- Alice's Introduction Magic --------------------------------------

    [Fact]
    public void The_spell_is_itself_hexerei_and_upgrades_to_retain()
    {
        // The ruling's second derived reading ("it counts as Hexerei itself,
        // so it does not need a second witch to start a circle") is the row's
        // own `hexerei: true`, which the codegen turns into the interface --
        // and the upgrade is the one the packet names.
        var card = new ProtoKoAlicesIntroductionMagic();
        Assert.IsAssignableFrom<IHexereiCard>(card);
        Assert.DoesNotContain(CardKeyword.Retain, card.Keywords);

        var upgraded = Upgraded<ProtoKoAlicesIntroductionMagic>();
        Assert.IsAssignableFrom<IHexereiCard>(upgraded);
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
    public void Every_reader_asks_the_marks_rather_than_the_interface()
    {
        // THE POINT OF HAVING ONE READER. Alice widens the family for a turn,
        // so a payoff that tested `is IHexereiCard` itself would be a second
        // definition of "Hexerei" -- and it would be the one that disagreed.
        // Nicole's Ladder is here because R244 MOVED it: it tested the type
        // before this row.
        foreach (var hook in new[]
                 {
                     typeof(LadderOfAscentPower)
                         .GetMethod("AfterCardPlayed", HeadlessGame.All)!,
                     typeof(WitchesCirclePower)
                         .GetMethod("AfterCardPlayed", HeadlessGame.All)!,
                 })
        {
            Assert.Contains("CompanionHexerei.IsHexerei", Il.Calls(hook));
        }

        // And the reader itself consults BOTH halves: the printed mark
        // (`is IHexereiCard`, an isinst rather than a call) and the this-turn
        // window, which it reaches through the owner's power list.
        var reader = Il.CallSequence(
            Il.Method("CompanionHexerei", "IsHexerei"));
        Assert.Contains(reader, c => c.Contains("IntroductionMagicPower"));
        Assert.Contains("Creature.get_Powers", reader);
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
