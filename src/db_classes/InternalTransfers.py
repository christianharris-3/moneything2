from src.DatabaseTable import DatabaseTable
import src.utils as utils

class InternalTransfers(DatabaseTable):
    TABLE = "InternalTransfers"
    COLUMNS = [
        "transfer_id",
        "source_store_id",
        "target_store_id",
        "date",
        "time",
        "money_transferred"
    ]
    DISPLAY_DF_RENAMED = {
        "transfer_id": "ID",
        "source_store": "Source",
        "target_store": "Target",
        "date": "Date",
        "time": "Time",
        "money_transferred": "Transferred"
    }

    def __init__(self, select_call, money_stores):
        self.display_inner_joins = utils.make_display_inner_joins(
            (money_stores, "source_store_id", "name", "source_store", "money_store_id"),
            (money_stores, "target_store_id", "name", "target_store", "money_store_id")
        )
        super().__init__(select_call, self.COLUMNS)

    def from_display_df(self, display_df):
        renamed_df = super().from_display_df(display_df)

        renamed_df["date"] = renamed_df["date"].apply(utils.conform_date_string)
        renamed_df["time"] = renamed_df["time"].apply(utils.conform_time_string)

        return renamed_df