# Pilot Program Metrics & KPIs

## Overview

This document outlines key metrics to track during the pilot program to demonstrate Lease Peace's value proposition.

## Primary Success Metrics

### 1. Conflict Reduction
**Target**: 50%+ reduction in reported conflicts

**SQL Query**:
```sql
-- Compare conflicts before/after Lease Peace
WITH monthly_conflicts AS (
  SELECT
    DATE_TRUNC('month', created_at) as month,
    property_id,
    COUNT(*) as conflict_count
  FROM conflict_reports
  GROUP BY month, property_id
)
SELECT
  property_id,
  AVG(CASE WHEN month < '2024-06-01' THEN conflict_count END) as pre_lease_peace_avg,
  AVG(CASE WHEN month >= '2024-06-01' THEN conflict_count END) as post_lease_peace_avg,
  ROUND(
    (AVG(CASE WHEN month < '2024-06-01' THEN conflict_count END) -
     AVG(CASE WHEN month >= '2024-06-01' THEN conflict_count END)) * 100.0 /
    AVG(CASE WHEN month < '2024-06-01' THEN conflict_count END),
    2
  ) as percent_reduction
FROM monthly_conflicts
GROUP BY property_id;
```

### 2. Renewal Rate
**Target**: 30%+ increase in lease renewals

**SQL Query**:
```sql
SELECT
  property_id,
  COUNT(*) FILTER (WHERE is_renewed = true) as renewals,
  COUNT(*) as total_leases,
  ROUND(COUNT(*) FILTER (WHERE is_renewed = true) * 100.0 / COUNT(*), 2) as renewal_rate
FROM move_ins
WHERE move_out_date IS NOT NULL OR move_in_date < NOW() - INTERVAL '6 months'
GROUP BY property_id;
```

### 3. Average Lease Duration
**Target**: 20%+ increase in average stay

**SQL Query**:
```sql
SELECT
  property_id,
  AVG(EXTRACT(EPOCH FROM (COALESCE(move_out_date, NOW()) - move_in_date)) / 86400) as avg_days_stayed,
  COUNT(*) as total_move_ins
FROM move_ins
JOIN beds ON move_ins.bed_id = beds.id
JOIN rooms ON beds.room_id = rooms.id
JOIN units ON rooms.unit_id = units.id
JOIN properties ON units.property_id = properties.id
GROUP BY property_id;
```

## Secondary Metrics

### 4. Match Quality (Resident Satisfaction)
**SQL Query**:
```sql
SELECT
  survey_type,
  AVG(satisfaction_score) as avg_satisfaction,
  AVG(match_accuracy_score) as avg_match_accuracy,
  COUNT(*) FILTER (WHERE would_recommend = true) * 100.0 / COUNT(*) as recommend_rate
FROM feedback_surveys
GROUP BY survey_type;
```

### 5. Time to Fill Vacancy
**SQL Query**:
```sql
-- Track how quickly beds are filled after running Lease Peace matching
SELECT
  property_id,
  AVG(EXTRACT(EPOCH FROM (move_in_date - match_run_date)) / 86400) as avg_days_to_fill
FROM (
  SELECT
    mi.move_in_date,
    mr.created_at as match_run_date,
    p.id as property_id
  FROM move_ins mi
  JOIN beds b ON mi.bed_id = b.id
  JOIN rooms r ON b.room_id = r.id
  JOIN units u ON r.unit_id = u.id
  JOIN properties p ON u.property_id = p.id
  JOIN match_runs mr ON mr.property_id = p.id
  WHERE mi.move_in_date >= mr.created_at
) subq
GROUP BY property_id;
```

### 6. Operator Engagement
**SQL Query**:
```sql
-- Match runs per month
SELECT
  operator_org_id,
  DATE_TRUNC('month', created_at) as month,
  COUNT(*) as match_runs,
  COUNT(*) FILTER (WHERE status = 'completed') as completed_runs
FROM match_runs
GROUP BY operator_org_id, month
ORDER BY month DESC;
```

### 7. Questionnaire Completion Rate
**SQL Query**:
```sql
SELECT
  COUNT(*) FILTER (WHERE questionnaire_completed = true) * 100.0 / COUNT(*) as completion_rate,
  COUNT(*) as total_residents
FROM resident_profiles;
```

## Event Tracking

### Key Events to Monitor
```sql
-- Event funnel analysis
SELECT
  event_name,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(*) as total_events
FROM events
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY event_name
ORDER BY total_events DESC;
```

## Dashboard Queries

### Operator Dashboard - Pilot Success
```sql
-- Overall pilot performance
SELECT
  'Total Properties' as metric, COUNT(*)::text as value
FROM properties
UNION ALL
SELECT
  'Total Applicants', COUNT(*)::text
FROM applicant_pool
WHERE status = 'approved'
UNION ALL
SELECT
  'Match Runs Completed', COUNT(*)::text
FROM match_runs
WHERE status = 'completed'
UNION ALL
SELECT
  'Avg Compatibility Score', ROUND(AVG(compatibility_score), 1)::text
FROM match_results
UNION ALL
SELECT
  'Low Risk Matches %',
  ROUND(COUNT(*) FILTER (WHERE risk_level = 'low') * 100.0 / COUNT(*), 1)::text
FROM match_results;
```

### Conflict Category Breakdown
```sql
-- Most common conflict categories
SELECT
  category,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM conflict_reports
GROUP BY category
ORDER BY count DESC;
```

### Risk Prediction Accuracy
```sql
-- How well do risk predictions correlate with actual conflicts?
WITH predictions AS (
  SELECT
    mr.resident_a_id,
    mr.resident_b_id,
    mr.risk_level,
    mr.risk_score,
    mr.created_at as match_date
  FROM match_results mr
),
actual_conflicts AS (
  SELECT
    cr.unit_id,
    cr.created_at as conflict_date,
    cr.severity
  FROM conflict_reports cr
)
-- This requires more complex join logic based on your move-in tracking
SELECT
  risk_level,
  COUNT(*) as predictions_made,
  -- Add conflict correlation logic
  'TBD' as actual_conflicts
FROM predictions
GROUP BY risk_level;
```

## Weekly Pilot Report

Run this query weekly to generate pilot status:

```sql
-- Weekly Pilot Report
WITH weekly_stats AS (
  SELECT
    DATE_TRUNC('week', NOW()) as week_start,

    -- Matching activity
    (SELECT COUNT(*) FROM match_runs
     WHERE created_at >= DATE_TRUNC('week', NOW())) as matches_this_week,

    -- New applicants
    (SELECT COUNT(*) FROM applicant_pool
     WHERE applied_at >= DATE_TRUNC('week', NOW())) as new_applicants,

    -- Move-ins
    (SELECT COUNT(*) FROM move_ins
     WHERE move_in_date >= DATE_TRUNC('week', NOW())) as move_ins,

    -- Conflicts
    (SELECT COUNT(*) FROM conflict_reports
     WHERE created_at >= DATE_TRUNC('week', NOW())) as conflicts,

    -- Feedback
    (SELECT AVG(satisfaction_score) FROM feedback_surveys
     WHERE created_at >= DATE_TRUNC('week', NOW())) as avg_satisfaction
)
SELECT * FROM weekly_stats;
```

## Export for Reporting

```bash
# Export metrics to CSV
docker-compose exec db psql -U leasepeace -d leasepeace -c "COPY (
  SELECT
    DATE(created_at) as date,
    event_name,
    COUNT(*) as count
  FROM events
  WHERE created_at >= NOW() - INTERVAL '30 days'
  GROUP BY DATE(created_at), event_name
  ORDER BY date DESC
) TO STDOUT WITH CSV HEADER" > pilot_events_$(date +%Y%m%d).csv
```

## Success Criteria for Pilot

### Minimum Viable Proof
- **3+ operators** actively using platform
- **50+ residents** with completed questionnaires
- **25+ match runs** completed
- **30%+ reduction** in reported conflicts
- **20%+ increase** in renewal rates
- **4.0+/5.0** average satisfaction score

### ROI Calculation

For operators:
```
Annual Savings = (Reduced Turnover + Fewer Conflict Hours + Higher Renewals) - Platform Cost

Example:
- 10 units @ $2000/month
- Previous turnover: 50% annually (5 units)
- Turnover cost: $1000 per unit (cleaning, marketing, vacancy)
- Conflict resolution: 10 hours/month @ $50/hour

With Lease Peace:
- Turnover reduced to 30% (3 units) = $2000 saved
- Conflict hours reduced to 3/month = $4200/year saved
- Platform cost: $1500/year

Net Savings: $4700/year per 10-unit property
```
