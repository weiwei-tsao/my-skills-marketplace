Owner: investigation.md

# Job timing

| Job | Starts (UTC) | Finishes (UTC) | Source |
|---|---|---|---|
| User-table export | 01:00 | ~03:00 | ops note, 2026-11-10: "the export usually wraps up around 3" |
| Nightly sync | 02:00 | ~02:25 | ops schedule |

The sync therefore reads the table while the export is still writing it.
