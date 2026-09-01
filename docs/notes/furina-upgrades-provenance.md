# furina-upgrades.yaml - comment provenance

Long comment blocks that used to sit in `docs/furina-upgrades.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## before aria_of_recompense

```
# Q3 (USER directive 2026-07-24), SHIPPED by EPOCH 2 (2026-07-26). "One Encore
# card should upgrade to Innate, to solve 'I have no Encore, so half my cards
# don't work.'" Q3a proved the pipeline supports it (two shipped precedents now:
# catalytic_conversion+, kurages_oath+); Q3b chose this card over the common-tier
# alternate (curtain_up) because a BASIC is guaranteed in every deck, making the
# fix a campfire decision every run rather than a draft lottery -- the shape of
# the complaint. Q3b/c/d measured it green: +0.4pt, A1 flat, no first-fire
# domination. The directive was then orphaned when its host doc went stale
# (missed-requirements sec.1.5) and never landed. Exactly one copy is in the
# starting deck, so Innate cannot flood an opening hand.
# The encore delta is KEPT: the directive ADDS Innate, it does not trade for it.
# (Contrast kokomi-upgrades `kurages_oath`, where [USER] ruled the upgrade buys
# INNATE ONLY.)
#
# [USER] RULING (2026-07-27, Serenitea Sweep II track E) -- option (a), KEEP AS
# SHIPPED. aria upgrades to 5->8 AND Innate; the encore delta is not traded for
# the Innate. This closes the "no equivalent ruling ever made here" flag above:
# the equivalent ruling is this one, and it went the other way from
# `kurages_oath` on purpose. A basic is guaranteed in every deck, so making it
# a campfire decision is the fix; the Oath is a draft-lottery rare, where
# INNATE-ONLY is the conservative read.
#
# NOTED, NOT ACTED ON: "Encore in the opening hand is strong." A revisit is
# REGISTERED BUT NOT SCHEDULED. If play reads it as too much, the recorded
# candidate shape is the two-card split -- the basic keeps 5->8 with no Innate,
# and a separate exhaust Encore card carries innate-on-upgrade. Recorded here
# so the alternative does not have to be re-derived from scratch, and so a
# future reader can tell "considered and kept" from "never looked at".
```

## lasting_impression

```
                                             # was {fanfare_cap: +2}, and it BOUND to the raise_fanfare_cap op
                                             # sec.5.2 removes -- which is exactly why this was the one card of
                                             # the sixteen that did not land with the rest. The card is now a
                                             # 1-cost Common Exhaust Encore battery with one number on it, so
                                             # the delta moves that number: the Furina Commons convention, ONE
                                             # number bump and ZERO cost reductions, with
                                             # surintendante_chevalmarin {encore: +2} and suffering_for_art
                                             # {encore: +1} as the precedents in this file.
                                             # AN UNBLOCKER, NOT A RICHNESS REPAIR: a later "too empty" verdict
                                             # opens a BODY redesign, never a second design hidden in an upgrade.
```

## before applause_line

```
# COMPENSATION PASS (2026-07-28), the three new common readers. Every delta
# bumps the PRINTED BASE and leaves the 1_per_4 read alone, which is the
# standing grammar for a reader card (applause_line, held_breath,
# thunderous_ovation; dramatic_entrance was one until W2b re-bodied it off the read):
# the rate is the card's identity and the upgrade is not where a rate moves.
```

## blocking_notes

```
                                             # SLOPE, +2 -> +3 Block per Companion played, exactly as the
                                             # ruling worded it. Base 5 unchanged: a rewrite whose point is
                                             # the slope should upgrade the slope, or the card's identity and
                                             # its upgrade pull in different directions.
```

## take_it_from_the_top

```
                                             # DESIGN-HONEST DELTA (R211): the card is about the bar, so the
                                             # upgrade pays off the bar. Before W3's pricing rider this delta
                                             # was invisible on the offer screen -- the card priced 5.0000 on
                                             # both faces -- which is why the ruling took the two together.
```

## take_your_bow

```
                                             # FANFARE REWORK Track D (2026-07-28) proposed an Encore rider and
                                             # argued AGAINST a second bow. OVERRIDDEN at the R130 sitting
                                             # (2026-08-07): the upgrade IS the second bow. The base was too
                                             # weak measured against Dualcast -- the Defect starter, 1(0)
                                             # energy for a double payoff -- and a cost-0 uncommon whose
                                             # upgrade buys 3 Encore is not in that conversation. At Uncommon
                                             # the ruled price for Dualcast-equivalent power is the repeat, so
                                             # the upgrade buys the second bow and the base stays the probe.
                                             # The old "combo piece before anyone measured the first one"
                                             # worry is answered by that split: the UNUPGRADED card is what
                                             # the playtest reads, and emptying a three-slot stage in two
                                             # plays now costs a smith.
```

## standing_ovation

```
                                             # +10%/spend amount is left authored rather than upgraded. NOTE the
                                             # original reasoning here ("would outgrow the two-copy cap") is VOID:
                                             # ovation_spend_boost's ceiling was dropped 2026-07-24 (uncap-all)
                                             # and it now stacks per copy. Cost stays the lever by ratification,
                                             # not by that argument.
```

## deep_breath

```
                                             # EB-118 2C, R194 point 6: the modal conversion takes the
                                             # upgrade with it. `remove: exhaust` was justified as
                                             # sugar_rush-EXACT parity, and the card is no longer Sugar
                                             # Rush -- it is a choose-one. A cost drop is the delta that
                                             # stays MODE-INDEPENDENT in effect as well as in grammar: it
                                             # improves both bodies by the same energy and changes neither
                                             # choice. Removing Exhaust would instead change HOW OFTEN the
                                             # choice is made, which is the one thing the prototype was
                                             # landed to measure.
```

## encore_performance

```
                                             # is too small — it is TARGET-DEPENDENCE: a 0-cost Rare that does
                                             # nothing at all unless a Spotlighted card is in hand when you draw
                                             # it. Retain answers exactly that, and only that. It lets the holder
                                             # keep the card across turns until a target exists, so the upgrade
                                             # buys TIMING rather than a bigger copy — the Rare never becomes
                                             # more explosive, it becomes reliable.
                                             # IT SIDESTEPS FLAG-2(ii) ENTIRELY. Every candidate that touched the
                                             # copy itself ran back into the `cost_override` semantics question;
                                             # `retain` binds to no op and sets a card FIELD, so it cannot
                                             # inherit that argument or break the way a bound delta breaks.
                                             # The v1 delta `{copy_cost_override: 0}` was DELETED 2026-08-06
                                             # ([USER], Y-4): R110/S-1 (S13 family X3) made the base card cost 0
                                             # and a 0-cost card cannot be discounted to 0, so it had already
                                             # stopped meaning anything. This is its authored replacement, and
                                             # the two `lint_upgrade_coverage.py` exemptions that carried the
                                             # debt in the meantime are deleted with it — the gate is green on
                                             # the real delta now, not on a curated silence.
```

## the_final_verdict

```
                                             # cuts the PRICE, floor drop 30 -> 20, rather than raising the
                                             # damage. Damage is already "equal to your Fanfare" and has no
                                             # printed number to grow; what the card actually costs is the
                                             # hole it digs, so that is the dial. PROPOSED.
```

## clorinde_impale_the_night

```
                                                 # upgrade buys the body and never the conditional --
                                                 # same split as Freminet's Backstroke. NOT re-scaled
                                                 # when the base doubled (2026-07-25 [USER] ruling on
                                                 # the card, which named the base only): +3 on a 20
                                                 # body is proportionally a much smaller upgrade than
                                                 # it was on a 10 body. Flagged for the red-pen rather
                                                 # than silently doubled to keep the ruling's scope
                                                 # exactly where it was set.
```

## neuvillette_ancient_sea_authority

```
                                                 # power_amount here would take auras from 3 turns to 4
                                                 # against a base AURA_DURATION_TURNS of 2, i.e. double
                                                 # duration, which lifts every applier in the pool and
                                                 # every aura-keyed payoff (Albedo, Clorinde) at once.
                                                 # That is a pool-wide multiplier bought on one card.
                                                 # Buying the same effect a turn earlier is the Nicole
                                                 # precedent and does not compound.
```

## arlecchino_masque_red_death

```
                                                 # names. The Bond of Life does NOT scale and is not
                                                 # removable by upgrade: the debt IS the card, and an
                                                 # upgrade that softened it would be a different card.
                                                 # +1 rather than +2 because the effect is a RATCHET --
                                                 # doubling the per-turn rate compounds over the fight,
                                                 # the same argument that made Nicole's upgrade cost.
```
