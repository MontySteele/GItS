"""One run, start to game_over, with a watchdog on every action.

Cut out of `soak.py` by `EB-180`: `RunDriver` is that file's class, moved
whole and re-exported from it, so `soak.RunDriver(...)` still resolves and a
`monkeypatch.setattr(soak, "RunDriver", ...)` still swaps what `soak.soak`
constructs. The route half of the class -- main menu, embark, character
read-back -- is the `Navigation` mixin in `soak_navigate`.
"""
from __future__ import annotations

import json
import time
from typing import Any

from understudy import deckwatch, hangwatch, naming, policy_v1
from understudy.soak_navigate import Navigation
from understudy.soak_screens import (_escape, _game_over_won, _hazard_event,
                                     _last_resort, _mechanical_action,
                                     _trim_state)
from understudy.soak_session import Session
from understudy.soak_shape import (COMBAT, DEFAULT_CHARACTER, Defect,
                                   GAME_EXE, MAX_ACTIONS_PER_RUN, MID_FIGHT,
                                   NO_PROGRESS_ACTIONS, NO_PROGRESS_CYCLE,
                                   RUN_TIMEOUT_S, SELECTOR_SCREENS,
                                   TIME_SCALE)
from understudy.soak_telemetry import (FightTelemetry, _enemy_pool, _meters,
                                       _telegraphed)


def _soak():
    """`understudy.soak` itself, imported at CALL time.

    The wire and the dials this seam reads are declared on `soak.py`, which
    is also where a caller (and the harness's own tests) reaches in to swap
    them -- `monkeypatch.setattr(soak, "bridge", fake)`. Binding them at
    import would take a private copy here and the swap would never be seen.
    """
    from understudy import soak
    return soak


def _wire():
    """`soak.bridge`, read at CALL time. Same reason as `_soak`."""
    from understudy import soak
    return soak.bridge


class RunDriver(Navigation):
    """One run, start to game_over, with a watchdog on every action."""

    # P2 leg one. A class attribute so every construction path has it --
    # including the test doubles that build a driver without running this
    # __init__ -- and so the OFF state is the default everywhere.
    sampler: Any = None

    # WHICH POLICY THIS DRIVER FLIES, and it is a FIELD because two drivers
    # can now be running at once. `None` means the module's own `policy_v1`,
    # which is every unscripted run. See `run_scripted` below for what this
    # replaced and what the old shape cost.
    policy: Any = None

    @property
    def pol(self) -> Any:
        return self.policy if self.policy is not None else policy_v1

    # EB-117, and a class attribute for the same reason: UNVERIFIED is the
    # default on every construction path, so nothing can read a character name
    # off a driver that never embarked.
    character_actual: str | None = None

    def __init__(self, session: Session, run_index: int, stamp: str,
                 character: str = DEFAULT_CHARACTER,
                 commit: str | None = None,
                 chosen_seed: str | None = None,
                 max_fights: int | None = None,
                 hazard_guard: bool = True,
                 p2_capture: bool = False,
                 policy: Any = None):
        self.session = session
        self.run_index = run_index
        self.character = character
        # EB-117. The character the run ACTUALLY started with, read off the
        # wire after the embark confirm fires. `None` until then, and `None`
        # is what every downstream stamp carries for a run that never got
        # there -- an unverified run has no character name, rather than
        # borrowing the requested one.
        self.character_actual: str | None = None
        # EB-1. ON by default: this is a defence against a known soft-lock,
        # not a policy. `--allow-hazard-events` turns it off for the one job it
        # is in the way of, which is deliberately reproducing the hang.
        self.hazard_guard = hazard_guard
        # P1.5 item 1. `None` is the R95 read-back arm -- the game rolls, we
        # record. A string is a CHOSEN seed, and the run verifies the choice
        # took rather than trusting the endpoint's answer.
        self.chosen_seed = chosen_seed
        # P1.5: stop cleanly after N closed fights. `None` is a full run.
        self.max_fights = max_fights
        # R99/4b. `None` is baseline -- the arm the R98 validation ran, and the
        # only arm whose numbers are comparable to R98's.
        self.commit = commit
        self.stamp = stamp
        self.policy = policy
        self.memo = self.pol.Memo()
        # P2 leg one (R94). OFF unless the soak asked for it; the baseline arm
        # R98 validated is the arm without it. Capture only -- no model is
        # called from this loop.
        if p2_capture:
            from understudy import p2capture
            self.sampler = p2capture.Sampler(stamp, run_index, enabled=True)
        self.seed: str | None = None
        # THE LANE IS IN THE FILE NAME, and the live proof is why. Two
        # lanes staging at once both reach `stage_board`, which stamps
        # the second, so both drivers took `soak-<stamp>-run001.jsonl`
        # and wrote ONE interleaved file -- two runs' records mixed,
        # with nothing on a row saying which run it belonged to. The
        # single-lane name is unchanged: a session with no lane adds
        # no infix.
        lane = getattr(getattr(session, "instance", None), "label", "")
        infix = f"-{lane}" if lane else ""
        self.log = (_soak().LOG_DIR
                    / f"soak-{stamp}{infix}-run{run_index:03d}.jsonl")
        self.actions = 0
        self.started = time.time()
        self.fights: list[FightTelemetry] = []
        self.fight: FightTelemetry | None = None
        self.defects: list[dict] = []
        self._fingerprints: list[str] = []
        self._last_state: dict[str, Any] | None = None
        self._forced_defaults = 0
        self._last_mech: tuple | None = None
        self._mech_repeats = 0

    # -- logging ----------------------------------------------------------
    def emit(self, record: dict) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        record.setdefault("ts", time.time())
        record.setdefault("run", self.run_index)
        record.setdefault("seed", self.seed)
        with self.log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def file_defect(self, kind: str, detail: str, state: dict,
                    extra: dict | None = None) -> dict:
        rec = {
            "record": "defect", "kind": kind, "detail": detail,
            "seed": self.seed, "run": self.run_index,
            "act": (state.get("run") or {}).get("act"),
            "floor": (state.get("run") or {}).get("floor"),
            "state_type": state.get("state_type"),
            "actions_taken": self.actions,
            # Recorded on EVERY defect, not just the process ones: "was the
            # game still running when this was filed" is the first question
            # asked of any row in this table, and reconstructing it afterwards
            # from a killed process is impossible.
            "proc_exit_code": self.session.exit_code,
            "state_dump": _trim_state(state),
            "recent": self._fingerprints[-NO_PROGRESS_ACTIONS:],
        }
        # Extra keys are ADDED, never allowed to overwrite: a defect row's
        # identity fields are the row, and a watchdog's evidence blob must not
        # be able to rename the kind it was filed under.
        for k, v in (extra or {}).items():
            rec.setdefault(k, v)
        self.defects.append(rec)
        self.emit(rec)
        return rec

    # -- watchdog ---------------------------------------------------------
    def _fingerprint(self, state: dict[str, Any]) -> str:
        from understudy import adapter
        p = state.get("player") or {}
        run = state.get("run") or {}
        b = state.get("battle") or {}
        return "|".join(str(x) for x in (
            state.get("state_type"), state.get("menu_screen"),
            run.get("act"), run.get("floor"), b.get("round"),
            p.get("hp"), p.get("energy"), len(p.get("hand") or []),
            _enemy_pool(state) if state.get("state_type") in COMBAT else "-",
            len(state.get("options") or []),
        ))

    def _check(self, state: dict[str, Any]) -> None:
        if not self.session.alive():
            raise Defect("process_died",
                         "the game process exited while the run was in "
                         "progress; godot.log holds the stack trace", state)
        hazard = _hazard_event(state) if getattr(
                self, "hazard_guard", True) else None
        if hazard is not None:
            ident, note = hazard
            # STOPPING IS THE WHOLE DEFENCE, and it is deliberately not a
            # choice of option. The room is already entered by the time this
            # state exists, so what is being avoided is the SECOND hang: the
            # save is poisoned, `continue` re-enters, and the soak's own
            # restart path answers that with `abandon_run` from the main menu,
            # which is EB-1's recorded recovery. Posting a verb here would be
            # guessing at a screen whose frozen capture had no options on it.
            raise Defect("hazard_event",
                         f"'{ident}' is on the harness's hazard register and "
                         f"will not be driven. {note}", state)
        if state.get("state_type") == "overlay":
            raise Defect("overlay_softlock",
                         "state_type 'overlay' is the bridge's catch-all for a "
                         "screen it cannot drive; no verb is accepted here",
                         state)
        if self.actions >= MAX_ACTIONS_PER_RUN:
            raise Defect("action_ceiling",
                         f"{MAX_ACTIONS_PER_RUN} actions posted without "
                         f"reaching game_over", state)
        if time.time() - self.started > RUN_TIMEOUT_S:
            raise Defect("run_timeout",
                         f"run exceeded {RUN_TIMEOUT_S:.0f}s of wall clock",
                         state)
        fp = self._fingerprint(state)
        self._fingerprints.append(fp)
        recent = self._fingerprints[-NO_PROGRESS_ACTIONS:]
        # A STALL IS A SMALL CYCLE, NOT ONLY A FROZEN FRAME, and the fourth
        # validation soak proved it: the shop arm bought a card-removal service,
        # the remove screen was declined and cancelled, and the run bounced
        # shop -> card_select -> shop forever. Two distinct fingerprints, so a
        # `len(set(...)) == 1` test never fired and the run would have spun to
        # the action ceiling three hours later.
        #
        # The bar is "at most NO_PROGRESS_CYCLE distinct states across a full
        # window". Real play cannot do that: the fingerprint carries floor,
        # round, HP, hand size and the enemy HP pool, and one of those moves on
        # essentially every action that accomplishes anything.
        if (len(recent) == NO_PROGRESS_ACTIONS
                and len(set(recent)) <= NO_PROGRESS_CYCLE):
            distinct = sorted(set(recent))
            raise Defect("no_progress",
                         f"{len(distinct)} distinct state fingerprint(s) across "
                         f"{NO_PROGRESS_ACTIONS} posted actions "
                         f"({'cycle' if len(distinct) > 1 else 'frozen'}): "
                         + " <-> ".join(distinct), state)

    # -- acting -----------------------------------------------------------
    def post(self, state: dict[str, Any], action: dict[str, Any],
             decision: policy_v1.Decision | None = None,
             mechanical: bool = False) -> dict[str, Any]:
        names = naming.describe(state, action)
        before = dict(state)
        result = _wire().post(**action)
        self.actions += 1
        rec = {
            "record": "decision", "i": self.actions,
            "state_type": state.get("state_type"),
            "act": (state.get("run") or {}).get("act"),
            "floor": (state.get("run") or {}).get("floor"),
            "round": (state.get("battle") or {}).get("round"),
            "hp": (state.get("player") or {}).get("hp"),
            "action": action,
            "names": names,                       # revision #7, on every row
            "hand": naming.hand_names(state),
            "mechanical": mechanical,
            "status": result.get("status"),
            "message": result.get("message") or result.get("error"),
        }
        if decision is not None:
            rec["policy"] = decision.as_log()
        self.emit(rec)
        # A PLAY THE GAME REFUSED IS NOT OFFERED AGAIN THIS TURN. Without this
        # the policy re-picks its highest-scoring card, the bridge rejects it
        # for a reason tier0 cannot see, and the run bounces until the
        # watchdog stops it -- which is how an Act 1 boss ended a run at 379
        # actions with "Card 'Stage Presence' cannot be played".
        if (result.get("status") == "error"
                and action.get("action") == "play_card"
                and names.get("card_id")):
            self.memo.rejected.add(
                (self.memo.turn_key(state), str(names["card_id"])))
        time.sleep(_soak().SETTLE_S)
        after = _wire().get_state()
        deckwatch.record(after)
        self._observe(before, after, names, action)
        return after

    # -- telemetry --------------------------------------------------------
    def _observe(self, before: dict, after: dict, names: dict,
                 action: dict) -> None:
        st_b, st_a = before.get("state_type"), after.get("state_type")
        pb = before.get("player") or {}
        pa = after.get("player") or {}

        if st_a in COMBAT and (self.fight is None
                               or self.fight.floor != (after.get("run") or {}).get("floor")):
            self._open_fight(after)
        if self.fight is None:
            return

        # END-OF-TURN BLOCK, not turn-opening block. The trajectory samples
        # block at the top of the player's turn, which is whatever SURVIVED the
        # enemy's -- a different quantity wearing the same word, and the wrong
        # one for an output curve.
        if st_b in COMBAT and action.get("action") == "end_turn":
            self.fight.block_at_turn_end.append(
                [(before.get("battle") or {}).get("round"),
                 int((pb or {}).get("block", 0) or 0)])

        if st_b in COMBAT and st_a in COMBAT:
            dealt = _enemy_pool(before) - _enemy_pool(after)
            if dealt > 0 and action.get("action") in ("play_card", "use_potion"):
                src = (names.get("card_name") or names.get("potion_name")
                       or action.get("action"))
                self.fight.damage_by_source[src] = \
                    self.fight.damage_by_source.get(src, 0.0) + dealt
            lost = int(pb.get("hp", 0)) - int(pa.get("hp", 0))
            if lost > 0:
                self.fight.damage_taken += lost
            rb = (before.get("battle") or {}).get("round")
            ra = (after.get("battle") or {}).get("round")
            if ra != rb and ra is not None:
                self._open_turn(after)

        # A PLAY IS RECORDED ON THE STATE IT WAS MADE FROM, never on where the
        # game went next (S7 family A, R101). This block used to live inside
        # the `st_a in COMBAT` arm above, which silently keyed the counter on
        # the AFTER-state: a play that opened a mid-fight overlay or ended the
        # fight was posted, answered `ok`, and then never written down. It cost
        # 707 Ethereal Spotlights -- Furina's starter relic grants one every
        # turn and playing it opens the Center Stage / Guest Cast `card_select`
        # -- plus exactly one play per fight, whichever card landed the killing
        # blow. Damage attribution stays inside the arm above on purpose: a
        # pool drop cannot be read across a screen change, and the enemy pool
        # is the honest damage curve anyway.
        if st_b in COMBAT:
            rnd_b = (before.get("battle") or {}).get("round")
            if action.get("action") == "play_card" and names.get("card_name"):
                self.fight.cards_played.append([rnd_b, names["card_name"]])
            if action.get("action") == "use_potion" and names.get("potion_name"):
                self.fight.potions_used.append([rnd_b, names["potion_name"]])

        # P1.5 item 3: THE SELECTOR CHANNEL, which the fight record was blind
        # to. Furina's Ethereal Spotlight opens a `card_select` every turn and
        # the Center Stage / Guest Cast answer is the whole of that turn's
        # Fanfare posture -- probe B3 (R103(b)) and family B's turn-1 gap both
        # stall on exactly this. It is recorded on the state it was made from,
        # for the same reason `cards_played` is (S7 family A, R101): the screen
        # a selector closes into is not where the choice happened.
        #
        # Recorded whether or not the fight is the reason the screen is up --
        # a selector that opens mid-fight belongs to the fight, and MID_FIGHT
        # is the set that already says so.
        if self.fight is not None and st_b in SELECTOR_SCREENS:
            self.fight.selectors.append(self._selector_row(before, action, names))

        if st_b in COMBAT and st_a not in COMBAT and st_a not in MID_FIGHT:
            self._close_fight(after, "survived")

    def _selector_row(self, before: dict, action: dict, names: dict) -> list:
        """One selector choice, with the list it was chosen from.

        The ROUND comes from the fight's own turn counter rather than from
        `battle.round`: a selector screen is an overlay, and the state the
        bridge builds for it carries no `battle` block at all. `self.fight.turns`
        is the highest round this fight has opened, which is the round the
        overlay is standing on.
        """
        assert self.fight is not None
        blob = before.get(str(before.get("state_type"))) or {}
        offered = blob.get("cards")
        if not isinstance(offered, list):
            offered = blob.get("bundles") if isinstance(blob, dict) else None
        offered_names = [
            (o.get("name") if isinstance(o, dict) else None) or ""
            for o in (offered or [])
        ]
        idx = action.get("index", action.get("card_index"))
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            idx = -1
        # LOWERCASED, and it is not cosmetic. `naming.describe` lowercases the
        # screen type and this fallback reads it raw, so the SAME screen
        # reached by two verbs was writing `NCombatPileCardSelectScreen` on one
        # row and `ncombatpilecardselectscreen` on the next -- two spellings of
        # one screen in a channel whose whole job is to be compared.
        return [
            self.fight.turns,
            str(names.get("screen_type")
                or (blob.get("screen_type") if isinstance(blob, dict) else "")
                or before.get("state_type") or "").lower(),
            idx,
            names.get("card_name") or "",
            offered_names,
        ]

    def _open_fight(self, state: dict) -> None:
        from understudy import adapter
        if self.fight is not None:
            self._close_fight(state, "superseded")
        p = state.get("player") or {}
        run = state.get("run") or {}
        self.fight = FightTelemetry(
            act=int(run.get("act", 0) or 0), floor=int(run.get("floor", 0) or 0),
            kind=str(state.get("state_type")),
            enemies=[{"name": e.get("name"), "max_hp": e.get("max_hp")}
                     for e in adapter.enemy_blobs(state)],
            hp_start=int(p.get("hp", 0)), max_hp=int(p.get("max_hp", 1)),
            intent=self.commit or "")
        self._open_turn(state)

    def _open_turn(self, state: dict) -> None:
        if self.fight is None:
            return
        p = state.get("player") or {}
        rnd = (state.get("battle") or {}).get("round")
        dmg, n = _telegraphed(state)
        self.fight.turns = max(self.fight.turns, int(rnd or 0))
        self.fight.hp_trajectory.append([rnd, p.get("hp"), p.get("block", 0)])
        self.fight.incoming_by_turn.append([rnd, dmg, n])
        # THE POOL IS THE HONEST OUTPUT CURVE. `damage_by_source` credits the
        # play the harness happened to read next and under-counts everything
        # that resolves off a play (salon ticks, auras, bombs); the enemy pool's
        # own drop between two turn openings cannot.
        self.fight.enemy_pool_by_turn.append([rnd, _enemy_pool(state)])
        self.fight.meters_by_turn.append([rnd] + _meters(state))

    def _close_fight(self, state: dict, outcome: str) -> None:
        if self.fight is None:
            return
        p = state.get("player") or {}
        self.fight.hp_end = int(p.get("hp", self.fight.hp_start))
        self.fight.outcome = outcome
        self.fights.append(self.fight)
        self.emit(self.fight.as_record())
        self.fight = None

    # -- the run ----------------------------------------------------------
    def run(self) -> dict:
        # EB-117: `character` here is the READ-BACK identity and it is null at
        # this point on purpose -- nothing has embarked yet, so there is no
        # character to name. The request is recorded beside it under its own
        # key, and `character_verified` (emitted the moment the wire answers)
        # fills the real one in. This record stays FIRST in the log because
        # the run_begin / defect / run_end triple is what `report.py` reads
        # and `test_track_o_s09` pins that order for a run that never
        # embarked; that is exactly the run whose character is unknowable.
        self.emit({"record": "run_begin", "character": None,
                   "character_requested": self.character,
                   "policy": self.pol.POLICY_VERSION,
                   # The arm, recorded per run for the same reason the dials
                   # are: a log has to stay self-describing when the flag moves.
                   "commit": self.commit,
                   "dials": {"BLOCK_MATTERS_FRACTION":
                             self.pol.BLOCK_MATTERS_FRACTION,
                             "COMPANION_SHARE_FOR_GUEST_CAST":
                             self.pol.COMPANION_SHARE_FOR_GUEST_CAST,
                             "TIME_SCALE": TIME_SCALE}})
        outcome, detail = "unknown", ""
        try:
            state = self._to_main_menu()
            state = self._embark(state)
            # EB-117: BEFORE the seed read-back, for the same reason the seed
            # read-back exists at all. A soak flying the wrong character is
            # unrecoverable after the fact -- the numbers are somebody else's
            # and nothing in the log says so.
            state = self._verify_character(state)
            # EB-210: THE READ-BACK CAN BE ANOTHER LANE'S. It is a FILE
            # read on the mod's side, and the file resolution ignored the
            # per-lane APPDATA -- so a two-lane round filed `seed_not_honoured`
            # against a game that had honoured its seed exactly. It is a
            # defect of its own now, with its own name, because the two need
            # different answers: one is the game refusing a seed, the other is
            # this harness reading the wrong game's save.
            try:
                self.seed = _wire().current_seed()
            except _wire().LaneCrossed as crossed:
                raise Defect("seed_read_back_crossed", str(crossed),
                             self._last_state or {}) from crossed
            self.emit({"record": "seed_read_back", "seed": self.seed,
                       "chosen": self.chosen_seed,
                       "honoured": (None if not self.chosen_seed
                                    else self.seed == self.chosen_seed),
                       "note": ("chosen; P1.5 arm" if self.chosen_seed
                                else "game-generated; R95 read-back arm")})
            # THE READ-BACK IS THE VERIFICATION, and it is a defect rather than
            # a warning. A chosen-seed soak whose runs quietly rolled their own
            # seeds is the exact failure that a build-vs-build comparison
            # cannot survive and cannot detect afterwards -- both builds would
            # simply be measured on different runs. Stopping here is cheap;
            # discovering it in the numbers is not.
            if self.chosen_seed and self.seed != self.chosen_seed:
                raise Defect(
                    "seed_not_honoured",
                    f"asked for seed {self.chosen_seed!r}, the run reads back "
                    f"{self.seed!r}", self._last_state or {})
            outcome, detail = self._drive(state)
        except Defect as d:
            self.file_defect(d.kind, d.detail, d.state)
            outcome, detail = "defect", f"{d.kind}: {d.detail}"
        except _wire().BridgeError as e:
            # THE GRACE PERIOD IS THE WHOLE POINT (see `Session.died`): asked
            # instantly, a game that is crashing right now still reads alive,
            # and the build defect gets filed under a harness-side kind.
            extra: dict = {}
            if self.session.died():
                kind = "process_died"
                detail_ = f"{e} [exit code {self.session.exit_code}]"
            else:
                # ALIVE AND SILENT IS TWO DIFFERENT FAILURES, and until EB-1
                # they shared one name. `bridge_unreachable` is harness-side:
                # filing a spinning game under it makes the instrument blame
                # its own wire for a build defect it has just caught. So the
                # process is asked, from outside, whether it is spinning.
                verdict = self._diagnose_spin()
                kind = (hangwatch.DEFECT_KIND if verdict.hung
                        else "bridge_unreachable")
                detail_ = f"{e} -- {verdict.reason}"
                extra = {"hangwatch": verdict.evidence,
                         "hangwatch_signals": list(verdict.signals)}
                if verdict.hung:
                    extra["teardown"] = self.session.halt_spin(
                        f"{hangwatch.DEFECT_KIND} at run {self.run_index}")
            self.file_defect(kind, detail_, self._last_state or {}, extra)
            outcome, detail = "defect", f"{kind}: {detail_}"
        except Exception as e:                               # noqa: BLE001
            # The harness itself fell over. That is a defect record like any
            # other -- the alternative is an exception that escapes `soak()`
            # and skips the teardown, which is how a game directory keeps a
            # mod it was promised it would not keep.
            self.file_defect("harness_exception",
                             f"{type(e).__name__}: {e}", self._last_state or {})
            outcome, detail = "defect", f"harness_exception: {e}"
        finally:
            if self.fight is not None:
                self._close_fight(self._last_state or {}, "interrupted")

        summary = {
            "record": "run_end", "outcome": outcome, "detail": detail,
            # EB-117: the READ-BACK identity, `None` for a run that never got
            # far enough to be asked. Never the requested string.
            "character": self.character_actual,
            "character_requested": self.character,
            "seed": self.seed, "run": self.run_index,
            "actions": self.actions,
            "wall_s": round(time.time() - self.started, 1),
            "fights": len(self.fights),
            "final_act": self.fights[-1].act if self.fights else None,
            "final_floor": self.fights[-1].floor if self.fights else None,
            "defects": len(self.defects),
            "forced_defaults": self._forced_defaults,
            "log": str(self.log),
        }
        if self.sampler is not None:
            summary["p2_capture"] = self.sampler.summary()
        self.emit(summary)
        return summary

    def _diagnose_spin(self):
        """Ask the OS whether the alive-but-silent game is spinning (EB-1).

        Wrapped rather than called inline for one reason: a watchdog that can
        raise is a watchdog that turns a classified failure back into
        `harness_exception`. Anything this cannot answer reads as "not a spin",
        which routes the run to `bridge_unreachable` -- the answer the file
        gave before this leg existed.
        """
        try:
            # PER-LANE: this session's own log and this session's own pid.
            # Both fall back to the machine-wide reads a single-lane soak
            # always used, so a session with no instance still diagnoses.
            inst = getattr(self.session, "instance", None)
            return hangwatch.diagnose(
                GAME_EXE, alive=True, wire_dead=True,
                log_path=(inst.log_path() if inst is not None else None),
                pid=getattr(self.session, "pid", None))
        except Exception as exc:                             # noqa: BLE001
            return hangwatch.Verdict(
                False, f"the spin probe itself failed ({type(exc).__name__}: "
                       f"{exc}); falling back to `bridge_unreachable`")

    def _drive(self, state: dict) -> tuple[str, str]:
        while True:
            state = self._settle_transient(state)
            self._last_state = state
            self._check(state)
            st = str(state.get("state_type"))

            # A BOUNDED RUN, ADDED BY P1.5 FOR ITS OWN ACCEPTANCE. Comparing
            # two recordings of one seed needs a run that ENDS at a stated
            # point in both, and "when the bot happened to die" is not one.
            # This is a clean stop, not a defect: the fight that is open has
            # already closed by the time the count reaches the bound, so the
            # records the comparison reads are complete records.
            #
            # OFF BY DEFAULT (`None`), so a soak is a soak.
            if (self.max_fights is not None
                    and len(self.fights) >= self.max_fights
                    and self.fight is None):
                self.emit({"record": "bounded_stop",
                           "fights": len(self.fights),
                           "max_fights": self.max_fights})
                return "bounded", f"stopped after {len(self.fights)} fight(s)"

            if st == "game_over":
                won = _game_over_won(state)
                self._close_fight(state, "died" if not won else "won")
                self.emit({"record": "game_over", "won": won,
                           "detail": _trim_state(state)})
                return ("won" if won else "died"), json.dumps(
                    state.get("game_over") or state.get("message") or "")[:300]

            mech = _mechanical_action(state)
            if mech is not None:
                # A MECHANICAL ACTION THAT CHANGES NOTHING IS NOT MECHANICAL.
                # With a full potion belt, `claim_reward` on a potion returns
                # ok and does nothing -- the reward stays, the screen stays,
                # and the walker re-claims it forever. Repeating the same
                # forced action on an unchanged screen is the tell, and the
                # escape is the verb every one of these screens advertises.
                fp = self._fingerprint(state)
                if (fp, json.dumps(mech, sort_keys=True)) == self._last_mech:
                    self._mech_repeats += 1
                else:
                    self._last_mech = (fp, json.dumps(mech, sort_keys=True))
                    self._mech_repeats = 0
                if self._mech_repeats >= 3:
                    escape = _escape(state)
                    if escape is not None:
                        self._forced_defaults += 1
                        self.emit({"record": "forced_default",
                                   "state_type": st,
                                   "why": f"{mech} repeated with no state "
                                          f"change; taking the screen's exit",
                                   "action": escape})
                        self._mech_repeats = 0
                        state = self.post(state, escape, mechanical=True)
                        continue
                state = self.post(state, mech, mechanical=True)
                continue

            decision = self.pol.decide(state, self.memo,
                                       commit=self.commit)
            # P2: a TURN OPENING is the first decision of a combat round, so
            # the sample is taken here -- after the policy has answered, so
            # the record carries what policy_v1 actually did rather than a
            # second evaluation that could differ.
            if self.sampler is not None:
                self.sampler.maybe_capture(state, self.memo, decision,
                                           self.seed)
            if not decision.available or decision.action is None:
                fallback = _last_resort(state)
                if fallback is None:
                    raise Defect(
                        "no_action",
                        f"policy_v1 has no action for '{st}' and no mechanical "
                        f"fallback exists: {decision.rationale}", state)
                self._forced_defaults += 1
                self.emit({"record": "forced_default", "state_type": st,
                           "why": decision.rationale, "action": fallback})
                state = self.post(state, fallback, decision, mechanical=True)
                continue
            if decision.notes.get("forced_default"):
                self._forced_defaults += 1
            state = self.post(state, decision.action, decision)
