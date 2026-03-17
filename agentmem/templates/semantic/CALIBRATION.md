# Calibration

Predictions and their outcomes for confidence tracking.

## Prediction: API refactor will take 3 days
- **Date:** 2026-02-15
- **Confidence:** 70%
- **Actual:** Took 5 days (connection pooling issues unexpected)
- **Delta:** -2 days (underestimate)
- **Lesson:** Add 50% buffer for refactors touching [[infrastructure]]
- **Tags:** [[estimation]], [[API]], [[refactoring]]

## Prediction: New caching layer will reduce latency by 40%
- **Date:** 2026-03-05
- **Confidence:** 60%
- **Actual:** Reduced latency by 55% (better than expected)
- **Delta:** +15% (underestimate of benefit)
- **Lesson:** [[Redis]] caching for read-heavy endpoints is reliably effective
- **Tags:** [[performance]], [[caching]], [[Redis]]
