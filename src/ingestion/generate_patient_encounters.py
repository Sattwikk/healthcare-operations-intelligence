import random
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# Configuration
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://sattwik@localhost:5432/healthcare_operations"
)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31, 23, 59)

RANDOM_SEED = 42
NUM_ENCOUNTERS = 100_000

random.seed(RANDOM_SEED)


# ============================================================
# Database connection
# ============================================================

print("Connecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


# ============================================================
# Load hospital capacity profiles
# ============================================================

print("Loading hospital capacity profiles...")

with engine.connect() as connection:
    hospitals = pd.read_sql(
        text(
            """
            SELECT
                facility_id,
                hospital_type,
                emergency_services,
                base_volume_weight,
                capacity_factor
            FROM hospital_capacity_profile
            ORDER BY facility_id;
            """
        ),
        connection,
    )

print(
    f"Loaded {len(hospitals):,} hospital capacity profiles."
)

if hospitals.empty:
    raise ValueError(
        "No hospital capacity profiles found."
    )


# ============================================================
# Calculate facility-level volume weights
# ============================================================

hospitals["facility_volume_weight"] = (
    hospitals["base_volume_weight"]
    * hospitals["capacity_factor"]
)

if (
    hospitals["facility_volume_weight"] <= 0
).any():
    raise ValueError(
        "Invalid facility volume weight detected."
    )

print("✓ Hospital volume weights calculated.")


# ============================================================
# Helper functions
# ============================================================

def random_timestamp(start, end):
    """Generate a random timestamp between two dates."""

    total_seconds = int(
        (end - start).total_seconds()
    )

    random_seconds = random.randint(
        0,
        total_seconds,
    )

    return start + timedelta(
        seconds=random_seconds
    )


def calculate_time_of_day_factor(hour):
    """
    Synthetic patient-demand multiplier by hour.

    Higher values represent periods of higher expected demand.
    These are simulation assumptions, not real hospital statistics.
    """

    hourly_factors = {
        0: 0.55,
        1: 0.50,
        2: 0.45,
        3: 0.45,
        4: 0.50,
        5: 0.55,
        6: 0.65,
        7: 0.80,
        8: 0.95,
        9: 1.05,
        10: 1.10,
        11: 1.15,
        12: 1.20,
        13: 1.20,
        14: 1.15,
        15: 1.10,
        16: 1.15,
        17: 1.25,
        18: 1.30,
        19: 1.25,
        20: 1.15,
        21: 1.00,
        22: 0.85,
        23: 0.70,
    }

    return hourly_factors[hour]


def calculate_weekday_factor(timestamp):
    """
    Synthetic weekday/weekend demand multiplier.

    Monday-Friday receive slightly higher demand.
    """

    weekday = timestamp.weekday()

    if weekday < 5:
        return 1.05

    return 0.90


def calculate_month_factor(month):
    """
    Synthetic seasonal demand multiplier.

    Winter months receive slightly higher demand.
    These are simulation assumptions.
    """

    monthly_factors = {
        1: 1.12,
        2: 1.08,
        3: 1.00,
        4: 0.96,
        5: 0.94,
        6: 0.92,
        7: 0.94,
        8: 0.96,
        9: 0.98,
        10: 1.00,
        11: 1.05,
        12: 1.10,
    }

    return monthly_factors[month]


def choose_department():
    """
    Choose a department using synthetic demand proportions.
    """

    departments = [
        "Emergency Department",
        "General Medicine",
        "Surgery",
        "ICU",
        "Cardiology",
        "Orthopedics",
    ]

    weights = [
        0.45,
        0.20,
        0.10,
        0.07,
        0.08,
        0.10,
    ]

    return random.choices(
        departments,
        weights=weights,
        k=1,
    )[0]


def choose_triage_level():
    """
    Triage levels:

    1 = most urgent
    5 = least urgent
    """

    levels = [
        1,
        2,
        3,
        4,
        5,
    ]

    weights = [
        0.03,
        0.12,
        0.35,
        0.35,
        0.15,
    ]

    return random.choices(
        levels,
        weights=weights,
        k=1,
    )[0]


def calculate_staffing(timestamp, department):
    """
    Generate synthetic staffing based on department and time.
    """

    hour = timestamp.hour

    if department == "ICU":
        base_staff = 12

    elif department == "Emergency Department":
        base_staff = 18

    elif department == "Surgery":
        base_staff = 10

    else:
        base_staff = 8

    if 7 <= hour < 15:
        variation = random.randint(2, 5)

    elif 15 <= hour < 23:
        variation = random.randint(1, 4)

    else:
        variation = random.randint(-2, 1)

    staffing = base_staff + variation

    return max(
        staffing,
        2,
    )


def calculate_wait_time(
    department,
    triage_level,
    staffing_level,
    timestamp,
):
    """
    Generate synthetic provider wait time.
    """

    if triage_level == 1:
        base_wait = random.randint(2, 10)

    elif triage_level == 2:
        base_wait = random.randint(5, 20)

    elif triage_level == 3:
        base_wait = random.randint(10, 40)

    elif triage_level == 4:
        base_wait = random.randint(15, 60)

    else:
        base_wait = random.randint(20, 75)

    if department == "Emergency Department":
        base_wait += random.randint(5, 25)

    if staffing_level < 8:
        base_wait += random.randint(10, 30)

    elif staffing_level > 15:
        base_wait = max(
            1,
            base_wait - random.randint(0, 10),
        )

    if 17 <= timestamp.hour < 23:
        base_wait += random.randint(0, 15)

    return max(
        1,
        base_wait,
    )


def choose_admission(
    department,
    triage_level,
):
    """
    Determine whether the patient is admitted.
    """

    probability = 0.20

    if department == "ICU":
        probability += 0.55

    elif department == "Surgery":
        probability += 0.35

    elif department == "Cardiology":
        probability += 0.25

    if triage_level == 1:
        probability += 0.25

    elif triage_level == 2:
        probability += 0.15

    elif triage_level == 3:
        probability += 0.05

    probability = min(
        probability,
        0.95,
    )

    return random.random() < probability


def choose_disposition(admission_flag):
    """
    Choose a synthetic discharge disposition.
    """

    if admission_flag:

        choices = [
            "Home",
            "Skilled Nursing Facility",
            "Transfer",
            "Home Health",
        ]

        weights = [
            0.55,
            0.15,
            0.15,
            0.15,
        ]

    else:

        choices = [
            "Home",
            "Transfer",
            "Left Without Being Seen",
        ]

        weights = [
            0.85,
            0.10,
            0.05,
        ]

    return random.choices(
        choices,
        weights=weights,
        k=1,
    )[0]


def calculate_length_of_stay(
    admission_flag,
    department,
    triage_level,
):
    """
    Generate synthetic length of stay in minutes.
    """

    if not admission_flag:
        return random.randint(
            60,
            480,
        )

    if department == "ICU":
        return random.randint(
            2880,
            10080,
        )

    if department == "Surgery":
        return random.randint(
            1440,
            7200,
        )

    if department == "Cardiology":
        return random.randint(
            1440,
            5760,
        )

    if triage_level <= 2:
        return random.randint(
            1440,
            5760,
        )

    return random.randint(
        720,
        4320,
    )


# ============================================================
# Prepare hospital selection
# ============================================================

hospital_records = hospitals.to_dict(
    "records"
)

hospital_weights = hospitals[
    "facility_volume_weight"
].tolist()


# ============================================================
# Generate encounters
# ============================================================

print(
    f"Generating {NUM_ENCOUNTERS:,} synthetic encounters..."
)

records = []

generated = 0


while generated < NUM_ENCOUNTERS:

    # --------------------------------------------------------
    # Select a hospital using synthetic volume weighting
    # --------------------------------------------------------

    hospital = random.choices(
        hospital_records,
        weights=hospital_weights,
        k=1,
    )[0]

    facility_id = hospital[
        "facility_id"
    ]


    # --------------------------------------------------------
    # Generate arrival timestamp
    # --------------------------------------------------------

    arrival_time = random_timestamp(
        START_DATE,
        END_DATE,
    )


    # --------------------------------------------------------
    # Department
    # --------------------------------------------------------

    department = choose_department()


    # --------------------------------------------------------
    # Emergency-service validation
    # --------------------------------------------------------

    # Hospitals without emergency services should not receive
    # synthetic Emergency Department encounters.

    if (
        department == "Emergency Department"
        and not hospital["emergency_services"]
    ):
        continue


    # --------------------------------------------------------
    # Demand factors
    # --------------------------------------------------------

    time_factor = calculate_time_of_day_factor(
        arrival_time.hour
    )

    weekday_factor = calculate_weekday_factor(
        arrival_time
    )

    month_factor = calculate_month_factor(
        arrival_time.month
    )


    # --------------------------------------------------------
    # Probabilistic demand filter
    # --------------------------------------------------------

    demand_factor = (
        time_factor
        * weekday_factor
        * month_factor
    )

    # Normalize around approximately 1.0.
    acceptance_probability = min(
        demand_factor / 1.30,
        1.0,
    )

    if random.random() > acceptance_probability:
        continue


    # --------------------------------------------------------
    # Triage
    # --------------------------------------------------------

    triage_level = choose_triage_level()


    # --------------------------------------------------------
    # Staffing
    # --------------------------------------------------------

    staffing_level = calculate_staffing(
        arrival_time,
        department,
    )


    # --------------------------------------------------------
    # Wait time
    # --------------------------------------------------------

    wait_time_minutes = calculate_wait_time(
        department,
        triage_level,
        staffing_level,
        arrival_time,
    )


    provider_seen_time = (
        arrival_time
        + timedelta(
            minutes=wait_time_minutes
        )
    )


    # --------------------------------------------------------
    # Admission
    # --------------------------------------------------------

    admission_flag = choose_admission(
        department,
        triage_level,
    )


    # --------------------------------------------------------
    # Bed assignment
    # --------------------------------------------------------

    if admission_flag:

        bed_assignment_delay = random.randint(
            10,
            180,
        )

        bed_assigned_time = (
            provider_seen_time
            + timedelta(
                minutes=bed_assignment_delay
            )
        )

    else:

        bed_assigned_time = None


    # --------------------------------------------------------
    # Length of stay
    # --------------------------------------------------------

    length_of_stay_minutes = (
        calculate_length_of_stay(
            admission_flag,
            department,
            triage_level,
        )
    )


    discharge_time = (
        arrival_time
        + timedelta(
            minutes=length_of_stay_minutes
        )
    )


    # --------------------------------------------------------
    # Discharge disposition
    # --------------------------------------------------------

    discharge_disposition = (
        choose_disposition(
            admission_flag
        )
    )


    # --------------------------------------------------------
    # Patient ID
    # --------------------------------------------------------

    patient_id = (
        f"SYN-PAT-"
        f"{random.randint(1, 50_000):06d}"
    )


    # --------------------------------------------------------
    # Store encounter
    # --------------------------------------------------------

    records.append(
        {
            "facility_id": facility_id,
            "patient_id": patient_id,
            "arrival_time": arrival_time,
            "provider_seen_time": provider_seen_time,
            "bed_assigned_time": bed_assigned_time,
            "discharge_time": discharge_time,
            "department": department,
            "triage_level": triage_level,
            "admission_flag": admission_flag,
            "discharge_disposition": discharge_disposition,
            "staffing_level": staffing_level,
            "wait_time_minutes": wait_time_minutes,
            "length_of_stay_minutes": length_of_stay_minutes,
        }
    )


    generated += 1


    if generated % 10_000 == 0:

        print(
            f"  Generated {generated:,} encounters..."
        )


# ============================================================
# Create DataFrame
# ============================================================

df = pd.DataFrame(
    records
)

print()
print(
    "Synthetic dataset created."
)

print(
    f"Rows: {len(df):,}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ============================================================
# Data-quality validation
# ============================================================

print()
print(
    "Running data-quality checks..."
)


# Facility IDs must exist.
valid_facilities = set(
    hospitals["facility_id"]
)

if not df[
    "facility_id"
].isin(
    valid_facilities
).all():

    raise ValueError(
        "Some encounters reference unknown facility IDs."
    )

print(
    "✓ All facility IDs exist in hospital profile table."
)


# Triage validation.
if not df[
    "triage_level"
].between(
    1,
    5,
).all():

    raise ValueError(
        "Invalid triage level detected."
    )

print(
    "✓ Triage levels are valid."
)


# Wait-time validation.
if (
    df["wait_time_minutes"] < 0
).any():

    raise ValueError(
        "Negative wait time detected."
    )

print(
    "✓ Wait times are valid."
)


# Length-of-stay validation.
if (
    df["length_of_stay_minutes"] < 0
).any():

    raise ValueError(
        "Negative length-of-stay detected."
    )

print(
    "✓ Length-of-stay values are valid."
)


# Provider timestamp validation.
if not (
    df["provider_seen_time"]
    >= df["arrival_time"]
).all():

    raise ValueError(
        "Provider timestamp occurs before arrival."
    )

print(
    "✓ Provider timestamps are valid."
)


# Discharge timestamp validation.
if not (
    df["discharge_time"]
    >= df["arrival_time"]
).all():

    raise ValueError(
        "Discharge timestamp occurs before arrival."
    )

print(
    "✓ Discharge timestamps are valid."
)


# Emergency-service validation.
ed_without_service = df[
    df["department"] == "Emergency Department"
].merge(
    hospitals[
        [
            "facility_id",
            "emergency_services",
        ]
    ],
    on="facility_id",
    how="left",
)

if (
    ~ed_without_service[
        "emergency_services"
    ]
).any():

    raise ValueError(
        "Emergency Department encounter "
        "assigned to hospital without "
        "emergency services."
    )

print(
    "✓ Emergency-service rules are valid."
)


# ============================================================
# Load into PostgreSQL
# ============================================================

print()
print(
    "Loading encounters into PostgreSQL..."
)


with engine.begin() as connection:

    connection.execute(
        text(
            "TRUNCATE TABLE patient_encounters;"
        )
    )

    df.to_sql(
        "patient_encounters",
        connection,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )


# ============================================================
# Final validation
# ============================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM patient_encounters;
            """
        )
    )

    count = result.scalar()


print()
print(
    f"Successfully loaded {count:,} encounters."
)


if count != len(df):

    raise ValueError(
        f"Record count mismatch: "
        f"expected {len(df):,}, "
        f"found {count:,}."
    )


print(
    "✓ PostgreSQL encounter data validation passed."
)

print()
print(
    "Patient-flow data generation complete!"
)
