from src.DatabaseTable import DatabaseTable
import src.utils as utils

class SpendingEvents(DatabaseTable):
    TABLE = "SpendingEvents"
    COLUMNS = [
        "spending_event_id",
        "date",
        "time",
        "shop_id",
        "shop_location_id",
        "category_id"
    ]
    DISPLAY_DF_RENAMED = {
        "spending_event_id": "ID",
        "date": "Date",
        "time": "Time",
        "shop_name": "Shop",
        "shop_location": "Location",
        "category_string": "Category"
    }

    def __init__(self, select_call, shops, shop_locations, categories):
        self.display_inner_joins = utils.make_display_inner_joins(
            (shops, "shop_id", "brand", "shop_name"),
            (shop_locations, "shop_location_id", "shop_location"),
            (categories, "category_id", "category_string"),
        )
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(
            self.db_data
        )

    def from_display_df(self, display_df):
        renamed_df = super().from_display_df(display_df)

        renamed_df["date"] = renamed_df["date"].apply(utils.conform_date_string)
        renamed_df["time"] = renamed_df["time"].apply(utils.conform_time_string)

        return renamed_df