# Run telemetry Worker

A Cloudflare Worker with one route, `POST /v1/run`, that stores one trimmed record per finished run of
the Teyvat Spire beta in a D1 database. This folder is the server side; the mod's side is
`klee-mod/KleeCode/RunStats/`, compiled only into a beta package built with `--telemetry-endpoint`
(`docs/current/operations/workshop.md`).

**Two switches gate every upload, and both must be on.** (1) The game's own "Upload data" setting: when
modded, the game skips Mega Crit's upload and calls `ModManager.OnMetricsUpload(run, isVictory,
localPlayerId)` instead, only with that setting on, and never for an abandoned run, a debug build or a
first-ever run (`MetricUtilities.UploadRunMetricsInternal`). (2) The mod's own opt-in switch, "Share
anonymous run stats with the Teyvat Spire developers" in BaseLib's mod config, default off.

## What is collected (schema v1, `schema/run-v1.json`)

| field | what |
|---|---|
| `schema_version`, `run_uuid`, `install_id` | `1`; a random UUID v4 per run (repeats are no-ops); a random UUID v4 per install, made and stored by the mod, never derived from Steam |
| `mod_version`, `variant`, `build_id` | mod version; `beta` or `public`; the game's build id |
| `character`, `ascension`, `game_mode` | character id, 0 to 20, e.g. `standard` |
| `coop`, `partners` | co-op flag; the other players' **character ids** (no player ids) |
| `victory`, `floor_reached`, `act_reached`, `acts` | result, floors, act number, act ids |
| `killed_by_encounter`, `killed_by_event` | encounter or event id, or null |
| `run_time_s` | run time in seconds |
| `deck` | final deck: `{id, upgrades}` per card |
| `relics` | final relic ids |
| `floors` | per map point: `floor`, `act`, `type`, `room` id, `hp`, `max_hp`, `damage_taken`, and when cards were offered `card_choice: {offered, picked}` (`picked` empty = skipped) |
| `ancients` | per Ancient: `floor`, `offered` ids, `picked` id |

Every string is an id or a version: at most 96 characters, no spaces, so no free text fits. Every array has
a maximum length, an unknown field at any level is rejected, and the body limit is 64 KB (the 186 finished
runs in the dev history trim to 6.7 KB on average, 16.3 KB at most).

**Never collected:** Steam id, net id or player id; player names; any free text; seed; gold; potions. The
client IP is never stored: it is hashed (SHA-256) and handed to Cloudflare's rate limiter as a key, then
dropped. Request logging (`observability`) is off in `wrangler.toml`.

## Server behaviour

- `POST /v1/run`: 204 on accept and on a repeated `run_uuid`; 400 on bad JSON, a schema miss or a body over
  64 KB; 429 past 20 requests a minute from one IP (the `IP_LIMITER` binding) or 60 runs a day from one
  install (counted in `runs`, `INSTALL_RUNS_PER_DAY`). Every other method or path is 404.
- Table `runs` (`migrations/0001_init.sql`): `id` (= `run_uuid`), `received_at`, `install_id`,
  `schema_version`, `mod_version`, `variant`, `character`, `ascension`, `victory`, `floor_reached`, `payload`.
- **Retention:** a daily cron deletes rows older than `RETENTION_DAYS` (365).

## Test (no account needed)

    cd telemetry-worker && npm install && npm test        # vitest in the Workers runtime (Miniflare)
    npm run typecheck

## Deploy (the account owner)

    cd telemetry-worker && npm install
    npx wrangler login
    npx wrangler d1 create gits-telemetry      # copy the printed database_id into wrangler.toml
    npx wrangler d1 migrations apply gits-telemetry --remote
    npx wrangler deploy                        # prints the https://gits-telemetry.<account>.workers.dev URL

The URL goes to `tools/package_workshop.py --variant beta --telemetry-endpoint URL`. No secrets are
needed.

## Pull the data

    python tools/telemetry_remote.py                  # runs by character, win rate, floor reached, top picks/passes
    python tools/telemetry_remote.py --variant beta --since-days 14 --top 15
    python tools/telemetry_remote.py --dump runs.jsonl
    python tools/telemetry_remote.py --local          # against `npx wrangler dev`'s local DB

Raw SQL: `npx wrangler d1 execute gits-telemetry --remote --json --command "SELECT ..."`.

## Workshop privacy paragraph (DRAFT)

`tools/package_workshop.py` adds this, as plain text, to the beta's description when it is given an
endpoint (`PRIVACY_PARAGRAPH`, which also names where the setting is).

> **Run data (optional).** If you turn on "Share anonymous run stats with the Teyvat Spire developers"
> in the mod's settings *and* the game's own
> "Upload data" setting is on, the mod sends a short summary of each finished run to the Teyvat Spire
> developers: your character, ascension, result, the cards and relics you ended with, which cards you were
> offered and took, and your HP floor by floor. It holds no Steam id, name, chat or other personal details,
> and your IP address is not stored. Runs are tied only to a random id made by the mod on your machine.
> Data is used to balance the mod and deleted after a year. Turn the switch off at any time to stop.
