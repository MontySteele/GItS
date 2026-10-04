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

    public void Dispose() { }

    // THE KLEE-ONLY COMPANIONS (2026-10-03,
    // review/active/mondstadt-companions-2026-10-03.md sec.4) left the seam
    // with NO pairs: four stand-ins cut, three to the shared pool, two to
    // Klee's own draftable pool. The decision pins that swept the pair table
    // went with it; what stays is the emitter sweep below (every personal
    // pool row still prints a bare character id) and the two structural pins.

    [Fact]
    public void An_empty_table_hands_every_card_back_unchanged()
    {
        var picked = new ProtoMcKaeyaGlacialWaltz();
        var none = Array.Empty<(CardModel, CardModel)>();
        Assert.Same(picked, CompanionStandIns.HandOffTo(picked, "klee", none));
        Assert.Same(picked, CompanionStandIns.HandOffTo(picked, null, none));
    }

    // ---- THE STRING THAT WAS WRONG, real on both sides ------------------

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
        // VARKA's four Knights are personal to him.
        ids.Add(CompanionPool.CharacterId(Seat.Varka().Player));

        var personals = typeof(ProtoMcDionaIcyPaws).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && !t.IsAbstract
                        && typeof(ICompanionCard).IsAssignableFrom(t))
            .Select(t => (Type: t,
                          Pool: ((ICompanionCard)Activator.CreateInstance(t)!)
                              .PersonalPool))
            .Where(row => row.Pool != null)
            .ToList();

        // Non-vacuous: Varka's Knights and Kokomi's Gorou are personal-pool
        // rows by construction, so an empty sweep means the filter stopped
        // matching.
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
    }

    [Fact]
    public void The_shipped_pair_table_is_empty()
    {
        // STRUCTURAL: `Pairs` names no card class since the Klee-only
        // companions (2026-10-03). Sim twin: `C.COMPANION_STANDIN_IDS == ()`.
        var pairs = typeof(CompanionStandIns).GetMethod("Pairs", HeadlessGame.All)
            ?? throw new InvalidOperationException(
                "CompanionStandIns.Pairs is gone -- the table moved.");
        Assert.DoesNotContain(Il.CallSequence(pairs),
                              call => call.Contains("ModelDb.Card", StringComparison.Ordinal));
    }
}
