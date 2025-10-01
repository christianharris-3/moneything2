import streamlit as st
from src.authentication import st_auth_ui
st.set_page_config(
    page_title="Home - Money Thing",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)
if __name__ == "__main__":
    st_auth_ui()

# TODO: HIGH PRIORITY
#  fix transactions spending info to be correct, and add vendor to message


# TODO: MIDDLE PRIORITY
#  make internal transfers editable in transactions menu
#  add pages at bottom to all transactions lists when len items > 15 etc
#  add less shit method to convert/merge/add locations to vendors and locations
#  method to add/edit/delete categories
#  make nan get ignored on transactions listing
#  add pygame image generator to visualize spending per category

# TODO: LOW PRIORITY
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)
#  unit test the mother loving fuck out of everything
#  improve logs
#  add a warning when editing an name entry in the adding/editing items section of transactions, when that is a reference to a product already and cant be edited






