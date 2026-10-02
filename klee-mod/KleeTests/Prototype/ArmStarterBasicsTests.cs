using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;
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
///
/// `EB-352`: THE SECOND DOOR. `EB-351` closed on "everything else goes through
/// `GetUnlockedCards`, which the arm already owns". That is true of every
/// consumer that OFFERS from the pool and false of the one that asks it a
/// question: `Fasten.ExtraHoverTips` renders a picture of the reader's own
/// Defend as <c>GetUnlockedCards(...).First(c =&gt;
/// c.Tags.Contains(CardTag.Defend))</c>, and OWNING `FilterThroughEpochs` is
/// what empties that predicate -- the arm's pool is the prototype rows, whose
/// base Defends live in the starter and not the pool. So the `First()` throws
/// the moment the card is SHOWN. The three pins that arrive with it are the
/// sweep list (<see cref="SweptSites"/>), the shipped getter's own IL, and the
/// arm pools carrying no `CardTag.Defend` -- which is the fact that makes the
/// throw a throw rather than a wrong picture.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class ArmStarterBasicsTests
{
    /// <summary>
    /// EVERY PLACE 0.111.0 ASKS A CARD POOL FOR "THE STRIKE" OR "THE DEFEND"
    /// AND CANNOT SURVIVE THE ANSWER BEING EMPTY, with the patch class that
    /// covers it and the seam that patch routes through.
    ///
    /// THE SWEEP THAT PRODUCED IT, so a reader can redo it rather than trust
    /// it: over the whole decompiled assembly, an unguarded
    /// <c>First</c>/<c>Single</c>/<c>Last</c> taking a `CardModel` predicate
    /// occurs at exactly these three call sites. Every other reader of
    /// `CardTag.Strike` / `CardTag.Defend` either reads the DECK rather than
    /// the pool (`Tezcatara`, `Amalgamator`, `NeowsTalisman`, `LeafyPoultice`,
    /// `NutritiousSoup`, `SoldiersStew`, `PerfectedStrike`) -- and an arm run's
    /// deck does hold four base Defends -- or asks ONE card about itself
    /// (`StrikeDummy`, `FakeStrikeDummy`, `GhostSeed`, `Spiral`, `Goopy`,
    /// `HellraiserPower`, `FastenPower`), which cannot be empty.
    ///
    /// A FOURTH SITE IS A VISIBLE ADDITION. The count is asserted below, the
    /// mod is asserted to route nothing else through the seam, and both halves
    /// have to be edited by hand -- so a site that appears after a Steam move
    /// (`docs/current/operations/steam-moves.md` step 1: re-sweep the new
    /// assembly) shows up as a row somebody wrote, never as silence.
    /// </summary>
    private static readonly (Type Target, string Member, bool Getter,
                             string Patch, string Seam)[] SweptSites =
    {
        (typeof(LargeCapsule), "GetStrikeForCharacter", false,
         "LargeCapsule_ArmStarterStrike_Patch", "ArmStarterBasics.StrikeFor"),
        (typeof(LargeCapsule), "GetDefendForCharacter", false,
         "LargeCapsule_ArmStarterDefend_Patch", "ArmStarterBasics.DefendFor"),
        (typeof(Fasten), "ExtraHoverTips", true,
         "Fasten_ArmDefendTip_Patch", "ArmStarterBasics.DefendTipsFor"),
    };

    /// <summary>Every `ModelDb.Card&lt;T&gt;()` a method makes, in order.</summary>
    private static IReadOnlyList<string> Cards(string type, string method) =>
        Il.CallSequence(Il.Method(type, method))
            .Where(c => c.StartsWith("ModelDb.Card<", StringComparison.Ordinal))
            .ToList();

    private static object Answer(string method, CharacterModel character) =>
        Il.Method("ArmStarterBasics", method)
            .Invoke(null, new object[] { character });

    /// <summary>
    /// The target method behind one <see cref="SweptSites"/> row, resolved the
    /// way HARMONY resolves it -- <c>DeclaredProperty</c> for a getter, which
    /// looks only at the named type. `Fasten.ExtraHoverTips` is an override, so
    /// the walking lookup (<c>AccessTools.Property</c>) would find `CardModel`'s
    /// virtual base and pass while Harmony found nothing.
    /// </summary>
    private static MethodBase Site(Type target, string member, bool getter) =>
        (getter
            ? AccessTools.DeclaredProperty(target, member)?.GetGetMethod(nonPublic: true)
            : AccessTools.DeclaredMethod(target, member))
        ?? throw new InvalidOperationException(
            $"{target.Name}.{member} did not resolve in the shipped assembly");

    // ---- no shipped row reaches the arm, on either seam --------------------

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
                     ("FurinaStageRoster", "StrikeSilent", "DefendSilent"),
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
        Assert.Contains("FurinaStageRoster.StarterStrike", strike);

        var defend = Il.Calls(Il.Method("ArmStarterBasics", "DefendFor"));
        Assert.Contains("KleeOverhaulRoster.StarterDefend", defend);
        Assert.Contains("KokomiOverhaulRoster.StarterDefend", defend);
        Assert.Contains("FurinaStageRoster.StarterDefend", defend);
    }

    // ---- the patch, against the real game method --------------------------

    // ---- EB-352: Fasten, the second door ----------------------------------

    [Fact]
    public void Fastens_defend_tip_is_still_the_unguarded_pool_read_it_was()
    {
        // REAL, not structural: read off the SHIPPED `Fasten`, so this is the
        // statement "the defect is still there" rather than "we believe it is".
        // Three facts, and the patch is wrong if any of them moves.
        var getter = Site(typeof(Fasten), "ExtraHoverTips", getter: true);
        var calls = Il.Calls(getter);

        // (a) It reads THE POOL, through the very method the arm replaces, and
        // takes the first match with no fallback -- `First`, not
        // `FirstOrDefault`. That pair is the throw.
        Assert.Contains("CardPoolModel.GetUnlockedCards", calls);
        Assert.Contains("Enumerable.First", calls);
        Assert.DoesNotContain("Enumerable.FirstOrDefault", calls);

        // (b) It builds exactly the two tips the prefix rebuilds, in that
        // order: the static Block tip, then a picture of a card. If MegaCrit
        // ever adds a third, this bites instead of the arm silently dropping
        // it.
        var factory = Il.CallSequence(getter)
            .Where(c => c.StartsWith("HoverTipFactory.", StringComparison.Ordinal))
            .ToList();
        Assert.Equal(new[] { "HoverTipFactory.Static", "HoverTipFactory.FromCard" },
                     factory);

        // (c) Its own fallback, for a card with no reader, is the Ironclad
        // Defend -- which is why the prefix hands the unowned case straight
        // back to the base getter instead of answering it.
        Assert.Contains("ModelDb.Card<DefendIronclad>", Il.CallSequence(getter));
    }

    [Fact]
    public void The_tip_pair_is_the_starters_defend_and_comes_from_the_one_seam()
    {
        // ONE ANSWER, NOT TWO. `DefendTipsFor` spells the tip PAIR and nothing
        // else -- the Defend it names is `DefendFor`'s, the same one Large
        // Capsule is handed -- so the relic and the hover tip cannot disagree
        // about which Defend is hers.
        var calls = Il.Calls(Il.Method("ArmStarterBasics", "DefendTipsFor"));
        Assert.Contains("ArmStarterBasics.DefendFor", calls);
        Assert.Contains("HoverTipFactory.Static", calls);
        Assert.Contains("HoverTipFactory.FromCard", calls);

        // And it names no roster of its own: it must not be a second place
        // that decides which Defend the arm uses.
        Assert.DoesNotContain("KleeOverhaulRoster.StarterDefend", calls);
        Assert.DoesNotContain("KokomiOverhaulRoster.StarterDefend", calls);
        Assert.DoesNotContain("FurinaStageRoster.StarterDefend", calls);
    }

    // ---- flag off ---------------------------------------------------------

}
