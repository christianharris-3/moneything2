import streamlit as st
st.set_page_config(layout="wide")

from src.db_manager import DatabaseManager
from src.adding_transaction import AddingTransaction
from src.add_to_db import add_money_store, add_internal_transfer
from src.money_tracker import build_money_ui
import src.utils as utils

# TODO: Add Special viewing menu for previous spending + proper edit system for spending
# TODO: Add Menu for current money,:
#  Allow you to enter money values for different store locations, e.g. cash, different bank accounts
#  Use given spending data to graph money stored in each location over time
#  Allow user to log movements between accounts as well (e.g. take money out of atm)
#  Add Spending method to add spending (the money store location used, e.g. cash/bank account)
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)

# TODO: unit test the mother loving fuck out of everything

# TODO: add "override price" to spending events

# TODO: change spending to be income/spending or add income tab


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

    money_tab, input_tab, data_base, data_tab = st.tabs(["Money Tracker","Add Transaction", "DataBase", "View Data"])

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

        build_money_ui(db_manager)



    with input_tab:

        location_column, info_column, datetime_column = st.columns(3)
        adding_spending = AddingTransaction(st.session_state, db_manager)

        adding_spending.set_vendor_name(
            location_column.selectbox("Vendor Name", db_manager.get_all_vendor_names(), accept_new_options=True, index=None)
        )
        selected_shop_locations = db_manager.get_shop_locations(adding_spending.vendor_name)
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

        adding_spending.set_override_money(
            location_column.number_input("Money Transferred", value=None)
        )
        adding_spending.set_is_income(
            info_column.selectbox("Spending or Income", ["Spending", "Income"])
        )

        if adding_spending.override_money is not None:
            total_cost = adding_spending.override_money
        else:
            total_cost = 0
        if not adding_spending.is_income:
            st.markdown("## Items")

            if "product_selection" not in st.session_state:
                st.session_state["product_selection"] = None

            selected_product = st.selectbox(
                "Add Item",
                options=db_manager.get_all_products(adding_spending.vendor_name),
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

            total_cost = sum(filter(
                lambda num: not utils.isNone(num),
                spending_display_df["Price Per"] * spending_display_df["Num Purchased"]
            ))
            st.divider()
            st.markdown(f"Add Transaction of spending £{total_cost:.2f}")
        else:
            st.divider()
            st.markdown(f"Add Income of £{total_cost:.2f}")
        if st.button("Add Transaction"):
            adding_spending.add_transaction_to_db()
            del st.session_state["adding_spending_df"]
            st.toast("Transaction Added!")



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
                            "Shop": {"type": "select", "options": db_manager.get_all_vendor_names()},
                            "Category": {"type": "select", "options": db_manager.get_all_category_strings()}
                        },
                    )
                )

            with st.expander("Vendors"):
                db_manager.save_vendors_df_changes(
                    utils.data_editor(
                        db_manager.get_vendors_display_df(),
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
                            "Name": {"type": "select", "options": db_manager.get_all_vendor_names()}
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
            with st.expander("Transactions"):
                db_manager.save_transactions_df_changes(
                    utils.data_editor(
                        db_manager.get_transactions_display_df(),
                        {
                            "ID": {"type": "number", "editable": False},
                            "Is Income": {"type": "boolean"},
                            "Money Store": {"type": "select", "options": db_manager.get_all_money_stores()},
                            "Shop": {"type": "select", "options": db_manager.get_all_vendor_names()},
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
                            "Transaction ID": {"type": "select", "options": db_manager.transactions.list_all_in_column("transaction_id")},
                            "Name": {"type": "select", "options": db_manager.products.list_all_in_column("name")},
                            "Price": {"type": "number", "format": "£:.2f"},
                            "Num Purchased": {"type": "number"}
                        },
                    )
                )



    double_run()





