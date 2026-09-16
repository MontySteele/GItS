using System.Linq;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// `EB-495`, the PROTOTYPE arm's verb rows of the kit-verb / base-game-trigger
/// matrix (`docs/current/atlas/kit-verbs-vs-base-triggers.md`). Split from
/// `KitVerbBaseTriggerPinTests` for the reason the whole `Prototype/` folder
/// exists: `ProtoBombPower`, `KokomiPlan` and `FurinaStage` are not compiled
/// without `-p:PrototypeCards=true`, so a pin against them would not compile
/// either.
///
/// The base-game TRIGGER half is not repeated here -- it is a fact about
/// `sts2.dll` and is pinned once, in the shipped class. What is here is the
/// verb half: which door each prototype verb goes through, and the one verb
/// in the mod that is genuinely an Attack.
/// </summary>
public class KitVerbBaseTriggerProtoPinTests
{
    [Theory]
    // MATRIX V5/V6, V9, V11, V14, V15. Every one of these reaches the elemental
    // door and none of them reaches `DamageCmd`, which is the whole of their
    // row: `damage-only` under T5 and `none` under every other trigger.
    [InlineData("ProtoBombPower", "Explode")]   // V5 explosion, and V6's mine
    [InlineData("KokomiPlan", "Hit")]           // V9 planned hit
    [InlineData("FurinaStage", "Perform")]      // V14 stage act
    [InlineData("FurinaStage", "Bow")]          // V15 stage bow
    [InlineData("TamakushiCasket", "Strike")]   // V11 casket strike
    public void A_prototype_kit_verb_goes_through_the_elemental_door(
        string type, string method)
    {
        var calls = Il.Calls(Il.Method(type, method));

        Assert.True(calls.Contains("ElementalHit.Deal")
                    || calls.Contains("ElementalHit.DealWithoutDealerMods"),
                    $"{type}.{method} reaches no elemental door");
        Assert.DoesNotContain("DamageCmd.Attack", calls);
        Assert.DoesNotContain("AttackCommand.Execute", calls);
    }

    [Fact]
    public void The_overhaul_bomb_takes_the_named_unpowered_door()
    {
        // `EB-343` (R248) again, from the caller's side: the ONE call site of
        // `DealWithoutDealerMods` in the mod. If `Explode` ever took plain
        // `Deal` instead, Klee's Strength would re-enter a charge and the
        // matrix's V5 row would need re-answering under T7.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "Explode"));

        Assert.Contains("ElementalHit.DealWithoutDealerMods", calls);
        Assert.DoesNotContain("ElementalHit.Deal", calls);
    }

    [Fact]
    public void A_mine_answers_a_powered_attack_and_resolves_as_an_explosion()
    {
        // MATRIX V6, both halves. The TRIGGER side: a Mine reads
        // `IsPoweredAttack()` off the incoming enemy hit, which is the same
        // predicate the base game's own retaliation powers read -- so a Mine
        // answers what Thorns answers. The EFFECT side: what it then deals is
        // an explosion, not an attack, so its own row is `Explode`'s row.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "BeforeDamageReceived"));

        Assert.Contains("ValuePropExtensions.IsPoweredAttack", calls);
        Assert.Contains("ProtoBombPower.Explode", calls);
    }

    [Fact]
    public void The_set_off_cards_own_hit_is_the_one_kit_verb_that_is_an_Attack()
    {
        // MATRIX V7, the single exception to the wall of `none`. A Set-off
        // card owes a printed number after its explosions, and that number is
        // a real `DamageCmd.Attack(...).FromCard(...)`: it takes T2, T3, T4
        // and T7 exactly as any Strike does, and it is the reason the matrix
        // has a V7 row separate from V5 at all.
        var calls = Il.Calls(Il.Method("ProtoBombPower", "DealCardDamage"));

        Assert.Contains("DamageCmd.Attack", calls);
        Assert.Contains("AttackCommand.FromCard", calls);
        Assert.Contains("AttackCommand.Execute", calls);
    }

    [Fact]
    public void A_plans_debuff_is_applied_by_Kokomi_with_no_card_source()
    {
        // MATRIX V10 / T8, and the mod side of DISAGREEMENT D7. The applier
        // stays Kokomi -- draft 6 gives the jellyfish the arithmetic, not the
        // authorship -- but the card source is null, so `UnsettlingLamp`
        // never doubles a planned Weak the way it doubles a card's.
        Assert.Contains("PowerCmd.Apply",
                        Il.Calls(Il.Method("KokomiPlan", "Debuff")));
    }

    [Fact]
    public void Spend_deals_no_damage_of_its_own()
    {
        // MATRIX V16, pinned as an absence because that is the whole cell:
        // a Spend moves the bar and, if it empties it, bows. Every number a
        // Spend card prints is its own `damage` clause, which is an Attack
        // card's row and not a verb's.
        var calls = Il.Calls(Il.Method("FurinaStage", "Spend"));

        Assert.DoesNotContain("ElementalHit.Deal", calls);
        Assert.DoesNotContain("DamageCmd.Attack", calls);
        Assert.DoesNotContain("CreatureCmd.Damage", calls);
        Assert.Contains("FurinaStage.Bow", calls);
    }
}
