---
name: shortlist-crosscheck
description: Use when the user already has a shortlist — restaurants/venues, products, travel places, courses, events — and wants each item verified across platforms before deciding: does it exist as named, is it available now, what do independent ratings and community threads say, any red flags. Triggers include "交叉验证", "核实一下", "这几个靠谱吗", "帮我查查这几个", "cross-check", "verify these". Distinct from xhs-topic-digest / en-community-digest, which find and summarize content on a topic; this skill only checks a given list and stops at a ✅/⚠️/❌ screen — the final choice is the user's.
---

# Shortlist Cross-check

## Overview

A shortlist from one source (a 小红书 digest, a friend, an ad) carries that source's blind spots: stale status, promo posts, community-specific taste, wrong names. This skill checks each item on independent platforms and returns evidence plus a first-pass screen. It does **not** find candidates and does **not** pick the winner for the user's situation — situations change; the user decides.

All page access goes through **browser-use** (the user's real Chrome); 小红书 through the xiaohongshu MCP. Don't try `curl`/WebFetch first — many of these sites block them.

## Workflow

1. **Pin the list and category.** One line per item; category from the table below. Note the user's need if stated (e.g. "Saturday lunch", "in Canada") — availability is judged against it.
2. **Identity + availability — one Google search per item.** `https://www.google.com/search?q=<name + locator>`; save `document.body.innerText` to `raw/google_<slug>.txt`. The knowledge panel usually gives the canonical name, address/model, status ("Temporarily closed"), hours, Google rating + count, and third-party rating snippets. No panel → retry with a sharper locator (address, full model number), then the platform itself (e.g. `https://www.google.com/maps/search/<q>`, read `div[role=main]`, save `raw/gmaps_<slug>.txt`).
   - If the canonical name/model differs from the shortlist's (renamed, misspelt, regional variant), record both and use the canonical one from here on.
3. **Platform signals** per the category row: ratings **with platform and count**, plus recent reviews where cheap. A bare `3.2(44)` on a results page belongs to the source line *above* it — check before attributing.
4. **Community threads.** Google `"<canonical name>" site:reddit.com` and `site:forums.redflagdeals.com` (one search per site; save results to `raw/google_site_searches.json`). Read the 1–3 most relevant threads in full with the en-community-digest recipes (Reddit `.json` fetch, RFD post extraction); save to `raw/reddit_<slug>.json` / `raw/rfd_<slug>.json`. Anything known only from a search snippet is marked `snippet_only` with its age.
5. **Write outputs** (below) in the caller's topic folder.
6. **Audit** (below) — not optional.

Pace like a person: sequential, one tab, a few seconds between searches.

## Category table

| Category | Identity | Available now? | Ratings / reviews | Red flags |
|---|---|---|---|---|
| Restaurant / local business | Address, canonical Google name | Google Maps status, hours on the user's day | Google, Yelp, TripAdvisor, delivery apps, local subreddit, RFD | sponsored posts; review count growing implausibly fast for its age; dine-in vs delivery rating gap |
| Product | Full model number, regional version | In stock + price at Canadian retailers (Amazon.ca, Costco, Best Buy, RFD price threads) | Amazon, RFD, Reddit, expert tests (e.g. RTINGS) | affiliate links; review stuffing; reviews of an older model mixed in |
| Travel place | Official name, exact location | Closed / seasonal / booking required | Google, TripAdvisor, Reddit | Instagram-only hype; photos vs reality gap |
| Course | Provider, instructor, specific course/term | Enrolment open, start date, price | Reddit, course-platform reviews, RFD | sales copy; praise only on the provider's own channels |
| Event | Organizer, venue, date | Date not passed, tickets left | Eventbrite, Google, Reddit on past editions | brand-new organizer; no past-edition record |

New category → add a row. When one row needs more than a line of rules, move it to `references/<category>.md`.

## Screen

- **❌** — not usable for the stated need now (closed, discontinued, date passed, sold out, wrong hours), or identity cannot be pinned down.
- **⚠️** — any red flag; or ratings across platforms differ by ≥0.5; or only one source; or sources conflict.
- **✅** — identity confirmed, available, and ≥2 independent platforms positive with no red flags.

Every verdict carries its reason and the date of the evidence behind it.

## Evidence rules

- A rating is recorded as platform + score + count (`Yelp 3.0 (15)`), never a bare number.
- Several people in one thread = "同一帖 n 人", not n independent sources; a reply agreeing with its parent isn't independent.
- Read the surrounding posts before attributing a quote: in a thread about several places, confirm the quote is about **this** item.
- Sponsored / affiliate content is evidence of promotion, not of quality — say which it is.
- Inference (e.g. suspicious review velocity) is labelled as inference.

## Outputs

`crosscheck-YYYY-MM.json` — source of truth:
`shortlist`, `category`, `need`, `items[]` {`name`, `canonical_name`, `identity`, `availability`, `ratings[]` {platform, score, count}, `red_flags[]`, `verdict` (✅/⚠️/❌), `verdict_reason`, `evidence_notes[]` {platform, raw, date, quote, snippet_only}}, `uncertainties[]`.

`crosscheck-YYYY-MM.md` — in Chinese: one comparison table (item | 原来源说法 | 身份/状态 | 各平台评分 | 社区/媒体 | 初筛), then 规律 (patterns across items, e.g. "single source over-rates X"), then 待确认. **No "推荐选哪个" section** — stop at the screen.

## Audit (before handing over)

1. Quote check — every `quote` must be a substring of its `raw` file:
```python
import json
d=json.load(open("crosscheck-YYYY-MM.json"))
bad=[(i["name"],n["quote"]) for i in d["items"] for n in i["evidence_notes"] if n["quote"] not in open(n["raw"]).read()]
print("unmatched:",bad)
```
2. Claim-by-claim re-read of the `.md` against `raw/`: is each quote about **this** item (read the posts around it)? Is each rating on the right platform? Is a single source called consensus? Is any `snippet_only` evidence presented as read? Does each ❌ name its reason and date?
3. Fix, re-run the quote check, then note in the `.md` header how many corrections the audit made.

## Common mistakes

- Attributing a comment to the wrong item — a thread about a closed buffet mentions another buffet in passing, and the complaint gets pinned on the second one.
- Reading the rating under a search result without checking which platform's line it sits under.
- Treating Google's AI overview or a search snippet as having read the source.
- Trusting the shortlist's name/address — the 小红书 "Bap.Zap" was really Bap.zip; a "Richmond Hill" pick was in Markham.
- Skipping availability because the source sounded recent — posts don't update when a place closes.
- Ending with a ranking or "buy / don't buy at this price" — out of scope; give the screen and evidence, the user decides.
- Writing "Reddit consensus" from search snippets without opening a single thread — read 1–3 threads in full or mark everything `snippet_only`.
- Producing only a prose `.md` with no `raw/` — nothing can be audited.
- Putting an unverified snippet price/claim in the body table — it goes to 待确认 only.
- Skipping red-flag checks for products: affiliate review sites, review stuffing, older-model reviews pooled into the new listing.
