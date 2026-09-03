using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Models.Powers;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI OVERHAUL, SLICE ONE, DRAFT 6: the four rules of the ruled brief
/// (`review/active/kokomi-brief-2026-09-01.md` draft 6 sec.2 -- the pet, the
/// Plan, where a planned clause lands, and "nothing happens by itself"), plus
/// Mend and the flag-off pin.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, said once, the same split
/// <c>KleeOverhaulRuleTests</c> makes and for the same reason. Draft 6's rules
/// are STRUCTURAL rather than arithmetic -- where a clause lands, in what
/// order, and on whose turn -- so what is pure is thinner than draft 2's: the
/// entry-HP cap, the per-turn Companion handover, and the two enums that ARE
/// the whitelists. Everything past those needs a live <c>CombatState</c>,
/// which the headless boundary does not reach (README, "The headless
/// boundary": <c>PowerCmd</c>, <c>CreatureCmd</c>, <c>ElementalHit.Deal</c>,
/// <c>PlayerCmd.AddPet</c> and a card PLAY are all outside it). So every
/// assertion below is either a real call on a real object, or a labelled
/// structural pin read off the compiled method -- never a mock's arithmetic.
///
/// STILL PLAY-DERIVED, narrowed rather than closed: the pet actually appearing
/// and being drag-targetable, the Hydro hit landing, the HP moving, the strip
/// drawing. Those need a combat and a Godot tree, and none of them needs a
/// decision.
/// </summary>
public class KokomiOverhaulRuleTests
{
    private static MethodBase Tide(string name) =>
        typeof(KokomiRules).GetMethod(name, HeadlessGame.All)
        ?? throw new System.InvalidOperationException(
            $"KokomiRules.{name} is gone -- the rule moved under this pin.");

    // ---- THE FLAG, OFF --------------------------------------------------

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST (2026-09-02).
    //
    // `dotnet test -p:KokomiOverhaul=true` defines `KOKOMI_OVERHAUL`, which is what MOVES
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
#if KOKOMI_OVERHAUL
    [Fact(Skip = "-p:KokomiOverhaul=true moves KokomiOverhaul.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        // The acceptance condition, and everything else here only matters
        // while it holds. `Enabled` is settable so a pin can assert both sides
        // in one build; nothing in the mod ever writes it.
        Assert.False(KokomiOverhaul.DefaultEnabled);
        Assert.Equal(KokomiOverhaul.DefaultEnabled, KokomiOverhaul.Enabled);
    }

    [Fact]
    public void The_arm_is_hers_alone()
    {
        // In co-op the other seat may be Klee, and a bare flag read would hand
        // him a Tide counter. Every rule in the arm asks through `LiveFor`.
        // BOTH SIDES OF THE SWITCH IN ONE BUILD, which is what `Enabled` is
        // settable for -- and restored, so no other pin reads a moved default.
        var was = KokomiOverhaul.Enabled;
        try
        {
            KokomiOverhaul.Enabled = true;
            Assert.False(KokomiOverhaul.LiveFor(Seat.Klee().Creature));
            Assert.False(KokomiOverhaul.LiveFor(Seat.Furina().Creature));
            Assert.True(KokomiOverhaul.LiveFor(Seat.Kokomi().Creature));

            KokomiOverhaul.Enabled = false;
            Assert.False(KokomiOverhaul.LiveFor(Seat.Kokomi().Creature));
        }
        finally
        {
            KokomiOverhaul.Enabled = was;
        }
    }

    [Fact]
    public void The_four_wiring_seams_read_the_flag_and_nothing_else()
    {
        // FLAG OFF IS BYTE-IDENTICAL, pinned where it is decided rather than
        // asserted in prose. Each seam is one `if` on the same property, so
        // with the arm off her starter, her relic and her pool fall through to
        // exactly what they were.
        var deck = typeof(global::KleeMod.Kokomi)
            .GetProperty("StartingDeck", HeadlessGame.All)!.GetGetMethod(true)!;
        Assert.Contains("KokomiOverhaul.get_Enabled", Il.Calls(deck));
        Assert.Contains("KokomiOverhaulRoster.StartingDeck", Il.Calls(deck));

        var relics = typeof(global::KleeMod.Kokomi)
            .GetProperty("StartingRelics", HeadlessGame.All)!
            .GetGetMethod(true)!;
        Assert.Contains("KokomiOverhaul.get_Enabled", Il.Calls(relics));
        Assert.Contains("KokomiOverhaulRoster.StartingRelics", Il.Calls(relics));

        var filter = typeof(global::KleeMod.KokomiCardPool)
            .GetMethod("FilterThroughEpochs", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaul.get_Enabled", Il.Calls(filter));
        Assert.Contains("KokomiOverhaulRoster.OfferablePool", Il.Calls(filter));

        var open = typeof(KokomiResourceHooks)
            .GetMethod("BeforeCombatStart", HeadlessGame.All)!;
        Assert.Contains("KokomiRules.InstallAll", Il.Calls(open));
    }

    [Fact]
    public void The_shipped_jellyfish_is_not_edited_by_this_arm()
    {
        // The whole reason the overhaul is a SECOND power. If this ever fails,
        // the arm has reached into the summon whose duration, ward and amp the
        // Kurage's-memory arm is also live inside.
        var shipped = typeof(KurageSummonPower).GetMethods(HeadlessGame.All)
            .Where(m => m.DeclaringType == typeof(KurageSummonPower))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.DoesNotContain(shipped, c => c.StartsWith("ProtoBakeKurage"));
        Assert.DoesNotContain(shipped, c => c.StartsWith("KokomiRules"));
        Assert.DoesNotContain(shipped, c => c.StartsWith("KokomiOverhaul"));
    }

    [Fact]
    public void The_memory_arm_is_switched_off_at_its_one_predicate()
    {
        // The two Kokomi arms are ALTERNATIVES, not layers, and this is the one
        // line that says so: `IsLive` is the single gate the whole memory arm
        // asks, so gating it here covers the entry rules, the fire, the keyword
        // door and the strip at once.
        var live = typeof(KurageMemory).GetMethod("IsLive", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaul.get_Enabled", Il.Calls(live));
    }

    [Fact]
    public void The_shipped_funnel_is_switched_off_under_the_arm()
    {
        // Brief sec.4, "What leaves": the Charge bank and its exhaust engine,
        // and the Burst gate. Each is one early return on the arm.
        var exhaust = typeof(KokomiResourceHooks)
            .GetMethod("AfterCardExhausted", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaul.LiveFor", Il.Calls(exhaust));

        var played = typeof(KokomiResourceHooks)
            .GetMethod("BeforeCardPlayed", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaul.LiveFor", Il.Calls(played));

        var grant = typeof(KokomiResourceHooks)
            .GetMethod("GrantKitIfLive", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaul.LiveFor", Il.Calls(grant));
    }

    // ---- RULE 1: the Bake-Kurage is a pet, and enemies cannot touch it ----

    [Fact]
    public void Rule1_the_jellyfish_is_a_pet_with_no_hp_bar()
    {
        // The 2026-09-02 decompile read is what settled the shape, and these
        // three properties are the whole of what makes it a jellyfish rather
        // than a monster: a `CustomPetModel` with the base library's own no-bar
        // pattern (`Byrdpip` and `PaelsLegion` are both 9999 / hidden).
        var pet = (BakeKurageMonster)RuntimeHelpers
            .GetUninitializedObject(typeof(BakeKurageMonster));
        Assert.Equal(9999, pet.MinInitialHp);
        Assert.Equal(9999, pet.MaxInitialHp);
        Assert.IsAssignableFrom<CustomPetModel>(pet);
    }

    [Fact]
    public void Rule1_the_install_summons_the_pet_and_the_marker_together()
    {
        // ONE ENTRY POINT, because a fight with one and not the other is a
        // fight in which either the Plans do not resolve or there is nothing
        // to aim them at -- and neither failure says so on screen.
        var install = Tide("Install");
        var calls = Il.Calls(install);
        Assert.Contains("BakeKuragePet.Summon", calls);
        Assert.Contains("PowerCmd.Apply", calls);

        // And the spawn is the engine's own pet door, not a creature the arm
        // adds by hand.
        var summon = typeof(BakeKuragePet)
            .GetMethod("Summon", HeadlessGame.All)!;
        Assert.Contains("PlayerCmd.AddPet", Il.Calls(summon));
    }

    [Fact]
    public void Rule1_nothing_in_this_arm_makes_the_pet_targetable_by_enemies()
    {
        // "Enemies cannot touch it" is FREE BY CONSTRUCTION -- an enemy move
        // only ever sees `CombatState.PlayerCreatures`, and a pet has no
        // `Player`. What this pin buys is that nobody added a flag: there is no
        // such flag in the assembly, so a future "fix" would have to reach for
        // the shipped redirect the Necrobinder's Osty uses.
        var arm = typeof(BakeKuragePet).GetMethods(HeadlessGame.All)
            .Concat(typeof(KokomiRules).GetMethods(HeadlessGame.All))
            .SelectMany(Il.Calls)
            .ToList();
        Assert.DoesNotContain(arm, c => c.Contains("DieForYou"));
        Assert.DoesNotContain(arm, c => c.Contains("ModifyUnblockedDamageTarget"));
    }

    // ---- RULE 2: the Plan, and where it is sent --------------------------

    [Fact]
    public void Rule2_a_play_on_the_jellyfish_is_one_question_about_the_target()
    {
        // The decompile read is what makes the generated branch one line: the
        // play pipeline hands `OnPlay` the CREATURE that was targeted, so
        // "played on the Bake-Kurage" is a property of the play rather than of
        // a mode, a keyword or a second card.
        var asked = typeof(KokomiPlan)
            .GetMethod("PlayedOnPet", HeadlessGame.All)!;
        Assert.Contains("BakeKuragePet.Is", Il.Calls(asked));
    }

    [Fact]
    public void Rule2_plans_are_carried_out_at_her_turn_start_in_order()
    {
        var resolve = typeof(ProtoBakeKuragePower)
            .GetMethod("AfterPlayerTurnStart", HeadlessGame.All)!;
        Assert.Contains("KokomiPlan.ResolveAll", Il.Calls(resolve));

        // THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS, so a Plan written
        // during resolution -- which Moon's Reflection's replay can reach --
        // waits for the next turn like every other.
        var all = typeof(KokomiPlan)
            .GetMethod("ResolveAll", HeadlessGame.All)!;
        var calls = Il.CallSequence(all).ToList();
        Assert.True(calls.IndexOf("List`1.Clear")
                    < calls.IndexOf("KokomiPlan.ResolveEntry"));
    }

    [Fact]
    public void Rule2_the_thirteen_planned_clauses_are_the_slices_eleven_and_two_more()
    {
        // A card cannot schedule anything else: the enum IS the whitelist the
        // codegen validates a row's `plan:` list against
        // (`gen_klee_cards.PLAN_CLAUSE_KINDS`). The twelfth is R236's
        // `PlayCopyOfCompanion` -- Gorou's Crystal Collapse, the Inazuma
        // workshop's one Personal, which plays a copy of the Companion card
        // captured when the Plan was WRITTEN. The thirteenth is `EB-335`'s
        // `BlockPerPlanThisMorning`, Tide Wall's per-Plan scaler. Eleven was
        // the SLICE's number and never a ceiling: a fourteenth kind owes this
        // list a line too.
        Assert.Equal(
            new[] { "Draw", "Energy", "Block", "Mend", "Damage",
                    "DamageQuarterMaxHp", "DamagePerCompanionLastTurn",
                    "ApplyWeak", "ApplyVulnerable", "PlanTwice",
                    "ReplayExhausted", "PlayCopyOfCompanion",
                    "BlockPerPlanThisMorning" },
            System.Enum.GetNames(typeof(KokomiPlan.Kind)));
    }

    [Fact]
    public void Rule3_a_planned_clause_lands_where_the_line_says_and_nowhere_else()
    {
        // "A planned hit lands on the front enemy (leftmost alive) unless the
        // line says every enemy." Three spellings, and the queue stores NO
        // creature at all -- which is the difference from draft 2 and the
        // reason a Plan cannot hold a pointer to an enemy that died overnight.
        Assert.Equal(new[] { "Self", "FrontEnemy", "AllEnemies" },
                     System.Enum.GetNames(typeof(KokomiPlan.Aim)));

        var planned = typeof(KokomiPlan.Planned);
        Assert.DoesNotContain(
            planned.GetProperties(HeadlessGame.All),
            f => f.PropertyType.Name == "Creature");
    }

    [Fact]
    public void Rule3_the_front_enemy_is_defined_once()
    {
        // "Leftmost alive" is a rule and not a per-card habit, so the two
        // things that read it -- a planned hit and The General's Banner --
        // read the same function.
        var front = typeof(KokomiPlan)
            .GetMethod("FrontEnemy", HeadlessGame.All)!;
        Assert.Contains("ICombatState.get_HittableEnemies", Il.Calls(front));

        var banner = typeof(GeneralsBannerPower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        Assert.Contains("KokomiPlan.FrontEnemy", Il.Calls(banner));
    }

    [Fact]
    public void The_moon_overlooks_the_waters_resolves_a_plan_now_as_well()
    {
        // "ALSO happen now" taken at its word: the Plan happens now AND is
        // still queued. Reading it as "instead" would delete rule 2 rather than
        // break it.
        var schedule = typeof(KokomiPlan)
            .GetMethod("Schedule", HeadlessGame.All)!;
        var calls = Il.CallSequence(schedule).ToList();
        Assert.Contains("List`1.Add", calls);
        Assert.Contains("KokomiPlan.ResolveEntry", calls);
        Assert.True(calls.IndexOf("List`1.Add")
                    < calls.IndexOf("KokomiPlan.ResolveEntry"));
    }

    [Fact]
    public void One_plan_is_one_entry_and_the_payoffs_are_priced_in_it()
    {
        // "Whenever the jellyfish carries out a Plan" is once per ENTRY, which
        // is what makes War Council -- two clauses, one sentence -- draw one
        // card and not two. The bus rings from the one place an entry finishes.
        var entry = typeof(KokomiPlan)
            .GetMethod("ResolveEntry", HeadlessGame.All)!;
        Assert.Contains("IKokomiPlanListener.OnPlanResolved", Il.Calls(entry));

        var one = typeof(KokomiPlan).GetMethod("ResolveOne", HeadlessGame.All)!;
        Assert.DoesNotContain("IKokomiPlanListener.OnPlanResolved",
                              Il.Calls(one));

        Assert.Contains("CardPileCmd.Draw",
                        Il.Calls(typeof(TreatisePower)
                            .GetMethod("OnPlanResolved", HeadlessGame.All)!));
        Assert.Contains("CreatureCmd.GainBlock",
                        Il.Calls(typeof(SongOfPearlsPower)
                            .GetMethod("OnPlanResolved", HeadlessGame.All)!));
    }

    // ---- THE ONCE-PER-TURN CAPS ([USER], live 2026-09-02) ----------------

    /// <summary>One ledger, rolled to a round, for the cap pins below. The
    /// instance is driven directly for the reason
    /// `Chain_of_command_reads_the_turn_that_just_ended` drives it directly:
    /// a headless seat has no `CombatState`, so `For` would re-roll to round
    /// zero on every read and clear the very latch under test.</summary>
    private static KokomiOverhaulLedger RolledLedger(int round = 3)
    {
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(Seat.Kokomi().Creature);
        ledger.RollTo(round);
        return ledger;
    }

    [Fact]
    public void Treatise_draws_once_a_turn_and_a_second_plan_draws_nothing()
    {
        // [USER], live: "Treatise looks too good (one draw per turn if a Plan
        // fired might be ok; one draw per Plan is too abuseable)."
        var ledger = RolledLedger();
        Assert.True(ledger.Claim(nameof(TreatisePower)));
        Assert.False(ledger.Claim(nameof(TreatisePower)));

        // A CAP AND NOT A ONE-SHOT: the next morning pays again.
        ledger.RollTo(4);
        Assert.True(ledger.Claim(nameof(TreatisePower)));

        // And the hook CLAIMS BEFORE IT DRAWS, so the second Plan of a
        // morning reaches no draw at all rather than drawing and refunding.
        var hook = typeof(TreatisePower)
            .GetMethod("OnPlanResolved", HeadlessGame.All)!;
        var calls = Il.CallSequence(hook).ToList();
        Assert.True(calls.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn")
                    < calls.IndexOf("CardPileCmd.Draw"));
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Song_of_pearls_blocks_once_a_turn_and_a_second_plan_does_not()
    {
        // [USER], live, in one word -- "Likewise" -- of Treatise's verdict:
        // the two cards are the same shape, so capping one and not the other
        // would just move the abusable line across.
        var ledger = RolledLedger();
        Assert.True(ledger.Claim(nameof(SongOfPearlsPower)));
        Assert.False(ledger.Claim(nameof(SongOfPearlsPower)));
        ledger.RollTo(4);
        Assert.True(ledger.Claim(nameof(SongOfPearlsPower)));

        var hook = typeof(SongOfPearlsPower)
            .GetMethod("OnPlanResolved", HeadlessGame.All)!;
        var calls = Il.CallSequence(hook).ToList();
        Assert.True(calls.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn")
                    < calls.IndexOf("CreatureCmd.GainBlock"));
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_generals_banner_weaks_once_a_turn_and_still_counts_them_all()
    {
        // [USER], live: "The General's Banner applies a LOT of Weak. Probably
        // too strong."
        var ledger = RolledLedger();
        Assert.True(ledger.Claim(nameof(GeneralsBannerPower)));
        Assert.False(ledger.Claim(nameof(GeneralsBannerPower)));
        ledger.RollTo(4);
        Assert.True(ledger.Claim(nameof(GeneralsBannerPower)));

        // THE COUNTER IS NOT CAPPED WITH THE WEAK, and the order in the hook
        // is what says so: every Companion play is counted (Chain of Command
        // reads that count) and only the Weak is claimed.
        var hook = typeof(GeneralsBannerPower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        var calls = Il.CallSequence(hook).ToList();
        Assert.True(calls.IndexOf("KokomiOverhaulLedger.NoteCompanionPlayed")
                    < calls.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn"));
        Assert.True(calls.IndexOf("KokomiOverhaulLedger.ClaimOncePerTurn")
                    < calls.IndexOf("PowerCmd.Apply<WeakPower>"));
        KokomiOverhaulLedger.ResetAll();
    }

    // ---- SANGO ISSHIN'S CONDITION ([USER], live 2026-09-02) --------------

    [Fact]
    public void A_carried_out_plan_is_remembered_for_the_turn_and_no_longer()
    {
        // [USER], live: "It's fine if Rares are strong (see: Knife Trap), but
        // this requires absolutely 0 setup or combo - it's just 'press button,
        // delete act 1'." So the Rare's payoff now asks a per-turn question,
        // and the ledger is what answers it.
        var ledger = RolledLedger();
        Assert.False(ledger.PlanCarriedOutThisTurn);
        ledger.NotePlanCarriedOut();
        Assert.True(ledger.PlanCarriedOutThisTurn);

        // A second Plan in the same turn changes nothing, and the turn
        // boundary forgets it -- a morning is not a combat.
        ledger.NotePlanCarriedOut();
        Assert.True(ledger.PlanCarriedOutThisTurn);
        ledger.RollTo(4);
        Assert.False(ledger.PlanCarriedOutThisTurn);
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_flag_is_written_where_a_plan_is_carried_out_and_nowhere_else()
    {
        // ONE EVENT, THREE DOORS: the morning queue, Change of Plans and The
        // Moon Overlooks the Waters all reach `ResolveEntry`, so writing the
        // flag there is what makes the card's printed "carried out a Plan this
        // turn" true of all three without naming any of them.
        var entry = typeof(KokomiPlan)
            .GetMethod("ResolveEntry", HeadlessGame.All)!;
        Assert.Contains("KokomiOverhaulLedger.NotePlanCarriedOut",
                        Il.Calls(entry));

        var writers = typeof(KokomiPlan).GetMethods(HeadlessGame.All)
            .Where(m => m.Name != "ResolveEntry"
                        && Il.Calls(m).Contains(
                            "KokomiOverhaulLedger.NotePlanCarriedOut"))
            .Select(m => m.Name)
            .ToList();
        Assert.Empty(writers);
    }

    [Fact]
    public void Sango_isshin_reads_the_flag_and_hits_all_enemies_behind_it()
    {
        // The card, as generated: 8 to the aimed enemy is the floor, and the
        // quarter -- computed by the ONE rule, so the face and the hit cannot
        // round differently -- is what a planned morning buys. It is an
        // ordinary aimed Attack now, not a card played on the jellyfish.
        var play = typeof(ProtoKkSangoIsshin)
            .GetMethod("OnPlay", HeadlessGame.All)!;
        var calls = Il.Calls(play);
        Assert.Contains("KokomiOverhaulLedger.get_PlanCarriedOutThisTurn",
                        calls);
        Assert.Contains("KokomiRules.QuarterMaxHpAll", calls);
        Assert.Contains("DamageCmd.Attack", calls);
        // No Plan line left: it is not playable on the pet.
        Assert.DoesNotContain("KokomiPlan.Schedule", calls);
        Assert.DoesNotContain(typeof(ProtoKkSangoIsshin).GetInterfaces(),
                              i => i.Name == "IPlannedCard");
    }

    [Fact]
    public void The_three_caps_are_one_latch_set_and_do_not_shadow_each_other()
    {
        // ONE helper shared by three powers, keyed by the power's own name --
        // so a morning that pays Treatise still pays Song of Pearls, and a
        // Companion played after both still applies its Weak.
        var ledger = RolledLedger();
        Assert.True(ledger.Claim(nameof(TreatisePower)));
        Assert.True(ledger.Claim(nameof(SongOfPearlsPower)));
        Assert.True(ledger.Claim(nameof(GeneralsBannerPower)));
        Assert.False(ledger.Claim(nameof(TreatisePower)));

        // And the turn boundary clears all three at once, which is why they
        // cannot come to disagree about when a turn began.
        ledger.RollTo(4);
        Assert.True(ledger.Claim(nameof(TreatisePower)));
        Assert.True(ledger.Claim(nameof(SongOfPearlsPower)));
        Assert.True(ledger.Claim(nameof(GeneralsBannerPower)));
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Change_of_plans_moves_the_front_plan_and_does_not_copy_it()
    {
        // "Carries out" means one resolution moved forward, everywhere in the
        // arm. The entry LEAVES the queue before it resolves, which is also
        // what keeps the badge from showing a Plan that already happened.
        var front = typeof(KokomiPlan)
            .GetMethod("ResolveFront", HeadlessGame.All)!;
        var calls = Il.CallSequence(front).ToList();
        Assert.True(calls.IndexOf("List`1.RemoveAt")
                    < calls.IndexOf("KokomiPlan.ResolveEntry"));
    }

    [Fact]
    public void Nereids_ascension_is_read_per_plan_and_never_doubles_itself()
    {
        // The reading, pinned where it is taken: the power is asked INSIDE the
        // drain loop, before each entry is carried out. So the Rare's own
        // clause -- which is what installs the power -- is not doubled, and
        // every Plan written after it in the same morning is.
        var all = typeof(KokomiPlan)
            .GetMethod("ResolveAll", HeadlessGame.All)!;
        var drain = Il.CallSequence(all).ToList();
        Assert.True(drain.IndexOf("KokomiPlan.CarryOutTimes")
                    < drain.IndexOf("KokomiPlan.ResolveEntry"));

        // And the window is a DURATION on her, so re-wearing extends rather
        // than stacking.
        var wear = typeof(PlanTwicePower).GetMethod("Wear", HeadlessGame.All)!;
        var calls = Il.Calls(wear);
        Assert.Contains("PowerCmd.Apply", calls);
        Assert.Contains("PowerCmd.ModifyAmount", calls);
        Assert.Contains("PowerCmd.TickDownDuration",
                        Il.Calls(typeof(PlanTwicePower)
                            .GetMethod("AfterSideTurnEnd", HeadlessGame.All)!));
    }

    [Fact]
    public void Moons_reflection_replays_a_plan_line_or_the_card_itself()
    {
        // Both shapes out of one screen, and neither is re-derived: a chosen
        // card that HAS a Plan line contributes its own typed clauses through
        // `IPlannedCard`, and one that has none is replayed whole through the
        // game's free-play door.
        var pick = typeof(KokomiPlan)
            .GetMethod("ScheduleFromExhaust", HeadlessGame.All)!;
        var calls = Il.Calls(pick);
        Assert.Contains("CardSelectCmd.FromCombatPile", calls);
        Assert.Contains("IPlannedCard.get_PlanClauses", calls);
        Assert.Contains("KokomiPlan.Schedule", calls);

        // The replay is move-to-hand THEN auto-play, which is
        // `KurageMemory.Fire`'s own argument: a card resolving out of a pile it
        // is still a member of is a bug class this mod has already paid for.
        var replay = typeof(KokomiPlan).GetMethod("Replay", HeadlessGame.All)!;
        var seq = Il.CallSequence(replay).ToList();
        Assert.True(seq.IndexOf("CardPileCmd.Add") < seq.IndexOf("CardCmd.AutoPlay"));
    }

    // ---- the debuff event, which two things read -------------------------

    [Fact]
    public void The_casket_and_the_clouds_read_one_definition_of_the_event()
    {
        // The relic and the Rare answer the SAME event, so they ask the same
        // predicate: a second spelling is how the two would eventually
        // disagree about what applying a debuff was.
        Assert.Contains("KokomiOverhaulKit.IsHerDebuffOnEnemy",
                        Il.Calls(typeof(global::KleeMod.Relics.TamakushiCasket)
                            .GetMethod("AfterPowerAmountChanged",
                                       HeadlessGame.All)!));
        Assert.Contains("KokomiOverhaulKit.IsHerDebuffOnEnemy",
                        Il.Calls(typeof(CloudsLikeWavesPower)
                            .GetMethod("AfterPowerAmountChanged",
                                       HeadlessGame.All)!));
    }

    [Fact]
    public void The_casket_cannot_answer_its_own_answer()
    {
        // NOT PARANOIA: a Hydro strike into a Cryo aura Freezes, and Frozen is
        // a debuff she applied to an enemy. Without the latch the relic would
        // answer itself until the stack ran out.
        Assert.Contains("KokomiOverhaulKit.Answer",
                        Il.Calls(typeof(global::KleeMod.Relics.TamakushiCasket)
                            .GetMethod("AfterPowerAmountChanged",
                                       HeadlessGame.All)!));
    }

    [Fact]
    public void The_jellyfish_is_the_dealer_of_the_caskets_strike()
    {
        // The reading: the slice says "IT strikes that enemy for 2", so the
        // applier is the PET -- which carries no Strength, so the 2 is a flat
        // 2. Routing it through her would have quietly made the Casket the best
        // Strength payoff in a pool that just got Strength back.
        var strike = typeof(global::KleeMod.Relics.TamakushiCasket)
            .GetMethod("Strike", HeadlessGame.All)!;
        var calls = Il.Calls(strike);
        Assert.Contains("BakeKuragePet.Of", calls);
        Assert.Contains("ElementalHit.Deal", calls);
    }

    // ---- THE MEND RULE ---------------------------------------------------

    [Fact]
    public void The_mend_ceiling_is_the_hp_she_walked_in_with()
    {
        var kokomi = Seat.Kokomi(maxHp: 80).Creature;
        Seat.Set(kokomi, "CurrentHp", 62);
        KokomiOverhaulLedger.ResetAll();

        KokomiOverhaulLedger.OpenCombat(kokomi);
        Assert.Equal(62, KokomiOverhaulLedger.For(kokomi).EntryHp);

        // Nothing inside the fight moves it, which is what makes rest sites
        // hers.
        Seat.Set(kokomi, "CurrentHp", 30);
        Assert.Equal(62, KokomiOverhaulLedger.For(kokomi).EntryHp);
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_cap_lives_in_exactly_one_place()
    {
        var mend = Tide("Mend");
        var calls = Il.Calls(mend);
        Assert.Contains("KokomiOverhaulLedger.get_EntryHp", calls);
        Assert.Contains("CreatureCmd.Heal", calls);

        // And nothing else heals, so no Mend can skip the cap.
        var others = typeof(KokomiRules).GetMethods(HeadlessGame.All)
            .Where(m => m.Name != "Mend"
                        && Il.Calls(m).Contains("CreatureCmd.Heal"))
            .Select(m => m.Name)
            .ToList();
        Assert.Empty(others);
    }

    // ---- rule 3's other half: Strength is HERS again ---------------------

    [Fact]
    public void Rule3_the_shipped_strength_refusal_is_skipped_under_the_arm()
    {
        // Draft 2 sent her Strength to the Tide at this chokepoint. Draft 6
        // says "your Strength and Dexterity count, since the plans are hers",
        // so the arm SKIPS the refusal and the Strength simply lands. The
        // shipped conversion is still there for a flag-off run.
        var hook = typeof(KokomiResourceHooks)
            .GetMethod("TryModifyPowerAmountReceived", HeadlessGame.All)!;
        var calls = Il.Calls(hook);
        Assert.Contains("KokomiOverhaul.LiveFor", calls);
        Assert.Contains("KokomiResources.GainCharge", calls);
        // Nothing of this arm's is paid into any more.
        Assert.DoesNotContain(calls, c => c.StartsWith("KokomiRules.Gain"));
    }

    // ---- the Commander's two powers --------------------------------------

    [Fact]
    public void Chain_of_command_reads_the_turn_that_just_ended()
    {
        var kokomi = Seat.Kokomi().Creature;
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(kokomi);
        ledger.RollTo(3);

        Assert.Equal(0, ledger.CompanionsPlayedThisTurn);
        ledger.NoteCompanionPlayed();
        ledger.NoteCompanionPlayed();
        Assert.Equal(2, ledger.CompanionsPlayedThisTurn);

        // THE HANDOVER IS THE WHOLE POINT: a Plan written on turn 3 is carried
        // out at the top of turn 4, and what it needs is turn 3's count.
        ledger.RollTo(4);
        Assert.Equal(0, ledger.CompanionsPlayedThisTurn);
        Assert.Equal(2, ledger.CompanionsPlayedLastTurn);
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Rally_discounts_rather_than_zeroes()
    {
        // Draft 6's change from draft 2's Vanguard: the card prints "costs 1
        // less", so the grant SUBTRACTS and floors at zero. Setting the cost
        // would be a different card on an expensive Companion.
        var hook = typeof(NextCompanionDiscountPower)
            .GetMethod("TryModifyEnergyCostInCombat", HeadlessGame.All)!;
        Assert.Contains("Math.Max", Il.Calls(hook));
        Assert.Equal(1, NextCompanionDiscountPower.Discount);
    }

    // ---- the roster ------------------------------------------------------

    [Fact]
    public void The_starter_is_ten_cards_and_the_pool_is_twenty_eight()
    {
        // Read off the IL rather than by building the models, which needs
        // ModelDb: `ModelDb.Card<T>()` throws until the game's pool build has
        // run (see PrototypeRoster's own header for the poisoned-type trap).
        var deck = Il.Method("KokomiOverhaulRoster", "StartingDeck");
        Assert.Equal(10, Il.CallSequence(deck)
            .Count(c => c.StartsWith("ModelDb.Card")));

        // EB-284 split the pool in two: `Slice` is the packet's rows and
        // `OfferablePool` is that plus the Ancient tail below. TWENTY-EIGHT
        // since `EB-335` (R246 pick 2) added Tide Wall and Shell Guard.
        var slice = Il.Method("KokomiOverhaulRoster", "Slice");
        Assert.Equal(28, Il.CallSequence(slice)
            .Count(c => c.StartsWith("ModelDb.Card")));
    }

    [Fact]
    public void The_arm_pool_carries_her_ancient_card()
    {
        // `EB-284`. The arm's `FilterThroughEpochs` RETURNS this list and never
        // reaches the shipped pool, so this list IS `GetUnlockedCards` under
        // the flag -- and `DustyTome.SetupForPlayer` draws a random
        // `CardRarity.Ancient` card from exactly that set. Without the tail the
        // draw is empty and `Darv.GenerateInitialOptions` NREs on room entry,
        // which is how [USER]'s run ended at the act-two door.
        var pool = Il.Method("KokomiOverhaulRoster", "OfferablePool");
        Assert.Contains("RosterAncientCards.get_Kokomi", Il.Calls(pool));
        Assert.Contains("KokomiOverhaulRoster.Slice", Il.Calls(pool));
    }

    // --- `EB-334`: who deals Plan damage (R246 pick 1) -------------------
    //
    // ONE PIN PER MODIFIER, which is what the row asks for, and each is a REAL
    // call on a REAL creature carrying a REAL power. `KokomiPlan.PlannedDamage`
    // is the arithmetic the face and the pins share (`EB-265`'s rule); the
    // morning reaches the same number through `ElementalHit.Deal`, which is
    // outside the headless boundary and is pinned structurally below instead.

    [Fact]
    public void EB334_her_weak_does_not_shrink_a_planned_hit()
    {
        // The seat's own arithmetic: "Plan: Deal 12 damage" paid 9 the next
        // morning against a Strategic enemy whose Weak landed at the end of
        // her turn, exactly x0.75, with no screen showing it
        // (`opus-act2b.md` finding 3).
        var kokomi = Seat.Kokomi().WithPower<WeakPower>(2);
        var enemy = Seat.Kokomi(40).Creature;

        // The term is REAL and would have bitten: this is the dealer half a
        // planned hit no longer runs.
        Assert.Equal(9m, SimDamagePipeline.DealerMods(kokomi.Creature, 12m));
        // And this is what the Plan deals.
        Assert.Equal(12, KokomiPlan.PlannedDamage(enemy, 12));
    }

    [Fact]
    public void EB334_enemy_vulnerable_multiplies_a_planned_hit()
    {
        // The half that paid nothing before: "27 landed where x1.5 would have
        // been 40" (`opus-act2.md` sec.(c)5).
        var enemy = Seat.Kokomi(60).WithPower<VulnerablePower>(2).Creature;
        Assert.Equal(18, KokomiPlan.PlannedDamage(enemy, 12));
    }

    [Fact]
    public void EB334_an_attack_buff_on_kokomi_does_not_reach_a_planned_hit()
    {
        // Strength is the mirror's whole vocabulary for a flat attack buff --
        // `SimDamagePipeline.DealerMods` is where every one of them lands, and
        // Fantastic Voyage is the base game's name for the same term, which
        // the seat watched add to card attacks and not to Plans.
        var kokomi = Seat.Kokomi().WithPower<StrengthPower>(5);
        var enemy = Seat.Kokomi(40).Creature;

        Assert.Equal(12m, SimDamagePipeline.DealerMods(kokomi.Creature, 7m));
        Assert.Equal(7, KokomiPlan.PlannedDamage(enemy, 7));
    }

    [Fact]
    public void EB334_the_planned_hit_is_unpowered_and_still_hers()
    {
        // STRUCTURAL, because `ElementalHit.Deal` needs a live combat. The two
        // halves of the ruling are one call each: the flag that drops the
        // dealer's mods, and the applier that stays her so a Plan-caused
        // Freeze is still a debuff SHE applied and the Casket answers it.
        var deal = Il.Method("ElementalHit", "Deal");
        var powered = deal.GetParameters().Single(p => p.Name == "powered");
        Assert.True(powered.HasDefaultValue);
        Assert.Equal(true, powered.DefaultValue);

        var hit = Il.Method("KokomiPlan", "Hit");
        Assert.Contains(Il.Calls(hit), c => c.Contains("ElementalHit.Deal"));

        // The face reads the SAME arithmetic the pins above read, so it cannot
        // drift from the morning.
        var preview = typeof(KokomiPlan.PlanDamageVar)
            .GetMethod("UpdateCardPreview", HeadlessGame.All)!;
        Assert.Contains("KokomiPlan.PlannedDamage", Il.Calls(preview));
    }

    // --- `EB-335`: the kit's own defence in act 2 (R246 pick 2) -----------

    [Fact]
    public void EB335_tide_wall_multiplies_the_whole_mornings_depth()
    {
        // The count is written once, at the drain, so a Tide Wall written
        // first, second or last in the queue pays the same number. Real
        // ledger, real turn boundary.
        var ledger = new KokomiOverhaulLedger();
        Assert.Equal(0, ledger.PlansThisMorning);
        ledger.NoteMorning(3);
        Assert.Equal(3, ledger.PlansThisMorning);
        // A morning that drains nothing reads an honest zero rather than
        // yesterday's depth: the roll clears it and `ResolveAll` writes it.
        ledger.RollTo(2);
        Assert.Equal(0, ledger.PlansThisMorning);

        Assert.Contains("KokomiOverhaulLedger.NoteMorning",
                        Il.Calls(Il.Method("KokomiPlan", "ResolveAll")));
        Assert.Contains("KokomiOverhaulLedger.get_PlansThisMorning",
                        Il.Calls(Il.Method("KokomiPlan", "ResolveOne")));
    }

    [Fact]
    public void EB335_shell_guard_reads_the_casket_strike_and_closes_after_the_morning()
    {
        // The card names the RELIC, so the payout hangs off the strike itself
        // and not off the debuff that caused it -- which is what keeps it
        // separable from The Clouds Like Waves Rippling.
        Assert.Contains("ShellGuardPower.Pay",
                        Il.Calls(Il.Method("TamakushiCasket", "Strike")));
        // "Until your next turn" INCLUDES that turn's morning: R246 pick 2
        // says the morning's Plans strike it too, so the window closes one
        // line after the drain rather than on the turn-start roll.
        var turnStart = Il.CallSequence(
            Il.Method("ProtoBakeKuragePower", "AfterPlayerTurnStart")).ToList();
        var drain = turnStart.FindIndex(c => c.Contains("KokomiPlan.ResolveAll"));
        var close = turnStart.FindIndex(c => c.Contains("ShellGuardPower.Close"));
        Assert.True(drain >= 0, "the morning is gone");
        Assert.True(close > drain,
                    "the window closes before the morning it is meant to cover");
    }

    [Fact]
    public void EB335_shell_guard_pays_nothing_without_the_card()
    {
        // A run that never drew Shell Guard, and a run that traded the Casket
        // away, both pay nothing -- the guard is the power's presence and its
        // amount, checked before any command is reached.
        var bare = Seat.Kokomi();
        Assert.Empty(bare.Creature.Powers.OfType<ShellGuardPower>());
        Assert.Null(Record.Exception(
            () => ShellGuardPower.Pay(null, bare.Creature).Wait()));
        Assert.Null(Record.Exception(
            () => ShellGuardPower.Close(bare.Creature).Wait()));
    }

    [Fact]
    public void The_wire_carries_the_queue_and_the_pets_id()
    {
        // `EB-216`. A seat that cannot read the queue cannot play her, and a
        // seat with no id to aim at cannot write a Plan at all. The bridge
        // reaches this by REFLECTION (gits/GitsKokomiPlan.cs), so the method's
        // name and its return type are the contract.
        var snapshot = typeof(KokomiPlan)
            .GetMethod("Snapshot", HeadlessGame.All)!;
        Assert.True(snapshot.IsStatic && snapshot.IsPublic);
        Assert.Equal("Dictionary`2", snapshot.ReturnType.Name);
        var calls = Il.Calls(snapshot);
        Assert.Contains("BakeKuragePet.Of", calls);
        Assert.Contains("KokomiPlan.Pending", calls);
    }
}
