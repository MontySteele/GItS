using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-351`: THE THIRD SEAM, and the pins that say a shipped row cannot reach
/// an overhaul run through it.
///
/// THE DEFECT. A blind seat on `0.2.2301+proto` opened fight 1 of a Klee
/// overhaul run holding **Duck and Cover**, with **Kaboom!** in the same
/// twelve-card deck (`review/qa/klee-round-8-2026-09-03/opus-act1.md`). Both of
/// the arm's own seams were intact. The third reader was Large Capsule, the
/// Neow relic that adds "an additional Strike and Defend", which resolves those
/// two words as
/// <c>character.CardPool.AllCards.First(c =&gt; c.Rarity == Basic &amp;&amp;
/// c.Tags.Contains(CardTag.Strike))</c> -- `AllCards`, which
/// `FilterThroughEpochs` is never applied to and which the arm therefore never
/// replaced. The whole argument is on
/// <see cref="KleeMod.Powers.ArmStarterBasics"/>.
///
/// WHY THE ID PINS READ THE POOL RATHER THAN A LIST. The two "no shipped row"
/// pins below take the shipped set from the pool's OWN declaration
/// (`KleeCardPool.GenerateAllCards`, `KokomiCardRoster.All`) rather than from a
/// list written here, so a row added to a sheet tomorrow is covered the day it
/// lands and no second definition of "which rows are shipped" can drift.
///
/// STRUCTURAL WHERE IT HAS TO BE, and labelled. `ModelDb` is populated only by
/// the game's boot (README, "The headless boundary"), so every
/// <c>ModelDb.Card&lt;T&gt;()</c> in these lists throws if called -- the ids are
/// read off the compiled methods instead. What IS real: the shipped basics'
/// own rarity and tags, the game method the patch targets, and the seam
/// answering null with the arms off.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class ArmStarterBasicsTests
{
    /// <summary>Every `ModelDb.Card&lt;T&gt;()` a method makes, in order.</summary>
    private static IReadOnlyList<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();

    private static Type PatchType(string name) =>
        typeof(KleeOverhaul).Assembly.GetTypes()
            .FirstOrDefault(t => t.Name == name)
        ?? throw new InvalidOperationException($"no type named {name} in klee.dll");

    private static object Answer(string method, CharacterModel character) =>
        Il.Method("ArmStarterBasics", method)
            .Invoke(null, new object[] { character });

    // ---- no shipped row reaches the arm, on either seam --------------------

    [Fact]
    public void The_klee_arm_opens_with_ten_ids_and_not_one_is_a_shipped_row()
    {
        // THE STARTER, restated as the defect's own question: not "is it ten
        // cards" (`BaseBasicsTests` pins that against R242's ruled order) but
        // "can a shipped Klee row be in the deck a run opens on".
        var starter = Cards("KleeOverhaulRoster", "StartingDeck");
        var shipped = Cards("KleeCardPool", "GenerateAllCards");

        Assert.Equal(10, starter.Count);
        // The sets must be non-empty or the intersection below is a free pass:
        // an IL read that resolved nothing would "prove" the arm clean.
        Assert.NotEmpty(shipped);
        Assert.Contains("ModelDb.Card<Kaboom>", shipped);
        Assert.Contains("ModelDb.Card<DuckAndCover>", shipped);

        Assert.Empty(starter.Intersect(shipped));
    }

    [Fact]
    public void No_shipped_klee_row_is_offerable_under_the_arm()
    {
        // The OFFER surface, read at the list the arm states rather than at
        // `OfferablePool`, whose body is a Concat and names no card itself.
        // The Ancient tail it adds is deliberately shared with the shipped
        // pool (`EB-284`, Dusty Tome), which is why the slice is the honest
        // thing to intersect.
        var slice = Cards("KleeOverhaulRoster", "Slice");
        var shipped = Cards("KleeCardPool", "GenerateAllCards");

        Assert.NotEmpty(slice);
        Assert.NotEmpty(shipped);
        Assert.Empty(slice.Intersect(shipped));
    }

    [Fact]
    public void The_kokomi_arm_names_no_shipped_row_on_either_seam()
    {
        // The same defect lives on her arm for the same reason -- Large
        // Capsule would hand a Kokomi overhaul run her shipped Water's Edge
        // and Coral Guard -- so the same two pins are owed here.
        var starter = Cards("KokomiOverhaulRoster", "StartingDeck");
        var slice = Cards("KokomiOverhaulRoster", "Slice");
        var shipped = Cards("KokomiCardRoster", "get_All");

        Assert.Equal(10, starter.Count);
        Assert.NotEmpty(slice);
        Assert.NotEmpty(shipped);
        Assert.Contains("ModelDb.Card<WatersEdge>", shipped);
        Assert.Contains("ModelDb.Card<CoralGuard>", shipped);

        Assert.Empty(starter.Intersect(shipped));
        Assert.Empty(slice.Intersect(shipped));
    }

    // ---- the third seam answers with the starter's own pair ---------------

    [Fact]
    public void The_relic_pair_is_the_pair_the_starter_opens_with()
    {
        // THE CORRESPONDENCE THE COMPILER CANNOT HOLD. The starter states its
        // ten ids literally, because that list is R242's ruled artifact and its
        // pin reads it straight off the method; the relic seam states the pair
        // a second time. This pin is what stops the two drifting -- move the
        // starter to a different base pair without moving the accessors and it
        // bites.
        foreach (var (roster, strike, defend) in new[]
                 {
                     ("KleeOverhaulRoster", "StrikeIronclad", "DefendIronclad"),
                     ("KokomiOverhaulRoster", "StrikeSilent", "DefendSilent"),
                 })
        {
            Assert.Equal(new[] { $"ModelDb.Card<{strike}>" },
                         Cards(roster, "StarterStrike"));
            Assert.Equal(new[] { $"ModelDb.Card<{defend}>" },
                         Cards(roster, "StarterDefend"));

            // And the starter opens with those two base types and no other:
            // eight of its ten slots, four apiece.
            var starter = Cards(roster, "StartingDeck");
            Assert.Equal(4, starter.Count(c => c == $"ModelDb.Card<{strike}>"));
            Assert.Equal(4, starter.Count(c => c == $"ModelDb.Card<{defend}>"));
        }
    }

    [Fact]
    public void Both_arms_route_through_the_one_seam()
    {
        // STRUCTURAL, and the fact is that there is ONE answer rather than a
        // per-relic copy: whatever else ever asks "which Strike is hers", it
        // asks here.
        var strike = Il.Calls(Il.Method("ArmStarterBasics", "StrikeFor"));
        Assert.Contains("KleeOverhaulRoster.StarterStrike", strike);
        Assert.Contains("KokomiOverhaulRoster.StarterStrike", strike);
        Assert.Contains("KleeOverhaul.get_Enabled", strike);
        Assert.Contains("KokomiOverhaul.get_Enabled", strike);

        var defend = Il.Calls(Il.Method("ArmStarterBasics", "DefendFor"));
        Assert.Contains("KleeOverhaulRoster.StarterDefend", defend);
        Assert.Contains("KokomiOverhaulRoster.StarterDefend", defend);
        Assert.Contains("KleeOverhaul.get_Enabled", defend);
        Assert.Contains("KokomiOverhaul.get_Enabled", defend);
    }

    // ---- the patch, against the real game method --------------------------

    [Fact]
    public void The_patch_targets_the_two_methods_the_base_game_still_declares()
    {
        // REAL, not structural, and it is the pin that catches a Steam move:
        // both target methods are resolved off the shipped `LargeCapsule`, and
        // the PARAMETER NAME is asserted because Harmony binds a prefix's
        // arguments by name -- a rename would arm the patch and then never
        // pass it a character.
        foreach (var (patch, target, seam) in new[]
                 {
                     ("LargeCapsule_ArmStarterStrike_Patch",
                      "GetStrikeForCharacter", "ArmStarterBasics.StrikeFor"),
                     ("LargeCapsule_ArmStarterDefend_Patch",
                      "GetDefendForCharacter", "ArmStarterBasics.DefendFor"),
                 })
        {
            var method = AccessTools.Method(typeof(LargeCapsule), target);
            Assert.NotNull(method);
            Assert.True(method.IsStatic);
            var parameter = Assert.Single(method.GetParameters());
            Assert.Equal("character", parameter.Name);
            Assert.Equal(typeof(CharacterModel), parameter.ParameterType);

            // The class-level [HarmonyPatch] names that same method, which is
            // what `KleePatchBootstrap` reports on if it ever stops resolving.
            var declared = PatchType(patch)
                .GetCustomAttributes(inherit: true)
                .OfType<HarmonyPatch>()
                .Select(a => a.info)
                .ToList();
            Assert.Contains(declared, i => i.declaringType == typeof(LargeCapsule)
                                           && i.methodName == target);

            // A PREFIX, not a postfix: a postfix would have to let the base
            // game's own unguarded `First()` run first, which is the throw
            // KleeSelfCheck's R11 exists to prevent.
            var prefix = PatchType(patch).GetMethod("Prefix", HeadlessGame.All);
            Assert.NotNull(prefix);
            Assert.Equal(typeof(bool), prefix.ReturnType);
            Assert.Contains(seam, Il.Calls(prefix));
        }
    }

    [Fact]
    public void The_shipped_basics_are_what_the_relic_would_otherwise_hand_over()
    {
        // WHY THE SEAM IS NEEDED AT ALL, asserted rather than described. These
        // two rows satisfy Large Capsule's predicate exactly, they are first in
        // the pool's declaration, and they CANNOT be taken out of it -- a card
        // missing from `AllCards` has no `CardModel.Pool` and throws "You
        // monster!" on draw, which is why `GenerateAllCards` is untouched by
        // the arm. Delete the patch and this pair is what an arm run receives.
        var kaboom = new Kaboom();
        Assert.Equal(CardRarity.Basic, kaboom.Rarity);
        Assert.Contains(CardTag.Strike, kaboom.Tags);

        var duckAndCover = new DuckAndCover();
        Assert.Equal(CardRarity.Basic, duckAndCover.Rarity);
        Assert.Contains(CardTag.Defend, duckAndCover.Tags);

        var shipped = Cards("KleeCardPool", "GenerateAllCards");
        Assert.Equal("ModelDb.Card<Kaboom>", shipped[0]);
        Assert.Equal("ModelDb.Card<DuckAndCover>", shipped[1]);
    }

    // ---- flag off ---------------------------------------------------------

    [Fact]
    public void With_the_arms_off_the_seam_claims_nobody()
    {
        // THE ACCEPTANCE CONDITION. Off the arms the seam returns null before
        // it touches `ModelDb`, the prefix returns true, and Large Capsule
        // answers exactly as the base game wrote it -- her shipped basics,
        // which off the arm is the right answer.
        var klee = KleeOverhaul.Enabled;
        var kokomi = KokomiOverhaul.Enabled;
        try
        {
            KleeOverhaul.Enabled = false;
            KokomiOverhaul.Enabled = false;

            foreach (CharacterModel character in new CharacterModel[]
                     { new global::KleeMod.Klee(), new global::KleeMod.Kokomi() })
            {
                Assert.Null(Answer("StrikeFor", character));
                Assert.Null(Answer("DefendFor", character));
            }

            // FURINA IS NEVER CLAIMED, on or off. The reframe arm does not
            // replace her starter, so her shipped basics are still the honest
            // answer and the base game already gives it.
            KleeOverhaul.Enabled = true;
            KokomiOverhaul.Enabled = true;
            var furina = new global::KleeMod.Furina();
            Assert.Null(Answer("StrikeFor", furina));
            Assert.Null(Answer("DefendFor", furina));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }
    }
}
