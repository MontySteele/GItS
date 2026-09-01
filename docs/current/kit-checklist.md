# KIT CHECKLIST

Nine yes/no checks a reviewer runs on a character brief, a package or a card
sheet. They were LAW's *Design charter* (R217, D1 to D9) until 2026-09-01, when
the machinery review's change 6 demoted them: they are a checklist a sheet is
read against, not a gate rows pass, and answering "no" to one is a finding for
the brief, not a merge block.

Nothing here is a numeric band and nothing here gates. The clause that says so,
and decision closeness (R213 F) as the only numeric design falsifier, stayed in
`LAW.md` under *Design governance*.

Provisional through the Klee slice, then reviewed.

## The checks

1. **Brief before pool.** Does the character have a short [USER]-owned brief,
   written before any pool construction, naming the player promise, two or
   three core verbs, one or two recurring tensions, the three archetype loops,
   the bridges among them, the intended weakness, what the starting relic and
   starter deck teach, and the failure modes to avoid? (A tension sentence
   summarises the character; it does not mandate that every card serve one
   mechanic.)

2. **Player-controlled leverage.** Does every persistent resource and every
   automatic engine feed a decision the player can steer, by timing, targeting,
   placement, acquisition, conversion or forgoing? Is that control reachable
   early and reliably, from the starter kit, the starting relic, the base
   system or the ordinary pool, rather than only through a rare? ("Watch it
   rise until the number is large" is not a decision.)

3. **Binding prices.** Where a card gives both defence and engine advancement,
   does one of them carry a binding cost: energy or tempo, a below-rate half,
   mutually exclusive outcomes, target or timing awkwardness, a card or
   resource spent, identity position, a future draw or deck cost, or the loss
   of another action? Run the counterfactual: remove the defence, and is what
   remains still a full-rate play the player already wanted? If yes, the
   defence was a subsidy.

4. **Visible and live.** At the decision point, can the player perceive and
   forecast the consequences that matter, through the card, a keyword, a
   persistent UI element or a character rule? (Not necessarily verbatim on
   every face.) Is any text unable to bind in the shipped world, any feed
   invisible, any calculated display misleading? A rare intentional edge case
   is not a defect for being rare.

5. **Simple surfaces, deep interactions.** Does the richness come from
   interactions between cards, enemies, energy, draw order, piles, targets and
   future turns, rather than from clauses on faces? Do the Commons establish
   the verbs and stay concise? Does every added line of text alter a decision?

6. **Every card has a place.** Does each card have one primary decision home:
   acquisition and build; combat (sequencing, targeting, holding, conversion,
   timing); teaching or utility, deliberately plain; or bridge? Plain cards are
   legal and necessary, and a pool of them is not a defect to be edited away.

7. **Mesh without preassembly.** Does the pool carry linear signposts AND
   modular tools, with no preassembled deck and no archetype written in a
   private language only its own cards speak? Do bridges exist, so combinations
   arrive unexpectedly? (Shared-verb and hook counts describe a pool. They are
   never acceptance bands.)

8. **Distinct play patterns.** Do the archetypes differ in how turns and drafts
   unfold, rather than in the label on a bigger number? Damage may stay
   terminal, but does the route, cadence, constraint, targeting,
   transformation, control or economy differ? One non-scalar payoff does not
   rescue an otherwise automatic loop.

9. **Shared layer and starting tutorial.** Do the Companion packages connect to
   both character verbs and universal verbs, and does each package have a
   distinctive identity? (Not every Companion card needs a hook.) Do the
   starting relic and starter deck introduce the central verbs and one
   recurring tension from fight one, with visible triggers and no invisible
   feed?

## Descriptive only, never a band

Hook share, bridge %, payoff-role %, scalar-payoff %, random-target %,
Powers-per-universal-verb count, plain-card % and word count, and the rate of
turns with a named alternative, are descriptive. No subjective front-matter
field enters card YAML, and there is no waiver mechanism.

(R217, drafted by GPT, sharpened by Claude, ratified by [USER]; demoted from
LAW to this checklist 2026-09-01, machinery review change 6.)
