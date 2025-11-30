import pandas as pd
from IPython.display import display

def print_one_random_record(df):
    print("\nA random record from the dataframe:\n")
    # show full content of a random picked row without truncation
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    display(df.sample(1).T)
