from src.DatabaseTable import DatabaseTable
import src.utils as utils

class SpendingEvents(DatabaseTable):
    TABLE = "SpendingEvents"
    COLUMNS = [
        "spending_event_id",
        "date",
        "time",
        "shop_id",
        "shop_location_id"
    ]
    def __init__(self, select_call, shops, shop_locations):
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(
            self.db_data, shops, shop_locations
        )

    def update_foreign_data(self, db_data, shops, shop_locations):
        db_data["shop_name"] = db_data.merge(
            shops.db_data,
            left_on="shop_id",
            right_on="shop_id",
            how="left"
        )["brand"]

        db_data["shop_location"] = db_data.merge(
            shop_locations.db_data,
            left_on="shop_location_id",
            right_on="shop_location_id",
            how="left"
        )["shop_location"]

        return utils.force_int_ids(db_data)

    def to_display_df(self):
        df = self.db_data.rename({
            "spending_event_id": "ID",
            "date": "Date",
            "time": "Time",
            "shop_name": "Shop",
            "shop_location": "Location"
        }, axis=1)

        return df[["ID", "Date", "Time", "Shop", "Location"]]

    def from_display_df(self, display_df, shops, shop_locations):
        renamed_df = display_df.rename({
            "ID": "spending_event_id",
            "Date": "date",
            "Time": "time",
            "Shop": "shop_name",
            "Location": "shop_location"
        }, axis=1)

        renamed_df["shop_id"] = renamed_df.merge(
            shops.db_data,
            left_on="shop_name",
            right_on="brand",
            how="left"
        )["shop_id"]

        renamed_df["shop_location_id"] = renamed_df.merge(
            shop_locations.db_data,
            left_on="shop_location",
            right_on="shop_location",
            how="left"
        )["shop_location_id"]

        return self.update_foreign_data(
            renamed_df[["spending_event_id", "date", "time", "shop_id", "shop_location_id"]],
            shops, shop_locations
        )