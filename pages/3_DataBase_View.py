import streamlit as st
import src.utils as utils
from src.db_manager import DatabaseManager
from src.sql_database import SQLDatabase

st.set_page_config(page_title="Database - Money Thing", page_icon="📈",layout="wide")

@st.fragment
def user_input_sql():
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
            else:
                return True

            st.session_state["cache_sql_input"].add(sql_statement)
        else:
            st.write("SQL Failed to Execute")
            st.write(output)
    return False


if __name__ == "__main__":
    db_manager = DatabaseManager()

    st.markdown("## Database Tables")

    left, right = st.columns(2)

    db_edited = False

    with left:
        with st.expander("Products"):
            db_edited = db_manager.save_products_df_changes(
                utils.data_editor(
                    db_manager.get_products_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Price": {"type": "number", "format": "£%.2f"},
                        "Shop": {"type": "select", "options": db_manager.get_all_vendor_names()},
                        "Category": {"type": "select",
                                     "options": db_manager.get_all_category_strings()}
                    },
                )
            ) or db_edited

        with st.expander("Vendors"):
            db_edited = db_manager.save_vendors_df_changes(
                utils.data_editor(
                    db_manager.get_vendors_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                    },
                )
            ) or db_edited

        with st.expander("ShopLocations"):
            db_edited = db_manager.save_locations_df_changes(
                utils.data_editor(
                    db_manager.get_locations_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Name": {"type": "select", "options": db_manager.get_all_vendor_names()}
                    },
                )
            ) or db_edited

        with st.expander("Categories"):
            db_edited = db_manager.save_categories_df_changes(
                utils.data_editor(
                    db_manager.get_categories_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Importance": {"type": "number"},
                        "Parent Category": {"type": "select",
                                            "options": db_manager.get_all_categories()}
                    },
                )
            ) or db_edited

        with st.expander("Run SQL"):
            db_edited = user_input_sql() or db_edited

    with right:
        with st.expander("Money Stores"):
            db_edited = db_manager.save_money_stores_df_changes(
                utils.data_editor(
                    db_manager.get_money_stores_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                    },
                )
            ) or db_edited

        with st.expander("Store Snapshots"):
            db_edited = db_manager.save_store_snapshots_df_changes(
                utils.data_editor(
                    db_manager.get_store_snapshots_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Money Store": {"type": "select",
                                        "options": db_manager.get_all_money_stores()},
                        "Balance": {"type": "number", "format": "£%.2f"}
                    },
                )
            ) or db_edited

        with st.expander("Internal Transfers"):
            db_edited = db_manager.save_internal_transfers_df_changes(
                utils.data_editor(
                    db_manager.get_internal_transfers_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Source": {"type": "select", "options": db_manager.get_all_money_stores()},
                        "Target": {"type": "select", "options": db_manager.get_all_money_stores()},
                        "Transferred": {"type": "number", "format": "£%.2f"},
                    },
                )
            ) or db_edited
        with st.expander("Transactions"):
            db_edited = db_manager.save_transactions_df_changes(
                utils.data_editor(
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
            ) or db_edited

        with st.expander("Spending Items"):
            db_edited = db_manager.save_spending_items_df_changes(
                utils.data_editor(
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
            ) or db_edited

    # if db_edited:
    #     utils.double_run()