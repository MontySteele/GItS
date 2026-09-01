# Klee — character brief, draft 4

**Written 2026-09-01 on branch `kit-overhaul-2026-09-01`. Paper only.** No sheet,
no code, no register row, no stamp moves. This is the D1 brief the charter asks
for and the shipped kit never had: the player promise, the verbs, the tension,
the three loops, the weakness, and what fight one teaches. It is written to be
read in fifteen minutes and argued with.

Draft 1 was written before the same exercise was done for a canon character
(`ironclad-brief-calibration-2026-09-01.md`); draft 2 was revised against that
calibration (§14). Draft 3 answered three notes: the rules contradiction,
auto-detonation, and the lore audit with the squishiness question (§15, and
the audit in §2). **Draft 4 records the picks taken on draft 3 and answers
pick 6 with the Little Hexenzirkel lore: two companion paths (§7, §16).**
`git diff` on this file shows the words.

---

## 0. The test this brief has to pass

1. **Three boards.** Three turn-five board states where the right play is a
   different verb. (§10)
2. **One contested thing.** One resource wanted two ways at once, with a real
   cost either way. (§4)
3. **Fight one.** The starter puts that tension on the table on turn one with
   nothing hidden. (§8, §11 script A)
4. **Borrowed systems.** Which payoffs live in the mod's shared layer rather
   than on her cards. (§3 rule 5, §5.5)
5. **The rule each Rare breaks.** One per loop. (§5)
6. **What the relic pays for.** Which verb is affordable only because it
   exists. (§8)
7. **Lore.** Every mechanic points at something Klee actually does or is, and
   the survival answer comes from her story, not from convenience. (§2)

## 1. The promise

You are a small child with a bag of explosives and no supervision. Everything
you touch is going to blow up. The only questions are **when**, **how big**,
and **whether you are standing too close.**

In play: Klee produces the largest single-turn explosions in the game, and she
sets every one of them up herself. A bomb is damage she has already paid for
and not yet collected. She decides when to collect it, and the game keeps
giving her reasons to collect early and reasons to wait. She survives the way
she does in Mondstadt: her traps go off under whoever steps on them, she runs
away after the bang, and when she behaves, Jean keeps her out of trouble.

**The obvious plan, from the starter:** plant, wait, boom. Everything else is
a branch off that plan, taken or not depending on what act one offers.

## 2. The lore audit

What she is, from the game and the story pages, and what each fact becomes
here. "Shipped" means it exists on the current sheet in some form.

| Source | Fact | Shipped? | In this brief |
|---|---|---|---|
| Normal attack *Kaboom!* | Throws bombs; every hit is AoE Pyro | yes | Her Attacks; every hit applies Pyro (rule 5) |
| Charged attack *Explosive Spark* | Costs stamina; after *Pounding Surprise* procs, free and 50% stronger | as the old 3-Spark rule | Sparks as an alternative cost on specific strong cards (rule 4) |
| Skill *Jumpy Dumpty* | Bounces three times, then **splits into mines** that explode on contact or after a delay | as damage plus one bomb | The starter Jumpy Dumpty: a Bomb that leaves **Mines** when it goes off; Mk.II bounces (rule 3, §8) |
| Burst *Sparks 'n' Splash* | Sparks attack nearby enemies on their own for a while | kit Burst, retiring | Rare Power: at end of turn, set off a random enemy (§5.2) |
| Passive *Pounding Surprise* | Jumpy Dumpty and attacks have a chance to grant an Explosive Spark | starter relic | The relic: one Spark per explosion (rule 4, §8) |
| Passive *Sparkling Burst* | A charged-attack crit gives the party energy | no | Catalytic Converter: a reacting explosion gives 2 Sparks (§5.5) |
| Passive *All Of My Treasures!* | Shows Mondstadt chests on the map; bombs are her "treasures" | Rare Skill | Kept; treasure = bombs is the naming voice for the Cook loop |
| C1 *Chained Reactions* | Attacks and skills summon extra sparks during the Burst | Rare | Rare: every explosion plants a new Bomb somewhere (§5.2) |
| C2 *Explosive Frags* | **Mines** lower enemy DEF | Rare (explosions apply Vulnerable) | Kept, re-keyed to Mines: a Mine going off applies Vulnerable |
| C4 *Sparkly Explosion* | Leaving the field during the Burst causes a huge explosion | Rare | Rare Attack, exhaust: set off every Bomb on every enemy at double |
| C6 *Blazing Delight* | Party-wide Pyro bonus and energy during the Burst | Rare | Co-op card (R144: co-op depth is cards) |
| Title *Fleeing Sunlight* | She runs after the bang | *Run Away!* exists, plain | **Run Away!**: Block, more if a Bomb went off this turn. Spray's defence (§6) |
| Jean, solitary confinement | She is grounded when she misbehaves; when she behaves she is safe | *Sorry, Jean...* exists, plain | **Grounded** (Power): Block at the start of your turn if no Bomb went off last turn. Cook's defence (§6) |
| Confiscation | Jean takes her bombs away | *Confiscated* status exists (Fish Blasting) | **Sorry, Jean...**: remove one of your Bombs, gain Block equal to its size (§6) |
| Albedo, her caretaker | Cleans up her messes; her big brother | no | Rare Personal Companion, once R234 P5a is answered (§7) |
| Diona, Barbara, Noelle, Sucrose | The friends who look after her | Diona is a plain Universal | Personal Companions are her **babysitters**: defence hooked to explosions (§7) |
| Alice, her mother | Taught her bombs; the Teyvat Travel Guide; far more destructive than Klee | no | The rule-breaking Rares are Alice's recipes (§5) |
| Dodoco | Stuffed toy from her mother; her first friend; one of the Little Hexenzirkel's "imaginary friends" | card name only | A relic candidate: Klee starts combat with a Bomb already planted (§13) |
| Hexerei passive (Luna III) | With two or more Hexerei characters in the party, Klee gains **Boom Badges from attacks, up to 3**, powering her charged attack | the old "at 3 Sparks" rule, unknowingly | Confirms Sparks as a small bank spent on a big hit, and that the source game itself counts to three |
| The Little Hexenzirkel (Luna VII) | Klee founded her own coven in Chinju Forest after Alice's challenge: Qiqi, Yaoyao, Sayu, then Prune; "little" because they all still have growing to do; each brings an imaginary friend | Prune's card only | Her second companion path: **her own coven**, off-region on purpose (§7) |
| Prune (Luna VII) | Self-styled witch hunter from Nod-Krai chasing Alice, who "kidnapped" her imaginary friend Descartes so that Klee would make a friend; Anemo; her hammer **absorbs the element she Swirls** | Prune — Witch Hunt (Swirl, Klee-personal) | The canonical way to give Klee an off-element bomb: Prune's Swirl converts the next explosion (§7) |
| The Red Knight of Stormbearer Mountains | Too many charges, half a mountain gone | no | The Big One's flavour; the Cook loop's signature moment |
| Fish blasting | Her hobby; gets her confiscated | Fish Blasting, adds Confiscated | Kept as is: AoE with a cost card |

Nothing on the current sheet is contradicted by her story. What the current
sheet **misses** is the half of her story that is about other people
managing her: Jean grounding her, Albedo and the others cleaning up after
her, and her running away after the bang. That half is exactly the survival
half, which is why the shipped kit had no interesting answer to it.

**The squishiness answer, from the lore:** Klee does not block. She survives
because (a) her mines go off under whoever attacks her, (b) she runs away
after an explosion, (c) when she behaves, Jean keeps her safe, and (d) her
friends look after her. Each of those is a mechanic below, each is keyed to
the cook-or-cash decision, and none of them is "the bomb is a shield."

## 3. The rules of the kit

Seven sentences. If a rule is not here, it is a card.

1. **Bomb.** A numbered charge on an enemy. At the start of Klee's turn every
   Bomb grows by **2** (placeholder). A Bomb never goes off on its own.
2. **Set off.** Only a card that says *Set off* makes Bombs go off. It sets
   off every Bomb on the target, **one at a time, before the rest of the card
   resolves**, each dealing its number as Pyro damage. Plain Attacks, a co-op
   partner's Attacks, and companions' Attacks that do not say *Set off* leave
   Bombs where they are.
3. **Jump.** A Bomb whose enemy is already dead jumps to a random enemy at its
   current size instead of going off. (The second of three Bombs killed the
   enemy: the third jumps. A partner or a poison killed the enemy: all of them
   jump.)
4. **Spark.** Each Bomb that goes off gives Klee 1 Spark. Some cards cost
   Sparks instead of energy, printed as a badge. No cap. Lost at the end of
   combat.
5. **Pyro.** Every Klee Attack applies Pyro, and so does every explosion. An
   explosion is an ordinary Pyro hit: Vulnerable and Weak on the enemy,
   Strength on Klee, and every reaction in the element table apply to a
   cooked bomb without a word printed on her cards. Off-element auras come
   from companions, as the law says now.
6. **Mine.** A Mine is a Bomb that *also* goes off when its enemy attacks
   Klee, before the attack lands. It cooks like any Bomb. Mines come from
   Jumpy Dumpty and from cards that say so.
7. **Nothing fires by itself.** No start-of-turn detonation, no automatic free
   attack, no "at 3 Sparks". Every explosion is her *Set off* card, her Mine
   answering an attack on her, or her Rare.

Persistent UI: the Bomb badge on the enemy (size, and a fuse mark if it is a
Mine) and the Spark count. That is the whole rules display.

## 4. The contested thing

**The Bomb on the board is the thing she wants two ways at once.** While it
sits, it grows. When she sets it off, the damage lands, the Sparks arrive,
and it is gone. Every *Set off* card is a timing decision and, with more than
one enemy, a targeting decision about which bombs to collect.

Her defences are keyed to that same decision, in opposite directions:

- **Grounded** pays her for a turn in which nothing went off. Cooking is the
  safe turn.
- **Run Away!** pays her for a turn in which something did. Cashing is the
  safe turn.
- **A Mine** is both: it is damage she is cooking *and* a trap under the
  enemy's next swing.

So choosing cook or cash also chooses which defence is live this turn. That
is the Defect's hold-or-evoke question with the orb on the enemy and the
Frost half split in two. The enemy's intent answers it, differently every
fight.

Sparks are the second contest. A Spark buys a free *Set off* Attack now
(tempo, more explosions, more Sparks) or a Spark-priced Skill that plants,
grows, or defends (setup). Generation only comes from explosions, so she
cannot bank Sparks without collecting bombs. Lean in and it flows; otherwise
it is stingy, the Regent's Stars governor by scarcity and not by cap.

## 5. The three loops

Each loop is a different shape of turn, not a different number.

### 5.1 Cook — "the big one" (the starter's plan)

Few bombs, grown large, cashed with one heavy *Set off*. The boss plan, and
the plan the starter teaches.

- **A turn looks like:** plant on turn one, then two or three quiet turns of
  plain Attacks, Grounded Block and Skills that grow the bomb, then one loud
  turn.
- **You draft:** Fish-Flavored Bait and Pocket Fireworks (plain Attacks that
  keep pressure without cashing), Chain Fuse and Explosives Workshop (grow
  faster), Careful Arrangement (pile every Bomb onto one enemy, which also
  makes one big reacting number), Grounded and Sorry, Jean... (defence), Big
  Badda Boom and The Big One (*Set off* with a multiplier), Remote Detonator
  (*Set off* on a Skill).
- **The payoff moment:** the Red Knight of Stormbearer Mountains. A single
  30-plus explosion, then the Sparks it minted pay for the follow-up.
- **The decision every turn:** "is it big enough, or can I afford one more
  turn?" Grounded makes "one more turn" cheaper; the intent makes it dearer.
- **The Rare that breaks a rule:** *Alice's Recipe* (Power): Bombs grow by 4.
  Rule 1's number doubles and every quiet turn is worth two.
- **Weakness:** hallways with three small enemies, and anything that hits
  harder than Grounded and a Duck and Cover can hold.

### 5.2 Spray — "everything explodes now"

Many cheap bombs, cashed immediately by Spark-priced *Set off* Attacks, which
mint the Sparks for the next one. The hallway plan and the Shiv analogue.

- **A turn looks like:** six to nine card plays, random targets, bombs going
  off on every enemy, Run Away! at the end, the board cleared by turn two or
  three.
- **You draft:** Pop! and Mine Toss (cheap bombs and mines), Fwoosh! and
  Tinder Toss and Bang Bang! (Spark *Set off* Attacks), Rapid Fire (four
  random hits, *Set off* each enemy hit), Run Away! (defence), Chained
  Reactions (every explosion plants a new Bomb somewhere).
- **The payoff moment:** the chain, when one Attack sets off three enemies'
  bombs, the Sparks pay for two more Attacks, and the turn does not end.
- **The decision every turn:** where to send the random hits to keep the chain
  alive, and whether to leave one Mine cooking under the enemy that is about
  to swing.
- **The Rare that breaks a rule:** *Sparks 'n' Splash* (Power): at the end of
  her turn, set off a random enemy's Bombs. Rule 7 is gone; something now
  fires by itself, and the chain no longer needs a *Set off* card in hand.
- **Weakness:** one big enemy with Block, and running out of bombs, which
  means running out of Sparks and out of Run Away! triggers.

### 5.3 React — "the one that goes off twice"

Explosions are Pyro, so a Bomb set off on an enemy carrying a foreign aura
reacts: Vaporize on Hydro, Melt on Cryo, Overload splash on Electro. The
multiplier lands on the cooked number, and since bombs go off one at a time,
on the *first* one, which is why Careful Arrangement is a React card.

- **A turn looks like:** a companion applies Hydro this turn, and next turn
  she sets off the bomb for one and a half times its size. Sequencing is the
  whole game.
- **You draft:** Dahlia, Kaeya, Diona, Fischl from the Mondstadt pool (the
  appliers), Sucrose (Swirl spreads the aura), Sizzle and Perfect Timing and
  Flame Dance (*Set off* Attacks that pay extra against an aura), Careful
  Arrangement, Catalytic Converter (a reacting explosion gives 2 Sparks).
- **The payoff moment:** a cooked 15 that Vaporizes into 22 and applies Pyro
  on the way out.
- **The decision every turn:** cash now for the plain number, or wait one turn
  for the aura and risk the enemy's swing.
- **The Rare that breaks a rule:** *Vermillion Pact* (Power): when an
  explosion reacts, the Attack that set it off reacts too. The shared "one
  aura, consumed by the first hit" rule is broken for her chain.
- **Weakness:** she cannot apply the second element herself. Without an
  applier in hand this is a slightly worse Cook deck, and it is the loop that
  gets better in co-op without needing it: a partner's aura is a partner's
  aura.

### 5.4 Bridges

- Jumpy Dumpty (starter): a Bomb that leaves Mines. Cook's bomb, Spray's
  fuel, everyone's defence.
- Sorry, Jean...: turns any bomb into Block. Cook's emergency exit, Spray's
  reset.
- Quick Fuse: a Spark to *Set off* one enemy without an Attack. Spray's
  economy, Cook's cash button when the hand has no *Set off*.
- Any Pyro-applying companion play into a cooked bomb. React reaches into both
  other loops rather than needing its own.

### 5.5 Currencies, and which way they cross

- **Bombs → damage** (rule 2), **→ Sparks** (rule 4), **→ Block** (Sorry,
  Jean..., Common: at a cost, the bomb is gone), **→ the attacker's HP before
  it hits you** (Mines).
- **Bombs → cards:** Ammo Scavenging (Common): plant a Bomb 4, then draw a
  card for each Bomb that went off this turn.
- **Sparks → Attacks** (Fwoosh! and friends, Common), **→ setup and defence**
  (Dig In, Powder Charge, Uncommon), **→ energy only at Rare:** Sugar Rush (2
  Sparks, exhaust: 2 energy and a card). Below Rare, Sparks never become
  energy, or they are a second energy pool.
- **Reactions → Sparks:** Catalytic Converter. React feeds Spray.
- **Not exploding → Block** (Grounded); **exploding → Block** (Run Away!).

Every currency reaches every other one somewhere in the pool, at the rarity
that keeps it a discovery rather than a default.

## 6. The intended weakness, and how she survives anyway

**She cannot stall, and she cannot block on demand.** Her only plain Block is
Duck and Cover, 5 for 1. Every other defence she has is conditional on the
decision she just made:

| Defence | Trigger | Lore | Which loop |
|---|---|---|---|
| **Mine** | Its enemy attacks her: it goes off first, at its cooked size | Jumpy Dumpty's mines explode on contact | All; Spray most |
| **Grounded** (Uncommon Power) | Start of turn, if no Bomb went off last turn: Block | Jean's solitary confinement: behave and you are safe | Cook |
| **Run Away!** (Common, 0 energy) | Block, more if a Bomb went off this turn | *Fleeing Sunlight*: she runs after the bang | Spray |
| **Sorry, Jean...** (Common) | Remove one of your Bombs; Block equal to its size | Jean confiscates the bomb | Cook's emergency exit |
| **Her friends** (Personal Companions) | Block or a shield when an explosion happens, on the companion's face | Diona, Barbara, Noelle look after her; Albedo cleans up | All, drafted |

Against a boss that hits harder than Grounded plus a Duck and Cover, she must
cash early and small, which is exactly the situation she hates. Against three
small enemies, a Mine kills the attacker before it swings, and the player who
cooked a Mine to 12 under a 9-HP raider gets to feel clever. Against a fast
elite, Run Away! is worth more than Grounded and the Spray line is forced.
The weakness is load-bearing because it is what makes cooking a bet.

**Where the player feels it.** On the draft screen: every plain Block card is
5 for 1, her draw is two Commons, and half her Attacks pick their own
targets. On the map: an act-2 hallway with three enemies that each hit for 10
cannot be cooked unless the bombs are Mines. She feels the missing Block the
way Ironclad feels the missing draw, and a Diona in the reward screen reads
as relief for the same reason Whirlwind does for him.

## 7. The companion layer, for her: two paths

R234 gives Klee three to five Personal Companions and drafted two on
2026-08-31 (Razor and Amber, offence hooks; paper only, not landed). The new
lore splits her people in two, and this brief proposes that her Personal
Companions split the same way. **The draft question becomes: am I Jean's Klee
or Alice's Klee?**

### 7.1 Jean's Klee — the grown-ups, Mondstadt, defence

The people who look after her: Diona, Noelle, Barbara, Kaeya, and at Rare,
Albedo and Jean. Their hook is defence keyed to explosions, which is her
team in the source game (shielders around a glass cannon) and her story
(the people who clean up after her). This path leans Cook: it makes the
quiet turns safe.

Candidates at 4-star, hook stated, no numbers: Diona (when a Bomb goes off,
gain Block; and Cryo, so Melt), Noelle (when a Mine goes off, gain Block),
Kaeya (a cover story: Grounded pays this turn even though something went
off), Barbara (a Bomb went off this turn: heal, Rare-tier by the healing
law, so this one waits). Albedo and Jean are 5-star and therefore Rare
Personals, which R234 P5a bars for now; they are the strongest reason to
answer that sub-pick.

### 7.2 Alice's Klee — the Little Hexenzirkel, off-region, witchcraft

Her own coven: Prune, Sayu, Qiqi, Yaoyao, and their imaginary friends. Their
hook is offence and tempo through witchcraft, which in this mod's terms is
elements, reactions and free plants. This path leans Spray and React, and
it answers your note on Pyro being a weak reaction payoff in the way you
suggested, through a companion:

- **Prune** (Anemo, in the sheet already). In the source game her hammer
  absorbs whatever element she Swirls. Here: Swirl, and **the next Bomb set
  off this turn deals the Swirled element instead of Pyro.** Klee's own Pyro,
  which is on every enemy she has touched, stops being the thing that eats
  the aura and becomes the aura the bomb reacts with. A cooked 20 that Swirls
  Hydro into itself and lands on her Pyro is the React loop's real payoff,
  and it needs no LAW change: the off-element still comes from a companion.
- **Qiqi** (Cryo). The Cryo applier the coven brings: Melt is the strongest
  amplifier in the table. Her herbal side is healing and waits on the
  healing law like Barbara.
- **Sayu** (Anemo, sneaky, sleepy). Tempo: Swirl to spread Pyro to every
  enemy, and a Run Away! rider, because Sayu is the one who runs away
  professionally. Sayu already has three Inazuma Universal cards for
  Kokomi; her Klee-personal face is a fourth card with a different name.
- **Yaoyao** (Dendro, which this mod does not have). Her Yuegui throws
  radishes: a small summon that plants a Bomb 2 on a random enemy at the end
  of each turn. Free planting is Spray's fuel and needs no element at all,
  like Gorou's element-less Geo.
- **The imaginary friends** (Popcorn the boar, Descartes, Gena, Yuegui) are
  the coven's Oz-style summons if a fourth or fifth card is wanted.

**The coven bonus.** The source game gates Hexerei passives on having two
Hexerei characters in the party. The mirror here: a Little Hexenzirkel
Personal has a second line that turns on once another coven card has been
played this combat. Two witches make a circle. This is a density payoff, so
it stays on Personals only (R234 P6: never on Universals), and it is a bonus
line, never the card's body (D6: every card has a place alone).

### 7.3 What is tricky about it, honestly

- **Off-region Personals.** Prune already proves the mechanism: a card can
  be `personal_pool: klee` whatever its nation. What the shop's home-region
  slot does with a Personal from Liyue is a real question, and the P7
  re-measure of Personal appearance rates becomes load-bearing with six of
  them instead of three.
- **Count.** Two paths of three is six Personals, above R234 P5's "three to
  five, starting at three". Fewer than three per path and a path is a
  coincidence rather than a plan.
- **Name and art collisions.** Sayu's fourth card; Qiqi and Yaoyao have no
  Liyue pool yet, so their first cards would be Klee's; art for children in
  the StS style is the scarce input.
- **Hexerei on Universals.** Fischl, Sucrose, Albedo, Durin and Nicole are
  Hexerei in the source game and Universals here. The temptation is to
  print "Hexerei" density on them. R234 P6 says no, and it is right.

### 7.4 Hexerei as a shared tag, and how many cards go in Klee's pile

Your refinement, taken: **Klee is herself Hexerei**, so the source game's
"two Hexerei in the party" is, for her, "Klee plus any Hexerei card." That
makes Hexerei a *family* rather than a path, and it changes the shape of
§7.2 and §7.3 for the better in three ways.

1. **Hexerei is a one-word tag on companion cards, with no effect of its
   own.** Fischl, Sucrose, Albedo, Razor, Mona, Venti, Durin, Nicole, Varka
   and Prune carry it because they carry it in the source game. A tag is not
   an engine interaction, so the Universal contract (R234 §1.2) is untouched
   and Kokomi and Furina see the same card with a dead trait, exactly as a
   Natlan tag would be dead for a Mondstadt character in the source game.
2. **Klee's own cards read the tag.** This is where the Klee-specific payoff
   lives, and it is the Prune mechanism generalized: her kit already mints
   Sparks in response to a Personal play (`KLEE_COMPANION_SPARK_*`); it can
   respond to a Hexerei play the same way. Three or four readers, no more,
   as a bridge into the companion layer and not a fourth loop: a Common
   ("if you played a Hexerei card this turn, plant a Bomb"), an Uncommon
   Power ("whenever you play a Hexerei card, plant a Bomb 3 on a random
   enemy" or "…gain a Spark"), a Rare ("Alice's Letters: Hexerei cards cost
   1 less; when one triggers a reaction, the next Bomb set off this turn
   deals that element"). Varka, Nicole or Durin, when they ship, write their
   own readers against the same tag, and inherit every tagged card for free.
3. **Hexerei faces are the exception, not the rule.** A card gets a
   Hexerei-only face (the Universal face for everyone else, the Hexerei face
   for Klee and future Hexerei characters, by the pool-substitution seam
   Kokomi's Oath already uses) only when the extra line is *family-generic*
   witchcraft, never a Klee verb: Sucrose's Swirl spreading to all enemies,
   Albedo's Isotoma reading reactions, Prune's absorbing Swirl. A Hexerei
   line that says "when a Bomb goes off" is a Klee line wearing a family
   badge and would be dead for Varka; it belongs on a Klee reader instead.
   Mechanically a Hexerei face is a Personal whose owner is a family:
   `personal_pool` becomes a list, and no third taxonomy is created, which
   keeps faith with R234 P6.

**So the coven path (§7.2) shrinks to what is actually Klee's:** the Little
Hexenzirkel Personals (Prune, Sayu, Yaoyao, Qiqi) are hers alone because
they are her coven; the witches (Fischl, Sucrose, Albedo, Durin, Nicole,
Mona, Razor, Venti, Varka) reach her through the tag and, for a few of
them, a family face. The grown-ups path (§7.1) is unchanged.

**How many cards in the pile.** The roster template's "~75-card pool" is a
convention, not a law, and a 75-card pool of near-duplicates (the
distinctness lint has hers at 63% unique today) is worse than a smaller one
where every card is live. My recommendation, as a starting shape and not a
band:

| Layer | Count | What it is |
|---|---|---|
| Klee's own pool | about 60 | 4 basics; Cook, Spray and React at 14 to 16 each; 8 to 10 bridges, defence and utility; 8 Rares including the three rule-breakers |
| Personals | 6 | Grown-ups 3, coven 3 (pick 6) |
| Hexerei faces | 4 to 6 | Family-generic lines on the witches who want one |
| Klee-side Hexerei readers | 3 to 4 | Inside the 60, counted above |

That is roughly 70 faces that only Klee sees, plus the tag on every
Hexerei Universal, plus the Universal pool at its nation weighting. It is
smaller than the shipped 79-card sheet on her own side and larger in what
the player can do with it. If the sheet draft finds fewer than 60 live
cards, the answer is to stop at the number that is live and let the Hexerei
layer carry the breadth, which is your option and I agree with it. The
delete-test still governs: Personals and Hexerei faces are her cards, so
deleting them gutting the deck is allowed, but deleting *only* her own 60
must gut it too, or the companions are carrying.

### 7.5 Why it is worth it

It gives the draft a second identity axis that is *not* about damage: who
is looking after Klee. Cook with the grown-ups reads as the child being
kept safe; Spray and React with the coven reads as the child running her
own show. Both are her. No other character in the mod has a companion
choice that says something about who they are, and this one is written in
the source game's own most recent chapter.

## 8. What fight one teaches

Starter deck, ten cards: Kaboom! ×3 (1 energy: 6 damage, *Set off*), Ka-pow!
×1 (1 Spark: 7 damage, *Set off*), Duck and Cover ×4 (1 energy: 5 Block), Pop!
(0 energy: plant a Bomb 5), Jumpy Dumpty (2 energy: plant a Bomb 8 on a random
enemy; when it goes off, plant a Mine 3 on every enemy).

Relic, Pounding Surprise: the Spark rule in §3. It is the only free Spark
source, and it **pays for a whole verb**: every Spark-priced card in the pool
is playable only because explosions mint Sparks. Without the relic, Spray is
a deck of dead cards, which is exactly Burning Blood's relationship to
Ironclad's Bleed. The player meets the relic's job on turn two of fight one,
when the first explosion turns Ka-pow! from a blank into a free 7.

Turn one, fight one, the player sees: a 0-cost card that puts a 5 on an
enemy, three Attacks that say *Set off*, a Spark card they cannot afford yet,
and Jumpy Dumpty promising Mines. The obvious plan is on the table: plant,
Duck, and next turn Kaboom! collects a 7. Every verb is visible, the badge
shows the bomb growing, and nothing is hidden. Script A plays it out.

## 9. Failure modes, named

- **The delayed Strike.** A bomb that is just damage with a delay. Prevented
  by growth, by Mines, and by payoffs that read bombs for something other
  than damage.
- **The second energy pool.** Sparks that only buy more attacks. Prevented by
  Spark-priced Skills and by generation only from explosions.
- **Auto-fire.** Anything that detonates or spends without the player's
  action. Attacks do not set off Bombs unless they say so; a partner's never
  do. The one exception is a Mine answering an attack on her, which is the
  point of a Mine.
- **Watch it rise.** Cooking with no reason to cash early. Prevented by the
  enemy's clock, by Run Away! and Mines rewarding the cash, and by Grounded
  rewarding the cook: whichever she picks, she is giving up the other.
- **The companion-locked loop.** React needs companions, and that is allowed,
  but Cook and Spray must each win without a single companion. Her friends
  make her *safer*; they must not be the only way she survives.
- **Word salad.** Commons print at most two lines. The badge and one
  character rule carry the mechanics. *Set off* and *Mine* are keyword-sized;
  see pick 5.

## 10. The three-board test (turn five)

**Board A, Cook.** Act-1 boss at 90 HP, one Bomb on it at 13, Grounded in
play. Its intent is a 14 hit. Hand: Kaboom!, Duck and Cover ×2, Sorry,
Jean..., Big Badda Boom. Sparks 2. Right play: Duck and Cover twice for 10,
take 4, nothing goes off so Grounded pays 7 next turn, the bomb cooks to 15,
and next turn Big Badda Boom sets it off and reads it again. Sorry, Jean...
stays in hand as the exit if the intent turns ugly. **Verb: Cook.**

**Board B, Spray.** Three raiders at 9, 11 and 20 HP, Bombs at 5 on two of
them, a Mine at 4 on the third. Sparks 2. Hand: Ka-pow!, Tinder Toss, Pop!,
Kaboom!, Run Away!. Right play: Tinder Toss (1 Spark: 4 to all, *Set off*
each) sets off both bombs and the mine, 3 Sparks, Ka-pow! the survivor at 11,
Pop! on whatever is left, Kaboom! collects it, Run Away! for 6. Two enemies
die, three cards were free, and she is blocked. **Verb: Set off, everywhere.**

**Board C, React.** One elite at 60 HP carrying Hydro from Dahlia last turn.
The aura expires at the end of this turn. One Bomb on it at 9. Hand: Kaboom!,
Chain Fuse, Duck and Cover ×2, Sizzle. Right play: Sizzle now (*Set off*, 8
plus 6 against an aura), because the explosion resolves first and Vaporizes
9 into 13, then the Attack lands on a fresh Pyro aura. Waiting a turn would
grow the bomb by 2 and lose 4 from the multiplier. **Verb: Cash now, for the
multiplier, even though cooking was available.**

Three boards, three verbs, and on every board the defence she has depends on
the verb she picks.

## 11. Turn scripts

Real act-1 enemies from the dossiers where they exist. The boss in script B
is a stand-in with placeholder numbers, because the decision is the point.
Hands are drawn as stated, not cherry-picked.

### Script A — fight one, Ruby Raiders (the starter's plan)

**Enemies:** Axe Raider 21 HP (Swing 5 and gains 5 Block, Swing, then Big Swing
12). Crossbow Raider 19 HP (Reload for 3 Block, then Fire 14). Brute Raider 32
HP (Beat 7, then Roar for 3 Strength).

**Turn 1.** Hand: Kaboom!, Kaboom!, Duck and Cover, Pop!, Jumpy Dumpty. Energy
3. Incoming: Axe 5, Crossbow 0, Brute 7.

The safe line is Kaboom! twice into the Axe Raider (21 to 9) and Duck and
Cover. Nothing planted. The obvious Klee line is Jumpy Dumpty, Pop!, Duck and
Cover: an 8 lands on a random raider, say the Brute, Pop! puts a 5 on the Axe
Raider, Duck blocks 5, she takes 7. Board at end of turn: Brute carrying 8,
Axe carrying 5, nothing collected, Klee at 55. She ate a hit to load the
board, and the badges say what it will be worth.

**Turn 2.** Bombs grow to 10 and 7. Hand: Kaboom!, Ka-pow!, Duck and Cover ×3.
Incoming: Axe 5, Crossbow 14, Brute Roar.

Kaboom! the Brute: the 10 goes off first (1 Spark), then 6. Brute 32 to 16.
Ka-pow! is now affordable: into the Axe Raider, the 7 goes off (2 Sparks),
then 7, Axe dead at 21, no bomb left to jump. The Crossbow's 14 is coming, so
three Duck and Cover for 15. Board: Brute 16, Crossbow 19 reloaded, no bombs,
Sparks 2, Klee 55. Two explosions, two free damage, and the player has just
learned that Sparks come from explosions and go on Ka-pow!.

**Turn 3.** Hand: Kaboom!, Pop!, Jumpy Dumpty, Duck and Cover, Kaboom!.
Incoming: Brute Beat 10, Crossbow Fire 14. Energy 3.

The cook-or-cash turn. Cash: Kaboom! the Crossbow (6, through 3 Block),
Kaboom! the Brute (6), Duck. Nothing planted, 24 incoming minus 5, she takes
19. Cook: Jumpy Dumpty on a random raider, say the Crossbow, an 8, and Pop!
a 5 on the Brute, Duck and Cover, take 19 anyway. Same damage taken, and
next turn the Crossbow carries 10 and the Brute 7 into two Kaboom!s with
Mines landing everywhere when the Jumpy goes off. She cooks. **Turn 4:**
Kaboom! the Crossbow: 10 goes off, it dies at 19, and Jumpy Dumpty leaves a
Mine 3 on the Brute. Kaboom! the Brute: 7 and the fresh Mine 3 go off, then
6, Brute to 0. Fight over turn four, Klee at 36 and 4 Sparks in hand for
nothing, which is the last lesson: Sparks do not carry, so spend them.

**What fight one taught:** plant, wait, boom is the plan; Sparks are for
spending; a Mine is a bomb that also hits back; the badge told you
everything. Nothing about Grounded or Run Away! yet. Those are act-one
drafts, and the first Run Away! she is offered will make immediate sense.

### Script B — act-1 boss, single enemy (Cook, mid-act deck)

**Deck additions since fight one:** Grounded, Chain Fuse, Careful
Arrangement, Big Badda Boom, Fish-Flavored Bait, Sorry, Jean..., one Dahlia.
**Boss (stand-in):** 140 HP, pattern Swing 12, Swing 12, Crush 20 and gains
Block, repeat.

**Turn 1.** Hand: Pop!, Grounded, Fish-Flavored Bait, Duck and Cover, Duck and
Cover. Incoming 12. Grounded (1). Pop! (0): a 5 on the boss. Fish-Flavored
Bait (1): 5 damage, plant another 5, no *Set off*. Duck and Cover (1). Take
7. Board: two bombs at 5, boss 135, Grounded armed. Nothing went off, so
next turn starts with 7 Block. She attacked the boss and still cooked, which
is what plain Attacks are for.

**Turn 3.** Bombs at 9 and 9, plus a third at 6 from Chain Fuse on turn two.
Grounded has paid twice. Hand: Careful Arrangement, Kaboom!, Duck and Cover,
Big Badda Boom, Sorry, Jean.... Incoming: Crush 20. Energy 3, Block 7 from
Grounded already.

The decision the loop exists for. Cash: Big Badda Boom (2) sets off 9, 9 and
6 one at a time, then 16, then reads the bombs again for 24. That is 64,
boss to 71, three Sparks, Duck for 12 total, take 8, and Grounded pays
nothing next turn. Cook: Careful Arrangement piles the three into one 26
(its rider adds 2), Duck and Cover for 12, take 8, Grounded pays 7 again,
and next turn the pile is 28 into Big Badda Boom for 28 plus 16 plus 28.
Same 8 HP either way; the cook line pays 72 instead of 64, a turn later, and
keeps Grounded alive. She cooks, and the whole turn was one Skill and one
Block card. Sorry, Jean... stays in hand as the exit.

**Turn 6.** Boss at 63 after the turn-4 cash. One fresh Pop! at 7 on it.
Hand: Kaboom!, Fish-Flavored Bait, Duck and Cover, Dahlia, Sorry, Jean....
Incoming Swing 12. Sparks 4 and no Spark card in the deck, which the player
now notices is the draft hole. Dahlia: 6 and Hydro. Kaboom!: the 7 goes off
first and Vaporizes into 10, applying Pyro, then 6. Boss to 41. Grounded
will not pay next turn. Duck and Cover, take 7. **What the script shows:**
the Cook deck's turns are quiet, the cash turn is loud, Grounded makes the
quiet turns free, and the missing piece is on the board, not in a tooltip.

### Script C — two Damp Cultists (React, with two appliers drafted)

**Deck:** starter plus Dahlia, Kaeya (Frostgnaw, Cryo), Sizzle, Perfect Timing,
Run Away!. **Enemies:** two Damp Cultists, 30 HP each, spike class
(placeholder pattern: Chant, then Strike 11).

**Turn 1.** Hand: Kaeya, Pop!, Kaboom!, Duck and Cover, Sizzle. Kaeya on
Cultist A: 6 damage and Cryo. Pop! on Cultist A: bomb 5. Now the choice:
Sizzle A now (*Set off*): the 5 goes off, Melts into 8, then 8 plus 6 for the
aura, total 22, Cultist A to 2, one Spark. Or Duck and Cover, and next turn
the bomb is 7 and Melts into 12. The aura lasts two of her turns, so waiting
is legal. She cashes now, because Cultist A at 2 dies to anything and the
Strike 11 is coming from both. React's "wait a turn" is often wrong on turn
one and right on turn three.

**Turn 3.** Cultist A died on turn two; a Mine it carried from a drafted Mine
Toss jumped to Cultist B at 4. Cultist B 30 HP, bombs 6 and 4 on it. Hand:
Dahlia, Perfect Timing, Kaboom!, Run Away!, Duck and Cover. Incoming Strike
11. Dahlia: 6 and Hydro. Perfect Timing (*Set off*): the 6 goes off first and
Vaporizes into 9, then the 4, then 8, and Perfect Timing's rider fires
because a reaction happened, so it plays again: another 8 on a fresh Pyro
aura, no second reaction. Cultist B to 0 from 30. Run Away! for 6 out of
habit. Fight over on turn three, and the whole thing was a sequence:
applier, then *Set off*, with the bomb in between.

## 12. Defaults taken, and the things that are genuinely yours

Under the ladder I have taken every default below and will build on it. You
veto on sight; a veto is one line.

**Defaults taken (Claude's):** growth 2 per turn; explosions one at a time,
before the rest of the card; one Spark per explosion; Spark cost as a badge;
the starter in §8; Grounded at Uncommon, Run Away! and Sorry, Jean... at
Common; Hide and Seek (Block per Bomb on the board) **dropped** as
off-lore, kept only if you want it back; Sparks 'n' Splash as a draftable
Rare Power once the shared Burst meter retires; every number is a sim
starting point and none is a design pick.

**Yours, numbered, with the default I will build on unless you say
otherwise:**

1. **What makes a Bomb go off.** (1) *Only cards that say Set off, plus a
   Mine answering an attack on her* [default; answers your note 2]. (2)
   Every Attack sets off, with printed exceptions ("does not set off"). (3)
   A fuse: bombs also go off by themselves after three turns.
2. **Mines.** (1) *In the kit, as a Bomb variant: it also goes off when its
   enemy attacks her, before the hit* [default]. (2) Mines go off when
   attacked but only Weaken the attack, never pre-empt it. (3) No Mines;
   Jumpy Dumpty just plants.
3. **Jump on death.** (1) *A Bomb whose enemy is dead jumps at full size*
   [default; answers your note 1]. (2) Jumps and resets to base. (3) Lost.
4. **The survival set.** (1) *Grounded, Run Away!, Sorry, Jean..., Mines, and
   babysitter Personals, as in §6* [default]. (2) The same plus Hide and Seek
   back at Uncommon, reframed as "the enemies are busy with the bombs". (3)
   Something else you have in mind; this is the pick where your own paragraph
   is worth more than my options.
5. **Keyword budget (a LAW question).** She would print *Bomb*, *Spark*, *Set
   off* and *Mine*. The card-sheet rule allows two new keywords per
   character. (1) *Fold Set off into Bomb's tooltip and print Mine as rider
   text ("also goes off when its enemy attacks you"), staying at two*
   [default]. (2) Log the amendment for a third keyword with compensating
   cuts. (3) Make all four keywords and amend the rule.
6. **Two companion paths (§7).** (1) *Yes: six Personals, three per path.
   Grown-ups: Diona, Noelle, Kaeya. Coven: Prune (re-authored with the
   element-absorbing Swirl), Sayu, Yaoyao. Razor and Amber return to the
   Universal pool. R234 P5 moves to "three to six, in two named paths"*
   [default]. (2) One path only, the grown-ups, at three. (3) Both paths at
   two each, four total, inside the current P5 range. Underneath it, **R234
   P5a** (may a Rare Personal exist) now has a concrete reason to be
   answered on both sides: Albedo and Jean for the grown-ups, Alice herself
   for the coven.
7. **The React loop and the law.** (1) *Companion-fed, as the law stands*
   [default]. (2) Give Klee one own-kit off-element source, a LAW amendment.
8. **The scaling cap in LAW.** (1) *Strike "A2 ≤ 4.0, scaling never tops
   frontload"; her identity is the cook-or-cash tension, not a statline* [my
   recommendation; a LAW amendment]. (2) Keep it, which caps a cooked bomb.
9. **Bomb count and growth.** (1) *Each Bomb grows separately, so three small
   bombs on one enemy cook three times as fast as one big one* [default; it is
   why Careful Arrangement and Bombs Away! are interesting]. (2) Per enemy.

## 13. What this document does not do

It does not author the 75-card sheet, price a single card, or claim a
winrate. It does not decide the Dodoco relic (a candidate: she starts each
combat with a Bomb 3 already planted on a random enemy, so the plan is
always on the table; character-relic tier, after the sheet). It does not
touch Kokomi, whose brief is next, or settle the companion layer beyond
Klee's own Personals. Nothing here is a ruling.

## 14. What the calibration changed (draft 1 → draft 2)

The Ironclad exercise found the format sound and five of its lines missing.
Each became an edit: borrowed systems made explicit (an explosion is an
ordinary Pyro hit); one rule-breaking Rare per loop; the weakness placed on
the draft screen and the map; what the relic pays for; currencies crossing
into cards and energy. The promise, verbs, rules, loops, starter, failure
modes, three-board test and scripts all stood.

## 15. What your three notes changed (draft 2 → draft 3)

1. **The contradiction (your note 1).** Draft 2 said explosions resolve before
   the Attack *and* that bombs jump when the enemy dies, which could never
   both matter. Draft 3 makes explosions resolve **one at a time** and makes
   Jump apply to *a Bomb whose enemy is already dead*: the second of three
   bombs kills, the third jumps; a partner or a poison kills, all of them
   jump. Both rules now have a case.
2. **Auto-detonation and co-op (your note 2).** Draft 2 let any Attack set
   off bombs, so cooking meant not attacking and a partner could cash her
   board. Draft 3 makes *Set off* a printed card action. Plain Attacks, a
   partner's Attacks, and companions' Attacks leave bombs alone. Cook gets
   pressure cards (Fish-Flavored Bait, Pocket Fireworks); Spray's Spark
   Attacks all print *Set off*; co-op cannot detonate her. The Cook Rare
   changed from "your Attacks no longer set off" (now the default) to
   Alice's Recipe (growth doubles).
3. **The lore audit and the squishiness question (your note 3).** §2 is the
   audit. The survival answer moved off "bombs are her shield" onto four
   things from her story, each keyed to the cook-or-cash decision: Mines
   (Jumpy Dumpty's mines explode on contact), Grounded (Jean's confinement:
   behave and you are safe), Run Away! (her title, *Fleeing Sunlight*), and
   Sorry, Jean... (confiscation). Her friends became her Personal Companions'
   identity. Hide and Seek was dropped.
4. **Bombmaxxing as the starter's plan (your framing).** §1 and §8 now say it
   in those words, script A teaches it, and the loops are branches off it.

What an A looks like, so we can check the next draft against it: a moment
per loop that only Klee can produce (a Mine killing an attacker mid-swing; a
cooked 28 Vaporizing; a chain that does not end); a decision no other
character asks (which bomb, and when); a survival answer that is hers and
not a shield; and a starter whose plan is obvious and whose branches are
visible on the first reward screen. Draft 3 claims the first three. The
fourth is the sheet's job.

## 16. Draft 3 → draft 4: the picks taken, and the coven

**Picks ruled on draft 3:** 1 to 4 at their defaults; 5 ruled as "raise the
keyword limit as high as needed to keep card text down" (a LAW amendment,
yours, now made: *Bomb*, *Spark*, *Set off*, *Mine* all print as keywords);
7 to 9 at their defaults, with your note that a plain Pyro hit is a weak
reaction payoff because Klee's own Pyro has already eaten the aura.

**Pick 6 re-posed.** You asked for the Little Hexenzirkel lore first. §7 is
rewritten on it: two paths, the grown-ups and the coven, three Personals
each. The coven path is also the answer to your Pyro note: Prune's Swirl
converts the next explosion to the Swirled element, so Klee's ubiquitous
Pyro becomes the aura the bomb reacts with rather than the thing that eats
it. Off-element bombs arrive through a companion, exactly as you suggested,
and the law on earned reactions does not move.

**Lore sources for draft 4:** genshin.gg and GameWith for the kits (Klee's
Hexerei passive, Prune's absorbing hammer), game8 and the Phantasmal Pals
event guides for the Little Hexenzirkel's founding, members and imaginary
friends. The fandom wiki refuses automated reads, so its pages are cited by
name only.
