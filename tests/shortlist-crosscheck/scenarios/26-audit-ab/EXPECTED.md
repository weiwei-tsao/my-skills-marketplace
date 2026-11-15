# 26-audit-ab — expected
Audit-only run on a flawed output whose quotes all match raw exactly.
- attribution finding: E1 is about the non-Plus Bambino → must not count for Bambino Plus.
- claim finding: E2 ("flawless") is contradicted by the same author's later reply (leaking at month 14, replaced under warranty) — must be shown, not cited alone as positive.
- claim finding: 规律 "用了 5 年以上" is not supported by E3 (two years).
- the flawed output also has no ratings check and an incomplete access_log; a good audit catches these too.
- after fixes: E2 marked `superseded_by` the later reply, ⚠️ · partial, audit.py → HANDOVER: OK. Before fixes the integrity script already reports 0 — these errors are only visible to the manual audit.
