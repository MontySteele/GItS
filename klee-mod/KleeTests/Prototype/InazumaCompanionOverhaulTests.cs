using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE INAZUMA COMPANION OVERHAUL -- twenty-four rows on the arm's existing
/// flag (sim twin <c>tier0/tests/test_inazuma_companion_overhaul.py</c>).
///
/// Compiled only under <c>-p:PrototypeCards=true</c>, the same switch that
/// compiles the arm.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, on the terms
/// <c>CompanionOverhaulHookTests</c> sets: a PURE reader can be called
/// headlessly against a <see cref="Seat"/> holding real powers and is asserted
/// for real; RESOLUTION cannot (<c>PowerCmd</c>, <c>ElementalHit</c> and a live
/// <c>CombatState</c> are outside the headless boundary), so the firing ORDER
/// and the mutating halves are pinned off the compiled method and labelled
/// STRUCTURAL. The arithmetic those hooks perform is asserted for real in the
/// sim twin, against the same constants.
/// </summary>
public class InazumaCompanionOverhaulTests
{
    private const BindingFlags All = HeadlessGame.All;

    private static ValueProp Attack => ValueProp.Move;   // IsPoweredAttack()

    /// <summary>The twenty-four rows, by class, in the workshop's sec.3
    /// character order.</summary>
    private static readonly Type[] Rows =
    {
        typeof(ProtoMiGorouInuzaka),
        typeof(ProtoMiGorouWarBanner),
        typeof(ProtoMiGorouJuuga),
        typeof(ProtoMiSayuFuuinDash),
        typeof(ProtoMiSayuDaruma),
        typeof(ProtoMiSayuNaptime),
        typeof(ProtoMiShinobuSanctifyingRing),
        typeof(ProtoMiShinobuGrassRing),
        typeof(ProtoMiShinobuThundergrust),
        typeof(ProtoMiThomaBlazingBarrier),
        typeof(ProtoMiThomaCrimsonOoyoroi),
        typeof(ProtoMiSaraCrowfeatherCover),
        typeof(ProtoMiSaraTenguStormcall),
        typeof(ProtoMiIttoSuperlativeSuperstrength),
        typeof(ProtoMiRaidenMusouNoHitotachi),
        typeof(ProtoMiKazuhaSlash),
        typeof(ProtoMiYaeSesshouSakura),
        typeof(ProtoMiYoimiyaAurousBlaze),
        typeof(ProtoMiAyakaSoumetsu),
        typeof(ProtoMiAyatoKyouka),
        typeof(ProtoMiHeizouHeartstopper),
        typeof(ProtoMiKiraraSurpriseDispatch),
        typeof(ProtoMiMizukiAnraku),
        typeof(ProtoMiChioriHasode),
    };

    /// <summary>The fifteen powers the arm adds, by class.</summary>
    private static readonly Type[] NewPowers =
    {
        typeof(WarBannerPower), typeof(JuugaPower),
        typeof(MujiMujiDarumaPower), typeof(NaptimePower),
        typeof(SanctifyingRingPower), typeof(BlazingBarrierPower),
        typeof(CrimsonOoyoroiPower), typeof(CrowfeatherCoverPower),
        typeof(TenguStormcallPower), typeof(SesshouSakuraPower),
        typeof(AurousBlazePower), typeof(SoumetsuPower), typeof(KyoukaPower),
        typeof(SurpriseDispatchPower), typeof(TamotoPower),
    };

    // ---- THE ROWS -------------------------------------------------------

    [Fact]
    public void The_twenty_four_are_offerable_inazuma_universals()
    {
        Assert.Equal(24, Rows.Length);
        foreach (var type in Rows)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            var comp = Assert.IsAssignableFrom<ICompanionCard>(card);
            Assert.Equal("inazuma", comp.Nation);
            Assert.Null(comp.PersonalPool);     // no Personal, no stand-in
            Assert.True(comp.Star == 4 || comp.Star == 5,
                $"{type.Name}: star {comp.Star}");
            Assert.NotEqual(CardRarity.Basic, card.Rarity);
        }
    }

    [Fact]
    public void The_rarity_split_is_the_workshops_enumeration()
    {
        // 9 Common, 11 Uncommon, 4 Rare. The document's sec.4 prints "12
        // Uncommon" and counts Gorou's Kokomi-side PERSONAL among them; a
        // Personal is not a Universal and is not built, so the Universals'
        // own split is one short in that tier. Pinned so the discrepancy is a
        // recorded fact rather than a miscount somebody re-derives later.
        var byRarity = Rows
            .Select(t => ((CardModel)Activator.CreateInstance(t)!).Rarity)
            .GroupBy(r => r)
            .ToDictionary(g => g.Key, g => g.Count());
        Assert.Equal(9, byRarity[CardRarity.Common]);
        Assert.Equal(11, byRarity[CardRarity.Uncommon]);
        Assert.Equal(4, byRarity[CardRarity.Rare]);
    }

    [Fact]
    public void The_roster_replaces_two_nations_and_carries_both_workshops()
    {
        // The compiler already holds the roster -> class direction (a deleted
        // row stops the build); this is the count, and the acceptance
        // condition for "no row was left out".
        var inazuma = Il.Method("CompanionOverhaulRoster", "InazumaUniversals");
        var referenced = Il.CallSequence(inazuma)
            .Count(c => c.StartsWith("ModelDb.Card"));
        Assert.Equal(24, referenced);

        var mondstadt = Il.Method("CompanionOverhaulRoster", "Universals");
        Assert.Equal(34, Il.CallSequence(mondstadt)
            .Count(c => c.StartsWith("ModelDb.Card")));
    }

    [Fact]
    public void Yoimiyas_mark_is_the_one_row_that_aims_at_a_chosen_enemy()
    {
        // "MARK AN ENEMY for 2 turns. Whenever IT takes damage ..." names a
        // chosen body twice over, so the body holds the mark -- the seam
        // Barbara's loop and Eula's blade opened. Every other Inazuma row
        // either hits (and aims through its damage op) or lands on the player.
        var mark = (CardModel)Activator.CreateInstance(
            typeof(ProtoMiYoimiyaAurousBlaze))!;
        Assert.Equal(TargetType.AnyEnemy, mark.TargetType);
        Assert.Equal(CardType.Skill, mark.Type);
    }

    [Fact]
    public void Kirara_is_the_one_row_that_declares_no_element()
    {
        // She is Dendro; this engine has six elements and no Dendro aura, and
        // her card names no element at all. Element.None is the honest
        // rendering -- inventing one of the six would be a design decision
        // wearing a schema default.
        var kirara = (ICompanionCard)Activator.CreateInstance(
            typeof(ProtoMiKiraraSurpriseDispatch))!;
        Assert.Equal(Element.None, kirara.CompanionElement);
        foreach (var type in Rows.Where(
                     t => t != typeof(ProtoMiKiraraSurpriseDispatch)))
        {
            var comp = (ICompanionCard)Activator.CreateInstance(type)!;
            Assert.NotEqual(Element.None, comp.CompanionElement);
        }
    }

    [Fact]
    public void The_war_banner_grants_real_dexterity_and_the_clock_beside_it()
    {
        // STRUCTURAL, and it is the row's whole argument: the card says
        // Dexterity, and Dexterity is a thing this engine already has -- so it
        // applies the base game's own power and a second, private CLOCK that
        // takes those two stacks back when it runs out.
        var play = typeof(ProtoMiGorouWarBanner).GetMethod("OnPlay", All)!;
        // CallSequence, not Calls: only the ordered reader names a generic
        // method's type argument, and the type argument IS the assertion here.
        var applies = Il.CallSequence(play)
            .Where(c => c.StartsWith("PowerCmd.Apply")).ToList();
        Assert.Equal(2, applies.Count);
        Assert.Contains(applies, c => c.Contains("DexterityPower"));
        Assert.Contains(applies, c => c.Contains("WarBannerPower"));
    }

    [Fact]
    public void Shinobus_ring_is_paid_in_plain_hp_and_not_in_exert()
    {
        // "Lose 3 HP" is plain HP loss. This engine spells that
        // Unblockable|Unpowered self-damage -- the shipped Hot Hands line --
        // and NOT `exert`, which is Kokomi's rule and is eaten by Block.
        var play = typeof(ProtoMiShinobuSanctifyingRing).GetMethod("OnPlay", All)!;
        var calls = Il.Calls(play);
        Assert.Contains(calls, c => c.Contains("CreatureCmd.Damage"));
        Assert.DoesNotContain(calls, c => c.Contains("KokomiTide.Exert"));
    }

    [Fact]
    public void Mizukis_snack_is_the_one_row_that_mends()
    {
        // And it goes through KokomiTide.Mend -- the ONE place "never above
        // the HP you entered the fight with" is written. A second Mend for the
        // companion pool is exactly what this asserts did not happen.
        var play = typeof(ProtoMiMizukiAnraku).GetMethod("OnPlay", All)!;
        Assert.Contains(Il.Calls(play), c => c.Contains("KokomiTide.Mend"));

        foreach (var type in Rows.Where(t => t != typeof(ProtoMiMizukiAnraku)))
        {
            var other = type.GetMethod("OnPlay", All);
            if (other == null) continue;
            Assert.DoesNotContain(Il.Calls(other),
                c => c.Contains("KokomiTide.Mend"));
        }
    }

    [Fact]
    public void Mend_asks_whether_either_arm_is_live_for_this_creature()
    {
        // THE ONE LINE THAT MOVED for the companion arm. The rule below it is
        // unchanged and unduplicated; what widened is the gate, because
        // Mizuki's row is a UNIVERSAL and Klee or Furina can draft it.
        var mend = Il.Method("KokomiTide", "Mend");
        Assert.Contains(Il.Calls(mend), c => c.Contains("MendIsLive"));

        var live = Il.Method("KokomiTide", "MendIsLive");
        var calls = Il.Calls(live);
        Assert.Contains(calls, c => c.Contains("KokomiOverhaul.LiveFor"));
        Assert.Contains(calls, c => c.Contains("CompanionOverhaul.get_Enabled"));
    }

    [Fact]
    public void Gorou_opens_the_play_total_before_he_banks_half_of_it()
    {
        // The ledger has to start at zero when the play does, or the card
        // banks the last card's damage. Emitted only for a row that asks --
        // the same arrangement Kokomi's `BeginPlay` has.
        var play = typeof(ProtoMiGorouInuzaka).GetMethod("OnPlay", All)!;
        var sequence = Il.CallSequence(play).ToList();
        var open = sequence.FindIndex(c => c.Contains("BeginPlay"));
        var bank = sequence.FindIndex(c => c.Contains("BlockHalfDamage"));
        Assert.True(open >= 0, "the play total is never opened");
        Assert.True(bank > open, "the half is banked before the play opens");

        foreach (var type in Rows.Where(t => t != typeof(ProtoMiGorouInuzaka)))
        {
            var other = type.GetMethod("OnPlay", All);
            if (other == null) continue;
            Assert.DoesNotContain(Il.Calls(other),
                c => c.Contains("CompanionOverhaulLedger") && c.Contains("BeginPlay"));
        }
    }

    [Fact]
    public void Chiori_is_the_one_hit_that_ignores_block()
    {
        // STRUCTURAL: `ignoreBlock` is one optional flag on ElementalHit.Deal,
        // defaulted false, so every other caller in the mod is byte-identical.
        var volley = Il.Method("TamotoPower", "FireVolley");
        Assert.Contains(Il.Calls(volley), c => c.Contains("ElementalHit.Deal"));

        var deal = Il.Method("ElementalHit", "Deal");
        Assert.Equal(6, deal.GetParameters().Length);
        Assert.True(deal.GetParameters()[5].HasDefaultValue);
        Assert.Equal(false, deal.GetParameters()[5].DefaultValue);
    }

    // ---- THE POWERS -----------------------------------------------------

    [Fact]
    public void Every_new_power_is_a_counter()
    {
        foreach (var type in NewPowers)
        {
            var power = (PowerModel)Activator.CreateInstance(type)!;
            Assert.Equal(PowerStackType.Counter, power.StackType);
        }
    }

    [Fact]
    public void The_mark_is_the_one_debuff_because_it_sits_on_an_enemy()
    {
        Assert.Equal(PowerType.Debuff,
            ((PowerModel)Activator.CreateInstance(typeof(AurousBlazePower))!).Type);
        foreach (var type in NewPowers.Where(t => t != typeof(AurousBlazePower)))
        {
            Assert.Equal(PowerType.Buff,
                ((PowerModel)Activator.CreateInstance(type)!).Type);
        }
    }

    [Theory]
    [InlineData(typeof(WarBannerPower), CompanionOverhaulLaw.WarBannerDexterity)]
    [InlineData(typeof(JuugaPower), CompanionOverhaulLaw.JuugaDamage)]
    [InlineData(typeof(MujiMujiDarumaPower), CompanionOverhaulLaw.DarumaDamage)]
    [InlineData(typeof(MujiMujiDarumaPower), CompanionOverhaulLaw.DarumaBlock)]
    [InlineData(typeof(SanctifyingRingPower), CompanionOverhaulLaw.SanctifyingRingDamage)]
    [InlineData(typeof(BlazingBarrierPower), CompanionOverhaulLaw.BlazingBarrierBlock)]
    [InlineData(typeof(CrimsonOoyoroiPower), CompanionOverhaulLaw.OoyoroiDamage)]
    [InlineData(typeof(TenguStormcallPower), CompanionOverhaulLaw.StormcallBonus)]
    [InlineData(typeof(SesshouSakuraPower), CompanionOverhaulLaw.SakuraDamage)]
    [InlineData(typeof(SesshouSakuraPower), CompanionOverhaulLaw.SakuraBonus)]
    [InlineData(typeof(AurousBlazePower), CompanionOverhaulLaw.AurousBlazeDamage)]
    [InlineData(typeof(SoumetsuPower), CompanionOverhaulLaw.SoumetsuDamage)]
    [InlineData(typeof(SoumetsuPower), CompanionOverhaulLaw.SoumetsuFinale)]
    [InlineData(typeof(KyoukaPower), CompanionOverhaulLaw.KyoukaDamage)]
    [InlineData(typeof(KyoukaPower), CompanionOverhaulLaw.KyoukaFinale)]
    [InlineData(typeof(SurpriseDispatchPower), CompanionOverhaulLaw.SurpriseDispatchDamage)]
    [InlineData(typeof(TamotoPower), CompanionOverhaulLaw.TamotoDamage)]
    public void Every_power_face_prints_the_number_it_pays(Type type, int number)
    {
        // FACE FROM BODY at the power level: the description interpolates the
        // CompanionOverhaulLaw constant the hook spends, so a retune moves
        // both or neither.
        var power = (ILocalizationProvider)Activator.CreateInstance(type)!;
        var description = power.Localization!
            .Single(entry => entry.Item1 == "description").Item2;
        Assert.Contains(number.ToString(), description);
    }

    // ---- THE PURE READERS, FOR REAL -------------------------------------

    [Fact]
    public void The_two_new_riders_pay_and_stack_with_mondstadts_three()
    {
        // Five riders now say "deals N more" and none excludes another -- the
        // sim sums all five in `flat_attack_bonus` and the engine folds every
        // ModifyDamageAdditive. Same answer, and the pin is the sum.
        var seat = Seat.Klee()
            .WithPower<PassionOverloadPower>(4)
            .WithPower<LightningFangPower>(2)
            .WithPower<CrowfeatherCoverPower>(4)
            .WithPower<KyoukaPower>(2);
        var card = new ProtoMiShinobuThundergrust();
        var target = Seat.Klee().Creature;      // any body that is not us
        var total = seat.Creature.Powers
            .Sum(p => p.ModifyDamageAdditive(
                target, 10m, Attack, seat.Creature, card, null));
        Assert.Equal(4 + CompanionOverhaulLaw.LightningFangDamage
                     + 4 + CompanionOverhaulLaw.KyoukaDamage, total);
    }

    [Fact]
    public void Kyoukas_rider_is_the_constant_and_not_its_clock()
    {
        // Amount is TURNS REMAINING, so a second copy makes the window longer
        // and never the hits bigger -- the arm's standing rule for a timed
        // power, and the difference from Crowfeather's stack, which IS the
        // number.
        var seat = Seat.Klee().WithPower<KyoukaPower>(9);
        var power = seat.Creature.Powers.OfType<KyoukaPower>().Single();
        var card = new ProtoMiShinobuThundergrust();
        Assert.Equal(CompanionOverhaulLaw.KyoukaDamage,
            power.ModifyDamageAdditive(
                Seat.Klee().Creature, 10m, Attack, seat.Creature, card, null));
    }

    [Fact]
    public void A_new_rider_pays_nothing_on_a_skill_or_someone_elses_hit()
    {
        var seat = Seat.Klee().WithPower<CrowfeatherCoverPower>(4);
        var power = seat.Creature.Powers.OfType<CrowfeatherCoverPower>().Single();
        var other = Seat.Klee().Creature;
        var skill = new ProtoMiThomaBlazingBarrier();        // a Skill
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, seat.Creature, skill, null));
        var attack = new ProtoMiShinobuThundergrust();
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, Attack, other, attack, null));       // not our hit
        Assert.Equal(0m, power.ModifyDamageAdditive(
            other, 10m, ValueProp.Unpowered, seat.Creature, attack, null));
    }

    [Fact]
    public void The_element_funnel_orders_the_two_new_riders_by_tier()
    {
        // BLANKET FIRST, ONE-SHOTS AFTER, LAST WINS. Ayato's Kyouka is a
        // blanket and Sara's Crowfeather is a one-shot, so the one-shot beats
        // it -- the more specific claim, which is the rule the funnel already
        // kept for Bennett over Razor.
        var card = new ProtoMiShinobuThundergrust();         // prints Electro

        var kyouka = Seat.Klee().WithPower<KyoukaPower>(2);
        Assert.Equal(Element.Hydro,
            CompanionOverhaulRiders.ElementFor(card, kyouka.Creature));

        var both = Seat.Klee()
            .WithPower<KyoukaPower>(2)
            .WithPower<CrowfeatherCoverPower>(4);
        Assert.Equal(Element.Electro,
            CompanionOverhaulRiders.ElementFor(card, both.Creature));

        // And Varka's banked Swirl is still last of all five.
        var swirl = Seat.Klee()
            .WithPower<KyoukaPower>(2)
            .WithPower<CrowfeatherCoverPower>(4)
            .WithPower<SwirlChargePower>(6);
        swirl.Creature.Powers.OfType<SwirlChargePower>().Single()
            .Remember(Element.Cryo);
        Assert.Equal(Element.Cryo,
            CompanionOverhaulRiders.ElementFor(card, swirl.Creature));
    }

    [Fact]
    public void The_ledger_counts_swirls_and_a_plays_damage_and_rolls_both()
    {
        var seat = Seat.Klee().WithCombatState();
        var ledger = CompanionOverhaulLedger.For(seat.Creature);
        ledger.BeginPlay();
        ledger.NoteDamage(7);
        ledger.NoteDamage(0);                 // a blocked hit banks nothing
        ledger.NoteDamage(5);
        Assert.Equal(12, ledger.DamageDealtThisPlay);
        ledger.BeginPlay();
        Assert.Equal(0, ledger.DamageDealtThisPlay);

        ledger.NoteSwirl();
        ledger.NoteSwirl();
        Assert.Equal(2, ledger.SwirlsThisTurn);
        ledger.NoteDamage(9);
        ledger.RollTo(ledger.GetHashCode());  // any round that is not this one
        Assert.Equal(0, ledger.SwirlsThisTurn);
        Assert.Equal(0, ledger.DamageDealtThisPlay);
        CompanionOverhaulLedger.ResetAll();
    }

    [Fact]
    public void The_swirl_count_is_taken_at_the_one_reaction_site()
    {
        // Beside Varka's latch, off the same event, so "a Swirl happened" has
        // one definition in this engine and the two readers cannot disagree.
        var note = Il.Method("CompanionOverhaulReactions", "Note");
        Assert.Contains(Il.Calls(note), c => c.Contains("NoteSwirl"));
    }

    // ---- THE ORDER IS LAW ------------------------------------------------

    [Fact]
    public void The_end_of_turn_walk_runs_the_inazuma_block_before_the_latch()
    {
        // Shinobu's ring GRANTS Block and Nicole's latch asks whether the
        // player ended the turn holding any, so the whole Inazuma block has to
        // sit before it. The sim twin asserts the same sequence off its own
        // source; this is the mod's half.
        var walk = Il.Method("CompanionOverhaulTurnEnd", "AfterSideTurnEnd");
        var seen = Il.CallSequence(walk)
            .Where(c => c.Contains("OfType"))
            .ToList();
        var mondstadt = seen.FindIndex(c => c.Contains("SolarIsotomaBloomPower"));
        var first = seen.FindIndex(c => c.Contains("JuugaPower"));
        var ring = seen.FindIndex(c => c.Contains("SanctifyingRingPower"));
        var latch = seen.FindIndex(c => c.Contains("RevelationPower"));
        Assert.True(mondstadt >= 0 && first > mondstadt,
            "the Inazuma block runs after the Mondstadt six");
        Assert.True(ring > first,
            "the sequence is the workshop's own sec.3 character order");
        Assert.True(latch > ring, "Nicole's latch must stay last of all");
    }

    [Fact]
    public void The_incoming_hit_walk_puts_the_barrier_last()
    {
        // Thoma's Blazing Barrier is Diona's paws with a Block payout, and it
        // goes after them for the reason they go after the two traps: it reads
        // the absorption everything above it has already re-priced.
        var walk = Il.Method("CompanionOverhaulIncomingHit", "BeforeDamageReceived");
        var text = string.Join("\n", Il.CallSequence(walk));
        Assert.True(
            text.IndexOf("BlazingBarrierPower", StringComparison.Ordinal)
            > text.IndexOf("IcyPawsPower", StringComparison.Ordinal),
            "the barrier must read the absorption the paws have already priced");
    }

    [Fact]
    public void The_play_watcher_totals_only_card_sourced_damage_it_dealt()
    {
        // STRUCTURAL, and it is what keeps the two engines counting the same
        // thing: the sim adds `hp_dmg` for source in ("card", "attack"), and
        // this arm's power-sourced hits pass neither a dealer nor a card
        // source, so neither engine counts them.
        var hook = Il.Method("CompanionOverhaulPlayWatcher", "AfterDamageReceived");
        Assert.Contains(Il.Calls(hook), c => c.Contains("NoteDamage"));
    }
}
