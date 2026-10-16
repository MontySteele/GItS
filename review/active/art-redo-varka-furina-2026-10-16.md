# Art redo: Varka and Furina (2026-10-16)

**Why.** [USER]: "I don't remember the last time we did an art pass over Klee,
Varka or Furina looking at the actual art ... can we do a run over Varka and
Furina and assess the general quality of all the current picks an whether we
want any redos?" Every current card picture for both kits was looked at. The
rows below had a real defect (logo or text, a duplicate of another card, a tiny
upscaled icon, a screenshot), and Claude chose a replacement for each from a
sheet of the actual crops. This PR changes `art/plan.tsv` (the rank-1 row of
each card, which is the picture that ships) and the matching
`art/SOURCES.tsv` lines. All 31 crops come from the Genshin Impact fandom wiki
(official art).

## The swaps

| Card | Problem | New picture (wiki file) |
|---|---|---|
| Curtain Rise | wish banner with text; same image as Singer | Soloist's Prologue Computer Graphic.png |
| Singer of Many Waters | same image as Curtain Rise | Marechaussee Hunter Judgment Day Furina Marechaussee Hunter.png |
| Mademoiselle Crabaletta | GIF frame, tiny figure on flat green | Item Crab Ocean.png |
| Bis! | big GENSHIN IMPACT logo; near-copy of The Show Must Go On | The Two Musketeers' Triumph Quest Still 1 Lumine.png |
| The Show Must Go On | same file as All the World's a Stage | Version 4.1 Full Wallpaper 1.png |
| Crowd Favorite | same file as Ensemble Cast | Version 4.1 Full Wallpaper 3.jpg |
| Bubble Aria | same arms-out pose as three other cards | Splashscreen Romaritime Meluserenity Chanson of Many Waters.png |
| Crescendo | same arms-out pose as three other cards | Version 4.2 Special Program Coming Soon.png |
| Ebb and Flow | same scene as Clean Slate | Fontaine.png |
| Tidal Flourish | same scene as Clean Slate | Splashscreen Chanson of Many Waters Tempestuous Destiny.png |
| Final Bow | same chibi as Velvet Curtain | This Life, Just Like a Light Trickle of Song Still 1 Aether.png |
| Neuvillette: Sourcewater Droplets | same wish art as Guest Star: Neuvillette | App Store Event Character Wallpaper Neuvillette Version 4.1.png |
| Neuvillette: Equitable Judgment | same wish art as Guest Star: Neuvillette | Version 4.1 Wallpaper 2.png (see note 1) |
| Plot Twist | comic panel with red arrows | Apocalypse Still 2.png |
| Pneuma Refrain | headless body crop | Character Furina Game (Pneuma).png, recropped on head and shoulders |
| Arkhe in Balance | side-by-side screenshot | Coronated Prima Donna Ousia Turnaround.png |
| Coup de Théâtre | on-hit effect screenshot | Weapon Splendor of Tranquil Waters Ousia.png |
| Surintendante Chevalmarin | small upscaled item icon | Ride the Waves to a Rendezvous in Fontaine Bubbler Seahorse Concept Art.png |
| Oathbound Aegis | 115 px icon upscaled | Swords of the Grand Masters.png |
| Wildfire Oath | framed item icon upscaled | Red Dead of Night Preview.png |
| Vow of the Blade | upscaled head icon | Ready for Battle Varka Preview.png |
| A Bard's Tale | chibi emoji upscaled | Venti Birthday 2025.png |
| Knights' Roll Call | chibi emoji upscaled | Mondstadt Tourism Revitalization Project Wallpaper.png |
| Unwavering Banner | flat emblem upscaled | Namecard Background Mondstadt Hero's Fame.png |
| Converging Winds | same art as Windward Flank, plus a logo | Global Release in 1 Day Artwork - Venti, Boreas and Dvalin.jpg |
| Knight of Boreas | same still as Charge of the Knights; shows Kaeya | NPC Wolf Knight.png |
| Frost Ward, Kindled Edge, Rippling Guard, Storm Battery | logo and white frame in the crop | same birthday art, zoomed (`x0.5,y0.52@1.35`) past the logo and frame |
| Boreas Fang (relic) | same icon as Andrius's Howl | Item Boreal Wolf's Broken Fang.png |

Notes:

1. Equitable Judgment's source has a small ©COGNOSPHERE mark at the bottom
   right. The focus is set to `x0.62,y0.47@1.06`: a 6% zoom that takes the
   crop's bottom edge to source row 1358, above the mark (rows 1390 to 1420).
2. Three of the picks come from families `tools/art_lint.py` bans by title
   (the two "Splashscreen" wish banners and the "Ride the Waves" concept-art
   page), because those files carry text or a page border. The chosen crops
   leave all of it out, so each file gets one entry in
   `APPROVED_FAMILY_EXCEPTIONS`. The families stay banned.

**Kept as they are.** Quick Flourish and Thunderous Applause: there is no
better unused official art for them.

**Preview.** One sheet per kit, old and new side by side at 300 px:
`C:\Users\Monty\AppData\Local\Temp\claude\C--Users-Monty-Documents-GitHub-GItS\3bee9add-2181-4b79-8aec-fcedf624f7ec\scratchpad\art-redo\preview-furina.png`
and `...\scratchpad\art-redo\preview-varka.png` (same folder). They are not in
git: official art stays out of the repo (`docs/current/operations/art.md`), and
`review/qa/` is gitignored.

**Other notes.**
- Furina's unused official art is nearly used up. Several candidates in this
  hunt were offered on two or three rows at once, and Quick Flourish and
  Thunderous Applause found nothing new. A later Furina redo will have very
  few official files left to choose from.
- Some of Varka's off-element cards show characters from other nations: Cyno
  on Charged Lunge, Beidou on Chain Lightning, Keqing on Static Field, Ganyu on
  Absolute Zero. They stay as they are (pick 2).

**After merge (main checkout, Git Bash).** This fetches only these rows'
sources into `art/raw`, renders them, promotes rank 1 into `ImageGen`, and
rebuilds the pck. It does not run `art_fetch.py`, so `art/SOURCES.tsv` is not
rewritten.

```sh
cd C:/Users/Monty/Documents/GitHub/GItS
IDS=proto_fs_curtain_rise,singer_of_many_waters,mademoiselle_crabaletta,proto_fs_bis,proto_fs_the_show_must_go_on,proto_fs_crowd_favorite,proto_fs_bubble_aria,proto_fs_crescendo,proto_fs_ebb_and_flow,proto_fs_tidal_flourish,proto_fs_final_bow,guest_neuvillette_droplets,guest_neuvillette_judgment,proto_fs_plot_twist,proto_fs_pneuma_refrain,proto_fs_arkhe_in_balance,proto_fs_riptide_lunge,surintendante_chevalmarin,proto_vk_oathbound_aegis,proto_vk_wildfire_oath,proto_vk_vow_of_the_blade,proto_vk_tailwind_stride,proto_vk_knights_roll_call,proto_vk_unwavering_banner,proto_vk_converging_winds,proto_vk_sworn_brotherhood,proto_vk_frost_ward,proto_vk_kindled_edge,proto_vk_rippling_guard,proto_vk_storm_battery,relic_boreas_fang
.venv/Scripts/python.exe -c "import sys,urllib.request as u;sys.path.insert(0,'tools');import art_fetch as f;ids=set(sys.argv[1].split(','));t=sorted({r['title'] for r in f.read_plan() if r['asset_id'] in ids and r['rank']==1});res=f.resolve(t);[(f.RAW/f.rawname(x)).write_bytes(u.urlopen(u.Request(res[x][0],headers=f.HEADERS),timeout=120).read()) for x in t if x in res and not (f.RAW/f.rawname(x)).exists()];print(len(res),'of',len(t),'resolved')" "$IDS"
printf '%s\t1\n' ${IDS//,/ } > "$TEMP/art-redo-picks.tsv"
.venv/Scripts/python.exe tools/art_process.py --assets "$IDS"
.venv/Scripts/python.exe tools/art_process.py --apply-picks "$TEMP/art-redo-picks.tsv"
powershell -File tools/build_pck.ps1
```

`--assets` renders every rank of these rows. A GAP line for a rank 2 or 3
whose source is not on disk does not matter: only rank 1 is promoted. Expect
"31 picks promoted".

## Picks
1. **The new art.**
   - **(a) Default:** take every swap in the table.
   - (b) Take them except the ones you name.
2. **Varka's other-nation faces.**
   - **(a) Default:** keep them; the cards are off-element by design.
   - (b) Re-pick them with Mondstadt characters where one fits.
