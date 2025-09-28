import src.utils as utils
utils.block_if_no_auth()

import streamlit as st
from src.db_manager import DatabaseManager
from src.logger import log

st.set_page_config(page_title="Vendors - Money Thing", page_icon="📈")#,layout="wide")


def merge_vendors(db_manager, edit_vendor_id, target_vendor_id, target_location):
    # convert shop locations to link to new vendor id + create new shop location
    target_location_id = None
    if target_location is not None:
        target_location_id = db_manager.shop_locations.get_id_from_value("shop_location", target_location)

        if target_location_id is None:
            target_location_id = db_manager.db.create_row(
                db_manager.shop_locations.TABLE,
                {"shop_location": target_location,
                 "vendor_id": target_vendor_id}
            )
        db_manager.db.update_row(
            db_manager.shop_locations.TABLE,
            {"vendor_id": target_vendor_id},
            "shop_location_id",
            target_location_id
        )

    # update transactions to new vendor id

    transaction_changes = {
        "vendor_id": target_vendor_id,
    }
    if target_location_id is not None:
        transaction_changes["shop_location_id"] = target_location_id
    db_manager.db.update_row(
        db_manager.transactions.TABLE,
        transaction_changes,
        "vendor_id",
        edit_vendor_id
    )

    # update products to link to new vendor id

    db_manager.db.update_row(
        db_manager.products.TABLE,
        {"vendor_id": target_vendor_id},
        "vendor_id",
        edit_vendor_id
    )

    # delete old vendor

    db_manager.db.delete(
        db_manager.vendors.TABLE,
        "vendor_id",
        edit_vendor_id
    )

if __name__ == "__main__":
    log("Loading page 2: Edit Vendors")

    db_manager = DatabaseManager()

    st.markdown("## Edit Vendor")

    edit_vendor_name = st.selectbox("Vendors", options=db_manager.get_all_vendor_names(), index=None)

    edit_vendor_id = db_manager.vendors.get_id_from_value("name", edit_vendor_name)

    if edit_vendor_id is not None:
        merge_vendor = st.toggle("Merge ")

        if not merge_vendor:
            st.markdown("### Rename Vendor")

            new_vendor_name = st.text_input(
                "Rename Vendor",
                value=edit_vendor_name
            )

            if st.button("Rename"):
                db_manager.vendors.rename_vendors(db_manager.db, edit_vendor_id, new_vendor_name)
                st.toast(f"Renamed To {new_vendor_name}")
        else:
            st.markdown("### Merge into other vendor")

            target_vendor = st.selectbox(
                "Target Vendor",
                options=db_manager.get_all_vendor_names(),
                index=None,
                key="target_vendor_input"
            )

            target_location = st.selectbox(
                "Target Location",
                options=db_manager.get_shop_locations(target_vendor),
                accept_new_options=True,
                index = None
            )

            target_vendor_id = db_manager.vendors.get_id_from_value("name", target_vendor)


            if st.button("Merge", disabled=(target_vendor_id is None)):
                merge_vendors(db_manager, edit_vendor_id, target_vendor_id, target_location)
                st.toast(f"Merged {edit_vendor_name} into {target_vendor}")
