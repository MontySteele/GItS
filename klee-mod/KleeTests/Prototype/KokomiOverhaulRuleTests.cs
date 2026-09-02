using System.Linq;
using System.Reflection;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE KOKOMI OVERHAUL, SLICE ONE: rules 1 to 8 of the ruled brief
/// (`review/active/kokomi-brief-2026-09-01.md` sec.4), and the flag-off pin.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, said once, the same split
/// <c>KleeOverhaulRuleTests</c> makes and for the same reason. The rules were
/// written with the DECISIONS pure -- the Tide's arithmetic, the pulse's two
/// numbers, the entry-HP cap's arithmetic, the per-turn latches, the Garment's
/// hit latch, the Banner's "first each turn" -- and everything past them needs
/// a live <c>CombatState</c>, which the headless boundary does not reach
/// (README, "The headless boundary": <c>PowerCmd</c>, <c>CreatureCmd</c>,
/// <c>ElementalHit.Deal</c> and a card PLAY are all outside it). So every
/// assertion below is either a real call on a real object, or a labelled
/// structural pin read off the compiled method -- never a mock's arithmetic.
///
/// STILL PLAY-DERIVED, narrowed rather than closed: the Hydro hit actually
/// landing, the HP actually moving, the badge redrawing, and the Block that
/// eats an Exert. Those need a combat, and none of them needs a decision.
/// </summary>
public class KokomiOverhaulRuleTests
{
    private static MethodBase Tide(string name) =>
        typeof(KokomiTide).GetMethod(name, HeadlessGame.All)
        ?? throw new System.InvalidOperationException(
            $"KokomiTide.{name} is gone -- the rule moved under this pin.");

    // ---- THE FLAG, OFF --------------------------------------------------

    [Fact]
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
        Assert.Contains("KokomiTide.InstallAll", Il.Calls(open));
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
        Assert.DoesNotContain(shipped, c => c.StartsWith("KokomiTide"));
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

    // ---- RULE 1: the jellyfish holds the Tide, and nothing resets it ------

    [Fact]
    public void Rule1_the_tide_starts_at_zero_and_the_badge_shows_it()
    {
        var kokomi = Seat.Kokomi();
        var kurage = ProtoKurage.Field(kokomi.Creature);

        Assert.Equal(0, kurage.Tide);
        Assert.Equal(0, kurage.DisplayAmount);
        // The presence marker is NOT the Tide: a Counter at zero stacks is a
        // power the game may tear down, and rule 1 says the jellyfish is out
        // for the WHOLE combat, opening turn included.
        Assert.Equal(1, kurage.Amount);
    }

    [Fact]
    public void Rule2_her_cards_add_to_it_and_it_accumulates()
    {
        var kokomi = Seat.Kokomi();
        var kurage = ProtoKurage.Field(kokomi.Creature);

        kurage.AddTide(5);
        kurage.AddTide(4);
        kurage.AddTide(10);

        Assert.Equal(19, kurage.Tide);
        Assert.Equal(19, kurage.DisplayAmount);
        Assert.Equal(19, KokomiTide.Of(kokomi.Creature));
    }

    [Fact]
    public void Rule1_nothing_in_the_power_resets_the_tide_by_itself()
    {
        // "never resetting on its own" is the whole hold half of the loop, and
        // it is a property of what the type CAN do: the only writer that lowers
        // the Tide is TakeTide, and the only caller of TakeTide is the Surge.
        var writers = typeof(ProtoBakeKuragePower)
            .GetMethods(HeadlessGame.All)
            .Where(m => m.DeclaringType == typeof(ProtoBakeKuragePower)
                        && Il.Calls(m).Contains("ProtoBakeKuragePower.TakeTide"))
            .Select(m => m.Name)
            .ToList();
        Assert.Empty(writers);

        var callers = typeof(KokomiTide).GetMethods(HeadlessGame.All)
            .Where(m => Il.Calls(m).Contains("ProtoBakeKuragePower.TakeTide"))
            .Select(m => m.Name)
            .ToList();
        Assert.Equal(new[] { "Surge" }, callers);
    }

    // ---- RULE 3: Surge ---------------------------------------------------

    [Fact]
    public void Rule3_a_surge_takes_the_whole_tide_and_leaves_zero()
    {
        var kokomi = Seat.Kokomi();
        var kurage = ProtoKurage.Field(kokomi.Creature, tide: 14);

        Assert.Equal(14, kurage.TakeTide());
        Assert.Equal(0, kurage.Tide);
        Assert.Equal(0, kurage.DisplayAmount);
    }

    [Fact]
    public void Rule3_the_surge_is_hydro_and_take_then_resolve()
    {
        // Structural: the hit needs a combat. What is pinned is the ORDER --
        // the Tide leaves the jellyfish BEFORE anything that can kill runs, the
        // EB-138 discipline -- and that the hit goes through the shared
        // elemental pipeline rather than a private one, which is what makes
        // rule 3's Hydro need no card text.
        var surge = Tide("Surge");
        var calls = Il.CallSequence(surge).ToList();
        Assert.Contains("ProtoBakeKuragePower.TakeTide", calls);
        Assert.Contains("ElementalHit.Deal", calls);
        Assert.True(calls.IndexOf("ProtoBakeKuragePower.TakeTide")
                    < calls.IndexOf("ElementalHit.Deal"));
        // And the turn latch is set from the same call, so the pulse and the
        // Surge cannot disagree about whether she cashed.
        Assert.Contains("KokomiOverhaulLedger.NoteSurge", Il.Calls(surge));
    }

    [Fact]
    public void Rule4_an_empty_surge_still_counts_as_a_surge()
    {
        // "a turn in which she did not Surge", not "a turn in which the Surge
        // did something": cashing nothing is still cashing, and the alternative
        // would pay the pulse for a wasted card.
        var kokomi = Seat.Kokomi();
        var ledger = KokomiOverhaulLedger.For(kokomi.Creature);
        ledger.RollTo(1);
        Assert.False(ledger.SurgedThisTurn);

        ledger.NoteSurge(0);
        Assert.True(ledger.SurgedThisTurn);
        Assert.Equal(0, ledger.SurgeDamageThisPlay);
    }

    [Fact]
    public void Undertow_blocks_half_the_tide_that_went_out()
    {
        var kokomi = Seat.Kokomi();
        var ledger = KokomiOverhaulLedger.For(kokomi.Creature);
        ledger.RollTo(2);
        ledger.BeginPlay(livingEnemies: 1);
        ledger.NoteSurge(15);

        // Half, rounded down -- and it is the TIDE, not the number that landed
        // after the pipeline's amplifier and the target's Vulnerable, neither
        // of which is a fact about her Tide.
        Assert.Equal(7, ledger.SurgeDamageThisPlay / 2);
    }

    // ---- RULE 4: the pulse, and both its numbers on the relic -------------

    [Fact]
    public void Rule4_the_pulse_is_two_up_to_eight()
    {
        var kokomi = Seat.Kokomi().Creature;
        Assert.Equal(2, KokomiOverhaulLaw.PulseMend);
        Assert.Equal(8, KokomiOverhaulLaw.PulseBudget);
        Assert.Equal(KokomiOverhaulLaw.PulseMend,
                     global::KleeMod.Relics.TamanooyasCasket.PulseMend(kokomi));
        Assert.Equal(KokomiOverhaulLaw.PulseBudget,
                     global::KleeMod.Relics.TamanooyasCasket.PulseBudget(kokomi));
    }

    [Fact]
    public void Song_of_pearls_replaces_both_numbers()
    {
        var kokomi = Seat.Kokomi().WithPower<SongOfPearlsPower>(1).Creature;
        Assert.Equal(KokomiOverhaulLaw.SongOfPearlsMend,
                     global::KleeMod.Relics.TamanooyasCasket.PulseMend(kokomi));
        Assert.Equal(KokomiOverhaulLaw.SongOfPearlsBudget,
                     global::KleeMod.Relics.TamanooyasCasket.PulseBudget(kokomi));
    }

    [Fact]
    public void The_clouds_like_waves_only_reads_under_half_hp()
    {
        var whole = Seat.Kokomi().WithPower<CloudsLikeWavesPower>(4);
        Assert.False(CloudsLikeWavesPower.UnderHalf(whole.Creature));
        Assert.Equal(KokomiOverhaulLaw.PulseMend,
                     global::KleeMod.Relics.TamanooyasCasket.PulseMend(
                         whole.Creature));

        var hurt = Seat.Kokomi().WithPower<CloudsLikeWavesPower>(4);
        Seat.Set(hurt.Creature, "CurrentHp", 30);
        Assert.True(CloudsLikeWavesPower.UnderHalf(hurt.Creature));
        Assert.Equal(4, global::KleeMod.Relics.TamanooyasCasket.PulseMend(
            hurt.Creature));
    }

    [Fact]
    public void The_two_pulse_cards_compose_by_max_and_the_budget_is_songs()
    {
        // A READING, and it is recorded on TamanooyasCasket.PulseMend: both
        // cards make a flat statement about the same number and neither prints
        // an order, so the larger is taken because that is the only reading
        // that leaves both printed faces true.
        var both = Seat.Kokomi()
            .WithPower<SongOfPearlsPower>(1)
            .WithPower<CloudsLikeWavesPower>(4);
        Seat.Set(both.Creature, "CurrentHp", 30);

        Assert.Equal(4, global::KleeMod.Relics.TamanooyasCasket.PulseMend(
            both.Creature));
        Assert.Equal(KokomiOverhaulLaw.SongOfPearlsBudget,
                     global::KleeMod.Relics.TamanooyasCasket.PulseBudget(
                         both.Creature));
    }

    [Fact]
    public void Rule4_the_budget_counts_hp_that_landed()
    {
        // The brief's own arithmetic: script A's turn-1 pulse "would Mend 2,
        // but she is at 80, so nothing", and after three effective pulses "the
        // pulse paid 6 of its 8". An ineffective pulse spends nothing.
        var kokomi = Seat.Kokomi().Creature;
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(kokomi);

        Assert.Equal(0, ledger.PulseSpent);
        Assert.Equal(KokomiOverhaulLaw.PulseBudget,
                     global::KleeMod.Relics.TamanooyasCasket.BudgetRemaining(
                         kokomi));

        ledger.NotePulse(0);                      // she was at entry HP
        Assert.Equal(0, ledger.PulseSpent);

        ledger.NotePulse(2);
        ledger.NotePulse(2);
        ledger.NotePulse(2);
        Assert.Equal(6, ledger.PulseSpent);
        Assert.Equal(2, global::KleeMod.Relics.TamanooyasCasket
                          .BudgetRemaining(kokomi));
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Rule4_the_pulse_reads_the_surge_latch_and_the_budget()
    {
        // Structural: the Mend needs a combat. What is pinned is that the relic
        // asks all three questions -- did she Surge, what does the pulse Mend
        // now, and what is left of the budget -- and pays the ledger back only
        // what landed.
        var pulse = typeof(global::KleeMod.Relics.TamanooyasCasket)
            .GetMethod("BeforeSideTurnEnd", HeadlessGame.All)!;
        var calls = Il.Calls(pulse);
        Assert.Contains("KokomiOverhaulLedger.For", calls);
        Assert.Contains("KokomiOverhaulLedger.get_SurgedThisTurn", calls);
        Assert.Contains("TamanooyasCasket.PulseMend", calls);
        Assert.Contains("TamanooyasCasket.PulseBudget", calls);
        Assert.Contains("KokomiTide.Mend", calls);
        Assert.Contains("KokomiOverhaulLedger.NotePulse", calls);
    }

    // ---- THE MEND RULE, and the Rare that breaks it ----------------------

    [Fact]
    public void The_mend_ceiling_is_the_hp_she_walked_in_with()
    {
        var kokomi = Seat.Kokomi(maxHp: 80).Creature;
        Seat.Set(kokomi, "CurrentHp", 62);
        KokomiOverhaulLedger.ResetAll();

        KokomiOverhaulLedger.OpenCombat(kokomi);
        Assert.Equal(62, KokomiOverhaulLedger.For(kokomi).EntryHp);

        // Nothing inside the fight moves it, which is what makes rest sites
        // hers (brief sec.14).
        Seat.Set(kokomi, "CurrentHp", 30);
        Assert.Equal(62, KokomiOverhaulLedger.For(kokomi).EntryHp);
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_cap_and_sango_isshin_live_in_one_place()
    {
        // Structural, and the reason it is worth pinning: the excess only
        // exists at the moment the cap is applied, so the Rare that converts it
        // has to sit exactly there. A hook would have to recompute "would have
        // gone past", which is the drift this arrangement makes impossible.
        var mend = Tide("Mend");
        var calls = Il.Calls(mend);
        Assert.Contains("KokomiOverhaulLedger.get_EntryHp", calls);
        Assert.Contains("CreatureCmd.Heal", calls);
        Assert.Contains("SangoIsshinPower.Overflow", calls);

        // And nothing else applies the cap, so no Mend can skip it.
        var others = typeof(KokomiTide).GetMethods(HeadlessGame.All)
            .Where(m => m.Name != "Mend"
                        && Il.Calls(m).Contains("CreatureCmd.Heal"))
            .Select(m => m.Name)
            .ToList();
        Assert.Empty(others);
    }

    // ---- RULE 5: Exert ---------------------------------------------------

    [Fact]
    public void Rule5_exert_is_damage_and_not_an_hp_loss()
    {
        // The one word that IS the rule. The mod's shipped self-cost walks past
        // Block on purpose (`Unblockable | Unpowered`, Hot Hands); Exert must
        // not, because the brief's contested thing is that a Block card is
        // worth two things and she picks which. The ValueProp itself is an
        // enum literal and invisible to an IL call scan, so the source-level
        // half of this pin lives in tier0/tests/test_kokomi_overhaul.py.
        Assert.Contains("CreatureCmd.Damage", Il.Calls(Tide("Exert")));
    }

    // ---- RULE 6: the Garment ---------------------------------------------

    [Fact]
    public void Rule6_the_garment_pays_once_per_attack_that_hit()
    {
        var kokomi = Seat.Kokomi().WithPower<ProtoGarmentPower>(2);
        var garment = kokomi.Creature.Powers.OfType<ProtoGarmentPower>().First();

        // An Attack that hit nothing pays nothing: the latch is never raised.
        Assert.False(garment.AttackHitPending);

        garment.NoteAttackHit();
        Assert.True(garment.AttackHitPending);
        // A three-hit Attack raises the same latch three times and still pays
        // once -- which is why the Mend is spent in AfterCardPlayed and not in
        // the damage hook.
        garment.NoteAttackHit();
        Assert.True(garment.AttackHitPending);
    }

    [Fact]
    public void Rule6_the_garment_mends_through_the_one_capped_mend()
    {
        var pay = typeof(ProtoGarmentPower)
            .GetMethod("AfterCardPlayed", HeadlessGame.All)!;
        Assert.Contains("KokomiTide.Mend", Il.Calls(pay));
    }

    // ---- RULE 7: Strength becomes Tide -----------------------------------

    [Fact]
    public void Rule7_strength_becomes_tide_at_the_shared_chokepoint()
    {
        // The brief's sec.6.5 names this seam as "how any shared Strength
        // source in the mod reaches her without a card", so it has to be the
        // chokepoint every source flows through rather than a card.
        var hook = typeof(KokomiResourceHooks)
            .GetMethod("TryModifyPowerAmountReceived", HeadlessGame.All)!;
        var calls = Il.Calls(hook);
        Assert.Contains("KokomiOverhaul.LiveFor", calls);
        Assert.Contains("KokomiTide.GainImmediate", calls);
        // And the shipped conversion is still there for a flag-off run.
        Assert.Contains("KokomiResources.GainCharge", calls);
    }

    // ---- RULE 8: the Plan ------------------------------------------------

    [Fact]
    public void Rule8_plans_resolve_at_her_turn_start_in_order()
    {
        var resolve = typeof(ProtoBakeKuragePower)
            .GetMethod("AfterPlayerTurnStart", HeadlessGame.All)!;
        Assert.Contains("KokomiPlan.ResolveAll", Il.Calls(resolve));

        // THE QUEUE IS DRAINED BEFORE THE FIRST CLAUSE RUNS, so a Plan written
        // during resolution waits for the next turn like every other.
        var all = typeof(KokomiPlan)
            .GetMethod("ResolveAll", HeadlessGame.All)!;
        var calls = Il.CallSequence(all).ToList();
        Assert.True(calls.IndexOf("List`1.Clear")
                    < calls.IndexOf("KokomiPlan.ResolveOne"));
    }

    [Fact]
    public void Rule8_the_seven_planned_clauses_are_the_slices_seven()
    {
        // A card cannot schedule anything else: the enum IS the whitelist the
        // codegen validates a `plan:` body against.
        Assert.Equal(
            new[] { "Draw", "Energy", "DamageRandomEnemy", "DamageStoredTarget",
                    "Block", "Mend", "PlayTopOfDraw" },
            System.Enum.GetNames(typeof(KokomiPlan.Kind)));
    }

    [Fact]
    public void The_art_of_war_resolves_a_plan_now_as_well_as_next_turn()
    {
        // "ALSO happen now" taken at its word: the clause happens now AND is
        // still queued. Reading it as "instead" would delete rule 8 rather than
        // break it, and the brief's gloss is "Rule 8's delay is gone".
        var schedule = typeof(KokomiPlan)
            .GetMethod("Schedule", HeadlessGame.All)!;
        var calls = Il.CallSequence(schedule).ToList();
        Assert.Contains("List`1.Add", calls);
        Assert.Contains("KokomiPlan.ResolveOne", calls);
        Assert.True(calls.IndexOf("List`1.Add")
                    < calls.IndexOf("KokomiPlan.ResolveOne"));
    }

    [Fact]
    public void Treatise_fires_once_per_clause_and_only_on_her_own_plans()
    {
        var listener = typeof(TreatisePower)
            .GetMethod("OnPlanResolved", HeadlessGame.All)!;
        Assert.Contains("CardPileCmd.Draw", Il.Calls(listener));
        // The bus rings once per clause, from the one place a clause resolves.
        var one = typeof(KokomiPlan).GetMethod("ResolveOne", HeadlessGame.All)!;
        Assert.Contains("IKokomiPlanListener.OnPlanResolved", Il.Calls(one));
    }

    // ---- the Commander's two powers --------------------------------------

    [Fact]
    public void The_generals_banner_reads_the_first_companion_of_the_turn()
    {
        var kokomi = Seat.Kokomi().Creature;
        KokomiOverhaulLedger.ResetAll();
        var ledger = KokomiOverhaulLedger.For(kokomi);
        ledger.RollTo(3);

        Assert.Equal(0, ledger.CompanionsPlayedThisTurn);
        ledger.NoteCompanionPlayed();
        Assert.Equal(1, ledger.CompanionsPlayedThisTurn);

        // A new turn is a new first.
        ledger.RollTo(4);
        Assert.Equal(0, ledger.CompanionsPlayedThisTurn);
        KokomiOverhaulLedger.ResetAll();
    }

    [Fact]
    public void Vanguard_zeroes_rather_than_discounts()
    {
        // The card prints "costs 0", so the grant SETS rather than subtracts; a
        // subtraction would be a different card on an expensive Companion.
        var hook = typeof(NextCompanionFreePower)
            .GetMethod("TryModifyEnergyCostInCombat", HeadlessGame.All)!;
        // Structural, because the modifier needs a real CardModel with an
        // owner: what is pinned is that the body carries no subtraction at all,
        // unlike the shipped CompanionCostThisTurnPower it is modelled on.
        Assert.DoesNotContain("Math.Max", Il.Calls(hook));
        Assert.Contains("Math.Max",
                        Il.Calls(typeof(CompanionCostThisTurnPower)
                            .GetMethod("TryModifyEnergyCostInCombat",
                                       HeadlessGame.All)!));
    }

    // ---- the roster ------------------------------------------------------

    [Fact]
    public void The_starter_is_ten_cards_and_the_pool_is_twenty_eight()
    {
        // Read off the IL rather than by building the models, which needs
        // ModelDb: `ModelDb.Card<T>()` throws until the game's pool build has
        // run (see PrototypeRoster's own header for the poisoned-type trap).
        // The roster type is `internal`, so it is reached the way every other
        // internal seam in this file is: by name, through the harness.
        var deck = Il.Method("KokomiOverhaulRoster", "StartingDeck");
        Assert.Equal(10, Il.CallSequence(deck)
            .Count(c => c.StartsWith("ModelDb.Card")));

        // EB-284 split the pool in two: `Slice` is the packet's 28 rows and
        // `OfferablePool` is that plus the Ancient tail below, so the count
        // the packet states is asked of the list that states it.
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
        //
        // Structural, because building the models needs `ModelDb`: what is
        // pinned is that the pool reads the SAME ledger the shipped pool reads
        // (`tools/lint_ancient_coverage.py` owns the rest of the invariant --
        // that the ledger is non-empty and every class in it is Ancient).
        var pool = Il.Method("KokomiOverhaulRoster", "OfferablePool");
        Assert.Contains("RosterAncientCards.get_Kokomi", Il.Calls(pool));
        Assert.Contains("KokomiOverhaulRoster.Slice", Il.Calls(pool));
    }
}
