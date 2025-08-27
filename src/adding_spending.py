import pandas as pd
import math
import src.utils as utils

class AddingSpending:
    def __init__(self, session_state, db_manager):
        if not "adding_spending_df" in session_state:
            session_state["adding_spending_df"] = pd.DataFrame(
                columns=[
                    "parent_product_id",
                    "new_item_name",
                    "override_price",
                    "num_purchased"
                ]
            )

        self.spending_df = session_state["adding_spending_df"]
        self.db_manager = db_manager

        self.spending_time = None
        self.spending_date = None
        self.shop_brand = None
        self.shop_location = None

    def set_spending_time(self, spending_time):
        self.spending_time = spending_time
    def set_spending_date(self, spending_date):
        self.spending_date = spending_date
    def set_shop_brand(self, shop_brand):
        self.shop_brand = shop_brand
    def set_shop_location(self, shop_location):
        self.shop_location = shop_location


    def add_product(self, product_string):
        product_id = self.db_manager.products.get_product_id_from_product_string(product_string)
        if product_id is None:
            self.spending_df.loc[len(self.spending_df)] = {
                "parent_product_id": math.nan,
                "new_item_name": product_string,
                "override_price": None,
                "num_purchased": 1
            }
        else:
            self.spending_df.loc[len(self.spending_df)] = {
                "parent_product_id": product_id,
                "new_item_name": None,
                "override_price": None,
                "num_purchased": 1
            }

        print("PRODUCT ADDED")
        print(self.spending_df)

    def to_display_df(self):
        df = self.spending_df.merge(
            self.db_manager.products.db_data,
            left_on="parent_product_id",
            right_on="product_id",
            how="left",
        ).rename({
            "parent_product_id": "ID",
            "name": "Name",
            "override_price": "Price Per",
            "price": "parent_price",
            "num_purchased": "Num Purchased",
            "category_string": "Category"
        }, axis=1)

        df["Price Per"] = df["Price Per"].combine(
            df["parent_price"],
            lambda price, parent: price if not utils.isNone(price) else parent
        )
        df["Name"] = df["Name"].combine(
            df["new_item_name"],
            lambda parent, new: parent if not utils.isNone(parent) else new
        )

        return df[["ID", "Name", "Price Per", "Num Purchased"]]

    def from_display_df(self, edited_df):
        renamed_df = edited_df.rename({
            "ID": "parent_product_id",
            "Num Purchased": "num_purchased"
        }, axis=1)

        merged_df = renamed_df.merge(
            self.db_manager.products.db_data,
            left_on="parent_product_id",
            right_on="product_id",
            how="left"
        )
        renamed_df["override_price"] = renamed_df["Price Per"].combine(
            merged_df["price"],
            lambda price, parent: None if price == parent else price
        )
        renamed_df["new_item_name"] = renamed_df["Name"].combine(
            merged_df["name"],
            lambda combined, parent: combined if utils.isNone(parent) else None
        )

        return renamed_df[["parent_product_id", "new_item_name", "override_price", "num_purchased"]]
