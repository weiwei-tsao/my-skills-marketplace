---
name: shortlist-crosscheck
description: Use when the user already has a shortlist — restaurants/venues, products, travel places, courses, events — and wants each item verified across platforms before deciding: does it exist as named, is it available now, what do independent ratings and community threads say, any red flags. Triggers include "交叉验证", "核实一下", "这几个靠谱吗", "帮我查查这几个", "cross-check", "verify these". Distinct from xhs-topic-digest / en-community-digest, which find and summarize content on a topic; this skill only checks a given list and stops at a ✅/⚠️/❌ screen — the final choice is the user's.
---

# Shortlist Cross-check

## Overview

A shortlist from one source (a 小红书 digest, a friend, an ad) carries that source's blind spots: stale status, promo posts, community-specific taste, wrong names. This skill checks each item on independent platforms and returns evidence plus a first-pass screen. It does **not** find candidates and does **not** pick the winner for the user's situation — situations change; the user decides.

Pages are fetched with whichever **permitted** method suits the source (see *Access and failures*). **The caller's project rules decide what is permitted and preferred** — e.g. a repo that says "browser-use first for social sites, no curl/WebFetch first" wins. 小红书 goes through the xiaohongshu MCP.

## Workflow

1. **Pin the list, category and need.** One line per item; category from the table below. Record the need as `need` {text, requires, target_window, tz} — `requires` is what availability must prove (`hours`, `reservation`, `listing`, `stock`, `seats`, `dates`), e.g. "Saturday 12:30 lunch for 6, booked" → `reservation`, `2026-11-14T12:30/13:30`, `America/Toronto`.
2. **Identity + availability — one Google search per item.** `https://www.google.com/search?q=<name + locator>`; save `document.body.innerText` to `raw/google_<slug>.txt`. The knowledge panel usually gives the canonical name, address/model, status ("Temporarily closed"), hours, Google rating + count, and third-party rating snippets. No panel → retry with a sharper locator (address, full model number), then the platform itself (e.g. `https://www.google.com/maps/search/<q>`, read `div[role=main]`, save `raw/gmaps_<slug>.txt`).
   - Google's **AI Overview is not evidence** — including its source cards ("Product: … Model: …" blurbs with no URL, sitting above "Web results"). Use only Web-result lines that carry a source URL, or pages you opened.
   - If the canonical name/model differs from the shortlist's (renamed, misspelt, regional variant), record both and use the canonical one from here on.
3. **Platform signals** per the category row: ratings **with platform and count**, plus recent reviews where cheap. A bare `3.2(44)` on a results page belongs to the source line *above* it — check before attributing.
4. **Community threads.** Google `"<canonical name>" site:reddit.com` and `site:forums.redflagdeals.com` (one search per site; save results to `raw/google_site_searches.json`). Read the 1–3 most relevant threads in full with the en-community-digest recipes (Reddit `.json` fetch, RFD post extraction); save to `raw/reddit_<slug>.json` / `raw/rfd_<slug>.json` with the thread URL stored in the file. For Reddit also keep each comment's permalink — add `link:'https://www.reddit.com'+x.permalink` to the recipe's comment object; for RFD each reply's `id` (already like `p12345`) gives the anchor `#<id>` on the thread link. Anything known only from a search snippet is marked `snippet_only` with its age.
5. **Write outputs** (below) in the caller's topic folder.
6. **Audit** (below) — not optional.

Pace like a person: sequential, one tab, a few seconds between searches.

## Access and failures

Access, evidence and verification are three different questions: did this attempt get usable content; what kind of evidence is it (opened page, official structured data, snippet, user-provided); and are the item's required checks done (*Verification status*). A successful fetch never by itself makes an item `verified`.

- **Pick a permitted method per source**, not one tool for everything: a search engine to discover; an official API/feed for structured data where available; a plain HTTP fetch for public pages where the project allows it; browser-use for interactive, dynamic or logged-in pages; content the user exports when nothing else works. No fixed fallback order.
- **Log every attempt** in the item's `access_log[]` {source, url, method, at, outcome, partial, note}. `outcome` is one of `ok`, `timeout`, `rate_limited` (HTTP 429), `captcha`, `auth_required`, `content_incomplete`, `not_found`, `browser_error`; `partial` = the page loaded but key content was missing.
- **Bounded retries.** `timeout` / `browser_error` / `content_incomplete`: one retry of the same URL. `rate_limited` / `captcha` / `auth_required`: no retry of that URL in this run (honour Retry-After; don't wait it out inside the run). At most **12 attempts per item**.
- **Never bypass access controls**: no solving or dodging CAPTCHAs, no switching IPs, profiles or browsers to get past a block, no logging in to accounts the user didn't set up for this.
- **After a failure**, use another *permitted* route to the same evidence if there is one (e.g. the public `.json` of a thread the browser couldn't load) and log both attempts. If none works, record the step in `verification.missing[]` with the failure type and **move on to the next item** — one blocked site never stops the shortlist.
- `blocked` is an item-level outcome: only when a required check stayed undone because access failed on every permitted route. A failed attempt rescued by another route is just a logged failure.
- Stop early on decisive cheap evidence for the *search budget* (e.g. a second thread adds nothing new), but never skip a required check.

## Category table

| Category | Identity | Available now? | Ratings / reviews | Positive signal | Red flags | Investigation triggers |
|---|---|---|---|---|---|---|
| Restaurant / local business | Address, canonical Google name | Google Maps status, hours on the user's day | Google, Yelp, TripAdvisor, delivery apps, local subreddit, RFD | a diner praising the food/service/value relevant to the need | sponsored posts presented as reviews | review count growing implausibly fast for its age; dine-in vs delivery rating gap |
| Product | Full model number, regional version | In stock + price at Canadian retailers (Amazon.ca, Costco, Best Buy, RFD price threads) | Amazon, RFD, Reddit, expert tests (e.g. RTINGS) | an owner reporting it works as expected after real use; an expert test recommending it | affiliate links; review stuffing; reviews of an older model mixed in | rating gap between retailers; spike of recent 5★ reviews |
| Travel place | Official name, exact location | Closed / seasonal / booking required | Google, TripAdvisor, Reddit | a visitor recommending it for this kind of trip | Instagram-only hype; photos vs reality gap | rating gap; mostly old reviews |
| Course | Provider, instructor, specific course/term | Enrolment open, start date, price | Reddit, course-platform reviews, RFD | a past student reporting the promised outcome | sales copy; praise only on the provider's own channels | ratings only on the provider's site |
| Event | Organizer, venue, date | Date not passed, tickets left | Eventbrite, Google, Reddit on past editions | a past attendee recommending a previous edition | brand-new organizer; no past-edition record | ticket-site rating far from community talk |

New category → add a row. When one row needs more than a line of rules, move it to `references/<category>.md`.

## Verification status

Keep **what the item is like** (the screen) apart from **how much you managed to check** (`verification`). A page that wouldn't load is not evidence about the item.

Required checks per item: (1) identity, (2) availability for the stated need, (3) platform ratings, (4) community search — **every** site search step 4 of the workflow lists (Reddit and RFD); one site answering doesn't excuse skipping the other. A check is done when it ran and gave an answer — including `no_results` (the search ran and found nothing relevant), which does **not** make the item partial.

**Availability is proven only for what the need requires.** Record `availability` {kind, status, target_window, tz, checked_at, source, method}: `kind` is what the evidence actually shows (`hours`, `reservation`, `listing`, `stock`, `seats`, `dates`), `status` is `confirmed` / `not_available` / `unconfirmed` for the target window. Opening hours don't prove a table can be booked; a product listing doesn't prove stock; an event page doesn't prove seats. Check (2) is done only when `kind` matches `need.requires` (confirmed or not available); otherwise it goes in `missing[]` (e.g. "parties of 6 must phone to book" → reservation `unconfirmed`, `partial`).

`verification.status` is exactly one value; when several apply, take the first in this order:

| Status | When |
|---|---|
| `ambiguous` | the item can't be pinned to one entity (two businesses / models fit the shortlist name) — leave it unresolved, list the candidates, don't pick one |
| `blocked` | a required check couldn't be done because access failed (HTTP 429, captcha, login wall, page won't load after a retry) |
| `partial` | a required check is still missing for another reason (e.g. hours not published anywhere you looked) |
| `verified` | all four checks done |

Every unfinished check goes in `missing[]` as {step, reason}; checks that ran and found nothing go in `no_results[]`.

## Screen

- **❌** — evidence (dated) that it's not usable for the stated need now (closed, discontinued, date passed, sold out, wrong hours) or that it's the wrong item. Requires `verified`.
- **⚠️** — any red flag; or an investigation trigger left `unresolved`; or fewer than 2 independent positive sources; or sources conflict; **or verification isn't `verified`**.
- **✅** — identity confirmed, available, ≥2 **independent positive sources** (below) with at least one read on-page (not `snippet_only`), no red flags, no unresolved trigger. Requires `verified`.

| verification | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| `verified` | yes | yes | yes |
| `partial` / `blocked` / `ambiguous` | no | yes | no |

This is deliberately strict: a place confirmed permanently closed whose community check was blocked stays ⚠️ — put the dated closure evidence first in `verdict_reason` so the user sees it.

## Independent positive evidence

- **Positive** = an explicit favourable judgment relevant to the user's need, per the category's *Positive signal* column. A rating alone is not positive unless the source shows it in a favourable context you can quote; no complaints found is not positive.
- **Independent** = a different originating source (`origin`): who first published the judgment. Count origins, not URLs:
  - all `snippet_only` notes from one search results page = **one indirect source**, however many platforms it lists (Google aggregates; it is not Yelp + TripAdvisor + Google); the **knowledge panel is part of that page** — Google's own aggregate, `snippet_only`, not an opened page (it still counts as Google evidence for identity/availability);
  - a snippet whose origin you also opened (a Google result quoting the Reddit thread you read) is that same origin, not an extra source; a snippet whose origin you can't identify stays page-level indirect evidence;
- a repost, quote or syndicated copy of a review = the original's origin (identical text on two sites counts once);
  - one thread = one origin, however many people in it (still report "同一帖 n 人").
- **Investigation triggers** (rating gap between two comparable platforms each with ≥100 reviews of more than 0.5 — brand-own-site and expert /10 scores excluded; suspicious review velocity; the category's triggers column) are not findings. Record each in `investigation_triggers[]` {trigger, check, result: resolved | unresolved, note}: do the check (same model/location/time window? recent spike?) and say what it showed. Only a substantiated problem becomes a `red_flag`; an unresolved trigger keeps the item at ⚠️ with the explanation.
- Every verdict states `verdict_scope`: what was actually checked and how (e.g. "identity+hours via Google panel; Reddit thread opened; RFD searched, no results; Yelp snippet only").

A red flag is about the item itself (quality, safety, honesty of its reviews). Market noise — third-party marketplace mark-ups, a newer model also on sale, bundles — goes in a `notes` line and doesn't block ✅.

Every verdict carries `verdict_reason` and `verdict_date` (the day this screen was made; each `evidence_notes[].checked_at` is the day you retrieved that evidence, and `date` is the evidence's own date — when the post/review was written, or `checked_at` for undated live data like a status panel) — in the JSON and in the md 初筛 cell.

## Evidence rules

- A rating is recorded as platform + score + count (`Yelp 3.0 (15)`), never a bare number. Every score that appears anywhere — `ratings[]`, expert totals and sub-scores (e.g. RTINGS 7.4, Build Quality 6.5), verdict reasons, the md — has an evidence note quoting the line with that score.
- Identity claims ("X is the US model number", regional model mappings) need an evidence note too; otherwise label them inference or move them to 待确认.
- Snippet-derived price / stock / rating may go in the md table only tagged `（搜索结果 YYYY-MM-DD）` — the tag must cover every snippet number in the cell, including brand-site or store ratings that are only listed; unverified claims stay in 待确认.
- Several people in one thread = "同一帖 n 人" — both ways: not n independent sources, and not "单例" either. "一致 / 共识" only when it appears in ≥2 different threads or platforms.
- Before quoting a "used it X years, no problems" comment, read the same author's later replies and any follow-up question to it — the device may have died since.
- Contested characterisations ("entry-level", "overpriced") are written as "X 人这样说，Y 人反对", never as fact.
- Read the surrounding posts before attributing a quote: in a thread about several places or models ("Bambino/Plus", "my dyson cordless"), confirm the author means **this** item — if you can't tell, don't count it.
- For a reply in a comment section, confirm which comment it answers. Write a role ("staff", "official") only when the page marks it; otherwise label it inference.
- Sponsored / affiliate content is evidence of promotion, not of quality — say which it is.
- Inference (e.g. suspicious review velocity) is labelled as inference.

## Outputs

`crosscheck-YYYY-MM.json` — source of truth:
`shortlist`, `category`, `need` {text, requires, target_window, tz}, `items[]` {`name`, `canonical_name`, `identity`, `availability` {kind, status, target_window, tz, checked_at, source, method}, `access_log[]` {source, url, method, at, outcome, partial, note}, `ratings[]` {platform, score, count}, `red_flags[]`, `investigation_triggers[]` {trigger, check, result, note}, `notes[]`, `verification` {status, missing[] {step, reason}, no_results[], reason}, `verdict` (✅/⚠️/❌), `verdict_reason`, `verdict_date`, `verdict_scope`, `evidence_notes[]` {platform, origin, via, url, raw, date, checked_at, quote, snippet_only, supports[]}}, `uncertainties[]`.

Provenance per note: `origin` = who first published it (e.g. `yelp.ca`, `reddit r/Markham aaa111`, `google maps`, the original site for a repost); `via` = how you reached it (`google_serp`, `gmaps`, `reddit_json`, `rfd_page`, `site_page`, …); `snippet_only` = access level (true = seen only in a results page/aggregator); `supports[]` = which claim(s) it backs (`identity`, `availability`, `rating`, `positive`, `negative`, `red_flag`, `closure`). `url` is required so the user can reopen the source: the comment/post permalink when there is one (Reddit comment link, RFD `#<id>` e.g. `#p12345`), else the thread or page URL; for `snippet_only` evidence the search result's own URL; for knowledge-panel data the Google search URL.

`crosscheck-YYYY-MM.md` — in Chinese: one comparison table (item | 原来源说法 | 身份/状态 | 各平台评分 | 社区/媒体 | 初筛) — the 初筛 cell reads `<verdict> · <verification.status>：<reason> · <verdict_date>` (e.g. `⚠️ · blocked：Reddit 429，未完成社区核实 · 2026-11-14`), matching the JSON; then 规律 (patterns across items, e.g. "single source over-rates X"), then 待确认. **No "推荐选哪个" section** — stop at the screen.

## Audit (before handing over)

1. Script check, run from the topic folder — every `quote` is in its `raw` file (JSON raw is parsed and HTML entities decoded first), every `ratings[]` score appears in one of that item's quotes, every evidence note has a url and provenance, verdict and verification follow the Screen matrix, and ✅ rests on ≥2 independent positive sources:
```python
import json,re,html
def text(p):  # raw file as plain text: JSON → its string values joined; HTML entities decoded
    s=open(p,encoding="utf-8").read()
    if p.endswith(".json"):
        out=[]
        def walk(x):
            if isinstance(x,str): out.append(x)
            elif isinstance(x,(list,dict)): [walk(v) for v in (x.values() if isinstance(x,dict) else x)]
        walk(json.loads(s)); s="\n".join(out)
    return html.unescape(s)
norm=lambda t:re.sub(r"\s+"," ",t).strip()
d=json.load(open("crosscheck-YYYY-MM.json",encoding="utf-8")); exact=fuzzy=0; bad=[]
for i in d["items"]:
    for n in i["evidence_notes"]:
        try: raw=text(n["raw"])
        except Exception as e: bad.append((i["name"],n.get("raw"),repr(e))); continue
        q=html.unescape(n["quote"])
        if q in raw: exact+=1
        elif norm(q) in norm(raw): fuzzy+=1
        else: bad.append((i["name"],n["quote"]))
nosrc=[(i["name"],r["platform"],r["score"]) for i in d["items"] for r in i.get("ratings",[])
       if not any(str(r["score"]) in n["quote"] for n in i["evidence_notes"])]
print(f"exact {exact} / whitespace-normalised {fuzzy} / unmatched {len(bad)}",bad)
print(f"scores without an evidence quote: {len(nosrc)}",nosrc)
nourl=[(i["name"],n["quote"][:40]) for i in d["items"] for n in i["evidence_notes"] if not str(n.get("url") or "").startswith("http")]
print(f"evidence without a source url: {len(nourl)}",nourl)
rule=[]
for i in d["items"]:
    v=i.get("verification") or {}; st=v.get("status"); vd=i.get("verdict")
    if st not in ("verified","partial","blocked","ambiguous"): rule.append((i["name"],"bad status",st))
    if vd in ("✅","❌") and st!="verified": rule.append((i["name"],f"{vd} needs verified",st))
    if st in ("partial","blocked","ambiguous") and not v.get("missing"): rule.append((i["name"],"missing[] empty",st))
    if st=="verified" and v.get("missing"): rule.append((i["name"],"verified with unfinished checks",v["missing"]))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",str(i.get("verdict_date") or "")): rule.append((i["name"],"no verdict_date",None))
    if vd=="❌" and not any(n.get("date") for n in i["evidence_notes"]): rule.append((i["name"],"❌ without dated evidence",None))
    for n in i["evidence_notes"]:
        if not (n.get("origin") and n.get("via") and n.get("supports") and re.fullmatch(r"\d{4}-\d{2}-\d{2}",str(n.get("checked_at") or ""))):
            rule.append((i["name"],"note missing provenance",n["quote"][:30]))
    if not i.get("verdict_scope"): rule.append((i["name"],"no verdict_scope",None))
    if vd=="✅" and any(t.get("result")!="resolved" for t in i.get("investigation_triggers",[])): rule.append((i["name"],"✅ with unresolved trigger",None))
    pos=[n for n in i["evidence_notes"] if "positive" in (n.get("supports") or [])]
    op={str(n.get("origin")).lower() for n in pos if not n.get("snippet_only")}
    keys,seen,opened=[],{},False  # independence: snippets on one results page = one source, unless their origin was also opened (then = that origin); same quote text = same source
    for n in pos:
        o=str(n.get("origin")).lower()
        k=("origin",o) if (not n.get("snippet_only") or o in op) else ("serp",n["raw"])
        q=norm(n["quote"]).lower(); k=seen.setdefault(q,k) if len(q)>=30 else k
        keys.append(k); opened|=not n.get("snippet_only")
    if vd=="✅" and (len(set(keys))<2 or not opened): rule.append((i["name"],"✅ without 2 independent positive sources incl. 1 opened",sorted(set(keys))))
need=d.get("need") or {}
HARD={"rate_limited","captcha","auth_required"}; SOFT={"timeout","browser_error","content_incomplete"}
OUT=HARD|SOFT|{"ok","not_found"}
for i in d["items"]:
    log=i.get("access_log") or []; av=i.get("availability") or {}; st=(i.get("verification") or {}).get("status")
    if not log: rule.append((i["name"],"no access_log",None))
    if len(log)>12: rule.append((i["name"],"over 12 attempts",len(log)))
    by={}
    for a in log:
        if a.get("outcome") not in OUT: rule.append((i["name"],"bad outcome",a.get("outcome")))
        by.setdefault(a.get("url"),[]).append(a.get("outcome"))
    for u,outs in by.items():
        if any(o in HARD for o in outs[:-1]): rule.append((i["name"],"retried after 429/captcha/auth",u))
        if sum(o in SOFT for o in outs)>2 or (len(outs)>2 and outs[0] in SOFT): rule.append((i["name"],"more than one retry",u))
    if st=="blocked" and not any(a.get("outcome") in HARD|SOFT for a in log): rule.append((i["name"],"blocked without a logged failure",None))
    if any(not av.get(k) for k in ("kind","status","target_window","tz","checked_at","source","method")): rule.append((i["name"],"availability incomplete",sorted(k for k in av if av.get(k))))
    if i.get("verdict")=="✅" and not (av.get("kind")==need.get("requires") and av.get("status")=="confirmed"): rule.append((i["name"],"✅ without availability of the required kind",(av.get("kind"),av.get("status"),need.get("requires"))))
reposts=[]
for i in d["items"]:
    by={}
    for n in i["evidence_notes"]: by.setdefault(norm(n["quote"]).lower(),set()).add(str(n.get("origin")).lower())
    reposts+=[(i["name"],q[:40],sorted(o)) for q,o in by.items() if len(o)>1 and len(q)>=30]
print(f"screen/verification rule violations: {len(rule)}",rule)
print(f"possible reposts (same text, different origin — check manually): {len(reposts)}",reposts)
```
2. Claim-by-claim re-read of the `.md` against `raw/`: is each quote about **this** item (read the posts around it)? Is each rating on the right platform? Is a single source called consensus? Does every score in the md / verdict reasons (incl. expert sub-scores) and every identity claim map to an evidence note? Is any `snippet_only` evidence presented as read? Was any quote cherry-picked against the same author's later reply? Does each ❌/⚠️ name its reason and date? For each ❌, does the unusability fact itself (closed, discontinued, sold out…) cite a dated evidence note that states it — not just any dated note on the item? (The script only checks that some dated note exists.) For each `blocked`, does every access failure used to justify it belong to a required check that is still unfinished? A failure on an unrelated source, or on a check another route later completed, can't justify `blocked`. (The script only checks that some failure was logged.)
   Hand over only when the script prints 0 unmatched and 0 rule violations.
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
- Putting a snippet price in the table untagged, or an unverified claim anywhere but 待确认.
- Every product landing on ⚠️ because a 57-review brand site differs from a 5,000-review retailer — apply the ≥100-review and same-kind-platform conditions.
- Writing "单例" when three people in the same thread report the same failure.
- Marking an item `blocked` because Reddit returned 429 while the missing step is availability and the booking page loaded fine — the 429 belongs to the community check (done another way, or its own `missing` entry); the unfinished availability check is `partial` unless *its* routes failed.
- Skipping red-flag checks for products: affiliate review sites, review stuffing, older-model reviews pooled into the new listing.
