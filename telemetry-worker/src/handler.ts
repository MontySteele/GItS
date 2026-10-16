// The telemetry Worker logic: POST /v1/run, and a daily retention sweep.
// src/index.ts is the entry; it may export only handlers, so the helpers and
// constants the tests use live here.
//
// What it keeps: the validated run record (schema/run-v1.json) and the time it
// arrived. What it never keeps: the client IP (hashed, handed to the rate
// limiter, then dropped), or anything the schema does not name.
import { Validator } from "@cfworker/json-schema";
import schema from "../schema/run-v1.json";

export interface Env {
  DB: D1Database;
  IP_LIMITER?: RateLimit;
  RETENTION_DAYS?: string;
  INSTALL_RUNS_PER_DAY?: string;
}

export const MAX_BODY_BYTES = 64 * 1024;
const DAY_S = 86_400;

const validator = new Validator(schema as object, "2020-12", true);

interface RunRecord {
  schema_version: number;
  run_uuid: string;
  install_id: string;
  mod_version: string;
  variant: string;
  character: string;
  ascension: number;
  victory: boolean;
  floor_reached: number;
}

const empty = (status: number) => new Response(null, { status });
const fail = (status: number, error: string) =>
  new Response(JSON.stringify({ error }), {
    status,
    headers: { "content-type": "application/json" },
  });

// Reads at most `max` bytes; null when the body is larger.
async function readBody(req: Request, max: number): Promise<Uint8Array | null> {
  const declared = req.headers.get("content-length");
  if (declared !== null && Number(declared) > max) return null;
  if (req.body === null) return new Uint8Array(0);
  const reader = req.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > max) {
      await reader.cancel();
      return null;
    }
    chunks.push(value);
  }
  const out = new Uint8Array(total);
  let at = 0;
  for (const c of chunks) {
    out.set(c, at);
    at += c.byteLength;
  }
  return out;
}

// The limiter key: a hash, so not even the limiter sees the address.
async function ipKey(ip: string): Promise<string> {
  const data = new TextEncoder().encode(`gits-telemetry/ip/${ip}`);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function intVar(value: string | undefined, fallback: number): number {
  const n = Number(value);
  return Number.isInteger(n) && n > 0 ? n : fallback;
}

async function postRun(req: Request, env: Env): Promise<Response> {
  const bytes = await readBody(req, MAX_BODY_BYTES);
  if (bytes === null) return fail(400, "body over 64 KB");

  let text: string;
  let record: unknown;
  try {
    text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: false }).decode(bytes);
    record = JSON.parse(text);
  } catch {
    return fail(400, "body is not JSON");
  }
  const result = validator.validate(record);
  if (!result.valid) {
    const first = result.errors[result.errors.length - 1];
    return fail(400, `invalid at ${first?.instanceLocation ?? "#"}: ${first?.error ?? "schema"}`);
  }
  const run = record as RunRecord;

  if (env.IP_LIMITER) {
    const ip = req.headers.get("cf-connecting-ip") ?? "unknown";
    const { success } = await env.IP_LIMITER.limit({ key: await ipKey(ip) });
    if (!success) return fail(429, "too many requests");
  }

  const seen = await env.DB.prepare("SELECT 1 FROM runs WHERE id = ?")
    .bind(run.run_uuid)
    .first();
  if (seen !== null) return empty(204);

  const now = Math.floor(Date.now() / 1000);
  const perDay = intVar(env.INSTALL_RUNS_PER_DAY, 60);
  const recent = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM runs WHERE install_id = ? AND received_at > ?",
  )
    .bind(run.install_id, now - DAY_S)
    .first<{ n: number }>();
  if ((recent?.n ?? 0) >= perDay) return fail(429, "daily limit for this install");

  await env.DB.prepare(
    `INSERT INTO runs (id, received_at, install_id, schema_version, mod_version,
       variant, character, ascension, victory, floor_reached, payload)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT (id) DO NOTHING`,
  )
    .bind(
      run.run_uuid,
      now,
      run.install_id,
      run.schema_version,
      run.mod_version,
      run.variant,
      run.character,
      run.ascension,
      run.victory ? 1 : 0,
      run.floor_reached,
      JSON.stringify(record),
    )
    .run();
  return empty(204);
}

export async function sweep(env: Env, nowS = Math.floor(Date.now() / 1000)): Promise<number> {
  const days = intVar(env.RETENTION_DAYS, 365);
  const res = await env.DB.prepare("DELETE FROM runs WHERE received_at < ?")
    .bind(nowS - days * DAY_S)
    .run();
  return res.meta.changes ?? 0;
}

export default {
  async fetch(req: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    if (req.method === "POST" && url.pathname === "/v1/run") return postRun(req, env);
    return empty(404);
  },
  async scheduled(_event: ScheduledController, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(sweep(env));
  },
} satisfies ExportedHandler<Env>;
