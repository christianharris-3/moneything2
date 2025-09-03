import pandas as pd
import src.utils as utils


def add_money_store(db_manager, name, date, stored):
    money_store_id = db_manager.money_stores.generate_id()
    date = utils.date_to_string(date)

    db_manager.db.insert(
        db_manager.money_stores.TABLE,
        pd.DataFrame([{
            "money_store_id": money_store_id,
            "name": name,
            "creation_date": date
        }]).iloc[0]
    )

    if stored is not None:
        snapshot_id = db_manager.store_snapshots.generate_id()

        db_manager.db.insert(
            db_manager.store_snapshots.TABLE,
            pd.DataFrame([{
                "snapshot_id": snapshot_id,
                "money_store_id": money_store_id,
                "snapshot_date": date,
                "money_stored": stored
            }]).iloc[0]
        )

def add_internal_transfer(
        db_manager,
        source_money_store,
        target_money_store,
        date,
        time,
        transfer_amount
):
    transfer_id = db_manager.internal_transfers.generate_id()
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

    db_manager.db.insert(
        db_manager.internal_transfers.TABLE,
        pd.DataFrame([{
            "transfer_id": transfer_id,
            "source_store_id": store_ids[0],
            "target_store_id": store_ids[1],
            "date": date,
            "time": time,
            "money_transferred": transfer_amount
        }]).iloc[0]
    )
