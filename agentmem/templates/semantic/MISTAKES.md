# Mistakes

Mistakes made and lessons learned. Review before similar tasks.

## Deployed migration without checking data volume
- **Date:** 2026-02-10
- **Impact:** 45-minute downtime on [[production]]
- **Root cause:** Migration locked table with 50M rows, no batching
- **Lesson:** Always check row count before running ALTER TABLE. Use batched migrations for tables > 1M rows.
- **Tags:** [[database]], [[migration]], [[production]], [[downtime]]

## Assumed test environment matched production config
- **Date:** 2026-03-01
- **Impact:** Bug in [[payment-service]] not caught until staging
- **Root cause:** Test DB used SQLite, production uses [[PostgreSQL]] with different JSON handling
- **Lesson:** Integration tests must use the same database engine as production.
- **Tags:** [[testing]], [[environment-parity]], [[PostgreSQL]]
