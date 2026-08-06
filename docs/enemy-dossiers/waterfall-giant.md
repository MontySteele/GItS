# Waterfall Giant

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `WaterfallGiant` (`MonsterModel`)
- **Kind:** boss (sole monster of the `WaterfallGiantBoss` encounter)
- **Act:** Act 1 — Underdocks (act index 0, the alternate first act; first in that act's boss discovery order, ahead of Soul Fysh and Lagavulin Matriarch)
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. Shape of the fight

One boss, alone, on a custom background with the camera pulled out slightly (0.9× scaling).
No adds, no summons, no minion phase. The whole design hangs off a single counter power,
**Steam Eruption**, that the giant stacks on *itself* every single turn and never spends —
until you kill it, at which point the accumulated counter is fired back at the party as one
guaranteed hit and *then* the boss dies for real.

So the fight has two parts that overlap in time rather than in sequence:

1. **The body.** A deterministic 5-move rotation of moderate attacks, one self-heal, and one
   attack that escalates permanently. Nothing here threatens to one-shot anybody.
2. **The bill.** Every move the giant takes — including the ones that do nothing to you —
   raises the size of the terminal blow. The longer the body takes, the bigger the bill.

The player's real decision is therefore not "how do I survive this turn" but "how fast can I
close, and what do I have left in the tank when the bill arrives".

## 2. Intent pattern / move cycle

Fully deterministic. There is no RNG anywhere in this monster's move selection: every state
declares a single follow-up state, so the rotation is a fixed ring.

Opening move (initial state, happens exactly once):

```
PRESSURIZE
```

then the permanent ring:

```
STOMP → RAM → SIPHON → PRESSURE GUN → PRESSURE UP → STOMP → ...
```

Pressurize is never re-entered. The ring is five moves long and repeats forever.

| Move | Intent shown | Effect |
| --- | --- | --- |
| Pressurize | buff | No damage. Puts a large lump of Steam Eruption on itself. |
| Stomp | attack + debuff + buff | Damage, **1 Weak** to the players, +3 Steam Eruption |
| Ram | attack + buff | Damage, +3 Steam Eruption |
| Siphon | heal + buff | **Heals itself**, +3 Steam Eruption. Hidden from the bestiary move list (see §7). |
| Pressure Gun | attack + buff | Damage, then **permanently raises its own Pressure Gun damage by 5**, +3 Steam Eruption |
| Pressure Up | attack + buff | Damage, +3 Steam Eruption |

Every move in the ring adds exactly 3 Steam Eruption. Only the opening Pressurize adds a
larger lump. The buff icon on every single intent is that counter ticking up — it is not a
Strength-style multiplier and it never modifies the giant's attacks.

Two states sit outside the ring and are only reachable by dying (see §3): **About To Blow**
(shown as a stun intent) and **Explode** (shown with the special death-blow intent icon and a
live damage number). Explode's follow-up is itself, as a safety loop.

## 3. The gimmick: dying doesn't end it

Steam Eruption is a counter buff on the giant with three unusual properties: it prevents
combat from ending, it prevents its owner from being removed from combat on death, and it
survives its owner's death. When the giant's HP hits zero while it holds any Steam Eruption:

1. Removal is cancelled. A knockout sting plays, the ambient rumble goes to max, the boss
   music parameter jumps to its top intensity tier.
2. Its max and current HP are set to an effectively infinite value and its HP bar switches to
   an **infinite-without-numbers** display. It cannot be damaged, killed, or raced during this
   window; attacks into it are wasted.
3. Its move is force-set to **About To Blow**, which is flagged must-perform-once — the state
   machine cannot skip past it, so the party is guaranteed exactly one clean turn.
4. On the enemy turn, About To Blow resolves: the entire Steam Eruption counter is read off,
   stored as the explosion damage, and the power is removed from the giant. Nothing else
   happens that turn — it is a free turn for the player.
5. The following turn it performs **Explode**: one hit for the stored value against everyone,
   then it kills itself for real.

Consequences worth writing down:

- The explosion number is **visible for one full player turn before it lands**, on the
  death-blow intent. This is a block/heal check with perfect information, not an ambush.
- Instant-kill and forced-removal effects do not dodge it. The giant is explicitly exempted
  from disappearing to Doom-style removal while it still holds the counter, and the power
  refuses to be stripped by its owner's death.
- Overkill damage is irrelevant. The blow's size is set by *how many turns the fight took*,
  not by how you finished it.
- Because the fight cannot end while the power is up, there is no "win before it resolves"
  line at all.

Audio/visual tells are honest here and worth treating as real UI: each move bumps the boss
music intensity parameter and the ambient loop, and the giant's spine rig steps through three
escalating "buildup" tracks as the counter climbs. A player who never reads the buff number
still gets a rising-pressure signal.

## 4. Numbers

Base (Ascension 0, single player). All attacks target **all opponents** (§6).

| Stat | Value |
| --- | --- |
| Initial HP | 240 (min == max — no roll) |
| Stomp | 15 damage + 1 Weak |
| Ram | 10 damage |
| Pressure Gun | 20 damage on first use, **+5 permanently per use** (20 → 25 → 30 → …) |
| Pressure Up | 13 damage |
| Siphon heal | 10 × number of players |
| Pressurize (opening) | +15 Steam Eruption |
| Every other move | +3 Steam Eruption |
| Explosion damage | = total Steam Eruption held at the moment of "death" |

### Turn-by-turn, single player, Ascension 0

| Enemy turn | Move | Damage to player | Pressure banked (running total) |
| --- | --- | --- | --- |
| 1 | Pressurize | 0 | 15 |
| 2 | Stomp | 15 (+Weak 1) | 18 |
| 3 | Ram | 10 | 21 |
| 4 | Siphon | 0 (heals 10) | 24 |
| 5 | Pressure Gun | 20 | 27 |
| 6 | Pressure Up | 13 | 30 |
| 7 | Stomp | 15 (+Weak 1) | 33 |
| 8 | Ram | 10 | 36 |
| 9 | Siphon | 0 (heals 10) | 39 |
| 10 | Pressure Gun | 25 | 42 |
| 11 | Pressure Up | 13 | 45 |
| 12 | Stomp | 15 (+Weak 1) | 48 |
| 13 | Ram | 10 | 51 |
| 14 | Siphon | 0 (heals 10) | 54 |
| 15 | Pressure Gun | 30 | 57 |

Closed form: after N enemy turns the banked explosion is **15 + 3 × (N − 1)**, i.e. exactly
3 damage of future burst per turn you spend. A lap of the ring costs the player 58 damage
(first lap; 63 the second, 68 the third, as the gun climbs) while returning 10 HP to the
giant — so effective HP is 240 plus 10 per lap, roughly 250–270 in practice.

Realistic kill turns land in the 8–14 range, putting the explosion at **36–54** — a number
comparable to two full ring laps of chip damage, delivered in one hit, on a turn where the
player has already spent everything getting the boss down.

## 5. Ascension scaling

Two gates, both flat alternate values rather than modifiers. Nothing else in the monster reacts
to ascension.

| Gate | What changes | Base → gated |
| --- | --- | --- |
| Tough Enemies | Initial HP | 240 → 250 |
| Tough Enemies | Siphon heal (per player) | 10 → 15 |
| Deadly Enemies | Pressurize (opening pressure lump) | 15 → 20 |
| Deadly Enemies | Stomp damage | 15 → 16 |
| Deadly Enemies | Ram damage | 10 → 11 |
| Deadly Enemies | Pressure Up damage | 13 → 14 |
| Deadly Enemies | Pressure Gun base damage | 20 → 23 |

Not scaled at any ascension: the +3-per-move pressure tick, the +5 Pressure Gun escalation, the
Weak amount (1), the move order, and the About-To-Blow free turn.

Net effect of the Deadly gate is subtle but compounding in the right way for this design: it
raises the opening pressure lump by 5 (so the explosion starts a lap and a half ahead) *and*
raises the chip damage by roughly 7%, while the Tough gate adds 10 HP and 50% more per-lap
healing — which lengthens the fight, which enlarges the explosion. At high ascension the two
gates push the same lever from opposite ends.

## 6. Multiplayer / seat count

The giant does not have a bespoke co-op mode, but four ordinary systems interact badly (for
the players) here:

- **HP.** Boss HP is multiplied by seat count and by the act's multiplayer factor. Underdocks
  is act index 0, factor **1.1**. So 240 → **528** at 2 seats, **792** at 3, **1056** at 4
  (250 → 550 / 825 / 1100 with Tough Enemies).
- **Every attack hits every seat.** Monster attacks here are built as "target all opponents",
  so Stomp, Ram, Pressure Gun, Pressure Up — and Explode — each land on every player at full
  printed value. Party-wide damage is not divided.
- **Weak hits every seat.** Stomp's Weak is applied to the whole player list, once per lap.
- **Siphon is explicitly per-seat.** Its heal is multiplied by the player count in the move
  itself: 10 / 20 / 30 / 40 at 1–4 seats (15 / 30 / 45 / 60 with Tough Enemies). This is the
  one number written to scale by hand, and it is the one that most directly lengthens the fight.
- **Steam Eruption does *not* scale in multiplayer.** The counter takes the flat +15/+3, so the
  explosion's per-seat value is unchanged by seat count *directly*. It grows indirectly, and
  hard: 2.2×–4.4× the effective HP means 2.2×–4.4× the turns, and every one of those turns is
  another +3 to a blow that then hits everybody for full. A 4-seat fight that runs 25–30 enemy
  turns detonates for **~90–105 per player**.

Practical co-op consequence: solo, the explosion is a bruise you plan around; at 3–4 seats it is
a party wipe unless the group deliberately banks defense across the guaranteed free turn. Note
that the About-To-Blow turn is a full free round for *every* seat, so a co-op party actually has
more total resources to answer it — the fight is asking for a coordinated, pre-announced defensive
turn rather than more damage.

## 7. Bestiary presentation

The Siphon move is deliberately suppressed from the auto-generated bestiary move list; every
other move (including Explode) shows normally. The self-heal is meant to be discovered in play,
not read in advance — which matters because Siphon is the move that quietly converts a slow
clear into a bigger explosion.

Cosmetic-only details, listed so nobody mistakes them for mechanics: the giant takes magic-type
damage sounds, has no death sound of its own (the explosion borrows the death sfx slot), and
only fades out on death if the pressure buildup never started.

## 8. Proposed fight class: `mixed`

Per turn, the body of this fight demands ordinary attrition management: 10–20 unavoidable
damage on a fixed, fully telegraphed five-move ring, one Weak per lap to blunt your offense, one
self-heal per lap to tax slow clears, and a single attack that grows +5 every lap so the ring's
cost climbs from 58 to 63 to 68. None of that is a spike — no individual hit threatens a healthy
player, and the correct play most turns is simply "block the number and keep hitting". But the
fight simultaneously runs a hidden clock that converts *every* turn, including the ones where the
giant heals or does nothing, into 3 points of guaranteed terminal burst, and that burst arrives
as a single unblockable-by-death, one-turn-telegraphed hit for 36–54 solo and 90+ in co-op.

`attrition` alone would miss the terminal check that actually kills players; `spike` alone would
miss that the spike's size is set entirely by how you played the attrition phase; `gimmick` would
imply a puzzle with a trick answer, and there isn't one — you cannot dodge, deny, or outrace the
explosion, only shrink it by winning faster and survive it with saved defense. Track B should
model this as a flat mid-tier attrition demand curve with a **player-controlled terminal spike
whose magnitude is a linear function of fight length**, plus one guaranteed zero-demand turn
immediately before that spike.
