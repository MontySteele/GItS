using KleeMod.Elements;

namespace KleeMod.Cards;

/// <summary>
/// Marker for companion cards (docs/mondstadt-companions.yaml): drafted from
/// the 4th reward slot, never in KleeCardPool (tier05 character_pool excludes
/// companions and the game's own reward roll draws from the pool). The
/// element here is the COMPANION's element for reward/UI purposes -- whether
/// a hit applies it is the sheet's explicit applies_element call, carried by
/// IElementalCard exactly as on Klee's own attacks (companions are exempt
/// from catalyst cadence; tier0 effects._element_for).
/// </summary>
public interface ICompanionCard
{
    /// <summary>4 or 5 -- 5-stars are the rare tier of the companion slot.</summary>
    int Star { get; }

    Element CompanionElement { get; }

    /// <summary>
    /// Personal-pool owner character id (Prune is Klee's designated
    /// teammate), or null for the shared nation pool. tier05: personal-pool
    /// cards are only ever offered to their own character.
    /// </summary>
    string? PersonalPool => null;

    /// <summary>
    /// Home nation ("mondstadt", "fontaine"), from the companion sheet the
    /// card came from. The reward slot concentrates
    /// SAME_NATION_REWARD_SHARE of its weight on the run character's nation
    /// (tier05 _nation_weighted_choice); null spreads with the remainder.
    /// </summary>
    string? Nation => null;
}
