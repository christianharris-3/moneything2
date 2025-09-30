from src.DatabaseTable import DatabaseTable
import src.utils as utils
import pandas as pd

class Transactions(DatabaseTable):
    TABLE = "Transactions"
    COLUMNS = [
        "transaction_id",
        "date",
        "time",
        "override_money",
        "is_income",
        "money_store_id",
        "vendor_id",
        "shop_location_id",
        "category_id",
        "description"
    ]
    DISPLAY_DF_RENAMED = {
        "transaction_id": "ID",
        "date": "Date",
        "time": "Time",
        "override_money": "Override Money",
        "is_income": "Is Income",
        "money_store": "Money Store",
        "vendor_name": "Vendor",
        "shop_location": "Location",
        "category_string": "Category",
        "description": "Description"
    }

    def __init__(self, select_call, money_stores, vendors, shop_locations, categories):
        self.display_inner_joins = utils.make_display_inner_joins(
            (money_stores, "money_store_id", "name", "money_store"),
            (vendors, "vendor_id", "name", "vendor_name"),
            (shop_locations, "shop_location_id", "shop_location"),
            (categories, "category_id", "category_string")
        )
        super().__init__(select_call, self.COLUMNS)

    def from_display_df(self, display_df):
        renamed_df = super().from_display_df(display_df)

        renamed_df["date"] = renamed_df["date"].apply(utils.conform_date_string)
        renamed_df["time"] = renamed_df["time"].apply(utils.conform_time_string)

        return renamed_df
