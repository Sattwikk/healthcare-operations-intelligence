import pandas as pd
from sqlalchemy import create_engine, text


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CSV_PATH = "data/processed/cms_hospitals_clean.csv"

DATABASE_URL = (
    "postgresql+psycopg2://sattwik@localhost:5432/healthcare_operations"
)


# --------------------------------------------------
# Load cleaned CMS data
# --------------------------------------------------

print("Loading cleaned CMS hospital data...")

df = pd.read_csv(CSV_PATH)

print(f"Loaded {len(df):,} hospital records.")


# --------------------------------------------------
# Rename columns to match PostgreSQL schema
# --------------------------------------------------

column_mapping = {
    "city_town": "city",
    "meets_criteria_for_birthing_friendly_designation":
        "birthing_friendly_designation",
}

df = df.rename(columns=column_mapping)


# --------------------------------------------------
# Prepare PostgreSQL-compatible values
# --------------------------------------------------

# Convert empty strings to NULL
df = df.replace(r"^\s*$", pd.NA, regex=True)


# --------------------------------------------------
# Connect to PostgreSQL
# --------------------------------------------------

print("Connecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# Load data into hospitals table
# --------------------------------------------------

print("Loading data into PostgreSQL...")

with engine.begin() as connection:

    # Clear existing records so the script can be safely re-run
    connection.execute(text("TRUNCATE TABLE hospitals;"))

    df.to_sql(
        "hospitals",
        connection,
        if_exists="append",
        index=False,
        chunksize=500,
        method="multi",
    )


# --------------------------------------------------
# Validation
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("SELECT COUNT(*) FROM hospitals;")
    )

    count = result.scalar()


print(f"Successfully loaded {count:,} hospital records.")

if count != len(df):
    raise ValueError(
        f"Record count mismatch: expected {len(df):,}, "
        f"but found {count:,} in PostgreSQL."
    )

print("✓ PostgreSQL hospital data validation passed.")