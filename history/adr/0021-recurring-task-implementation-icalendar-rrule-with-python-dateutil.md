# ADR-0021: Recurring Task Implementation (iCalendar RRULE with python-dateutil)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-01
- **Feature:** 002-event-driven
- **Context:** Phase V requires automatic regeneration of recurring tasks (e.g., weekly meetings, monthly reports) when users mark them complete. Need to implement industry-standard recurrence rules that support complex patterns (daily, weekly, monthly, yearly with custom intervals) while ensuring parsing correctness and preventing infinite loops or malformed rules.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement recurring task automation using the following integrated approach:

- **Recurrence Format:** iCalendar RRULE (RFC 5545 standard)
- **Parsing Library:** python-dateutil 2.8.2 (rrule module)
- **Validation Strategy:** Whitelist-based RRULE pattern validation
- **Trigger Mechanism:** Kafka event-driven (TaskCompletedEvent → Recurring Task Service)
- **Next Occurrence Calculation:** rrulestr().after() with future-only filtering
- **Error Handling:** Graceful skip on invalid RRULE, log-and-continue for malformed events

**Supported RRULE Patterns (Whitelist):**
- Daily: `FREQ=DAILY`, `FREQ=DAILY;INTERVAL=N`
- Weekly: `FREQ=WEEKLY;BYDAY=MO,WE,FR`, `FREQ=WEEKLY;INTERVAL=2;BYDAY=TU`
- Monthly: `FREQ=MONTHLY;BYMONTHDAY=15`, `FREQ=MONTHLY;BYDAY=1MO`
- Yearly: `FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25`

## Consequences

### Positive

- **Industry-standard format:** iCalendar RRULE is RFC 5545 compliant, used by Google Calendar, Outlook, Apple Calendar (users already familiar)
- **Battle-tested library:** python-dateutil used by major calendar applications, proven correctness for complex recurrence patterns
- **Pythonic API:** Integrates seamlessly with Python datetime objects, no conversion overhead
- **Comprehensive coverage:** Supports FREQ, COUNT, UNTIL, INTERVAL, BYDAY, BYMONTH, etc. (covers all common use cases)
- **Whitelist validation:** Prevents malicious or overly complex RRULEs (e.g., SECONDLY frequency causing infinite loops)
- **Event-driven decoupling:** Recurring Task Service operates independently, can scale horizontally if needed
- **Graceful degradation:** Invalid RRULEs are logged and skipped (no service crash or task corruption)
- **Future extensibility:** Can add new patterns to whitelist without changing core logic

### Negative

- **Learning curve:** Users may not be familiar with RRULE syntax (e.g., `FREQ=WEEKLY;BYDAY=MO` vs natural language "every Monday")
- **Whitelist maintenance:** Adding new recurrence patterns requires code changes and redeployment
- **No human-readable format:** RRULEs are machine-optimized, not user-friendly (e.g., `FREQ=MONTHLY;BYDAY=1MO` instead of "First Monday of each month")
- **Validation complexity:** Regex-based whitelist can become hard to maintain as patterns grow
- **No COUNT enforcement:** python-dateutil respects COUNT in RRULE, but we don't track occurrences (tasks repeat forever if COUNT not specified)
- **Timezone handling:** RRULE parsing requires careful handling of UTC vs local time (risk of off-by-one errors near DST transitions)

## Alternatives Considered

### Alternative A: Natural Language Recurrence (e.g., "every Monday")
- **Components:** Custom parser + NLP library (spaCy/nltk) to parse "every Monday", "every 2 weeks", etc.
- **Why rejected:**
  - High complexity: Natural language parsing is ambiguous (e.g., "every other Monday" vs "every second Monday of the month")
  - No standard: Each application invents its own syntax, leading to user confusion
  - Translation overhead: Still need to convert to internal representation (likely RRULE or similar)
  - Maintenance burden: Requires training data, grammar rules, and continuous updates for edge cases
  - Less precise: Natural language lacks expressiveness for complex patterns (e.g., "2nd and 4th Thursday of each month")

### Alternative B: Custom RRULE Parser (Reinvent the Wheel)
- **Components:** Handwritten RRULE parser with regex and state machine
- **Why rejected:**
  - Error-prone: RFC 5545 has edge cases and corner cases that python-dateutil already handles
  - Maintenance cost: Need to fix bugs, add features, and keep up with RFC updates
  - No benefit: python-dateutil is well-tested, optimized, and free (no reason to reinvent)
  - Testing burden: Would need comprehensive test suite to match python-dateutil's coverage

### Alternative C: Standalone rrule Library (npm-style rrule port)
- **Components:** Standalone `rrule` package (PyPI alternative to python-dateutil)
- **Why rejected:**
  - Less mature: Fewer years in production compared to python-dateutil
  - Smaller community: python-dateutil has broader adoption, more Stack Overflow answers, better documentation
  - No clear advantage: Both implement RFC 5545, but python-dateutil is part of standard Python tooling

### Alternative D: Cron-style Recurrence (e.g., "0 9 * * 1" for 9am every Monday)
- **Components:** Cron expression parser (croniter library) + custom validation
- **Why rejected:**
  - Not user-friendly: Cron syntax is cryptic for non-developers ("0 9 * * 1" is not intuitive)
  - Limited expressiveness: Cron doesn't support "every other week", "first Monday of month", or COUNT/UNTIL
  - Server-centric: Cron is for scheduled jobs, not user-facing recurrence rules
  - No industry standard: Users expect calendar-style recurrence, not server cron

## References

- Feature Spec: [specs/002-event-driven/spec.md](../../specs/002-event-driven/spec.md) (FR-017 through FR-024)
- Implementation Plan: [specs/002-event-driven/plan.md](../../specs/002-event-driven/plan.md)
- Research Doc: [specs/002-event-driven/research.md](../../specs/002-event-driven/research.md) (Section 3: iCalendar RRULE Parsing)
- Data Model: [specs/002-event-driven/data-model.md](../../specs/002-event-driven/data-model.md) (Recurring Task Service data flow)
- Related ADRs: ADR-0020 (Event-Driven Architecture Stack)
- RFC 5545 Spec: https://datatracker.ietf.org/doc/html/rfc5545 (iCalendar standard)
