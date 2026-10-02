import random
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine, text


DATABASE_URL = (
    "postgresql+psycopg2://sattwik@localhost:5432/healthcare_operations"
)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31, 23, 59)

RANDOM_SEED = 42
NUM_ENCOUNTERS = 100_000

random.seed(RANDOM_SEED)


print("Connecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


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


def random_timestamp(start, end):
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


def choose_department():
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
    levels = [1, 2, 3, 4, 5]

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

    return max(staffing, 2)


def calculate_wait_time(
    department,
    triage_level,
    staffing_level,
    timestamp,
):
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

    return max(1, base_wait)


def choose_admission(
    department,
    triage_level,
):
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
    if not admission_flag:
        return random.randint(60, 480)

    if department == "ICU":
        return random.randint(2880, 10080)

    if department == "Surgery":
        return random.randint(1440, 7200)

    if department == "Cardiology":
        return random.randint(1440, 5760)

    if triage_level <= 2:
        return random.randint(1440, 5760)

    return random.randint(720, 4320)


print(
    f"Generating {NUM_ENCOUNTERS:,} synthetic encounters..."
)

records = []

hospital_records = hospitals.to_dict("records")

hospital_weights = hospitals[
    "facility_volume_weight"
].tolist()


for i in range(
    1,
    NUM_ENCOUNTERS + 1,
):

    hospital = random.choices(
        hospital_records,
        weights=hospital_weights,
        k=1,
    )[0]

    facility_id = hospital["facility_id"]

    patient_id = (
        f"SYN-PAT-"
        f"{random.randint(1, 50_000):06d}"
    )

    arrival_time = random_timestamp(
        START_DATE,
        END_DATE,
    )

    department = choose_department()

    triage_level = choose_triage_level()

    staffing_level = calculate_staffing(
        arrival_time,
        department,
    )

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

    admission_flag = choose_admission(
        department,
        triage_level,
    )

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

    discharge_disposition = choose_disposition(
        admission_flag
    )

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

    if i % 10_000 == 0:
        print(
            f"  Generated {i:,} encounters..."
        )


df = pd.DataFrame(records)

print()
print("Synthetic dataset created.")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


print()
print("Running data-quality checks...")


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


if not df[
    "triage_level"
].between(
    1,
    5,
).all():

    raise ValueError(
        "Invalid triage level detected."
    )

print("✓ Triage levels are valid.")


if (
    df["wait_time_minutes"] < 0
).any():

    raise ValueError(
        "Negative wait time detected."
    )

print("✓ Wait times are valid.")


if (
    df["length_of_stay_minutes"] < 0
).any():

    raise ValueError(
        "Negative length of stay detected."
    )

print("✓ Length-of-stay values are valid.")


if not (
    df["provider_seen_time"]
    >= df["arrival_time"]
).all():

    raise ValueError(
        "Provider timestamp occurs before arrival."
    )

print("✓ Provider timestamps are valid.")


if not (
    df["discharge_time"]
    >= df["arrival_time"]
).all():

    raise ValueError(
        "Discharge timestamp occurs before arrival."
    )

print("✓ Discharge timestamps are valid.")


print()
print("Loading encounters into PostgreSQL...")


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