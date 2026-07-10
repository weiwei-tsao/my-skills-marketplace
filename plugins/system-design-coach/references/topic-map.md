# Topic Map

Use this as a lightweight graph for roadmap planning. It is intentionally an index, not
a copied textbook.

## Foundations

- System design interview framing
- Requirements: functional, non-functional, out of scope
- Back-of-the-envelope estimation
- Latency vs throughput
- Performance vs scalability
- Availability, reliability, durability
- Consistency and CAP
- SLO, SLA, SLI

## Networking and Edge

- IP, TCP, UDP
- DNS and DNS caching
- HTTP, REST, GraphQL, gRPC
- CDN
- Reverse proxy
- Load balancing: L4, L7, active-passive, active-active
- Long polling, WebSocket, Server-Sent Events

## Data and Storage

- Relational databases
- NoSQL: key-value, document, wide-column, graph
- Indexes
- Replication: leader-follower, multi-leader
- Sharding and partitioning
- Consistent hashing
- Denormalization
- Transactions, distributed transactions
- ACID and BASE
- Object storage

## Caching

- Client, CDN, application, database caching
- Cache-aside
- Write-through
- Write-behind
- Refresh-ahead
- Eviction, TTL, invalidation
- Hot keys and cache stampede

## Async and Distributed Systems

- Message queues
- Publish-subscribe
- Task queues
- Backpressure
- Event-driven architecture
- Event sourcing
- CQRS
- Idempotency
- Retries and dead-letter queues

## Services and Operations

- Monoliths and microservices
- API gateway
- Service discovery
- Circuit breaker
- Rate limiting
- Observability: logs, metrics, traces
- Monitoring and alerting
- Disaster recovery
- Security basics: OAuth, OIDC, TLS, mTLS

## Suggested Progression

1. Interview framework and estimation.
2. Networking edge: DNS, CDN, load balancing.
3. Storage: SQL/NoSQL, indexes, replication, sharding.
4. Caching and queues.
5. Consistency, failures, and observability.
6. Case drills from simple to complex.
