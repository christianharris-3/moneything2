import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode

ITEMS_PER_PAGE = 15

def pages_manager_ui(state, df):
    num_items = len(df)
    total_pages = num_items//ITEMS_PER_PAGE+1

    if state["page"]>total_pages:
        state["page"] = 1

    left, middle, right = st.columns([1,1.6,1], width=200, vertical_alignment="center")

    def move_page(state, change):
        state["page"]+=change

    left.button(
        "◀️",
        disabled=state["page"]<=1,
        on_click=move_page,
        args=(state, -1)
    )
    right.button(
        "▶️",
        disabled=state["page"]>=total_pages,
        on_click=move_page,
        args=(state, 1)
    )
    middle.markdown(f"Page {state['page']}/{total_pages}")

    return df.iloc[ITEMS_PER_PAGE * (state["page"] - 1):ITEMS_PER_PAGE * state["page"]]


def double_run():
    if "has_rerun" not in st.session_state:
        st.session_state["has_rerun"] = False

    if not st.session_state["has_rerun"]:
        st.session_state["has_rerun"] = True
        st.rerun()
    else:
        st.session_state["has_rerun"] = False

# EXTRA_INCLUDE_UI_CACHE = [
#     "selected_category"
# ]

def store_to_ui_cache(page_key):
    if "ui_cache" not in st.session_state:
        st.session_state["ui_cache"] = {
            page_key: {}
        }
    to_store = {}
    for key, val in st.session_state.items():
        if "input" in key:
            to_store[key] = val

    st.session_state["ui_cache"][page_key] = to_store

def load_ui_cache(page_key):
    if "ui_cache" not in st.session_state:
        return

    if page_key in st.session_state["ui_cache"]:
        for key, val in st.session_state["ui_cache"][page_key].items():
            st.session_state[key] = val


def data_editor(df, column_config=None, aggrid=False, container=None, num_rows="dynamic"):
    if column_config is None:
        column_config = {}
    if aggrid:
        return aggrid_data_editor(df, column_config)
    else:
        return streamlit_data_editor(df, column_config, container, num_rows=num_rows)

def aggrid_data_editor(df, column_config: dict[str, dict]):
    grid_options = GridOptionsBuilder.from_dataframe(df)
    grid_options.configure_selection("multiple", use_checkbox=True)
    grid_options.configure_auto_height(True)

    for column_title in df.columns:
        if column_title not in column_config.keys():
            column_config[column_title] = {}

    for column_title in column_config:
        config = column_config[column_title]
        args = {
            "editable": config.get("editable", True),
            "filter": config.get("filter", True),
            "sortable": config.get("sortable", True),
        }
        if "options" in config:
            args["cellEditor"] = "agSelectCellEditor"
            args["cellEditorParams"] = {"values": config["options"]}

        grid_options.configure_column(
            column_title,
            **args
        )
    build_options = grid_options.build()

    data_edits = AgGrid(
        df,
        gridOptions=build_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=True,
    )
    return data_edits.data

def streamlit_data_editor(df, column_config: dict[str, dict], container=None, num_rows="dynamic"):
    if container is None:
        container = st

    st_column_config = {}
    for column_title in column_config:
        config = column_config[column_title]
        args = {
            "disabled": not config.pop("editable", True),
        }
        type_ = config.pop("type", "column")
        args.update(config)
        match type_:
            case "number":
                config_obj = st.column_config.NumberColumn(**args)
            case "select":
                config_obj = st.column_config.SelectboxColumn(**args)
            case "boolean":
                config_obj = st.column_config.CheckboxColumn(**args)
                df[column_title] = df[column_title].apply(
                    lambda x: True if x==1 else False
                )
            case _:
                config_obj = st.column_config.Column(**args)

        st_column_config[column_title] = config_obj

    return container.data_editor(
        df,
        column_config=st_column_config,
        hide_index=True,
        num_rows=num_rows,
    )