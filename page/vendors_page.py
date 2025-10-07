import streamlit as st
import src.utils as utils
from src.db_manager import DatabaseManager
from src.adding_vendor import AddingVendor
import src.streamlit_utils as st_utils
from src.st_transaction_input import find_transaction_value
from src.logger import log

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

def vendor_list_ui(db_manager):

    state = st.session_state["vendors_state"]

    st.markdown("## Find Vendors")
    search_term = st.text_input("Search Vendors", icon="🔎", key="vendor_search_input")

    vendors = db_manager.vendors.db_data.copy()
    transactions = db_manager.transactions.db_data.copy()

    vendor_container = st.container()

    vendors = utils.get_df_matching_search_term(vendors, search_term)
    vendors = st_utils.pages_manager_ui(state, vendors.sort_values("name"))

    vendors = vendors.reset_index(drop=True)

    def get_transactions_for_vendor(vendor_id):
        filtered = transactions[transactions["vendor_id"] == vendor_id].copy()
        filtered["date_obj"] = transactions["date"].apply(utils.string_to_date)
        filtered.sort_values("date_obj", ascending=False)
        return filtered

    for i, row in vendors.iterrows():
        vendor_transactions = get_transactions_for_vendor(row["vendor_id"])
        vendors.at[i, "income"] = sum(map(
            lambda r: find_transaction_value(db_manager, r[1]) if r[1]["is_income"] else 0,
            vendor_transactions.iterrows()
        ))
        vendors.at[i, "spending"] = sum(map(
            lambda r: 0  if r[1]["is_income"] else find_transaction_value(db_manager, r[1]),
            vendor_transactions.iterrows()
        ))

        row = vendors.iloc[i]
        title = ""
        if row['income']>0:
            title+=f" Income: £{row['income']:.2f}"
        if row['spending']>0:
            title+=f" Spending: £{row['spending']:.2f}"
        if title == "":
            title+=" No Money Transferred"
        title = f"{row['name']} -"+title
        vendors.at[i, "title"] = title

    for i, row in vendors.iterrows():
        vendor_container.button(
            row["title"],
            use_container_width=True,
            on_click=load_vendor,
            args=(db_manager, row)

        )

def load_vendor(db_manager, row):
    adding_vendor = AddingVendor(db_manager)
    adding_vendor.clear_input()

    st.session_state["vendor_name_input"] = row["name"]
    st.session_state["selected_vendor_id"] = row["vendor_id"]

    category_row = db_manager.categories.get_db_row(row["default_category_id"])
    category_name = None
    if category_row is not None and not utils.isNone(category_row["name"]):
        category_name = category_row["name"]
    st.session_state["default_category_input"] = category_name

    location_row = db_manager.shop_locations.get_db_row(row["default_location_id"])
    location_name = None
    if location_row is not None and not utils.isNone(location_row["shop_location"]):
        location_name = location_row["shop_location"]
    st.session_state["default_location_input"] = location_name

    locations = db_manager.shop_locations.get_filtered_df("vendor_id", row["vendor_id"])
    for i, r in locations.iterrows():
        adding_vendor.add_location(r["shop_location"], r["shop_location_id"])


def edit_vendor_ui(db_manager):
    adding_vendor = AddingVendor(db_manager)

    if st.session_state.get("delete_vendor_inputs", False):
        adding_vendor.clear_input()
        st.session_state["delete_vendor_inputs"] = False

    title, clear = st.columns([0.8, 0.2], vertical_alignment="center")

    clear.button(
        "Clear",
        on_click=adding_vendor.clear_input,
        use_container_width=True
    )

    if st.session_state["selected_vendor_id"] is None:
        title.markdown("## Create Vendor")
    else:
        title.markdown(f"## Editing Vendor {st.session_state['selected_vendor_id']}")

    st.text_input(
        "Vendor Name", None,
        key="vendor_name_input"
    )

    locations = list(adding_vendor.get_df()["name"])

    st.selectbox(
        "Default Category",
        db_manager.get_all_categories(),
        index=None,
        key="default_category_input"
    )
    st.selectbox(
        "Default Location",
        locations,
        index=None,
        key="default_location_input"
    )


    list_vendor_locations_ui(db_manager, adding_vendor)
    return



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
                index=None
            )

            target_vendor_id = db_manager.vendors.get_id_from_value("name", target_vendor)

            if st.button("Merge", disabled=(target_vendor_id is None)):
                merge_vendors(db_manager, edit_vendor_id, target_vendor_id, target_location)
                st.toast(f"Merged {edit_vendor_name} into {target_vendor}")


def list_vendor_locations_ui(db_manager, adding_vendor):
    container = st.container(border=True)

    container.markdown("### Locations")

    table = container.container()
    container.button("Add Location", on_click=adding_vendor.add_location)

    for i, row in adding_vendor.get_df().iterrows():
        text, delete = table.columns([0.8, 0.2])
        text.text_input(
            "Location Name",
            label_visibility="collapsed",
            key=f"location_name_input_{i}"
        )
        delete.button(
            "",
            icon="🗑️",
            use_container_width=True,
            on_click=adding_vendor.delete_location,
            args=(i,),
            key=f"delete_location_button_{i}"
        )

    save, view, delete = st.columns([1,1,1])

    if save.button("Save Vendor", use_container_width=True):
        adding_vendor.save_vendor(db_manager)
    if view.button("View Transactions", use_container_width=True):
        st.session_state["set_search_query"] = f"vendor:{st.session_state['vendor_name_input']}"
        st.session_state["switch_page"] = "transactions"
        st.rerun()
    if st.session_state["selected_vendor_id"] is not None and delete.button("Delete Vendor", icon="🗑️", use_container_width=True):
        adding_vendor.delete_vendor(db_manager)


def edit_vendors_page_ui():
    utils.block_if_no_auth()
    st.set_page_config(page_title="Vendors - Money Thing", page_icon="📈", layout="wide")
    log("Loading page 2: Edit Vendors")

    db_manager = DatabaseManager()

    if "vendors_state" not in st.session_state:
        st.session_state["vendors_state"] = {
            "page": 1,
            "vendor_id": None,
        }

    st.markdown("# Add/Edit Vendors")
    st.divider()

    edit_column, list_column = st.columns([0.5, 0.5])
    list_column = list_column.container(border=True)

    with list_column:
        vendor_list_ui(db_manager)
    with edit_column:
        edit_vendor_ui(db_manager)

if __name__ == "__main__":
    edit_vendors_page_ui()
