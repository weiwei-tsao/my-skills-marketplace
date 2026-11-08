---
name: en-community-digest
description: Use when the user wants English-language community opinion on a topic — what Reddit or RedFlagDeals (RFD) threads and comments actually say (recommendations, warnings, recent changes, consensus, disagreements) — especially Canadian/Ontario topics like credit cards, deals, services, kids activities, travel. Also use when asked to merge an English web digest with a xiaohongshu (小红书) digest. Triggers include "英文资料", "Reddit 怎么说", "RFD 上", "English sources", "what does reddit think".
---

# EN Community Digest (Reddit + RFD)

## Overview

English counterpart of `xhs-topic-digest`: a small UGC qualitative study — search → diversify → read bodies **and** comments → corroborate → stop at saturation → synthesize. Value lives in comment threads (corrections, data points, "don't bother"), not in the post that asked the question.

All page access goes through the **browser-use** skill (user's real Chrome, logged-in, human-like). Don't try `curl`/WebFetch first — Reddit and many forums block them.

Sources in scope: Reddit, RFD. Other platforms (X, Telegram, GitHub, custom sites) are not covered yet — see repo issue #1; for a user-named site, use the same Google `site:` + read-the-page approach and say it's ad hoc.

## Workflow

1. **Candidate pool — one Google search per site** (combining with `OR` lets Reddit crowd out RFD):
   `https://www.google.com/search?q=<kw>+site%3Areddit.com&tbs=qdr:y` and the same with `site%3Aforums.redflagdeals.com`. `tbs=qdr:y` = past year; drop it for evergreen topics. Extract with `js("[...document.querySelectorAll('a h3')].map(h=>({t:h.innerText,u:h.closest('a').href}))")`. Multi-part question → one search per sub-question (and per site); put the user's situation in a phrasing (e.g. `SUV`, `Ontario`). Add another phrasing (`<kw> worth it`, `<kw> vs`, `<kw> problem`) if the pool is one-note.
2. **Sample** ~6–10 threads in total (both platforms; ~3 per sub-question for multi-part asks), across sub-angles, subreddits, recency, and opposing takes — not just top results. A brand subreddit (r/Wealthsimple, r/amexcanada) skews fan-side: counterweight with r/PersonalFinanceCanada or RFD and say in `sample_summary` if the sample still leans one way. Read each (recipes below) and save every extraction to `<Topic>/raw/<platform>_<id>.json`. Keep adding threads only while each adds a new angle, shifts confidence, or shows real disagreement.
3. **Read comments for information gain**: data points, dated changes, corrections, failures, dissent. Skip "this"/"following". Weight by score, but a low-score dated correction beats a high-score joke.
4. **Corroborate**: several independent users agree → consensus; one user → attribute it; conflicting → say so, don't average. A reply quoting or agreeing with its parent (`d`+1) is not independent. Affiliate/referral-link posts = evidence of *what* is pushed, not *whether* it's good. Note dates on anything time-sensitive (fees, earn rates, policies, prices). Products get renamed or re-tiered — map old/new names explicitly. Seasonal topics: separate this season's evidence from last season's and flag a theme resting mostly on year-old posts.
5. **Output** to the topic folder in this repo (create `<Topic-Name>/` if missing):
   - `en-digest-YYYY-MM.json` — source of truth: `topic`, `sample_summary` (threads read, per platform), `themes[]` {`theme`, `consensus`, `disagreements`, `recommendations`, `warnings`, `evidence_notes`}, `notable_updates[]`, `uncertainties[]`. `evidence_notes` = one entry per source: {platform, url (thread URL; RFD add `#p<id>`), author, date, post|comment, quote}.
   - `en-digest-YYYY-MM.md` — in Chinese (user's reading language). Shape:
     1. **结论**: a direct answer to the user's actual question, applied to their stated situation (province, eligibility, spending). When it compares options (where to buy, which card), give each option's net cost/terms from raw side by side — never favour one while omitting the other's discount or counter-evidence.
     2. **Key terms** the decision hinges on — fees, caps/limits, earn rates, eligibility, deadlines — each with its source date. Check the raw data for these explicitly; they're easy to drop.
     3. **Themes** fit to the topic. Every claim carries a label: `共识(n)` with n independent users, `单一来源`, or `分歧` (state each side with its sources; don't pick a winner).
     4. **待确认** — only things the raw data truly leaves open.
     Keep the key claim's English verbatim in quotes. Translate only what the source says — no added qualifiers (e.g. a nationality the source didn't name).
   - Counts in `sample_summary` come from the raw files (threads read, comments extracted) — not from page headers you didn't save.
6. **Self-audit before handing over**: script-check that every JSON `quote` is a substring of a `raw/` file, then re-read the `.md` against `raw/` claim by claim. Fix anything unsupported, mis-labelled (single source called 共识), misattributed (wrong platform/thread/date), or where a number in raw contradicts the digest.

## Reading recipes (browser-use)

**Reddit** — use `www.reddit.com` + the `.json` fetch below (old.reddit sometimes redirects to a login wall, and its HTML caps at ~200 comments without expanding). The page only renders ~25 comments; fetch the full tree same-origin from the open thread:

```python
goto_url(url); wait_for_load()   # new_tab(...) once for the first thread, then goto_url for each
r = js("""(async()=>{const j=await (await fetch(location.pathname.replace(/\\/$/,'')+'.json?sort=top&limit=500&depth=10&raw_json=1')).json();
const p=j[0].data.children[0].data, out=[];
const walk=(cs,d)=>cs.forEach(c=>{if(c.kind!=='t1')return;const x=c.data;
 out.push({d,score:x.score,date:new Date(x.created_utc*1000).toISOString().slice(0,10),author:x.author,body:x.body.slice(0,800)});
 if(x.replies)walk(x.replies.data.children,d+1)});
walk(j[1].data.children,0);
return {title:p.title,sub:p.subreddit,date:new Date(p.created_utc*1000).toISOString().slice(0,10),score:p.score,body:p.selftext.slice(0,2000),comments:out}})()""")
```
Save the full extraction to `raw/` first, then print a condensed view (score ≥ 3 or top-level, indented by `d`; raise the threshold for 300+ comment threads — tool output overflows). Login wall or captcha → stop and ask the user. (Only if you fall back to reading the rendered DOM and the page is blank: `activate_tab(current_tab())`.)

**RFD** (`forums.redflagdeals.com`, no login needed). Long megathreads run hundreds of pages; page 1 is years old. Read the **OP once** (often a maintained wiki/summary — note its "Updated:" date) plus the **last pages** (`<thread-url>/<N>/`), walking backward until you've covered ~6 months or the topic's last material change (often 3–12 pages; last page may hold only a few posts). The OP repeats at the top of every page — skip it after the first read; it has no `date` key (read fields with `.get`). Megathread OPs are often years stale — don't cite them for current terms. Page count: `js("document.body.innerText.match(/Page \\d+ of (\\d+)/)?.[1]")`. The recipe cuts posts at 800 chars and the OP at "Click to read more" — when the OP holds key terms (rebate tables, wiki), save its full `innerText` as `op_full`. Extract posts with quotes stripped:

```python
r = js("""[...document.querySelectorAll('article.post')].map(a=>{const c=a.querySelector('.post_content .content')?.cloneNode(true);
c?.querySelectorAll('blockquote').forEach(q=>q.remove());
return {id:a.id,date:a.querySelector('.dateline_timestamp')?.innerText,author:a.querySelector('.postauthor')?.innerText?.trim(),txt:c?.innerText?.trim().slice(0,800)}})""")
```

Pace like a person: read threads sequentially in one tab, don't fire dozens of fetches in parallel.

## Merging with a xiaohongshu digest

Only when asked. Read both `.md`/`.json` digests in the topic folder and write `<Topic>/merged-YYYY-MM.md`: (1) where Chinese and English sources agree, (2) where they conflict — keep both, with dates, (3) what only one side covers (often: XHS = 华人视角/实操体验, Reddit/RFD = 本地政策/数据点/最新变动). Don't re-research during the merge.

## Common mistakes

- One combined `OR` search → RFD vanishes from the pool.
- Trying old.reddit or reading only rendered `shreddit-comment`s → missing most of the thread.
- Reading RFD page 1 of a megathread and reporting 2017 info as current.
- Treating one confident comment as fact; counting echoed replies as independent corroboration.
- Dumping a list of thread summaries instead of synthesizing by theme.
- Writing "community consensus" when it's two users and several others cancelled — that's a 分歧.
- Misreading a personal stat as a general one ("I use Amex 95% of the time" ≠ "95% of restaurants take Amex").
- Listing as 待确认 a number that's in the raw data (fees, caps) because it wasn't in the top comments.
