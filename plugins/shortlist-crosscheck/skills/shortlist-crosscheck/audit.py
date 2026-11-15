"""Evidence-integrity / structural check for a shortlist-crosscheck output.

Usage (from the topic folder):  python3 -I <skill-dir>/audit.py crosscheck-YYYY-MM.json
Checks structure and string-level integrity only; it cannot prove that a quote is about the right
item or that evidence supports a verdict — that is the manual attribution and claim audit.
Writes audit-result.json next to the input and exits 1 unless every blocking count is zero.
"""
import sys,os
J=sys.argv[1] if len(sys.argv)>1 else "crosscheck.json"
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
d=json.load(open(J,encoding="utf-8")); exact=fuzzy=0; bad=[]
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
    pos=[n for n in i["evidence_notes"] if "positive" in (n.get("supports") or []) and not n.get("superseded_by")]  # a reversed note no longer counts
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
# evidence ids, md ↔ JSON links, manual audits recorded, availability evidence, progress state (#26)
here=os.path.dirname(os.path.abspath(J))
ids=[n.get("id") for i in d["items"] for n in i["evidence_notes"]]
for x in sorted({str(x) for x in ids if not re.fullmatch(r"E\d+",str(x)) or ids.count(x)>1}): rule.append(("*","evidence id missing or duplicated",x))
mdp=os.path.splitext(J)[0]+".md"; md=open(mdp,encoding="utf-8").read() if os.path.exists(mdp) else ""
if not md: rule.append(("*","no md next to the json",mdp))
for x in sorted(set(re.findall(r"\[(E\d+)\]",md))-set(ids)): rule.append(("*","md cites unknown evidence",x))
au=d.get("audit") or {}
pp=os.path.join(here,"progress.json"); prog=json.load(open(pp,encoding="utf-8")).get("items",{}) if os.path.exists(pp) else None
if prog is None: rule.append(("*","no progress.json",None))
for i in d["items"]:
    rows=[l for l in md.splitlines() if l.startswith("|") and i["name"] in l]
    if md and not rows: rule.append((i["name"],"item missing from md table",None))
    if any(not re.search(r"\[E\d+\]",l) for l in rows): rule.append((i["name"],"md row without evidence id",None))
    if i["name"] not in (au.get("attribution_checked") or []): rule.append((i["name"],"attribution audit not recorded",None))
    if i["name"] not in (au.get("claim_checked") or []): rule.append((i["name"],"claim audit not recorded",None))
    if i.get("verdict")=="✅" and not any("availability" in (n.get("supports") or []) and not n.get("snippet_only") for n in i["evidence_notes"]):
        rule.append((i["name"],"✅ without availability evidence",None))
    pg=(prog or {}).get(i["name"])
    if prog is not None and i.get("verdict") in ("✅","❌") and (not pg or any(pg.get(s)!="done" for s in ("identity","availability","community"))):
        rule.append((i["name"],"verdict while a stage not done",pg))
reposts=[]
for i in d["items"]:
    by={}
    for n in i["evidence_notes"]: by.setdefault(norm(n["quote"]).lower(),set()).add(str(n.get("origin")).lower())
    reposts+=[(i["name"],q[:40],sorted(o)) for q,o in by.items() if len(o)>1 and len(q)>=30]
print(f"screen/verification rule violations: {len(rule)}",rule)
print(f"possible reposts (same text, different origin — check manually): {len(reposts)}",reposts)
blocking={"unmatched":len(bad),"scores_without_quote":len(nosrc),"evidence_without_url":len(nourl),"rule_violations":len(rule)}
ok=not any(blocking.values())
json.dump({"blocking":blocking,"unmatched":bad,"scores_without_quote":nosrc,"evidence_without_url":nourl,
           "rule_violations":[list(map(str,r)) for r in rule],"possible_reposts":reposts,"handover":"OK" if ok else "BLOCKED"},
          open(os.path.join(os.path.dirname(os.path.abspath(J)),"audit-result.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1,default=str)
print("HANDOVER:","OK" if ok else "BLOCKED",blocking)
sys.exit(0 if ok else 1)
