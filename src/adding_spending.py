import pandas as pd
import math

import streamlit as st

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
        self.category_id = None
        self.money_store_id = None

    def set_spending_time(self, spending_time):
        if spending_time is not None:
            spending_time = spending_time.strftime("%I:%M%p")
        self.spending_time = spending_time
    def set_spending_date(self, spending_date):
        if spending_date is not None:
            spending_date = utils.date_to_string(spending_date)
        self.spending_date = spending_date
    def set_shop_brand(self, shop_brand):
        self.shop_brand = shop_brand
    def set_shop_location(self, shop_location):
        self.shop_location = shop_location
    def set_spending_category(self, spending_category):
        if spending_category is None:
            self.category_id = None
        else:
            filtered_category = self.db_manager.categories.db_data[
                    self.db_manager.categories.db_data["name"] == spending_category
            ]
            if len(filtered_category) == 0:
                self.category_id = None
            else:
                self.category_id = filtered_category.iloc[0]["category_id"]
    def set_money_store_used(self, money_store):
        if money_store is None:
            self.money_store_id = None
        else:
            filtered_money_stores = self.db_manager.money_stores.db_data[
                self.db_manager.money_stores.db_data["name"] == money_store
                ]
            if len(filtered_money_stores) == 0:
                self.money_store_id = None
            else:
                self.money_store_id = filtered_money_stores.iloc[0]["money_store_id"]

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
        st.session_state["adding_spending_df"] = self.spending_df

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

        spending_event_id = self.db_manager.spending_events.generate_id()


        ## Add to shops
        if self.shop_brand is None:
            shop_id = None
        else:
            filtered_shops = self.db_manager.shops.db_data[
                self.db_manager.shops.db_data["brand"] == self.shop_brand]
            if len(filtered_shops) > 0:
                shop_id = filtered_shops.iloc[0]["shop_id"]
            else:
                shop_id = self.db_manager.shops.generate_id()
                self.db_manager.db.insert(
                    self.db_manager.shops.TABLE,
                    pd.DataFrame([{
                        "shop_id": shop_id,
                        "brand": self.shop_brand,
                    }]).iloc[0]
                )

        ## Add to shop locations
        if self.shop_location is None:
            shop_location_id = None
        else:
            filtered_locations = self.db_manager.shop_locations.db_data[
                self.db_manager.shop_locations.db_data[
                    "shop_location"] == self.shop_location]
            if len(filtered_locations) > 0:
                shop_location_id = filtered_locations.iloc[0]["shop_location_id"]
            else:
                shop_location_id = self.db_manager.shop_locations.generate_id()
                self.db_manager.db.insert(
                    self.db_manager.shop_locations.TABLE,
                    pd.DataFrame([{
                        "shop_location_id": shop_location_id,
                        "shop_id": shop_id,
                        "shop_location": self.shop_location,
                    }]).iloc[0]
                )

        ## Add to Spending Events
        self.db_manager.db.insert(
            self.db_manager.spending_events.TABLE,
            pd.DataFrame([{
                "spending_event_id": spending_event_id,
                "date": self.spending_date,
                "time": self.spending_time,
                "money_store_id": self.money_store_id,
                "shop_id": shop_id,
                "shop_location_id": shop_location_id,
                "category_id": self.category_id
            }]).iloc[0]
        )

        ## Add new Products
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
                "shop_id": shop_id,
                "category_id": category_id,
            }]).iloc[0]
            self.db_manager.products.db_data.loc[
                len(self.db_manager.products.db_data)
            ] = product_row
            self.db_manager.db.insert(
                self.db_manager.products.TABLE,
                product_row
            )

        ## Add to Spending Items
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
