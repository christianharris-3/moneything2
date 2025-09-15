import streamlit as st
from src.db_manager import DatabaseManager
from src.st_transaction_input import transaction_input_tab
import src.utils as utils

st.set_page_config(page_title="Transactions - Money Thing", page_icon="📈",layout="wide")

if __name__ == "__main__":
    db_manager = DatabaseManager()

    st.markdown("# Add/Edit Transactions")

    input_tab, upload_tab = st.tabs(["Input Transactions", "Upload Transactions"])

    with input_tab:
        transaction_input_tab(db_manager)

    with upload_tab:
        st.markdown("## Upload HSBC Statements")

    utils.double_run()