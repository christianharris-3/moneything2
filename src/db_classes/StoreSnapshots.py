from src.DatabaseTable import DatabaseTable
import src.utils as utils

class StoreSnapshots(DatabaseTable):
    TABLE = "StoreSnapshots"
    COLUMNS = [
        "snapshot_id",
        "money_store_id",
        "snapshot_date",
        "snapshot_time",
        "money_stored"
    ]
    DISPLAY_DF_RENAMED = {
        "snapshot_id": "ID",
        "money_store": "Money Store",
        "snapshot_date": "Date",
        "snapshot_time": "Time",
        "money_stored": "Balance"
    }

    def __init__(self, select_call, money_stores):
        self.display_inner_joins = utils.make_display_inner_joins(
            (money_stores, "money_store_id", "name", "money_store")
        )
        super().__init__(select_call, self.COLUMNS)

    def to_display_df(self):
        return super().to_display_df(
            self.update_foreign_data(
                utils.force_int_ids(self.db_data)
            )
        )

    def from_display_df(self, display_df):
        renamed_df = super().from_display_df(display_df)

        renamed_df["snapshot_date"] = renamed_df["snapshot_date"].apply(utils.conform_date_string)
        renamed_df["snapshot_time"] = renamed_df["snapshot_time"].apply(utils.conform_time_string)

        return renamed_df