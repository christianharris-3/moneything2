import streamlit as st
from src.authentication import st_auth_ui
st.set_page_config(page_title="Home - Money Thing", page_icon="📈",layout="wide")


# TODO: Add Special viewing menu for previous spending + proper edit system for spending
# TODO: Add Menu for current money,:
#  Use given spending data to graph money stored in each location over time
#  System for future modelling: make modelling irrelevant to now (spending can be added in the future, then confirmed later to the date)

# TODO: unit test the mother loving fuck out of everything

# TODO: add method to convert/merge/add locations to vendors and locations
# TODO: add method to change transactions into internal transfers
# TODO: add pages to all transactions lists

# TODO: host website, vercel.com

if __name__ == "__main__":
    st_auth_ui()





