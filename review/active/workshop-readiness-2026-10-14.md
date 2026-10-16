# Steam Workshop readiness, 2026-10-14

[USER], 2026-10-14: "My immediate goal is to get at least 4 characters to a
presentable-enough state that we can put this on the Steam Workshop without
feeling embarrassed, along with a functional Spiral Abyss mode." This narrows
`distribution-readiness-2026-10-12.md`: its pick 2 (where it lists) now has
an answer, the Workshop, and its section 2 becomes the checklist below.

## How a Workshop upload works

From Mega Crit's own patch notes (v0.107.1, Major Update 2, which added
Workshop support) and the uploader's README
(`github.com/megacrit/sts2-mod-uploader`):

- `ModUploader.exe` makes a workspace. The mod's files go in its `content`
  folder, the page fields in `workshop.json`, and a preview image as
  `image.png`, **under 1 MB**.
- `ModUploader.exe upload -w <workspace>` publishes. Later uploads update the
  same item (the id is kept in `mod_id.txt`), with a `changeNote`.
- Subscribers enable the mod in the game's Mods menu. Modded saves are
  separate from unmodded ones.

Not answered by those two pages, and checked when we first run the tool:
how a dependency is declared, visibility (private, friends-only, public), and
tags.

## The checklist

| # | Item | State tonight |
|---|---|---|
| 1 | **Four presentable kits** | Klee and Varka at Balance. Furina's design is final and her sweep is built (#1271). Kokomi's overhaul is in its seat round tonight; more passes planned |
| 2 | **Spiral Abyss works start to finish** | Solo seat reached floor 48 (2026-10-12). Tonight's co-op pair is in act 2; two page fixes from it are built (#1268) |
| 3 | **No harness in the package** | The `content` folder gets `mods/klee` only, never `mods/STS2_MCP` or the auto-play mod |
| 4 | **Telemetry off for players** | It writes for everyone today: `PlayTelemetry.cs` tags a run `human` when the harness's `GITS_TELEMETRY_FEED` is unset (line 67) and writes under `user://gits_telemetry`. A release build must write only when that variable is set |
| 5 | **A release version stamp** | Builds read `0.2.NNNN`. A Workshop release takes a plain `0.3.0` |
| 6 | **BaseLib** | We need BaseLib 3.4.7. It is distributed through GitHub and NuGet; I found no Workshop listing. If it isn't on the Workshop, either the uploader can declare it as a required item, or we ship it beside ours, which needs Alchyr's permission. Settle this before the first upload |
| 7 | **Game branch** | We build against v0.111.0 on `public-beta`; Workshop users on `main` may be on an older version. The page must name the branch, and we rebuild after each patch |
| 8 | **Art with no visible gaps** | 6 Kokomi cards draw blank; Yae's 32 are done; Furina's 15 new cards are fetched; the Abyss's icons are stand-ins (BACKLOG) |
| 9 | **Models** | Klee, Furina and Varka are done. Kokomi's is rendered (#1266, deployed in the morning). Yae's is set up and waits for its render |
| 10 | **The page** | Description, the four characters, "Fan-made, not affiliated with HoYoverse or Mega Crit," free, co-op needs matching versions. Preview image under 1 MB |
| 11 | **Tooltips a stranger can read** | Trimmed on #1269 |
| 12 | **Yae** | A fifth kit, 30 cards, two seats tonight (both died in act 1, no crashes). Ship her marked "in progress," or hold her back |

## Picks

**Ruled 2026-10-14.** [USER]: "On Steam, I'm good with the defaults." All three picks (a).

1. **Who uploads:** **(a) you run the uploader from your Steam account**, and
   I prepare the workspace (content, `workshop.json`, image) and a dry run.
   (b) Some other route you name. Uploading is your call: it publishes under
   your account and vouches for the content to Valve.
2. **First visibility:** **(a) friends-only or private first, for your co-op
   friend's group; public once items 1 to 11 are ticked**; (b) public on the
   first upload.
3. **Yae in the first upload:** **(a) hold her back until her model and a card
   pass are done**; (b) include her, marked "in progress."
