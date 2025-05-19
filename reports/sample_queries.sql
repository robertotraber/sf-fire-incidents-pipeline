-- Sample queries to demonstrate the data model usage

-- 1. Monthly incidents by district (last 6 months)
SELECT 
    district,
    month,
    total_incidents,
    total_property_loss,
    total_civilian_injuries
FROM analytics.fire_incidents_by_district
WHERE month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY district, month;

-- 2. Peak hours for fire incidents
SELECT 
    incident_hour,
    SUM(total_incidents) as total_incidents
FROM analytics.fire_incidents_by_time
GROUP BY incident_hour
ORDER BY total_incidents DESC
LIMIT 10;

-- 3. Top 5 districts by total property loss
SELECT 
    district,
    SUM(total_property_loss) as total_loss,
    COUNT(*) as incident_count
FROM analytics.fire_incidents_by_district
WHERE month >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY district
ORDER BY total_loss DESC
LIMIT 5;

-- 4. Battalion performance comparison
SELECT 
    battalion,
    AVG(avg_suppression_units) as avg_units_deployed,
    AVG(avg_suppression_personnel) as avg_personnel,
    SUM(total_incidents) as total_incidents
FROM analytics.fire_incidents_by_battalion
WHERE month >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY battalion
ORDER BY total_incidents DESC;

-- 5. Day of week pattern analysis
SELECT 
    CASE day_of_week
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    AVG(total_incidents) as avg_incidents_per_day
FROM analytics.fire_incidents_by_time
GROUP BY day_of_week
ORDER BY day_of_week;

-- 6. Seasonal trends
SELECT 
    EXTRACT(month FROM incident_date_month) as month_num,
    TO_CHAR(incident_date_month, 'Month') as month_name,
    AVG(total_incidents) as avg_incidents
FROM analytics.fire_incidents_by_time
GROUP BY EXTRACT(month FROM incident_date_month), TO_CHAR(incident_date_month, 'Month')
ORDER BY month_num;