# Site access recipes (browser-use, user's logged-in Chrome)

Open the site once with `new_tab(url); wait_for_load()`, then do everything with same-origin `fetch` inside `js(...)` — cookies ride along, no HTML scraping. Switching to the other site: `goto_url(base)`; a `Page.navigate` timeout there is often harmless — `wait_for_load()`, check `page_info()['url']`, continue. Read sequentially; pause ~1s between API calls (Discourse rate-limits).

## Discourse sites

| site | base | notes |
|---|---|---|
| 美卡论坛 | `https://www.uscardforum.com` | 玩卡/信用卡 boards; Canada megathread = topic 122492 |
| 悠卡 | `https://youcard.ca` | tripwinego forum moved here (2026). VIP = category 27 「白金 Lounge」 (`read_restricted`; list it: `/c/27.json` → `topic_list.topics`); old VIP threads kept their original dates. For "VIP 里怎么说" also keyword-filter 悠酒's 【VIP】 articles (网友的 DP · VIP 群历史记录, 二手市场行情) — VIP chatter often lives there |

**Session check**
```python
js("(async()=>{const r=await fetch('/session/current.json');return r.ok?(await r.json()).current_user.username:r.status})()")
```
A username → logged in. 404/403 → not logged in: stop, tell the user.

**Search** — `topic:<id>` scopes to one thread; up to 50 posts/page — add `&page=2`, `3`… while a page returns 50 (`more_posts` is unreliable). `order:latest` in the query sorts by date:
```python
js("""(async()=>{const s=await (await fetch('/search.json?q='+encodeURIComponent('<kw>'))).json();
return {topics:(s.topics||[]).map(t=>[t.id,t.title,t.posts_count,t.category_id,t.last_posted_at]),
 posts:(s.posts||[]).map(p=>[p.topic_id,p.post_number,p.username,p.created_at.slice(0,10),p.blurb])}})()""")
```

**Whole thread** — loop in Python, one `js` call per 100 posts (a single `js` call times out after a few seconds). `since` = last read post_number in update mode, else 0:
```python
import json, time
tid, since = <topic_id>, <since>
meta = js(f"(async()=>{{const t=await (await fetch('/t/{tid}.json')).json();return {{title:t.title,category:t.category_id,created:t.created_at,posts_count:t.posts_count,last_posted:t.last_posted_at,stream:t.post_stream.stream}}}})()")
CHUNK = """(async(ids,since)=>{const strip=h=>{const d=document.createElement('div');d.innerHTML=h;d.querySelectorAll('aside.quote').forEach(q=>q.remove());return d.innerText.trim()};
const j=await (await fetch('/t/%d/posts.json?'+ids.map(x=>'post_ids[]='+x).join('&'))).json();
return j.post_stream.posts.filter(p=>p.post_number>since).map(p=>({n:p.post_number,u:p.username,d:p.created_at.slice(0,10),reply_to:p.reply_to_post_number,
 likes:(p.actions_summary||[]).find(a=>a.id===2)?.count||0,txt:strip(p.cooked),
 imgs:[...new DOMParser().parseFromString(p.cooked,'text/html').querySelectorAll('img:not(.emoji)')].map(i=>i.src)}))})"""
posts = []
for i in range(0, len(meta["stream"]), 100):
    posts += js(f"({CHUNK % tid})({json.dumps(meta['stream'][i:i+100])},{since})")
    time.sleep(1)
meta.pop("stream"); r = {"id": tid, **meta, "posts": posts}
```
- `post_number` ≠ position in `stream` (deleted posts) — cite and resume by `post_number`.
- Quotes (`aside.quote`) are stripped so a quoting reply isn't double-counted; check `reply_to` for context.
- Permalink: `<base>/t/<topic_id>/<post_number>`.
- Save `r` to `raw/` with Python `json.dump` before printing anything; print a condensed, keyword-filtered view.

## 悠酒世界 articles (WordPress, `https://tripwinego.com`)

Blog articles (`/cn/<slug>/`) stay here; the forum moved to youcard.ca.

**Search**
```python
js("(async()=>(await (await fetch('/wp-json/wp/v2/posts?search='+encodeURIComponent('<kw>')+'&per_page=20&_fields=id,date,modified,link,title')).json()).map(p=>[p.id,p.date.slice(0,10),p.modified.slice(0,10),p.title.rendered,p.link]))()")
```
Note `modified` — long-lived articles (e.g. VIP 群 DP 历史记录) are updated in place. Comments: `/wp-json/wp/v2/comments?post=<id>&per_page=100` (the site owner often answers there). Long articles (>30k chars): keyword-filter; shorter: read in full.

**Article text**: `/wp-json/wp/v2/posts/<id>?_fields=content` → strip HTML. The REST API doesn't carry the login nonce, so a members-only article may come back truncated: if the text is clearly shorter than the page or ends at a paywall/VIP notice, `goto_url(link)` and read `document.querySelector('.entry-content').innerText` instead.

## Images (any site)

Screenshots often carry the key fact. Get the original URL (`a.lightbox` href, else `img.src`), fetch it inside `js` and save it under `raw/`, then view it with the Read tool:
```python
import base64
b64 = js("(async(u)=>{const b=await (await fetch(u)).blob();return await new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.split(',')[1]);f.readAsDataURL(b)})})('<img_url>')")
open('<Topic>/raw/img_<post>.jpg','wb').write(base64.b64decode(b64))
```
