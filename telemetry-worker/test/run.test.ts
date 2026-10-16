import { createExecutionContext, env, waitOnExecutionContext } from "cloudflare:test";
import { describe, expect, it } from "vitest";
import worker, { MAX_BODY_BYTES, sweep, type Env } from "../src/handler";
import * as entry from "../src/index";

const E = env as unknown as Env;

let counter = 0;
function uuid(): string {
  return crypto.randomUUID();
}
function freshIp(): string {
  counter += 1;
  return `198.51.${Math.floor(counter / 250)}.${counter % 250}`;
}

// A long, realistic run: 84-card deck, 50 floors, three wide shops.
function record(over: Record<string, unknown> = {}): Record<string, unknown> {
  const floors = Array.from({ length: 50 }, (_, i) => {
    const type = i % 16 === 5 ? "shop" : i % 16 === 0 ? "ancient" : "monster";
    const f: Record<string, unknown> = {
      floor: i + 1,
      act: Math.floor(i / 17) + 1,
      type,
      room: type === "monster" ? "ENCOUNTER.TOADPOLES_WEAK" : null,
      hp: 60,
      max_hp: 78,
      damage_taken: 7,
    };
    if (type !== "ancient") {
      const n = type === "shop" ? 34 : 4;
      const offered = Array.from({ length: n }, (_, k) => `CARD.KLEEMOD-PROTO_FS_SOME_LONG_CARD_NAME_${k}`);
      f.card_choice = { offered, picked: i % 3 === 0 ? [] : [offered[0]] };
    }
    return f;
  });
  return {
    schema_version: 1,
    run_uuid: uuid(),
    install_id: uuid(),
    mod_version: "0.9.0-beta.1",
    variant: "beta",
    build_id: "v0.111.0",
    character: "CHARACTER.KLEEMOD-FURINA",
    ascension: 3,
    game_mode: "standard",
    coop: false,
    partners: [],
    victory: true,
    floor_reached: 50,
    act_reached: 3,
    acts: ["ACT.UNDERDOCKS", "ACT.HIVE", "ACT.GLORY"],
    killed_by_encounter: null,
    killed_by_event: null,
    run_time_s: 3308,
    deck: Array.from({ length: 84 }, (_, k) => ({ id: `CARD.KLEEMOD-PROTO_FS_DECK_CARD_${k}`, upgrades: k % 2 })),
    relics: Array.from({ length: 24 }, (_, k) => `RELIC.KLEEMOD-SALON_RELIC_${k}`),
    floors,
    ancients: [{ floor: 1, offered: ["ARCANE_SCROLL", "PHIAL_HOLSTER", "CURSED_PEARL"], picked: "ARCANE_SCROLL" }],
    ...over,
  };
}

async function send(
  body: string | object,
  opts: { ip?: string; method?: string; path?: string; headers?: Record<string, string> } = {},
): Promise<Response> {
  const text = typeof body === "string" ? body : JSON.stringify(body);
  const req = new Request(`https://telemetry.example${opts.path ?? "/v1/run"}`, {
    method: opts.method ?? "POST",
    headers: { "content-type": "application/json", "cf-connecting-ip": opts.ip ?? freshIp(), ...opts.headers },
    body: (opts.method ?? "POST") === "GET" ? undefined : text,
  });
  const ctx = createExecutionContext();
  const res = await worker.fetch(req, E, ctx);
  await waitOnExecutionContext(ctx);
  return res;
}

async function rowCount(id: string): Promise<number> {
  const r = await E.DB.prepare("SELECT COUNT(*) AS n FROM runs WHERE id = ?").bind(id).first<{ n: number }>();
  return r?.n ?? 0;
}

describe("POST /v1/run", () => {
  it("accepts a valid record with 204 and stores the indexed columns", async () => {
    const rec = record();
    const res = await send(rec);
    expect(res.status).toBe(204);
    expect(await res.text()).toBe("");
    const row = await E.DB.prepare("SELECT * FROM runs WHERE id = ?").bind(rec.run_uuid).first<Record<string, unknown>>();
    expect(row).not.toBeNull();
    expect(row!.install_id).toBe(rec.install_id);
    expect(row!.character).toBe("CHARACTER.KLEEMOD-FURINA");
    expect(row!.variant).toBe("beta");
    expect(row!.victory).toBe(1);
    expect(row!.floor_reached).toBe(50);
    expect(JSON.parse(row!.payload as string)).toEqual(rec);
  });

  it("a realistic long run fits well under the body cap", () => {
    expect(new TextEncoder().encode(JSON.stringify(record())).byteLength).toBeLessThan(MAX_BODY_BYTES / 2);
  });

  it("stores no IP: no column holds the client address", async () => {
    const rec = record();
    const ip = "203.0.113.77";
    expect((await send(rec, { ip })).status).toBe(204);
    const row = await E.DB.prepare("SELECT * FROM runs WHERE id = ?").bind(rec.run_uuid).first<Record<string, unknown>>();
    expect(JSON.stringify(row)).not.toContain(ip);
    const tables = await E.DB.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '\\_%' ESCAPE '\\' AND name NOT LIKE 'd1_%' AND name NOT LIKE 'sqlite_%'").all<{ name: string }>();
    expect(tables.results.map((t) => t.name)).toEqual(["runs"]);
  });

  it("a duplicate run uuid is a 204 no-op", async () => {
    const rec = record();
    expect((await send(rec)).status).toBe(204);
    expect((await send({ ...rec, victory: false })).status).toBe(204);
    expect(await rowCount(rec.run_uuid as string)).toBe(1);
    const row = await E.DB.prepare("SELECT victory FROM runs WHERE id = ?").bind(rec.run_uuid).first<{ victory: number }>();
    expect(row!.victory).toBe(1);
  });

  it("co-op records carry partner character ids", async () => {
    const rec = record({ coop: true, partners: ["CHARACTER.IRONCLAD"] });
    expect((await send(rec)).status).toBe(204);
  });

  const bad: Array<[string, Record<string, unknown>]> = [
    ["an unknown top-level field", { steam_id: "76561197999302235" }],
    ["an unknown nested field", { deck: [{ id: "CARD.X", upgrades: 0, player_id: 1 }] }],
    ["a wrong type", { ascension: "3" }],
    ["a float where an int belongs", { floor_reached: 12.5 }],
    ["an out-of-range ascension", { ascension: 21 }],
    ["a bad variant", { variant: "dev" }],
    ["free text in an id", { character: "my name is Monty" }],
    ["an over-long id", { character: `CHARACTER.${"A".repeat(100)}` }],
    ["a non-v4 install id", { install_id: "76561197999302235" }],
    ["an oversize array", { relics: Array.from({ length: 101 }, () => "RELIC.X") }],
    ["a wrong schema version", { schema_version: 2 }],
  ];
  for (const [name, over] of bad) {
    it(`rejects ${name} with 400`, async () => {
      const rec = record(over);
      const res = await send(rec);
      expect(res.status).toBe(400);
      expect(await rowCount(rec.run_uuid as string)).toBe(0);
    });
  }

  it("a 400 names where the record went wrong", async () => {
    const res = await send(record({ deck: [{ id: "CARD.X", upgrades: "2" }] }));
    expect(res.status).toBe(400);
    const { error } = (await res.json()) as { error: string };
    expect(error).toContain("#/deck/0/upgrades");
  });

  it("rejects a missing required field with 400", async () => {
    const rec = record();
    delete rec.floors;
    expect((await send(rec)).status).toBe(400);
  });

  it("rejects non-JSON and non-object bodies with 400", async () => {
    expect((await send("not json")).status).toBe(400);
    expect((await send("[1,2,3]")).status).toBe(400);
    expect((await send("")).status).toBe(400);
  });

  it("rejects a body over 64 KB with 400, by length and by stream", async () => {
    // Valid JSON for a valid record, padded past the cap with whitespace, so
    // the size is the only thing wrong with it.
    const text = JSON.stringify(record()) + " ".repeat(MAX_BODY_BYTES);
    expect(text.length).toBeGreaterThan(MAX_BODY_BYTES);
    expect((await send(text.slice(0, MAX_BODY_BYTES))).status).toBe(204);
    expect((await send(text)).status).toBe(400);
    // A streamed body with no content-length is cut off at the cap too.
    const stream = new Blob([text]).stream();
    const req = new Request("https://telemetry.example/v1/run", {
      method: "POST",
      headers: { "cf-connecting-ip": freshIp() },
      body: stream,
      duplex: "half",
    } as RequestInit);
    const ctx = createExecutionContext();
    expect((await worker.fetch(req, E, ctx)).status).toBe(400);
  });

  it("limits one install to INSTALL_RUNS_PER_DAY runs a day", async () => {
    const install = uuid();
    const now = Math.floor(Date.now() / 1000);
    const stmt = E.DB.prepare(
      "INSERT INTO runs (id, received_at, install_id, schema_version, mod_version, variant, character, ascension, victory, floor_reached, payload) VALUES (?, ?, ?, 1, 'x', 'beta', 'C', 0, 0, 1, '{}')",
    );
    await E.DB.batch(Array.from({ length: 60 }, () => stmt.bind(uuid(), now - 60, install)));
    expect((await send(record({ install_id: install }))).status).toBe(429);
    // Yesterday's runs do not count.
    const other = uuid();
    await E.DB.batch(Array.from({ length: 60 }, () => stmt.bind(uuid(), now - 90_000, other)));
    expect((await send(record({ install_id: other }))).status).toBe(204);
  });

  it("a retried run already stored is a 204 even past the daily limit", async () => {
    const install = uuid();
    const rec = record({ install_id: install });
    expect((await send(rec)).status).toBe(204);
    const now = Math.floor(Date.now() / 1000);
    const stmt = E.DB.prepare(
      "INSERT INTO runs (id, received_at, install_id, schema_version, mod_version, variant, character, ascension, victory, floor_reached, payload) VALUES (?, ?, ?, 1, 'x', 'beta', 'C', 0, 0, 1, '{}')",
    );
    await E.DB.batch(Array.from({ length: 60 }, () => stmt.bind(uuid(), now, install)));
    expect((await send(rec)).status).toBe(204);
  });

  it("limits one client IP to a burst of 20 a minute", async () => {
    const ip = "192.0.2.10";
    const statuses: number[] = [];
    for (let i = 0; i < 22; i++) statuses.push((await send(record(), { ip })).status);
    expect(statuses.slice(0, 20).every((s) => s === 204)).toBe(true);
    expect(statuses.slice(20)).toEqual([429, 429]);
    expect((await send(record(), { ip: "192.0.2.11" })).status).toBe(204);
  });
});

describe("entry module", () => {
  it("exports only the handler (workerd refuses any other export)", () => {
    expect(Object.keys(entry)).toEqual(["default"]);
    expect(entry.default).toBe(worker);
  });
});

describe("everything else", () => {
  it.each([
    ["GET", "/v1/run"],
    ["PUT", "/v1/run"],
    ["POST", "/"],
    ["POST", "/v1/runs"],
    ["GET", "/"],
  ])("%s %s is 404", async (method, path) => {
    expect((await send(record(), { method, path })).status).toBe(404);
  });
});

describe("retention sweep", () => {
  it("deletes rows older than RETENTION_DAYS and keeps the rest", async () => {
    const now = 2_000_000_000;
    const old = uuid();
    const fresh = uuid();
    const stmt = E.DB.prepare(
      "INSERT INTO runs (id, received_at, install_id, schema_version, mod_version, variant, character, ascension, victory, floor_reached, payload) VALUES (?, ?, ?, 1, 'x', 'beta', 'C', 0, 0, 1, '{}')",
    );
    await E.DB.batch([stmt.bind(old, now - 366 * 86_400, uuid()), stmt.bind(fresh, now - 364 * 86_400, uuid())]);
    await sweep(E, now);
    expect(await rowCount(old)).toBe(0);
    expect(await rowCount(fresh)).toBe(1);
  });
});
