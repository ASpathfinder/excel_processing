import pandas as pd


def load_excel(**kwargs):
    system_df = pd.read_excel(**kwargs)
    return system_df
