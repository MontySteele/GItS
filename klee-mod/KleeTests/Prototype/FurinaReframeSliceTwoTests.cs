using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA REFRAME, SLICE TWO -- the five rows the rules finally have
/// (R220 A; <c>review/ruled/furina-reframe-2026-08-29.md</c> sec.6.2, with
/// sec.4.4 the Evoke, sec.4.6 the drain and sec.5 the starter delta). Slice one
/// built the RULES and left the prototype surface with no row that speaks them;
/// <see cref="FurinaReframeRuleTests"/> is that file and this one is its
/// card-side sibling, in the same shape and for the same reasons.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the same split slice one makes
/// (README, "The headless boundary"). REAL, on live objects: the drain
/// arithmetic at every interesting meter value, what the drain leaves alone,
/// the preview-versus-resolved answer that makes the printed number and the
/// landed number one number, the per-play record's lifecycle, the Encore gate's
/// refusal, and each row's identity and price. STRUCTURAL, read off the
/// compiled method: anything that RESOLVES -- a bow, a deploy, an Attack --
/// needs a combat this harness cannot build, so what is pinned is the wiring:
/// which verb each row's body calls and which of them carries an aim.
///
/// THE ONE FACT NO C# PIN CAN MAKE. `SalonMember.Chevalmarin` and
/// `SalonMember.Crabaletta` are compiled into the emitted bodies as enum
/// operands, and <see cref="Il.Calls"/> reads call TOKENS -- it can say the row
/// calls <c>BowLeftmost</c>, never which member it names. WHICH member is
/// therefore pinned on the python side, off the emitted source, in
/// <c>tier0/tests/test_furina_reframe_slice2.py</c>; the two halves are named
/// in each other's comments so neither can be deleted quietly.
/// </summary>
public class FurinaReframeSliceTwoTests
{
    // ==================================================================
    // Fixtures
    // ==================================================================

    /// <summary>Slice one's fixture, verbatim, and for its reason: the five
    /// flags are static, so a test that moved one and did not restore it would
    /// silently arm the next one.</summary>
    private sealed class Arm : IDisposable
    {
        private readonly bool _enabled = FurinaReframe.Enabled;
        private readonly bool _manual = FurinaReframe.ManualEnabled;
        private readonly bool _evoke = FurinaReframe.EvokeEnabled;
        private readonly bool _meter = FurinaReframe.MeterEnabled;
        private readonly bool _spotlight = FurinaReframe.SpotlightEnabled;

        internal Arm(bool manual = false, bool evoke = false, bool meter = false,
                     bool spotlight = false, bool master = true)
        {
            FurinaReframe.Enabled = master;
            FurinaReframe.ManualEnabled = manual;
            FurinaReframe.EvokeEnabled = evoke;
            FurinaReframe.MeterEnabled = meter;
            FurinaReframe.SpotlightEnabled = spotlight;
        }

        public void Dispose()
        {
            FurinaReframe.Enabled = _enabled;
            FurinaReframe.ManualEnabled = _manual;
            FurinaReframe.EvokeEnabled = _evoke;
            FurinaReframe.MeterEnabled = _meter;
            FurinaReframe.SpotlightEnabled = _spotlight;
        }
    }

    /// <summary>A Furina seat with a live combat state and an empty meter, and
    /// with both static tables this slice writes to cleared -- they are keyed on
    /// Creature objects, which outlive a headless fixture.</summary>
    private static Seat Furina(int maxHp = 60)
    {
        FurinaDrain.ResetAll();
        FurinaReframeLedger.ResetAll();
        return Seat.Furina(maxHp).WithCombatState();
    }

    /// <summary>A card in a seat's hand: mutable, owned, and therefore askable.
    /// `IsMutable` first -- Owner's setter calls AssertMutable. Lifted from
    /// <c>MeterCostBadgeTests.Held</c>.</summary>
    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The cap a seat's meter has, which is <c>0.5 x MaxHp</c> and NOT
    /// a constant: the "at the cap" case below has to ask rather than assume,
    /// or a retune of the fraction turns this pin into a test of 30.</summary>
    private static int Cap(Seat seat) => FurinaResources.FanfareCap(seat.Creature);

    /// <summary>Every call token a card TYPE makes, its compiler-generated
    /// lambda classes included.
    ///
    /// <see cref="Il.Calls"/> reads ONE method, and a `CalculatedVar`'s
    /// multiplier is a static lambda: the emitted `get_CanonicalVars` body
    /// carries an `ldftn` to a `&lt;&gt;c` display class and the call this file
    /// cares about is inside THAT method. Walking the declared methods of the
    /// type and of its nested types is the smallest thing that can see it, and
    /// it is enough here because the assertions are "does this row reach X",
    /// where a stray match cannot make a regression pass.</summary>
    private static HashSet<string> AllCalls(Type type)
    {
        var found = new HashSet<string>(StringComparer.Ordinal);
        foreach (var owner in new[] { type }.Concat(
                     type.GetNestedTypes(HeadlessGame.All)))
        {
            foreach (var method in owner.GetMethods(
                         HeadlessGame.All | System.Reflection.BindingFlags.DeclaredOnly))
            {
                found.UnionWith(Il.Calls(method));
            }
        }
        return found;
    }

    private static readonly Type[] TheFive =
    {
        typeof(ProtoFrSalonDebutNamed),
        typeof(ProtoFrCurtainCall),
        typeof(ProtoFrExitStageLeft),
        typeof(ProtoFrLetThePeopleRejoice),
        typeof(ProtoFrIntermission),
    };

    // ==================================================================
    // 0. THE QUARANTINE. Read this section before any other.
    // ==================================================================

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST, and slice one's copy of this
    // comment carries the argument in full: under `-p:FurinaReframe=true` the
    // property MOVES the value this asserts, so green would mean the property
    // did nothing and red would mean it worked. Skipped there rather than left
    // to fail. Arm properties are deploy-line only
    // (docs/current/operations/prototype.md).
#if FURINA_REFRAME
    [Fact(Skip = "-p:FurinaReframe=true moves FurinaReframe.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        // The five rows exist in this build and the rules they print do not.
        Assert.False(FurinaReframe.DefaultEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.Enabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.EvokeEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.ManualEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.MeterEnabled);
    }

    [Fact]
    public void All_five_rows_are_furinas_and_none_is_a_kit_card()
    {
        // `ICharacterCard.CharacterId` is what puts a row in HER off-pool list
        // and what every character-aware mechanic reads. A row that answered
        // "klee" would draw wearing Klee's frame, which is a lie about the
        // thing under test (`PrototypeRoster`'s own note).
        foreach (var type in TheFive)
        {
            var card = (CardModel)Activator.CreateInstance(type)!;
            Assert.Equal("furina", Assert.IsAssignableFrom<ICharacterCard>(card)
                .CharacterId);
        }
    }

    // ==================================================================
    // 1. THE ROWS' BODIES -- structural, one verb each
    // ==================================================================

    [Fact]
    public void Each_row_resolves_through_the_verb_its_face_prints()
    {
        // STRUCTURAL, and the point is that there is no SECOND implementation
        // of any of these rules on a card. A deploy is `SalonMemberPower.Deploy`
        // (which is where the perform clause and the overflow Evoke live), an
        // Evoke is `SalonMemberPower.BowLeftmost` (which is where the Focus
        // multiplier, the mint and the aim live) and a drain is
        // `FurinaDrain.Drain`. A row that grew its own copy of one would drift
        // from the rule the same card's tip describes.
        Assert.Contains("SalonMemberPower.Deploy",
            Il.Calls(Il.Method("ProtoFrSalonDebutNamed", "OnPlay")));

        foreach (var row in new[] { "ProtoFrCurtainCall", "ProtoFrExitStageLeft" })
        {
            var calls = Il.Calls(Il.Method(row, "OnPlay"));
            Assert.Contains("SalonMemberPower.BowLeftmost", calls);
            // ... and NOT the deploy path: an Evoke card must never be able to
            // put a member back on the stage it just emptied.
            Assert.DoesNotContain("SalonMemberPower.Deploy", calls);
        }

        foreach (var row in new[] { "ProtoFrLetThePeopleRejoice",
                                    "ProtoFrIntermission" })
        {
            var calls = Il.Calls(Il.Method(row, "OnPlay"));
            Assert.Contains("FurinaDrain.Drain", calls);
        }
    }

    [Fact]
    public void The_two_drain_rows_read_the_drain_and_never_the_meter()
    {
        // THE DEFECT THIS EXISTS TO STOP, and it is silent in every other
        // reading: `drain_fanfare` empties the meter, so a multiplier bound to
        // `FurinaResources.ReadableFanfare` -- which is what every OTHER Fanfare
        // rider in this mod binds to -- would resolve to 0 on both rows, every
        // time, while the face promised scaling. The var declaration is where
        // that choice is made, so that is what is read.
        foreach (var type in new[] { typeof(ProtoFrLetThePeopleRejoice),
                                     typeof(ProtoFrIntermission) })
        {
            var calls = AllCalls(type);
            Assert.Contains("FurinaDrain.Amount", calls);
            Assert.DoesNotContain("FurinaResources.ReadableFanfare", calls);
        }
    }

    [Fact]
    public void The_aimed_row_is_the_only_one_that_names_a_member()
    {
        // THE C# HALF of the aim pin, and it is deliberately the weaker half:
        // the enum operand is unreadable here (see the class note), so what is
        // asserted is that BOTH Evoke rows go through the ONE verb that takes an
        // aim, and that the verb consults `FurinaReframe.EvokeTargetIndex` --
        // which is the flag-gated resolver, so the aim cannot reach a shipped
        // bow. WHICH member Exit Stage Left names is pinned in
        // `tier0/tests/test_furina_reframe_slice2.py` off the emitted source.
        Assert.Contains("FurinaReframe.EvokeTargetIndex",
            Il.Calls(Il.Method("SalonMemberPower", "BowLeftmost")));

        using var _ = new Arm(evoke: true);
        var seat = Furina();
        var company = new List<SalonMember>
            { SalonMember.Crabaletta, SalonMember.Chevalmarin };

        // The resolver the row's argument lands in, on the board the row is
        // written for: naming Chevalmarin takes the SECOND member, not the
        // front, which is the whole of the slot-6 ruling.
        Assert.Equal(1, FurinaReframe.EvokeTargetIndex(
            seat.Creature, company, SalonMember.Chevalmarin));
        Assert.Equal(0, FurinaReframe.EvokeTargetIndex(
            seat.Creature, company, FurinaReframe.EvokeTargetFront));
        // ... and an absent member is REPORTED, not wasted: Curtain Call's
        // unaimed Evoke is what an aimed one degrades into.
        Assert.Equal(FurinaReframe.EvokeTargetAbsent,
            FurinaReframe.EvokeTargetIndex(
                seat.Creature,
                new List<SalonMember> { SalonMember.Usher },
                SalonMember.Chevalmarin));
    }

    // ==================================================================
    // 2. THE DRAIN -- sec.4.6, real arithmetic at every value that matters
    // ==================================================================

    [Fact]
    public void A_drain_at_zero_takes_nothing_and_is_still_a_play()
    {
        // BOTH ROWS ARE PLAYABLE AT ANY VALUE, including this one: neither
        // carries a `requires` gate, so a drain of nothing is a wasted card the
        // player can see coming from the meter. The ledger says it happened,
        // which is the D4 half -- a meter at 0 because nothing was earned and a
        // meter at 0 because twelve were just spent are the same board a moment
        // later.
        var seat = Furina();

        Assert.Equal(0, FurinaDrain.Drain(seat.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));

        var ledger = FurinaReframeLedger.For(seat.Creature);
        Assert.Equal(1, ledger.Drains);
        Assert.Equal(0, ledger.LastDrained);
    }

    [Fact]
    public void A_drain_at_seventeen_takes_seventeen_and_leaves_nothing()
    {
        var seat = Furina();
        FurinaResources.GainFanfare(seat.Creature, 17);

        Assert.Equal(17, FurinaDrain.Drain(seat.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(17, FurinaReframeLedger.For(seat.Creature).LastDrained);
    }

    [Fact]
    public void A_drain_at_the_cap_takes_the_cap()
    {
        // THE CEILING IS NOT A SECOND RULE. `GainFanfare` clamps at the cap, so
        // over-filling and draining takes exactly the cap and no more -- which
        // is worth pinning rather than assuming, because the drain is the first
        // op in this kit that can move the whole meter in one line.
        var seat = Furina();
        var cap = Cap(seat);
        Assert.True(cap > 0, "a Furina seat with no cap cannot hold Fanfare");

        FurinaResources.GainFanfare(seat.Creature, cap + 50);
        Assert.Equal(cap, FurinaResources.Fanfare(seat.Creature));

        Assert.Equal(cap, FurinaDrain.Drain(seat.Creature));
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
        Assert.Equal(cap, FurinaReframeLedger.For(seat.Creature).TotalDrained);
    }

    [Fact]
    public void A_drain_moves_neither_the_floor_nor_the_cap()
    {
        // THE WHOLE DIFFERENCE FROM `crash_fanfare`, which is the op beside it
        // on the same meter: that card's price IS the falling baseline, and this
        // card's price is the meter itself. A drain that also dropped the floor
        // would be The Final Verdict wearing a different name.
        var seat = Furina();
        FurinaResources.GainFanfareFloor(seat.Creature, 4);
        var floor = FurinaResources.FanfareFloor(seat.Creature);
        var cap = Cap(seat);
        FurinaResources.GainFanfare(seat.Creature, 6);

        FurinaDrain.Drain(seat.Creature);

        Assert.Equal(floor, FurinaResources.FanfareFloor(seat.Creature));
        Assert.Equal(cap, Cap(seat));
    }

    [Fact]
    public void A_debt_cannot_be_drained()
    {
        // Track C.2 leaves the meter below zero on purpose and every reader in
        // this mod clamps at zero (`ReadableFanfare`). So a drain finds nothing
        // to take, takes nothing, and LEAVES THE HOLE -- paying a card for a
        // debt would make the settle a resource rather than a price.
        var seat = Furina();
        FurinaResources.DropFanfareToFloor(seat.Creature, 5);
        var held = FurinaResources.Fanfare(seat.Creature);

        Assert.Equal(0, FurinaDrain.Drain(seat.Creature));
        Assert.Equal(held, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void The_drain_is_scoped_to_furina()
    {
        // Every leg of this arm is character-scoped and so is this: in co-op the
        // other seat may be Klee, and a bare mutation would empty a meter he
        // does not have.
        FurinaDrain.ResetAll();
        var klee = Seat.Klee().WithCombatState();

        Assert.Equal(0, FurinaDrain.Drain(klee.Creature));
    }

    // ==================================================================
    // 3. ONE VALUE PATH -- the previewed number IS the landed number
    // ==================================================================

    [Fact]
    public void A_card_in_hand_previews_the_drain_it_would_make()
    {
        // The multiplier both rows bind to is called BOTH while the card sits
        // in hand and again as it resolves. In hand, with no play in flight, the
        // honest answer is the live meter -- otherwise the Rare would read
        // "Deal 5 damage" on a full meter and land for far more.
        var seat = Furina();
        var card = Held<ProtoFrLetThePeopleRejoice>(seat);
        FurinaResources.GainFanfare(seat.Creature, 9);

        Assert.Equal(9, FurinaDrain.Amount(card));
    }

    [Fact]
    public void The_same_read_after_the_drain_is_the_number_it_took()
    {
        // ... and this is the half a live meter read cannot do: the drain has
        // already emptied the meter by the time the hit resolves, so the count
        // has to be the RECORD. Same method, same card, two answers, one number.
        var seat = Furina();
        var card = Held<ProtoFrIntermission>(seat);
        FurinaResources.GainFanfare(seat.Creature, 12);

        Assert.Equal(12, FurinaDrain.Amount(card));      // in hand
        FurinaDrain.Drain(seat.Creature);
        Assert.Equal(12, FurinaDrain.Amount(card));      // mid-resolution
        Assert.Equal(0, FurinaResources.Fanfare(seat.Creature));
    }

    [Fact]
    public void A_new_card_play_wipes_the_record_before_anything_reads_it()
    {
        // THE STALE-PREVIEW GUARD, and it is why the record is opened per play
        // rather than closed per drain: a drain row drawn again later must
        // preview the live meter, not the number it took last time.
        var seat = Furina();
        var card = Held<ProtoFrIntermission>(seat);
        FurinaResources.GainFanfare(seat.Creature, 12);
        FurinaDrain.Drain(seat.Creature);
        Assert.Equal(12, FurinaDrain.Amount(card));

        FurinaDrain.BeginPlay(seat.Creature);

        Assert.Equal(0, FurinaDrain.Amount(card));
        FurinaResources.GainFanfare(seat.Creature, 3);
        Assert.Equal(3, FurinaDrain.Amount(card));
    }

    [Fact]
    public void The_record_is_opened_by_the_shipped_play_hook()
    {
        // STRUCTURAL, on the seam: the clear rides `BeforeCardPlayed`, which is
        // the same hook the shipped Encore spend uses and which runs before
        // `OnPlay`. A clear that lived anywhere else would be a lifecycle
        // nothing enforces.
        Assert.Contains("FurinaDrain.BeginPlay",
            Il.Calls(Il.Method("FurinaResourceHooks", "BeforeCardPlayed")));
    }

    [Fact]
    public void A_card_nobody_owns_reads_nothing()
    {
        // A card with no owner reads 0 rather than throwing: an NRE inside a
        // CalculatedVar multiplier is a black screen, not an exception anyone
        // sees. The unowned card here is MUTABLE, which is the honest state to
        // ask about -- `CardModel.Owner`'s getter asserts mutability, so an
        // IMMUTABLE canonical copy throws before this method is reached, and it
        // does so identically for every shipped Fanfare rider in the mod
        // (`card.Owner.Creature` is what `fanfare_calc_rider` emits). This is
        // not a defect this slice introduced and it is not one it hides.
        var loose = new ProtoFrIntermission();
        Seat.Set(loose, "IsMutable", true);

        Assert.Equal(0, FurinaDrain.Amount(loose));
        Assert.Equal(0, FurinaDrain.Amount(null));
    }

    // ==================================================================
    // 4. THE EVOKE PRICE -- F7 (1), shipped machinery, refused below price
    // ==================================================================

    [Fact]
    public void Each_evoke_row_charges_the_encore_its_face_prints()
    {
        // `F7` (1) made the Evoke's cost the card's own printed Encore, which is
        // shipped machinery in both engines: the playability gate and the spend
        // both run before the op resolves, so the arm needed no port for it. The
        // number the badge shows and the number the gate refuses on are the same
        // resolved cost, which is what `MeterCost.Priced` reads.
        var curtain = MeterCost.Priced(new ProtoFrCurtainCall());
        var exit = MeterCost.Priced(new ProtoFrExitStageLeft());

        Assert.Equal(Meter.Encore, curtain!.Value.Meter);
        Assert.Equal(2, curtain.Value.Amount);
        Assert.Equal(Meter.Encore, exit!.Value.Meter);
        Assert.Equal(1, exit.Value.Amount);

        // The three rows that print no price charge none. A drain row charging
        // Encore as well would be two costs on one card, and the free deploy is
        // the starter.
        Assert.Null(MeterCost.Priced(new ProtoFrSalonDebutNamed()));
        Assert.Null(MeterCost.Priced(new ProtoFrLetThePeopleRejoice()));
        Assert.Null(MeterCost.Priced(new ProtoFrIntermission()));
    }

    [Fact]
    public void An_evoke_is_refused_below_its_price_and_allowed_at_it()
    {
        // THE REFUSAL, on the seat's real buffer. One below the price is not
        // "free with a shortfall" -- that is `Breathless`' rule and it is
        // printed on `Breathless` -- and the boundary is inclusive, so exactly
        // the price pays.
        var seat = Furina();
        var card = Held<ProtoFrCurtainCall>(seat);
        // The PRICE is read off a canonical copy and the AFFORDABILITY off the
        // held one, which is not a convenience: `GetResolved` walks the card's
        // pile to find its combat state, and a card this harness has put in a
        // hand is in no pile. The two reads are the same declaration either way
        // -- `MeterCost.Priced` is one function -- and affordability is a bank
        // read that needs no pile at all.
        var price = MeterCost.Priced(new ProtoFrCurtainCall())!.Value;

        FurinaResources.GainEncore(seat.Creature, 1);
        Assert.False(MeterCost.Affordable(card, price));

        FurinaResources.GainEncore(seat.Creature, 1);
        Assert.True(MeterCost.Affordable(card, price));
    }

    // ==================================================================
    // 5. THE THREE WORDS -- EB-272's attach, on these five faces
    // ==================================================================

    [Fact]
    public void Every_row_carries_the_definition_of_the_word_it_prints()
    {
        // STRUCTURAL, and the rule it pins is `EB-272`'s: the tip is attached
        // because the face PRINTED the word, not because somebody remembered.
        // A missing hover tip renders as nothing at all -- no wrong number, no
        // exception, no visual seam -- which is why the join is asserted by a
        // machine that knows both ends.
        Assert.Contains("ArmKeywordTips.ForDeploy",
            Il.Calls(Il.Method("ProtoFrSalonDebutNamed", "get_ExtraHoverTips")));

        foreach (var row in new[] { "ProtoFrCurtainCall", "ProtoFrExitStageLeft" })
        {
            Assert.Contains("ArmKeywordTips.ForEvoke",
                Il.Calls(Il.Method(row, "get_ExtraHoverTips")));
        }

        foreach (var row in new[] { "ProtoFrLetThePeopleRejoice",
                                    "ProtoFrIntermission" })
        {
            Assert.Contains("ArmKeywordTips.ForDrain",
                Il.Calls(Il.Method(row, "get_ExtraHoverTips")));
        }
    }

    [Fact]
    public void The_evoke_tip_quotes_the_arms_own_numbers()
    {
        // `EB-89`: a retune of the multiplier or the mint must not be able to
        // leave a sentence on a card quoting a retired number, so the tip reads
        // the constants rather than printing digits. Read off the compiled
        // method, which is where an inlined literal would show up as the ABSENCE
        // of the interpolation.
        var tip = string.Join(" ", Il.Strings(
            Il.Method("ArmKeywordTips", "ForEvoke")));

        Assert.Contains("counts ", tip);
        Assert.DoesNotContain("counts 3 times", tip);
        Assert.DoesNotContain("prints 5 ", tip);
        Assert.Equal(3, FurinaReframeLaw.EvokeFocusMult);
        Assert.Equal(5, FurinaReframeLaw.FanfarePerEvoke);
    }
}
