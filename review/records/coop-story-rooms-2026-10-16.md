# Co-op story rooms, 2026-10-16: two pairs, four seats

The first look at co-op story rooms (#1373, ruled in
`review/active/klee-varka-story-chains-2026-10-14.md`, "Co-op"). [USER]:
"Is it possible to instead give them separate events, appropriate to their
character? And for characters who have no events, they get a placeholder like
"heal 10 or gain 50 gold"". There were two blind Sonnet co-op pairs at A0 on
install 0.2.5741 (main 343052e37), each player quoting every event page.
Records: scratch `seats/archive/coop-2026-10-16/`; transcripts are not kept.

| Pair (host + client) | Seed | End |
|---|---|---|
| Furina + Varka | DJCAV76ZKAUN | Floor 45, act 3 boss (Queen + Torch Head Amalgam). Both acts' bosses beaten |
| Klee + Kokomi | FTBYF0Y9J6D5 | Floor 40, act 3 elite (Mecha Knight at 89 and 53 of 720) |

No crash or desync. Kokomi's seat stopped once at floor 26 after three
refused commands, chained onto a waiting page. It was reset and the run
finished.

## Did each player get their own story? Yes, in every act

| Player | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| Furina | Charlotte's letter | The Court's letter | The throne |
| Varka | The rearguard ("Take the rear yourself") | Boreas ("Spar with him") | Pick a Knight |
| Klee | The pond ("Blast the pond!") | Jean's letter | Friends arrive (pick a friend) |
| Kokomi (no story) | Placeholder: "Rest." (Heal 10 HP) / "Search the landing." (Gain 50 Gold) | Placeholder | Placeholder |

Each page carried its own character's options, and the act 2 events
followed each player's own act 1 choice. Both players in a pair saw the same
room at the same time, and the shared chests and votes behaved as in the
base game.

## What did not work

- **The title on every routed page read "A Quiet Landing"** (the
  placeholder's name). The seat bridge reads the room's canonical event
  (`vendor/STS2_MCP/McpMod.StateBuilder.cs`, `BuildEventState`), which is
  never routed to a player. Whether the in-game screen shows the same thing
  is being checked, and the fix is in flight.
- **Screen text from the seats:**
  - Furina: "Gain 2 additional 1 Energy next turn" has a stray "1".
  - Furina: Soloist's Solicitation reads "Spends 6: 1 more hit" but spent the whole bank.
  - Varka: Vambrace's Block preview doubles every card, though only the first is doubled.
  - Klee: Kaeya's Frozen preview does not say Artifact blocks it.
- **Lizard-Tail Gunpowder draws only after a Set off, and the page does not
  say so** (Klee seat). The staged cleanup on `klee-next` replaces this with a
  plain "Draw 1 card."

## Notes for the kits (one round, not a cut list)

- Klee: The Big One+ with Boom Badge did 260 to 444 in one turn. Tinder Toss
  was the card the seat would never take again.
- Kokomi: Plans bypassed the Gardeners' Skittish. In co-op, Klee often
  finished fights with Kokomi's hand still full. Kelp Wall's Plan line never
  mattered.
- Furina: Huddle Up's draw mostly helped the partner. Drain on Curtain Rise
  followed by Clean Slate was the best line.
- Varka: Marching Orders always read "+0 damage". The free 0-cost Ascension
  was left in hand twice.
- All four act 3 losses came from scaling enemies (Queen's Chains plus the
  Amalgam, the Mecha Knight's Strength 5 a turn) against decks with little
  Block left.
