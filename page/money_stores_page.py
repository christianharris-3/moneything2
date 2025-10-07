import src.utils as utils
import src.streamlit_utils as st_utils
from src.db_manager import DatabaseManager
from src.add_to_db import add_money_store, add_internal_transfer
from src.money_tracker import build_money_ui
import streamlit as st
from src.logger import log

def money_stores_page_ui():
    utils.block_if_no_auth()
    st.set_page_config(page_title="Money Store - Money Thing", page_icon="📈", layout="wide")
    log("Loading page 4: Money Stores")

    db_manager = DatabaseManager()

    money_tab, data_tab = st.tabs(["Money Tracker", "View Data"])

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

    st_utils.double_run()

if __name__ == "__main__":
    money_stores_page_ui()