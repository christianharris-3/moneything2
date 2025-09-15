import pandas as pd
import src.utils as utils
import datetime


def add_money_store(db_manager, name, date, stored):
    date = utils.date_to_string(date)
    date_now = utils.date_to_string(datetime.date.today())

    money_store_id = db_manager.db.create_row(
        db_manager.money_stores.TABLE,
        {
            "name": name,
            "creation_date": date
        }
    )

    if stored is not None:
        db_manager.db.create_row(
            db_manager.store_snapshots.TABLE,
            {
                "money_store_id": money_store_id,
                "snapshot_date": date_now,
                "money_stored": stored
            }
        )

def add_internal_transfer(
        db_manager,
        source_money_store,
        target_money_store,
        date,
        time,
        transfer_amount
):
    date = utils.date_to_string(date)
    time = utils.time_to_string(time)

    store_ids = []
    for store_name in [source_money_store, target_money_store]:
        if store_name is None:
            store_ids.append(None)
        else:
            filtered = db_manager.money_stores.db_data[
                db_manager.money_stores.db_data["name"] == store_name]
            if len(filtered) == 0:
                store_ids.append(None)
            else:
                store_ids.append(filtered.iloc[0]["money_store_id"])

    db_manager.db.create_row(
        db_manager.internal_transfers.TABLE,
        {
            "source_store_id": store_ids[0],
            "target_store_id": store_ids[1],
            "date": date,
            "time": time,
            "money_transferred": transfer_amount
        }
    )
