import streamlit as st
import src.utils as utils
from src.authentication import st_auth_ui
from page.transactions_page import transactions_page_ui
from page.vendors_page import edit_vendors_page_ui
from page.categories_page import categories_page_ui
from page.money_stores_page import money_stores_page_ui
from page.database_view_page import database_view_page_ui

st.set_page_config(
    page_title="Home - Money Thing",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def run_if_auth(func):
    if utils.is_authenticated():
        func()
    else:
        st.switch_page(pages_dict["account"])

def Account():
    st_auth_ui()

def Transactions():
    run_if_auth(transactions_page_ui)

def Vendors():
    run_if_auth(edit_vendors_page_ui)

def Categories():
    run_if_auth(categories_page_ui)

def Money_Stores():
    run_if_auth(money_stores_page_ui)

def DataBase_View():
    run_if_auth(database_view_page_ui)

pages_dict = {
    "account": st.Page(Account, icon="👤", title="Money Thing"),
    "transactions": st.Page(Transactions, icon="💳", title="Transactions"),
    "vendors": st.Page(Vendors, icon="🏪", title="Vendors"),
    "categories": st.Page(Categories, icon="📋", title="Categories"),
    "money_stores": st.Page(Money_Stores, icon="🏦", title="Money Stores"),
    "database_view": st.Page(DataBase_View, icon="📂", title="Database View")
}

if st.session_state.get("switch_page", None) is not None:
    target_page = pages_dict[st.session_state["switch_page"]]
    st.session_state["switch_page"] = None
    st.switch_page(target_page)

pages_info = {
    "Account": [
        pages_dict["account"]
    ],
    "Enter Info": [
        pages_dict["transactions"],
        pages_dict["vendors"],
        pages_dict["categories"],
        pages_dict["money_stores"],
        pages_dict["database_view"]
    ]
}


if __name__ == "__main__":
    pg = st.navigation(pages_info)
    pg.run()

# TODO: HIGH PRIORITY
#  fix transactions spending info to be correct, and add vendor to message
#  Add table thing for editing locations
#  make rest of vendors ui work

# TODO: MIDDLE PRIORITY
#  make internal transfers editable in transactions menu
#  add pages at bottom to all transactions lists when len items > 15 etc
#  add pygame image generator to visualize spending per category

# TODO: LOW PRIORITY
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)
#  unit test the mother loving fuck out of everything
#  improve logs
#  add a warning when editing an name entry in the adding/editing items section of transactions, when that is a reference to a product already and cant be edited






