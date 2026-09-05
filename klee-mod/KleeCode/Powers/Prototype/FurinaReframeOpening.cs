using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Powers;

/// <summary>
/// R258 (`EB-479`): under the reframe Furina starts every combat with
/// <see cref="FurinaReframeLaw.OpeningEncore"/> Encore.
///
/// WHAT THE PICK BUYS. Rounds 5 to 8 each read her first turn as no decision
/// at 0 Encore, and round 9 called the opening "by construction its own
/// weakest version": both of the arm's turn-one doors -- a Spotlight
/// designation and a member performing wet rather than at 3/4 -- cost Encore,
/// and she had none. Two is the price of exactly one of them, so the opening
/// buys one move and never two.
///
/// THE ARM AND NOT A LEG. This is a fact about the whole reframe rather than
/// about the manual stage, the Evoke or the meter, so it asks
/// <see cref="FurinaReframe.LiveFor"/> -- the master flag -- and the sim's
/// <c>furina_reframe.opening_encore</c> asks the same question the same way.
///
/// THE SITE IS <c>KleeOverhaulOpening</c>'s, and its argument carries over
/// whole: <c>BeforeCombatStart()</c> sounds right and is wrong, because the
/// sim fires its combat-start effects on TURN 1 after the block clear, the
/// energy reset and the draw rather than before the combat exists
/// (<c>combat.py _player_turn</c>). Turn 1 of <c>AfterPlayerTurnStart</c> is
/// that same moment, and it is the moment the blind-play page renders its
/// first Encore line -- which is where the number has to show.
///
/// <c>TurnNumber == 1</c> rather than <c>&lt;= 1</c> so an extra first turn
/// cannot pay twice, and per-PLAYER so a co-op partner's turn counter cannot
/// mint hers. Identity is <see cref="FurinaReframe.IsFurina"/>, which is what
/// <c>tools/lint_prototype_patch_scope.py</c> requires of anything running on
/// every seat at the table under the one prototype switch.
///
/// FLAG OFF IT DOES NOT RUN, and a release build does not compile this file at
/// all -- so a shipped Furina opens on 0 Encore exactly as she always has.
///
/// PUBLIC WHERE <c>KleeOverhaulOpening</c> IS INTERNAL, and the difference is
/// what the pins can do: the Spark's grant routes through <c>PowerCmd</c> and
/// is outside the headless boundary, so its pins are structural and internal
/// is enough. Encore's funnel needs a <c>PlayerCombatState</c> and nothing
/// else, so <c>FurinaReframeRuleTests</c> calls this for real and checks the
/// number that lands -- which it cannot do through an internal.
/// </summary>
public static class FurinaReframeOpening
{
    public static void GrantEncore(Player player)
    {
        if (player.Creature is not { } creature) return;
        if (!FurinaReframe.LiveFor(creature)) return;
        if (player.PlayerCombatState?.TurnNumber != 1) return;

        // The one Encore funnel, which is what keeps the gauge and the stage
        // ribbon in step with the number: `FurinaResources.GainEncore`. No
        // Fanfare prints on the way in (Track A), so an opening bank is not
        // also an opening mint.
        FurinaResources.GainEncore(creature, FurinaReframeLaw.OpeningEncore);
    }
}
