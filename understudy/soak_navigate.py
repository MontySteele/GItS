"""Menu to embark to the first fight, and WHO actually embarked.

Cut out of `soak.py` by `EB-180`. The five methods below were `RunDriver`'s
and still are: `Navigation` is a mixin `RunDriver` inherits, so
`driver._embark(state)` and `driver._verify_character(state)` are the same
bound methods on the same object, in the same order, with the same words.
The three character comparators were module level in `soak.py` and are
re-exported from it, so `soak.canonical_character(name)` still resolves.
"""
from __future__ import annotations

import time
from typing import Any

from understudy.soak_screens import _first_of, _option_names
from understudy.soak_shape import Defect


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


# ------------------------------------------------- who actually embarked ----
#
# EB-117. `--character` used to be matched case-insensitively against the
# character-select options and a string that matched NOTHING was not an error:
# the pick simply never fired, the driver walked on, the game embarked on
# whatever the screen had highlighted (Ironclad), and the report header printed
# the REQUESTED name. A six-run soak launched with `--character furina` (the id
# is `KLEEMOD-FURINA`) produced a report headed `character furina` whose every
# damage source was an Ironclad card. The operator error is cheap; the silent
# mislabel is the defect.
#
# Two things fix it, and both live below: the select screen is CHECKED before
# the embark, and the character the run actually started with is READ BACK off
# the wire afterwards. The read-back is what gets stamped -- never the request.
#
# The two strings are not the same vocabulary, which is why a comparator is
# needed rather than `==`. The request is a character-select OPTION id
# (`KLEEMOD-FURINA`); the read-back is the wire's own DISPLAY name
# (`player.character`: "Furina", "Klee", "Sangonomiya Kokomi"), the same field
# `harness.render` and `policy_v1._plan_for` read. `tier0.roster` is the
# registry that joins them, asked rather than copied -- a second table here is
# a second thing to forget when slot 4 lands.

_CHARACTER_PREFIX = "kleemod-"


def canonical_character(name: str) -> str:
    """Fold an option id or a display name onto one comparable key.

    Roster members fold onto their registry id (`kokomi`); anything the
    registry does not know -- the base-game characters, a future mod -- folds
    onto its own normalised text, so `IRONCLAD` and `Ironclad` still compare
    equal and nothing is silently claimed to be a roster member.
    """
    key = str(name or "").strip().casefold()
    if key.startswith(_CHARACTER_PREFIX):
        key = key[len(_CHARACTER_PREFIX):]
    key = " ".join(key.replace("-", " ").replace("_", " ").split())
    # The base game's display names carry an article the option id does not:
    # the select screen offers `IRONCLAD`, the run reads back `The Ironclad`.
    # Both are the one character, and the CONTROL round asks by the id.
    if key.startswith("the "):
        key = key[4:]
    if not key:
        return ""
    from tier0 import roster
    for ch in roster.ROSTER:
        if key in (ch.id.casefold(), ch.display.casefold()):
            return ch.id.casefold()
    return key


def character_matches(requested: str, actual: str) -> bool:
    """Did the run start as the character that was asked for?

    An empty side is never a match: "the wire told us nothing" is a failure to
    verify, not a verification, and it is reported as its own defect kind.
    """
    a, b = canonical_character(requested), canonical_character(actual)
    return bool(a) and a == b


def _selectable_characters(options: list[str]) -> list[str]:
    """The character rows on a character-select screen.

    The confirm/embark button and the back link share `options` with the
    characters; a screen offering only those is one that has not finished
    settling, and the pre-embark check declines to judge it rather than
    filing a defect against a frame.
    """
    return [o for o in options
            if o.strip().casefold() not in {"confirm", "embark", "back",
                                            "cancel", "ok"}]


class Navigation:
    """`RunDriver`'s route: main menu, embark, settle, read the name back.

    A mixin rather than a module, because every method here was written
    against `RunDriver`'s own `self` -- `self.post`, `self.file_defect`,
    `self.session`, `self.character`. `EB-180` moved the text, not the
    binding.
    """

    def _to_main_menu(self) -> dict:
        """Reach the main menu, abandoning any resumable run on the way.

        R97/5b: the profile's leftover run may be abandoned freely. The soak
        does not negotiate with a save -- a resumable run on the profile would
        otherwise make `continue` the first option and quietly resume someone
        else's measurement.
        """
        state = _wire().get_state()
        for _ in range(40):
            self._last_state = state
            st = str(state.get("state_type"))
            if st == "game_over":
                state = self.post(state, {"action": "menu_select",
                                          "option": "main_menu"},
                                  mechanical=True)
                continue
            if st != "menu":
                # Mid-run somewhere. Get to the menu the only way the wire
                # offers: there is none, so this is a stop-and-surface.
                raise Defect("unexpected_start_state",
                             f"expected a menu at run start, found '{st}'",
                             state)
            opts = _option_names(state)
            screen = str(state.get("menu_screen") or "")
            if screen == "main" and "abandon_run" in opts:
                state = self.post(state, {"action": "menu_select",
                                          "option": "abandon_run"},
                                  mechanical=True)
                continue
            if screen == "main":
                return state
            pick = _first_of(opts, ("back", "main_menu", "ignore", "confirm",
                                    "yes", "ok"))
            if pick is None:
                return state
            state = self.post(state, {"action": "menu_select", "option": pick},
                              mechanical=True)
        raise Defect("menu_loop",
                     "could not reach the main menu in 40 menu actions",
                     state)

    def _embark(self, state: dict) -> dict:
        """main -> singleplayer -> standard -> character -> confirm.

        NO `seed` PARAMETER IS PASSED ON THIS PATH, AND THAT IS STILL TRUE ON
        THE CHOSEN-SEED ARM. Upstream's `menu_select(seed=...)` returns "Seeded
        embark is not supported for standard singleplayer from this API",
        behind a `charSelect.Lobby == null` guard that the decompile
        contradicts -- `InitializeSingleplayer` builds a lobby and `SetSeed`
        accepts singleplayer. P1.5 did not rewrite that arm, because a fork
        that rewrites an upstream refusal owns the refusal forever. It fires
        its own endpoint instead, below, between the character pick and the
        confirm.

        So there are two arms here and one embark verb:

          chosen_seed is None  -- R95's read-back arm, byte-for-byte unchanged
          chosen_seed is set   -- P1.5: `POST /api/v1/gits/seed` before the
                                  confirm, verified by the read-back in `run`
        """
        picks = 0
        for _ in range(30):
            self._last_state = state
            st = str(state.get("state_type"))
            if st != "menu":
                return state
            screen = str(state.get("menu_screen") or "")
            opts = _option_names(state)
            if screen == "character_select":
                # ORDER MATTERS AND IT COST A RUN TO LEARN. `KLEEMOD-FURINA`
                # stays in `options` after it has been chosen -- the verb is
                # idempotent and the bridge answers "Selected Furina. Use
                # 'confirm' to embark." every time. A loop that prefers the
                # character over the confirm therefore re-selects her forever
                # and never embarks, which is the `embark_loop` defect the
                # first validation soak filed.
                #
                # So: pick the character exactly once, then take `confirm`.
                # The confirm button only appears in `options` while it is
                # enabled (`_option_names` drops disabled entries), so it is
                # absent until a character is chosen and cannot fire early.
                #
                # EB-117: CHECK THE SCREEN BEFORE TOUCHING IT. A `--character`
                # that matches no option used to fall straight through to the
                # confirm below and embark on whatever was highlighted. The
                # options are right here, so the answer is knowable before the
                # run exists rather than six runs later from a damage table.
                # Guarded on there being characters to check: a screen showing
                # only the confirm/back chrome is one still settling, and the
                # bounded retry below is the answer to that, not a defect.
                offered = _selectable_characters(opts)
                if offered and self.character.lower() not in [o.lower()
                                                              for o in opts]:
                    raise Defect(
                        "character_not_offered",
                        f"character select offers no {self.character!r}; "
                        f"the options are {offered}. Embarking anyway would "
                        f"soak whatever the screen has highlighted and label "
                        f"it {self.character!r}", state)
                if picks == 0 and self.character.lower() in [o.lower()
                                                             for o in opts]:
                    picks += 1
                    state = self.post(state,
                                      {"action": "menu_select",
                                       "option": self.character},
                                      mechanical=True)
                    continue
                pick = _first_of(opts, ("confirm", "embark"))
                if pick is not None and self.chosen_seed:
                    # P1.5 item 1, AND THE MOMENT IS THE WHOLE TRICK. The seed
                    # goes on HERE -- character select is up, a character is
                    # chosen, the embark has not fired. Earlier is wasted:
                    # `NCharacterSelectScreen.AfterInitialized()` clears the
                    # debug override as this screen opens. Later does not
                    # exist: the run is generated inside the confirm.
                    #
                    # This is a separate endpoint rather than upstream's
                    # `menu_select(seed=...)` because that arm refuses
                    # singleplayer on a guard the decompile contradicts; see
                    # vendor/STS2_MCP/gits/GitsSeed.cs.
                    self.session.note_seed_channel()
                    # EB-15: WHICH ROUTE FIRED IS NOT ENOUGH TO DIAGNOSE WHY.
                    # Three live runs took `debug_override` and the record
                    # could not say whether the character-select screen was
                    # missed or the lobby on it was null, because `route` was
                    # the only key kept off a report that answers both. The
                    # endpoint's own precondition -- `charSelect != null` and
                    # `charSelect.Lobby != null` (vendor/STS2_MCP/gits/
                    # GitsSeed.cs, GitsSeedApply) -- is read once BEFORE the
                    # POST and once from the POST's own report, so a fourth
                    # observation says which half of the guard failed.
                    try:
                        before = _wire().get_seed()
                    except _wire().BridgeError as exc:
                        before = {"error": str(exc)}
                    report = _wire().set_seed(self.chosen_seed)
                    # THE CANONICAL FORM COMES BACK FROM THE GAME, and it is
                    # taken rather than computed. `SeedHelper.CanonicalizeSeed`
                    # upper-cases, maps 'O'->'0' and 'I'->'1', and the run
                    # reads back the CANONICAL string -- so a harness that
                    # compared the read-back against what a person typed would
                    # file `seed_not_honoured` against a seed the game honoured
                    # exactly. Retyping the mapping here would be a second copy
                    # of somebody else's rule; asking for it is one copy.
                    requested = self.chosen_seed
                    self.chosen_seed = report.get("chosen") or self.chosen_seed
                    self.emit({"record": "seed_chosen",
                               "requested": requested,
                               "seed": self.chosen_seed,
                               "route": report.get("route"),
                               "status": report.get("status"),
                               "message": report.get("message"),
                               # EB-15 diagnosis keys. Adding keys to a log
                               # record is free; these are read, not driven on.
                               "on_char_select": report.get("on_char_select"),
                               "lobby_seed": report.get("lobby_seed"),
                               "debug_override": report.get("debug_override"),
                               "before_on_char_select":
                                   before.get("on_char_select"),
                               "before_lobby_seed": before.get("lobby_seed")})
                if pick is None:
                    if picks < 3 and self.character.lower() in [o.lower()
                                                                for o in opts]:
                        # The selection did not take. Retry a bounded number of
                        # times rather than spinning; three is enough to ride
                        # out a frame the screen was still settling on.
                        picks += 1
                        state = self.post(state,
                                          {"action": "menu_select",
                                           "option": self.character},
                                          mechanical=True)
                        continue
                    raise Defect("no_embark",
                                 f"character select offers no confirm/embark "
                                 f"after {picks} selection(s); options were "
                                 f"{opts}", state)
                self.post(state, {"action": "menu_select", "option": pick},
                          mechanical=True)
                # EMBARKING IS NOT INSTANT, AND THE SECOND VALIDATION SOAK
                # PROVED IT. `confirm` returns "Embarking on run" and the very
                # next GET still reads `character_select`, because the run is
                # generated over several frames. A driver that trusts the
                # post-action read re-selects the character and files
                # `no_embark` on a run that in fact started. So this is the one
                # place with a transition wait rather than a settle.
                state = self._await_leaving_menu()
                continue
            pick = _first_of(opts, ("standard", "singleplayer", "confirm",
                                    "ignore", "ok"))
            if pick is None:
                raise Defect("no_embark_path",
                             f"menu_screen '{screen}' offers none of the "
                             f"embark options; saw {opts}", state)
            state = self.post(state, {"action": "menu_select", "option": pick},
                              mechanical=True)
        raise Defect("embark_loop", "could not embark in 30 menu actions", state)

    def _settle_transient(self, state: dict[str, Any],
                          tries: int = 60,
                          delay: float = 0.5) -> dict[str, Any]:
        """Ride out a state that is a MOMENT, not a screen.

        Two shapes qualify, and they are the same moment wearing two faces:

          `state_type: "unknown"`  -- the bridge documents it as "unrecognized
            room or null state", and the instant after embarking is exactly
            that: act 1, floor 0, the run generated and no room entered yet.
            The third validation soak embarked cleanly and then filed
            `no_action` against it within a second, because the driver treated
            a transition as a screen it could not drive.

          NO `state_type` KEY AT ALL (EB-11 / understudy defect 13) -- the same
            transition read one frame earlier, before `StateBuilder` has a room
            to name. `str(state.get("state_type"))` renders that as the string
            `"None"`, which matched neither the `unknown` test above nor any
            screen below it, so the missing key fell all the way through to
            `policy_v1` declining and `_last_resort` returning None: a run
            ended by `no_action` against a state that was never a screen.
            Riding it out is the same answer the `unknown` face already gets.

        A settle that never lands is NOT swallowed. `unknown` is handed back
        for the no-progress watchdog to catch with a fingerprint history behind
        it, which is a better record than an instant refusal. A missing
        `state_type` cannot be caught that way -- nothing downstream can post an
        action against it, so the watchdog never gets a second sample -- and it
        is therefore filed here, under its own kind, with the settle it was
        given stated. Loud, classified, and not disguised as `no_action`.
        """
        st = state.get("state_type")
        if st is not None and str(st) != "unknown":
            return state
        waited = 0.0
        for _ in range(tries):
            time.sleep(delay)
            waited += delay
            state = _wire().get_state()
            st = state.get("state_type")
            if st is not None and str(st) != "unknown":
                self.emit({"record": "transient_settled",
                           "waited_s": round(waited, 1),
                           "settled_to": str(st)})
                return state
        if state.get("state_type") is None:
            raise Defect(
                "state_type_missing",
                f"the bridge answered with no `state_type` key for "
                f"{waited:.0f}s ({tries} reads); a state with no screen name "
                f"cannot be driven and no action can be posted against it, so "
                f"the no-progress watchdog would never see a second sample",
                state)
        return state

    def _await_leaving_menu(self, tries: int = 60,
                            delay: float = 0.5) -> dict[str, Any]:
        """Poll until the game is off the menu, or give the menu back.

        Deliberately returns the menu state rather than raising when the wait
        runs out: the caller's loop is the retry, and a wait that raises would
        turn a slow machine into a filed defect.
        """
        state = _wire().get_state()
        for _ in range(tries):
            if str(state.get("state_type")) != "menu":
                return state
            time.sleep(delay)
            state = _wire().get_state()
        return state

    def _verify_character(self, state: dict[str, Any],
                          tries: int = 60,
                          delay: float = 0.5) -> dict[str, Any]:
        """EB-117: read back WHO embarked, and refuse to soak anybody else.

        The wire names the run's character on `player.character` -- the
        display name, the field `harness.render` prints and
        `policy_v1._plan_for` resolves the plan off. It is not there the
        instant the confirm returns (the run is generated over several frames,
        which is the same reason `_await_leaving_menu` exists), so this polls
        for it on the same bound rather than trusting the first read.

        Three outcomes, and two of them are defects:

          match      -- `character_actual` is stamped and the run proceeds
          mismatch   -- `character_mismatch`, harness-side. This is the EB-117
                        run: `--character furina` never matched the option
                        `KLEEMOD-FURINA`, the pick never fired, and the game
                        embarked on whatever was highlighted
          unreadable -- `character_unverified`. NOT waved through: a run whose
                        identity cannot be read cannot be labelled, and an
                        unlabelled soak is the defect this row is about
        """
        for attempt in range(tries):
            who = str(((state.get("player") or {}).get("character")
                       or "")).strip()
            if who:
                if not character_matches(self.character, who):
                    raise Defect(
                        "character_mismatch",
                        f"asked to embark as {self.character!r}, the run "
                        f"reads back {who!r}; every number this run produces "
                        f"belongs to {who!r} and none of it is quotable "
                        f"against {self.character!r}", state)
                self.character_actual = who
                self.emit({"record": "character_verified",
                           "character": who,
                           "character_requested": self.character,
                           "run": self.run_index})
                return state
            # The last pass READS ONLY. Re-fetching after the final check
            # would make the bound `tries` reads plus one wire call whose
            # answer nothing looks at.
            if attempt < tries - 1:
                time.sleep(delay)
                state = _wire().get_state()
        raise Defect(
            "character_unverified",
            f"the run started but the wire never named a character "
            f"(`player.character` empty after {tries} reads); "
            f"{self.character!r} was requested and cannot be confirmed",
            state)
