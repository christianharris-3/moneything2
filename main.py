import streamlit as st
import src.utils as utils
import src.streamlit_utils as st_utils
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

def load_page(page_key):
    if "current_page_key" not in st.session_state:
        st.session_state["current_page_key"] = page_key

    if st.session_state["current_page_key"] != page_key:
        st_utils.load_ui_cache(page_key)
        st.session_state["current_page_key"] = page_key

def make_page(page_func, check_auth=True):
    page_key = str(page_func)
    load_page(page_key)
    if check_auth:
        run_if_auth(page_func)
    else:
        page_func()
    st_utils.store_to_ui_cache(page_key)

def Account():
    make_page(st_auth_ui, False)

def Transactions():
    make_page(transactions_page_ui)

def Vendors():
    make_page(edit_vendors_page_ui)

def Categories():
    make_page(categories_page_ui)

def Money_Stores():
    make_page(money_stores_page_ui)

def DataBase_View():
    make_page(database_view_page_ui)

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
#  add vendor merging back to vendor menu
#  improve edit money store menu
#  re-add merging transactions
#  make internal transfers editable in transactions menu

# TODO: MIDDLE PRIORITY
#  make default location/category auto set based on a transaction
#  add pages at bottom to all transactions lists when len items > 15 etc
#  add pygame image generator to visualize spending per category

# TODO: LOW PRIORITY
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)
#  unit test the mother loving fuck out of everything
#  improve logs
#  add a warning when editing an name entry in the adding/editing items section of transactions, when that is a reference to a product already and cant be edited






