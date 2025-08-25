import pandas as pd
from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Products(DatabaseTable):
    TABLE = "Products"
    COLUMNS = [
        "product_id",
         "name",
         "price",
         "shop_id",
         "category_id"
    ]
    def __init__(self, select_call, shops, categories):
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(
            self.db_data, shops, categories
        )

    def update_foreign_data(self, db_data, shops, categories):
        db_data["category_string"] = db_data.merge(
            categories.db_data,
            left_on="category_id",
            right_on="category_id",
            how="left"
        )["category_string"]
        db_data["shop_name"] = db_data.merge(
            shops.db_data,
            left_on="shop_id",
            right_on="shop_id",
            how="left"
        )["brand"]

        return utils.force_int_ids(db_data)

    def to_display_df(self, shops, categories):
        df = self.db_data.rename({
            "product_id": "ID",
            "name": "Name",
            "price": "Price",
            "category_string": "Category",
            "shop_name": "Shop",
        }, axis=1
        )

        return df[["ID", "Name", "Price", "Shop", "Category"]]

    def from_display_df(self, display_df, shops, categories):
        renamed_df = display_df.rename({
            "ID": "product_id",
            "Name": "name",
            "Price": "price",
            "Category": "category_string",
            "Shop": "shop_name"
        }, axis=1)

        renamed_df["category_id"] = renamed_df.merge(
            categories.db_data,
            left_on="category_string",
            right_on="category_string",
            how="left"
        )["category_id"]
        renamed_df["shop_id"] = renamed_df.merge(
            shops.db_data,
            left_on="shop_name",
            right_on="brand",
            how="left"
        )["shop_id"]

        return self.update_foreign_data(
            utils.force_int_ids(renamed_df[["product_id", "name", "price", "shop_id", "category_id"]]),
            shops, categories
        )
