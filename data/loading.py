import pandas as pd
import gzip
import json
import os

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    data = []
    # Open the gzipped file in text mode ('rt') for reading.
    # This allows us to decompress and read the file line by line,
    # preventing the entire 1.5GB content from being loaded into RAM at once.
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        # Iterate over each line in the file.
        # We assume the file is in JSON Lines format, where each line is a self-contained JSON object.
        for line in f:
            # Parse each line as a JSON object and append it to our list.
            # This processes data incrementally, keeping memory usage low.
            data.append(json.loads(line))
    # Convert the list of dictionaries into a pandas DataFrame.
    # Pandas is optimized for creating DataFrames from such structures efficiently.
    return pd.DataFrame(data)
    