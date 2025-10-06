import streamlit as st
from src.authentication import st_auth_ui
from page.transactions_page import transactions_page_ui
from page.vendors_page import edit_vendors_page_ui
from page.categories_page import categories_page_ui
from page.money_stores_page import money_stores_page_ui
from page.database_view_page import database_view_page_ui

# st.set_page_config(
#     page_title="Home - Money Thing",
#     page_icon="📈",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

def Account():
    st_auth_ui()

def Transactions():
    transactions_page_ui()

def Vendors():
    edit_vendors_page_ui()

def Categories():
    categories_page_ui()

def Money_Stores():
    money_stores_page_ui()

def DataBase_View():
    database_view_page_ui()


pages = {
    "Account": [
        st.Page(Account, icon="👤")
    ],
    "Enter Info": [
        st.Page(Transactions, icon="💳"),
        st.Page(Vendors, icon="🏪"),
        st.Page(Categories, icon="📋"),
        st.Page(Money_Stores, icon="🏦"),
        st.Page(DataBase_View, icon="📂")
    ],
}

if __name__ == "__main__":
    pg = st.navigation(pages)
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






