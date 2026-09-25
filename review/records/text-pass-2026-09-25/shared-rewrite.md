# Shared surfaces: text rewrite (from `textpass/shared.md`, 2026-09-25)

TEXT ONLY. No number or behaviour moves. Numbers stay interpolated where they are
now.

| Surface | New text |
|---|---|
| Element Aura badges (`AuraPower`, one template for all four), in-combat face | `{Element} clings to this enemy for {N} more turns. A hit of another element triggers an [gold]Elemental Reaction[/gold].` |
| Element Aura badges, static face | `{Element} clings to this enemy. A hit of another element triggers an [gold]Elemental Reaction[/gold].` |
| Kokomi, character select | Divine Priestess of Watatsumi Island, a strategist who plans a turn ahead. |
| Reaction preview: Frozen | Hydro meets Cryo: its next action deals 50% less damage. Until it acts, the next Attack on it Shatters for 6 unblockable damage. |
| Reaction preview: Frozen (Boss) | Hydro meets Cryo: bosses can't be Frozen, so it gains 2 [gold]Vulnerable[/gold] instead. |
| Reaction preview: Overload | Pyro meets Electro: deals 6 damage to ALL enemies and applies 1 [gold]Weak[/gold] to the reacted enemy. |
| Reaction preview: Crystallize | Geo meets an aura: gain 4 [gold]Block[/gold]. The aura is consumed. |
| Applies Anemo | No aura: nothing happens. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. Anemo never stays on an enemy. |
| Applies Geo | No aura: nothing happens. Another aura: consumed, and an [gold]Elemental Reaction[/gold] triggers. Geo never stays on an enemy. |
| Reaction preview: Electro-Charged | Hydro meets Electro: the reacted enemy gains 4 [gold]Poison[/gold]. (Make sure Poison's own tip attaches.) |
| Burst Energy tip (`KleeCardTooltips.BurstBody`) | Fills {5} from each Elemental Skill card and each [gold]Elemental Reaction[/gold]. When full, your Burst card joins your hand, and casting it empties the meter. |
| Crashing Waves (shipped Furina) | Deal 8 damage to ALL enemies. Enemies with an aura take 5 additional damage. |
| Courtroom Drama (shipped Furina) | Your first [gold]Elemental Reaction[/gold] each turn applies 1 [gold]Vulnerable[/gold] and 1 [gold]Weak[/gold] to its target before the hit lands. |

- **The dropped aura clause.** "a <same element> hit refreshes its duration" is
  gone from the aura badges. Confirm the behaviour still exists (it does not move);
  it is simply not printed. This also removes the "a Electro" grammar bug.
- **Burst tip.** Keep the live "You hold X of Y" line if the tip prints one today,
  as `{12}/{40}.` at the end. If a character's fill rule differs from "5 per
  Elemental Skill card and per Elemental Reaction", STOP and report.
- **Codegen conditional.** The codegen's `conditional` op prints "If X: Y."; make
  it print "If X, Y." (text-conventions rule 7). This moves Stage Combat
  ("If an enemy intends to attack, gain 3 Block.") and every other generated row
  that uses it.
  - Run the codegen and let the diff show every face that moves. Report the count.
  - Shipped-sheet faces change their generated text only. If a sheet stamp or
    digest lint re-pins on generated text, follow its re-pin procedure and report.
- **Crashing Waves and Courtroom Drama** are shipped rows. The change is text-only;
  keep the stamp lints green and report anything that re-pins.
- **Not changed here:** Dodoco Tales, Klee's starter relic after its Ancient
  upgrade, prints the same text as Pounding Surprise under the arm, because the
  arm gates off its opening-Spark half. That is a design gap, not a text gap. Add
  ONE BACKLOG line: "Dodoco Tales does nothing beyond Pounding Surprise under the
  Klee arm (its opening-Spark half is gated off); it needs an arm body."
