using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using BaseLib.Abstracts;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// ROUND 8 -- the two things the blind act-2 seat could not reconcile
/// (`review/qa/klee-round-8-2026-09-03/opus-act2.md`). Rows `EB-353` and
/// `EB-354`.
///
/// `EB-353` IS TWO DEFECTS ON ONE CARD, Thoma's Blazing Barrier.
///
///   (a) THE BADGE PRINTED ITS OWN TEMPLATE. The seat quoted the buff list
///       verbatim: "Blazing Barrier 6 (buff) -- {Left} Block left." Nothing
///       was wrong with the var; <c>PowerModel.HoverTips</c> simply never
///       binds it on the row the mark wrote it into. The SMART branch
///       (<c>HasSmartDescription &amp;&amp; IsMutable</c>) is the only one
///       that calls <c>DynamicVars.AddTo</c>; the static branch binds the
///       game's own three dumb variables (<c>Amount</c>,
///       <c>singleStarIcon</c>, <c>energyPrefix</c>) and nothing else. Both
///       marks had put <c>{Left}</c> in the STATIC row and declared no smart
///       one, so the placeholder went to the screen. <c>SalonPowers</c> has
///       kept the two rows apart for exactly this reason since 2026-07-29,
///       and says so in its own comment.
///
///   (b) THE RIDER PAID ONCE PER BARRIER, NOT PER ABSORPTION. "Whenever this
///       Block absorbs damage, gain 3 Block" -- and a multi-hit attack is
///       several absorptions. The mark was spent whole by the first hit and
///       the Block it paid was left unmarked, so nothing was ever absorbed by
///       "this Block" a second time: the card absorbed exactly 9 on all three
///       occasions the seat could measure it (18 in / 9 taken, 9 in / 0 taken,
///       21 in / 12 taken), and it wrote "Thoma is a 9-Block card that prints
///       6 and implies more". The payout is marked now, which is what makes
///       the next hit another absorption of the same Block.
///
/// `EB-354` IS NOT A DEFECT, and this file is where that is SHOWN rather than
/// asserted -- <c>KleeOverhaulRoundFourTests</c>' treatment of <c>EB-288</c>,
/// one round on. The derivation is in the section below.
///
/// WHAT IS REAL AND WHAT IS STRUCTURAL, on the README's terms. The loc rows,
/// the live <c>{Left}</c> var against a <see cref="Seat"/>-built creature, the
/// mark arithmetic and the game's own <c>StrengthPower.ModifyDamageAdditive</c>
/// all RUN. What needs a live <c>CombatState</c> -- <c>Thicken</c> actually
/// spending its commands, a card actually being played -- is pinned off the
/// compiled method and says so. The end-to-end three-hit enemy turn is the sim
/// twin's, <c>tier0/tests/test_inazuma_companion_overhaul.py</c>.
///
/// <c>BlockMark</c> is internal and this mod carries no
/// <c>InternalsVisibleTo</c> -- the standing call, recorded in
/// <c>ProtoBombPower</c> and three files beside it -- so its arithmetic is
/// exercised through reflection rather than by widening the surface for a
/// test.
/// </summary>
public class Round8Tests
{
    private const BindingFlags All = HeadlessGame.All;

    /// <summary>`IsPoweredAttack()`: Move without Unpowered -- what an Attack
    /// card's hit and an enemy's swing both carry.</summary>
    private static ValueProp Attack => ValueProp.Move;

    /// <summary>The name <c>BlockMarkVar</c> registers itself under, and the
    /// token the row writes. Restated rather than read because the var class
    /// is internal too.</summary>
    private const string Left = "Left";

    // ---- EB-353 (a): the badge prints a number, not its own template -----

    [Fact]
    public void EB353_neither_block_mark_writes_a_var_token_into_its_static_row()
    {
        // The mutation guard, and it is the defect itself: a `{` in the static
        // row is a placeholder the game will never bind, because that branch
        // of `HoverTips` calls no `DynamicVars.AddTo`.
        Assert.DoesNotContain("{", Row<BlazingBarrierPower>("description"));
        Assert.DoesNotContain("{", Row<IcyPawsPower>("description"));

        // And the static row still prints the number the rider pays, which is
        // what `InazumaCompanionOverhaulTests` asks of every face on this arm.
        Assert.Contains(CompanionOverhaulLaw.BlazingBarrierBlock.ToString(),
                        Row<BlazingBarrierPower>("description"));
    }

    [Fact]
    public void EB353_both_marks_declare_the_smart_row_that_carries_left()
    {
        // The half that makes the number appear at all: the smart row exists,
        // so `HasSmartDescription` is true on a live mark, so the vars are
        // added and `{Left}` resolves.
        Assert.Contains("{" + Left + "}",
                        Row<BlazingBarrierPower>("smartDescription"));
        Assert.Contains("{" + Left + "}",
                        Row<IcyPawsPower>("smartDescription"));
    }

    [Fact]
    public void EB353_neither_mark_renames_the_row_the_game_probes_for()
    {
        // `PowerModel.SmartDescriptionLocKey` is `Id.Entry + ".smartDescription"`
        // and `HasSmartDescription` is a `LocString.Exists` probe on it, so the
        // row's KEY has to be that exact suffix. `ProtoBombPower` overrides the
        // property to select among a grid of rows; these two must not, or the
        // row above would be registered under a key nothing looks up -- the
        // same class of miss as the raw `{Left}`.
        foreach (var type in new[]
                 { typeof(BlazingBarrierPower), typeof(IcyPawsPower) })
        {
            Assert.Null(type.GetProperty("SmartDescriptionLocKey",
                                         All | BindingFlags.DeclaredOnly));
        }
    }

    [Fact]
    public void EB353_the_left_var_is_the_live_number_the_row_will_print()
    {
        // REAL: the var the game hands to SmartFormat, asked the way
        // SmartFormat asks it. `DynamicVars` is the game's own set, built off
        // `CanonicalVars` and owner-initialised by `PowerModel`, so this is the
        // exact object `DynamicVars.AddTo` puts under the name "Left" -- and
        // `ToString()` is the call the formatter makes on it.
        var thoma = Seat.Klee().WithPower<BlazingBarrierPower>(6);
        var barrier = Only<BlazingBarrierPower>(thoma);

        Seat.Set(thoma.Creature, "Block", 6);
        Assert.Equal("6", barrier.DynamicVars[Left].ToString());

        Seat.Set(thoma.Creature, "Block", 2);
        Assert.Equal("2", barrier.DynamicVars[Left].ToString());

        Seat.Set(thoma.Creature, "Block", 0);
        Assert.Equal("0", barrier.DynamicVars[Left].ToString());

        var diona = Seat.Klee().WithPower<IcyPawsPower>(6);
        Seat.Set(diona.Creature, "Block", 4);
        Assert.Equal("4",
                     Only<IcyPawsPower>(diona).DynamicVars[Left].ToString());
    }

    // ---- EB-353 (b): the rider fires per absorption ----------------------

    [Fact]
    public void EB353_a_three_hit_attack_is_three_absorptions()
    {
        // The row's own acceptance, walked hit by hit against the game's one
        // Block pool. `Thicken` pays inside `BeforeDamageReceived`, so the pool
        // the hit meets is the standing Block plus the payout, and the mark the
        // NEXT hit meets is what `BlockMark.Absorb` returned.
        var (fired, absorbed) = Barrage(mark: 6, block: 6, hit: 3, times: 3);

        Assert.Equal(3, fired);         // three absorptions, three payouts
        Assert.Equal(9, absorbed);      // 3x3 absorbed whole
    }

    [Fact]
    public void EB353_the_seats_own_seven_by_three_absorbs_twelve_not_nine()
    {
        // The board the seat measured: 21 incoming against a fresh barrier. It
        // absorbed 9 and the seat took 12; per absorption it absorbs 12 and the
        // player takes 9, which is what the sim twin's end-to-end enemy turn
        // asserts against the same constants.
        var (fired, absorbed) = Barrage(mark: 6, block: 6, hit: 7, times: 3);

        Assert.Equal(12, absorbed);

        // TWO payouts here where the sim pays three, because this engine pays
        // BEFORE the hit is blocked and the sim pays after: the same 12 is
        // absorbed either way, and the mod's larger early absorptions run the
        // pool out one hit sooner. That the two engines disagree about Block
        // inside this hook is pre-existing and written down on both sides
        // (`EB-336`'s note in `combat._enemy_turn`).
        Assert.Equal(2, fired);
    }

    [Fact]
    public void EB353_the_mark_survives_its_own_absorption_and_the_paws_do_not()
    {
        // The one-line statement of the fix, and of its scope. The barrier's
        // payout is Block and is marked, so a hit can never spend the mark to
        // nothing; the paws pay an aura, pass 0, and keep the marked-first
        // spend they always had -- including the 0 that means "gone".
        Assert.Equal(CompanionOverhaulLaw.BlazingBarrierBlock,
                     Absorb(6, 6, 7, CompanionOverhaulLaw.BlazingBarrierBlock));
        Assert.Equal(0, Absorb(6, 6, 7, payout: 0));

        // And nothing fires when nothing of this mark is standing, or when
        // nothing was absorbed.
        Assert.Null(Absorb(6, 0, 7, CompanionOverhaulLaw.BlazingBarrierBlock));
        Assert.Null(Absorb(6, 6, 0, CompanionOverhaulLaw.BlazingBarrierBlock));
    }

    [Fact]
    public void EB353_both_marks_spend_through_the_one_arithmetic()
    {
        // STRUCTURAL: `CreatureCmd.GainBlock`, `ElementalHit` and `PowerCmd`
        // all need a live combat. What is read is that the two hooks share
        // `BlockMark.Absorb` -- so the marks cannot drift apart again -- and
        // that the barrier no longer removes itself mid-hit, which is what
        // "the payout is marked" means at the command level.
        var thicken = Il.Calls(Il.Method("BlazingBarrierPower", "Thicken"));
        var bite = Il.Calls(Il.Method("IcyPawsPower", "Bite"));

        Assert.Contains("BlockMark.Absorb", thicken);
        Assert.Contains("BlockMark.Absorb", bite);
        Assert.Contains("CreatureCmd.GainBlock", thicken);
        Assert.Contains("PowerCmd.ModifyAmount", thicken);
        Assert.DoesNotContain("PowerCmd.Remove", thicken);
        Assert.Contains("PowerCmd.Remove", bite);
    }

    // ---- EB-354: Rapid Fire's hits, and why they are right ---------------

    [Fact]
    public void EB354_tenders_loss_lands_after_the_card_resolves()
    {
        // THE LOAD-BEARING FACT, read off the base game. `TenderPower`
        // ("Whenever you play a card, lose 1 Strength and 1 Dexterity this
        // turn") hangs its two `PowerCmd.Apply` calls off `AfterCardPlayed`
        // and overrides no BEFORE hook -- so every hit of ONE card sees ONE
        // Strength, the Strength standing when that card was played. The seat
        // measured the same thing live off a single Thoma play: "the penalty
        // lands after the card resolves".
        var tender = typeof(TenderPower);

        Assert.NotNull(tender.GetMethod("AfterCardPlayed",
                                        All | BindingFlags.DeclaredOnly));
        Assert.Null(tender.GetMethod("BeforeCardPlayed",
                                     All | BindingFlags.DeclaredOnly));
        Assert.Contains(Il.Calls(tender.GetMethod("AfterCardPlayed", All)!),
                        c => c.StartsWith("PowerCmd.Apply"));
    }

    [Fact]
    public void EB354_rapid_fires_face_and_its_hits_take_the_same_strength()
    {
        // THE CARD, read off the shipped class: a base of 3 and a face that
        // renders the var rather than a literal, so the PRINTED number is
        // `base + Strength` and never the base.
        var card = new ProtoKoRapidFire();
        var damage = Vars(card).OfType<DamageVar>().Single();

        Assert.Equal(3m, damage.BaseValue);
        Assert.Contains("{Damage:diff()}", Face(card));

        // THE FACE AND THE HIT RUN THE SAME MODIFIER SET.
        // `DamageVar.UpdateCardPreview` composes `Hook.ModifyDamage(...,
        // Props, ...)` off `BaseValue`, and the hit `SetOffRandom` deals goes
        // out through `DamageCmd.Attack`, whose `DamageProps` is that same
        // `ValueProp.Move`. One props value, one set of modifiers, one answer.
        Assert.Equal(ValueProp.Move, damage.Props);
        Assert.Equal(ValueProp.Move, DamageCmd.Attack(3m).DamageProps);

        // And the term itself, run for real -- the game's own StrengthPower
        // against a real Creature, the way `EB-288` ran WeakPower. At Strength
        // +1 the face composes 3 + 1 = 4 and each of the four hits deals
        // 3 + 1 = 4, so 16: exactly what the seat measured. Its predicted 24
        // read the printed 5 (3 plus the Strength Potion's 2, the face as it
        // stood BEFORE the turn's first Tender tick) as the card's BASE and
        // added Strength a second time. That double count is the whole 8, and
        // the rest of the turn reconciles on the nose: Bomb 11 + Mine 4 + 16
        // = 31 dealt against 31 measured.
        var klee = Seat.Klee().WithPower<StrengthPower>(1);
        var enemy = Seat.Klee(30).Creature;
        var term = klee.Creature.Powers.OfType<StrengthPower>().Single()
            .ModifyDamageAdditive(enemy, damage.BaseValue, Attack,
                                  klee.Creature, card, null);

        Assert.Equal(1m, term);
        Assert.Equal(4m, damage.BaseValue + term);           // the face
        Assert.Equal(16m, 4 * (damage.BaseValue + term));    // the four hits
    }

    [Fact]
    public void EB354_the_hits_are_dealt_off_the_base_and_never_off_the_preview()
    {
        // STRUCTURAL, and it is what keeps the two numbers one number: a card
        // play needs a live `CombatState`. The generated `OnPlay` hands
        // `DynamicVars.Damage.BaseValue` -- the raw 3 -- to `SetOffRandom`,
        // which sends it through `DamageCmd.Attack`, and the pipeline adds
        // Strength exactly once. Dealing the PREVIEW value instead would add
        // it twice, which is the shape the seat's prediction assumed and the
        // card does not have.
        var play = Il.Calls(Il.Method("ProtoKoRapidFire", "OnPlay"));

        Assert.Contains("ProtoBombPower.SetOffRandom", play);
        Assert.Contains(play, c => c.EndsWith("get_BaseValue"));
        Assert.DoesNotContain(play, c => c.EndsWith("get_PreviewValue"));
        Assert.Contains("DamageCmd.Attack",
                        Il.Calls(Il.Method("ProtoBombPower", "DealCardDamage")));
    }

    // ---- helpers ---------------------------------------------------------

    /// <summary>A power's loc rows, off an instance allocated uninitialised:
    /// every one of these `Localization` getters is a pure string builder that
    /// reads nothing off the instance (`KurageBuffFaceTests`' idiom, and
    /// `InterpolationPinTests`' before it).</summary>
    private static string Row<T>(string key) where T : notnull
    {
        var model = RuntimeHelpers.GetUninitializedObject(typeof(T));
        var rows = (List<(string, string)>)model.GetType()
            .GetProperty("Localization", All)!.GetValue(model)!;
        return rows.Single(r => r.Item1 == key).Item2;
    }

    private static string Face(CardModel card) =>
        ((CustomCardModel)card).Localization!
            .First(r => r.Item1 == "description").Item2;

    /// <summary>`CanonicalVars` is protected, so it is read the way every other
    /// internal seam in this project is read.</summary>
    private static IReadOnlyList<DynamicVar> Vars(CardModel card) =>
        ((IEnumerable<DynamicVar>)typeof(CardModel)
            .GetProperty("CanonicalVars", All)!.GetValue(card)!).ToList();

    /// <summary><c>BlockMark.Absorb</c>, through reflection -- see the class
    /// note on why the surface is not widened for a test.</summary>
    private static int? Absorb(int mark, int standing, int incoming, int payout)
        => (int?)typeof(BlazingBarrierPower).Assembly
            .GetType("KleeMod.Powers.BlockMark")!
            .GetMethod("Absorb", All)!
            .Invoke(null, new object[] { mark, standing, incoming, payout });

    /// <summary>One multi-hit attack against a standing Block mark, walked the
    /// way <c>CompanionOverhaulIncomingHit</c> walks it: the rider is asked
    /// BEFORE the hit is blocked, its payout joins the one pool, and the hit
    /// then eats what it can. Returns how many times the rider fired and how
    /// much of the attack the pool absorbed.</summary>
    private static (int Fired, int Absorbed) Barrage(
        int mark, int block, int hit, int times)
    {
        var fired = 0;
        var absorbed = 0;
        for (var i = 0; i < times; i++)
        {
            var next = Absorb(mark, block, hit,
                              CompanionOverhaulLaw.BlazingBarrierBlock);
            if (next != null)
            {
                fired++;
                mark = next.Value;
                block += CompanionOverhaulLaw.BlazingBarrierBlock;
            }
            var eaten = Math.Min(block, hit);
            absorbed += eaten;
            block -= eaten;
        }
        return (fired, absorbed);
    }

    /// <summary>The power this seat was just given, read back off the creature
    /// -- `Seat.WithPower` returns the seat, not the power.</summary>
    private static T Only<T>(Seat seat) where T : PowerModel
    {
        foreach (var power in seat.Creature.Powers)
        {
            if (power is T match) return match;
        }
        throw new InvalidOperationException("the power was not applied");
    }
}
