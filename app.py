import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


def load_data(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(
            filepath,
            parse_dates=["ANCHORAGE_DT", "BERTHING_DATE", "SAILED_DT", "REG_DT"],
            dayfirst=True
        )
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()


def clean_and_save(df: pd.DataFrame) -> pd.DataFrame:
    date_columns = ["ANCHORAGE_DT", "BERTHING_DATE", "SAILED_DT", "REG_DT"]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    if "VESSEL_NAME" in df.columns:
        df["VESSEL_NAME"] = df["VESSEL_NAME"].str.strip().str.title()

    if "CARGO_TONNAGE" in df.columns:
        df["CARGO_TONNAGE"] = pd.to_numeric(df["CARGO_TONNAGE"], errors="coerce")


    df.to_csv("cleaned_dataset.csv", index=False)


    csv_data = df.to_csv(index=False).encode("utf-8")
    st.success("Dataset cleaned and saved.")
    st.download_button(
        label="Download Cleaned Dataset",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )
    return df


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "BERTHING_DATE" in df.columns and "SAILED_DT" in df.columns:
        df["TURNAROUND_HOURS"] = (df["SAILED_DT"] - df["BERTHING_DATE"]).dt.total_seconds() / 3600
    return df


def summarize_data(df: pd.DataFrame) -> None:
    st.subheader("Dataset Overview")
    st.dataframe(df.head(200))

    st.subheader("Cargo Summary")
    avg_cargo = df["CARGO_TONNAGE"].mean()
    st.metric("Average Cargo Tonnage (tons)", f"{avg_cargo:.2f}")

    if "TURNAROUND_HOURS" in df.columns:
        avg_turnaround = df["TURNAROUND_HOURS"].mean()
        st.metric("Average Turnaround Time (hours)", f"{avg_turnaround:.2f}")


def get_active_vessels(df: pd.DataFrame) -> pd.DataFrame:
    active_vessels = df[(df["BERTHING_DATE"].notnull()) & (df["SAILED_DT"].isnull())]
    return active_vessels[["VESSEL_NO", "VESSEL_NAME", "VESSEL_CALL_ID", "BERTHING_DATE", "BERTHING_BERTH_CODE"]]


def visualize_cargo(df: pd.DataFrame) -> None:
    if "VESSEL_CALL_ID" not in df.columns or "CARGO_TONNAGE" not in df.columns:
        st.warning("Required columns not found for visualization.")
        return

    cargo_summary = df.groupby("VESSEL_CALL_ID")["CARGO_TONNAGE"].sum()
    cargo_summary.index = cargo_summary.index.astype(int)

    fig, ax = plt.subplots(figsize=(30, 10))
    cargo_summary.plot(
        kind="bar",
        color="skyblue",
        edgecolor="black",
        alpha=0.7,
        ax=ax
    )
    ax.set_xlabel("Vessel Call ID (sample)")
    ax.set_ylabel("Cargo Tonnage (metric tons, MT)")
    ax.set_title("Cargo Tonnage by Vessel Call ID")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def main(filepath: str) -> None:
    st.title("Vessel Data Analysis Dashboard")

    df = load_data(filepath)
    if df.empty:
        st.error("No data available.")
        return

    df = clean_and_save(df)
    df = process_data(df)

    summarize_data(df)

    st.subheader("Active Vessels")
    active_vessels = get_active_vessels(df)
    if active_vessels.empty:
        st.info("No active vessels found.")
    else:
        st.dataframe(active_vessels)

    st.subheader("Cargo Visualization")
    visualize_cargo(df)


if __name__ == "__main__":
    csv_file = "vessel_calls.csv"
    main(csv_file)
