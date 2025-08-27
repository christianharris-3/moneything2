import streamlit as st
from src.db_manager import DatabaseManager
import src.utils as utils

from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode

def double_run():
    if "has_rerun" not in st.session_state:
        st.session_state["has_rerun"] = False

    if not st.session_state["has_rerun"]:
        st.session_state["has_rerun"] = True
        st.rerun()
    else:
        st.session_state["has_rerun"] = False

if __name__ == "__main__":
    db_manager = DatabaseManager()

    input_tab, data_base, data_tab = st.tabs(["Input Spending", "DataBase", "View Data"])
    with input_tab:

        with st.expander("Add Spending"):
            shop_brand = st.selectbox("Shop Name", db_manager.get_all_shop_brands(), accept_new_options=True)

            selected_shop_locations = db_manager.get_shop_locations(shop_brand)
            if selected_shop_locations != []:
                shop_location = st.selectbox("Location Name", selected_shop_locations, accept_new_options=True)

            spending_date = st.date_input("Spending Date")

            st.markdown("## Items")

            item_name = st.selectbox("Add Item", db_manager.get_all_products(shop_brand), accept_new_options=True)

            # with st.button("Add"):
                # if item_name
                # add_item(item_name)


    with data_base:

        with st.expander("Products"):
            db_manager.save_products_df_changes(
                utils.data_editor(
                    db_manager.get_products_display_df(),
                    {
                        "ID": {"type":"number", "editable": False},
                        "Price": {"type": "number", "format": "£%.2f"},
                        "Shop": {"type": "select", "options": db_manager.get_all_shop_brands()},
                        "Category": {"type": "select", "options": db_manager.get_all_category_strings()}
                    },
                )
            )

        with st.expander("Shops"):
            db_manager.save_shops_df_changes(
                utils.data_editor(
                    db_manager.get_shops_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                    },
                )
            )

        with st.expander("Categories"):
            db_manager.save_categories_df_changes(
                utils.data_editor(
                    db_manager.get_categories_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Importance": {"type": "number"},
                        "Parent Category": {"type": "select", "options": db_manager.get_all_categories()}
                    },
                )
            )

        with st.expander("ShopLocations"):
            db_manager.save_locations_df_changes(
                utils.data_editor(
                    db_manager.get_locations_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Brand": {"type": "select", "options": db_manager.get_all_shop_brands()}
                    },
                )
            )


    double_run()




