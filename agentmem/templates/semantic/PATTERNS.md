# Patterns

Recurring patterns extracted from outcomes and corrections.

## API timeout usually caused by missing connection pool config
- **Status:** active
- **Confidence:** high
- **Evidence:** Seen 3 times in [[payment-service]], [[auth-service]], [[notification-service]]
- **Rule:** When debugging API timeouts, check connection pool settings first
- **Tags:** [[API]], [[timeout]], [[connection-pooling]]

## User prefers explicit error messages over generic ones
- **Status:** active
- **Confidence:** high
- **Evidence:** Corrected generic error handling twice (2026-02-20, 2026-03-05)
- **Rule:** Always include specific error context (what failed, why, what to do)
- **Tags:** [[error-handling]], [[user-preference]], [[UX]]
