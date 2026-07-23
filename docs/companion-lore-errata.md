# Companion Lore Errata — Xingqiu → Dahlia (mechanical no-op)

For Claude Code, mid-C2. User caught a lore error: Xingqiu is Liyue (Feiyun Commerce Guild), not Mondstadt. His two cards re-flavor onto Dahlia (Mondstadt 4-star Hydro, Church of Favonius deacon) whose actual kit maps 1:1 onto the same two effects — his Skill zone deals damage + applies Hydro; his Burst grants a shield. **Effects, costs, rarities, roles unchanged. Sim results carry; no re-runs.**

Rename map (apply everywhere: companions yaml, klee.yaml packages, C2 slice list, any generated C#/localization, telemetry ids):
- `xingqiu_raincutter` → `dahlia_sacramental_shower` ("Dahlia — Sacramental Shower")
- `xingqiu_rain_swords` → `dahlia_favonian_favor` ("Dahlia — Favonian Favor")

Art sprint: source from Dahlia's TCG/skill art instead of Xingqiu's; update SOURCES.tsv rows.

Logged for later, not now: (1) Xingqiu joins the future Liyue pool at full strength — in Genshin he's the *better* applier and Dahlia's canonical weakness is poor Hydro application, so when Liyue ships, Dahlia's cards may deserve a slight applier-downgrade + shield-upgrade to restore the real hierarchy; (2) a Benison-flavored Dahlia uncommon rewarding Shatter procs is a natural v0.2 card given his actual Frozen-synergy passive — pleasant coincidence with our Frozen v2; (3) Mona/Jean/Diluc = Mondstadt Rare rotation bench (principles v1.7) — the 3-slot 5-star lineup rotating per mod version is our banner rotation, and it's flavor-perfect that the standard banner characters are the ones waiting their turn.

Process: lore audit (nation checked against wiki) is now on the companion checklist. The sim validates numbers, chat validates structure, the user validates ecosystem pricing — and now also geography.
