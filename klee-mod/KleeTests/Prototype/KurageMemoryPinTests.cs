using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Cards;
using KleeMod.Cards.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// THE KURAGE'S MEMORY v3 (QUARANTINED) -- what the headless bite-check can
/// actually reach, and nothing beyond it.
///
/// Spec: review/active/kokomi-kurage-memory-2026-08-29.md sec.11. Rule:
/// klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs. Sim twin:
/// tier0/tests/test_kurage_memory.py, which tests the whole rule because the
/// sim has an engine to run it in.
///
/// WHAT IS REACHABLE HERE, AND IT IS ONE THING: THE PRICE. `FaceCost` and
/// `Price` are pure reads off a CardModel's own `CardEnergyCost`, so the 3x,
/// the permanent-upgrade clause, the temporary-discount exclusion and the
/// X-cost refusal are all REAL assertions against the shipped arithmetic --
/// which matters more than it looks, because the price is the one number in
/// the rule a player pays and the one thing a strip can be wrong about.
///
/// WHAT IS NOT REACHABLE, stated rather than faked past (README, "The headless
/// boundary"):
///
///   * THE FIRE. `Fire` needs a live CombatState (CloneCard), a card PLAY
///     (CardCmd.AutoPlay) and a pile move (CardPileCmd.RemoveFromCombat). All
///     three are outside the boundary, so the fire, the BLOCK, the
///     one-per-turn latch and the removal are pinned STRUCTURALLY below --
///     the call set, not the behaviour -- and labelled as such.
///   * BOTH ENTRY RULES. `NoteMuster` runs inside a transform and
///     `NoteExhaust` inside the exhaust funnel; both need a Player whose
///     Creature carries a live combat, and enrolment writes a queue keyed off
///     it. The sim owns those, per rule, in its own section.
///   * THE PULSE, for the same reason: damage, Block and Charge grants are
///     command calls into a combat.
///   * THE STRIP. It draws into a Godot Label out of the pck, and no test may
///     touch a Godot object at all.
/// </summary>
public class KurageMemoryPinTests
{
    /// <summary>A 2-cost Skill, standing in for any remembered face. Built
    /// here rather than borrowed from a sheet so a repricing of a shipped card
    /// cannot silently move what this file asserts.</summary>
    private sealed class ProbeFace : CustomCardModel
    {
        public ProbeFace()
            : base(2, CardType.Skill, CardRarity.Common, TargetType.Self,
                   autoAdd: false)
        {
        }

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    /// <summary>An X-cost face. "X" has no cost to multiply.</summary>
    private sealed class ProbeXFace : CustomCardModel
    {
        public ProbeXFace()
            : base(0, CardType.Skill, CardRarity.Common, TargetType.Self,
                   autoAdd: false)
        {
        }

        protected override bool HasEnergyCostX => true;

        protected override Task OnPlay(
            PlayerChoiceContext choiceContext, CardPlay cardPlay)
            => Task.CompletedTask;
    }

    private static ProbeFace MutableProbe()
    {
        var card = new ProbeFace();
        // A freshly constructed CardModel is CANONICAL -- the shared prototype
        // -- and CardEnergyCost.GetWithModifiers short-circuits on it, as does
        // every mutator. The same IsMutable flag the game's ToMutable would
        // set is set directly (M2's idiom, ParityAuthorityPinTests).
        Seat.Set(card, "IsMutable", true);
        return card;
    }

    // --- the price -------------------------------------------------------

    [Fact]
    public void The_price_is_three_times_the_face_cost()
    {
        // [USER], sec.11.1: "cards cost Charge equal to 3x their Cost."
        Assert.Equal(6, KurageMemory.Price(MutableProbe()));
    }

    [Fact]
    public void A_zero_cost_face_is_free_because_it_is()
    {
        // Gorou in the starter deck is the named example, and the whole reason
        // the engine is reachable at turn one at all.
        var gorou = new GorouInuzakaCharge();
        Seat.Set(gorou, "IsMutable", true);

        Assert.Equal(0, KurageMemory.FaceCost(gorou));
        Assert.Equal(0, KurageMemory.Price(gorou));
    }

    [Fact]
    public void A_permanent_upgrade_moves_the_price()
    {
        // UpgradeBy writes CardEnergyCost's `_base`, which is the face -- so
        // an upgraded card is remembered at its upgraded cost.
        var card = MutableProbe();
        card.EnergyCost.UpgradeBy(-1);

        Assert.Equal(1, KurageMemory.FaceCost(card));
        Assert.Equal(3, KurageMemory.Price(card));
    }

    [Fact]
    public void A_temporary_discount_is_ignored()
    {
        // sec.11.4: "the price is read off the CARD and never off
        // combat.card_cost". Both shapes of temporary discount the mod uses
        // are local modifiers and none of them touches `_base`.
        var thisTurn = MutableProbe();
        thisTurn.EnergyCost.SetThisTurn(0);
        Assert.Equal(6, KurageMemory.Price(thisTurn));

        var thisCombat = MutableProbe();
        thisCombat.EnergyCost.AddThisCombat(-2, reduceOnly: false);
        Assert.Equal(6, KurageMemory.Price(thisCombat));
    }

    [Fact]
    public void A_muster_recruits_stamped_face_cost_wins_over_the_modifier()
    {
        // THE ONE EXCEPTION, and the reason it exists: tier0's _op_conscript
        // writes recruit.cost PERMANENTLY, while the mod applies the same -1
        // as AddThisCombat because CardModel has no settable base cost. The
        // recruit's intended face cost is stamped at the transformation so
        // both engines price a Muster recruit at the same number.
        var recruit = MutableProbe();
        recruit.EnergyCost.AddThisCombat(-1, reduceOnly: false);
        var kokomi = Seat.Kokomi();
        KurageMemory.NoteMusterRecruit(kokomi.Player, recruit, 1);

        Assert.Equal(1, KurageMemory.FaceCost(recruit));
        Assert.Equal(3, KurageMemory.Price(recruit));
        KurageMemory.ResetForCombat();
    }

    [Fact]
    public void An_x_cost_face_has_no_price_and_is_refused()
    {
        // Refused at the door rather than priced off a turn that is over.
        var card = new ProbeXFace();
        Seat.Set(card, "IsMutable", true);

        Assert.Null(KurageMemory.Price(card));
    }

    // --- the empty state -------------------------------------------------

    [Fact]
    public void A_fresh_fight_has_an_empty_memory_and_says_so()
    {
        KurageMemory.ResetForCombat();
        var kokomi = Seat.Kokomi().WithCombatState();

        Assert.Empty(KurageMemory.Queue(kokomi.Player));
        // An EMPTY memory is not a BLOCKED one, and the strip must not let the
        // two look alike (sec.11.5).
        Assert.Equal("Charge 0 — memory empty",
                     KurageMemory.Reading(kokomi.Player));
        Assert.DoesNotContain("blocked", KurageMemory.StripText(kokomi.Player));
    }

    [Fact]
    public void A_non_kokomi_seat_has_no_memory_at_all()
    {
        // The character test is not decoration: a Companion-playing Furina
        // must not start banking a memory.
        var furina = Seat.Furina().WithCombatState();

        Assert.False(KurageMemory.IsLive(furina.Creature));
        Assert.Empty(KurageMemory.Queue(furina.Player));
        Assert.Equal(string.Empty, KurageMemory.Reading(furina.Player));
    }

    [Fact]
    public void The_bridge_snapshot_is_empty_for_a_seat_that_is_not_hers()
    {
        // EB-181's contract: an EMPTY map means "the rule is here and this
        // player is not Kokomi". The bridge turns that into a present-but-empty
        // key; an ABSENT key is a build with no rule in it.
        Assert.Empty(KurageMemory.Snapshot(Seat.Klee().Player));
    }

    [Fact]
    public void The_snapshot_carries_every_field_the_bridge_contract_names()
    {
        KurageMemory.ResetForCombat();
        var kokomi = Seat.Kokomi().WithCombatState();
        var snapshot = KurageMemory.Snapshot(kokomi.Player);

        foreach (var key in new[]
                 {
                     "bank", "front_price", "blocked", "fires_next", "empty",
                     "summon", "base_kit", "pulse_kind", "pulse_amount",
                     "pulse_unit", "reading", "queue",
                 })
        {
            Assert.True(snapshot.ContainsKey(key),
                        $"the bridge reads `{key}` and the snapshot omits it");
        }
        // front_price is NULL on an empty queue, not zero: "no ceiling" and
        // "a ceiling of nothing" are different facts on the wire.
        Assert.Null(snapshot["front_price"]);
        Assert.Equal(true, snapshot["empty"]);
        Assert.Equal(false, snapshot["blocked"]);
    }

    // --- STRUCTURAL: the fire (see the class doc for why) ----------------

    [Fact]
    public void The_fire_spends_the_price_plays_the_card_and_removes_it()
    {
        var calls = Il.Calls(Il.Method("KurageMemory", "Fire"));

        // The bank pays through the SAME spender a printed Charge cost uses.
        Assert.Contains("KokomiResources.SpendCharge", calls);
        // The game's own free-play door, so a copy fires the real card-played
        // hooks and every ordinary "when you play a Companion" effect.
        Assert.Contains("CardCmd.AutoPlay", calls);
        // "Then remove that Memory from combat", taken literally.
        Assert.Contains("CardPileCmd.RemoveFromCombat", calls);
        // A copy is NOT an Exhaust event, so the keyword comes off before the
        // play rather than the funnel carrying a special case.
        Assert.Contains("CardCmd.RemoveKeyword", calls);
        // ...and the fire never exhausts anything itself.
        Assert.DoesNotContain("CardCmd.Exhaust", calls);
    }

    [Fact]
    public void The_fire_asks_one_predicate_whether_the_jellyfish_is_here()
    {
        // [USER] 2026-08-29 makes the Bake-Kurage base kit and ALWAYS ON. That
        // swap has to be one method: if the fire ever learns to read the
        // summon power directly, the always-on change stops being local and
        // this pin is what says so.
        var calls = Il.Calls(Il.Method("KurageMemory", "Fire"));

        Assert.Contains("KurageMemory.SummonIsFielded", calls);
    }

    // --- v4 BASE KIT: STRUCTURAL, for the same boundary reason -----------

    [Fact]
    public void The_install_is_not_a_summon_and_is_idempotent()
    {
        // sec.12.6 ITEM 4: nothing summoned the jellyfish and no card paid for
        // it, so a listener counting summons must not see one. The install goes
        // to the game's own PowerCmd.Apply and deliberately NOT through the
        // mod's summon wrapper, which carries that meaning.
        var calls = Il.Calls(Il.Method("KurageMemory", "Install"));

        Assert.Contains("PowerCmd.Apply", calls);
        Assert.DoesNotContain("KurageSummon.Field", calls);
        // Idempotent: it asks the ONE predicate first, so a second call and a
        // belt call at turn start both cost a read and nothing else.
        Assert.Contains("KurageMemory.SummonIsFielded", calls);
        // ITEM 2: nothing here starts or spends a countdown.
        Assert.DoesNotContain("PowerCmd.TickDownDuration", calls);
    }

    [Fact]
    public void The_pulse_never_ticks_a_duration_down()
    {
        // sec.12.6 ITEMS 2 and 3: the jellyfish never expires, so the turn-end
        // pulse must not spend a turn of anything. The shipped pulse does tick;
        // the memory branch returns before reaching it, and this is the pin
        // that says the memory pulse itself carries no countdown either.
        var calls = Il.Calls(Il.Method("KurageMemory", "Pulse"));

        Assert.DoesNotContain("PowerCmd.TickDownDuration", calls);
    }

    [Fact]
    public void The_install_runs_before_the_first_turn_opens()
    {
        // sec.12.6 ITEM 1. `BeforeCombatStart` and NOT
        // `AfterCreatureAddedToCombat`: the game raises the latter from
        // CreatureCmd.AddToCombat, i.e. for creatures SPAWNED into a live
        // combat, and the seats never pass through it. CombatManager raises
        // BeforeCombatStart after every creature is in and immediately before
        // StartTurn. This pin is what stops that repair being undone.
        var hook = typeof(KokomiResourceHooks).GetMethod(
            "BeforeCombatStart", HeadlessGame.All);

        Assert.NotNull(hook);
        Assert.Contains("KurageMemory.InstallAll", Il.Calls(hook));
    }

    [Fact]
    public void The_install_covers_every_seat_not_only_the_local_one()
    {
        // Co-op is two players and a second Kokomi is entitled to her own
        // jellyfish. The walk is over the combat's own seat list.
        var calls = Il.Calls(Il.Method("KurageMemory", "InstallAll"));

        Assert.Contains("KurageMemory.Install", calls);
    }

    [Fact]
    public void The_ward_is_paid_by_the_fire_and_not_by_the_pulse()
    {
        // sec.12.6 ITEM 13 / sec.12.4 pick 4, RULED. The Oath keys to a MEMORY
        // PLAY, so a blocked or empty memory pays nothing -- both of those
        // return long before the payment line -- and the pulse no longer grants
        // it. With the flag off the ward still rides the shipped pulse, which
        // is code this file does not exist alongside.
        var fire = Il.Calls(Il.Method("KurageMemory", "Fire"));
        var pulse = Il.Calls(Il.Method("KurageMemory", "Pulse"));

        Assert.Contains("KurageWardPower.WardAmount", fire);
        Assert.DoesNotContain("KurageWardPower.WardAmount", pulse);
    }

    [Fact]
    public void The_prototype_oath_gets_its_own_face_text()
    {
        // sec.12.6 ITEM 14. gen_klee_cards renders a Power's description per
        // POWER ID, so the generated prototype face carries the SHIPPED Oath's
        // pulse wording and is wrong. The mirror overrides that one key and
        // nothing else; the shipped face must not move.
        // `EB-194`: the merge moved OUT of InjectLocStrings and into the
        // off-pool builder. The string pin follows it; the call-site pin below
        // is what keeps it from moving back.
        var strings = Il.Strings(
            Il.Method("KokomiOffPoolCards", "InjectPrototypeLoc"));

        Assert.Contains(strings, s =>
            s.Contains("plays a card from its memory")
            && s.Contains("Block"));
        // The override is keyed off the LIVE model's entry (R4's rule), never
        // a hardcoded id.
        Assert.DoesNotContain(strings, s =>
            s.Contains("PROTO_KURAGES_OATH_MEMORY"));
    }

    [Fact]
    public void Loc_injection_never_touches_the_prototype_surface()
    {
        // `EB-194` LOCK (a). InjectLocStrings is a Harmony postfix on
        // LocManager.Initialize, so it runs during boot, BEFORE any mod card
        // model exists -- the generated rows are `autoAdd: false` and are
        // constructed at pool-build time. Reaching into the prototype surface
        // from there forced PrototypeRoster's initializer against an empty
        // ModelDb, ModelDb.Card<T>() threw KeyNotFoundException, and a static
        // constructor that throws POISONS ITS TYPE for the process: the
        // self-check aborted and GenerateAllCards rethrew at StartRun, so NO
        // run of ANY character could start on a +proto build.
        //
        // The rule this pins is a TIMING rule, and the only structural shadow
        // it casts is the call itself. So: the loc postfix may name neither
        // seam, in either build. It is a compile-time-shaped guard on a
        // runtime-ordering bug, which is the honest amount this test can do --
        // the bite-check in KleeTests/Prototype is what proves the ordering.
        var calls = Il.Calls(Il.Method("KleeMod", "InjectLocStrings"));

        Assert.DoesNotContain(calls, c => c.Contains("PrototypeRoster"));
        Assert.DoesNotContain(calls, c => c.Contains("PrototypeCards"));
    }

    [Fact]
    public void The_prototype_roster_survives_a_touch_with_an_empty_model_db()
    {
        // `EB-194` LOCK (b), the bite-check: ask the roster for a character
        // while ModelDb holds no prototype models -- exactly the state boot was
        // in -- and it must not throw, and must not poison itself for the ask
        // that follows. Before the laziness fix the eager static dictionary
        // resolved EVERY character's rows in the type initializer, so this threw
        // TypeInitializationException on the first line and again on the second.
        //
        // This is a HEADLESS test: nothing here builds a card, so ModelDb is
        // empty by construction and no game bring-up is needed.
        var furina = Record.Exception(() => PrototypeCards.For("furina"));
        Assert.Null(furina);

        // The type is still usable after the touch above -- a poisoned type
        // would rethrow its cached TypeInitializationException here.
        var again = Record.Exception(() => PrototypeCards.For("furina"));
        Assert.Null(again);

        // An unknown character is empty, not a throw.
        Assert.Empty(PrototypeCards.For("nobody"));
    }

    [Fact]
    public void The_shipped_oath_is_swapped_off_every_offer_surface()
    {
        // sec.12.6 ITEM 15. FilterThroughEpochs feeds GetUnlockedCards, which
        // is the sole path into reward rolls, the shop and transforms, so a
        // substitution there covers every offer surface by construction. The
        // shipped Oath stays IN the pool (Pool must resolve or a held copy
        // throws on draw) and is only unofferable.
        var calls = Il.Calls(Il.Method("KokomiCardPool", "FilterThroughEpochs"));

        Assert.Contains("KurageMemory.SwapOfferedOath", calls);
    }

    [Fact]
    public void The_swap_removes_the_shipped_row_and_adds_the_prototype_one()
    {
        // A SUBSTITUTION, not an addition: same rarity, same cost, same type,
        // therefore the same weight in every roll. A pure add would make the
        // Oath twice as likely and a pure remove would take a Common out of
        // her pool.
        var calls = Il.Calls(Il.Method("KurageMemory", "SwapOfferedOath"));

        Assert.Contains("PrototypeCards.For", calls);
    }

    [Fact]
    public void The_starter_swap_happens_at_exactly_one_seam()
    {
        // sec.12.6 ITEM 5: one seam, so the mod and the sim cannot disagree
        // about what she opens with. If a second site ever swaps a starter
        // card, this pin does not catch it -- but the authored deck reaching
        // the seam at all is what makes there be only one.
        var calls = Il.Calls(Il.Method("Kokomi", "get_StartingDeck"));

        Assert.Contains("KurageMemory.StarterSlotEleven", calls);
    }

    // ------------------------------------------------ the affordability run --
    //
    // THE ONE DISPLAY FACT WITH NO RESOLUTION-SIDE EXPRESSION TO BORROW, and
    // therefore the one that needed a function and a fixture of its own
    // (review/active/kokomi-kurage-memory-2026-08-29.md sec.14.4). The engine
    // only ever fires ONE memory, so nothing in it asks how far down the queue
    // the bank reaches -- but the pile view the memory card opens has to answer
    // exactly that, front first, red at the shortfall and red for everything
    // behind it ([USER]: "also red").
    //
    // REACHABLE HERE, unlike almost everything else in this file, because it is
    // PURE: prices in, states out. No CombatState, no card play, no pile move,
    // no Godot. The sim twin is `tier0/engine/effects.py kurage_affordability`.

    /// <summary>Prices to an Entry list. Every Entry field but the price is
    /// irrelevant to the run and is filled with the least interesting legal
    /// value, so a reader is not invited to think one of them matters.</summary>
    private static IReadOnlyList<KurageMemory.Entry> Queue(params int[] prices)
    {
        var entries = new List<KurageMemory.Entry>();
        foreach (var price in prices)
        {
            entries.Add(new KurageMemory.Entry
            {
                Card = new ProbeFace(),
                Name = "probe",
                Cost = price / KurageMemory.KurageMemoryLaw.CostPerEnergy,
                Price = price,
                Target = null,
                Ephemeral = false,
                Rule = "exhaust",
            });
        }
        return entries;
    }

    private static string[] Wire(IReadOnlyList<KurageMemory.EntryState> states)
    {
        var wire = new string[states.Count];
        for (var i = 0; i < states.Count; i++)
        {
            wire[i] = KurageMemory.Wire(states[i]);
        }
        return wire;
    }

    [Fact]
    public void The_run_walks_the_queue_and_holds_everything_behind_the_shortfall()
    {
        // sec.14.3's mock, worked: bank 4 over 3 / free / 3 / free. The free
        // card does not move the bank, so the first three fit and the second 3
        // does not -- and the FREE card behind it is HELD, which is the case a
        // naive per-card `bank >= price` test gets wrong and the reason this is
        // a run rather than a comparison.
        var states = KurageMemory.Affordability(Queue(3, 0, 3, 0), bank: 4);

        Assert.Equal(new[] { "payable", "payable", "runs_out", "held" },
                     Wire(states));
        Assert.Equal(2, KurageMemory.RunOutIndex(states));
    }

    [Fact]
    public void A_dry_bank_runs_out_at_the_front_and_holds_the_free_card()
    {
        var states = KurageMemory.Affordability(Queue(3, 0), bank: 0);

        Assert.Equal(new[] { "runs_out", "held" }, Wire(states));
        Assert.Equal(0, KurageMemory.RunOutIndex(states));
    }

    [Fact]
    public void A_free_front_is_payable_and_the_run_stops_behind_it()
    {
        // `EB-198`'s own frame. The strip printed this state as "Charge 1 / 0"
        // and the blind tester read it as a fraction over a zero denominator.
        // Free is free: the front is PAYABLE and the 3 behind it is where the
        // Charge stops.
        var states = KurageMemory.Affordability(Queue(0, 3), bank: 1);

        Assert.Equal(new[] { "payable", "runs_out" }, Wire(states));
        Assert.Equal(1, KurageMemory.RunOutIndex(states));
    }

    [Fact]
    public void An_empty_memory_has_no_entries_and_no_shortfall()
    {
        // AN EMPTY MEMORY IS NOT A BLOCKED ONE -- the same distinction the
        // reading has always had to keep, now on the projection too. -1 rather
        // than 0: there is no entry the bank failed to reach.
        var states = KurageMemory.Affordability(Queue(), bank: 0);

        Assert.Empty(states);
        Assert.Equal(-1, KurageMemory.RunOutIndex(states));
    }

    [Fact]
    public void The_run_matches_the_sims_table_case_for_case()
    {
        // THE PARITY CLAIM. `docs/kurage-affordability-vectors.json` is derived
        // from the sim by `tier0/tests/test_kurage_affordability.py`, which also
        // asserts the file on disk IS the sim's answer. This runs the C#
        // arithmetic against the same file, so the two implementations cannot
        // drift without one of the two suites going red.
        var path = FixturePath("docs/kurage-affordability-vectors.json");
        using var doc = JsonDocument.Parse(File.ReadAllText(path));

        var cases = 0;
        foreach (var row in doc.RootElement.EnumerateArray())
        {
            cases++;
            var bank = row.GetProperty("bank").GetInt32();
            var prices = new List<int>();
            foreach (var price in row.GetProperty("prices").EnumerateArray())
            {
                prices.Add(price.GetInt32());
            }

            var expected = new List<string>();
            foreach (var state in row.GetProperty("states").EnumerateArray())
            {
                expected.Add(state.GetString()!);
            }

            var states = KurageMemory.Affordability(prices, bank);
            Assert.Equal(expected.ToArray(), Wire(states));
            Assert.Equal(row.GetProperty("run_out_index").GetInt32(),
                         KurageMemory.RunOutIndex(states));
        }

        // A fixture that silently emptied would pass every assertion above.
        Assert.True(cases >= 7, "only " + cases + " parity cases were read");
    }

    /// <summary>Walk up from the test binary to the repo root, which is the
    /// directory that carries the fixture. There is no build-time copy of it: a
    /// stale copy beside the dll is exactly the drift this file prevents.</summary>
    private static string FixturePath(string relative)
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var candidate = Path.Combine(
                dir.FullName,
                relative.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(candidate))
            {
                return candidate;
            }
            dir = dir.Parent;
        }

        throw new FileNotFoundException(
            "no " + relative + " above " + AppContext.BaseDirectory);
    }

    // ------------------------------------------------ the element, in part --

    [Fact]
    public void The_memory_card_resolves_the_local_seat_and_only_the_local_seat()
    {
        // STRUCTURAL, and it has to be: the element is a Godot `Control` under
        // `%CombatUi` and no test here may touch a Godot object, so "it draws
        // nothing for a partner" is NOT assertable headless. What IS assertable
        // is that both of its entry points go through `LocalContext` rather than
        // looping `state.Players` the way `GaugeBridge`, `SalonVisualsBridge`
        // and `TurnEndPreviewBridge` deliberately do -- which is the whole of
        // the co-op behaviour [USER] signed off ("Local only is fine (partner
        // doesn't need to see the queue)").
        //
        // THE LIVE HALF IS OWED: that a partner's screen carries no element at
        // all is `EB-198`'s live acceptance on a `+proto` dev deploy, not a pin.
        Assert.Contains("LocalContext.GetMe",
                        Il.Calls(Il.Method("KurageMemoryCard", "Setup")));
        Assert.Contains("LocalContext.IsMe",
                        Il.Calls(Il.Method("KurageMemoryCard", "Refresh")));
    }

    [Fact]
    public void The_element_draws_the_projection_rather_than_re_deriving_it()
    {
        // ONE EXPRESSION OF THE RULE PER ENGINE. If the drawing code ever
        // inlines the subtraction, the pile view and the wire snapshot can
        // disagree about where the Charge runs out and nothing catches it.
        Assert.Contains("KurageMemory.Affordability",
                        Il.Calls(Il.Method("KurageMemoryCard", "OpenQueue")));
        Assert.Contains("KurageMemory.Affordability",
                        Il.Calls(Il.Method("KurageMemory", "Snapshot")));
    }

    // ------------------------------------------- the pile ring (`EB-201`) --
    //
    // WHY THESE ARE STRUCTURAL AND ONE IS A VALUE. The ring is a Godot `Panel`
    // parented to a pooled `NCard` inside the base game's pile grid: nothing
    // headless can see it drawn. What CAN be reached is the one thing that was
    // actually wrong -- its RECT -- because that is arithmetic on a base-game
    // constant, and the two calls that put it on screen.

    [Fact]
    public void The_pile_ring_takes_its_rect_from_the_card_face_not_an_anchor()
    {
        // EB-201's cause. The first cut anchored the ring `FullRect` to the
        // `NCard`, whose own Control rect is NOT the card face: the holder pins
        // `CardNode.Position` to zero and the grid places holders at the CELL
        // CENTRE, and `NCard.GetCurrentSize` returns the CONSTANT
        // `defaultSize * Scale` rather than reading `Size`. The preset
        // therefore produced a 0x0 Panel -- correctly parented, correctly
        // coloured, zero pixels wide. This pin FAILS on that cut, where
        // `RingRect` does not exist at all.
        Assert.Contains("KurageMemoryPileRing.RectFor",
                        Il.Calls(Il.Method("KurageMemoryPileRing", "RingRect")));
    }

    [Fact]
    public void The_pile_ring_is_the_card_face_centred_on_the_node_origin()
    {
        // The value, not just the shape: 300x422 (`NCard.defaultSize`) with its
        // top-left at minus half of that, because the face is drawn centred on
        // the node's origin. Neutering the offset back to `Vector2.Zero` -- the
        // top-left rect an anchor preset would have produced -- fails here.
        // `RectFor` rather than `RingRect`: reading `NCard.defaultSize` runs
        // NCard's static constructor, which builds `StringName`s through the
        // native library and kills the test host (0xC0000005). The split is
        // what makes the value reachable at all.
        var rect = (Rect2)Il.Method("KurageMemoryPileRing", "RectFor")
                            .Invoke(null, new object[] { new Vector2(300f, 422f) })!;

        Assert.Equal(300f, rect.Size.X);
        Assert.Equal(422f, rect.Size.Y);
        Assert.Equal(-150f, rect.Position.X);
        Assert.Equal(-211f, rect.Position.Y);
    }

    [Fact]
    public void The_pile_ring_sizes_itself_and_moves_over_the_face()
    {
        // Both halves of the repair, at the one seam that applies them. The
        // rect is re-applied every paint because a pooled `NCard` arrives
        // carrying whatever the last screen left on it, and the ring is moved
        // to LAST CHILD so it draws over `%CardContainer` rather than under it.
        var calls = Il.Calls(Il.Method("KurageMemoryPileRing", "Paint"));

        Assert.Contains("KurageMemoryPileRing.RingRect", calls);
        Assert.Contains("Control.set_Size", calls);
        Assert.Contains("GodotTreeExtensions.MoveChildSafely", calls);
    }

    [Fact]
    public void The_pile_ring_still_arms_off_the_redraw_the_game_already_does()
    {
        // NOT re-pointed. `NCardGrid.InitGrid` calls `nCard.UpdateVisuals` on
        // every entry it builds and `NCardHolder.ReassignToCard` calls it again
        // on the scrolled-window reuse path; `UpdateVisuals` calls
        // `UpdateStarCostVisuals` unconditionally. The hook was never the
        // defect, so this pin exists to catch a later "fix" that moves it.
        Assert.Contains(
            "KurageMemoryPileRing.Paint",
            Il.Calls(Il.Method(
                "NCard_UpdateStarCostVisuals_KurageQueueRing_Patch",
                "Postfix")));
    }
}
