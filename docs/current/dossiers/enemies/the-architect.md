# The Architect

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Architect` (`MonsterModel`)
- **Kind:** boss (registered as an encounter monster; in practice a scripted epilogue actor)
- **Act:** Epilogue — the victory room entered after the final act
- **Fight class:** `gimmick`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What this encounter actually is

The Architect is not a combat boss. It is the *victory room*: an event
(`TheArchitect`, an `EventModel` with a combat-style layout) whose canonical encounter
spawns exactly one Architect monster on the enemy side, on a custom background, in a room
typed as a Monster room.

The run manager routes here instead of advancing acts: when the player would leave the
last act, the game enters the Architect event room. A room is flagged as "the victory
room" precisely by asking whether its canonical event is this one. Choosing the final
dialogue option (`PROCEED`) ends the run as a win, marks the local player ready on the
act-change synchronizer, and — in the run-manager's win path — force-kills all player
creatures to tear the combat scene down.

So: there is no combat loop, no card play, no turn structure the player participates in
here. Everything below describes a cutscene wearing a fight's clothes.

## 2. Intent pattern / AI

Deliberately inert. The move state machine is a single state named `NOTHING`:

| Field | Behavior |
| --- | --- |
| Move count | 1 |
| Move action | no-op (completes immediately, targets ignored) |
| Intent shown | Hidden intent (no icon, no hover tip, no telegraph text) |
| Follow-up | itself — the state loops to itself forever |
| Initial state | the same single state |

The state machine's normal job (roll a move from the eligible pool, log it, advance to the
follow-up) degenerates to "stay in `NOTHING`". The Architect can never attack, block,
buff, or apply a power through the monster-move system. Every offensive beat it appears
to land is played by the event script as pure VFX (see §4).

## 3. HP, damage, and block numbers

| Stat | Value | Note |
| --- | --- | --- |
| Initial HP (min) | 9999 | min == max, so no roll |
| Initial HP (max) | 9999 | flat sentinel "unkillable" value |
| Block | none | no block move exists |
| Damage dealt to player | 0 real damage | the Architect's "attack" is animation + VFX only |
| Health bar | not suppressed by the model | it does not override the default visible-health-bar flag; whatever the victory-room scene does with it is presentation-side |

The Architect has no move that deals damage, so its 9999 HP is a display/safety number
rather than a health pool the player is meant to chew through.

## 4. The gimmick: your score is the damage number

The one genuinely mechanical thing in the room is that **the run's final score is
rendered as damage dealt to the Architect.**

On room entry the event refreshes global stats, grabs the single enemy-side creature as
"the Architect", and computes the final score for the run *as a win*. That score integer
is then the total the player's scripted attack sequence displays.

Score is assembled from (all values from the score utility):

| Component | Formula |
| --- | --- |
| Floors climbed | for each act *i* (1-indexed), rooms-in-act × 10 × *i* — later acts are worth more per floor |
| Gold gained | total gold gained across all players ÷ (100 × player count) |
| Elites killed | 50 each (the final room is excluded if it was an elite) |
| Bosses slain | 100 each (on a loss, the room you died in doesn't count; here `won: true` is passed) |
| **Ascension multiplier** | the summed total is multiplied by (1 + ascension × 0.1), then truncated |

The player-attack animation splits that total into one damage popup per character-specific
attack VFX, using a deliberately lopsided divider: exactly one randomly chosen part is
weighted 2.0–3.0×, exactly one other part is weighted 0.1–0.5×, and the rest are weighted
0.7–1.3×. Weights are normalized, each part floors at 1, and the last part absorbs the
remainder so the popups always sum to the score exactly. The result is a hit sequence with
one obvious "big number" and one obvious "chip" — the wild split is cosmetic drama, not
balance.

Per-character hit counts (the number of VFX entries = the number of damage popups):

| Character | Hits |
| --- | --- |
| Ironclad | 5 |
| Defect | 5 |
| Regent | 5 |
| Silent | 4 |
| Necrobinder | 4 |
| Deprived / RandomCharacter | 0 (empty VFX list — the attack sequence is skipped entirely) |

The VFX list is shuffled per run, so hit order varies. The final hit triggers a strong
screen shake; the others a weak one. The Architect's own retaliation is a single attack
animation plus a lightning VFX and a fire burst on the player creature — again, no damage
application.

## 5. Dialogue state machine (the actual "turn structure")

The Architect's behavior is a dialogue walk, not a move cycle:

1. On entry, the Architect's spine head track plays a looping "reading" animation.
2. A dialogue is picked at random from the valid set for the current character (see below),
   and the initial option list is cleared so the player can't skip past the intro beats.
3. Line 0 plays: if the dialogue declares start-attackers, a beat of delay, then the player's
   scripted attack sequence, then the Architect stops reading (head goes to a normal track),
   then the Architect's scripted counter-attack if declared.
4. Each line shows a speech bubble (dark gray for the Architect, the character's own bubble
   color for the player) and offers one button — "Respond" when the Architect just spoke,
   "Continue" when the player did, or a per-line override.
5. The last line offers `PROCEED`, which runs the end-attacker sequence (player attack, then
   Architect attack) and wins the run.

Dialogue selection is by **win count, not by ascension or act**. The chosen bucket is the
character's total wins (`VisitIndex` match); the global win count across all characters is
also passed and would select a first-visit-ever dialogue, except the Architect explicitly
has none — the docs on the dialogue set name the Architect as the example of an ancient
with no first-visit dialogue. Character-agnostic dialogues are disallowed for the Architect
(the set is empty and any-character dialogues are switched off at the call site), so an
unlisted character or an out-of-range win count falls through to an empty repeating pool and
the room degrades gracefully to a bare `PROCEED`.

Authored dialogue coverage, with who swings:

| Character | Dialogues (by win index) | Attack pattern |
| --- | --- | --- |
| Ironclad | 3 (wins 0,1,2) | end: both (player hits, Architect hits back) |
| Defect | 3 (wins 0,1,2) | end: both |
| Regent | 3 (wins 0,1,2) | end: both |
| Necrobinder | 4 (wins 0–3) | end: both |
| Silent | 4 (wins 0–3) | start: player attacks; end: both at wins 0–1, **Architect only** at wins 2–3 |

The Silent is the only character who opens the scene mid-swing, and the only one whose
later-win dialogues end with the Architect getting the last word unanswered. That is a
narrative escalation encoded in the attacker enum, not a difficulty change.

## 6. Scaling

- **By act:** none. The room only exists past the final act. Act count affects the scene
  only indirectly, through the floor component of the score (later acts weight more per room).
- **By ascension:** the *displayed damage* scales — the whole score total is multiplied by
  (1 + ascension × 0.1). The Architect's HP, moves, and threat do not change. Higher
  ascension makes the numbers bigger, nothing else.
- **By wins:** dialogue branch selection only (see §5).

## 7. Multiplayer / seat count

- The encounter always generates exactly **one** Architect regardless of seat count. No
  per-seat HP or damage scaling exists.
- Nearly every animation and dialogue path is gated on "is this my local player", so each
  seat plays its own dialogue, against its own character's VFX set, with its own score.
- The gold component of score is divided by player count, so a co-op party's gold does not
  inflate everyone's number proportionally to headcount.
- On confirming `PROCEED` in a multi-seat run, the local player raises a "waiting for other
  players" overlay and marks itself ready on the act-change synchronizer. The overlay is
  dismissed by an explicit victory trigger the run manager calls when the run actually ends.
  Net effect: the fastest reader waits on the slowest; the run wins as a group.

## 8. Proposed fight class: `gimmick`

Per-turn, this encounter demands **nothing** of the player: no damage to mitigate, no
intent to read (the intent is literally hidden), no clock, no resource decision. The only
input is pressing a button once per dialogue line. Its entire mechanical content is the
one-way trick of converting the run's score into a damage-number spectacle, with an
ascension multiplier and a randomized lopsided split that exist purely to make the payoff
read well. Classifying it as spike or attrition would inject a phantom demand curve into
Track B for a room that applies zero pressure; `gimmick` is the only honest bucket, and
downstream consumers should treat it as a zero-demand outlier rather than a difficulty
data point.
