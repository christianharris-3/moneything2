from src.DatabaseTable import DatabaseTable
import src.utils as utils

class ShopLocations(DatabaseTable):
    TABLE = "ShopLocations"
    COLUMNS = [
        "shop_location_id",
        "shop_location",
        "shop_id"
    ]
    def __init__(self, select_call, shops):
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(self.db_data, shops)

    def update_foreign_data(self, db_data, shops):
        db_data["brand"] = db_data.merge(
            shops.db_data,
            left_on="shop_id",
            right_on="shop_id",
            how="left"
        )["brand"]
        return db_data

    def get_shop_locations(self, shop_brand):
        return sorted(set(self.db_data[self.db_data["brand"] == shop_brand]["shop_location"]))

    def to_display_df(self):
        df = self.db_data.rename({
            "shop_location_id": "ID",
            "shop_location": "Location",
            "brand": "Brand"
        }, axis=1)

        return df[["ID", "Location", "Brand"]]

    def from_display_df(self, display_df, shops):
        renamed_df = display_df.rename({
            "ID": "shop_location_id",
            "Location": "shop_location",
            "Brand": "brand"
        }, axis=1)

        renamed_df["shop_id"] = renamed_df.merge(
            shops.db_data,
            left_on="brand",
            right_on="brand",
            how="left"
        )["shop_id"]

        return self.update_foreign_data(
            renamed_df[["shop_location_id", "shop_location", "shop_id"]],
            shops
        )

