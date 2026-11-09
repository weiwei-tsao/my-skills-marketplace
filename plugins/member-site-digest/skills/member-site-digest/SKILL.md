---
name: member-site-digest
description: Use when the user wants content distilled from a specific site they read with their own logged-in account — currently 美卡论坛 (uscardforum.com), 悠卡 (youcard.ca, formerly the tripwinego.com forum incl. VIP/白金 Lounge) and 悠酒世界 (tripwinego.com) articles — either a topic researched across that site, a long thread read end to end, or an earlier digest updated with new posts. Triggers include "美卡论坛", "uscardforum", "悠酒", "悠卡", "tripwinego", "youcard", "VIP 帖", "追更新", "这个帖子后面又说了什么".
---

# Member Site Digest

## Overview

Distill what members of a user-named site actually say, read through the user's **own logged-in Chrome session** via the **browser-use** skill (never curl/WebFetch — members-only content and bot blocking). Same research discipline as `en-community-digest`: read replies not just the OP, label consensus vs single DP vs conflict, date everything, audit against raw before handing over.

Site access recipes live in `sites.md` (this directory) — read it before touching a site. Site not in `sites.md` → follow **Adding a new site** below before researching.

## Modes

| User gives | Mode | Scope |
|---|---|---|
| a topic (+ optional site) | **topic** | search **every site in `sites.md`** unless the user names specific ones → pick relevant threads/articles → read each fully |
| a thread URL | **thread** | read every post; long threads: filter by sub-topic keywords, then read matches in full with their reply context |
| an existing digest / "追更新" | **update** | report on posts after the header's `已读至` marker; write a separate update file |

## Workflow

1. **Session check first** (recipe in `sites.md`). Not logged in, or a members-only category returns 403/404 → stop and tell the user which site/account; never log in or reset passwords yourself. If the user says to go ahead with public content only, proceed and list in 待验证/YMMV what guests may not see (e.g. replies count > posts fetched).
2. **Locate**: site search (several phrasings, incl. English product names and Chinese slang), plus threads the user named. Old tripwinego.com/community/ links → find the migrated topic on youcard.ca by title.
3. **Update mode — start point**: use `已读至 #N`. No marker → take the doc's 调研时间 and start after the last post dated on or before it (record how you chose); never trust a post *count* quoted in the doc (deleted posts). Check sibling update files in the folder for later markers. Fetch with `since=0` anyway — you need it to verify the start point and to read parents of replies (`reply_to`) that predate it. Read the original doc first and keep its structure and distinctions (e.g. its split between true credit-liquidation MS and plain bill-pay optimization) — the update answers per item it covers.
4. **Read** with the API recipe; save every extraction to `<Topic>/raw/<site>_<topic-id>.json` before reading condensed views. Long thread: if the posts in scope total under ~30k characters, read them all; otherwise keyword-filter per sub-topic with plain case-insensitive substring match (no `\b` — it fails next to Chinese) and several spellings, then read each hit plus its parent (`reply_to`) and replies. Image-only or image-heavy posts (`imgs` non-empty, short `txt`) often hold the key screenshot — open the image and read it.
5. **Weigh** — before citing a post, read replies to it and the same author's next few posts; members often clarify ("拉满了" may mean *their own* quota, not a platform limit). Then: several independent members → 共识(n); one DP → attribute with `#楼层`/author/date; conflicting → 分歧, both sides with dates. A reply agreeing with its parent is not independent. Check the user's premise too — a figure in the question ("8x") may be a blogger's amortised number, not the product's terms; say so up front. Mod/OP guides = what's recommended, not proof it still works. The site's own articles can contradict each other (e.g. one says breakfast in Canada, another says a dining credit) — that's 分歧 too: say which article says what. Everything time-sensitive (fees, rules, "已死/还能用") carries a date; prefer newer, flag unresolved conflicts. Channels die fast — say "截至 YYYY-MM-DD 的最新楼层".
6. **Write** to the topic folder in the research repo (create `<Topic>/` if missing), in Chinese:
   - `findings-<site>-<n>.md` (`<site>` = uscardforum | tripwinego; `<n>` = next free number). One file per **source**: 悠酒's articles (tripwinego.com) and its forum (youcard.ca) are the same source → one `findings-tripwinego-*` file with forum and article sections. When the question spans sources, each file answers from its own evidence and links the other — don't copy the same answer into both. Update mode: `<original-file-stem>-update-YYYY-MM.md`, linking the file it updates.
   - Header: 来源 (each thread/article: title + URL + author + start date), 调研时间, and per thread `已读至 #<post_number>（YYYY-MM-DD）`.
   - Body: start with the direct answer to the user's question; then key terms (fees, limits, thresholds, dates); then themes fit to the topic. Cite DPs as `（#1357，author，YYYY-MM-DD）`. When comparing options (channels, cards), list each option's cost/terms side by side.
   - End with **待验证 / YMMV**.
   - Members-only content stays in this private repo; don't paste it anywhere public.
7. **Self-audit**: script-check that every quoted string appears in the `txt` of the very post (`#楼层`) it's cited to, and author/date match (normalise “”/"" and 「」 first; match each quote separately, not greedily); a paraphrase is never put in quote marks; then for each key claim grep raw for counter-evidence (a contrary DP, a failed attempt, another article saying otherwise); then re-read the md claim by claim against raw — fix unsupported, mislabelled (single DP called 共识), misattributed, or stale claims.

## Adding a new site

Triggered by "把 XX 加进 member-site-digest", or by any request about a site missing from `sites.md`. Do it once, then the site is a first-class source:

1. **Identify the platform** (open the site in the user's Chrome):
   - Discourse: `meta[name=generator]` says Discourse, or `/session/current.json` answers → reuse the Discourse recipes.
   - WordPress: `/wp-json/` answers → reuse the article recipes.
   - Discuz: `discuz_uid` JS global, or `/api/mobile/index.php?version=4&module=check` answers → its mobile API returns thread JSON (`module=viewthread&tid=&page=`); search is HTML only.
   - Anything else (phpBB, XenForo, custom): work out from the page DOM how posts, post ids/floor numbers, dates, authors and pagination are marked up, and whether there's a JSON endpoint.
   - Always check: charset (GBK/Big5 sites need search terms encoded in that charset — UTF-8 silently returns 0 hits), Cloudflare interstitials (wait/poll until the real page loads), and keep one fetch per `js` call (multi-fetch calls time out).
2. **Session check**: confirm the user is logged in and members-only sections are readable. Not logged in → stop and ask; never log in yourself. If the user says to go ahead logged out, prove the recipes on public threads and mark the `sites.md` entry "members-only: unverified".
3. **Prove the recipes with real values** before writing them down, each run verbatim: session check; one search including page 2; one whole thread spanning 2+ pages; one update from a mid-thread floor; the permalink format. Check whether floor numbers stay stable when earlier posts are deleted — if not (Discuz, many custom forums), resume by a stable post id and record it in the marker: `已读至 #30（pid 55082157，YYYY-MM-DD）`.
4. **Record it**: add a row/section to `sites.md` (base URL, platform, members-only area, quirks), add the site's names to this skill's `description` triggers, and add its slug to the `<site>` list in Workflow step 6 (plus its marker format if it uses a stable id).
5. **Commit** in the marketplace repo (`claude plugin validate .`, `python3 vetting/audit_skill.py plugins/member-site-digest`), then push — ask the user before pushing.

## Common mistakes

- Reading only page 1 / the OP of a 2000-post thread, or only the last page.
- Treating stream position as post number (deleted posts make them diverge) — use `post_number`.
- Using the dead tripwinego.com/community/ URL instead of youcard.ca.
- Reporting a mod's year-old guide as current without checking later replies.
- Writing "大家都说" when it's one DP and an echo.
