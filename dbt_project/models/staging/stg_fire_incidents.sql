{{ config(materialized='view') }}

WITH source_data AS (
    SELECT * FROM {{ source('raw', 'raw_fire_incidents') }}
),

cleaned_data AS (
    SELECT
        -- Incident identifiers
        incident_number::VARCHAR AS incident_number,
        exposure_number::INT AS exposure_number,
        
        -- Time dimensions
        CAST(incident_date AS TIMESTAMP) AS incident_date,
        DATE_TRUNC('day', CAST(incident_date AS TIMESTAMP)) AS incident_date_day,
        DATE_TRUNC('month', CAST(incident_date AS TIMESTAMP)) AS incident_date_month,
        DATE_TRUNC('year', CAST(incident_date AS TIMESTAMP)) AS incident_date_year,
        EXTRACT(hour FROM CAST(incident_date AS TIMESTAMP)) AS incident_hour,
        EXTRACT(dow FROM CAST(incident_date AS TIMESTAMP)) AS day_of_week,
        
        -- Geographic dimensions
        TRIM(UPPER(neighborhood_district)) AS district,
        battalion::VARCHAR AS battalion,
        TRIM(address) AS address,
        TRIM(city) AS city,
        zipcode::VARCHAR AS zipcode,
        
        -- Incident details
        TRIM(UPPER(primary_situation)) AS primary_situation,
        TRIM(UPPER(mutual_aid)) AS mutual_aid,
        TRIM(UPPER(action_taken_primary)) AS action_taken_primary,
        TRIM(UPPER(action_taken_secondary)) AS action_taken_secondary,
        TRIM(UPPER(action_taken_other)) AS action_taken_other,
        TRIM(UPPER(detector_alerted_occupants)) AS detector_alerted_occupants,
        TRIM(UPPER(property_use)) AS property_use,
        TRIM(UPPER(area_of_fire_origin)) AS area_of_fire_origin,
        TRIM(UPPER(ignition_cause)) AS ignition_cause,
        TRIM(UPPER(ignition_factor_primary)) AS ignition_factor_primary,
        TRIM(UPPER(heat_source)) AS heat_source,
        TRIM(UPPER(item_first_ignited)) AS item_first_ignited,
        TRIM(UPPER(human_factors_associated_with_ignition)) AS human_factors_associated_with_ignition,
        TRIM(UPPER(structure_type)) AS structure_type,
        TRIM(UPPER(structure_status)) AS structure_status,
        TRIM(UPPER(floor_of_fire_origin)) AS floor_of_fire_origin,
        TRIM(UPPER(no_flame_spread)) AS no_flame_spread,
        
        -- Numerical data
        COALESCE(number_of_alarms::INT, 0) AS number_of_alarms,
        COALESCE(estimated_property_loss::FLOAT, 0) AS estimated_property_loss,
        COALESCE(estimated_contents_loss::FLOAT, 0) AS estimated_contents_loss,
        COALESCE(fire_fatalities::INT, 0) AS fire_fatalities,
        COALESCE(fire_injuries::INT, 0) AS fire_injuries,
        COALESCE(civilian_fatalities::INT, 0) AS civilian_fatalities,
        COALESCE(civilian_injuries::INT, 0) AS civilian_injuries,
        COALESCE(number_of_sprinkler_heads_operating::INT, 0) AS number_of_sprinkler_heads_operating,
        
        -- Suppression details
        COALESCE(suppression_units::INT, 0) AS suppression_units,
        COALESCE(suppression_personnel::INT, 0) AS suppression_personnel,
        
        -- Timestamps
        CURRENT_TIMESTAMP AS loaded_at
        
    FROM source_data
    WHERE incident_date IS NOT NULL
)

SELECT * FROM cleaned_data