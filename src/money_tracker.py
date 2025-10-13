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
        st.line_chart(
            pd.DataFrame({"Date":x_values, "Money":y_values}),
            x="Date", y="Money"
        )


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

    change_data = []

    for i, row in transfer_df.iterrows():
        change_data.append({
            "relative": True,
            "timestamp": utils.string_to_date(row["date"]),
            "type": "transfer",
            "value": row["money_transferred"]
        })

    for i, row in transactions_df.iterrows():
        value = row["override_money"]
        if value is None:
            db_manager.spending_items.get_filtered_df(
                "transaction_id", row["transaction_id"]
            )
            value = sum(
                db_manager.spending_items.get_filtered_df(
                    "transaction_id", row["transaction_id"]
                )["display_price"]
            )
        if not row["is_income"]:
            value = -value
        change_data.append({
            "relative": True,
            "timestamp": utils.string_to_date(row["date"]),
            "type": "transaction",
            "value": value
        })

    for i, row in snapshots_df.iterrows():
        change_data.append({
            "relative": False,
            "timestamp": utils.string_to_date(row["snapshot_date"]),
            "type": "snapshot",
            "value": row["money_stored"]
        })

    creation = {
        "relative": False,
        "timestamp": utils.string_to_date(money_store_row["creation_date"]),
        "type": "creation",
        "value": 0
    }

    change_data.sort(
        key=lambda x:
        datetime.date.today()
        if utils.isNone(x["timestamp"])
        else x["timestamp"]
    )
    if change_data[0]["timestamp"]<creation["timestamp"]:
        creation["timestamp"] = change_data[0]["timestamp"] - datetime.timedelta(days=1)

    change_data.insert(0, creation)

    x_values = []
    y_values = []

    money_stored = 0
    for change in change_data:
        if change["relative"]:
            money_stored+=change["value"]
        else:
            money_stored = change["value"]

        x_values.append(change["timestamp"])
        y_values.append(money_stored)

    return x_values, y_values


