---
name: xhs-topic-digest
description: Use when the user wants a xiaohongshu (小红书) keyword or topic understood and summarized as real content — what posts and comments actually say (recommendations, places, tips, consensus, disagreements) — rather than an engagement/growth-metrics or content-strategy analysis. Triggers include "内容分析", "内容理解", "大家怎么说", "值不值得", "推荐", "避坑", "攻略", "评价". Distinct from requests about which formats/themes get more likes or how to grow an account, which belong to a content-strategy skill instead.
---

# XHS Topic Digest

## Overview

This is not a summary of "what the popular posts said" — it's a lightweight UGC qualitative research pipeline: search → diversify → inspect → corroborate → reach saturation → synthesize, extracting consensus, disagreement, recommendations, warnings, and recent changes from a representative sample of post bodies *and* comments. The key insight from testing this workflow: high-value practical information (corrections, price/hours updates, "don't bother" warnings) lives in comment threads, not post bodies, which skew toward selling the place/product/idea.

## When to use

- Default to this skill whenever the request names a xiaohongshu keyword/topic and asks what people say, whether something's worth it, recommendations, or 避坑/攻略/评价 — treat these as content-digest requests without asking which kind of report is wanted.
- Route to a content-strategy skill instead when the request is about which formats/themes get more engagement, growing an account, or "什么内容爆款" — signals: 爆款/点赞/互动/涨粉/怎么做账号.
- Only ask which is wanted when both sets of signals are clearly and strongly present in the same request.

## Workflow

1. `search_feeds(keyword, sort_by=...)` returns a **candidate pool** of ~20-30 posts, not the final sample. Sorting by 最多点赞 alone skews toward one popular sub-angle — e.g. "西安亲子游" sorted by likes returns famous landmarks, not stroller access, kid-friendly hotels, or queue avoidance. If the pool looks narrow or one-note, run a second search with a different `sort_by` (综合 / 最新) to widen it.
2. From the pool, select a sample covering different sub-angles, recency, and (where visible) differing opinions — not just the top N by likes. Call `get_feed_detail(feed_id, xsec_token)` for each selected post — required, not optional.
   - `get_feed_detail` is the expensive step — don't detail the whole pool. Aim for roughly 8-12 detailed posts for a normal-breadth topic; fewer for a narrow one, more only if viewpoints stay under-covered.
   - Stop condition (saturation): keep adding detailed posts only while each new one introduces a new sub-angle, materially shifts confidence in an existing claim, or reveals a real disagreement. Stop once additional posts mostly repeat what's already covered.
   - Batch ~3 in parallel; the tool times out under higher concurrency.
   - A failed call is skipped by default. Retry once only if that post covered an angle no other sampled post covers — don't retry just because a call failed.
3. Read comments for **information gain over the post body** — corrections, updated prices/hours, wait times, closures, alternatives, failed attempts, dissenting opinions, and the author's own replies. Comments like "求链接/好漂亮/收藏了" carry nothing — skip them, don't process every comment equally.
4. Weigh every claim by how it's corroborated, not by how confidently it's stated:
   - multiple independent posts/comments agree → state as consensus. "Independent" means separately-arrived-at reports, not the same wording repeated, repost-like content, a templated marketing script, or several comments echoing one original claim — ten comments agreeing sounds like consensus, ten comments copying each other isn't.
   - one post/comment says it → attribute it to that source, don't generalize it
   - sources conflict (e.g. differing ticket prices) → say so explicitly; don't average or silently pick one
   - treat clearly promotional/affiliate-style posts (探店/美妆/酒店合作 are common cases) as good evidence for *what* is being recommended, but weaker evidence for *whether* it's actually good — being recommended isn't the same as being reliably good
   - for anything time-sensitive (price, hours, opening/closure, construction, queue length), note the post/comment date. Prefer newer reports, but "newer" isn't automatically "correct" — if reports still disagree after checking dates, flag it as an open conflict rather than resolving it yourself
5. Synthesize into categories that fit the actual topic — don't force a fixed template. Travel: 必去景点/小众地点/吃什么避坑/实用提示/参考路线. Product roundup: 推荐单品/避雷单品/价格区间. Let the content decide the shape.
6. Produce two outputs:
   - A structured JSON as the source of truth. Conceptual fields, not a fixed schema — adapt names to the topic, but cover: `topic`, `sample_summary`, `themes[]` (each with `theme`, `consensus`, `disagreements`, `recommendations`, `warnings`, `evidence_notes`), `notable_updates[]`, `uncertainties[]`. Keep `evidence_notes` traceable to specific `feed_id`(s) and whether each came from the post body or a comment — a claim that can't be traced back to which post said it shouldn't be in the digest.
   - A Markdown digest built from that JSON, written so the user could act on it directly.
7. Only if the user asks for a shareable or visual version, create an Artifact styled as a reference document (sections, cards, tips) — not an engagement dashboard. Don't default to bar charts of likes/collects unless growth analysis was actually asked for.

## Common mistakes

- Defaulting to an engagement-metrics dashboard (average likes/collect-ratio by content theme) when the user asked for content understanding — same surface request, different data needs (comments + body vs. just `search_feeds` fields), and produces a report the user can't act on.
- Treating a single comment as verified fact (e.g. writing "the cable car is now free for kids" into the digest as settled because one comment said so) — weigh it per step 4 instead.
- Taking `search_feeds`' top-N-by-likes as the sample instead of a candidate pool — this silently drops entire sub-angles of the topic.
- Detailing the entire candidate pool, or stopping at 2-3 posts regardless of coverage — use the saturation rule in step 2, not a fixed count.
- Counting repeated/templated/copy-paste comments as independent corroboration.
