using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json.Nodes;

namespace KleeMod.Diagnostics;

/// <summary>
/// ONE STORY CHOICE (ruled 2026-10-19, the story rewards paper, item 4:
/// "Telemetry logs each story choice (event, option, HP, Gold, deck size at
/// the time), and the next seat rounds judge the prices"). A `record: "story"`
/// row in the same JSONL feed as the fight records (<see cref="PlayTelemetry"/>),
/// which every fight reader filters out by its `record` key.
///
/// The state is read BEFORE the option's effects run; what the option gave is
/// filled in as the effects run: the cards a choose-one screen offered and the
/// one taken, cards added outright, relics gained and potions offered. PURE
/// and public so the headless suite pins the keys; the key names are the
/// schema (<c>tools/telemetry_report.py --story</c> reads them).
/// </summary>
public sealed class StoryChoiceRecord
{
    public string Event = string.Empty;
    public string Option = string.Empty;
    /// <summary>The display title, as the fight records file it (`Klee`, `The Ironclad`).</summary>
    public string Character = string.Empty;
    public string CharacterId = string.Empty;
    public int Act;
    public int Floor;
    public int Seats = 1;
    public int SeatIndex;
    public int HpBefore;
    public int MaxHpBefore;
    public int GoldBefore;
    public int DeckBefore;

    /// <summary>The act's event room this story fired in, 1-based (1, 2 or 3
    /// under the ruled schedule; later when a base substitution took the due
    /// room).</summary>
    public int EventRoom;

    public readonly List<(string Id, bool Upgraded)> CardsOffered = new();
    public readonly List<(string Id, bool Upgraded)> CardsPicked = new();
    public readonly List<(string Id, bool Upgraded)> CardsAdded = new();
    public readonly List<string> RelicsGained = new();
    public readonly List<string> PotionsOffered = new();

    /// <summary>The row, with the feed's linkage keys the writer supplies.</summary>
    public JsonObject ToJson(string schema, string feed, string intent, string runId,
                             string runInstance, double ts)
    {
        return new JsonObject
        {
            ["record"] = "story",
            ["schema"] = schema,
            ["feed"] = feed,
            ["source"] = "mod",
            ["intent"] = intent,
            ["run_id"] = runId,
            ["run_instance"] = runInstance,
            ["seats"] = Seats,
            ["seat_index"] = SeatIndex,
            ["character"] = Character,
            ["character_id"] = CharacterId,
            ["event"] = Event,
            ["option"] = Option,
            ["act"] = Act,
            ["floor"] = Floor,
            ["event_room"] = EventRoom,
            ["hp_before"] = HpBefore,
            ["max_hp_before"] = MaxHpBefore,
            ["gold_before"] = GoldBefore,
            ["deck_before"] = DeckBefore,
            ["cards_offered"] = Cards(CardsOffered),
            ["cards_picked"] = Cards(CardsPicked),
            ["cards_added"] = Cards(CardsAdded),
            ["relics_gained"] = Strings(RelicsGained),
            ["potions_offered"] = Strings(PotionsOffered),
            ["ts"] = double.Parse(ts.ToString("F3", CultureInfo.InvariantCulture),
                                  CultureInfo.InvariantCulture),
        };
    }

    private static JsonArray Cards(IEnumerable<(string Id, bool Upgraded)> cards) =>
        new(cards.Select(c => (JsonNode)new JsonObject
        {
            ["id"] = c.Id,
            ["upgraded"] = c.Upgraded,
        }).ToArray());

    private static JsonArray Strings(IEnumerable<string> ids) =>
        new(ids.Select(s => (JsonNode)JsonValue.Create(s)!).ToArray());
}
