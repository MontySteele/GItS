using System.Collections.Generic;

namespace KleeMod.Vfx;

/// <summary>
/// KOKOMI'S PLAN STRIP AND VIEW, KEYED (the localization census, 2026-10-23,
/// step 3). The words under a waiting Plan's picture on the strip
/// (<c>KokomiPlan.StripCaption</c>, <c>KokomiPlan.LiveLine</c>), the strip's
/// marks and pager, the Plans view's captions, prompts and button hint, and
/// the refusals a flip can meet. Each is a <see cref="CodeRow"/> in
/// <c>card_keywords</c> under <c>KLEEMOD-KOKOMI_PLAN_STRIP.*</c> or
/// <c>KLEEMOD-KOKOMI_PLAN_VIEW.*</c>, its numbers vars, its plurals
/// SmartFormat's.
///
/// NOT HERE: the jellyfish's wire line (<c>KurageBeat.Line</c>, "Bake-Kurage:
/// Ambush, 12"), which only the blind page prints since the art polish
/// (2026-10-21) put a caption of the card and its number over the pet, and
/// the lower-case refusals <c>KokomiPlan.RequestFlip</c> hands the bridge.
/// Both are seat text.
/// </summary>
public static class KokomiPlanText
{
    private const string Table = "card_keywords";
    private const string Strip = "KLEEMOD-KOKOMI_PLAN_STRIP.";
    private const string View = "KLEEMOD-KOKOMI_PLAN_VIEW.";

    private static CodeRow S(string leaf, string english) => new(Table, Strip + leaf, english);
    private static CodeRow V(string leaf, string english) => new(Table, View + leaf, english);

    // ---- the strip's captions (`KokomiPlan.LiveLine`, `.StripCaption`) ----
    public static readonly CodeRow Energy = S("energy", "Energy {Amount}");
    public static readonly CodeRow Attackers = S("attackers", "{N} attacker{N:plural:|s}");
    public static readonly CodeRow RandomCompanion = S("random_companion", "Random Companion");
    public static readonly CodeRow Copies = S("copies", "Copies {Name}");
    public static readonly CodeRow Deals = S("deals", "Deals {Amount}");
    public static readonly CodeRow Hits = S("hits", "{N} hit{N:plural:|s}");
    public static readonly CodeRow HpLost = S("hp_lost", "HP lost");
    public static readonly CodeRow Blocked = S("blocked", "{Amount} blocked so far");
    public static readonly CodeRow BlockedDeals = S("blocked_deals", "{Amount} blocked, deals {Deals}");
    public static readonly CodeRow Taken = S("taken", "{Amount} taken so far");
    public static readonly CodeRow TakenDeals = S("taken_deals", "{Amount} taken, deals {Deals}");
    public static readonly CodeRow NoAttackYet = S("no_attack_yet", "No attack yet");
    public static readonly CodeRow NoAttackIntended = S("no_attack_intended", "No enemy intends to attack");
    public static readonly CodeRow NoAttackDeals = S("no_attack_deals", "No enemy intends to attack: deals {Deals}");
    public static readonly CodeRow Block = S("block", "Block {Amount}");
    public static readonly CodeRow IntoBlockOf = S("into_block_of", "into {Amount} Block");
    public static readonly CodeRow IntoBlock = S("into_block", "into Block");

    // ---- the strip's marks and pager --------------------------------------
    public static readonly CodeRow PlanLine = S("plan_line", "Plan line");
    public static readonly CodeRow NowLine = S("now_line", "Now-line");
    public static readonly CodeRow NowLineNotDoubled = S("now_line_not_doubled", "Now, not doubled");
    public static readonly CodeRow First = S("first", "First");
    public static readonly CodeRow PlanAt = S("plan_at", "Plan {N}");
    public static readonly CodeRow Back = S("back", "Back");
    public static readonly CodeRow More = S("more", "+{N}");

    // ---- the Plans view ----------------------------------------------------
    public static readonly CodeRow PlanOnly = V("plan_only", "Plan only");
    public static readonly CodeRow Hint = V("hint", "Plans");
    public static readonly CodeRow HintKey = V("hint_key", "{Key}: Plans");
    public static readonly CodeRow Caption = V("caption", "{N}. {Line}");
    public static readonly CodeRow FlipToPlanLine = V("flip_to_plan_line", "{Title}: flipping to its Plan line.");
    public static readonly CodeRow FlipToNowLine = V("flip_to_now_line", "{Title}: flipping to its now-line.");
    public static readonly CodeRow FlipToNowLineLosesDouble = V("flip_to_now_line_loses_double",
        "{Title}: flipping to its now-line. Opening Gambit's double damage does not reach a now-line.");
    public static readonly CodeRow LosesDouble = V("loses_double",
        "Opening Gambit's double damage does not reach a now-line.");
    public static readonly CodeRow NoLongerWaiting = V("no_longer_waiting", "That Plan is no longer waiting.");

    // ---- a flip refused (the view's prompt) --------------------------------
    public static readonly CodeRow NoKurage = V("refused_no_kurage", "There is no Bake-Kurage here.");
    public static readonly CodeRow NotYourTurn = V("refused_not_your_turn", "A Plan can be flipped only during your turn.");
    public static readonly CodeRow NoPlanAt = V("refused_no_plan", "There is no waiting Plan {N}.");
    public static readonly CodeRow OneLine = V("refused_one_line", "{Title} has only one line.");

    // ---- Scry's auto-take (`ScryTake.AutoTakeLine`) -----------------------
    public static readonly CodeRow AutoTake = new(Table, "KLEEMOD-SCRY_TAKE.auto_take",
        "Only one card left to look at: {Title} taken.");

    public static IEnumerable<CodeRow> Rows() => new[]
    {
        Energy, Attackers, RandomCompanion, Copies, Deals, Hits, HpLost, Blocked, BlockedDeals,
        Taken, TakenDeals, NoAttackYet, NoAttackIntended, NoAttackDeals, Block, IntoBlockOf, IntoBlock,
        PlanLine, NowLine, NowLineNotDoubled, First, PlanAt, Back, More,
        PlanOnly, Hint, HintKey, Caption, FlipToPlanLine, FlipToNowLine, FlipToNowLineLosesDouble,
        LosesDouble, NoLongerWaiting, NoKurage, NotYourTurn, NoPlanAt, OneLine, AutoTake,
    };

    /// <summary>The row, read.</summary>
    public static string Text(CodeRow row, params (string Name, object Value)[] vars) =>
        CodeText.Format(row, vars.Length == 0 ? null : CodeText.Vars(vars));
}
