import pandas as pd
import streamlit as st

class AddingVendor:
    def __init__(self, db_manager):
        if "vendor_locations_display_df" not in st.session_state:
            st.session_state["vendor_locations_display_df"] = pd.DataFrame(
                columns=["location_id", "name", "is_default"]
            )
        if "selected_vendor_id" not in st.session_state:
            st.session_state["selected_vendor_id"] = None

    def get_df(self):
        return st.session_state["vendor_locations_display_df"]

    def add_location(self, name=None, location_id=None):
        df = self.get_df()
        index = 0
        if len(df)>0:
            index = df.tail(1).index[0]+1
        if name is None:
            name = f"New Location ({index})"
        df.loc[index] = (
            {"location_id": location_id, "name": name, "is_default": False}
        )
        st.session_state[f"location_name_input_{index}"] = name

    def delete_location(self, index):
        self.get_df().drop(
            index, inplace=True
        )

    def save_vendor(self):
        print("----- saving")
        for i, row in self.get_df().iterrows():
            name = st.session_state.get(f"location_name_input_{i}", row["name"])
            print(f"saving {i} -> {name} as id {row['location_id']}")

    def clear_input(self):
        st.session_state["vendor_locations_display_df"] = pd.DataFrame(
            columns=self.get_df().columns
        )
        st.session_state["default_category_input"] = None
        st.session_state["default_location_input"] = None
        st.session_state["vendor_name_input"] = None

    # def edit_name(self, index):
    #     st.session_state["editing_locations_data"]
