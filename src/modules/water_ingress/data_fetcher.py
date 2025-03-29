import pandas as pd
from datetime import datetime
from pathlib import Path


class DataFetcher:
    """
    fast-failing

    Fetches pre-hour close data and hourly ATG observation data for the water_ingress module.
    Data must be provided as CSV files in the input path.
    """

    @staticmethod
    def get_pre_result(current_time: datetime, input_path: Path):
        """
        Load pre-hour close data from pre_result.csv.
        """
        input_file = input_path / "pre_result.csv"
        if not input_file.exists():
            raise FileNotFoundError(f"Expected pre_result.csv at {input_file}")

        df = pd.read_csv(input_file)
        return {"pre_obs_result": df.to_dict(orient="records")}

    @staticmethod
    def get_atg_result(current_time: datetime, input_path: Path):
        """
        Load hourly ATG observation data from atg_result.csv.
        """
        input_file = input_path / "atg_result.csv"
        if not input_file.exists():
            raise FileNotFoundError(f"Expected atg_result.csv at {input_file}")

        df = pd.read_csv(input_file)
        return {
            "last_hour_start": current_time.replace(minute=0, second=0, microsecond=0).isoformat(),
            "atg_result": df.to_dict(orient="records"),
        }
