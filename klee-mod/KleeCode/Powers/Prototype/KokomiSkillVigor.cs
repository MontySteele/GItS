#nullable enable

using System.Threading.Tasks;
using HarmonyLib;
using KleeMod.Cards.Prototype.Generated;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;

namespace KleeMod.Powers;

/// <summary>
/// Kokomi round 4 (2026-10-13), item 3: Opening Gambit's and Second Wave's
/// now-line damage no longer spends Vigor. Both are Skills; Vigor is "your
/// next Attack". Lane 3 F7: "Vigor's text says next Attack", and Gambit ate it.
///
/// WHY A PATCH. The base game's <c>VigorPower</c> reads the HIT, not the card:
/// <c>BeforeAttack</c> latches any powered <c>AttackCommand</c> whose source is
/// a card (0.111.0 decompile), and <c>ModifyDamageAdditive</c> adds the amount
/// to any powered hit. Both cards deal through <c>DamageCmd.Attack</c> so that
/// Strength, Weak and Vulnerable still read them (`EB-469`/`EB-481`); making
/// the hit unpowered would drop those too. So Vigor alone is told to look past
/// these two sources: no bonus, no latch, and the stack waits for the next
/// Attack.
///
/// The Companions' next-Attack riders need nothing: <c>NextAttackRiderPower</c>
/// already refuses a card whose type is not Attack. The sim needs nothing:
/// <c>effects</c> pops <c>next_attack_up</c> only on an Attack.
/// </summary>
public static class KokomiSkillVigor
{
    /// <summary>Is <paramref name="source"/> one of the two Skills whose
    /// now-line Vigor must not read?</summary>
    public static bool Exempt(object? source) =>
        source is ProtoKkOpeningGambit or ProtoKkSecondWave;

    /// <summary>The <c>ModifyDamageAdditive</c> prefix's body: false (skip
    /// the original) with 0 when the hit comes from an exempt card.</summary>
    public static bool ModifyPrefix(CardModel? cardSource, ref decimal result)
    {
        if (!Exempt(cardSource)) return true;
        result = 0m;
        return false;
    }

    /// <summary>The <c>BeforeAttack</c> prefix's body: false (skip the
    /// latch) when the command comes from an exempt card.</summary>
    public static bool BeforeAttackPrefix(object? modelSource, ref Task result)
    {
        if (!Exempt(modelSource)) return true;
        result = Task.CompletedTask;
        return false;
    }
}

// lint: no-seat: scoped by the card itself, Opening Gambit or Second Wave,
// which only the Kokomi arm prints. It must run on every character, because
// the rule is the card's (a Skill is not an Attack) whoever plays it; it
// resolves no seat and reads only the hit's source card.
[HarmonyPatch(typeof(VigorPower), nameof(VigorPower.ModifyDamageAdditive))]
internal static class VigorPower_SkillNowLine_Modify_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(CardModel? cardSource, ref decimal __result) =>
        KokomiSkillVigor.ModifyPrefix(cardSource, ref __result);
}

// lint: no-seat: scoped by the card itself, Opening Gambit or Second Wave,
// which only the Kokomi arm prints. It must run on every character, because
// the rule is the card's (a Skill is not an Attack) whoever plays it; it
// resolves no seat and reads only the hit's source card.
[HarmonyPatch(typeof(VigorPower), nameof(VigorPower.BeforeAttack))]
internal static class VigorPower_SkillNowLine_BeforeAttack_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(AttackCommand command, ref Task __result) =>
        KokomiSkillVigor.BeforeAttackPrefix(command.ModelSource, ref __result);
}
