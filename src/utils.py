import math

from pandas.errors import IntCastingNaNError


def isNone(value):
    return value is None or (isinstance(value, float) and math.isnan(value))

def force_int_ids(df):
    df = df.copy()
    for column in df.columns:
        if column.endswith("_id"):
            try:
                df[column] = df[column].astype(int)
            except (IntCastingNaNError, TypeError):
                df[column] = df[column].astype(float)
    return df