import src.utils as utils
utils.block_if_no_auth()

import streamlit as st
from src.db_manager import DatabaseManager
from src.st_transaction_input import transaction_input_tab
from src.pdf_reader import upload_pdf

st.set_page_config(page_title="Transactions - Money Thing", page_icon="📈",layout="wide")

if __name__ == "__main__":

    db_manager = DatabaseManager()

    st.markdown("# Add/Edit Transactions")

    input_tab, upload_tab = st.tabs(["Input Transactions", "Upload Transactions"])

    with input_tab:
        transaction_input_tab(db_manager)

    with upload_tab:
        st.markdown("## Upload")

        money_store = st.radio("Money Store", options=db_manager.get_all_money_stores())

        files = st.file_uploader("Upload HSBC Statements", accept_multiple_files=True)

        if st.button("Store data to database"):
            progress_bar = st.progress(1, text="Uploading Files")
            for i,file in enumerate(files):
                upload_pdf(file, db_manager, money_store)
                progress_bar.progress((i+1)/len(files))
            st.markdown("Upload Complete!")

    # utils.double_run()