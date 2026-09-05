using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KLEE OVERHAUL, SLICE ONE: rules 1 to 7 of the ruled brief
/// (`review/active/klee-brief-2026-09-01.md` sec.3), and the flag-off pin.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, said once. The rules were written
/// with the shipped Bomb's own split -- the DECISIONS are pure (growth, the
/// take, the Mine split, the single removal, the counters, the doubling), and
/// everything past them needs a live <c>CombatState</c>, which the headless
/// boundary does not reach (README, "The headless boundary": <c>PowerCmd</c>,
/// <c>ElementalHit.Deal</c> and a card PLAY are all outside it). So every
/// assertion below is either a real call on a real pile, or a labelled
/// structural pin read off the compiled method -- never a mock's arithmetic.
///
/// STILL PLAY-DERIVED, narrowed rather than closed: the Pyro hit actually
/// landing, the aura it consumes, the badge redrawing, and the enemy attack
/// that a Mine answers. Those need a combat, and none of them needs a decision.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulRuleTests
{
    private static MethodBase Method(string name) =>
        typeof(ProtoBombPower).GetMethod(
            name, HeadlessGame.All)
        ?? throw new System.InvalidOperationException(
            $"ProtoBombPower.{name} is gone -- the rule moved under this pin.");

    // ---- THE FLAG, OFF --------------------------------------------------

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST (2026-09-02).
    //
    // `dotnet test -p:KleeOverhaul=true` defines `KLEE_OVERHAUL`, which is what MOVES
    // `DefaultEnabled` -- the exact value this pin asserts. So under that
    // property the pin cannot say anything true: green would mean the property
    // did nothing, and red is the property working. It is skipped there rather
    // than left to fail, because a red that means "the switch works" trains
    // everyone to ignore reds.
    //
    // ARM PROPERTIES ARE DEPLOY-LINE ONLY. The supported test configurations
    // are `dotnet test` and `dotnet test -p:PrototypeCards=true`, and this pin
    // runs in both -- which is where the acceptance condition has to hold.
    // docs/current/operations/prototype.md carries the rule.
#if KLEE_OVERHAUL
    [Fact(Skip = "-p:KleeOverhaul=true moves KleeOverhaul.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        // The acceptance condition, and everything else here only matters
        // while it holds. `Enabled` is settable so a pin can exercise both
        // sides in one build; nothing in the mod ever writes it.
        Assert.False(KleeOverhaul.DefaultEnabled);
        Assert.Equal(KleeOverhaul.DefaultEnabled, KleeOverhaul.Enabled);
    }

    [Fact]
    public void The_three_wiring_seams_read_the_flag_and_nothing_else()
    {
        // FLAG OFF IS BYTE-IDENTICAL, pinned where it is decided rather than
        // asserted in prose. Each seam is one `if` on the same property, so
        // with the arm off `Klee.StartingDeck` falls through to the template
        // the Sparks arm owns and `KleeCardPool.FilterThroughEpochs` falls
        // through to the shipped off-pool filter.
        var deck = typeof(global::KleeMod.Klee)
            .GetProperty("StartingDeck", HeadlessGame.All)!.GetGetMethod(true)!;
        Assert.Contains("KleeOverhaul.get_Enabled", Il.Calls(deck));
        Assert.Contains("KleeOverhaulRoster.StartingDeck", Il.Calls(deck));

        var filter = typeof(global::KleeMod.KleeCardPool)
            .GetMethod("FilterThroughEpochs", HeadlessGame.All)!;
        Assert.Contains("KleeOverhaul.get_Enabled", Il.Calls(filter));
        Assert.Contains("KleeOverhaulRoster.OfferablePool", Il.Calls(filter));

        // THE THIRD, ADDED BY `EB-351`: which pair of basics is hers when a
        // base-game effect asks the CHARACTER rather than reading the deck.
        // Large Capsule reads `CardPool.AllCards`, which the second seam is
        // never applied to, so it was handing an arm run her two SHIPPED
        // basics. `ArmStarterBasicsTests` holds the rest of it.
        var basics = Il.Calls(Il.Method("ArmStarterBasics", "StrikeFor"));
        Assert.Contains("KleeOverhaul.get_Enabled", basics);
        Assert.Contains("KleeOverhaulRoster.StarterStrike", basics);
    }

    [Fact]
    public void The_shipped_bomb_is_not_edited_by_this_arm()
    {
        // The whole reason the overhaul is a SECOND power. If this ever fails,
        // the arm has reached into the file whose per-placer instancing,
        // suppression arbiter and death-teardown compensation are the mod's
        // most load-bearing co-op work.
        var shipped = typeof(BombPower).GetMethods(HeadlessGame.All)
            .Where(m => m.DeclaringType == typeof(BombPower))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.DoesNotContain(shipped, c => c.StartsWith("ProtoBombPower."));
        Assert.DoesNotContain(shipped, c => c.StartsWith("KleeOverhaul"));
    }

    // ---- RULE 1: the Bomb grows, and never goes off by itself ------------

    [Fact]
    public void Rule1_every_charge_grows_by_the_same_amount()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(8));

        pile.GrowBy(KleeOverhaulLaw.BombGrowth);

        Assert.Equal(new[] { 9, 12 }, pile.Charges.Select(c => c.Size));
        Assert.Equal(21, pile.TotalSize);
    }

    [Fact]
    public void Rule1_growth_is_four_by_default()
    {
        // FOUR: the round-5 packet raised it from 3 to 5 and [USER] read 5
        // back down the same day ("growth 5 is likely too much").
        var klee = Seat.Klee();
        Assert.Equal(4, KleeOverhaulLaw.BombGrowth);
        Assert.Equal(KleeOverhaulLaw.BombGrowth,
                     GrowthFor(klee.Creature));
    }

    [Fact]
    public void Rule1_the_workshop_adds_one_more_per_stack()
    {
        var klee = Seat.Klee().WithPower<ExplosivesWorkshopGrowthPower>(1);
        Assert.Equal(KleeOverhaulLaw.BombGrowth + KleeOverhaulLaw.WorkshopGrowth,
                     GrowthFor(klee.Creature));

        var stacked = Seat.Klee().WithPower<ExplosivesWorkshopGrowthPower>(3);
        Assert.Equal(
            KleeOverhaulLaw.BombGrowth + 3 * KleeOverhaulLaw.WorkshopGrowth,
            GrowthFor(stacked.Creature));
    }

    [Fact]
    public void Rule1_alices_recipe_doubles_the_turns_growth_workshop_included()
    {
        // "Your Bombs grow TWICE each turn" (balance pass 2026-09-02) --
        // multiply, and multiply what the Workshop already added, which is the
        // only reading that leaves both printed faces true. The row used to
        // read "grow by 4 instead of 3", a Rare a second Workshop beat.
        var alice = Seat.Klee().WithPower<AlicesRecipePower>(1);
        Assert.Equal(KleeOverhaulLaw.BombGrowth * KleeOverhaulLaw.AliceMultiplier,
                     GrowthFor(alice.Creature));

        var both = Seat.Klee()
            .WithPower<AlicesRecipePower>(1)
            .WithPower<ExplosivesWorkshopGrowthPower>(1);
        Assert.Equal(
            (KleeOverhaulLaw.BombGrowth + KleeOverhaulLaw.WorkshopGrowth)
                * KleeOverhaulLaw.AliceMultiplier,
            GrowthFor(both.Creature));
    }

    [Fact]
    public void Rule1_the_turn_start_hook_grows_and_does_not_detonate()
    {
        // RULE 7, at the one place the shipped Bomb fires by itself. The
        // overhaul's hook must reach `GrowBy` and must NOT reach anything that
        // deals damage. Structural: running the hook needs a combat.
        var hook = Method("BeforeSideTurnStart");
        var calls = Il.Calls(hook);
        Assert.Contains("ProtoBombPower.GrowBy", calls);
        Assert.Contains("ProtoBombPower.GrowthFor", calls);
        Assert.DoesNotContain(calls, c => c.StartsWith("ElementalHit."));
        Assert.DoesNotContain(calls, c => c.Contains("Explode"));
    }

    // ---- RULE 2: Set off, one at a time, before the card's own damage ----

    [Fact]
    public void Rule2_the_pile_is_taken_whole_before_anything_resolves()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6, IsMine: true));

        var taken = pile.TakeAll();

        Assert.NotNull(taken);
        Assert.Equal(2, taken!.Count);
        Assert.Equal(new[] { 4, 6 }, taken.Select(c => c.Size));
        // Emptied FIRST, which is what stops a kill mid-payload re-entering
        // the pile (the shipped Bomb's EB-138 discipline, inherited).
        Assert.Empty(pile.Charges);
        Assert.Equal(0, pile.TotalSize);
        Assert.Null(pile.TakeAll());
    }

    [Fact]
    public void Rule2_set_off_explodes_one_at_a_time_and_then_the_card_hits()
    {
        // THE ORDER IS THE RULE. `SetOffAimed` must resolve the explosions
        // through `SetOff` BEFORE it deals the card's own damage; the call
        // SEQUENCE is what says so, and it is the whole of rule 2's second
        // sentence. Structural: both halves need a combat.
        var seq = Il.CallSequence(Method("SetOffAimed")).ToList();
        var setOff = seq.FindIndex(c => c.EndsWith("SetOff"));
        var hit = seq.FindIndex(c => c.EndsWith("DealCardDamage"));
        Assert.True(setOff >= 0 && hit >= 0, string.Join(", ", seq));
        Assert.True(setOff < hit,
            "the card's own damage must land AFTER every Bomb on the target "
            + "has gone off: " + string.Join(", ", seq));

        // One at a time: SetOff loops the taken charges and calls Explode per
        // charge rather than summing them into one hit.
        Assert.Contains("ProtoBombPower.Explode", Il.Calls(Method("SetOff")));
    }

    [Fact]
    public void Rule2_a_random_target_set_off_re_rolls_per_hit()
    {
        // The rule's last sentence: "For random-target Attacks, per target
        // hit." So the roll, the Set off and the hit are all inside the loop --
        // four hits is four Set offs, not one Set off and four hits.
        var seq = Il.CallSequence(Method("SetOffRandom")).ToList();
        Assert.Contains(seq, c => c.Contains("NextItem"));
        Assert.Contains(seq, c => c.EndsWith("SetOff"));
        Assert.Contains(seq, c => c.EndsWith("DealCardDamage"));
    }

    // ---- RULE 3: the Jump -----------------------------------------------

    [Fact]
    public void Rule3_a_bomb_whose_enemy_died_moves_at_its_current_size()
    {
        // A jump is a MOVE: `JumpCharges` re-places each charge through the
        // one `Place` every other source uses, so the size, the Mine flag and
        // the payload all travel and the new pile is registered like any
        // other. Structural: placing needs a combat.
        var calls = Il.Calls(Method("JumpCharges"));
        Assert.Contains("ProtoBombPower.Place", calls);
        Assert.DoesNotContain(calls, c => c.StartsWith("ElementalHit."));
    }

    [Fact]
    public void Rule3_set_off_jumps_the_charges_behind_a_kill()
    {
        // The brief's own worked example: "The second of three Bombs killed
        // the enemy: the third jumps." So the corpse test is read PER CHARGE
        // inside SetOff's loop, and the remainder goes to JumpCharges.
        var calls = Il.Calls(Method("SetOff"));
        Assert.Contains("ProtoBombPower.JumpCharges", calls);
        Assert.Contains("Creature.get_IsDead", calls);
    }

    [Fact]
    public void Rule3_a_death_this_arm_did_not_cause_is_swept()
    {
        // "A partner or a poison killed the enemy: all of them jump." The
        // game strips a corpse's powers inline, so the sweep reads the arm's
        // own register of live piles rather than the board.
        var calls = Il.Calls(Method("SweepJumps"));
        Assert.Contains("Register.Claim", calls);
        Assert.Contains("ProtoBombPower.JumpCharges", calls);
    }

    // ---- RULE 4: one Spark per explosion, and no other source ------------

    [Fact]
    public void Rule4_the_spark_comes_off_the_explosion_bus()
    {
        // The relic IS the rule (the brief sec.8), so the grant hangs on the
        // arm's bus rather than on a card. One event per explosion, so a
        // three-Bomb Set off banks three.
        var relic = typeof(global::KleeMod.Relics.PoundingSurprise)
            .GetMethod("OnBombExploded", HeadlessGame.All)!;
        var calls = Il.Calls(relic);
        Assert.Contains("SparkPower.Gain", calls);
        Assert.Contains("KleeOverhaul.get_Enabled", calls);

        Assert.Contains("ProtoBombPower.NotifyExplosionListeners",
                        Il.Calls(Method("Explode")));
        Assert.Equal(1, KleeOverhaulLaw.SparkPerExplosion);
    }

    /// <summary>
    /// THE POOL PASS's one named exception (`EB-491`, Flash Point). Every
    /// other card-borne Spark grant is still a finding.
    /// </summary>
    private static readonly string[] SparkMintersAllowed = { "ProtoKoFlashPoint" };

    [Fact]
    public void Rule4_no_slice_card_mints_a_spark_except_the_named_one()
    {
        // "Under this flag Sparks come ONLY from explosions." Every generated
        // slice card is swept, so a row that printed `gain_spark` fails here
        // rather than quietly opening a second income.
        //
        // ONE ROW IS NAMED SINCE THE POOL PASS (2026-09-05, `EB-491`), and it
        // is named rather than excused: Flash Point pays "gain 1 Spark and
        // draw 1 card" and pays it ONLY when a Bomb triggered an Elemental
        // Reaction this turn, so the income is still keyed to an explosion --
        // it is the rider Catalytic Converter's Power already prints, bought
        // on a card instead of on a Power. The list is the exception's whole
        // record: a SECOND row minting Sparks fails here, which is the tooth
        // this test was written for.
        var minters = typeof(ProtoBombPower).Assembly.GetTypes()
            .Where(t => t.Namespace == "KleeMod.Cards.Prototype.Generated"
                        && t.Name.StartsWith("ProtoKo"))
            .SelectMany(t => t.GetMethods(HeadlessGame.All)
                              .Where(m => m.DeclaringType == t))
            .Where(m => Il.Calls(m).Contains("SparkPower.Gain"))
            .Select(m => m.DeclaringType!.Name)
            .Distinct()
            .ToList();
        Assert.Equal(SparkMintersAllowed, minters);
    }

    [Fact]
    public void Rule4_the_upgraded_relic_keeps_the_rate_and_loses_the_windfall()
    {
        // An act-2 Touch of Orobas must not take the arm's only income away,
        // and must not hand out a bank before any Bomb has gone off.
        var frags = typeof(global::KleeMod.Relics.ExplosiveFrags);
        Assert.Contains("SparkPower.Gain",
            Il.Calls(frags.GetMethod("OnBombExploded", HeadlessGame.All)!));
        Assert.Contains("KleeOverhaul.get_Enabled",
            Il.Calls(frags.GetMethod("AfterPlayerTurnStart", HeadlessGame.All)!));
    }

    // ---- RULE 6: the Mine ------------------------------------------------

    [Fact]
    public void Rule6_only_the_mines_go_off_and_plain_bombs_stay()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true),
            new ProtoBombs.Charge(9),
            new ProtoBombs.Charge(6, IsMine: true));

        Assert.Equal(2, pile.MineCount);
        var mines = pile.TakeMines();

        Assert.NotNull(mines);
        Assert.Equal(new[] { 4, 6 }, mines!.Select(c => c.Size));
        Assert.Equal(new[] { 9 }, pile.Charges.Select(c => c.Size));
        Assert.Equal(0, pile.MineCount);
        Assert.Null(pile.TakeMines());
    }

    [Fact]
    public void Rule6_a_mine_grows_exactly_like_a_bomb()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true), new ProtoBombs.Charge(4));

        pile.GrowBy(KleeOverhaulLaw.BombGrowth);

        Assert.Equal(new[] { 8, 8 }, pile.Charges.Select(c => c.Size));
        Assert.True(pile.Charges[0].IsMine);
    }

    [Fact]
    public void Rule6_the_mine_fires_before_the_hit_lands()
    {
        // `BeforeDamageReceived` is the one pre-hit hook that carries a choice
        // context, and dealing damage needs one. The guards are the rule: this
        // enemy's own attack, on the Klee who placed the pile, and a real
        // Attack rather than a bomb's Unpowered hit. Structural: the hit needs
        // a combat.
        var hook = Method("BeforeDamageReceived");
        var calls = Il.Calls(hook);
        Assert.Contains("ProtoBombPower.TakeMines", calls);
        Assert.Contains("ProtoBombPower.Explode", calls);
        Assert.Contains(calls, c => c.Contains("IsPoweredAttack"));
    }

    // ---- THE PAYLOAD (Jumpy Dumpty) --------------------------------------

    [Fact]
    public void The_payload_rides_the_explosion_not_the_card()
    {
        // Which is the whole of what makes the starter's promise legible: the
        // Mines arrive when the big Bomb finally goes off, not when it was
        // planted. So `Explode` places them and the card does not.
        Assert.Contains("ProtoBombPower.Place", Il.Calls(Method("Explode")));

        var jumpy = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKoJumpyDumpty")!;
        var play = jumpy.GetMethod("OnPlay", HeadlessGame.All)!;
        var calls = Il.Calls(play);
        // R242: the plant is on the enemy you CHOOSE, so the one detonator can
        // line up with it. Draft 3 placed it at random, which made the
        // starter's whole plan a coin flip.
        Assert.Contains("ProtoBombPower.Place", calls);
        Assert.DoesNotContain(calls, c => c.Contains("PlaceOnRandom"));
        Assert.DoesNotContain(calls, c => c.Contains("PlaceOnAll"));
    }

    [Fact]
    public void The_payload_travels_with_the_charge_that_carries_it()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(8, PayloadMineAll: 3));

        var taken = pile.TakeAll()!;

        Assert.Equal(3, taken[0].PayloadMineAll);
        Assert.False(taken[0].IsMine);      // the CARRIER is a plain Bomb
    }

    [Fact]
    public void The_payload_survives_being_stacked_with_a_plain_bomb()
    {
        // `EB-395`. The round-10 seat planted Jumpy Dumpty, stacked a Pop!
        // Bomb on the same enemy, let both grow for two turns and set the
        // aggregate off at `Bomb 25 / Bombs here: 2` -- and reported no Mine
        // afterwards, where every single-Bomb Set off in the same run placed
        // one. Either the rider was lost in the stack or nothing printed that
        // it had fired.
        //
        // THIS IS THE FIRST HALF, and it is the half a headless pin can hold:
        // the charge list is a list, not a total, so a second charge beside
        // the carrier changes nothing about the carrier -- and NEITHER DOES
        // GROWTH, which is where a `new ProtoCharge(size + amount, isMine)`
        // would have dropped the payload field on the floor. `GrowBy` uses a
        // `with` expression, and this reads that back rather than trusting it.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(8, PayloadMineAll: 3),   // Jumpy Dumpty
            new ProtoBombs.Charge(5));                     // Pop!

        pile.GrowBy(KleeOverhaulLaw.BombGrowth);
        pile.GrowBy(KleeOverhaulLaw.BombGrowth);
        var taken = pile.TakeAll()!;

        Assert.Equal(2, taken.Count);
        Assert.Equal(8 + 2 * KleeOverhaulLaw.BombGrowth, taken[0].Size);
        Assert.Equal(3, taken[0].PayloadMineAll);
        Assert.Equal(0, taken[1].PayloadMineAll);
        // AND THE SECOND HALF, structurally: `SetOff` explodes the charges it
        // took ONE AT A TIME (`Explode` per charge, pinned above), and
        // `Explode` places the payload on every enemy -- so the carrier pays
        // whether it is alone on the pile or second in a stack of four. The
        // sim twin runs the whole board:
        // `test_the_payload_pays_from_inside_a_stacked_pile`.
        Assert.Contains("ProtoBombPower.Explode", Il.Calls(Method("SetOff")));
        Assert.Contains("ProtoBombPower.Place", Il.Calls(Method("Explode")));
    }

    [Fact]
    public void A_merge_carries_every_payload_it_moved()
    {
        // `EB-395`'s other named suspect: Careful Arrangement moves every Bomb
        // onto one enemy AS ONE Bomb, and a merge is a MOVE, so it loses
        // nothing -- the merged charge is a Mine if any part of it was, and it
        // carries the summed payload. Read off `MergeAllTo`'s own loop, which
        // is the only place in the arm that folds charges together.
        var il = Il.Calls(Method("MergeAllTo"));

        Assert.Contains("ProtoBombPower.Place", il);
        Assert.Contains("ProtoBombPower.TakeAll", il);
        // The three fields the fold must READ, off the compiled method that
        // folds them. A getter missing here is a rider deleted by a card whose
        // face says it only moves Bombs.
        Assert.Contains(il, c => c.Contains("get_PayloadMineAll"));
        Assert.Contains(il, c => c.Contains("get_IsMine"));
        Assert.Contains(il, c => c.Contains("get_Size"));
    }

    // ---- RULE 7: the two per-turn counters -------------------------------

    [Fact]
    public void Rule7_both_counters_are_written_at_one_site()
    {
        var ledger = NewLedger();

        ledger.NoteExplosion(reacted: false, damageDealt: 5);
        ledger.NoteExplosion(reacted: true, damageDealt: 7);

        Assert.Equal(2, ledger.SetOffThisTurn);
        Assert.Equal(1, ledger.ReactedThisTurn);
        Assert.Equal(12, ledger.DamageSetOffThisPlay);
    }

    [Fact]
    public void Rule7_grounded_reads_last_turns_count_and_the_turn_rolls()
    {
        var ledger = NewLedger();
        ledger.RollTo(1);
        ledger.NoteExplosion(reacted: false, damageDealt: 4);
        Assert.Equal(1, ledger.SetOffThisTurn);
        Assert.Equal(0, ledger.SetOffLastTurn);

        ledger.RollTo(2);
        Assert.Equal(0, ledger.SetOffThisTurn);
        Assert.Equal(1, ledger.SetOffLastTurn);      // Grounded stays quiet

        ledger.RollTo(3);
        Assert.Equal(0, ledger.SetOffLastTurn);      // Grounded pays
    }

    [Fact]
    public void Rule7_a_skipped_round_reports_an_honest_zero()
    {
        // The roll is on the round STAMP, so a jump of more than one round
        // means Klee had no turn in between and last turn's count is zero
        // rather than a stale number from three rounds ago.
        var ledger = NewLedger();
        ledger.RollTo(1);
        ledger.NoteExplosion(reacted: false, damageDealt: 4);
        ledger.RollTo(5);
        Assert.Equal(0, ledger.SetOffLastTurn);
    }

    // ---- EB-344 / R248: the held turn also grants a Spark ----------------

    [Fact]
    public void Grounded_pays_block_and_a_spark_behind_one_condition()
    {
        // STRUCTURAL (Il): the payout needs a live context -- both
        // `CreatureCmd.GainBlock` and `SparkPower.Gain` are outside the
        // headless boundary -- so what is read is the hook's own shape, which
        // is where the rule lives.
        //
        // ONE CONDITION, TWO PAYOUTS is the whole claim, and the ORDER is what
        // says it: the condition is read FIRST (the guard returns before
        // either grant), then the Block, then the Spark. A turn that fails it
        // therefore grants NEITHER, because there is one place to return from
        // and it is above both.
        //
        // `EB-516` MOVED WHAT THE GUARD READS and left the shape: it asked the
        // explosion ledger and now asks the BOARD, so the pin asks for
        // `ProtoBombPower.AnyPlacedBy` where it asked for the ledger, and adds
        // the ledger's ABSENCE -- reading both would be two conditions.
        var hook = typeof(GroundedPower)
            .GetMethod("AfterPlayerTurnStart", HeadlessGame.All)!;
        var sequence = Il.CallSequence(hook).ToList();

        var boardAt = sequence.FindIndex(c => c == "ProtoBombPower.AnyPlacedBy");
        var blockAt = sequence.FindIndex(c => c == "CreatureCmd.GainBlock");
        var sparkAt = sequence.FindIndex(c => c == "SparkPower.Gain");

        Assert.True(boardAt >= 0, "the guard reads the board");
        Assert.True(blockAt > boardAt, "the Block is behind the guard");
        Assert.True(sparkAt > blockAt, "the Spark is behind the same guard");

        // And the board is consulted ONCE, so there is no second reading of
        // "cooking" for the two halves to drift apart on -- and the explosion
        // ledger is not consulted at all.
        Assert.Single(sequence, c => c == "ProtoBombPower.AnyPlacedBy");
        Assert.DoesNotContain("KleeOverhaulLedger.For", sequence);
    }

    [Fact]
    public void Groundeds_spark_is_the_kits_rate_and_the_upgrade_is_the_block()
    {
        // The number's home. `Amount` is the BLOCK and the row's upgrade moves
        // it (`{power_amount: +2}`, 6 -> 8); the Spark is 1 at both levels, so
        // it is a constant mirrored against tier0 rather than a second reading
        // of the stack.
        Assert.Equal(1, KleeOverhaulLaw.GroundedSpark);

        var upgrade = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKoGrounded")!
            .GetMethod("OnUpgrade", HeadlessGame.All)!;
        var moved = Il.Strings(upgrade);
        Assert.Contains("PowerAmount", moved);
        Assert.Single(moved);

        // The face states both halves, and the Spark numeral comes from the
        // constant rather than a typed literal (`EB-89`).
        var face = new GroundedPower().Localization!
            .First(r => r.Item1 == "description").Item2;
        Assert.Contains("[blue]{Amount}[/blue] [gold]Block[/gold]", face);
        Assert.Contains("[blue]" + KleeOverhaulLaw.GroundedSpark
                        + "[/blue] [gold]Spark[/gold]", face);
    }

    [Fact]
    public void The_per_play_size_memory_is_opened_by_the_card_that_reads_it()
    {
        var ledger = NewLedger();
        ledger.NoteExplosion(reacted: false, damageDealt: 9);
        ledger.BeginPlay();
        Assert.Equal(0, ledger.DamageSetOffThisPlay);
        // The turn counter is NOT reset by a play: Run Away! and Ammo
        // Scavenging read the turn, and Big Badda Boom reads the play.
        Assert.Equal(1, ledger.SetOffThisTurn);

        var boom = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKoBigBaddaBoom")!;
        Assert.Contains("KleeOverhaulLedger.BeginPlay",
                        Il.Calls(boom.GetMethod("OnPlay", HeadlessGame.All)!));
    }

    [Fact]
    public void The_multiplier_is_armed_by_the_card_and_spent_by_its_set_off()
    {
        // R243 ([USER]: "move The Big One to 4x with no flat number"): the
        // flag became the row's own number, and an unarmed Set off is x1.
        var ledger = NewLedger();
        Assert.Equal(1, ledger.PeekMultiplier());

        ledger.ArmMultiplier(4);
        Assert.Equal(4, ledger.PeekMultiplier());   // a Mine may not eat it
        Assert.Equal(4, ledger.TakeMultiplier());
        Assert.Equal(1, ledger.TakeMultiplier());   // "this way" means this card

        var bigOne = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Cards.Prototype.Generated.ProtoKoTheBigOne")!;
        var seq = Il.CallSequence(
            bigOne.GetMethod("OnPlay", HeadlessGame.All)!).ToList();
        var arm = seq.FindIndex(c => c.EndsWith("ArmMultiplier"));
        var setOff = seq.FindIndex(c => c.EndsWith("SetOffAimed"));
        Assert.True(arm >= 0 && setOff > arm, string.Join(", ", seq));
    }

    // ---- Sorry, Jean... --------------------------------------------------

    [Fact]
    public void The_emergency_exit_removes_one_charge_and_reports_its_size()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(3), new ProtoBombs.Charge(11),
            new ProtoBombs.Charge(7));

        var removed = pile.TakeAt(1);

        Assert.Equal(11, removed!.Value.Size);
        Assert.Equal(new[] { 3, 7 }, pile.Charges.Select(c => c.Size));
        Assert.Null(pile.TakeAt(9));
    }

    // ---- the badge (the whole of the UI the slice asks for) --------------

    [Fact]
    public void The_badge_shows_the_total_size_and_the_tooltip_counts_the_mines()
    {
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5, IsMine: true), new ProtoBombs.Charge(8));

        // The shipped Bomb's own ruling, inherited: an enemy-side number reads
        // as incoming damage, and a COUNT hides what growing did.
        Assert.Equal(13, pile.DisplayAmount);
        Assert.Equal(13, pile.TotalSize);
        Assert.Equal(1, pile.MineCount);
    }

    // ---- SPARKS 'N' SPLASH, [USER]'s 2026-09-02 design -------------------

    [Fact]
    public void The_echo_reads_this_klees_pile_and_leaves_every_charge_on_it()
    {
        // R250 (2026-09-04): the echo pays the LARGEST charge, not the sum.
        // 5 and 3 is a 5-point hit, and the pile is still [5, 3] afterwards,
        // [9, 7] after the next morning's growth -- largest still 9.
        var klee = Seat.Klee();
        var other = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(5), new ProtoBombs.Charge(3));

        Assert.Equal(5, ProtoBombPower.LargestPlacedBy(enemy, klee.Creature));
        Assert.Equal(8, pile.TotalSize);              // the SUM still prices growth/jumps
        Assert.Equal(5, pile.LargestSize);
        Assert.Equal(2, pile.Charges.Count);

        pile.GrowBy(KleeOverhaulLaw.BombGrowth);
        Assert.Equal(5 + KleeOverhaulLaw.BombGrowth,
                     ProtoBombPower.LargestPlacedBy(enemy, klee.Creature));

        // R205, like every other read in this file: another Klee's pile is
        // not hers to echo.
        Assert.Equal(0, ProtoBombPower.LargestPlacedBy(enemy, other.Creature));
    }

    [Fact]
    public void The_echo_is_a_pyro_hit_and_not_a_set_off()
    {
        // The whole of what makes it playable in a growth deck: nothing is
        // taken, so no Spark is minted (rule 4 pays per EXPLOSION), no Mine
        // answers, rule 7's counters do not move, and rule 2 -- "only a card
        // that says Set off" -- is untouched.
        var hook = typeof(BombEchoPower)
            .GetMethod("BeforeSideTurnEnd", HeadlessGame.All)!;
        var calls = Il.Calls(hook);

        Assert.Contains("ProtoBombPower.HoldsChargeFrom", calls);
        Assert.Contains("ProtoBombPower.LargestPlacedBy", calls);
        Assert.Contains("ElementalHit.Deal", calls);

        Assert.DoesNotContain("ProtoBombPower.SetOff", calls);
        Assert.DoesNotContain("ProtoBombPower.TakeAll", calls);
        Assert.DoesNotContain("SparkPower.Gain", calls);
        Assert.DoesNotContain(calls,
                              c => c.StartsWith("KleeOverhaulLedger."));
        Assert.DoesNotContain("DamageCmd.Attack", calls);
    }

    [Fact]
    public void A_second_copy_is_its_own_hit_not_a_doubled_constant()
    {
        // `EB-358`, default applied: a second Sparks 'n' Splash used to badge
        // `Amount` 2 (this power's own `StackType` is `Counter`, one stack
        // per copy played) and pay the pile ONCE. Now the end-of-turn hook
        // loops `Amount` times -- ONE `ElementalHit.Deal` call SITE, run
        // `Amount` times, not two unrolled call sites (which would double the
        // damage at compile time regardless of how many copies are live, and
        // could not roll two independent targets).
        var hook = typeof(BombEchoPower)
            .GetMethod("BeforeSideTurnEnd", HeadlessGame.All)!;
        var calls = Il.Calls(hook);

        Assert.Single(calls, c => c == "ElementalHit.Deal");
        // The candidate roll is likewise ONE site, read fresh each pass of
        // the loop -- not hoisted out and reused for every copy.
        Assert.Single(calls, c => c.Contains("NextItem"));
    }

    // ---- helpers ---------------------------------------------------------

    private static int GrowthFor(MegaCrit.Sts2.Core.Entities.Creatures.Creature klee) =>
        (int)typeof(ProtoBombPower)
            .GetMethod("GrowthFor", HeadlessGame.All)!
            .Invoke(null, new object[] { klee })!;

    /// <summary>A ledger with no combat behind it. `For` needs a live
    /// CombatState to key on, so the pins construct one directly -- the class
    /// is plain state and its rules are pure.</summary>
    private static dynamic NewLedger()
    {
        var type = typeof(ProtoBombPower).Assembly
            .GetType("KleeMod.Powers.KleeOverhaulLedger")!;
        return System.Activator.CreateInstance(type, nonPublic: true)!;
    }
}
