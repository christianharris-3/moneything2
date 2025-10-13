import streamlit as st
from src.db_manager import DatabaseManager
from src.st_transaction_input import transaction_input_tab
from src.pdf_reader import upload_pdf
from src.receipt_reader import upload_lidl_receipt
from src.logger import log
import src.utils as utils


def view_transaction(transaction_id):
    db_manager = DatabaseManager()
    row = db_manager.transactions.get_db_row(transaction_id)
    st.session_state["transaction_viewer_date"] = {
        "depth": "specific",
        "timestamp": utils.string_to_date(row["date"]),
        "transaction_id": transaction_id,
        "search_mode": False,
        "search_term": None,
        "page": 1,
        "is_internal": False
    }

def transactions_page_ui():
    utils.block_if_no_auth()
    st.set_page_config(page_title="Transactions - Money Thing", page_icon="📈", layout="wide")
    log("Loading page 1: Input Transactions")

    db_manager = DatabaseManager()

    st.markdown("# Add/Edit Transactions")

    input_tab, upload_tab = st.tabs(["Input Transactions", "Upload Transactions"])

    with input_tab:
        transaction_input_tab(db_manager)

    with upload_tab:
        upload_type = st.selectbox("File Type", ["Lidl Digital Receipt", "HSBC Bank Statement"])


        if upload_type == "HSBC Bank Statement":
            st.markdown("## Upload Statement")

            money_store = st.radio("Money Store Related", options=db_manager.get_all_money_stores())

            files = st.file_uploader("Upload HSBC Statements", accept_multiple_files=True)

            if st.button("Store data to database"):
                if len(files) >= 5:
                    progress_bar = st.progress(1, text="Uploading Files")
                for i,file in enumerate(files):
                    upload_pdf(file, db_manager, money_store)
                    if len(files) >= 5:
                        progress_bar.progress((i+1)/len(files))
                st.toast("Upload Complete!", icon="✔️")
        else:
            st.markdown("## Upload Digital Receipt")

            money_store = st.radio("Money Store Used", options=db_manager.get_all_money_stores())

            files = st.file_uploader("Upload Lidl Receipts", accept_multiple_files=True, key="lidl_receipt_input")

            if st.button("Store data to database"):
                if len(files)>=2:
                    progress_bar = st.progress(1, text="Uploading Receipts")

                st.session_state["view_new_uploaded_transactions"] = []

                for i, file in enumerate(files):
                    print("loading file", file)
                    transaction_id = upload_lidl_receipt(file, db_manager, money_store)
                    st.session_state["view_new_uploaded_transactions"].append(transaction_id)
                    if len(files) >= 2:
                        progress_bar.progress((i + 1) / len(files))
                st.toast("Upload Complete!", icon="✔️")
                del st.session_state["lidl_receipt_input"]


            new_transactions = st.session_state.get("view_new_uploaded_transactions", [])
            if len(new_transactions) > 0:
                st.markdown("View uploaded transactions")
                for id_ in new_transactions:
                    st.button(
                        f"View {id_}",
                        on_click=view_transaction,
                        args=(id_,)
                    )

    # utils.double_run()

if __name__ == "__main__":
    transactions_page_ui()
