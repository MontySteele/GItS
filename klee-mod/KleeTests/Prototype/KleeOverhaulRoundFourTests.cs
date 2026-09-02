using System.Linq;
using System.Text.RegularExpressions;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// KLEE OVERHAUL, ROUND FOUR: the two seats' blind act-one runs on
/// `0.2.1966+proto` (`review/active/klee-overhaul-round-3-2026-09-02.md`).
///
///   * The growth number moved from 2 to 3 (the round packet's sec.3, a D
///     pick taken at its default). Its pins are
///     <c>KleeOverhaulRuleTests.Rule1_growth_is_three_by_default</c> and the
///     constant-parity gate; nothing is repeated here.
///   * <c>EB-287</c> -- the Bomb face read like a debug string ("(2 Bombs, 0
///     of them Mines)"), and nothing printed anywhere said what happens when
///     a second Bomb lands on an enemy that already has one: "the single most
///     important interaction in the deck and I only found it by gambling a
///     card on it" (r3 Opus seat).
///   * <c>EB-288</c> -- NOT A DEFECT, and this file is where that is shown
///     rather than asserted. See the section below.
///
/// WHAT IS REAL HERE. The faces are strings on the power and the tip class,
/// read off the real assembly. The EB-288 derivation runs the game's OWN
/// <c>WeakPower.ModifyDamageMultiplicative</c> against a real Creature and
/// prints through the game's OWN <c>DynamicVar.ToHighlightedString</c>. What
/// is NOT reachable is <c>DamageVar.UpdateCardPreview</c> itself, which needs
/// <c>card.Owner.RunState</c> and a live <c>CombatState</c> (README, "The
/// headless boundary") -- so the preview value is composed here from the two
/// halves the game composes it from, each of them run for real.
///
/// THE COLLECTION IS LOAD-BEARING, for the reason
/// <c>KleeOverhaulRoundOneFixTests</c> gives: <c>KleeOverhaul.Enabled</c> is
/// one static for the whole process.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class KleeOverhaulRoundFourTests
{
    private static string Row(ProtoBombPower pile, string key) =>
        pile.Localization!.First(r => r.Item1 == key).Item2;

    private static string LocKey(ProtoBombPower pile) =>
        (string)typeof(ProtoBombPower)
            .GetProperty("SmartDescriptionLocKey", HeadlessGame.All)!
            .GetValue(pile)!;

    // ---- EB-287: the face is prose now ----------------------------------

    [Fact]
    public void The_face_is_prose_and_carries_no_parenthetical_count()
    {
        // The seat's own words: "reads like a debug string". The old face put
        // the two counts in brackets after the total, including a `0 of them
        // Mines` on a pile with no Mine in it.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4), new ProtoBombs.Charge(6));

        var face = Row(pile, "smartDescription");

        Assert.DoesNotContain("(", face);
        Assert.DoesNotContain("of them", face);
        Assert.Contains("A [gold]Set off[/gold] here deals {Size} Pyro damage "
                        + "in total.", face);
        // `EB-289`: `{Count}`, not `{Amount}` -- see the test below and
        // `ProtoBombPower.Bombs` for why the stack amount could not be it.
        Assert.Contains(" Bombs here: {Count}.", face);
        Assert.EndsWith(" Each grows at the start of your turn, and none goes "
                        + "off by itself.", face);
    }

    [Fact]
    public void A_pile_with_no_mine_never_prints_a_mine_count()
    {
        // The half of the parenthetical that was actively misleading: `{Mines}`
        // is 0 on most piles, and printing "0 of them Mines" is a sentence
        // about something that is not there.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4));

        Assert.Equal(0, pile.MineCount);
        Assert.DoesNotContain("{Mines}", Row(pile, "smartDescription"));
        Assert.Contains("{Mines}", Row(pile, "smartDescriptionMines"));
    }

    // ---- EB-287: "after Weak", and only while it is true -----------------

    [Fact]
    public void The_total_names_weak_exactly_when_weak_is_shrinking_it()
    {
        // The r3 Codex seat: "The Bomb display showed Bomb 17 but said Set off
        // would deal 12 total, which I inferred was the Weak-adjusted amount
        // but had to reason through." The face says it now, and says it only
        // while it is true -- the key is chosen off the same pile state
        // `PredictedSetOffDamage` reads.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(8), new ProtoBombs.Charge(9));

        Assert.EndsWith(".smartDescription", LocKey(pile));
        Assert.DoesNotContain("after [gold]Weak[/gold]",
                              Row(pile, "smartDescription"));
        Assert.Equal(17, pile.PredictedSetOffDamage());

        klee.WithPower<WeakPower>(1);

        // The seat's own board: Bomb 17, Set off deals 12.
        Assert.Equal(12, pile.PredictedSetOffDamage());
        Assert.EndsWith(".smartDescriptionWeak", LocKey(pile));
        Assert.Contains("{Size} Pyro damage in total, after [gold]Weak[/gold].",
                        Row(pile, "smartDescriptionWeak"));
    }

    [Fact]
    public void The_two_axes_compose_into_the_four_rows_that_exist()
    {
        // A key with no row behind it falls back to the STATIC description
        // (`PowerModel.HasSmartDescription` is a `LocString.Exists` probe), so
        // a missing row is a silently blank face rather than a crash. Every
        // combination the selector can produce must therefore be present.
        var klee = Seat.Klee().WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true), new ProtoBombs.Charge(6));

        Assert.EndsWith(".smartDescriptionMinesWeak", LocKey(pile));

        var rows = pile.Localization!.Select(r => r.Item1).ToList();
        foreach (var key in new[] { "smartDescription", "smartDescriptionWeak",
                                    "smartDescriptionMines",
                                    "smartDescriptionMinesWeak" })
        {
            Assert.Contains(key, rows);
        }

        // And the Weak row is the plain row with exactly that one clause in
        // it -- the mutation guard across the whole grid.
        Assert.Equal(
            Row(pile, "smartDescription"),
            Row(pile, "smartDescriptionWeak")
                .Replace(", after [gold]Weak[/gold]", string.Empty));
        Assert.Equal(
            Row(pile, "smartDescriptionMines"),
            Row(pile, "smartDescriptionMinesWeak")
                .Replace(", after [gold]Weak[/gold]", string.Empty));
    }

    [Fact]
    public void A_canonical_pile_never_claims_a_weak_it_cannot_read()
    {
        // `HasSmartDescription` resolves this key BEFORE the mutability check
        // that gates the smart face, so the selector runs on a compendium copy
        // whose `Owner` getter asserts. It must answer without throwing, and
        // it must answer the same thing `PredictedSetOffDamage` does on such a
        // copy: no owner, no modifiers, the raw total.
        var canonical = new ProtoBombPower();

        Assert.EndsWith(".smartDescription", LocKey(canonical));
        Assert.Equal(0, canonical.PredictedSetOffDamage());
    }

    // ---- EB-287: the keyword tip says the Bombs join --------------------

    [Fact]
    public void The_bomb_keyword_tip_says_a_second_bomb_joins_the_first()
    {
        var printed = string.Concat(Il.Strings(
            typeof(ArmKeywordTips).GetMethod("ForBomb", HeadlessGame.All)!));

        Assert.Contains("A Bomb placed on an enemy that already has one joins "
                        + "it there: the badge shows their total, and a single "
                        + "[gold]Set off[/gold] pops them all.", printed);
    }

    [Fact]
    public void The_tip_does_not_claim_the_charges_fuse_into_one()
    {
        // They do not, and Careful Arrangement is the card that says so: it
        // moves every Bomb onto one enemy AS ONE BOMB. A kit that fused them
        // for free would print that card as a blank -- and the charges really
        // are separate, which `GrowBy` is the proof of: each grows on its own,
        // so three small Bombs cook faster than one big one (the brief's pick
        // 9, taken at its default).
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).Creature;
        var pile = ProtoBombs.Place(enemy, klee.Creature,
            new ProtoBombs.Charge(2), new ProtoBombs.Charge(2),
            new ProtoBombs.Charge(2));

        pile.GrowBy(KleeOverhaulLaw.BombGrowth);

        Assert.Equal(3, pile.Charges.Count);
        Assert.Equal(6 + 3 * KleeOverhaulLaw.BombGrowth, pile.TotalSize);
    }

    // ---- EB-288: the two Ka-pow! faces, and why both were right ---------

    /// <summary>The numeral a `{Damage:diff()}` slot actually prints, with the
    /// highlight markup the game wraps it in stripped off.</summary>
    private static string Numeral(string highlighted) =>
        Regex.Replace(highlighted, @"\[[^\]]*\]", string.Empty);

    [Fact]
    public void Weak_multiplies_a_move_by_three_quarters_and_the_face_truncates()
    {
        // The two halves the game composes a printed damage number from, each
        // run for real. FIRST: `DamageVar` declares `ValueProp.Move`, and
        // `WeakPower.ModifyDamageMultiplicative` returns its multiplier only
        // for a POWERED attack from its own owner.
        Assert.True(ValueProp.Move.IsPoweredAttack());

        var klee = Seat.Klee().WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;
        var weak = klee.Creature.Powers.OfType<WeakPower>().Single();

        var multiplier = weak.ModifyDamageMultiplicative(
            enemy, 0m, ValueProp.Move, klee.Creature, null, null);
        Assert.Equal(0.75m, multiplier);

        // SECOND: the printed slot is `(int)` of the preview value --
        // `DynamicVar.ToHighlightedString`'s own first line. So it TRUNCATES,
        // and 7.5 prints as 7 rather than 8.
        Assert.Equal(7, new DynamicVar("x", 7.5m).IntValue);
    }

    [Theory]
    [InlineData(false, 7, "5")]    // 7 x 0.75 = 5.25 -> 5
    [InlineData(true, 10, "7")]    // 10 x 0.75 = 7.5 -> 7
    public void Both_ka_pow_faces_read_weak_and_one_of_them_looks_like_it_does_not(
        bool upgraded, int printedBase, string underWeak)
    {
        // EB-288, the r3 Codex seat: "The upgraded Ka-pow! still printed 7
        // damage while the unupgraded one printed 5 under Weak, making it
        // unclear whether the upgrade had actually increased base damage or
        // simply resisted the debuff."
        //
        // NEITHER FACE IS WRONG. The upgraded card's base is 10 (EB-283's
        // delta, +3 damage), and 10 Weakened and truncated is 7 -- which is
        // also, by coincidence, the number the BASE card prints unweakened.
        // The seat read a collision, not a bug. This pins the collision so
        // that a face which really did stop reading the debuff would print 10
        // here and fail.
        var klee = Seat.Klee().WithPower<WeakPower>(1);
        var enemy = Seat.Klee(30).Creature;
        var weak = klee.Creature.Powers.OfType<WeakPower>().Single();
        var multiplier = weak.ModifyDamageMultiplicative(
            enemy, 0m, ValueProp.Move, klee.Creature, null, null);

        var card = new ProtoKoKapow();
        if (upgraded) Upgrade(card);

        var damage = card.DynamicVars["Damage"];
        Assert.Equal(printedBase, (int)damage.BaseValue);

        // What `DamageVar.UpdateCardPreview` writes: the base value through
        // the damage hooks. The hook walk itself needs a RunState and a live
        // CombatState, so the ONE modifier on this board is applied here and
        // the game's own printer is asked for the numeral.
        damage.PreviewValue = damage.BaseValue * multiplier;
        Assert.Equal(underWeak, Numeral(damage.ToHighlightedString(false)));
    }

    [Fact]
    public void The_upgrade_really_did_move_the_number_it_looked_like_it_had_not()
    {
        // The other half of the seat's doubt, said out loud: +3, through the
        // game's own `UpgradeInternal`, so 7 under Weak is 10 reduced and not
        // 7 unreduced. (`KleeOverhaulRoundThreeTests` pins the same pair for
        // EB-283; it is repeated here because it is half of EB-288's answer
        // and a reader of this file needs both halves in front of them.)
        var baseCard = new ProtoKoKapow();
        var upgraded = new ProtoKoKapow();
        Upgrade(upgraded);

        Assert.Equal(7m, baseCard.DynamicVars["Damage"].BaseValue);
        Assert.Equal(10m, upgraded.DynamicVars["Damage"].BaseValue);
    }

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
    }
}
