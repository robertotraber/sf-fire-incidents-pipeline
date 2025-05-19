
{{ config(materialized='table') }}

SELECT
    battalion,
    DATE_TRUNC('month', incident_date) AS month,
    COUNT(*) AS total_incidents,
    SUM(fire_fatalities) AS total_fire_fatalities,
    SUM(fire_injuries) AS total_fire_injuries,
    SUM(civilian_fatalities) AS total_civilian_fatalities,
    SUM(civilian_injuries) AS total_civilian_injuries,
    SUM(estimated_property_loss) AS total_property_loss,
    SUM(estimated_contents_loss) AS total_contents_loss,
    COUNT(DISTINCT primary_situation) AS unique_situations,
    COUNT(DISTINCT action_taken_primary) AS unique_actions,
    AVG(number_of_alarms::FLOAT) AS avg_alarms_per_incident,
    AVG(suppression_units::FLOAT) AS avg_suppression_units,
    AVG(suppression_personnel::FLOAT) AS avg_suppression_personnel
FROM {{ ref('stg_fire_incidents') }}
WHERE battalion IS NOT NULL
GROUP BY 
    battalion,
    DATE_TRUNC('month', incident_date)