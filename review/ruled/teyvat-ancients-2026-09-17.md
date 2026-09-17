Status: RULED R275 2026-09-17

# The Ancients, dressed per face: names, faces and words first, art second

Ruled R275 (2026-09-17) from a design discussion in the main session, on
the facts below. The August gallery
(`docs/current/dossiers/content/ancients-gallery.md`) supplied the
silhouettes; the nation mapping (R273) supplied the faces; this page
supplies the assignment.

## 1. What the game has

Eight Ancients. Act 1 is always Neow. Act 2 draws one of Orobas, Pael and
Tezcatara; act 3 one of Nonupeipe, Tanx and Vakuu; Darv recurs in both. The
pool is a property of the act model (`AllAncients`), so a face, which is a
sibling act model, can carry its own dressed variants. The Ancient classes
are not sealed. An Ancient's own text is its title, its epithet and its
dialogue lines (a first-visit line, three per known character, two
agnostic); its boons carry their own text.

## 2. The ruling

1. **One body per Ancient per face** (structure pick 1, default taken).
2. **Darv is Alice on every face** (pick 2, default taken): the recurring
   Ancient who rolls the Dusty Tome is Klee's mother, author of the Teyvat
   Travel Guide, met anywhere.
3. **The slate stands** (pick 3), with one change made by the enemy ruling
   of the same day: Azhdaha is the Liyue face's Waterfall Giant, so Neow on
   Liyue is Moon Carver.
4. **First pass = name, image and flavour text; the boons are not touched**
   (pick 4, default taken). Art is a second bill after the picture route is
   spiked.

| Ancient | silhouette (gallery) | face A | face B |
|---|---|---|---|
| Neow (act 1) | a great being in the dark, first boon | Mondstadt: Dvalin | Liyue: Moon Carver |
| Orobas (act 2) | refines what you already hold | Natlan: Xbalanque | Inazuma: the Sacred Sakura (Kitsune Saiguu) |
| Pael (act 2) | a dying dragon paying out of its own body | Natlan: Och-Kan, dragon lord | Inazuma: Orobashi |
| Tezcatara (act 2) | hospitality, food and drink | Natlan: a Wayob spirit, name kept | Inazuma: Ioroi the tanuki chief |
| Nonupeipe (act 3) | abundance and regalia | Fontaine: Egeria | Sumeru: Greater Lord Rukkhadevata |
| Tanx (act 3) | the many-headed beast king who heals and arms you | Fontaine: Elynas | Sumeru: Apep |
| Vakuu (act 3) | Faustian gifts, every one with a cost | Fontaine: Remus | Sumeru: King Deshret |
| Darv (acts 2-3) | the recurring scholar, the Dusty Tome | Alice | Alice |

Tezcatara keeps its name on the Natlan face and gains a body. Tanx, the
gallery's homeless case, lands on Elynas and Apep, which closes the earlier
"Tanx waits for a reflavoring" note.

## 3. What is frozen

Every boon, number, pool and lock. A dressed Ancient changes what it is
called, what it says and, later, what it looks like. Where the boon text
must be reachable under a dressed name, the build reuses the game's own
rows and never copies base-game prose into the repo.

## 4. What follows

The plumbing (a dressed class per Ancient per face, the face pool
override, a faces file the generator reads, headless pins), the faces
written by the main session, then the art bill.
