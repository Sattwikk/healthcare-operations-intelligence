-- ============================================================
-- Healthcare Operations & Patient Flow Intelligence Platform
-- Patient Encounter Fact Table
-- ============================================================

DROP TABLE IF EXISTS patient_encounters;

CREATE TABLE patient_encounters (
    encounter_id BIGSERIAL PRIMARY KEY,

    -- Hospital reference
    facility_id VARCHAR(20) NOT NULL,

    -- Synthetic patient identifier
    patient_id VARCHAR(30) NOT NULL,

    -- Encounter timestamps
    arrival_time TIMESTAMP NOT NULL,
    provider_seen_time TIMESTAMP,
    bed_assigned_time TIMESTAMP,
    discharge_time TIMESTAMP,

    -- Operational attributes
    department VARCHAR(50) NOT NULL,
    triage_level INTEGER NOT NULL,

    -- Admission / discharge information
    admission_flag BOOLEAN NOT NULL,
    discharge_disposition VARCHAR(50),

    -- Staffing available during encounter
    staffing_level INTEGER,

    -- Derived operational metrics
    wait_time_minutes INTEGER,
    length_of_stay_minutes INTEGER,

    -- Audit timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key to CMS hospital master data
    CONSTRAINT fk_patient_encounters_facility
        FOREIGN KEY (facility_id)
        REFERENCES hospitals(facility_id),

    -- Triage must be between 1 and 5
    CONSTRAINT chk_triage_level
        CHECK (triage_level BETWEEN 1 AND 5),

    -- Staffing cannot be negative
    CONSTRAINT chk_staffing_level
        CHECK (staffing_level IS NULL OR staffing_level >= 0),

    -- Derived metrics cannot be negative
    CONSTRAINT chk_wait_time
        CHECK (wait_time_minutes IS NULL OR wait_time_minutes >= 0),

    CONSTRAINT chk_length_of_stay
        CHECK (length_of_stay_minutes IS NULL OR length_of_stay_minutes >= 0)
);