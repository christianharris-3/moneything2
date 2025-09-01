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