import pandas as pd
from src.DatabaseTable import DatabaseTable

class Products(DatabaseTable):
    TABLE = "Products"
    COLUMNS = [
        "product_id",
         "name",
         "price",
         "shop_id",
         "category_id"
     ]
    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

    def to_display_df(self, shops, categories):
        df = self.db_data.rename({
            "product_id": "ID",
            "name": "Name",
            "price": "Price",
        }, axis=1
        )
        df["Category"] = df["category_id"].apply(categories.get_category_string)
        df["Shop"] = df["shop_id"].apply(lambda id_: shops.get_shop_string(id_, False))

        return df[["ID", "Name", "Price", "Shop", "Category"]]

    def from_display_df(self, display_df, shops, categories):
        renamed_df = display_df.rename({
            "ID": "product_id",
            "Name": "name",
            "Price": "price"
        }, axis=1)

        renamed_df["category_id"] = renamed_df["Category"].apply(categories.get_category_id_from_string)
        renamed_df["shop_id"] = renamed_df["Shop"].apply(shops.get_shop_id)

        return renamed_df[["product_id", "name", "price", "shop_id", "category_id"]]
