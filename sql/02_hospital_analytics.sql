-- ============================================================
-- Healthcare Operations Intelligence Platform
-- Hospital Analytics
-- ============================================================


-- ------------------------------------------------------------
-- 1. Total number of hospitals
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_hospitals
FROM hospitals;


-- ------------------------------------------------------------
-- 2. Hospitals by state
-- ------------------------------------------------------------

SELECT
    state,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY state
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 3. Hospitals by hospital type
-- ------------------------------------------------------------

SELECT
    hospital_type,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY hospital_type
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 4. Hospitals by ownership
-- ------------------------------------------------------------

SELECT
    hospital_ownership,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY hospital_ownership
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 5. Emergency services availability
-- ------------------------------------------------------------

SELECT
    emergency_services,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY emergency_services
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 6. Hospitals by state and hospital type
-- ------------------------------------------------------------

SELECT
    state,
    hospital_type,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY
    state,
    hospital_type
ORDER BY
    state,
    hospital_count DESC;


-- ------------------------------------------------------------
-- 7. Hospitals with an overall rating
-- ------------------------------------------------------------

SELECT
    hospital_overall_rating,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY hospital_overall_rating
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 8. Hospitals offering emergency services by state
-- ------------------------------------------------------------

SELECT
    state,
    COUNT(*) AS total_hospitals,
    SUM(
        CASE
            WHEN emergency_services = TRUE THEN 1
            ELSE 0
        END
    ) AS hospitals_with_emergency_services
FROM hospitals
GROUP BY state
ORDER BY total_hospitals DESC;
-- ============================================================
-- Business Analysis Queries
-- ============================================================


-- ------------------------------------------------------------
-- 9. States with the highest number of emergency-service
--    hospitals
-- ------------------------------------------------------------

SELECT
    state,
    COUNT(*) AS total_hospitals,
    COUNT(*) FILTER (
        WHERE emergency_services = TRUE
    ) AS emergency_service_hospitals,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE emergency_services = TRUE
        ) / COUNT(*),
        2
    ) AS emergency_service_percentage
FROM hospitals
GROUP BY state
ORDER BY emergency_service_percentage DESC;


-- ------------------------------------------------------------
-- 10. Hospital ownership distribution
-- ------------------------------------------------------------

SELECT
    hospital_ownership,
    COUNT(*) AS hospital_count,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_hospitals
FROM hospitals
GROUP BY hospital_ownership
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 11. Hospital type distribution
-- ------------------------------------------------------------

SELECT
    hospital_type,
    COUNT(*) AS hospital_count,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_hospitals
FROM hospitals
GROUP BY hospital_type
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 12. Overall hospital rating distribution
-- ------------------------------------------------------------

SELECT
    hospital_overall_rating,
    COUNT(*) AS hospital_count
FROM hospitals
GROUP BY hospital_overall_rating
ORDER BY hospital_count DESC;


-- ------------------------------------------------------------
-- 13. State-level hospital summary
-- ------------------------------------------------------------

SELECT
    state,
    COUNT(*) AS total_hospitals,

    COUNT(*) FILTER (
        WHERE hospital_type = 'Acute Care Hospitals'
    ) AS acute_care_hospitals,

    COUNT(*) FILTER (
        WHERE hospital_type = 'Critical Access Hospitals'
    ) AS critical_access_hospitals,

    COUNT(*) FILTER (
        WHERE emergency_services = TRUE
    ) AS emergency_service_hospitals

FROM hospitals
GROUP BY state
ORDER BY total_hospitals DESC;