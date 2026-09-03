using System.Linq;
using System.Text.RegularExpressions;
using KleeMod.Cards;
using KleeMod.Cards.Prototype.Generated;
using KleeMod.Powers;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Entities.Cards;
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
        Assert.Contains("[gold]Set off[/gold] here deals [blue]{Size}[/blue] "
                        + "Pyro damage.", face);
        // `EB-289`: `{Count}`, not `{Amount}` -- see the test below and
        // `ProtoBombPower.Bombs` for why the stack amount could not be it.
        Assert.Contains(" Bombs here: [blue]{Count}[/blue].", face);
        Assert.EndsWith(" Each grows at the start of your turn. None goes "
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

    // ---- EB-287 / EB-343: every modifier named, and only while true ------

    [Fact]
    public void The_total_names_vulnerable_exactly_when_it_is_moving_it()
    {
        // The r3 Codex seat: "The Bomb display showed Bomb 17 but said Set off
        // would deal 12 total, which I inferred was the Weak-adjusted amount
        // but had to reason through." The face says it now, and says it only
        // while it is true -- the key is chosen off the same state
        // `PredictedSetOffDamage` reads.
        //
        // `EB-343` (R248) moved WHOSE modifier that is. Klee's Weak no longer
        // reaches a Bomb at all, so the term the sentence has to name is the
        // ENEMY's Vulnerable -- which this same face used to fold in silently,
        // which is the other half of what R248 calls a defect.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(8), new ProtoBombs.Charge(9));

        Assert.EndsWith(".smartDescription", LocKey(pile));
        Assert.DoesNotContain("after [gold]Vulnerable[/gold]",
                              Row(pile, "smartDescription"));
        Assert.Equal(17, pile.PredictedSetOffDamage());

        enemy.WithPower<VulnerablePower>(1);

        Assert.Equal(25, pile.PredictedSetOffDamage());   // 12 + 13, per charge
        Assert.EndsWith(".smartDescriptionVulnerable", LocKey(pile));
        Assert.Contains("[blue]{Size}[/blue] Pyro damage after "
                        + "[gold]Vulnerable[/gold].",
                        Row(pile, "smartDescriptionVulnerable"));
    }

    [Fact]
    public void The_cap_is_named_too_and_by_the_power_that_set_it()
    {
        // `EB-343`'s other half. A cap folded into the printed number in
        // silence is the same defect as a silent Vulnerable, and the pinned
        // build has two powers that can set one -- so the sentence names
        // whichever of them the number actually went through.
        var klee = Seat.Klee();
        var hardToKill = Seat.Klee(30).WithPower<HardToKillPower>(3);
        var capped = ProtoBombs.Place(hardToKill.Creature, klee.Creature,
            new ProtoBombs.Charge(9));

        Assert.EndsWith(".smartDescriptionHardToKill", LocKey(capped));
        Assert.Contains("capped by [gold]Hard To Kill[/gold]",
                        Row(capped, "smartDescriptionHardToKill"));

        var intangible = Seat.Klee(30).WithPower<IntangiblePower>(1);
        var ghost = ProtoBombs.Place(intangible.Creature, klee.Creature,
            new ProtoBombs.Charge(9));

        Assert.EndsWith(".smartDescriptionIntangible", LocKey(ghost));
        Assert.Contains("capped by [gold]Intangible[/gold]",
                        Row(ghost, "smartDescriptionIntangible"));

        // Both terms at once read as ONE sentence, in pipeline order.
        var both = Seat.Klee(30).WithPower<VulnerablePower>(1)
                                .WithPower<HardToKillPower>(3);
        var pile = ProtoBombs.Place(both.Creature, klee.Creature,
            new ProtoBombs.Charge(9));

        Assert.EndsWith(".smartDescriptionVulnerableHardToKill", LocKey(pile));
        Assert.Contains("Pyro damage after [gold]Vulnerable[/gold], capped by "
                        + "[gold]Hard To Kill[/gold].",
                        Row(pile, "smartDescriptionVulnerableHardToKill"));
    }

    [Fact]
    public void The_two_axes_compose_into_the_rows_that_exist()
    {
        // A key with no row behind it falls back to the STATIC description
        // (`PowerModel.HasSmartDescription` is a `LocString.Exists` probe), so
        // a missing row is a silently blank face rather than a crash. Every
        // combination the selector can produce must therefore be present --
        // which is why `EB-343` GENERATES the grid off the same table the
        // selector reads instead of listing it by hand.
        var klee = Seat.Klee();
        var enemy = Seat.Klee(30).WithPower<VulnerablePower>(1);
        var pile = ProtoBombs.Place(enemy.Creature, klee.Creature,
            new ProtoBombs.Charge(4, IsMine: true), new ProtoBombs.Charge(6));

        Assert.EndsWith(".smartDescriptionMinesVulnerable", LocKey(pile));

        var rows = pile.Localization!.Select(r => r.Item1).ToList();
        var caps = new[] { "", "HardToKill", "Intangible", "Capped" };
        foreach (var mines in new[] { "", "Mines" })
        {
            foreach (var vulnerable in new[] { "", "Vulnerable" })
            {
                foreach (var cap in caps)
                {
                    Assert.Contains(
                        "smartDescription" + mines + vulnerable + cap, rows);
                }
            }
        }
        // And no more than the grid: two axes, nothing hand-added beside them.
        Assert.Equal(2 * 2 * caps.Length,
                     rows.Count(r => r.StartsWith("smartDescription")));

        // Each modified row is the plain row with exactly its own clause in
        // it -- the mutation guard across the whole grid.
        Assert.Equal(
            Row(pile, "smartDescription"),
            Row(pile, "smartDescriptionVulnerable")
                .Replace(" after [gold]Vulnerable[/gold]", string.Empty));
        Assert.Equal(
            Row(pile, "smartDescriptionMines"),
            Row(pile, "smartDescriptionMinesVulnerableHardToKill")
                .Replace(" after [gold]Vulnerable[/gold], capped by "
                         + "[gold]Hard To Kill[/gold]", string.Empty));
    }

    [Fact]
    public void A_canonical_pile_never_claims_a_modifier_it_cannot_read()
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

    // ---- ROUND 5 PICK 1: Ka-pow! retains from print ----------------------

    [Fact]
    public void Kapow_retains_at_base_and_its_upgrade_buys_damage_instead()
    {
        // [USER] 2026-09-02: "I'm fine with the default on Ka-Pow!" The card
        // is the arm's only detonator in the starter, so a hand held for the
        // Bomb to cook used to mean discarding it -- Retain from print is the
        // pick, and the game owns the whole behaviour from the keyword
        // (CombatManager keeps a Retain card in hand at end of turn), so the
        // keyword on the base card IS the rule.
        var card = new ProtoKoKapow();
        Assert.Contains(CardKeyword.Retain, card.CanonicalKeywords);

        // The upgrade is the default rule's again -- a set_off's hit, +3 --
        // because the row's authored `upgrade:` block went with the move.
        Assert.Equal(4m, card.DynamicVars["Damage"].BaseValue);
        var upgraded = new ProtoKoKapow();
        Seat.Set(upgraded, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(upgraded, new object?[] { });
        Assert.Equal(7m, upgraded.DynamicVars["Damage"].BaseValue);
        Assert.Contains(CardKeyword.Retain, upgraded.CanonicalKeywords);
    }

    [Fact]
    public void The_bomb_keyword_tip_says_a_second_bomb_joins_the_first()
    {
        var printed = string.Concat(Il.Strings(
            typeof(ArmKeywordTips).GetMethod("ForBomb", HeadlessGame.All)!));

        Assert.Contains("Bombs on one enemy go off together when "
                        + "[gold]Set off[/gold].", printed);
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
    [InlineData(false, 4, "3")]    // 4 x 0.75 = 3
    [InlineData(true, 7, "5")]     // round 5 pick 1: the upgrade buys damage
    public void Both_ka_pow_faces_read_weak_and_one_of_them_looks_like_it_does_not(
        bool upgraded, int printedBase, string underWeak)
    {
        // EB-288, the r3 Codex seat: "The upgraded Ka-pow! still printed 7
        // damage while the unupgraded one printed 5 under Weak, making it
        // unclear whether the upgrade had actually increased base damage or
        // simply resisted the debuff." NEITHER FACE WAS WRONG: 10 Weakened and
        // truncated was 7, which was also what the base card printed unweakened
        // -- a collision, not a bug.
        //
        // THE COLLISION IS GONE, and it stayed gone through two moves of this
        // card. Draft 4 (R242) stopped the number moving at all -- 0 energy
        // for 4, upgrade Retain -- and round 5 pick 1 put Retain on the base
        // card and handed the upgrade back to damage, 4 -> 7. The old
        // collision was the upgraded face printing 7 unweakened where the base
        // printed 7 Weakened from 10; at 4 and 7 no such pair exists. What
        // this pin is FOR survives both moves and is the reason it is kept:
        // the face has to keep reading the debuff.
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
    public void The_face_still_carries_a_token_after_the_upgrade_stopped_moving_it()
    {
        // `EB-308`, and it is the other half of EB-288's answer. The seat's
        // doubt was about whether a face reads its debuff; the emitter used to
        // answer that only for a number some upgrade moved, so R242's
        // Retain-only upgrade would have printed a dead literal 4 that
        // Strength and Weak could never touch. Round 5 pick 1 gave this card a
        // moving number back, but the defect it names is not about THIS card
        // having one -- the token has to be there for the same reason on every
        // row whose upgrade moves something else, so both are still asserted.
        var baseCard = new ProtoKoKapow();
        var upgraded = new ProtoKoKapow();
        Upgrade(upgraded);

        Assert.Equal(4m, baseCard.DynamicVars["Damage"].BaseValue);
        Assert.Equal(7m, upgraded.DynamicVars["Damage"].BaseValue);
        Assert.Contains("{Damage:diff()}", baseCard.Localization!
            .First(r => r.Item1 == "description").Item2);
    }

    private static void Upgrade(CardModel card)
    {
        Seat.Set(card, "IsMutable", true);
        typeof(CardModel).GetMethod("UpgradeInternal", HeadlessGame.All)!
            .Invoke(card, new object?[] { });
    }
}
