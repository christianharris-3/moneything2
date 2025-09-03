import streamlit as st
st.set_page_config(layout="wide")

from src.db_manager import DatabaseManager
from src.adding_spending import AddingSpending
from src.add_to_db import add_money_store, add_internal_transfer
import src.utils as utils

# TODO: Add Special viewing menu for previous spending + proper edit system for spending
# TODO: Add Menu for current money,:
#  Allow you to enter money values for different store locations, e.g. cash, different bank accounts
#  Use given spending data to graph money stored in each location over time
#  Allow user to log movements between accounts as well (e.g. take money out of atm)
#  Add Spending method to add spending (the money store location used, e.g. cash/bank account)
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)

# TODO: unit test the mother loving fuck out of everything


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

    money_tab, input_tab, data_base, data_tab = st.tabs(["Money Tracker","Input Spending", "DataBase", "View Data"])

    with money_tab:

        with st.expander("Add Money Store"):

            money_store_name = st.text_input("Store Name")

            creation_date = st.date_input("Creation Date", format="DD/MM/YYYY")

            current_money_stored = st.number_input("Current Money Stored")

            if st.button("Add Money Store"):
                add_money_store(
                    db_manager,
                    money_store_name,
                    creation_date,
                    current_money_stored
                )

        with st.expander("Log Internal Transfer"):

            account_column, datetime_column = st.columns(2)

            source_money_store = account_column.selectbox(
                "Source Money Store", db_manager.get_all_money_stores()
            )
            target_money_store = account_column.selectbox(
                "Target Money Store", db_manager.get_all_money_stores()
            )
            transfer_date = datetime_column.date_input(
                "Transfer Date", format="DD/MM/YYYY"
            )
            transfer_time = datetime_column.time_input(
                "Transfer Time", value=None
            )
            transfer_amount = st.number_input(
                "Transfer Amount", value=None
            )
            if st.button("Add Internal Transfer"):
                add_internal_transfer(
                    db_manager, source_money_store, target_money_store,
                    transfer_date, transfer_time, transfer_amount
                )



    with input_tab:

        location_column, info_column, datetime_column = st.columns(3)
        adding_spending = AddingSpending(st.session_state, db_manager)

        adding_spending.set_shop_brand(
            location_column.selectbox("Shop Name", db_manager.get_all_shop_brands(), accept_new_options=True, index=None)
        )
        selected_shop_locations = db_manager.get_shop_locations(adding_spending.shop_brand)
        adding_spending.set_shop_location(
            location_column.selectbox("Location Name", selected_shop_locations, accept_new_options=True, index=None)
        )

        adding_spending.set_spending_category(
            info_column.selectbox("Spending Category", db_manager.get_all_categories(), index=None)
        )
        adding_spending.set_money_store_used(
            info_column.selectbox("Money Store Used", db_manager.get_all_money_stores(), index=None)
        )
        adding_spending.set_spending_date(
            datetime_column.date_input("Spending Date", format="DD/MM/YYYY")
        )
        adding_spending.set_spending_time(
            datetime_column.time_input("Spending Time", value=None)
        )

        st.markdown("## Items")

        if "product_selection" not in st.session_state:
            st.session_state["product_selection"] = None

        selected_product = st.selectbox(
            "Add Item",
            options=db_manager.get_all_products(adding_spending.shop_brand),
            accept_new_options=True, index=None, key="product_selection"
        )
        def add_item_button_press(adding_spending_obj, selected_option):
            adding_spending_obj.add_product(selected_option)
            del st.session_state["product_selection"]

        st.button("Add Item", on_click=lambda: add_item_button_press(adding_spending, selected_product))

        spending_display_df = adding_spending.to_display_df()

        st.session_state["adding_spending_df"] = adding_spending.from_display_df(
            utils.data_editor(
                spending_display_df,
                {
                    "ID": {"type": "number", "editable": False},
                    "Price Per": {"type": "number", "format": "£%.2f"},
                }
            )
        )

        if st.dialog("Save Spending", width="large"):
            total_cost = sum(filter(
                lambda num: not utils.isNone(num),
                spending_display_df["Price Per"] * spending_display_df["Num Purchased"]
            ))
            st.markdown(f"Add Spending Event of spending £{total_cost:.2f}")
            if st.button("Add Spending Event"):
                adding_spending.add_spending_to_db()
                del st.session_state["adding_spending_df"]



    with data_base:

        left, right = st.columns(2)

        with left:
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
        with right:
            with st.expander("Money Stores"):
                db_manager.save_money_stores_df_changes(
                    utils.data_editor(
                        db_manager.get_money_stores_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                        },
                    )
                )

            with st.expander("Store Snapshots"):
                db_manager.save_store_snapshots_df_changes(
                    utils.data_editor(
                        db_manager.get_store_snapshots_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                            "Money Store": {"type": "select", "options": db_manager.get_all_money_stores()},
                            "Balance": {"type": "number", "format": "£%.2f"}
                        },
                    )
                )

            with st.expander("Internal Transfers"):
                db_manager.save_internal_transfers_df_changes(
                    utils.data_editor(
                        db_manager.get_internal_transfers_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                            "Source": {"type": "select", "options": db_manager.get_all_money_stores()},
                            "Target": {"type": "select", "options": db_manager.get_all_money_stores()},
                            "Transferred": {"type": "number", "format": "£%.2f"},
                        },
                    )
                )

            with st.expander("Spending Events"):
                db_manager.save_spending_events_df_changes(
                    utils.data_editor(
                        db_manager.get_spending_events_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                            "Money Store": {"type": "select", "options": db_manager.get_all_money_stores()},
                            "Shop": {"type": "select", "options": db_manager.get_all_shop_brands()},
                            "Location": {"type": "select", "options": db_manager.get_shop_locations(None)},
                            "Category": {"type": "select", "options": db_manager.get_all_category_strings()}
                        },
                    )
                )

            with st.expander("Spending Items"):
                db_manager.save_spending_items_df_changes(
                    utils.data_editor(
                        db_manager.get_spending_items_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                            "Event ID": {"type": "select", "options": db_manager.spending_events.list_all_in_column("spending_event_id")},
                            "Name": {"type": "select", "options": db_manager.products.list_all_in_column("name")},
                            "Price": {"type": "number", "format": "£:.2f"},
                            "Num Purchased": {"type": "number"}
                        },
                    )
                )



    double_run()





