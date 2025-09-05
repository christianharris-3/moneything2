import streamlit as st
import datetime
import src.utils as utils
import pandas as pd

def build_money_ui(db_manager):
    money_store = st.radio(
        "Money Store",
        db_manager.get_all_money_stores()
    )
    if money_store is not None:
        x_values, y_values = get_graph_info(db_manager, money_store)


def get_graph_info(db_manager, money_store) -> tuple[list[datetime], list[float]]:
    money_store_id = db_manager.money_stores.get_id_from_value("name", money_store)

    transactions_df = db_manager.transactions.get_filtered_df(
        "money_store_id", money_store_id
    )

    transfer_out_df = db_manager.internal_transfers.get_filtered_df(
        "source_store_id", money_store_id
    )[["date", "money_transferred"]]
    transfer_out_df["money_transferred"] = -transfer_out_df["money_transferred"]
    transfer_in_df = db_manager.internal_transfers.get_filtered_df(
        "target_store_id", money_store_id
    )[["date", "money_transferred"]]
    transfer_df = pd.concat([transfer_in_df, transfer_out_df])
    snapshots_df = db_manager.store_snapshots.get_filtered_df(
        "money_store_id", money_store_id
    )
    money_store_row = db_manager.money_stores.get_db_row(money_store_id)

    creation = {
        "relative": False,
        "timestamp": utils.string_to_date(money_store_row["creation_date"]),
        "type": "creation",
        "value": 0
    }

    change_data = []

    # for i, row in transfer_df:
    #     change_data.append({
    #         "relative": True,
    #         "timestamp": utils.string_to_date(row["date"]),
    #         "type": "transfer",
    #         "value"
    #     })

    print("TRANSFERS")
    print(transfer_df)




    x_values = []
    y_values = []

    return x_values, y_values


