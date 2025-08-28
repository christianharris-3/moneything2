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
        if spending_time is not None:
            spending_time = spending_time.strftime("%I:%M%p")
        self.spending_time = spending_time
    def set_spending_date(self, spending_date):
        if spending_date is not None:
            spending_date = spending_date.strftime("%a %d %b %Y")
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

    def add_spending_to_db(self):
        print("STORING")
        print(self.spending_df)

        spending_event_id = self.db_manager.spending_events.generate_id()
        shop_id = self.db_manager.shops.db_data[
            self.db_manager.shops.db_data["brand"] == self.shop_brand
        ].iloc[0]["shop_id"] if not utils.isNone(self.shop_brand) else None

        shop_location_id = self.db_manager.shop_locations.db_data[
            self.db_manager.shop_locations.db_data[
                "shop_location"] == self.shop_location
        ].iloc[0]["shop_location_id"] if not utils.isNone(self.shop_location) else None

        self.db_manager.db.insert(
            self.db_manager.spending_events.TABLE,
            pd.DataFrame(
                [{
                    "spending_event_id": spending_event_id,
                    "date": self.spending_date,
                    "time": self.spending_time,
                    "shop_id": shop_id,
                    "shop_location_id": shop_location_id,
                }]
            ).iloc[0]
        )

        new_products =  self.spending_df[
            self.spending_df["new_item_name"].apply(
                lambda var: not utils.isNone(var)
            )
        ]

        for i, row in new_products.iterrows():
            product_id = self.db_manager.products.generate_id()
            self.spending_df.loc[i, "parent_product_id"] = product_id
            product_row = pd.DataFrame([{
                "product_id": product_id,
                "name": row["new_item_name"],
                "price": row["override_price"],
                "shop_id": shop_id
            }]).iloc[0]
            self.db_manager.products.db_data.loc[
                len(self.db_manager.products.db_data)
            ] = product_row
            self.db_manager.db.insert(
                self.db_manager.products.TABLE,
                product_row
            )


        num_items = len(self.spending_df)
        spending_items_df = self.spending_df[["override_price", "num_purchased"]].copy()
        spending_items_df["product_id"] = self.spending_df["parent_product_id"]
        spending_items_df["spending_event_id"] = spending_event_id
        spending_items_df["parent_price"] = self.spending_df.merge(
            self.db_manager.products.db_data,
            left_on="parent_product_id",
            right_on="product_id",
            how="left"
        )["price"]
        spending_items_df["spending_item_id"] = [
            self.db_manager.spending_items.generate_id()
            for i in range(num_items)
        ]

        for i, row in spending_items_df[["spending_item_id"]+list(spending_items_df.columns)[:-1]].iterrows():
            self.db_manager.db.insert(
                self.db_manager.spending_items.TABLE,
                row
            )
