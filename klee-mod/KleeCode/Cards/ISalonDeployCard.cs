namespace KleeMod.Cards;

/// <summary>
/// A card that DEPLOYS onto Furina's stage (`EB-637`, `EB-644`).
///
/// A MARKER THE GENERATOR WRITES, the shape <see cref="ICompanionCard"/> and
/// <c>ISkillTagCard</c> take: a sheet row whose effects apply the
/// <c>salon_member</c> power is a deploy card, and `tools/gen_klee_cards.py`
/// says so on the class rather than any reader guessing it from the card's
/// text or its id. What the mark is FOR is the board: the Salon panel reads it
/// off the card under the player's cursor to say, before the card is played,
/// who leaves a full stage and which empty seat fills. Nothing about the
/// deploy RULE lives here -- that is <c>SalonMemberPower.Deploy</c> -- and the
/// count below is the card's static deploy total, which is also what
/// <c>SalonMemberPower.WillReplace</c> is asked with.
/// </summary>
public interface ISalonDeployCard
{
    /// <summary>How many members this card fields when played: the sum of
    /// its <c>salon_member</c> amounts on the sheet. The base amount for a
    /// row whose deploy count upgrades; the preview is a preview.</summary>
    int SalonDeployCount { get; }
}
