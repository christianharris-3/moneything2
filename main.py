import streamlit as st
from src.db_manager import DatabaseManager
from src.adding_spending import AddingSpending
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

        adding_spending = AddingSpending(st.session_state, db_manager)

        adding_spending.set_shop_brand(
            st.selectbox("Shop Name", db_manager.get_all_shop_brands(), accept_new_options=True)
        )
        selected_shop_locations = db_manager.get_shop_locations(adding_spending.shop_brand)
        if selected_shop_locations != []:
            adding_spending.set_shop_location(
                st.selectbox("Location Name", selected_shop_locations, accept_new_options=True)
            )
        adding_spending.set_spending_date(
            st.date_input("Spending Date", format="DD/MM/YYYY")
        )
        adding_spending.set_spending_time(
            st.time_input("Spending Time", value=None)
        )

        st.markdown("## Items")

        selected_product = st.selectbox(
            "Add Item",
            db_manager.get_all_products(adding_spending.shop_brand),
            accept_new_options=True
        )

        if st.button("Add"):
            adding_spending.add_product(selected_product)

        st.session_state["adding_spending_df"] = adding_spending.from_display_df(
            utils.data_editor(
                adding_spending.to_display_df(),
            )
        )


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




