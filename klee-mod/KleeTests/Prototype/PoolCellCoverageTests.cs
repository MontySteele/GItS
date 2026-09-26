using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-363`. THE RARITY x TYPE CELL LEDGER: every cell a BASE event, relic or
/// potion asks a character's own card pool for, walked against every arm pool,
/// with the choice taken for each empty or short one.
///
/// THE DEFECT THIS EXISTS FOR. The Future of Potions took a Regen Potion for an
/// "Upgraded Uncommon Attack" and opened a selection with zero rows, twice
/// (Kokomi r5 run 3). The event asks the character's pool for a rarity x type
/// CELL, the arm pool had nothing in it, and the mod's own reward clamp
/// (`CardFactory_CreateForReward_Clamp_Patch`) turned the base game's
/// descriptive throw into a silent clamp to zero. A 40-row arm pool leaves
/// cells that a 75-row shipped pool fills by sheer size, so this is a property
/// of REPLACING a pool, not of any one event.
///
/// WHAT A CELL IS ASKED FOR, and it is a DEPTH and not a yes/no. Every one of
/// these effects asks for N cards and `CardFactory.CreateForReward` loops N
/// times against an accumulating blacklist, so a cell holding 1 card cannot
/// answer a 3-card draw any more than an empty one can. The depths below are
/// read off the decompiled callers (0.111.0) and are named with them.
///
/// THE CENSUS, from `MegaCrit.Sts2.Core.Models.Events`,
/// `...Models.Relics` and `...Models.Potions`, taking every caller that reaches
/// the CHARACTER's pool with a filter on it:
///
///   TheFutureOfPotions.Trade      rarity x type, 3 cards. The rarity comes
///                                 from the potion (Rare/Event -> Rare,
///                                 Uncommon -> Uncommon, Common/Token ->
///                                 Common) and the type is rolled from
///                                 {Attack, Skill, Power}, with Power removed
///                                 for a Common or Token potion. EIGHT cells,
///                                 not nine: Common x Power is never asked.
///   RoomFullOfCheese.Gorge        Common, 8 cards.
///   GlassEye.AfterObtained        Common / Uncommon / Rare, 3 cards each.
///   SeaGlass.AfterObtained        Common / Uncommon / Rare, 5 cards each
///                                 (`Cards` is 15, divided by 3).
///   HeftyTablet.AfterObtained     Rare, 3 cards (`Cards` is 3).
///   ArcaneScroll.AfterObtained    Rare, 1 card (`Cards` is 1).
///   ScrollBoxes                   Common 4 and Uncommon 2 -- and the base game
///                                 guards this one itself, in
///                                 `CanGenerateBundles`, so it is listed for
///                                 the record and not as a risk.
///   InfestedAutomaton.Study       any rarity x Power, 1 card.
///   InfestedAutomaton.TouchCore   any card costing 0 and not X, 1 card.
///   AttackPotion/SkillPotion/     any rarity x one type, 3 cards, through
///   PowerPotion                   `GetDistinctForCombat` rather than
///                                 `CreateForReward` -- so these CLAMP by
///                                 themselves (`TakeRandom`) and cannot throw,
///                                 but an empty type cell still hands back an
///                                 empty hand.
///   OrobicAcid                    the same three types, 1 card each.
///   Crossbow / BigHat             Attack / Ethereal, and BOTH check
///                                 `Count == 0` themselves before generating.
///                                 Listed, not at risk.
///   DustyTome                     Ancient, already seamed by
///                                 `RosterAncientCards` and gated by
///                                 `tools/lint_ancient_coverage.py`.
///   LargeCapsule                  Basic + Strike / Basic + Defend off
///                                 `AllCards`, already seamed by
///                                 `ArmStarterBasics` (`EB-351`).
///   Trial, BrainLeech, LostCoffer, Orrery, MassiveScroll, DreamCatcher,
///   PrayerWheel, WhiteStar, Kaleidoscope, LeadPaperweight, EndlessConveyor
///                                 no filter at all, or the colorless pool.
///                                 The clamp has always owned these.
///   ColorfulPhilosophers          asks ANOTHER character's pool by
///                                 construction (`character.CardPool !=
///                                 cardPool`), so no arm pool is ever the one
///                                 queried. Out of scope, and said so here
///                                 because it looks in scope.
///
/// The Teyvat arm's event mirrors (`Teyvat/Events/Mirrors/`) re-implement
/// several of these, including The Future of Potions, and every one of them
/// routes through the same `CardFactory.CreateForReward`. The seam therefore
/// covers the mirrors without naming them.
///
/// THE ARMS ARE READ OFF THEIR OWN ROSTERS, not off a second list kept here. A
/// hand list in a test file is a copy of the pool that goes stale the day a row
/// lands; these walk the compiled `ModelDb.Card&lt;T&gt;` calls in the roster
/// methods themselves and construct each card, so a row added tomorrow is in
/// the matrix tomorrow. `ModelDb` is outside the headless boundary
/// (README.md), which is why the TYPE is taken from the call and the model is
/// built with `new` rather than fetched.
///
/// THE NUMBERS HERE ARE PROTOTYPE NUMBERS (D by the ladder). Nothing is
/// quotable.
/// </summary>
public class PoolCellCoverageTests
{
    // ---- The census, as data ---------------------------------------------

    /// <summary>One queried cell: what asks for it, what it admits, how deep.</summary>
    public sealed record Cell(
        string Name, string Asker, int Depth, Func<CardModel, bool> Admits);

    private static bool IsRollable(CardModel c) =>
        c.Rarity == CardRarity.Common
        || c.Rarity == CardRarity.Uncommon
        || c.Rarity == CardRarity.Rare;

    private static Cell RarityType(CardRarity r, CardType t, string asker, int depth) =>
        new($"{r}/{t}", asker, depth, c => c.Rarity == r && c.Type == t);

    /// <summary>
    /// Every cell in the census above that is NOT already guarded by the base
    /// game or by an existing seam. The guarded ones are named in the class
    /// comment rather than walked, because a test that asserts a fact the base
    /// game already enforces is a test of the base game.
    /// </summary>
    public static IReadOnlyList<Cell> Census { get; } = new List<Cell>
    {
        // The Future of Potions: eight cells, three deep.
        RarityType(CardRarity.Common, CardType.Attack, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Common, CardType.Skill, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Uncommon, CardType.Attack, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Uncommon, CardType.Skill, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Uncommon, CardType.Power, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Rare, CardType.Attack, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Rare, CardType.Skill, "TheFutureOfPotions", 3),
        RarityType(CardRarity.Rare, CardType.Power, "TheFutureOfPotions", 3),

        // Rarity-only, at the deepest ask each rarity carries.
        new("Common/*", "RoomFullOfCheese.Gorge", 8,
            c => c.Rarity == CardRarity.Common),
        new("Uncommon/*", "SeaGlass", 5, c => c.Rarity == CardRarity.Uncommon),
        new("Rare/*", "SeaGlass", 5, c => c.Rarity == CardRarity.Rare),

        // Type-only. The potions clamp themselves, so the depth that matters
        // for them is 1 -- but InfestedAutomaton.Study asks Power with DEFAULT
        // odds, where the rarity is rolled from whatever rarities the surviving
        // cards carry, so one Power of any rarity answers it.
        new("*/Power", "InfestedAutomaton.Study", 1,
            c => c.Type == CardType.Power && IsRollable(c)),
        new("*/Attack", "AttackPotion, OrobicAcid, Crossbow", 1,
            c => c.Type == CardType.Attack && IsRollable(c)),
        new("*/Skill", "SkillPotion, OrobicAcid", 1,
            c => c.Type == CardType.Skill && IsRollable(c)),

        // The one non-rarity, non-type cell that can go empty on a small pool.
        new("cost 0", "InfestedAutomaton.TouchCore", 1,
            c => IsRollable(c) && c.EnergyCost != null
                 && c.EnergyCost.Canonical == 0 && !c.EnergyCost.CostsX),
    };

    public static IEnumerable<object[]> ArmsAndCells =>
        from arm in ArmPools.Names
        from cell in Census
        select new object[] { arm, cell.Name };

    public static IEnumerable<object[]> Arms =>
        ArmPools.Names.Select(n => new object[] { n });

    // ---- The matrix -------------------------------------------------------

    /// <summary>
    /// THE ACCEPTANCE CONDITION, and the whole row in one line: no base event
    /// or relic opens an empty selection under either arm.
    ///
    /// A cell passes one of two ways. FILLED: it holds at least the depth its
    /// asker draws. SEAMED: the widening ladder in
    /// `CardFactory_CreateForReward_Clamp_Patch` finds it a non-empty set to
    /// draw from instead. A cell that is neither is a hand back of nothing,
    /// which is what `EB-363` was opened for.
    /// </summary>
    [Theory]
    [MemberData(nameof(ArmsAndCells))]
    public void Every_queried_cell_is_filled_or_seamed(string arm, string cellName)
    {
        var cell = Census.Single(c => c.Name == cellName);
        var pool = ArmPools.Offerable(arm);
        var inCell = pool.Where(cell.Admits).ToList();

        if (inCell.Count >= cell.Depth)
        {
            return; // FILLED.
        }

        var whole = pool.Where(IsRollable).ToList();
        var seam = Seam.WidenedAdmissions(cell.Depth, inCell, whole);

        Assert.True(
            seam is { Count: > 0 },
            $"{arm} cell {cellName} ({cell.Asker}, draws {cell.Depth}) holds "
            + $"{inCell.Count} card(s) and the widening ladder found nothing to "
            + "draw from instead -- the effect would hand back an empty "
            + "selection. Fill the cell on the sheet or extend the seam.");
    }

    /// <summary>
    /// THE LEDGER, and it is deliberately a whitelist rather than a count. A
    /// cell that stops being short is good news and this test says so by going
    /// red; a cell that BECOMES short is the defect and it says that the same
    /// way. Either way the PR body's matrix and the code agree or the suite
    /// fails, which is the only way a matrix in a PR body stays true.
    /// </summary>
    [Theory]
    [MemberData(nameof(Arms))]
    public void The_short_cells_are_the_ones_the_row_names(string arm)
    {
        var pool = ArmPools.Offerable(arm);
        var actual = Census
            .Where(c => pool.Count(c.Admits) < c.Depth)
            .Select(c => c.Name)
            .OrderBy(n => n, StringComparer.Ordinal)
            .ToList();

        var expected = (arm switch
        {
            // NONE SINCE THE R276 POOL EXPANSION: Rare/Attack and Rare/Skill
            // were the two short cells, and the expansion's ten Rares (two
            // Attacks, three Skills, five Powers) fill both.
            "klee-overhaul" => System.Array.Empty<string>(),

            // The four `EB-363` was raised on, plus the Rare shelf being
            // thinner than Sea Glass's five-card draw -- which no widening can
            // fix (it IS every Rare she has) and which the clamp has always
            // handled by offering four.
            "kokomi-overhaul" => new[] { "Rare/*", "Rare/Attack", "Rare/Power", "Rare/Skill", "Uncommon/Attack" },

            // THE SURPRISE OF THIS AUDIT. The Stage substitutes one for one at
            // the same rarity, so on paper it inherits the shipped sheet's
            // coverage -- but `DropRetiredRows`, the arm's TEXT filter, then
            // takes every remaining shipped row that still prints Encore,
            // Spotlight, Center Stage, Salon, Fanfare or Burst, and that is
            // most of the sheet: her offer pool was 29 rows, not 84.
            //
            // R276's BATCH TWO filled two of the five: fifteen Stage rows
            // (three Uncommon Powers, two Rare Powers) make the Rare shelf five
            // deep and give the Uncommon Powers a cell. The Rare cells by TYPE
            // are still short -- one Attack, two Powers, two Skills -- and are
            // seamed by the widening ladder.
            //
            // THE GUEST CAST (2026-09-25) filled Rare/Skill: three Rare Guest
            // Stars (Neuvillette, Clorinde, Navia).
            //
            // THE SUPPORTING POOL (2026-09-26) filled the last two: three Rare
            // Attacks (Bring the House Down, Grand Deluge beside Let the
            // People Rejoice) and four Rare Powers (Eternal Applause, Regina
            // of All Waters, One-Woman Show beside Arkhe Alignment and A
            // Five-Century Act). No cell is short.
            "furina-stage" => System.Array.Empty<string>(),
            _ => throw new InvalidOperationException(arm),
        }).OrderBy(n => n, StringComparer.Ordinal).ToList();

        Assert.Equal(expected, actual);
    }

    /// <summary>
    /// `EB-284`'s cell, asked again of every arm because `EB-363`'s audit found
    /// it EMPTY under the Furina Stage: Dusty Tome is the only thing in the
    /// game that draws a `CardRarity.Ancient` card, it draws it from
    /// `GetUnlockedCards`, and it does not check that it found one -- so an
    /// empty Ancient cell is not a thin reward, it is an NRE inside Darv's
    /// options and a run that ends at the act-two door.
    ///
    /// NOT IN THE CENSUS ABOVE, because this cell cannot be SEAMED. Widening it
    /// would hand Dusty Tome a card of another rarity, which is not what it
    /// asked for and not what Darv's screen is built to show. The only answer
    /// is a filled cell, which is what `RosterAncientCards` is for and what the
    /// Stage's filter now leaves alone.
    /// </summary>
    [Theory]
    [MemberData(nameof(Arms))]
    public void Every_arm_keeps_an_ancient_row_for_dusty_tome(string arm)
    {
        Assert.Contains(ArmPools.Offerable(arm),
            c => c.Rarity == CardRarity.Ancient);
    }

    /// <summary>
    /// Common x Power is the one cell both replacement arms leave EMPTY, and it
    /// is not in the census because nothing asks for it: The Future of Potions
    /// removes Power from the type list for a Common or Token potion, and every
    /// other Power query is rarity-free. Pinned rather than assumed, because
    /// "nothing asks for it" is the whole reason an empty cell is allowed to
    /// stand.
    /// </summary>
    [Fact]
    public void Common_by_Power_is_empty_on_both_replacement_arms_and_nothing_asks_for_it()
    {
        foreach (var arm in new[] { "klee-overhaul", "kokomi-overhaul" })
        {
            Assert.DoesNotContain(ArmPools.Offerable(arm),
                c => c.Rarity == CardRarity.Common && c.Type == CardType.Power);
        }

        Assert.DoesNotContain(Census, c => c.Name == "Common/Power");
    }

    /// <summary>
    /// And the claim the line above rests on, read off the SHIPPED event rather
    /// than off a comment: `TheFutureOfPotions` removes Power from the type
    /// list, and it is the potion's own rarity that decides when.
    /// </summary>
    [Fact]
    public void The_shipped_event_still_removes_Power_for_a_common_potion()
    {
        var potions = typeof(MegaCrit.Sts2.Core.Models.Events.TheFutureOfPotions);
        var getter = potions
            .GetProperty("PotionToCardType", HeadlessGame.All)!
            .GetGetMethod(nonPublic: true)!;

        var calls = Il.Calls(getter);
        Assert.Contains(calls, c => c.EndsWith(".Remove", StringComparison.Ordinal));
        Assert.Contains(calls, c => c.Contains("Rng.NextItem", StringComparison.Ordinal));

        // And the draw is still three cards deep.
        var trade = potions.GetMethod("Trade", HeadlessGame.All)!;
        Assert.Contains(Il.Calls(trade), c => c.Contains("CardReward", StringComparison.Ordinal));
    }

    // ---- The ladder itself ------------------------------------------------

    /// <summary>
    /// A REAL pool row of that rarity and type, not a stand-in. Every rung of
    /// the ladder is a decision about `CardModel`s, and the three arms between
    /// them stock every combination these tests need -- so a fake would be a
    /// third definition of a card model beside the game's and the mod's, for
    /// no fact it could reach that a real row cannot.
    /// </summary>
    private static CardModel One(CardRarity rarity, CardType type, int skip = 0) =>
        ArmPools.Names
            .SelectMany(ArmPools.Offerable)
            .Where(c => c.Rarity == rarity && c.Type == type)
            .Skip(skip)
            .First();

    [Fact]
    public void Rung_one_a_cell_that_can_fill_the_draw_is_not_widened()
    {
        var cell = new[]
        {
            One(CardRarity.Rare, CardType.Attack),
            One(CardRarity.Rare, CardType.Attack, 1),
            One(CardRarity.Rare, CardType.Attack, 2),
        };
        var whole = cell.Concat(new[] { One(CardRarity.Common, CardType.Skill) }).ToList();

        Assert.Null(Seam.WidenedAdmissions(3, cell, whole));
    }

    [Fact]
    public void Rung_one_an_unfiltered_draw_has_nothing_to_widen_to()
    {
        // The Sealed Deck case: the cell IS the pool, so the clamp owns it and
        // the ladder must not pretend otherwise.
        var whole = new[] { One(CardRarity.Common, CardType.Skill) }.ToList();
        Assert.Null(Seam.WidenedAdmissions(30, whole, whole));
    }

    [Fact]
    public void Rung_two_a_short_cell_widens_to_its_own_rarity_first()
    {
        // Kokomi's Rare x Attack: one row, three asked, four Rares in the pool.
        var cell = new[] { One(CardRarity.Rare, CardType.Attack) };
        var whole = cell.Concat(new[]
        {
            One(CardRarity.Rare, CardType.Skill),
            One(CardRarity.Rare, CardType.Power),
            One(CardRarity.Rare, CardType.Power, 1),
            One(CardRarity.Common, CardType.Skill),
            One(CardRarity.Common, CardType.Skill, 1),
        }).ToList();

        var seam = Seam.WidenedAdmissions(3, cell, whole);

        Assert.NotNull(seam);
        Assert.Equal(4, seam!.Count);
        Assert.All(seam, c => Assert.Equal(CardRarity.Rare, c.Rarity));
    }

    [Fact]
    public void Rung_three_an_empty_cell_widens_to_the_whole_pool()
    {
        // There is no rarity to preserve when nothing survived the filter.
        var whole = new[]
        {
            One(CardRarity.Common, CardType.Skill),
            One(CardRarity.Uncommon, CardType.Attack),
        }.ToList();

        var seam = Seam.WidenedAdmissions(3, Array.Empty<CardModel>(), whole);

        Assert.NotNull(seam);
        Assert.Equal(whole.Count, seam!.Count);
    }

    [Fact]
    public void Rung_three_is_taken_when_the_neighbour_cell_is_short_too()
    {
        // A neighbour that cannot fill the draw buys nothing over the whole
        // pool and would cost the rows the whole pool would have found.
        var cell = new[] { One(CardRarity.Rare, CardType.Attack) };
        var whole = cell.Concat(new[]
        {
            One(CardRarity.Rare, CardType.Skill),
            One(CardRarity.Common, CardType.Skill),
            One(CardRarity.Common, CardType.Attack),
        }).ToList();

        var seam = Seam.WidenedAdmissions(3, cell, whole);

        Assert.NotNull(seam);
        Assert.Equal(4, seam!.Count);
    }

    [Fact]
    public void The_seam_never_admits_a_card_the_pool_does_not_hold()
    {
        var cell = new[] { One(CardRarity.Rare, CardType.Attack) };
        var whole = cell.Concat(new[]
        {
            One(CardRarity.Rare, CardType.Skill),
            One(CardRarity.Rare, CardType.Power),
            One(CardRarity.Common, CardType.Skill),
        }).ToList();

        var seam = Seam.WidenedAdmissions(3, cell, whole);

        Assert.NotNull(seam);
        Assert.All(seam!, c => Assert.Contains(c, whole));
    }

    // ---- The plumbing the ladder is wired into ----------------------------

    /// <summary>
    /// STRUCTURAL, and labelled: the prefix takes its options by `ref` so the
    /// widening is per draw, and the copy carries the flags. A `CardReward`
    /// keeps the options object for its reroll and an event may hold it across
    /// two draws, so widening in place would widen a later draw the pool might
    /// by then answer as asked. Running it would need a live `Player`, which is
    /// outside the boundary.
    /// </summary>
    [Fact]
    public void The_prefix_widens_by_copy_and_per_draw()
    {
        var patch = typeof(global::KleeMod.KleeMod).Assembly
            .GetType("KleeMod.CardFactory_CreateForReward_Clamp_Patch", throwOnError: true)!;
        var prefix = patch.GetMethod("Prefix", HeadlessGame.All)!;

        var options = prefix.GetParameters().Single(p => p.Name == "options");
        Assert.True(options.ParameterType.IsByRef,
            "the prefix must take `ref CardCreationOptions` -- widening a shared "
            + "options object would widen a later draw too.");

        var clone = patch.GetMethod("Clone", HeadlessGame.All)!;
        var calls = Il.Calls(clone);
        Assert.Contains(calls, c => c.Contains("WithFlags", StringComparison.Ordinal));
        Assert.Contains(calls, c => c.Contains("WithRngOverride", StringComparison.Ordinal));
    }

    /// <summary>
    /// The member set `Clone` copies by hand, pinned against the record's own
    /// public surface. A game update adding a sixth member would be dropped
    /// silently by the copy; this turns that into a red test.
    /// </summary>
    [Fact]
    public void The_options_record_still_holds_exactly_the_members_the_copy_names()
    {
        var members = typeof(MegaCrit.Sts2.Core.Runs.CardCreationOptions)
            .GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Select(p => p.Name)
            .OrderBy(n => n, StringComparer.Ordinal)
            .ToList();

        Assert.Equal(
            new[] { "CardPoolFilter", "CardPools", "Flags", "RarityOdds", "RngOverride", "Source" },
            members);
    }
}
