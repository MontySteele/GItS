using System;
using System.Linq;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
// ALIASED, not imported: the base game ships its own
// `MegaCrit.Sts2.Core.Models.Cards.DramaticEntrance`, so a plain import of
// Furina's generated namespace makes names in it ambiguous. Slice two's file
// takes the same precaution for the same reason.
using FurinaGen = KleeMod.Cards.Furina.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// THE FURINA POOL PASS, ONE (<c>EB-493</c>) -- the arm-only Commons and the
/// one argument they needed.
/// <c>review/active/furina-pool-pass-2026-09-05.md</c> sec.2 is the design;
/// all four are FOLLOWS on the doctrine read
/// (<c>review/records/card-audit-2026-09-04.md</c> sec.5.5).
///
/// WHAT THE ROUNDS SAID, because every row is an answer to one sentence of it.
/// Rounds 9 and 10 read the Salon as FURNITURE: one Deploy in the whole deck,
/// most Companion plays printing "No member on stage: performs nobody", and no
/// card of Furina's own that asks a member to act. So:
///
///   <c>ProtoFrCurtainRises</c>  a second Deploy SHAPE -- a deploy on an Attack
///   <c>ProtoFrSecondCourse</c>  a second performance, priced in Encore
///   <c>ProtoFrGuestList</c>     a Companion generator in the pool, no Exhaust
///
/// THREE OF THE FOUR REMAIN. <c>ProtoFrRollingTide</c> -- the kit's own perform
/// verb on a draftable row -- was WITHDRAWN from the arm's offer in round 13
/// (<c>EB-552</c>, a D default): four seats over three rounds read it the same
/// way at 2 energy and at 1, so the price was never the reason and the row left
/// rather than moving a third time. The shipped <i>Undercurrent</i> is offered
/// again at that seam, and the row and its pins left the surface under
/// R213 B's deletion rule -- which is what <c>ThePass</c> below is for.
///
/// WHAT IS REAL HERE AND WHAT IS STRUCTURAL, the split
/// <see cref="FurinaReframeSliceTwoTests"/> makes and for its reasons (README,
/// "The headless boundary"). REAL, on live objects: each row's identity, type,
/// cost, rarity and keyword rail, and the Encore gate's refusal and allowance
/// on a seat's own buffer. STRUCTURAL, read off the compiled method: anything
/// that RESOLVES -- a deploy, a performance, an Attack, a generation -- needs a
/// combat this harness cannot build, so what is pinned is the WIRING: which
/// verb each row's body calls, and that no row grew a second copy of a rule.
///
/// THE ONE FACT NO C# PIN CAN MAKE, again. <c>SalonMember.Crabaletta</c> and
/// <c>SalonMember.Usher</c> compile into the emitted bodies as enum operands,
/// and <see cref="Il.Calls"/> reads call TOKENS -- it can say a row calls
/// <c>PerformLeftmost</c>, never whom it names. WHICH member, and the aim's
/// behaviour when she is not on stage, are pinned on the python side in
/// <c>tier0/tests/test_furina_pool_pass.py</c>; the two halves name each other
/// so neither can be deleted quietly.
/// </summary>
public class FurinaPoolPassTests
{
    // ==================================================================
    // Fixtures -- slice two's, verbatim, and for their reasons.
    // ==================================================================

    private static Seat Furina(int maxHp = 60)
    {
        FurinaDrain.ResetAll();
        FurinaReframeLedger.ResetAll();
        return Seat.Furina(maxHp).WithCombatState();
    }

    private static T Held<T>(Seat seat) where T : CardModel, new()
    {
        var card = new T();
        Seat.Set(card, "IsMutable", true);
        Seat.Set(card, "Owner", seat.Player);
        return card;
    }

    /// <summary>The pass, against the shipped Common each row replaces. Named
    /// once so a row deleted under R213 B's deletion rule takes its pins with
    /// it rather than leaving a green file asserting things about nothing.</summary>
    private static readonly (Type Proto, Type Shipped)[] ThePass =
    {
        (typeof(ProtoFrCurtainRises), typeof(FurinaGen.HouseCall)),
        (typeof(ProtoFrSecondCourse), typeof(FurinaGen.DinnerService)),
        (typeof(ProtoFrGuestList), typeof(FurinaGen.BlockingNotes)),
    };

    private static CardModel New(Type type) =>
        (CardModel)Activator.CreateInstance(type)!;

    // ==================================================================
    // 0. THE QUARANTINE. Read this section before any other.
    // ==================================================================

    // THE ONE PIN AN ARM PROPERTY MAKES DISHONEST: under
    // `-p:FurinaReframe=true` the property MOVES the value this asserts, so
    // green would mean the property did nothing and red would mean it worked.
    // Skipped there rather than left to fail. Arm properties are deploy-line
    // only (docs/current/operations/prototype.md).
#if FURINA_REFRAME
    [Fact(Skip = "-p:FurinaReframe=true moves FurinaReframe.DefaultEnabled, which is the value this pin asserts. Arm properties are deploy-line only: see docs/current/operations/prototype.md.")]
#else
    [Fact]
#endif
    public void The_arm_ships_off()
    {
        Assert.False(FurinaReframe.DefaultEnabled);
        Assert.Equal(FurinaReframe.DefaultEnabled, FurinaReframe.Enabled);
    }

    [Fact]
    public void Every_row_is_furinas()
    {
        // `ICharacterCard.CharacterId` is what puts a row in HER off-pool list
        // and what every character-aware mechanic reads. A row answering "klee"
        // would draw wearing Klee's frame, which is a lie about the thing under
        // test (`PrototypeRoster`'s own note).
        foreach (var (proto, _) in ThePass)
        {
            Assert.Equal("furina",
                Assert.IsAssignableFrom<ICharacterCard>(New(proto)).CharacterId);
        }
    }

    // ==================================================================
    // 1. THE SWAP IS A FACE SWAP
    // ==================================================================

    [Fact]
    public void Every_row_takes_its_shipped_rows_rarity_type_and_cost()
    {
        // A SUBSTITUTION IS A FACE SWAP: a prototype filed in another tier
        // would move the odds the row is offered at, which is a balance change
        // smuggled in as a quarantine. The sim raises on one
        // (`rewards.character_pool`); this is the same claim in the mod, read
        // off constructed models, which need no combat.
        //
        // TYPE TOO, and the rarity is the one that carries the claim: the odds
        // a row is offered at are the tier's, so common-for-common is what
        // makes the swap a face swap rather than a balance change.
        //
        // COST WAS THE PACKET'S D DEFAULT AND NOT A RULE OF THE SEAM: each
        // replaced row was PICKED as a plain number card of the same type and
        // cost. The one row whose cost ever moved off its shipped twin's was
        // Rolling Tide, and that row is withdrawn (`EB-552`), so the claim is
        // whole again and holds for every row still on the pass.
        foreach (var (protoType, shippedType) in ThePass)
        {
            var proto = New(protoType);
            var shipped = New(shippedType);
            Assert.Equal(CardRarity.Common, proto.Rarity);
            Assert.Equal(shipped.Rarity, proto.Rarity);
            Assert.Equal(shipped.Type, proto.Type);
            Assert.Equal(shipped.EnergyCost.Canonical,
                proto.EnergyCost.Canonical);
        }
    }

    [Fact]
    public void The_seam_that_offers_them_is_the_one_the_riders_use()
    {
        // STRUCTURAL, read off the compiled method, for this harness's usual
        // reason: `ModelDb.Card<T>()` throws until the game's pool build has
        // run, so what is pinned is the WIRING -- that the swap reads the arm
        // flag and concats out of `PrototypeCards.For`, and that
        // `FurinaCardPool` is the one thing that calls it. WHICH types it
        // names is an `isinst` operand rather than a call token, so that half
        // is pinned on the python side against `furina_reframe.POOL_SUBS`
        // (`tier0/tests/test_furina_pool_pass.py`), which is the map both
        // engines answer to.
        var calls = Il.Calls(Il.Method("FurinaReframeRoster", "SwapOfferedRiders"));
        Assert.Contains("PrototypeCards.For", calls);
        Assert.Contains("FurinaReframe.get_Enabled", calls);
        Assert.Contains("FurinaReframeRoster.SwapOfferedRiders",
            Il.Calls(Il.Method("FurinaCardPool", "FilterThroughEpochs")));
    }

    // ==================================================================
    // 2. THE ROWS' BODIES -- structural, one verb each
    // ==================================================================

    [Fact]
    public void Each_row_resolves_through_the_verb_its_face_prints()
    {
        // THE POINT IS THAT THERE IS NO SECOND IMPLEMENTATION of any of these
        // rules on a card. A deploy is `SalonMemberPower.Deploy` (which is
        // where the deploy-performs clause and the overflow Evoke live), a
        // performance is `SalonMemberPower.PerformLeftmost` (which resolves
        // through `PerformMember`, where the upkeep price, the dry cut, the
        // Focus term and the mint live), and a generation is
        // `GuestStarGenerator.Generate` (where the three structural guardrails
        // live). A row that grew its own copy of one would drift from the rule
        // the same card's tip describes.
        var curtainRises = Il.Calls(Il.Method("ProtoFrCurtainRises", "OnPlay"));
        Assert.Contains("SalonMemberPower.Deploy", curtainRises);

        var secondCourse = Il.Calls(Il.Method("ProtoFrSecondCourse", "OnPlay"));
        Assert.Contains("SalonMemberPower.Deploy", secondCourse);
        Assert.Contains("SalonMemberPower.PerformLeftmost", secondCourse);

        var guestList = Il.Calls(Il.Method("ProtoFrGuestList", "OnPlay"));
        Assert.Contains("GuestStarGenerator.Generate", guestList);
    }

    [Fact]
    public void No_row_reaches_past_the_one_implementation_of_a_performance()
    {
        // `PerformMember` is where the mint sits (sec.4.1's "a member
        // performing mints Fanfare, and nothing else does"), so a card that
        // called it directly would be a second caller of the mint with none of
        // `PerformLeftmost`'s empty-stage refusal in front of it.
        foreach (var (proto, _) in ThePass)
        {
            Assert.DoesNotContain("SalonMemberPower.PerformMember",
                Il.Calls(Il.Method(proto.Name, "OnPlay")));
        }
    }

    [Fact]
    public void The_perform_verb_takes_an_aim_and_defaults_it_to_the_front()
    {
        // `EB-493`'s ONE new argument, and it is an argument rather than an op
        // for the reason the aimed Evoke is: `tools/lint_op_parity.py` compares
        // the sim's op registry against the drafter's priced-op table, so a
        // `salon_perform_member` synonym would have bought a `DRAFTER_VERSION`
        // stamp for a verb both engines already have.
        //
        // THE DEFAULT IS THE FRONT, which is what makes every row written
        // before this pass mean exactly what it always meant -- `ChangeTheBill`
        // is the shipped row that proves it and its call is unchanged.
        var aim = typeof(SalonMemberPower)
            .GetMethod(nameof(SalonMemberPower.PerformLeftmost))!
            .GetParameters().Last();
        Assert.Equal("aim", aim.Name);
        Assert.Equal(typeof(SalonMember?), aim.ParameterType);
        Assert.True(aim.HasDefaultValue);
        Assert.Null(aim.DefaultValue);

        Assert.DoesNotContain("SalonMemberPower.PerformLeftmost",
            Il.Calls(Il.Method("ProtoFrCurtainRises", "OnPlay")));
    }

    // ==================================================================
    // 3. CURTAIN RISES -- a deploy on an ATTACK
    // ==================================================================

    [Fact]
    public void Curtain_rises_is_an_attack_that_aims_and_deploys()
    {
        // THE NEW SHAPE. Every Deploy row on this sheet before it was a Skill,
        // and rounds 9 and 10 found one Deploy in a whole deck. The row aims at
        // an enemy because its DAMAGE aims; the deploy is the owner's and takes
        // no target, which is why one card can carry both.
        var card = new ProtoFrCurtainRises();
        Assert.Equal(CardType.Attack, card.Type);
        Assert.Equal(TargetType.AnyEnemy, card.TargetType);

        var body = Il.Calls(Il.Method("ProtoFrCurtainRises", "OnPlay"));
        Assert.Contains("SalonMemberPower.Deploy", body);
        Assert.Contains(body, call => call.StartsWith("DamageCmd.",
            StringComparison.Ordinal));
    }

    [Fact]
    public void Curtain_rises_prints_the_deploy_keyword_and_names_its_member()
    {
        // `EB-272`: the tip is DERIVED from the printed word, so a row that
        // prints `[gold]Deploy[/gold]` carries the arm's definition of it, and
        // the member's own tooltip comes off the same face. The name printed
        // and the tooltip's title are one string (`SalonMemberTips.DisplayName`)
        // or the player cannot tell they are about the same member.
        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoFrCurtainRises", "get_Localization")));
        Assert.Contains("[gold]Deploy[/gold]", face);
        Assert.Contains("Surintendante Chevalmarin", face);
    }

    [Fact]
    public void Curtain_rises_fields_chevalmarin_and_no_longer_the_usher()
    {
        // `EB-530`, ROUND 12's SECOND ADJUSTMENT, and it is ONE WORD on the
        // face. Three seats read the row the same way -- "the card I never
        // wanted to play, because it puts the Usher at the front and converts
        // the damage engine into a block engine", with the Usher himself "below
        // a basic Defend" (3 Block a trigger, 2 dry) -- and the doctrine read
        // (card audit sec.5.7) is FOLLOWS on C6: against the shipped
        // `Surintendante Chevalmarin` (Common, 1 energy: deploy her, gain 3
        // Encore) this gains 6 damage and loses the 3 Encore, so neither row is
        // strictly better than the other.
        //
        // THE DEPLOY SHAPE IS UNCHANGED, which is the whole point of a one-word
        // change: she performs as she arrives because that clause is
        // `SalonMemberPower.Deploy`'s, and no row carries a copy of it. WHICH
        // member the call names is the enum operand this harness cannot read
        // (the class note above) and is pinned in
        // `tier0/tests/test_furina_pool_pass.py`; what is pinned here is the
        // PRINTED name and the tip derived from it, which is the half a player
        // reads -- and `EB-272`'s defect is exactly a face and a tooltip
        // naming different members.
        var body = Il.Calls(Il.Method("ProtoFrCurtainRises", "OnPlay"));
        Assert.Contains("SalonMemberPower.Deploy", body);
        Assert.Contains("SalonMemberTips.ForCard",
            Il.Calls(Il.Method("ProtoFrCurtainRises", "get_ExtraHoverTips")));

        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoFrCurtainRises", "get_Localization")));
        Assert.DoesNotContain("Usher", face);
    }

    // ==================================================================
    // 4. SECOND COURSE -- a second performance, priced in Encore
    // ==================================================================

    [Fact]
    public void Second_course_charges_the_price_its_face_prints()
    {
        // THE PRICE IS THE `encore_cost` GATE AND NOT THE OVERDRAW OP. One
        // below the price is not "free with a shortfall" -- that is
        // `Breathless`' rule and it is printed on `Breathless`.
        //
        // THE PRINTED PRICE IS 1 (`EB-552`, FOLLOWS on the doctrine read,
        // record sec.5.8). It was built at 3, and three rounds gave one
        // reading: the printed 3 plus the shipped per-performance drain is FIVE
        // Encore against an opening of 2, so the card was refused on all four
        // draws it ever had and "contributed nothing". At 1 its full value is
        // 3, which is the number the read compared against her opening.
        Assert.Equal(1, MeterCost.Priced(new ProtoFrSecondCourse())!.Value.Amount);

        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoFrSecondCourse", "get_Localization")));
        Assert.Contains("[gold]Encore[/gold]", face);
        Assert.Contains("Spend 1", face);
    }

    [Fact]
    public void Second_course_is_refused_below_its_price_and_allowed_at_it()
    {
        // THE REFUSAL, on the seat's real buffer, and the boundary is
        // inclusive: exactly the price pays.
        var seat = Furina();
        var card = Held<ProtoFrSecondCourse>(seat);
        var price = MeterCost.Priced(new ProtoFrSecondCourse())!.Value;

        Assert.Equal(0, FurinaResources.Encore(seat.Creature));
        Assert.False(MeterCost.Affordable(card, price));

        FurinaResources.GainEncore(seat.Creature, 1);
        Assert.True(MeterCost.Affordable(card, price));
    }

    [Fact]
    public void The_upgrade_takes_the_price_to_nothing()
    {
        // `upgrade: {encore_cost: -1}` emits a real `UpgradeCostBy(-1)`, so the
        // GATE and the BADGE charge the moved number the moment the smith is
        // used -- a face that went on printing the canonical price would be a
        // printed number that is not the number the card charges
        // (`EB-288`/`EB-291`'s defect class). The delta is unchanged by
        // `EB-552`; at a printed 1 it makes the `+` card free, and the codegen
        // drops the "Spend N Encore" sentence rather than printing "Spend 0"
        // (text conventions, the Evoke row).
        var upgraded = new ProtoFrSecondCourse();
        Seat.Set(upgraded, "IsMutable", true);
        BaseLib.Abstracts.CustomResources<EncoreResource>.Cost(upgraded)!
            .UpgradeCostBy(-1);

        // A FREE CARD IS UNPRICED, which is the same fact said twice:
        // `Priced` answers null below 1, so the `+` card carries no meter
        // badge and no shortfall gate -- and that is what "drops the sentence"
        // means downstream of the face.
        Assert.Equal(0, MeterCost.PriceIn(upgraded, Meter.Encore));
        Assert.Null(MeterCost.Priced(upgraded));

        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoFrSecondCourse", "get_Localization")));
        Assert.Contains("{IfUpgraded:show:|Spend 1 [gold]Encore[/gold]. }", face);
    }

    // ==================================================================
    // 5. GUEST LIST -- a generator in the pool, and no Exhaust
    // ==================================================================

    [Fact]
    public void Guest_list_does_not_exhaust_and_the_shipped_generator_does()
    {
        // THE ONE GUARDRAIL THIS ROW MOVES, and it is the only one of the four
        // kickoff sec.9 names that is a BALANCE rule rather than a structural
        // fact: this-combat-only, equal-rarity and the companion-plus-Guest-Star
        // pool are all properties of the code. "Generators Exhaust" is a sheet
        // field, and the pass buys An Invitation's verb back at a price of an
        // Energy and no Exhaust.
        Assert.DoesNotContain(CardKeyword.Exhaust,
            new ProtoFrGuestList().CanonicalKeywords);
        Assert.Contains(CardKeyword.Exhaust,
            new FurinaGen.AnInvitation().CanonicalKeywords);
    }

    [Fact]
    public void Guest_list_generates_at_its_own_rarity()
    {
        // GUARDRAIL C, and it is structural rather than printed: the generator
        // is a Common and asks for a Common, which is the same clause
        // `An Invitation` satisfies. A row that asked above its own rarity is
        // refused by `gen_klee_cards.blocked_reason` before it can be emitted
        // at all; this is the read from the other side, off the face.
        var card = new ProtoFrGuestList();
        Assert.Equal(CardRarity.Common, card.Rarity);

        var face = string.Join(" ", Il.Strings(
            Il.Method("ProtoFrGuestList", "get_Localization")));
        Assert.Contains("Common", face);
        Assert.Contains("[gold]Companion[/gold]", face);
    }
}
