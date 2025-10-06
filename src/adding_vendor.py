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

    def save_vendor(self, db_manager):
        print("----- saving")
        vendor_id = st.session_state["selected_vendor_id"]
        vendor_name = st.session_state["vendor_name_input"]
        default_category = st.session_state["default_category_input"]
        default_category_id = db_manager.categories.get_id_from_value("name", default_category)
        default_location = st.session_state["default_location_input"]
        default_location_id = db_manager.shop_locations.get_id_from_value("shop_location", default_location)

        vendor_data = {
            "name": vendor_name,
            "default_category_id": default_category_id,
            "default_location_id": default_location_id
        }

        if vendor_id is None:
            vendor_id = db_manager.db.create_row(
                db_manager.vendors.TABLE,
                vendor_data
            )
        else:
            db_manager.db.update_row(
                db_manager.vendors.TABLE,
                vendor_data,
                "vendor_id",
                vendor_id
            )

        ## save changed locations
        existing_location = db_manager.shop_locations.get_filtered_df("vendor_id", vendor_id)
        for i, row in self.get_df().iterrows():
            name = st.session_state.get(f"location_name_input_{i}", row["name"])
            location_id = row["location_id"]
            if location_id is not None:
                # edit existing location
                row_filter = existing_location["shop_location_id"]==location_id
                existing_row = existing_location[row_filter].iloc[0]
                existing_location = existing_location[
                    existing_location["shop_location_id"]!=location_id
                ]
                if name != existing_row["shop_location"]:
                    db_manager.db.update_row(
                        db_manager.shop_locations.TABLE,
                        {"shop_location": name},
                        "location_id",
                        location_id
                    )
            else:
                # create new location
                db_manager.db.create_row(
                    db_manager.shop_locations.TABLE,
                    {"shop_location": name}
                )

        # delete removed rows
        for i, row in existing_location.iterrows():
            db_manager.db.delete(
                db_manager.shop_locations.TABLE,
                "location_id",
                row["location_id"]
            )

        st.toast(f"Vendor {vendor_id} Saved", icon="✔️")

    def delete_vendor(self, db_manager):
        vendor_id = st.session_state["selected_vendor_id"]

        db_manager.db.delete(
            db_manager.vendors.TABLE,
            "vendor_id",
            vendor_id
        )

        st.session_state["delete_vendor_input"] = True
        st.toast(f"Vendor {vendor_id} Deleted", icon="✔️")

    def clear_input(self):
        st.session_state["vendor_locations_display_df"] = pd.DataFrame(
            columns=self.get_df().columns
        )
        st.session_state["default_category_input"] = None
        st.session_state["default_location_input"] = None
        st.session_state["vendor_name_input"] = None

    # def edit_name(self, index):
    #     st.session_state["editing_locations_data"]
