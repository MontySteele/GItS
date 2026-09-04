using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE COMPANION STAND-IN HAND-OFF (<c>EB-320</c>) -- the pin the seam shipped
/// without, and the defect that cost.
///
/// WHAT HAPPENED. A stand-in row spells <c>personal_pool: [klee]</c>, a
/// one-member list, and the C# emitter rendered that list's Python repr:
/// <c>PersonalPool =&gt; "['klee']"</c>. <see cref="CompanionStandIns.HandOffTo"/>
/// compares that string to the character id <c>CompanionPool.CharacterId</c>
/// answers, which is <c>"klee"</c>, so the swap never fired and the blind Klee
/// seat of 2026-09-02 was handed the Universal at both mouths. The sim
/// normalises the same key on the way in and was right the whole time, so
/// nothing in the sim twin could see it. The emitter is fixed
/// (<c>tools/gen_klee_cards.py</c>, PR #317); THIS file is the reason it
/// shipped -- the rule had no C# pin at all, because
/// <see cref="CompanionStandIns.HandOff"/> takes a <c>Player</c> and the pair
/// table resolves through <c>ModelDb</c>, and both are outside the headless
/// boundary (README).
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL. The DECISION is real: the seam's
/// second method takes the pair table as a parameter, so this file hands it
/// pairs it constructed itself -- shipped generated rows, not stand-in
/// doubles -- and the swap, the refusal for another character and the refusal
/// with the arm off are direct assertions against the shipped comparison. The
/// character id is real too: <c>Seat.Klee()</c> is a real <c>Player</c> and
/// <c>CompanionPool.CharacterId</c> is a pure switch on its Character, so BOTH
/// SIDES of the comparison that failed are computed here rather than assumed.
/// STRUCTURAL are the two things a <c>ModelDb</c>-free process cannot run: that
/// the game's own mouth routes through the pinned method, and that the shipped
/// pair table names the same classes this file pairs up.
///
/// Sim twin: <c>tier0/tests/test_companion_standins.py</c>, which pins the two
/// tables against each other by id.
/// </summary>
[Collection(CompanionOverhaulArm.Name)]
public class CompanionStandInHandOffTests : IDisposable
{
    private readonly bool _armWas = CompanionOverhaul.Enabled;

    public void Dispose() => CompanionOverhaul.Enabled = _armWas;

    /// <summary>
    /// The pairs, Universal -> stand-in, CONSTRUCTED HERE. These are the
    /// shipped generated classes, so the <c>PersonalPool</c> under test is the
    /// emitted one and not a value this file made up -- which is the whole
    /// point: a hand-written double would have carried <c>"klee"</c> and passed
    /// on the day the emitter was wrong.
    /// </summary>
    private static IReadOnlyList<(CardModel Universal, CardModel StandIn)> Table() =>
        new (CardModel, CardModel)[]
        {
            (new ProtoMcDionaIcyPaws(), new ProtoMcDionaShakenNotPurred()),
            (new ProtoMcNoelleBreastplate(), new ProtoMcNoelleIGotYourBack()),
            (new ProtoMcKaeyaFrostgnaw(), new ProtoMcKaeyaColdBloodedStrike()),
            (new ProtoMcJeanDandelionBreeze(), new ProtoMcJeanLionsFang()),
            // R252's fifth caretaker, named here for the reason the four above
            // are: every pin in this file is a sweep over this table, so a new
            // stand-in joins the seam's whole coverage by being listed once.
            (new ProtoMcBarbaraShowBegin(), new ProtoMcBarbaraFrontRowSeat()),
        };

    // ---- THE DECISION, real ---------------------------------------------

    [Fact]
    public void A_klee_seat_is_handed_the_stand_in()
    {
        // THE PIN THE SEAT'S ROUND WOULD HAVE FAILED. Red before PR #317's
        // emitter fix, green after, and it does not need the game to say so.
        CompanionOverhaul.Enabled = true;
        var table = Table();
        foreach (var (universal, standIn) in table)
        {
            Assert.Same(standIn,
                        CompanionStandIns.HandOffTo(universal, "klee", table));
        }
    }

    [Theory]
    [InlineData("kokomi")]
    [InlineData("furina")]
    public void Every_other_character_is_handed_the_universal(string characterId)
    {
        // The swap is keyed on the stand-in's own PersonalPool, so a table at
        // which another of our characters is sitting hands off nothing.
        CompanionOverhaul.Enabled = true;
        var table = Table();
        foreach (var (universal, _) in table)
        {
            Assert.Same(universal,
                        CompanionStandIns.HandOffTo(universal, characterId, table));
        }
    }

    [Fact]
    public void A_base_game_character_is_handed_the_universal()
    {
        // `CompanionPool.CharacterId` answers null for every character that is
        // not ours, and the mod must not change anything for one of those.
        CompanionOverhaul.Enabled = true;
        var table = Table();
        foreach (var (universal, _) in table)
        {
            Assert.Same(universal,
                        CompanionStandIns.HandOffTo(universal, null, table));
        }
    }

    [Fact]
    public void With_the_arm_off_even_klee_is_handed_the_universal()
    {
        // The acceptance condition: a flag-off build is byte-identical at this
        // seam, and every stand-in is unreachable rather than merely
        // unlikely.
        CompanionOverhaul.Enabled = false;
        var table = Table();
        foreach (var (universal, _) in table)
        {
            Assert.Same(universal,
                        CompanionStandIns.HandOffTo(universal, "klee", table));
        }
    }

    [Fact]
    public void A_card_the_table_does_not_name_is_handed_back_unchanged()
    {
        // The hand-off is called on EVERY companion the two mouths pick, so
        // the common case is a card no pair mentions. It must fall through --
        // and it must not fall through to some other pair's stand-in.
        CompanionOverhaul.Enabled = true;
        var picked = new ProtoMcKaeyaGlacialWaltz();
        Assert.Same(picked, CompanionStandIns.HandOffTo(picked, "klee", Table()));
    }

    // ---- THE STRING THAT WAS WRONG, real on both sides ------------------

    [Fact]
    public void The_id_a_klee_seat_answers_is_the_string_the_stand_ins_print()
    {
        // BOTH SIDES OF THE FAILED COMPARISON, computed. The left is a real
        // Player's Character run through the shipped switch; the right is the
        // emitted property on each shipped stand-in class. The defect was
        // exactly this equality, and nothing else in either engine asserted it.
        var characterId = CompanionPool.CharacterId(Seat.Klee().Player);
        Assert.Equal("klee", characterId);
        foreach (var (_, standIn) in Table())
        {
            Assert.Equal(characterId, ((ICompanionCard)standIn).PersonalPool);
        }
    }

    [Fact]
    public void No_prototype_companion_spells_its_personal_pool_as_a_list()
    {
        // THE REGRESSION THE SEAT CAUGHT, swept over the whole prototype
        // surface rather than over the four rows that happened to break: the
        // sheet key takes a list, the emitter renders one string, and any row
        // whose value arrives with a bracket or a quote in it is a card no
        // character can ever be handed. Class-wide, so the next `[name]` row
        // fails here instead of in a blind round.
        var ids = new[] { Seat.Klee(), Seat.Kokomi(), Seat.Furina() }
            .Select(seat => CompanionPool.CharacterId(seat.Player))
            .ToList();

        var personals = typeof(ProtoMcDionaShakenNotPurred).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && !t.IsAbstract
                        && typeof(ICompanionCard).IsAssignableFrom(t))
            .Select(t => (Type: t,
                          Pool: ((ICompanionCard)Activator.CreateInstance(t)!)
                              .PersonalPool))
            .Where(row => row.Pool != null)
            .ToList();

        // Non-vacuous: the four stand-ins are personal-pool rows by
        // construction, so an empty sweep means the filter stopped matching.
        Assert.True(personals.Count >= 4,
                    $"the sweep found {personals.Count} personal-pool rows");
        foreach (var (type, pool) in personals)
        {
            Assert.DoesNotContain("[", pool!, StringComparison.Ordinal);
            Assert.DoesNotContain("]", pool!, StringComparison.Ordinal);
            Assert.DoesNotContain("'", pool!, StringComparison.Ordinal);
            // And the positive half: a value no seat answers is unreachable
            // just as silently as a bracketed one.
            Assert.True(ids.Contains(pool),
                        $"{type.Name} is personal to \"{pool}\", which is not a "
                      + "character id CompanionPool.CharacterId ever returns");
        }
    }

    // ---- THE MOUTH AND THE TABLE, structural ----------------------------

    [Fact]
    public void The_mouth_the_game_calls_decides_through_the_pinned_method()
    {
        // STRUCTURAL, and it is what makes everything above worth anything:
        // `HandOff` is the method the reward slot and both shop slots call, it
        // takes a Player, and a Player is where the character id comes from --
        // so the pins reach the shipped decision only while this one call
        // stands. Reimplementing the comparison inside `HandOff` is what would
        // break the chain, so that is what this refuses.
        var handOff = typeof(CompanionStandIns)
            .GetMethod("HandOff", HeadlessGame.All)
            ?? throw new InvalidOperationException(
                "CompanionStandIns.HandOff is gone -- the seam moved.");
        var calls = Il.Calls(handOff);
        Assert.Contains("CompanionStandIns.HandOffTo", calls);
        Assert.Contains("CompanionPool.CharacterId", calls);
        Assert.Contains("CompanionOverhaul.get_Enabled", calls);
    }

    [Fact]
    public void The_shipped_pair_table_names_the_classes_pinned_here()
    {
        // STRUCTURAL: `Pairs` resolves every row through `ModelDb.Card<T>()`,
        // which throws until the game's boot builds the models, so the table
        // cannot be CALLED here -- but every type argument is in its IL.
        // Without this, the pairs above could drift into a fiction of
        // this file's own while the mod paired something else.
        var pairs = typeof(CompanionStandIns).GetMethod("Pairs", HeadlessGame.All)
            ?? throw new InvalidOperationException(
                "CompanionStandIns.Pairs is gone -- the table moved.");
        var sequence = Il.CallSequence(pairs);
        foreach (var (universal, standIn) in Table())
        {
            foreach (var card in new[] { universal, standIn })
            {
                var name = card.GetType().Name;
                Assert.Contains(sequence, call =>
                    call.Contains(name, StringComparison.Ordinal));
            }
        }
    }
}
