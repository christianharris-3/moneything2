import math
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode
from pandas.errors import IntCastingNaNError
import streamlit as st
import random


def isNone(value):
    return value is None or (isinstance(value, float) and math.isnan(value))

def force_int_ids(df):
    df = df.copy()
    for column in df.columns:
        if column.endswith("_id"):
            try:
                df[column] = df[column].astype(int)
            except (IntCastingNaNError, TypeError):
                df[column] = df[column].astype(float)
    return df

def data_editor(df, column_config, aggrid=False):
    if aggrid:
        return aggrid_data_editor(df, column_config)
    else:
        return streamlit_data_editor(df, column_config)

def aggrid_data_editor(df, column_config: dict[str, dict] = None):
    grid_options = GridOptionsBuilder.from_dataframe(df)
    grid_options.configure_selection("multiple", use_checkbox=True)
    grid_options.configure_auto_height(True)

    if column_config is None:
        column_config = {}

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

def streamlit_data_editor(df, column_config: dict[str, dict]):
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
            case _:
                config_obj = st.column_config.Column(**args)

        st_column_config[column_title] = config_obj

    return st.data_editor(
        df,
        column_config=st_column_config,
        hide_index=True,
        num_rows="dynamic",
    )
