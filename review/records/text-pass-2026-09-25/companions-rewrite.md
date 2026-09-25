# Companions (and every arm): text rewrite (from `textpass/companions.md`, 2026-09-25)

TEXT ONLY. No number or behaviour moves.

## 1. "(proto)" leaks into player-facing names: remove it everywhere

These names are in `docs/prototype-surface.yaml`, across ALL arms. Every
`name:` that ends in " (proto)" loses that suffix. Examples: "Kaeya — Frostgnaw
(proto)" becomes "Kaeya — Frostgnaw"; "Fish Blasting (proto)" becomes "Fish
Blasting"; "Sango Isshin (proto)" becomes "Sango Isshin".

- If any name then collides with another card offered in the SAME arm pool, or
  with a card the blind page has to tell apart on one screen, report it rather
  than renaming it.
- Tests and lints keyed on the old names follow.

## 2. Faces

| Card / badge | New text |
|---|---|
| Heizou — Heartstopper Strike (`proto_mi_heizou_heartstopper`) | Deal 6 damage. Deals 4 additional damage for each [gold]Swirl[/gold] this turn. |
| Eula — Glacial Illumination | Place a [gold]Lightfall Sword[/gold] on the enemy. In 2 turns it deals 8 damage, and 5 additional damage for each Attack you play before then. |
| LightfallSwordPower badge | Falls in {N} turns for 8 damage, plus 5 additional damage for each Attack you play first. |
| Kamisato Ayaka — Soumetsu | At the end of each of your next 2 turns, deal 8 [gold]Cryo[/gold] damage to ALL enemies. The last one deals 16 additional damage. |
| SoumetsuPower badge | At the end of your turn, deal 8 [gold]Cryo[/gold] damage to ALL enemies. {N} turns left. The last deals 16 additional damage. |
| Yae Miko — Sesshou Sakura + SesshouSakuraPower | VERIFY FIRST against `SesshouSakuraPower.FireVolley`: what "plus 3 after the first" really does (does each Sakura after the first deal 3 more than the one before it, or does every Sakura after the first deal 4+3?). Then write, in this style: card `Place a [gold]Sakura[/gold], up to 3. At the end of your turn, each Sakura deals 4 [gold]Electro[/gold] damage to a random enemy, <truthful clause>.` and badge `At the end of your turn, your {N} Sakura each deal …`. Report the wording you chose. |
| Lynette — Enigmatic Feint | [gold]Swirl[/gold] the enemy. Gain 6 [gold]Block[/gold]. |
| Lynette — Astonishing Shift | [gold]Swirl[/gold] the enemy. Deal 6 damage to ALL enemies. |
| Kaeya — Cold-Blooded Strike | Deal 8 damage. Apply [gold]Cryo[/gold]. Next turn, [gold]Grounded[/gold] triggers even if you played a [gold]Set off[/gold] card. |
| Gorou — General's War Banner | Gain 2 [gold]Dexterity[/gold] for 2 turns. |
| Sayu — Naptime | Gain 4 [gold]Block[/gold]. If you play no Attacks this turn, draw 2 cards next turn. |
| Sayu — Muji-Muji Daruma | For 2 turns, at the end of your turn: above 70% HP, deal 6 damage to a random enemy; otherwise, gain 6 [gold]Block[/gold]. |

- Lynette's two cards are SHIPPED Fontaine rows (`docs/fontaine-companions.yaml`).
  A text-only change is allowed, but do NOT move a number, and keep the sheet
  stamp lints green. Report any stamp that moves.
- **Lynette truthfulness.** Check that "Swirl the enemy" does exactly what the old
  face said: the enemy's aura is copied onto ALL enemies. It must match what the
  Swirl tip says the keyword does. If the Lynette card targets a different enemy
  or differs in any way, STOP on that card.
- **The War Banner.** "then the banner takes it back" described the Dexterity
  loss. Confirm "for 2 turns" is how the base game prints a temporary stat (the
  way Flex-like temporary Strength is printed) and follow the base-game template.
