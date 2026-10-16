namespace KleeMod.Story;

/// <summary>
/// THE CO-OP STORY ROOM'S PLACEHOLDER (ruled 2026-10-16,
/// <c>review/active/klee-varka-story-chains-2026-10-14.md</c>, "Co-op"):
/// "for characters who have no events, they get a placeholder like "heal 10
/// or gain 50 gold"". The page a player gets in the act's story room when
/// her character has no story table, her story has no event this act, or
/// hers already fired this act. Base-game template text: a short title, one
/// line, two options.
/// </summary>
public static class StoryCoop
{
    public static readonly StoryEvent QuietLanding = new(
        ActIndex: -1,
        EventType: typeof(StoryCoopRoomEvent),
        Title: "A Quiet Landing",
        Body: "The stairs are quiet here, and nothing on this landing is waiting for you.",
        Options: new[]
        {
            new StoryOption("REST", "Rest.",
                "Heal 10 HP.",
                new StoryEffect(StoryEffectKind.Heal, 10)),
            new StoryOption("SEARCH", "Search the landing.",
                "Gain 50 Gold.",
                new StoryEffect(StoryEffectKind.GainGold, 50)),
        },
        Portrait: () => null,
        FallbackPortraitPath: "res://images/events/wellspring.png");
}
