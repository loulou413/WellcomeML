import pandas as pd

def format_row(row, exclude):
    parts = []
    for col in row.index:
        if col not in exclude:
            col_upper = col.upper()
            value = row[col]
            # Remplacer NaN par chaîne vide
            if pd.isna(value):
                value = ""
            parts.append(f"[{col_upper}: {{{value}}}]")
    return " ".join(parts)
