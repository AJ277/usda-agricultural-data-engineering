-- USDA NASS corn grain yield analytics, 2020–2025
-- Gold table registered as corn_yield.
-- Excludes the aggregate OTHER STATES category.

-- QUERY 1: Top 10 states by 2025 corn yield
SELECT
    state_name,
    year,
    ROUND(reported_value, 2) AS yield_bu_acre
FROM corn_yield
WHERE year = 2025
  AND state_name <> 'OTHER STATES'
  AND commodity_desc = 'CORN'
  AND statisticcat_desc = 'YIELD'
  AND reported_value IS NOT NULL
ORDER BY reported_value DESC
LIMIT 10;

-- QUERY 2: Largest year-over-year declines
WITH annual_changes AS (
    SELECT
        state_name,
        year,
        reported_value AS current_yield,
        LAG(reported_value) OVER (
            PARTITION BY state_name
            ORDER BY year
        ) AS previous_yield,
        LAG(year) OVER (
            PARTITION BY state_name
            ORDER BY year
        ) AS previous_year
    FROM corn_yield
    WHERE state_name <> 'OTHER STATES'
      AND commodity_desc = 'CORN'
      AND statisticcat_desc = 'YIELD'
)
SELECT
    state_name,
    year,
    ROUND(
        100.0 * (current_yield - previous_yield)
        / NULLIF(previous_yield, 0), 2
    ) AS yoy_change_pct
FROM annual_changes
WHERE previous_year = year - 1
  AND previous_yield > 0
ORDER BY yoy_change_pct ASC
LIMIT 10;

-- QUERY 3: Six-year yield volatility
SELECT
    state_name,
    ROUND(AVG(reported_value), 2) AS avg_yield,
    ROUND(STDDEV_SAMP(reported_value), 2) AS yield_stddev,
    COUNT(*) AS observed_years
FROM corn_yield
WHERE state_name <> 'OTHER STATES'
  AND commodity_desc = 'CORN'
  AND statisticcat_desc = 'YIELD'
  AND reported_value IS NOT NULL
GROUP BY state_name
HAVING COUNT(DISTINCT year) = 6
ORDER BY yield_stddev DESC
LIMIT 10;
