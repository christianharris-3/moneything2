import streamlit as st
from src.db_manager import DatabaseManager
from src.sql_database import SQLDatabase
import src.streamlit_utils as st_utils
from src.logger import log
import src.utils as utils


@st.fragment
def user_input_sql():
    if st.session_state.get("current_user_id", 0) != 1:
        return
    db = SQLDatabase()

    if "cache_sql_input" not in st.session_state:
        st.session_state["cache_sql_input"] = set(
            f"SELECT * FROM {table}" for table in [
                "Products",
                "Vendors",
                "ShopLocations",
                "Categories",
                "Transactions",
                "SpendingItems",
                "MoneyStores",
                "StoreSnapshots",
                "InternalTransfers"
            ]
        )
    sql_autofill = st.selectbox(
        "Previous Statements",
        options=st.session_state["cache_sql_input"],
        index=None,
    )
    if "sql_autofill_input" not in st.session_state:
        st.session_state["sql_autofill_input"] = sql_autofill
    elif st.session_state["sql_autofill_input"] != sql_autofill and sql_autofill is not None:
        st.session_state["sql_autofill_input"] = sql_autofill
    sql_statement = st.text_input(
        "SQL", value=st.session_state["sql_autofill_input"]
    )
    button, statement = st.columns([0.2, 0.8], vertical_alignment="center")
    statement.markdown(sql_statement)
    if button.button(
            "Execute",
            disabled=(sql_statement is None),
            use_container_width=True
    ) or (sql_statement is not None and sql_statement.lower().startswith("select")):
        output, successful = db.run_user_sql(sql_statement)
        if successful:
            st.write("SQL Executed Successfully!")
            if sql_statement.lower().startswith("select"):
                st.write(output)

            st.session_state["cache_sql_input"].add(sql_statement)
        else:
            st.write("SQL Failed to Execute")
            st.write(output)

@st.fragment
def products_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_products_df_changes(
        st_utils.data_editor(
            db_manager.get_products_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Price": {"type": "number", "format": "£%.2f"},
                "Shop": {"type": "select", "options": db_manager.get_all_vendor_names()},
                "Category": {"type": "select",
                             "options": db_manager.get_all_category_strings()}
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def vendors_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_vendors_df_changes(
        st_utils.data_editor(
            db_manager.get_vendors_display_df(),
            {
                "ID": {"type": "number", "editable": False},
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def locations_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_locations_df_changes(
        st_utils.data_editor(
            db_manager.get_locations_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Name": {"type": "select", "options": db_manager.get_all_vendor_names()}
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def categories_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_categories_df_changes(
        st_utils.data_editor(
            db_manager.get_categories_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Importance": {"type": "number"},
                "Parent Category": {"type": "select",
                                    "options": db_manager.get_all_categories()}
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def money_stores_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_money_stores_df_changes(
        st_utils.data_editor(
            db_manager.get_money_stores_display_df(),
            {
                "ID": {"type": "number", "editable": False},
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def snapshot_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_store_snapshots_df_changes(
        st_utils.data_editor(
            db_manager.get_store_snapshots_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Money Store": {"type": "select",
                                "options": db_manager.get_all_money_stores()},
                "Balance": {"type": "number", "format": "£%.2f"}
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def internal_transfers_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_internal_transfers_df_changes(
        st_utils.data_editor(
            db_manager.get_internal_transfers_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Source": {"type": "select", "options": db_manager.get_all_money_stores()},
                "Target": {"type": "select", "options": db_manager.get_all_money_stores()},
                "Transferred": {"type": "number", "format": "£%.2f"},
            },
        )
    ):
        st.rerun(scope="fragment")

@st.fragment
def transactions_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_transactions_df_changes(
        st_utils.data_editor(
            db_manager.get_transactions_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Is Income": {"type": "boolean"},
                "Money Store": {"type": "select",
                                "options": db_manager.get_all_money_stores()},
                "Shop": {"type": "select", "options": db_manager.get_all_vendor_names()},
                "Location": {"type": "select",
                             "options": db_manager.get_shop_locations(None)},
                "Category": {"type": "select",
                             "options": db_manager.get_all_category_strings()}
            },
        )
    ):
        st.rerun()

@st.fragment
def spending_items_table_ui():
    db_manager = DatabaseManager()
    if db_manager.save_spending_items_df_changes(
        st_utils.data_editor(
            db_manager.get_spending_items_display_df(),
            {
                "ID": {"type": "number", "editable": False},
                "Transaction ID": {"type": "select",
                                   "options": db_manager.transactions.list_all_in_column(
                                       "transaction_id")},
                "Name": {"type": "select",
                         "options": db_manager.products.list_all_in_column("name")},
                "Price": {"type": "number", "format": "£:.2f"},
                "Num Purchased": {"type": "number"}
            },
        )
    ):
        st.rerun()

def database_view_page_ui():
    utils.block_if_no_auth()
    st.set_page_config(page_title="Database - Money Thing", page_icon="📈", layout="wide")
    log("Loading page 3: Database View")

    st.markdown("## Database Tables")

    left, right = st.columns(2)

    with left:
        with st.expander("Products"):
            products_table_ui()

        with st.expander("Vendors"):
            vendors_table_ui()

        with st.expander("ShopLocations"):
            locations_table_ui()

        with st.expander("Categories"):
            categories_table_ui()

        if st.session_state.get("current_user_id", 0) == 1:
            with st.expander("Run SQL"):
                user_input_sql()

    with right:
        with st.expander("Money Stores"):
            money_stores_table_ui()

        with st.expander("Store Snapshots"):
            snapshot_table_ui()

        with st.expander("Internal Transfers"):
            internal_transfers_table_ui()

        with st.expander("Transactions"):
            transactions_table_ui()

        with st.expander("Spending Items"):
            spending_items_table_ui()

if __name__ == "__main__":
    database_view_page_ui()

