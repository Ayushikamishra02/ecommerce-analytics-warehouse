-- Every cohort's month 0 must contain the whole cohort.
select * from {{ ref('mart_cohort_retention') }} where months_since = 0 and retention_rate < 1
