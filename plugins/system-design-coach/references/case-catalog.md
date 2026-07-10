# Case Catalog

Use this to select drills and map cases to concepts. It is a catalog of prompts and
learning targets, not a solution bank.

## Beginner

### URL Shortener
- Concepts: API design, redirects, unique IDs, storage, cache, analytics.
- Push on: custom aliases, expiration, abuse, hot links, read-heavy scaling.
- Sources to consult: system-design-primer solutions, Karan course, Admol chapter list.

### Rate Limiter
- Concepts: bucket-based limiting, leaky bucket, fixed/sliding windows, Redis, distributed limits.
- Push on: per-user vs per-IP, global limits, clock skew, fail-open vs fail-closed.
- Sources to consult: Admol chapter list, Karan course.

### Unique ID Generator
- Concepts: UUID, Snowflake-style IDs, coordination, clock issues, ordering.
- Push on: region bits, timestamp rollback, database bottlenecks.
- Sources to consult: Admol chapter list.

## Intermediate

### Chat System
- Concepts: WebSocket, fanout, online presence, message ordering, storage.
- Push on: offline messages, multi-device sync, delivery receipts, large groups.

### News Feed
- Concepts: fanout-on-write, fanout-on-read, ranking, cache, async workers.
- Push on: celebrity users, freshness, consistency, privacy.

### Notification System
- Concepts: queues, templates, preferences, retries, provider integration.
- Push on: dedupe, rate limits, quiet hours, priority.

### Search Autocomplete
- Concepts: trie, prefix index, ranking, cache, update pipeline.
- Push on: personalization, typo tolerance, trending queries.

### Web Crawler
- Concepts: frontier queue, politeness, dedupe, storage, scheduling.
- Push on: robots.txt, rate limits, canonical URLs, failures.

## Advanced

### Video Platform
- Concepts: upload pipeline, transcoding, CDN, metadata, recommendations.
- Push on: resumable upload, encoding ladder, global delivery, moderation.

### Object Storage
- Concepts: blob storage, metadata, replication, consistency, multipart upload.
- Push on: durability, hot objects, lifecycle policies, access control.

### Distributed Message Queue
- Concepts: partitioning, ordering, consumer groups, offset management.
- Push on: exactly-once claims, replay, backpressure, rebalancing.

### Monitoring and Alerting
- Concepts: metrics ingestion, time-series storage, alert evaluation, dashboards.
- Push on: high cardinality, retention, late data, alert fatigue.

### Payment System
- Concepts: ledger, idempotency, reconciliation, external providers, risk.
- Push on: double charge, partial failure, refunds, audit trail.

### Maps / Nearby Service
- Concepts: geohash, quadtrees, indexing, routing, real-time location.
- Push on: precision, privacy, freshness, hotspots.
