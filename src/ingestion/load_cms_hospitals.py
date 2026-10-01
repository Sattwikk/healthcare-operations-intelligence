from pathlib import Path

import pandas as pd


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Hospital_General_Information.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "cms_hospitals_clean.csv"


def load_raw_data(file_path: Path) -> pd.DataFrame:
    """Load the raw CMS hospital dataset."""
    print(f"Loading: {file_path}")

    df = pd.read_csv(file_path)

    print(f"Loaded {len(df):,} hospital records.")

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the CMS hospital dataset."""

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )

    # ZIP codes should be strings, not numbers
    df["zip_code"] = df["zip_code"].astype(str).str.zfill(5)

    # Convert measure/count columns to numeric
    numeric_columns = [
        "mort_group_measure_count",
        "count_of_facility_mort_measures",
        "count_of_mort_measures_better",
        "count_of_mort_measures_no_different",
        "count_of_mort_measures_worse",
        "safety_group_measure_count",
        "count_of_facility_safety_measures",
        "count_of_safety_measures_better",
        "count_of_safety_measures_no_different",
        "count_of_safety_measures_worse",
        "readm_group_measure_count",
        "count_of_facility_readm_measures",
        "count_of_readm_measures_better",
        "count_of_readm_measures_no_different",
        "count_of_readm_measures_worse",
        "pt_exp_group_measure_count",
        "count_of_facility_pt_exp_measures",
        "te_group_measure_count",
        "count_of_facility_te_measures",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Normalize yes/no fields
    df["emergency_services"] = (
        df["emergency_services"]
        .str.strip()
        .str.lower()
        .map({"yes": True, "no": False})
    )

    # Remove accidental whitespace from text columns
    text_columns = df.select_dtypes(include=["object", "str"]).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    return df


def validate_data(df: pd.DataFrame) -> None:
    """Run basic data-quality checks."""

    print("\nRunning data-quality checks...")

    # Required primary key
    assert df["facility_id"].notna().all(), "Facility ID contains missing values."

    # Facility IDs should be unique
    assert df["facility_id"].is_unique, "Facility IDs are not unique."

    # Expected minimum record count
    assert len(df) > 5000, "Unexpectedly low number of hospital records."

    # Emergency services should only contain True/False after cleaning
    assert df["emergency_services"].notna().all(), (
        "Emergency Services contains unexpected values."
    )

    print("✓ No missing Facility IDs")
    print("✓ Facility IDs are unique")
    print("✓ Record count is greater than 5,000")
    print("✓ Emergency Services values are valid")
    print("✓ Data-quality checks passed")


def save_data(df: pd.DataFrame, output_path: Path) -> None:
    """Save the cleaned dataset."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print(f"\nSaved cleaned dataset to: {output_path}")
    print(f"Final shape: {df.shape}")


def main() -> None:
    """Run the complete ingestion pipeline."""

    raw_df = load_raw_data(RAW_FILE)

    clean_df = clean_data(raw_df)

    validate_data(clean_df)

    save_data(clean_df, OUTPUT_FILE)


if __name__ == "__main__":
    main()