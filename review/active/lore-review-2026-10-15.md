# Lore review: Furina, Klee and Varka card names (2026-10-15)

**Why.** [USER], 2026-10-15: "a lore review to make sure her cards are not too
generic-sounding and are accurate to her (actually, I think we should do Klee
and Varka as well - Klee's is mostly fresh, but Varka hasn't been swept in
awhile)". Packets: scratch `lore-review/{furina,klee,varka}.md` (every row of
`docs/prototype-surface.yaml`, matched against the repo's lore sources).

**What was checked.** Card names only: the cards carry rules text and no
flavour. A name passes if it is a canon name, names a real person, place or
thing from the character's story, or is a plain word that fits her or his
voice. It fails if it is generic (it could sit on any kit) or collides with
another kit's vocabulary. Klee and Varka are at Balance; a rename is a text
change and may land on main.

## 1. Varka: the weakest of the three

7 of 88 names are canon (Four Winds' Ascension, Northwind Avatar, Dawn Wind's
March, Azure Devour, Grand Master's Order, Grand Master's Verdict, Tempest of
the Four Winds), plus his Knight cards. About half the rest are weather words
any Anemo kit could print (Wall of Gales, Storm Surge, Tailwind Stride,
Weathervane, Downburst, Eye Wall). His story has hooks the pool never uses:
his title Knight of Boreas (he is the Wolf of the North among the Four
Winds), his Oath's own name, the wolves (Razor, his adopted
son), the friend he lost (Crepus), the bards' tales he grew up wanting to be
in, and the desk work he leaves to Jean.

| Today | Text (short) | New name | Hook |
|---|---|---|---|
| Sworn Brotherhood (R Power) | gain Oath each turn | **Knight of Boreas** | his title |
| Oath Unto Death (R Power) | each Oath gain is +1 | **Azure Fang's Oath** | his passive's stack, the name of his Oath |
| Wolfpack (R Power) | Four Winds' Ascension shuffles a copy back | **Lupical** | Razor's word for family |
| Thundering Verdict (R Attack) | X-times Electro to ALL | **Lightning Fang** | Razor's Burst; also stops two "Verdict"s in his pool |
| Dawn Patrol (U Skill) | gain Energy, draw | **Leave It for Jean** | he dodges paperwork |
| Tailwind Stride (U Skill) | draw | **A Bard's Tale** | the hero tales he grew up on |
| Ashen Oath (U Power) | Strength and Pyro Oath | **For Crepus** | his old friend, Diluc's father |

Left as they are: the Knight cards ("Name: Move"), Eye of Stormterror (Dvalin),
Assembly at the Cathedral, Charge of the Knights, and the element words on his
element cards (Deep Freeze, Icebreaker, Static Field), which read as the
element, not as filler.

## 2. Furina: mostly good, five generic water names

Her names are theatre words (Encore!, Tutti!, Bravura, Prima Donna, Full
House) and canon (Salon Solitaire, the three Salon members, Singer of Many
Waters, Universal Revelry, Let the People Rejoice, Ousia / Pneuma, Arkhe in
Balance, Verdict of the Oratrice, A Five-Century Act). Theatre words are her
voice and pass. The misses are the water words, which belong to Kokomi
(Riptide, Undercurrent Snare and seven "Tide" cards are hers):

| Today | Text (short) | New name | Hook |
|---|---|---|---|
| Crashing Waves (C Attack) | hit twice, Spend for more hits | **Soloist's Solicitation** | her normal attack |
| Rising Tide (U Attack) | damage per Repay this turn | **Endless Waltz** | her passive: healing past full heals the party |
| Undercurrent (C Attack) | Drain 2, grows per Drain this combat | **Unheard Confession** | her other passive; the cost nobody saw |
| Riptide Lunge (U Attack) | Drain 3, 10 damage, Repay 6 on a kill | **Coup de Théâtre** | the twist that pays you back |
| Against the Tide (U Attack) | more damage if you Drained | **Against All Odds** | drops the Kokomi word, keeps the meaning |

**A clash this review found:** her Rare Plot Twist shares its name with a card
in the Yae pool paper (#1338). Yae's becomes **Genre Shift**; Furina keeps
Plot Twist.

## 3. Klee: no renames

Her names were swept on 2026-10-01 and read in her voice (Run Away!, Klee Can
Explain!, Behind Jean's Desk, Dodoco Tag) or are canon (Jumpy Dumpty, Sparks
'n' Splash, Chained Reactions, Explosive Frags, Exquisite Compound, Blazing
Delight, All of My Treasures!, Sparkling Burst). One question: her basic
**Ka-pow!** replaced her normal attack's canon name, **Kaboom!**, and nothing
in the repo records why. Canon names still unused, if a future card wants
one: Pounding Surprise, Sparkly Explosion, Nova Burst, Dodoco Tales.

## 4. What is not checked

The repo holds no verified lore census for Furina (or Yae), and Varka's rests
on secondary web pages. The new names above, the Furina story (#1339) and the
Yae paper's Ioroi and Eternal Promise readings are from memory or those
sources.

## Picks

1. **Varka's renames** (sec.1).
   - **(a) Default:** all of them.
   - (b) You name the ones to keep.
2. **Furina's five renames** (sec.2).
   - **(a) Default:** all five.
   - (b) You name the ones to keep.
3. **Klee's basic.**
   - **(a) Default:** keep Ka-pow!.
   - (b) Back to Kaboom!.
4. **A lore check before the Workshop release.**
   - **(a) Default:** one sourced census each for Furina and Yae, like
     Varka's, then every story line and name in sec.4 checked against it and
     the Varka census, with anything unconfirmed changed or cut.
   - (b) Ship on what we have.

## Ruled 2026-10-15

[USER]: "Varka is the current Wolf of the North; the current Lion of the South
is Jean. Otherwise these all make sense." So Sworn Brotherhood becomes Knight
of Boreas and Boreas Unbound keeps its name; the other Varka and all five
Furina renames stand (picks 1 and 2 (a)). The Varka census's Four Winds line
is corrected.

Pick 3 (b): "I think that at one point, Kaboom! was in use for something else;
we can rename that now." Ka-pow! becomes Kaboom! (the old Kaboom! card was
deleted; `docs/prototype-surface.yaml` header).

Pick 4 (a): "I'd say yes - let's build a lore source for the others."
