import math
from src.logger import log
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode
from pandas.errors import IntCastingNaNError
import pandas as pd
import streamlit as st
import datetime


def isNone(value):
    return value is None or (isinstance(value, float) and math.isnan(value))

def force_int_ids(df):
    df = df.copy()
    for column in df.columns:
        if column.endswith("_id"):
            try:
                df[column] = df[column].astype(int)
            except (IntCastingNaNError, TypeError, ValueError):
                df[column] = df[column].astype(float)
    return df

def get_row_differences(original_row, updated_row):
    differences = {}
    for column in updated_row.keys():
        if (column not in original_row) or (original_row[column] != updated_row[column]):
            if not (pd.isna(original_row[column]) and pd.isna(updated_row[column])):
                differences[column] = updated_row[column]
    return differences

def filter_df(df, column, value):
    if isinstance(column, list):
        for i in range(len(column)):
            df = df[(df[column[i]] == value[i]) | (pd.isna(df[column[i]]) & pd.isna(value[i]))]
        return df
    return df[(df[column] == value) | (pd.isna(df[column]) & pd.isna(value))]

def double_run():
    if "has_rerun" not in st.session_state:
        st.session_state["has_rerun"] = False

    if not st.session_state["has_rerun"]:
        st.session_state["has_rerun"] = True
        st.rerun()
    else:
        st.session_state["has_rerun"] = False

def is_authenticated() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    return st.session_state["authenticated"]

def block_if_no_auth():
    if not is_authenticated():
        log("Forcing user back to login page")
        st.switch_page("main.py")

def get_user_id():
    if is_authenticated():
        return st.session_state["current_user_id"]
    return None

def make_display_inner_joins(*args) -> list[dict]:
    """
    Takes any number of lists of data to generate inner join data
    Each input list takes the form:
    [
        object Object: the target object containing the data being pulled from
        left_join_id str: the name of the column joining the 2 tables
        source_column str: the name of the column being taken from Object
        new_column=target_column str: the name of the new column being created
        right_join_id str
    ]

    :param args:
    :return:
    """
    display_inner_joins = []
    for input_list in args:
        display_inner_joins.append({
            "object": input_list[0],
            "left_on": input_list[1],
            "right_on": input_list[1],
            "source_column": input_list[2],
            "new_column": input_list[2],
        })
        if len(input_list)>3:
            display_inner_joins[-1][
                "new_column"
            ]=input_list[3]
        if len(input_list)>4:
            display_inner_joins[-1][
                "right_on"
            ] = input_list[4]

    return display_inner_joins


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

def conform_date_string(input_string: str) -> str:
    date_obj = string_to_date(input_string)
    if date_obj is None:
        return input_string
    else:
        return date_to_string(date_obj)


def string_to_date(input_string) -> datetime.date | None:
    if isNone(input_string):
        return None

    string = input_string.lower()
    months = ["jan", "feb", "mar", "apr", "may", "jun",
              "jul", "aug", "sep", "oct", "nov", "dec"]
    split = split_to_numbers(string)

    day = "1" if len(split)<3 else split[-3]
    month = "1" if len(split)<2 else split[-2]
    year = "1970" if len(split)<1 else split[-1]

    for i in range(len(months)):
        if months[i] in string:
            day = month
            month = i+1
            break

    try:
        day = int(day)
        month = int(month)
        year = int(year)
    except Exception as e:
        log(f"ERROR converting date string: {input_string} -> {e}")
        return None
    if year<100:
        year += 2000
    try:
        date = datetime.date(year, month, day)
    except Exception as e:
        log(f"FAILED TO CONVERT: {input_string}, date output is: {day}/{month}/{year}, Exception: {e}", level="error")
        return None
    return date

def date_to_string(date: datetime.date) -> str | None:
    if date is None:
        return None
    return date.strftime("%a %d %b %Y")


def conform_time_string(input_string: str) -> str:
    time_obj = string_to_time(input_string)
    if time_obj is None:
        return input_string
    else:
        return time_to_string(time_obj)

def string_to_time(input_string: str) -> datetime.time | None:
    if isNone(input_string):
        return None

    string = input_string.lower()
    split = split_to_numbers(string)

    if len(split)<2:
        return None

    hours = int(split[0])
    minutes = int(split[1])
    if "pm" in string:
        hours = (hours+12)%24
    return datetime.time(hour=hours, minute=minutes%60)

def time_to_string(time: datetime.time) -> None | str:
    if time is None:
        return None
    return time.strftime("%I:%M%p")

def extract_numbers(string: str) -> str:
    output = ""
    for char in string:
        if char in "0123456789":
            output+=char
    return output

def split_to_numbers(string: str) -> list[str]:
    separators = "./-_:"
    for seperator in separators:
        string = string.replace(seperator, " ")
    split = list(filter(
        lambda x: bool(x),
        map(extract_numbers,string.split())
    ))
    return split


def get_df_matching_search_term(df, search_term):
    if search_term is None:
        search_term = ""
    def string_in_series(string, series):
        if isinstance(series, pd.Series):
            return series.apply(
                lambda value: str(string).lower().strip() in str(value).lower()
            )
        else:
            return list(map(
                lambda value: str(string).lower().strip() in str(value).lower(),
                series
            ))

    def row_matches_search_term(row, search_term):
        if isNone(search_term):
            return True
        search_term = search_term.strip()
        if search_term == "":
            return True
        if any(string_in_series(search_term, row)):
            return True
        if ":" in search_term:
            column, term = search_term.split(":", 1)
            if term == "":
                return True
            bool_map = string_in_series(column, row.keys())
            if any(bool_map):
                if any(string_in_series(term, row[bool_map])):
                    return True
        return False
    bools = None
    for term in search_term.split(";"):
        bools_2 = df.apply(
            lambda row: row_matches_search_term(row, term),
            axis=1
        )
        if bools is None:
            bools = bools_2.astype(bool)
        else:
            bools = bools & bools_2.astype(bool)
    return df[bools]
