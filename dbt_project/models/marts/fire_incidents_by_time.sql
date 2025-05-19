{{ config(materialized='table') }}

SELECT
    incident_date_day,
    incident_date_month,
    incident_date_year,
    incident_hour,
    day_of_week,
    COUNT(*) AS total_incidents,
    SUM(fire_fatalities) AS total_fire_fatalities,
    SUM(fire_injuries) AS total_fire_injuries,
    SUM(civilian_fatalities) AS total_civilian_fatalities,
    SUM(civilian_injuries) AS total_civilian_injuries,
    SUM(estimated_property_loss) AS total_property_loss,
    SUM(estimated_contents_loss) AS total_contents_loss,
    SUM(number_of_alarms) AS total_alarms,
    AVG(suppression_units::FLOAT) AS avg_suppression_units,
    AVG(suppression_personnel::FLOAT) AS avg_suppression_personnel
FROM {{ ref('stg_fire_incidents') }}
GROUP BY 
    incident_date_day,
    incident_date_month,
    incident_date_year,
    incident_hour,
    day_of_week