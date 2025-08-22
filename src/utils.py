import math

def isNone(value):
    return value is None or (isinstance(value, float) and math.isnan(value))

