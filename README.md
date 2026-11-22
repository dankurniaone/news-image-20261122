# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/dankurniaone/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/dankurniaone/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

The World in One Day — a one-image summary of the world's news of Sunday 22 November 2026, entered in make.fun's `news-image-20261122` bounty. The entry is a light-paper broadsheet, a single 680×1024 PNG rendered at 2× and downscaled: a Hong Kong election lead with a real skyline photograph owns the top of the page, Israel's government talks and the COP31 deadlock share the middle with real photographs, and three briefs carry the day's other fragments.

Bounty: https://make.fun/bounty/news-image-20261122 — referral: https://make.fun/r/adyjn11j

## What's on the page

- **Lead — Hong Kong votes.** Polls open at 9am in the Election Committee Subsector Ordinary Elections: 856 candidates contest 723 seats across 31 subsectors, and about 5,700 voters choose the 1,500-member committee that nominates and elects the chief executive. Shown with a real photograph of Hong Kong's skyline.
- **Israel — Eisenkot begins his bid.** Former army chief Gadi Eisenkot starts intensive coalition talks with Likud after President Isaac Herzog asked him — not Benjamin Netanyahu — to form the next government; the mandate handover takes place today. Shown with a real photograph of the Knesset.
- **Climate — COP31 deadlocked.** Talks in Antalya run past their deadline with no deal, stalled over fossil fuels after a draft stripped out every mention of them; a third draft is promised for this morning. Shown with a real photograph of wind turbines.
- **Briefs.** A magnitude 4.1 earthquake strikes Myanmar in the early hours · the 61st Venice Art Biennale closes after six months · the Nitto ATP Finals reach their final day in Turin.

## How it was made

`tools/render.py` draws the whole broadsheet in Pillow — masthead, headlines, columns, briefs strip, footer — pastes in the three photographs, and renders at 2× (1360×2048) before a LANCZOS downscale to 680×1024, so the small type stays crisp. `main.ts` validates `entry.png` (PNG signature, 680×1024, at most 1 MiB, whole file ending in IEND), copies it to `MAKEFUN_OUTPUT_DIR`, and verifies the copy byte-for-byte with a SHA-256 check.

## Photos

The three photographs are freely-licensed CC file photos from Flickr, credited here; none is a picture from 22 November itself, and the page says so in its footer:

- Hong Kong's skyline at morning — Portland Seminary, CC BY-SA (https://www.flickr.com/photos/104951964@N06/21643479918)
- The Knesset, Jerusalem — leighklotz, CC BY (https://www.flickr.com/photos/leighklotz/20443069095)
- Wind turbines, Southern Sweden — sludgegulper, CC BY-SA (https://www.flickr.com/photos/sludgegulper/5396636080)

News copy is sourced from the Hong Kong Registration and Electoral Office, China Daily Asia, Times of Israel, BBC and National Centre for Seismology reporting of 22 November 2026 (see the footer on the page). Every story on the page is an event of Sunday 22 November 2026 itself — the Hong Kong polls open at 9am today, Eisenkot's mandate ceremony and coalition talks begin today, the COP31 talks run into overtime today, the Myanmar quake struck in the early hours of today, and the Biennale and the ATP Finals reach their final day today. Stories from earlier in the weekend were checked and left out because their events fall on 20–21 November, not today.

## Run it

```sh
python3 tools/render.py        # rebuild entry.png (680x1024)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out npx --yes tsx main.ts
```
