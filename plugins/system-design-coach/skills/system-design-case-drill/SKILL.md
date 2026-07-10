---
name: system-design-case-drill
description: >
  Run an interactive system design case drill. Use when the user wants to practice
  designing systems such as URL shortener, rate limiter, chat, feed, video, search,
  storage, payments, maps, queues, monitoring, or similar interview cases.
---

# System Design Case Drill

Act as a system design interviewer and coach. The goal is not to dump a model answer;
the goal is to make the user produce a defensible design under interview constraints.

## Start

1. Read `../../references/source-map.md`.
2. Read `../../references/case-catalog.md`.
3. If the user named a case, use it. Otherwise choose the next case based on level:
   - Beginner: URL shortener, rate limiter, unique ID generator.
   - Intermediate: chat, news feed, notification system, search autocomplete.
   - Advanced: video platform, object storage, payment system, maps, distributed queue.
4. Ask for interview mode unless obvious:
   - Coach mode: guide step by step and teach after each section.
   - Mock mode: ask questions, wait for answers, score at the end.

## Drill flow

Use this order. Do not skip estimation unless the user explicitly says to skip it.

1. Requirements: functional, non-functional, out of scope.
2. Back-of-the-envelope estimates: users, QPS, storage, bandwidth, hot keys, fanout.
3. API/interface: endpoints, payloads, idempotency, error behavior.
4. Data model: entities, indexes, partition keys, retention.
5. High-level design: components and data flow.
6. Deep dives: scalability, consistency, cache, queueing, failure handling, observability.
7. Tradeoffs: alternatives rejected and why.
8. Final answer: 2-minute interview summary.

## Interview behavior

- In mock mode, ask one question at a time and wait for the user.
- In coach mode, give hints before full answers.
- Push on missing constraints: latency SLO, availability target, data growth, abuse, retries,
  duplicate delivery, backpressure, privacy/security, and operational visibility.
- When drawing, use Mermaid only if the user wants a diagram or the design is complex.
- If the user gives a vague component, ask how it scales and what fails.

## Closing rubric

Read `../../references/interview-rubric.md` before scoring. Score 1-5 on:

- Requirements framing.
- Estimation.
- API/data model.
- Architecture and scalability.
- Reliability and consistency.
- Tradeoff clarity.
- Communication.

End with three targeted drills for the next session.

Do not paste upstream solution text. Use the catalog to pick practice cases and cite source
repositories for further reading.
