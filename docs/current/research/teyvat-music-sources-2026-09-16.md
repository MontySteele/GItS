Status: RESEARCH (sources survey; nothing downloaded)

# Where Genshin's music actually lives, and what the terms say

Written 2026-09-16 for the Teyvat run frame's music layer
(`review/ruled/teyvat-run-frame-2026-09-14.md` §1.4: official tracks as locally
packaged placeholders, a copyright pass owed before anything is public). The
job here is to make that pass a lookup: every row in `media/MUSIC.tsv` needs an
`origin` and a `licence`, and this page says what can honestly go in those two
columns. **Nothing was downloaded and no fetch script was run.** All URLs were
checked 2026-09-16 unless a line says otherwise.

## 1. The official releases: streams, not files

HOYO-MiX publishes one large "Chapter" album per nation. Every one of them is
on Spotify, Apple Music and the official Genshin Impact YouTube channel, and
each ships as a small number of **discs whose names are already scene labels** —
that is the single most useful fact on this page, because the last disc of
every album is the combat disc.

| nation | album | released | discs (official YouTube upload) |
|---|---|---|---|
| Mondstadt | City of Winds and Idylls | 2020-09-28 | City of Winds and Idylls / The Horizon of Dandelion / Saga of the West Wind |
| Liyue | Jade Moon Upon a Sea of Clouds | 2020-11-06 | [Glazed Moon Over the Tides](https://www.youtube.com/watch?v=t1O7LpOTBfM) / [Shimmering Sea of Clouds and Moonlight](https://www.youtube.com/watch?v=c0jZ7sPyouE) / [**Battles of Liyue**](https://www.youtube.com/watch?v=keeqPGo-JZ4) |
| Inazuma | Realm of Tranquil Eternity | 2021-09-22 | Sakura and Violet Thunder / Stories of the Floating World / **Battles of Inazuma** |
| Sumeru | Forest of Jnana and Vidya | 2022-10-20 | [Dwelling Where Everlasting Spring Abides](https://www.youtube.com/watch?v=nR6Ncfdp4AU) / [Woods, Rivers and Mysteries](https://www.youtube.com/watch?v=6xMH6YGYBhc) / [Eternal Antagonism Between Life and Death](https://www.youtube.com/watch?v=FjXil_kWhHM) / [**Battles of Sumeru**](https://www.youtube.com/watch?v=skTz0aOisVs) |
| Fontaine | Fountain of Belleau | 2023-10-02 | [Chanson of Justice and Impartiality](https://www.youtube.com/watch?v=znHhRYBmfck) / [Arioso of Belle Epoque](https://www.youtube.com/watch?v=gwGOp351clk) / [Chapelloise of Trickling Springs](https://www.youtube.com/watch?v=xZSDdaYjV_c) / [**La bataille de Fontaine**](https://www.youtube.com/watch?v=xUcJtXtLb_I) |
| Natlan | Land of Tleyaoyotl | 2024-10-05 | [Altar of Ardor Ablaze](https://www.youtube.com/watch?v=m1KlMecTFuw) / [Saurian-Scorched Soil of Strife](https://www.youtube.com/watch?v=m9X-nDUVQvI) / [**Battles of Natlan**](https://www.youtube.com/watch?v=zdqCyJcT6iU) |

Album counts and dates are from [Music of Genshin Impact](https://en.wikipedia.org/wiki/Music_of_Genshin_Impact)
cross-checked against each album's own Fandom page; Mondstadt is 63 tracks,
Liyue 69, Inazuma 62, Sumeru 100, Fontaine 96, Natlan 78. Side series that also
matter: **The Shimmering Voyage** (story and battle music, vols 1-5, 2021-07
through 2025-08), **The Stellar Moments** (character themes, vols 1-6, through
2026-01), **Footprints of the Traveler** (version-trailer music, vols 1-4).
Nod-Krai's album is **Song of the Welkin Moon** (Version Luna I, 2025-09-10) —
worth noting because R273 scores Nod-Krai as a later act face.

Streaming homes, as examples of the pattern that holds for all six:
[City of Winds and Idylls on Apple Music](https://music.apple.com/us/album/genshin-impact-city-of-winds-and-idylls-original/1535605650)
(copyright line "℗ 2020 miHoYo"),
[on Spotify](https://open.spotify.com/album/4B5efqHkeq0UaDGx8nYOuf),
[Fountain of Belleau on Spotify](https://open.spotify.com/album/4UwFbGhMZA4LZqqAnt8LCB),
[Land of Tleyaoyotl on Apple Music](https://music.apple.com/us/album/genshin-impact-land-of-tleyaoyotl-original-game/1770034466).

**No official channel hands over a file.** Spotify, YouTube and TIDAL are
stream-only; Apple Music's page says the album is "also available in the iTunes
Store", which is a paid AAC purchase, not a lossless or OGG download; there is
no HoYoverse Bandcamp and no download link on `genshin.hoyoverse.com` (its OST
news posts, e.g. [the Sumeru OST MV post](https://genshin.hoyoverse.com/en/news/detail/23856),
embed video only). Physical CD box sets exist for Mondstadt, Liyue and Inazuma
and are sold through resellers — a CD is a file source, but a slow and paid one.

## 2. What HoYoverse actually permits

The operative sentence is short and it is the whole rule. HoYoverse's help
centre article **"Can I use in-game music for my fan-made content?"**
([support.hoyoverse.com article 50333834244633](https://support.hoyoverse.com/hc/en-us/articles/50333834244633-Can-I-use-in-game-music-for-my-fan-made-content),
read 2026-09-16 through the help-centre JSON API because the HTML page 403s to
automated fetches) says HoYoverse's in-game music is **"limited to personal,
non-commercial use"** and points to the official Legal FAQ for detail. The
companion article
["What are the guidelines for creating and selling fan-made content?"](https://support.hoyoverse.com/hc/en-us/articles/51005649400729-What-are-the-guidelines-for-creating-and-selling-fan-made-content)
covers the selling side; the Legal FAQ is mirrored on HoYoLAB at
[hoyolab.com/article/143107](https://www.hoyolab.com/article/143107).

The fan-creation guidelines that news coverage quotes at length
([Kotaku](https://kotaku.com/genshin-impact-embraces-fan-creators-rather-than-suing-1847714438),
[Siliconera](https://www.siliconera.com/mihoyo-lists-rules-on-overseas-genshin-impact-fan-made-merchandise/),
[HoYoLAB merchandising guide](https://www.hoyolab.com/article/381519)) are
generous about derivative works — doujinshi, illustrations, small runs — on
three conditions that read straight across to a mod: it must not be sold beyond
the stated limits without authorisation, it must not present itself as
official, and the creator may not claim copyright in the result.

**The distinction the terms do not draw explicitly, and which matters here:**
nothing in the published text separates *streaming a track*, *embedding it in a
downloadable mod*, and *redistributing the audio*. "Personal, non-commercial
use" plainly covers a private build the owner plays. A public download that
carries the audio files is redistribution of miHoYo's recordings under any
reading, and no published HoYoverse page grants it. That is exactly the gap the
`PLACEHOLDER-COPYRIGHTED` licence value and the pre-public grep in
`operations/media.md` §2 exist to hold shut — this survey found nothing that
would let a row move off that value.

## 3. Where the actual files are

**The owner's own game install is the best source, and it needs no third
party.** Genshin ships its audio as Wwise packages under
`GenshinImpact_Data/StreamingAssets/Audio/GeneratedSoundBanks/Windows`, and a
family of open-source extractors unpacks them. The relevant point for us:
[GenshinAudioExtractor](https://github.com/WRtux/GenshinAudioExtractor) converts
the Vorbis-encoded entries **straight to `.ogg`** — which is precisely
`media/MUSIC.tsv`'s default format, no re-encode, no quality loss. Peers:
[genshin-audio-exporter](https://github.com/dvingerh/genshin-audio-exporter)
(picks `.pck` files from the game directory, exports to several formats),
[MeguminSama/genshin-audio-extractor](https://github.com/MeguminSama/genshin-audio-extractor)
(to `.wav`), [AnimeWwise](https://github.com/Escartem/AnimeWwise) (fast, keeps
original filenames and paths — the one to prefer if track identity matters for
the `title` column), and the several `Genshin-Impact-New-Music-Unpacker` forks.
These are extraction tools, not cracks and not torrents; they operate on files
the owner already has. They change nothing about clause 2 — an extracted file is
still miHoYo's recording — but they make the *provenance* column honest and
exact, and they avoid a third-party mirror entirely.

**Genshin Impact Fandom wiki.** It has per-region soundtrack pages
([Liyue](https://genshin-impact.fandom.com/wiki/Liyue_(Soundtrack)),
[Inazuma](https://genshin-impact.fandom.com/wiki/Inazuma_(Soundtrack)),
[Natlan](https://genshin-impact.fandom.com/wiki/Natlan_(Soundtrack))), per-album
pages, and a [Category:Soundtrack Files](https://genshin-impact.fandom.com/wiki/Category:Soundtrack_Files)
alongside [Category:Audio](https://genshin-impact.fandom.com/wiki/Category:Audio).
Search results and the wiki's own [Talk:Soundtrack](https://genshin-impact.fandom.com/wiki/Talk:Soundtrack)
indicate it keeps `.ogg` files per track beside the Spotify and YouTube links —
the same shape as its card art, which the art pipeline already draws on. **I
could not confirm this eyes-on:** every `fandom.com` fetch from this session
returned HTTP 402, so the file hosting is reported, not verified. Fandom's terms
are CC-BY-SA for text, but that licence never covers a copyrighted game asset
uploaded under fair use; a wiki `.ogg` is the same miHoYo recording with a
convenient filename. Its real value is the **`title` column** — the wiki's file
titles are the source's own names, which is what `operations/media.md` §2 asks
for.

**archive.org.** At least two public items hold the audio:
[genshin-impact-music-collection](https://archive.org/details/genshin-impact-music-collection)
(public 2024-06-19, ~78 VBR MP3s covering The Wind and The Star Traveler, City
of Winds and Idylls and Jade Moon) and
[genshin-impact-ost-flac-jade-moon-upon-a-sea-of-clouds](https://archive.org/details/genshin-impact-ost-flac-jade-moon-upon-a-sea-of-clouds)
(FLAC plus MP3 derivatives, 49 tracks). Neither item carries a `licenseurl` or
any rights statement in its metadata — they are user uploads of a copyrighted
commercial album, retrievable in practice and unlicensed in fact. Cite one as
`origin` if that is genuinely where a file came from; it cannot move `licence`.

**KHInsider** ([downloads.khinsider.com](https://downloads.khinsider.com/game-soundtracks/publisher/mihoyo))
carries every album in MP3 and FLAC with per-track download —
e.g. [Realm of Tranquil Eternity](https://downloads.khinsider.com/game-soundtracks/album/genshin-impact-realm-of-tranquil-eternity)
(MP3 236 MB, FLAC 1,123 MB),
[City of Winds and Idylls](https://downloads.khinsider.com/game-soundtracks/album/genshin-impact-city-of-winds-and-idylls-original-soundtrack)
(MP3 208 MB, FLAC 516 MB),
[Land of Tleyaoyotl](https://downloads.khinsider.com/game-soundtracks/album/genshin-impact-land-of-tleyaoyotl-original-game-soundtrack-2024)
(MP3 258 MB, FLAC 1,500 MB). The site publishes **no rights statement or
licence of any kind** on its album pages. Treat it as a track-name reference —
it is the only place in this survey with clean, complete, machine-readable
tracklists — not as a licence.

## 4. Nation to scene: which tracks fit which slot

Slot names are ours (`map`, `rest`, `shop`, combat, `boss` — the `scene` column
in `media/MUSIC.tsv`). Track names below are verified against KHInsider
tracklists and the official disc uploads; the **disc** is the reliable mapping
and the individual titles are a starting shortlist, not a ruling.

| nation (act face) | map / exploration | rest / shop | combat | boss |
|---|---|---|---|---|
| **Mondstadt** (act 1) | Twilight Serenity; Whispering Plain; Beckoning | Windborne Hymn; Another Day in Mondstadt; Dawn Winery Theme | Perilous Path; Slight Distress; Say My Name | Forlorn Child of Archaic Winds; Whirl of Boreal Wind; Symphony of Boreal Wind |
| **Liyue** (act 1) | disc 1 *Glazed Moon Over the Tides* | disc 2 *Shimmering Sea of Clouds and Moonlight* | disc 3 *Battles of Liyue* | disc 3 *Battles of Liyue*, closing tracks |
| **Natlan** (act 2) | disc 1 *Altar of Ardor Ablaze* | disc 2 *Saurian-Scorched Soil of Strife* | disc 3 *Battles of Natlan* | disc 3 *Battles of Natlan* |
| **Inazuma** (act 2) | Inazuma; Fall of Maples; Lingering Blossom | Where the Heart Settles; Miko's Night; Streets of Elegance | Samurai's Sorrow; Fiery Pursuit | Duel in the Mist; Against the Invisible Net; Overlord of the Thunderstorm |
| **Fontaine** (act 3) | disc 2 *Arioso of Belle Epoque* | disc 3 *Chapelloise of Trickling Springs* | disc 4 *La bataille de Fontaine* | disc 4 *La bataille de Fontaine* |
| **Sumeru** (act 3) | disc 2 *Woods, Rivers and Mysteries* | disc 1 *Dwelling Where Everlasting Spring Abides* | disc 4 *Battles of Sumeru* | disc 3 *Eternal Antagonism Between Life and Death* |

Mondstadt and Inazuma are named down to the track because their full tracklists
fetched cleanly; the other four are given at disc level for the same reason the
whole section is honest about — the disc is what I could verify. Filling the
remaining four to track level is a twenty-minute pass on the KHInsider album
pages, done once and written into the ledger's `title` column.

On **trailers and PVs**: every Version PV, Story Teaser and character demo on
the [official Genshin Impact YouTube channel](https://www.youtube.com/@GenshinImpact)
scores its region with music that later appears on the Chapter album or on
*Footprints of the Traveler*, and the OST preview MVs (e.g.
[Sumeru's](https://www.youtube.com/watch?v=NfbT1Rgos4I),
[the promotional MV](https://www.youtube.com/watch?v=zQBrgGjwCPM)) are the
official showcase for each album. They are useful for **choosing** a track — a
90-second PV tells you in one listen whether a theme carries a map screen — and
useless for **obtaining** one: a trailer's audio is mixed under voice and sound
effects, and YouTube is stream-only regardless.

## What the owner can do with this

**(a) Stream-only — for choosing, never for filling `media/raw/`.** Spotify,
Apple Music, TIDAL, the official YouTube channel and all the PV/MV uploads.
These settle *which* track goes in which scene and they give the authoritative
spelling of a track's name for the `title` column. No file comes out of them.

**(b) Sources that produce a file the ledger can cite.** In order of
preference:

1. **Extract from the owner's own installed copy** with
   [GenshinAudioExtractor](https://github.com/WRtux/GenshinAudioExtractor) or
   [AnimeWwise](https://github.com/Escartem/AnimeWwise). Native OGG Vorbis, no
   re-encode, no third party, and `origin` can name the game build honestly.
   This is the recommendation.
2. **KHInsider** — MP3 or FLAC per track, complete tracklists, fastest route to
   a full six-nation set, no stated licence.
3. **archive.org** — MP3 and one FLAC album, no rights metadata.
4. **Fandom wiki `.ogg` per track** — probably the cleanest per-track filenames,
   *unverified* (402 on every fetch) and worth one eyes-on check.
5. **The physical CD box sets** — paid, slow, and the only route where the owner
   holds a licensed copy in his hand.

Whichever route: the `licence` column stays **`PLACEHOLDER-COPYRIGHTED`** on
every one of these rows. None of them is a licence.

**(c) The terms, private build versus public build.** A private friends-only
mod whose audio the owner packages himself, never commits, and never sells sits
inside "personal, non-commercial use" as HoYoverse states it — which is exactly
the posture R272 §1.4 records, and exactly what `media/raw/` being gitignored
enforces. A **public** build is a different act: shipping a package that
contains miHoYo's recordings is redistribution, it is not covered by any
published HoYoverse permission, and `grep PLACEHOLDER-COPYRIGHTED media/*.tsv`
returning any row is the correct block. Going public therefore has exactly two
honest routes, and they are a later decision, not this page's: replace each
placeholder with an `ORIGINAL` or `CC-BY-*` track and change the column, or ship
the code with no audio and let each player point the mod at his own extracted
files — the same shape the repo already uses for `game_ref/`.

**Not verified, and flagged as such:** whether the Fandom wiki hosts per-track
`.ogg` (Fandom 402s to automated fetches throughout); the exact text of the two
HoYoverse help-centre HTML pages beyond the one operative sentence recovered
through the JSON API; whether any Legal FAQ clause draws the
stream/embed/redistribute distinction, since the HoYoLAB mirror renders only
client-side; and track-level scene mapping for Liyue, Natlan, Fontaine and
Sumeru, given at disc level instead.
