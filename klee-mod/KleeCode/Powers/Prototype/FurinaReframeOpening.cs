using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;

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

    /// <summary>
    /// `EB-553` (R260): who is already on the stage when the fight opens, or
    /// NULL where nobody is.
    ///
    /// THE MEMBER IS NAMED AND NOT ROLLED, which is `EB-416`'s finding one
    /// rule over: under <see cref="FurinaReframe.ManualLiveFor"/> the FRONT
    /// member is the one a Companion play makes perform, so a rolled opening
    /// would decide for the player which member their first trigger fires.
    /// Mademoiselle Crabaletta is the starter deploy's own member
    /// (<c>ProtoFrSalonDebutNamed</c>) and the one the ruling names.
    /// </summary>
    public static readonly SalonMember OpeningMember = SalonMember.Crabaletta;

    /// <summary>
    /// Should this seat's stage be fielded right now? The decision half, split
    /// out from <see cref="FieldOpeningMember"/> for the reason every rule in
    /// this arm splits: <c>SalonMemberPower.Deploy</c> resolves through
    /// <c>PowerCmd</c> and <c>ElementalHit</c> and is outside the headless
    /// boundary, while the question "does the arm field anybody, for this
    /// creature, on this turn" is a pure read the pins can ask for real.
    /// </summary>
    public static SalonMember? OpeningMemberFor(Player player)
    {
        if (player.Creature is not { } creature) return null;
        if (!FurinaReframe.LiveFor(creature)) return null;
        if (player.PlayerCombatState?.TurnNumber != 1) return null;
        return OpeningMember;
    }

    /// <summary>
    /// `EB-553` (R260): under the reframe EVERY combat opens with a member
    /// already on the Salon stage, the way the Necrobinder's Osty and the
    /// Defect's first orb are already out.
    ///
    /// WHAT THE PICK BUYS. Round 11 read both lanes' turn one as empty BY
    /// CONSTRUCTION -- the stage starts unlit, so on turn one every Companion
    /// card prints "performs nobody" -- and the natural lane's count is the
    /// fact: zero empty turns in the fights where Salon Debut was in the
    /// opening hand, six of twenty-two otherwise. [USER] took the relic option
    /// over Innate on the starter, so the stage is never unlit and Salon Debut
    /// becomes a SECOND body. Duplicates on the stage are legal and always
    /// have been -- <i>Grand Gala</i> deploys Crabaletta twice on the shipped
    /// sheet.
    ///
    /// SHE PERFORMS ON ARRIVAL, because <c>SalonMemberPower.Deploy</c> is the
    /// one deploy and the arm's deploy-performs clause lives inside it. That
    /// is deliberate rather than inherited by accident: the ruling calls this
    /// a deploy, and a deploy performs. It also means the opening Encore
    /// (R258) pays this first performance's 1, so turn one opens on
    /// <see cref="FurinaReframeLaw.OpeningEncore"/> minus
    /// <c>SalonConstants.TickEncoreCost</c> rather than on the full bank.
    ///
    /// THE SITE IS <see cref="GrantEncore"/>'s, one line later and for its
    /// argument taken whole: this engine's combat-start effects fire on TURN 1
    /// after the block clear, the energy reset and the draw. AFTER the grant,
    /// which is the ordering the arithmetic needs -- a performance paid out of
    /// an Encore pool that had not been filled yet would act dry at
    /// three-quarters on the one turn the player cannot have done anything
    /// about it.
    ///
    /// THE LEDGER SURVIVES IT. <c>SalonMemberPower.AfterPlayerTurnStart</c>
    /// empties the turn's performance list, and it is a POWER: the game
    /// broadcasts to powers before the subscribed mod models, so
    /// <c>KleeElementalHooks</c> runs after it and this arrival is recorded on
    /// the turn the page reads. On turn 1 the power does not exist yet anyway.
    ///
    /// FLAG OFF NOTHING IS FIELDED, so a shipped Furina opens on an empty
    /// stage exactly as she always has.
    /// </summary>
    public static async Task FieldOpeningMember(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (OpeningMemberFor(player) is not { } member) return;
        // `cardSource: null` -- no card deployed this member, and the deploy's
        // own mirror apply has taken a null source since `BowLeftmost`.
        await SalonMemberPower.Deploy(
            choiceContext, player.Creature!, 1, cardSource: null, member);
    }
}
