import pandas as pd
pd.set_option("display.max_columns", None)  # show all columns
pd.set_option("display.width", None)       # don't wrap columns

df = pd.read_csv('vessel_calls.csv')
print(df.head(200))


import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:

    try:
        df = pd.read_csv(
            filepath,
            parse_dates=["ANCHORAGE_DT", "BERTHING_DATE", "SAILED_DT", "REG_DT"],
            dayfirst=True
        )
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()


def process_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    if "BERTHING_DATE" in df.columns and "SAILED_DT" in df.columns:
        df["TURNAROUND_HOURS"] = (df["SAILED_DT"] - df["BERTHING_DATE"]).dt.total_seconds() / 3600
    return df


def summarize_data(df: pd.DataFrame) -> None:

    print("\n---Dataset Overview---")
    print(df.head(200), "\n")

    print("--- Cargo Summary (by Vessel Call ID) ---")


    avg_cargo = df["CARGO_TONNAGE"].mean()
    print(f"Average Cargo Tonnage: {avg_cargo:.2f} tons")

    if "TURNAROUND_HOURS" in df.columns:
        avg_turnaround = df["TURNAROUND_HOURS"].mean()
        print(f"Average Turnaround Time: {avg_turnaround:.2f} hours\n")


def get_active_vessels(df: pd.DataFrame) -> pd.DataFrame:

    active_vessels = df[(df["BERTHING_DATE"].notnull()) & (df["SAILED_DT"].isnull())]
    return active_vessels[["VESSEL_NO", "VESSEL_NAME", "VESSEL_CALL_ID", "BERTHING_DATE", "BERTHING_BERTH_CODE"]]


def visualize_cargo(df: pd.DataFrame) -> None:

    import matplotlib.pyplot as plt

    if "VESSEL_CALL_ID" not in df.columns or "CARGO_TONNAGE" not in df.columns:
        print("Required columns not found for visualization.")
        return

    cargo_summary = df.groupby("VESSEL_CALL_ID")["CARGO_TONNAGE"].sum()
    cargo_summary.index = cargo_summary.index.astype(int)

    plt.figure(figsize=(30, 10))
    cargo_summary.plot(
        kind="bar",
        color="skyblue",
        edgecolor="black",
        alpha=0.7
    )

    plt.xlabel("Vessel Call ID (sample)")
    plt.ylabel("Cargo Tonnage (metric tons, MT)")
    plt.title("Cargo Tonnage by Vessel Call ID")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main(filepath: str) -> None:

    df = load_data(filepath)

    if df.empty:
        print("No data available.")
        return

    df = process_data(df)

    summarize_data(df)

    print("---Active Vessels ---")
    active_vessels = get_active_vessels(df)
    if active_vessels.empty:
        print("No active vessels found.\n")
    else:
        print(active_vessels, "\n")

    visualize_cargo(df)


if __name__ == "__main__":
    csv_file = "vessel_calls.csv"
    main(csv_file)



print(df.head(200))


date_columns = ["ANCHORAGE_DT", "BERTHING_DATE", "SAILED_DT", "REG_DT"]

for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)



if "VESSEL_NAME" in df.columns:
    df["VESSEL_NAME"] = df["VESSEL_NAME"].str.strip().str.title()


if "CARGO_TONNAGE" in df.columns:
    df["CARGO_TONNAGE"] = pd.to_numeric(df["CARGO_TONNAGE"], errors="coerce")

df.to_csv("cleaned_dataset.csv", index=False)

print("Dataset cleaned and saved")