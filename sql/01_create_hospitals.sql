CREATE TABLE hospitals (
    facility_id VARCHAR(20) PRIMARY KEY,
    facility_name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    state CHAR(2),
    zip_code VARCHAR(10),
    county_parish VARCHAR(100),
    telephone_number VARCHAR(30),

    hospital_type VARCHAR(100),
    hospital_ownership VARCHAR(150),
    emergency_services BOOLEAN,

    birthing_friendly_designation VARCHAR(50),
    hospital_overall_rating VARCHAR(20),
    hospital_overall_rating_footnote TEXT,

    mort_group_measure_count INTEGER,
    count_of_facility_mort_measures INTEGER,
    count_of_mort_measures_better INTEGER,
    count_of_mort_measures_no_different INTEGER,
    count_of_mort_measures_worse INTEGER,
    mort_group_footnote TEXT,

    safety_group_measure_count INTEGER,
    count_of_facility_safety_measures INTEGER,
    count_of_safety_measures_better INTEGER,
    count_of_safety_measures_no_different INTEGER,
    count_of_safety_measures_worse INTEGER,
    safety_group_footnote TEXT,

    readm_group_measure_count INTEGER,
    count_of_facility_readm_measures INTEGER,
    count_of_readm_measures_better INTEGER,
    count_of_readm_measures_no_different INTEGER,
    count_of_readm_measures_worse INTEGER,
    readm_group_footnote TEXT,

    pt_exp_group_measure_count INTEGER,
    count_of_facility_pt_exp_measures INTEGER,
    pt_exp_group_footnote TEXT,

    te_group_measure_count INTEGER,
    count_of_facility_te_measures INTEGER,
    te_group_footnote TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);