# Docket — the next Kokomi kit workshop

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status:** DOCKET. Routed, not decided, not scheduled. Zero design authority.
Opened 2026-08-06 (Track R) against the sitting of 2026-08-06
(`docs/sitting-record-predraft-2026-08-06.md`); ruling R111.

The workshop is already queued third in the pool-rework order. This docket
exists so the item below arrives with the session rather than being
rediscovered inside it.

---

## 1. X9 — the charge bank (NOTE, R111)

**Verdict, verbatim:** *"Probably too strong as-is and needs to be parsed
carefully. Review during the next kit workshop."*

**The venue is named by the verdict, so the item is not opened early.** Two
things follow from that and both are constraints, not suggestions:

- Nothing about the charge bank is changed, probed or pre-priced before the
  workshop sits. "Probably too strong" is a reading, not a ruling.
- "Parsed carefully" is the ask. The workshop's job on this item is to take the
  mechanism apart, not to pick a number for it.

**Mechanism, from `review/redteam/exploit-ledger.md` (X9):** Charge is uncapped
and nothing ever spends it; the pulse converts the whole bank every turn, and
the bank is read twice. Representative verified line:
`kokomi_charge_1_kurage_bank_turn1_kill`. Pin:
`tier0/tests/test_s13_exploit_pins.py::test_x9_kokomi_charge_bank_is_spent`.

**Adjacent, already tracked elsewhere — do not re-open here:**
`KURAGE_PULSE_PER_CHARGE` and `burst_max` carry standing flags in
`docs/kokomi-playtest-protocol.md`, and `kurages_oath = 12` joined them on
2026-08-06 (R107, S4 finding F9) with [USER]'s "too strong, first knob back"
disposition. Those are table questions; X9 is a kit question. They will want to
be read together, which is a reason to keep them in their own venues until
someone reads them.

---

## 2. Watch this space — FLAG-1's second question

`docs/dockets/klee-rework.md` §1 carries **FLAG-1**, held: the cost-delta
accumulator's second run-plausible enabler is **Kokomi's `honor_guard`**
(printed 0-cost), and one of the two held questions is whether that note should
also ride **this** docket. Until it is answered, the Kokomi leg is deliberately
not filed here. Recorded so the absence is legible as a held flag rather than
as a gap.
