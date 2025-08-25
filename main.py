import streamlit as st
from src.db_manager import DatabaseManager

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

    input_tab, data_tab = st.tabs(["Input Spending", "View Data"])
    with input_tab:

        with st.expander("Add Spending"):
            # shop_brand = st.selectbox("Shop Name", shops, accept_new_options=True)
            shop_location = st.selectbox("Location Name", [], accept_new_options=True)

            st.markdown("## Items")

            item_name = st.selectbox("Add Item", [], accept_new_options=True)
            # with st.button("Add"):
                # if item_name
                # add_item(item_name)

        with st.expander("Products"):
            db_manager.save_products_df_changes(
                st.data_editor(
                    db_manager.get_products_display_df(),
                    column_config={
                        "ID": st.column_config.NumberColumn(disabled=True),
                        "Price": st.column_config.NumberColumn(format="£%.2f"),
                        "Shop": st.column_config.SelectboxColumn(
                            options=db_manager.get_all_shop_brands()
                        ),
                        "Category": st.column_config.SelectboxColumn(
                            options=db_manager.get_all_category_strings()
                        )
                    },
                    hide_index=True,
                    num_rows="dynamic"
                )
            )

        with st.expander("Shops"):
            db_manager.save_shops_df_changes(
                st.data_editor(
                    db_manager.get_shops_display_df(),
                    column_config={
                        "ID": st.column_config.NumberColumn(disabled=True),
                    },
                    hide_index=True,
                    num_rows="dynamic"
                )
            )

        with st.expander("Categories"):
            db_manager.save_categories_df_changes(
                st.data_editor(
                    db_manager.get_categories_display_df(),
                    column_config={
                        "ID": st.column_config.NumberColumn(disabled=True),
                        "Importance": st.column_config.NumberColumn(),
                        "Parent Category": st.column_config.SelectboxColumn(
                            options=db_manager.get_all_categories()
                        ),
                    },
                    hide_index=True,
                    num_rows="dynamic"
                )
            )

        with st.expander("ShopLocations"):
            db_manager.save_locations_df_changes(
                st.data_editor(
                    db_manager.get_locations_display_df(),
                    column_config={
                        "ID": st.column_config.NumberColumn(disabled=True),
                        "Brand": st.column_config.SelectboxColumn(
                            options=db_manager.get_all_shop_brands()
                        )
                    },
                    hide_index=True,
                    num_rows="dynamic"
                )
            )


    double_run()




