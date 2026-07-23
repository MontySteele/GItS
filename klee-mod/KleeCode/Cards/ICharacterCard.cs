namespace KleeMod.Cards;

/// <summary>
/// Identifies the playable character whose personal pool owns a card.
///
/// Character-aware mechanics use this marker instead of namespaces, display
/// names, or concrete classes. Companion cards remain identified separately
/// by <see cref="ICompanionCard"/> because their character is the guest, not
/// the run's playable character.
/// </summary>
public interface ICharacterCard
{
    /// <summary>Stable YAML/roster id, such as "furina".</summary>
    string CharacterId { get; }
}
