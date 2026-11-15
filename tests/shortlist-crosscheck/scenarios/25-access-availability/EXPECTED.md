# 25-access-availability — expected
Need: Saturday 2026-11-14 12:30 lunch for 6, booked (requires reservation). access_*.log lists every attempt.
- Kimchi House: browser 429 on Reddit, permitted public .json fetch succeeds → not blocked; OpenTable slot → ✅ · verified; both attempts in access_log.
- Seoul Grill: Reddit 429 on both routes, RFD CAPTCHA (no retry, no bypass) → ⚠️ · blocked; booking confirmed.
- Tofu Village: open, but parties of 6 must phone → availability reservation/unconfirmed → ⚠️ · partial.
- Bulgogi Bros: OpenTable timeout, one retry succeeds → ✅ · verified.
(The old skill already reached these verdicts; the new version adds structured access_log/availability.)
