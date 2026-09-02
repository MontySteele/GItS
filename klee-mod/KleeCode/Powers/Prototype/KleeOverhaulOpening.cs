using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

namespace KleeMod.Powers;

/// <summary>
/// RULE 4's OPENING SPARK (R242 pick 1): Klee starts every combat with
/// <see cref="KleeOverhaulLaw.OpeningSpark"/>.
///
/// WHY IT IS A KIT RULE AND NOT A RELIC CLAUSE. The slice packet's sec.3 lists
/// it under the relic paragraph, but the ruled brief's RULE 4 is what carries
/// the line (R242: "Rule 4 in the brief carries the line"), and the difference
/// is load-bearing: Touch of Orobas swaps <c>PoundingSurprise</c> for
/// <c>ExplosiveFrags</c> at the act-2 starter-relic reward, and that relic's
/// own opening bank is deliberately gated OFF under this arm. A relic clause
/// would silently take the opening Spark away from a player who upgraded, which
/// is the opposite of what the pick bought.
///
/// THE SITE, AND IT IS THE SIM's. <c>BeforeCombatStart()</c> sounds right and
/// is wrong twice over, for the two reasons <c>ExplosiveFrags</c> already
/// records: it carries no <c>PlayerChoiceContext</c> (granting a power needs
/// one), and the sim fires its combat-start effects on TURN 1 after the block
/// clear, energy reset and draw, not before the combat exists
/// (<c>combat.py _player_turn</c>, <c>if state.turn == 1</c>). Turn 1 of
/// <c>AfterPlayerTurnStart</c> is that same moment, and it is the moment the
/// blind-play page renders its first Spark line -- which is the acceptance
/// condition the packet states ("the Spark line must show it on turn one").
///
/// <c>TurnNumber == 1</c> rather than <c>&lt;= 1</c> so an extra first turn
/// cannot pay twice, and per-PLAYER so a co-op partner's turn counter cannot
/// mint Klee's Spark. Identity through <see cref="IKleeCharacter"/>, which is
/// what <c>tools/lint_prototype_patch_scope.py</c> requires of anything running
/// on every seat at the table under the one prototype switch.
///
/// FLAG OFF IT DOES NOT RUN. The <c>KleeOverhaul.Enabled</c> guard is first, so
/// a build carrying the quarantine but not the arm -- and every release build,
/// which does not compile this file at all -- is byte for byte what it was.
/// </summary>
internal static class KleeOverhaulOpening
{
    internal static async Task GrantSpark(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (!KleeOverhaul.Enabled) return;
        if (player.Character is not IKleeCharacter) return;
        if (player.PlayerCombatState?.TurnNumber != 1) return;
        if (player.Creature is not { } creature) return;

        await SparkPower.Gain(
            choiceContext, creature, KleeOverhaulLaw.OpeningSpark,
            cardSource: null, source: "klee_overhaul/opening_spark");
    }
}
