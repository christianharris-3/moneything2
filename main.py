import streamlit as st
import pandas as pd
from src.database import Database

def add_new_item(item_name):
    pass

def add_existing_item(item_id):
    pass

def double_run():
    if "has_rerun" not in st.session_state:
        st.session_state["has_rerun"] = False

    if not st.session_state["has_rerun"]:
        st.session_state["has_rerun"] = True
        st.rerun()
    else:
        st.session_state["has_rerun"] = False

if __name__ == "__main__":
    db = Database()
    db.create_tables()

    products = db.load_products()
    shops = db.load_shops()
    categories = db.load_categories()


    input_tab, data_tab = st.tabs(["Input Spending", "View Data"])
    with input_tab:

        with st.expander("Add Spending"):
            shop_brand = st.selectbox("Shop Name", shops, accept_new_options=True)
            shop_location = st.selectbox("Location Name", [], accept_new_options=True)

            st.markdown("## Items")

            item_name = st.selectbox("Add Item", [], accept_new_options=True)
            # with st.button("Add"):
                # if item_name
                # add_item(item_name)

        with st.expander("Products"):
            products_df = products.to_display_df(shops, categories)
            products_edited = st.data_editor(
                products_df,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Price": st.column_config.NumberColumn(format="£%.2f"),
                    "Shop": st.column_config.SelectboxColumn(
                        options=shops.get_all_shops(False)
                    ),
                    "Category": st.column_config.SelectboxColumn(
                        options=categories.list_category_strings()
                    )
                },
                hide_index=True,
                num_rows="dynamic"
            )
            products.save_changes(
                products.from_display_df(products_edited, shops, categories),
                db
            )

        with st.expander("Shops"):
            shops_df = shops.to_display_df()
            shops_edited = st.data_editor(
                shops_df,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                },
                hide_index=True,
                num_rows="dynamic"
            )
            shops.save_changes(shops.from_display_df(shops_edited), db)

        with st.expander("Categories"):
            categories_df = categories.to_display_df()
            categories_edited = st.data_editor(
                categories_df,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Importance": st.column_config.NumberColumn(),
                    "Parent Category": st.column_config.SelectboxColumn(
                        options=categories.list_category_names()
                    ),
                },
                hide_index=True,
                num_rows="dynamic"
            )
            categories.save_changes(categories.from_display_df(categories_edited), db)


    double_run()




