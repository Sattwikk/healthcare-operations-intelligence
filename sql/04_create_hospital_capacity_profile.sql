-- ============================================================
-- Healthcare Operations & Patient Flow Intelligence Platform
-- Synthetic Hospital Capacity Profile
-- ============================================================

DROP TABLE IF EXISTS hospital_capacity_profile;

CREATE TABLE hospital_capacity_profile (
    facility_id VARCHAR(20) PRIMARY KEY,

    hospital_type VARCHAR(100) NOT NULL,

    emergency_services BOOLEAN NOT NULL,

    base_volume_weight NUMERIC(5,2) NOT NULL,

    capacity_factor NUMERIC(5,2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Link profile to CMS hospital master table
    CONSTRAINT fk_capacity_facility
        FOREIGN KEY (facility_id)
        REFERENCES hospitals(facility_id),

    -- Synthetic volume weight must be positive
    CONSTRAINT chk_base_volume_weight
        CHECK (base_volume_weight > 0),

    -- Capacity factor must be positive
    CONSTRAINT chk_capacity_factor
        CHECK (capacity_factor > 0)
);


-- ============================================================
-- Populate synthetic hospital capacity profiles
-- ============================================================

INSERT INTO hospital_capacity_profile (
    facility_id,
    hospital_type,
    emergency_services,
    base_volume_weight,
    capacity_factor
)

SELECT
    facility_id,
    hospital_type,
    emergency_services,

    CASE hospital_type
        WHEN 'Acute Care Hospitals'
            THEN 1.00

        WHEN 'Critical Access Hospitals'
            THEN 0.35

        WHEN 'Psychiatric'
            THEN 0.40

        WHEN 'Acute Care - Veterans Administration'
            THEN 0.75

        WHEN 'Childrens'
            THEN 0.70

        WHEN 'Rural Emergency Hospital'
            THEN 0.30

        WHEN 'Acute Care - Department of Defense'
            THEN 0.65

        WHEN 'Long-term'
            THEN 0.20

        ELSE 0.50
    END AS base_volume_weight,

   -- Synthetic facility-specific variation.
-- This is NOT a real-world hospital capacity measurement.
ROUND(
    (
        0.50
        + (
            (
                (
                    ASCII(SUBSTRING(facility_id, 1, 1))
                    + ASCII(SUBSTRING(facility_id, 2, 1))
                    + ASCII(SUBSTRING(facility_id, 3, 1))
                    + ASCII(SUBSTRING(facility_id, 4, 1))
                    + ASCII(SUBSTRING(facility_id, 5, 1))
                    + ASCII(SUBSTRING(facility_id, 6, 1))
                ) % 151
            ) / 100.0
        )
    )::numeric,
    2
) AS capacity_factor

FROM hospitals;


-- ============================================================
-- Validation
-- ============================================================

SELECT
    COUNT(*) AS profile_count,
    COUNT(DISTINCT facility_id) AS unique_facilities,
    ROUND(AVG(base_volume_weight), 2) AS avg_base_volume_weight,
    ROUND(AVG(capacity_factor), 2) AS avg_capacity_factor
FROM hospital_capacity_profile;