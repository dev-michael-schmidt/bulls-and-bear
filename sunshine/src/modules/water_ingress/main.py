from datetime import datetime, timezone
import pandas as pd

from data_fetcher import DataFetcher
from data_processor import DataProcessor
from src._internal.context import ModuleExecutionContext

def main(context: ModuleExecutionContext):
    """
    Context: the circumstances that form the setting for an event, and in terms of which it can
    be fully understood and assessed.

    Main entry point for the water_ingress module.
    Steps:
    1. Fetch raw data.
    2. Process the data.
    3. Save the processed result to a CSV.
    """

    input_path = context.input_path
    output_path = context.output_path
    config = context.config  # settings from configuration.toml if needed

    # Current UTC time, used by the data fetcher
    utc_now = datetime.now(timezone.utc)

    # Step 1: Fetch data
    pre_data = DataFetcher.get_pre_result(utc_now, input_path)
    atg_data = DataFetcher.get_atg_result(utc_now, input_path)

    # Step 2: Process data
    processed_pre_data = DataProcessor.process_pre_result(pre_data)
    observations = DataProcessor.build_obs_result(
        atg_result=atg_data["atg_result"],
        pre_dict=processed_pre_data,
        last_hour_start=atg_data["last_hour_start"]
    )

    # Step 3: Save results as a CSV
    output_file = output_path / "water_ingress_observations.csv"
    pd.DataFrame(observations).to_csv(output_file, index=False)

    print(f"[water_ingress] Processing complete. Output saved to {output_file}")
