import streamlit as st
from src.db_manager import DatabaseManager
from src.adding_spending import AddingSpending
import src.utils as utils

# TODO: make adding a new shop+location in the add spending tab add to the db

def double_run():
    if "has_rerun" not in st.session_state:
        st.session_state["has_rerun"] = False

    if not st.session_state["has_rerun"]:
        st.session_state["has_rerun"] = True
        st.rerun()
    else:
        st.session_state["has_rerun"] = False

if __name__ == "__main__":
    db_manager = DatabaseManager()

    input_tab, data_base, data_tab = st.tabs(["Input Spending", "DataBase", "View Data"])
    with input_tab:

        adding_spending = AddingSpending(st.session_state, db_manager)

        adding_spending.set_shop_brand(
            st.selectbox("Shop Name", db_manager.get_all_shop_brands(), accept_new_options=True, index=None)
        )
        selected_shop_locations = db_manager.get_shop_locations(adding_spending.shop_brand)
        if selected_shop_locations != []:
            adding_spending.set_shop_location(
                st.selectbox("Location Name", selected_shop_locations, accept_new_options=True, index=None)
            )

        adding_spending.set_spending_category(
            st.selectbox("Spending Category", db_manager.get_all_categories(), index=None)
        )
        adding_spending.set_spending_date(
            st.date_input("Spending Date", format="DD/MM/YYYY")
        )
        adding_spending.set_spending_time(
            st.time_input("Spending Time", value=None)
        )

        st.markdown("## Items")

        if "product_selection" not in st.session_state:
            st.session_state["product_selection"] = None

        selected_product = st.selectbox(
            "Add Item",
            options=db_manager.get_all_products(adding_spending.shop_brand),
            accept_new_options=True, index=None, key="product_selection"
        )
        def add_item_button_press(adding_spending_obj, selected_option):
            adding_spending_obj.add_product(selected_option)
            del st.session_state["product_selection"]

        st.button("Add", on_click=lambda: add_item_button_press(adding_spending, selected_product))

        spending_display_df = adding_spending.to_display_df()

        st.session_state["adding_spending_df"] = adding_spending.from_display_df(
            utils.data_editor(
                spending_display_df,
                {
                    "ID": {"type": "number", "editable": False},
                    "Price Per": {"type": "number", "format": "£%.2f"},
                }
            )
        )

        if st.dialog("Save Spending", width="large"):
            total_cost = sum(filter(
                lambda num: not utils.isNone(num),
                spending_display_df["Price Per"] * spending_display_df["Num Purchased"]
            ))
            st.markdown(f"Add Spending Event of spending £{total_cost:.2f}")
            if st.button("ADD"):
                adding_spending.add_spending_to_db()
                # del st.session_state["adding_spending_df"]



    with data_base:

        with st.expander("Products"):
            db_manager.save_products_df_changes(
                utils.data_editor(
                    db_manager.get_products_display_df(),
                    {
                        "ID": {"type":"number", "editable": False},
                        "Price": {"type": "number", "format": "£%.2f"},
                        "Shop": {"type": "select", "options": db_manager.get_all_shop_brands()},
                        "Category": {"type": "select", "options": db_manager.get_all_category_strings()}
                    },
                )
            )

        with st.expander("Shops"):
            db_manager.save_shops_df_changes(
                utils.data_editor(
                    db_manager.get_shops_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                    },
                )
            )

        with st.expander("ShopLocations"):
            db_manager.save_locations_df_changes(
                utils.data_editor(
                    db_manager.get_locations_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Brand": {"type": "select", "options": db_manager.get_all_shop_brands()}
                    },
                )
            )

        with st.expander("Categories"):
            db_manager.save_categories_df_changes(
                utils.data_editor(
                    db_manager.get_categories_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Importance": {"type": "number"},
                        "Parent Category": {"type": "select", "options": db_manager.get_all_categories()}
                    },
                )
            )

        with st.expander("Spending Events"):
            db_manager.save_spending_events_df_changes(
                utils.data_editor(
                    db_manager.get_spending_events_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Shop": {"type": "select", "options": db_manager.get_all_shop_brands()},
                        "Location": {"type": "select", "options": db_manager.get_shop_locations(None)},
                        "Category": {"type": "select", "options": db_manager.get_all_categories()}
                    },
                )
            )

        with st.expander("Spending Items"):
            db_manager.save_spending_items_df_changes(
                utils.data_editor(
                    db_manager.get_spending_items_display_df(),
                    {
                        "ID": {"type": "number", "editable": False},
                        "Event ID": {"type": "select", "options": db_manager.spending_events.list_all_in_column("spending_event_id")},
                        "Name": {"type": "select", "options": db_manager.products.list_all_in_column("name")},
                        "Price": {"type": "number", "format": "£:.2f"},
                        "Num Purchased": {"type": "number"}
                    },
                )
            )

    double_run()





