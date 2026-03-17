# Facts

Known facts with freshness tracking. Review and update regularly.

## Freshness Rules
| Freshness | Review Interval | Action |
|-----------|----------------|--------|
| 🟢 Fresh | < 7 days | Trust as-is |
| 🟡 Aging | 7–30 days | Verify before relying on |
| 🔴 Stale | > 30 days | Must re-verify |

## Facts

### Project uses PostgreSQL 15 for primary database
- **Added:** 2026-03-01
- **Freshness:** 🟢
- **Source:** docker-compose.yml
- **Tags:** [[database]], [[PostgreSQL]], [[infrastructure]]

### API rate limit is 1000 req/min per API key
- **Added:** 2026-02-15
- **Freshness:** 🟡
- **Source:** Confirmed by [[backend-team]] in Slack
- **Tags:** [[API]], [[rate-limiting]], [[backend]]

### Staging deploys run on every merge to `develop` branch
- **Added:** 2026-01-20
- **Freshness:** 🟡
- **Source:** CI/CD pipeline config
- **Tags:** [[deployment]], [[CI-CD]], [[staging]]

### Frontend bundle size budget is 250KB gzipped
- **Added:** 2026-03-10
- **Freshness:** 🟢
- **Source:** Team performance review
- **Tags:** [[frontend]], [[performance]], [[budget]]
