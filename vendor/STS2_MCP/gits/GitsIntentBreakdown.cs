// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-607` and `EB-323`. THE TWO FACTS AN INTENT NEVER CARRIED: HOW ITS
// NUMBER WAS ARRIVED AT, AND WHOSE SIDE IT LANDS ON.
//
// ============================================================
// `EB-607` -- THE BREAKDOWN
// ============================================================
//
// THE FIND (Klee r23, lane 1 (c) 3). "Fossil Stalker read 12 before and after
// I gave it Strength 3, while Corpse Slug's number moved." One icon folds a
// modifier in and the other does not, and nothing on any surface says which
// of the two a reader is looking at. `EB-607`'s first half printed the game's
// own `GetIntentLabel` unchanged and named the pair where an icon and its
// sentence disagree -- that is a DETECTOR, and it fires after the fact. The
// half owed was the arithmetic itself.
//
// AND THE ARITHMETIC IS THE GAME'S, NOT OURS. `AttackIntent.GetSingleDamage`
// (decompiled, sts2.dll 0.111.0 `41cef1ea`) is
//
//     decimal num = DamageCalc();
//     Player me = LocalContext.GetMe(owner.CombatState);
//     if (me != null)
//         num = Hook.ModifyDamage(me.RunState, me.Creature.CombatState,
//                                 me.Creature, owner, DamageCalc(),
//                                 ValueProp.Move, null, null,
//                                 ModifyDamageHookType.All,
//                                 CardPreviewMode.None, out var modifiers);
//     return Math.Max(0, (int)num);
//
// so the BASE is `DamageCalc()` -- a public `Func<decimal>` on
// `AttackIntent` -- the FOLDED number is what that call returns, and the
// MODELS THE GAME FOLDED come back in the `out` parameter the game itself
// throws away. `McpMod.StateBuilder.cs` makes that same call and keeps the
// third answer. Nothing here recomputes anything: the moment this file starts
// doing arithmetic of its own, a page can disagree with the icon beside it,
// which is the defect rather than the fix.
//
// THE PAIR THE ROW ASKS FOR is base and folded together: `base 12, folded 12,
// nothing folded` and `base 12, folded 15, Strength` are the two readings the
// r23 seat could not tell apart, and they differ in this block and nowhere
// else on the feed.
//
// ============================================================
// `EB-323` -- THE TARGET
// ============================================================
//
// THE FIND (Klee r7). "`Empower (Buff)` names no target" -- a heading, a
// bracketed kind, and nothing else, on a board of three bodies.
//
// WHAT THE GAME ACTUALLY KNOWS, AND IT IS LESS THAN IT LOOKS.
// `MoveState.Intents` is a list of `AbstractIntent` and NO intent carries a
// target: the bodies arrive at `MoveState.PerformMove(targets)` when the move
// resolves, which is after the telegraph a reader is looking at. So a field
// naming a CREATURE would be an invention, and this file refuses to invent
// one.
//
// WHAT IS ON THE WIRE AND WAS BEING DROPPED IS THE SIDE. `IntentType` is the
// game's own fifteen-value classification and twelve of those values settle
// the side by themselves: an Attack, a Debuff, a StatusCard or a DeathBlow is
// aimed at the player, and a Buff, a Defend, a Heal or a Summon is the
// enemy's own side helping itself. `Escape`, `Sleep`, `Stun`, `Hidden` and
// `Unknown` settle nothing and answer null, which keeps the wire key ABSENT
// and the page exactly as it was -- the same absent/known contract every
// other block on this feed keeps.
//
// SIDE AND NOT BODY, spelled in the printed words a reader uses, because
// "which of the three" is the question the game cannot answer here and the
// page must not pretend it can. The page's own `BUFF_INTENT_CLAUSE` says so
// today; with this key it can say the half that IS known instead.
//
// NO GAME TYPE IN THIS FILE, on `GitsSettledHp.cs`'s terms and for its
// reasons: the classification has exactly one way to look right and be wrong,
// and `klee-mod/KleeTests/GitsIntentBreakdownTests.cs` compiles THIS file to
// pin it rather than a fork of it.

using System.Collections.Generic;
using System.Linq;

// The bridge project sets `<Nullable>enable</Nullable>`; `KleeTests`, which
// compiles this file to pin its two decisions, does not. Declared here so the
// one file reads the same in both.
#nullable enable

namespace STS2_MCP;

/// <summary>`EB-607` / `EB-323`. The two facts an enemy intent never carried:
/// how the game arrived at its number, and whose side it lands on.</summary>
public static class GitsIntentBreakdown
{
    /// <summary>The wire key the breakdown block is published under, inside
    /// the intent's own dictionary. Spelled once so the bridge and the blind
    /// page cannot drift apart.</summary>
    public const string BreakdownKey = "breakdown";

    /// <summary>The number the card/move declares, before any hook.</summary>
    public const string BaseKey = "base_damage";

    /// <summary>The number the game's own hook phases arrived at, per hit.
    /// This is the figure the icon draws for a single-hit intent.</summary>
    public const string FoldedKey = "folded_damage";

    /// <summary>How many times the move repeats that hit.</summary>
    public const string RepeatsKey = "repeats";

    /// <summary>Folded times repeats: what the whole move delivers if every
    /// hit lands. NOT a prediction -- see the header on multi-part moves.
    /// </summary>
    public const string TotalKey = "total_damage";

    /// <summary>The player-facing names of the models the game folded in, in
    /// the order `Hook.ModifyDamage` handed them back.</summary>
    public const string ModifiersKey = "modifiers";

    /// <summary>The wire key the side is published under (`EB-323`).</summary>
    public const string TargetSideKey = "target_side";

    /// <summary>What <see cref="TargetSide"/> says for an intent aimed at the
    /// player's side.</summary>
    public const string SideYou = "you";

    /// <summary>What <see cref="TargetSide"/> says for an intent the enemy
    /// side aims at itself.</summary>
    public const string SideEnemy = "its own side";

    /// <summary>The intent types that settle the side as the player's. Spelled
    /// as the enum's own words (`IntentType.ToString()`), which is what the
    /// wire's `type` field already carries.</summary>
    private static readonly HashSet<string> AtYou = new()
        { "Attack", "Debuff", "DebuffStrong", "StatusCard", "CardDebuff",
          "DeathBlow" };

    /// <summary>The intent types that settle the side as the enemy's own.
    /// </summary>
    private static readonly HashSet<string> AtItself = new()
        { "Buff", "Defend", "Heal", "Summon" };

    /// <summary>
    /// The breakdown block for one attack intent, or null when there is
    /// nothing to say.
    ///
    /// NULL WHEN THE BASE IS NOT A NUMBER THE GAME DECLARED -- a repeat count
    /// of zero, which is what every non-attack intent answers -- so the key
    /// stays ABSENT on the parts it cannot describe rather than printing a
    /// row of zeroes a reader would take for a reading.
    /// </summary>
    public static Dictionary<string, object?>? Compose(
        int baseDamage, int folded, int repeats,
        IEnumerable<string>? modifiers)
    {
        if (repeats <= 0) return null;
        var named = (modifiers ?? Enumerable.Empty<string>())
            .Where(m => !string.IsNullOrWhiteSpace(m))
            .Select(m => m.Trim())
            .ToList();
        return new Dictionary<string, object?>
        {
            [BaseKey] = baseDamage,
            [FoldedKey] = folded,
            [RepeatsKey] = repeats,
            [TotalKey] = folded * repeats,
            [ModifiersKey] = named,
        };
    }

    /// <summary>
    /// Whose side this intent lands on, in the words a reader uses, or null
    /// where the game's own classification does not settle it.
    ///
    /// The argument is the wire's `type` field, which is
    /// `IntentType.ToString()`.
    /// </summary>
    public static string? TargetSide(string? intentType)
    {
        if (string.IsNullOrWhiteSpace(intentType)) return null;
        var t = intentType!.Trim();
        if (AtYou.Contains(t)) return SideYou;
        if (AtItself.Contains(t)) return SideEnemy;
        return null;
    }
}
