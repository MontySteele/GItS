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

    private static Type PatchType(string name) =>
        typeof(KleeOverhaul).Assembly.GetTypes()
            .FirstOrDefault(t => t.Name == name)
        ?? throw new InvalidOperationException($"no type named {name} in klee.dll");

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

    /// <summary>
    /// The live `CardModel` behind every `ModelDb.Card&lt;T&gt;` an IL read
    /// named. Real cards: the type is found in klee.dll and constructed, which
    /// is what makes `Tags` a measured fact rather than a restated one.
    /// </summary>
    private static IEnumerable<CardModel> Built(IEnumerable<string> calls)
    {
        foreach (var call in calls)
        {
            var name = call.Substring("ModelDb.Card<".Length).TrimEnd('>');
            var type = typeof(KleeOverhaul).Assembly.GetTypes()
                           .FirstOrDefault(t => t.Name == name)
                       ?? throw new InvalidOperationException(
                           $"no card type named {name} in klee.dll");
            yield return (CardModel)Activator.CreateInstance(type)!;
        }
    }

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

    // ---- EB-352: Fasten, the second door ----------------------------------

    [Fact]
    public void The_swept_pool_lookups_are_the_three_this_seam_covers()
    {
        // THE LIST IS THE CLAIM. Three rows, each resolving on the shipped
        // game type, each claimed by exactly one patch class in klee.dll, and
        // nothing else in the mod routing through the seam. Every one of those
        // four assertions has to be edited by hand to add a site.
        Assert.Equal(3, SweptSites.Length);

        foreach (var (target, member, getter, patch, seam) in SweptSites)
        {
            // (1) The base game still declares it. This is the pin that
            // catches a Steam move: a renamed member fails HERE with the name
            // in the message, rather than at boot with Harmony's "Patching
            // exception in method null".
            Assert.NotNull(Site(target, member, getter));

            // (2) The class-level [HarmonyPatch] names that same member, which
            // is what `KleePatchBootstrap` reports on if it stops resolving.
            var declared = PatchType(patch)
                .GetCustomAttributes(inherit: true)
                .OfType<HarmonyPatch>()
                .Select(a => a.info)
                .ToList();
            Assert.Contains(declared, i => i.declaringType == target
                                           && i.methodName == member);

            // (3) A PREFIX returning bool, reaching the seam. A postfix would
            // have to let the base game's own unguarded `First()` run, which
            // is the throw the whole file exists to prevent.
            var prefix = PatchType(patch).GetMethod("Prefix", HeadlessGame.All);
            Assert.NotNull(prefix);
            Assert.Equal(typeof(bool), prefix.ReturnType);
            Assert.Contains(seam, Il.Calls(prefix));
        }

        // (4) NOTHING ELSE IN THE MOD ANSWERS THIS QUESTION. A fourth patch
        // wired to ArmStarterBasics without a row above fails here, so the
        // list cannot quietly fall behind the code it describes.
        var routed = typeof(KleeOverhaul).Assembly.GetTypes()
            .Where(t => t.GetCustomAttributes(inherit: true).OfType<HarmonyPatch>().Any())
            .Where(t => t.GetMethods(HeadlessGame.All)
                         .Any(m => Il.Calls(m).Any(c => c.StartsWith(
                                       "ArmStarterBasics.", StringComparison.Ordinal))))
            .Select(t => t.Name)
            .OrderBy(n => n, StringComparer.Ordinal)
            .ToList();

        Assert.Equal(SweptSites.Select(s => s.Patch).OrderBy(n => n, StringComparer.Ordinal),
                     routed);
    }

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
    public void The_fasten_prefix_binds_the_two_arguments_harmony_passes_by_name()
    {
        // Harmony binds a prefix's arguments BY NAME, so a signature that
        // reads correctly and is named wrongly arms the patch and then never
        // receives the card. `__result` must also be `ref` and must be the
        // property's own type, or the replacement is written to a copy.
        var prefix = PatchType("Fasten_ArmDefendTip_Patch")
            .GetMethod("Prefix", HeadlessGame.All);
        Assert.NotNull(prefix);

        var parameters = prefix.GetParameters();
        Assert.Equal(2, parameters.Length);

        Assert.Equal("__instance", parameters[0].Name);
        Assert.Equal(typeof(Fasten), parameters[0].ParameterType);

        Assert.Equal("__result", parameters[1].Name);
        Assert.True(parameters[1].ParameterType.IsByRef);
        Assert.Equal(typeof(IEnumerable<IHoverTip>),
                     parameters[1].ParameterType.GetElementType());

        // The card-shaped guard is the patch's, and it is the base game's own
        // order: `IsMutable` before `Owner`, because `Owner` calls
        // `AssertMutable()` and throws on a canonical model.
        var calls = Il.Calls(prefix);
        Assert.Contains("AbstractModel.get_IsMutable", calls);
        Assert.Contains("CardModel.get_Owner", calls);
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
    }

    [Fact]
    public void No_card_either_arm_offers_carries_the_defend_tag()
    {
        // WHY THE LOOKUP THROWS RATHER THAN ANSWERING WRONGLY, measured on the
        // real card objects rather than asserted in prose. The arm's
        // `GetUnlockedCards` IS `OfferablePool()` (`KleeCardPool` /
        // `KokomiCardPool` `FilterThroughEpochs`), and not one row in it --
        // slice or Ancient tail -- satisfies `c.Tags.Contains(CardTag.Defend)`.
        //
        // THIS IS ALSO THE FIX'S BOUNDARY. Making one of these rows carry the
        // tag would silence Fasten and would ALSO put a Defend in the reward
        // roll, which is not the fix and is why the answer is a seam instead.
        foreach (var (roster, ancients) in new[]
                 {
                     ("KleeOverhaulRoster", nameof(RosterAncientCards.Klee)),
                     ("KokomiOverhaulRoster", nameof(RosterAncientCards.Kokomi)),
                 })
        {
            var offered = Built(Cards(roster, "Slice"))
                .Concat(Built(Cards("RosterAncientCards", "get_" + ancients)))
                .ToList();

            // Non-empty or the assertion below is a free pass.
            Assert.NotEmpty(offered);
            Assert.DoesNotContain(offered, c => c.Tags.Contains(CardTag.Defend));
        }
    }

    // ---- flag off ---------------------------------------------------------

    [Fact]
    public void With_the_arms_off_the_seam_claims_nobody()
    {
        // THE ACCEPTANCE CONDITION. Off the arms all three seams return null
        // before they touch `ModelDb`, every prefix returns true, and Large
        // Capsule and Fasten answer exactly as the base game wrote them -- her
        // shipped basics and a picture of Duck and Cover, which off the arm is
        // the right answer.
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
                Assert.Null(Answer("DefendTipsFor", character));
            }

            // FURINA IS NEVER CLAIMED, on or off. The reframe arm does not
            // replace her starter, so her shipped basics are still the honest
            // answer and the base game already gives it.
            KleeOverhaul.Enabled = true;
            KokomiOverhaul.Enabled = true;
            var furina = new global::KleeMod.Furina();
            Assert.Null(Answer("StrikeFor", furina));
            Assert.Null(Answer("DefendFor", furina));
            Assert.Null(Answer("DefendTipsFor", furina));
        }
        finally
        {
            KleeOverhaul.Enabled = klee;
            KokomiOverhaul.Enabled = kokomi;
        }
    }
}
