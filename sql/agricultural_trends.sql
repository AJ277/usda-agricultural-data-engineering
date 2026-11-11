-- Run against the gold_metrics temporary view created by the Spark application.
-- Never aggregate production and yield quantities together or mix units.
SELECT year, commodity_desc, statisticcat_desc, unit_desc,
       COUNT(DISTINCT state_name) AS states,
       SUM(reported_value) AS state_values_total
FROM gold_metrics
GROUP BY year, commodity_desc, statisticcat_desc, unit_desc
ORDER BY year, commodity_desc, statisticcat_desc;

-- Examples of targeted comparisons require same units and statistic category.
SELECT year, state_name, commodity_desc, reported_value
FROM gold_metrics
WHERE commodity_desc = 'CORN'
  AND statisticcat_desc = 'YIELD'
  AND unit_desc = 'BU / ACRE'
ORDER BY year, state_name;
