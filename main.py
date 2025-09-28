import streamlit as st
from src.authentication import st_auth_ui
st.set_page_config(
    page_title="Home - Money Thing",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# TODO: Add Menu for current money,:
#  Use given spending data to graph money stored in each location over time
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)

# TODO: unit test the mother loving fuck out of everything

# TODO: add method to convert/merge/add locations to vendors and locations
# TODO: add method to change transactions into internal transfers
# TODO: add pages to all transactions lists

# TODO: host website, vercel.com

# TODO: default money store input
#  fix transactions spending info to be correct, and add vendor to message
#  reduce double refreshing when entering info

# TODO: add change password, and user page
#  fix side bar not making sense

# TODO: when sorting by search, do most recent first
#  search by column with format "name: cheese"

# TODO: create logs for server

# TODO: put internal transfers in the same area as transactions

if __name__ == "__main__":
    st_auth_ui()





