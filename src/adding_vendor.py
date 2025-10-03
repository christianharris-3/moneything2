import pandas as pd
import math
from src.logger import log
import streamlit as st

import src.utils as utils

class AddingVendor:
    def __init__(self, db_manager):
        if "editing_locations_data" not in st.session_state:
            st.session_state["editing_locations_data"] = {
                "locations_display":[]
            }