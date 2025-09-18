import streamlit as st

from src.db_manager import DatabaseManager

st.set_page_config(page_title="Vendors - Money Thing", page_icon="📈")#,layout="wide")

if __name__ == "__main__":
    db_manager = DatabaseManager()

    st.markdown("## Edit Vendors")

    edit_vendor = st.selectbox("Vendors", options=db_manager.get_all_vendor_names(), index=None)

    if edit_vendor is not None:
        st.text_input("Rename Vendor", value=edit_vendor)

        st.markdown("### Convert into other vendor")

        target_vendor = st.selectbox("Target Vendor", options=db_manager.get_all_vendor_names(), index=None)

        target_location = st.selectbox(
            "Target Location",
            options=db_manager.get_shop_locations(target_vendor),
            accept_new_options=True,
            index = None
        )

        st.button("Save")