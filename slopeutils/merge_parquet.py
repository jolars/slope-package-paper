import glob
import os

import pandas as pd


def merge_parquet_files(directory_path: str) -> pd.DataFrame | None:
    """
    Merge all parquet files in a directory into a single pandas DataFrame.

    Parameters:
    -----------
    directory_path : str
        Path to the directory containing parquet files

    Returns:
    --------
    pandas.DataFrame or None
        Combined DataFrame from all parquet files, or None if no files found
    """
    # Find all parquet files in the specified directory
    parquet_files = glob.glob(os.path.join(directory_path, "*.parquet"))
    print(f"Found {len(parquet_files)} parquet files to merge")

    if not parquet_files:
        print("No parquet files found in the specified directory.")
        return None

    # Read and concatenate all parquet files
    dfs = []
    for file in parquet_files:
        try:
            df = pd.read_parquet(file)
            dfs.append(df)
            print(f"Read {file}: {len(df)} rows")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not dfs:
        print("No valid DataFrames found.")
        return None

    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Created combined DataFrame with {len(combined_df)} rows")

    return combined_df
