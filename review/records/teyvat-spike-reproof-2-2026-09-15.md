Status: RECORD (spike item-2 re-proof after EB-764/765; feasibility only, nothing measured)

# The Springvale Cheese Cellar, played twice

Follows `review/records/teyvat-spike-reproof-2026-09-15.md`. **Nothing here is measured or
quotable** — no pre-registration, no blind grading, no slate. Loadout untouched.

**Installed.** `deploy_round.py --arms klee,companion,kokomi,furina-stage,teyvat` (the
bridge did not move). Read back: **`0.2.3265+proto.dirty`**, bridge present, 406 staged
card png(s). **The arm is ON in the installed build** — the next calibration deploy must
turn it off.

**Soak (R225).** `--runs 1 --character KLEEMOD-KLEE --max-fights 3` →
**`bounded seed=YCN9UW1U24JQ actions=66 fights=3 defects=0`**. The merge line grew the
third term: `[INFO] [klee] teyvat: loc merged (1 dressed enemy name(s), 0 dressed intent
word(s), 10 converted-event row(s)).` No `TeyvatLoc` NRE. **One** EB-758 music ERROR
(`res://teyvat/music/mondstadt`) — expected, counted, not chased.

## The page, in both runs

Two fresh Mondstadt runs (a visited event is skipped before the read, so each was its own
embark). `force_next_event` logged `debug_state: force_next_event MONDSTADT
ROOM_FULL_OF_CHEESE index 19 -> slot 1`, and the `?` room opened on it. The page:

```
{"event_id": "SPRINGVALE_CHEESE_CELLAR", "event_name": "The Springvale Cheese Cellar",
 "options": [
   {"index": 0, "title": "Taste the Racks",
    "description": "Choose 2 of 8 random Common cards to add to your Deck."},
   {"index": 1, "title": "Haul Out the Back Wall",
    "description": "Lose 14 HP. Obtain the Chosen Cheese.",
    "keywords": [{"name": "The Chosen Cheese",
                  "description": "At the end of combat, gain 1 Max HP."}]}]}
```

**Zero** `AssetLoadException`, **zero** `Asset previously failed to load`, **zero** NREs
from `GenerateInitialOptions` / `CharacterModel.AddDetailsTo`: the portrait draws and both
dressed options are constructed.

**One field still reads null: `body`.** The bridge fills it from
`SafeGetText(() => eventModel.Description)` (`McpMod.StateBuilder.cs:1649`) and it read
null for **Neow's base event page** too, so on this evidence it is not a gap in the
dressed rows: the dressed text reaches the screen by three other routes — the event name,
both option titles and descriptions, and the page-level prompt below.

## Run A — Taste the Racks (Ironclad, seed `P0JY39K8GLYU`)

- Prompt is the **dressed** one: `Choose 2 wheels`.
- **Eight** cards offered, all Common, **8 distinct ids** — no duplicates: Armaments,
  Sword Boomerang, Body Slam, Shrug It Off, Thunderclap, Breakthrough, Tremble, Anger.
- Two taken, and they land in the deck: the next combat's piles sum to **12 cards** and
  contain **Armaments** and **Sword Boomerang**, the two selected.
- HP unchanged, **80/80** — this option costs none, and the event then offers `Proceed`
  and returns to the map: the option completes.

## Run B — Haul Out the Back Wall (Ironclad, seed `6FB00FBWFEQX`)

- HP **73 → 59**, exactly **14 lost**, with Block 0 out of combat.
- Relics **before** `['Burning Blood', 'Pomander']`, **after**
  `['Burning Blood', 'Pomander', 'The Chosen Cheese']` — the relic is granted, and its
  hover reads "At the end of combat, gain 1 Max HP."
- The event then offers `Proceed` and the run returns to the map: the option completes.

## What the evidence closes

- **EB-764 — closes.** Acceptance: *"The forced event opens with a portrait and godot.log
  has no AssetLoadException for it."* **Met verbatim** — the page opened in both runs, the
  log carrying no `AssetLoadException` and no `Asset previously failed to load`.
- **EB-765 — closes.** Acceptance: *"The forced event shows both options, each completes,
  The Chosen Cheese is granted."* **Met verbatim** — both options render with dressed
  titles and descriptions, each was taken and completed to `Proceed` and back to the map,
  and The Chosen Cheese is in the bridge's relic list after run B.
- **EB-761 — closes.** Acceptance: *"A scenario reaches Room Full of Cheese on demand in a
  Mondstadt run and observes the substituted text, both options and The Chosen Cheese."*
  **Met verbatim** — reached on demand by `force_next_event` in two Mondstadt runs, the
  substituted text observed (event name, both option titles and descriptions, and the
  dressed `Choose 2 wheels` prompt), both options observed, and The Chosen Cheese granted.

No row is retired. All four spike items are now met in the real game; EB-758's music ERROR is the one disclosed cost still open.
