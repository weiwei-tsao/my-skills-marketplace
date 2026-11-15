"""Regression tests for plugins/shortlist-crosscheck/.../audit.py (the evidence-integrity / structural check).

Run:  python3 -m unittest discover -s tests/shortlist-crosscheck -v
Each case = one valid base output + one mutation; the audit must report exactly the expected rule kind(s)
(or the expected blocking counter) and exit non-zero; the untouched base must hand over (exit 0).
"""
import copy, json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT = os.path.join(ROOT, "plugins/shortlist-crosscheck/skills/shortlist-crosscheck/audit.py")
NAME = "Kimchi House"

RAW = {
    "raw/reddit.json": json.dumps({"url": "https://www.reddit.com/r/rh/comments/k1/", "comments": [
        {"author": "k1", "body": "Kimchi House galbi jjim is fantastic and they handle big groups well."},
        {"author": "k2", "body": "Second Kimchi House, friendly staff and fair prices for lunch."}]}),
    "raw/rfd.json": json.dumps({"url": "https://forums.redflagdeals.com/rh-2600111/", "posts": [
        {"id": "p7001", "txt": "Kimchi House did our team lunch for 8, great banchan and quick service."}]}),
    "raw/ot.txt": "Party size 6 · Sat, Nov 14 · 12:30 PM\nAvailable times: 12:30 PM\n",
    "raw/serp.txt": "Yelp 4.4(152) Best Korean in the area, generous banchan\nTripadvisor 4.5(40) Great value lunch special here\n",
    "raw/blog.txt": "What locals say: Kimchi House galbi jjim is fantastic and they handle big groups well.\n",
}


def note(i, quote, origin, via, raw, supports=("positive",), snippet=False):
    return {"id": f"E{i}", "platform": origin.split()[0], "origin": origin, "via": via,
            "url": f"https://src.example/{i}", "raw": raw, "date": "2026-10-01", "checked_at": "2026-11-14",
            "quote": quote, "snippet_only": snippet, "supports": list(supports)}


E_RED = note(1, "Kimchi House galbi jjim is fantastic and they handle big groups well.", "reddit r/rh k1", "reddit_json", "raw/reddit.json")
E_RFD = note(2, "Kimchi House did our team lunch for 8, great banchan and quick service.", "rfd rh p7001", "rfd_page", "raw/rfd.json")
E_OT = note(3, "Party size 6 · Sat, Nov 14 · 12:30 PM", "opentable kimchi", "site_page", "raw/ot.txt", ("availability",))


def access(url, outcome):
    return {"source": "s", "url": url, "method": "browser-use", "at": "2026-11-14T10:00-05:00",
            "outcome": outcome, "partial": False, "note": ""}


def base():
    item = {
        "name": NAME, "ratings": [], "red_flags": [], "notes": [],
        "verification": {"status": "verified", "missing": [], "no_results": [], "reason": "all checks done"},
        "verdict": "✅", "verdict_reason": "two independent opened positives; table confirmed",
        "verdict_date": "2026-11-14", "verdict_scope": "Google panel; Reddit+RFD opened; OpenTable opened",
        "investigation_triggers": [],
        "availability": {"kind": "reservation", "status": "confirmed", "target_window": "2026-11-14T12:30/13:30",
                         "tz": "America/Toronto", "checked_at": "2026-11-14", "source": "https://www.opentable.ca/r/kimchi",
                         "method": "browser-use"},
        "access_log": [access("https://www.opentable.ca/r/kimchi", "ok")],
        "evidence_notes": [copy.deepcopy(E_RED), copy.deepcopy(E_RFD), copy.deepcopy(E_OT)],
    }
    out = {"need": {"text": "Sat 12:30 lunch for 6, booked", "requires": "reservation",
                    "target_window": "2026-11-14T12:30/13:30", "tz": "America/Toronto"},
           "items": [item],
           "audit": {"attribution_checked": [NAME], "claim_checked": [NAME], "findings": [], "corrections": 0}}
    md = f"| 店 | 初筛 |\n|---|---|\n| {NAME} | ✅ · verified：两条独立好评 [E1][E2]，订位已确认 [E3] · 2026-11-14 |\n"
    progress = {"items": {NAME: {"identity": "done", "availability": "done", "community": "done",
                                 "audited": True, "failure": None, "checked_at": "2026-11-14"}}}
    return out, md, progress


def run(out, md, progress):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "raw"))
        for p, t in RAW.items():
            open(os.path.join(d, p), "w", encoding="utf-8").write(t)
        json.dump(out, open(os.path.join(d, "crosscheck-2026-11.json"), "w", encoding="utf-8"), ensure_ascii=False)
        open(os.path.join(d, "crosscheck-2026-11.md"), "w", encoding="utf-8").write(md)
        if progress is not None:
            json.dump(progress, open(os.path.join(d, "progress.json"), "w", encoding="utf-8"))
        rc = subprocess.run([sys.executable, "-I", AUDIT, "crosscheck-2026-11.json"], cwd=d,
                            capture_output=True, text=True).returncode
        res = json.load(open(os.path.join(d, "audit-result.json"), encoding="utf-8"))
    return rc, res


def it(o):
    return o["items"][0]


def set_status(o, st, missing=True):
    it(o)["verification"].update(status=st, missing=[{"step": "community", "reason": "rate_limited"}] if missing else [])


# name -> (mutation(out, md, progress) -> (out, md, progress), expected rule kind substring | blocking key)
CASES = {
    # --- #23 verification vs verdict
    "blocked ❌": (lambda o, m, p: (set_status(o, "blocked"), it(o).update(verdict="❌"), (o, m, p))[-1], "❌ needs verified"),
    "ambiguous ✅": (lambda o, m, p: (set_status(o, "ambiguous"), (o, m, p))[-1], "✅ needs verified"),
    "partial ❌": (lambda o, m, p: (set_status(o, "partial"), it(o).update(verdict="❌"), (o, m, p))[-1], "❌ needs verified"),
    "no verdict_date": (lambda o, m, p: (it(o).update(verdict_date=None), (o, m, p))[-1], "no verdict_date"),
    "partial, empty missing": (lambda o, m, p: (set_status(o, "partial", False), it(o).update(verdict="⚠️"), (o, m, p))[-1], "missing[] empty"),
    "verified with missing": (lambda o, m, p: (it(o)["verification"].update(missing=[{"step": "availability", "reason": "hours unknown"}]), (o, m, p))[-1], "verified with unfinished checks"),
    # --- #24 provenance and independence
    "two snippets one SERP": (lambda o, m, p: (it(o).update(evidence_notes=[
        note(1, "Yelp 4.4(152) Best Korean in the area, generous banchan", "yelp.ca", "google_serp", "raw/serp.txt", snippet=True),
        note(2, "Tripadvisor 4.5(40) Great value lunch special here", "tripadvisor.ca", "google_serp", "raw/serp.txt", snippet=True),
        copy.deepcopy(E_OT)]), (o, m, p))[-1], "without 2 independent positive sources"),
    "syndicated repost": (lambda o, m, p: (it(o).update(evidence_notes=[
        copy.deepcopy(E_RED), note(2, "Kimchi House galbi jjim is fantastic and they handle big groups well.", "local blog", "site_page", "raw/blog.txt"),
        copy.deepcopy(E_OT)]), (o, m, p))[-1], "without 2 independent positive sources"),
    "same thread twice": (lambda o, m, p: (it(o).update(evidence_notes=[
        copy.deepcopy(E_RED), note(2, "Second Kimchi House, friendly staff and fair prices for lunch.", "reddit r/rh k1", "reddit_json", "raw/reddit.json"),
        copy.deepcopy(E_OT)]), (o, m, p))[-1], "without 2 independent positive sources"),
    "serp snippet of opened origin": (lambda o, m, p: (it(o).update(evidence_notes=[
        copy.deepcopy(E_RED), note(2, "Yelp 4.4(152) Best Korean in the area, generous banchan", "reddit r/rh k1", "google_serp", "raw/serp.txt", snippet=True),
        copy.deepcopy(E_OT)]), (o, m, p))[-1], "without 2 independent positive sources"),
    "unresolved trigger": (lambda o, m, p: (it(o).update(investigation_triggers=[{"trigger": "rating_gap", "check": "c", "result": "unresolved", "note": ""}]), (o, m, p))[-1], "unresolved trigger"),
    "missing provenance": (lambda o, m, p: (it(o)["evidence_notes"][0].update(origin=None), (o, m, p))[-1], "missing provenance"),
    # --- #25 access and availability
    "429 retried": (lambda o, m, p: (it(o).update(access_log=[access("u", "rate_limited"), access("u", "rate_limited")]), (o, m, p))[-1], "retried after 429"),
    "captcha retried": (lambda o, m, p: (it(o).update(access_log=[access("u", "captcha"), access("u", "ok")]), (o, m, p))[-1], "retried after 429"),
    "✅ on hours": (lambda o, m, p: (it(o)["availability"].update(kind="hours"), (o, m, p))[-1], "availability of the required kind"),
    "blocked without failure": (lambda o, m, p: (set_status(o, "blocked"), it(o).update(verdict="⚠️"), (o, m, p))[-1], "blocked without a logged failure"),
    "availability incomplete": (lambda o, m, p: (it(o)["availability"].pop("tz"), (o, m, p))[-1], "availability incomplete"),
    "timeout retried twice": (lambda o, m, p: (it(o).update(access_log=[access("u", "timeout"), access("u", "timeout"), access("u", "ok")]), (o, m, p))[-1], "more than one retry"),
    # --- blocking counters (handover requires all zero)
    "quote not in raw": (lambda o, m, p: (it(o)["evidence_notes"][0].update(quote="Kimchi House is the worst"), (o, m, p))[-1], "unmatched"),
    "score without quote": (lambda o, m, p: (it(o).update(ratings=[{"platform": "Google", "score": 4.7, "count": 300}]), (o, m, p))[-1], "scores_without_quote"),
    "evidence without url": (lambda o, m, p: (it(o)["evidence_notes"][0].update(url=""), (o, m, p))[-1], "evidence_without_url"),
    # --- #26 evidence ids, md links, manual audits, availability evidence, progress
    "duplicate evidence id": (lambda o, m, p: (it(o)["evidence_notes"][1].update(id="E1"), (o, m, p))[-1], "evidence id"),
    "md cites unknown id": (lambda o, m, p: (o, m.replace("[E3]", "[E9]"), p), "md cites unknown evidence"),
    "md row without citation": (lambda o, m, p: (o, m.replace("[E1][E2]", "").replace("[E3]", ""), p), "md row without evidence id"),
    "✅ without availability evidence": (lambda o, m, p: (it(o).update(evidence_notes=[copy.deepcopy(E_RED), copy.deepcopy(E_RFD)]), (o, m.replace("[E3]", ""), p))[-1], "without availability evidence"),
    "attribution audit not recorded": (lambda o, m, p: (o["audit"].update(attribution_checked=[]), (o, m, p))[-1], "attribution audit not recorded"),
    "claim audit not recorded": (lambda o, m, p: (o["audit"].update(claim_checked=[]), (o, m, p))[-1], "claim audit not recorded"),
    "verdict while stage pending": (lambda o, m, p: (p["items"][NAME].update(community="pending", audited=False), (o, m, p))[-1], "stage not done"),
    "no progress file": (lambda o, m, p: (o, m, None), "no progress.json"),
    "audited false, all stages done": (lambda o, m, p: (p["items"][NAME].update(audited=False), (o, m, p))[-1], "item not audited"),
    "superseded positive still counted": (lambda o, m, p: (it(o).update(evidence_notes=[
        copy.deepcopy(E_RED), dict(copy.deepcopy(E_RFD), superseded_by="E4"),
        note(4, "Second Kimchi House, friendly staff and fair prices for lunch.", "rfd rh p7001", "rfd_page", "raw/reddit.json", ("negative",)),
        copy.deepcopy(E_OT)]), (o, m, p))[-1], "without 2 independent positive sources"),
}


class AuditRegression(unittest.TestCase):
    def test_base_hands_over(self):
        rc, res = run(*base())
        self.assertEqual(res["handover"], "OK", res)
        self.assertEqual(rc, 0)

    def test_cases(self):
        for name, (mutate, expect) in CASES.items():
            with self.subTest(name):
                rc, res = run(*mutate(*base()))
                self.assertEqual(rc, 1, f"{name}: should block handover")
                if expect in res["blocking"]:
                    self.assertGreater(res["blocking"][expect], 0, res)
                else:
                    kinds = [r[1] for r in res["rule_violations"]]
                    self.assertTrue(any(expect in k for k in kinds), f"{name}: expected '{expect}' in {kinds}")


if __name__ == "__main__":
    unittest.main()
