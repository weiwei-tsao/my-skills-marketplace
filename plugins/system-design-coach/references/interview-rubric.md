# Interview Rubric

Score from 1 to 5. Use this for both drills and answer review.

## 1. Requirements Framing

- 1: Starts designing without clarifying.
- 3: Captures main features and a few non-functional requirements.
- 5: Defines functional scope, out-of-scope items, SLOs, scale, and success criteria.

## 2. Estimation

- 1: No numbers or impossible numbers.
- 3: Computes QPS/storage roughly with reasonable assumptions.
- 5: Uses estimates to drive design choices and identifies hot paths.

## 3. API and Data Model

- 1: No clear interface or entities.
- 3: Basic APIs and schema/indexes are plausible.
- 5: Covers idempotency, pagination, indexes, partition keys, retention, and errors.

## 4. Architecture and Scalability

- 1: Single box or vague boxes.
- 3: Reasonable components and scaling strategy.
- 5: Explains bottlenecks, partitioning, cache/queue placement, and evolution path.

## 5. Reliability and Consistency

- 1: Ignores failures.
- 3: Mentions replication, retries, and consistency choices.
- 5: Defines failure modes, recovery, data-loss tolerance, backpressure, and tradeoffs.

## 6. Operations and Security

- 1: No monitoring or abuse handling.
- 3: Basic metrics/logging and access control.
- 5: Includes observability, alerting, abuse prevention, privacy, and incident handling.

## 7. Communication

- 1: Hard to follow.
- 3: Organized but uneven depth.
- 5: Drives the interview, states assumptions, explains tradeoffs, and summarizes clearly.

## Feedback Format

Use:

- Verdict: ready / close / needs work.
- Top 3 gaps.
- One concrete revision path.
- Next drill.
