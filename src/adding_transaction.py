import pandas as pd
import math
from src.logger import log
import streamlit as st

import src.utils as utils

class AddingTransaction:
    def __init__(self, db_manager):
        if not "adding_spending_df" in st.session_state:
            st.session_state["adding_spending_df"] = pd.DataFrame(
                columns=[
                    "temp_item_id",
                    "parent_product_id",
                    "spending_item_id",
                    "new_item_name",
                    "override_price",
                    "num_purchased"
                ]
            )
        if not "adding_spending_display_df" in st.session_state:
            st.session_state["adding_spending_display_df"] = None

        self.spending_df = st.session_state["adding_spending_df"]
        self.display_df = st.session_state["adding_spending_display_df"]
        self.db_manager = db_manager

        self.spending_time = None
        self.spending_date = None
        self.vendor_name = None
        self.shop_location = None
        self.category_id = None
        self.money_store_id = None
        self.override_money = None
        self.is_income = False
        self.description = None

    def set_spending_time(self, spending_time):
        if spending_time is not None:
            spending_time = spending_time.strftime("%I:%M%p")
        self.spending_time = spending_time
    def set_spending_date(self, spending_date):
        if spending_date is not None:
            spending_date = utils.date_to_string(spending_date)
        self.spending_date = spending_date
    def set_vendor_name(self, vendor_name):
        self.vendor_name = vendor_name
    def set_shop_location(self, shop_location):
        self.shop_location = shop_location
    def set_override_money(self, override_money):
        self.override_money = override_money
    def set_is_income(self, is_income):
        if isinstance(is_income, str):
            self.is_income = (is_income == "Income")
        else:
            self.is_income = is_income
    def set_description(self, description):
        self.description = description
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

    def add_product(self, product_string, override_price=None):
        product_id = self.db_manager.products.get_product_id_from_product_string(product_string)
        if product_id is None:
            self.spending_df.loc[len(self.spending_df)] = {
                "temp_item_id": self.generate_temp_item_id(),
                "parent_product_id": math.nan,
                "spending_item_id": math.nan,
                "new_item_name": product_string,
                "override_price": override_price,
                "num_purchased": 1
            }
        else:
            self.spending_df.loc[len(self.spending_df)] = {
                "temp_item_id": self.generate_temp_item_id(),
                "parent_product_id": product_id,
                "spending_item_id": math.nan,
                "new_item_name": None,
                "override_price": override_price,
                "num_purchased": 1
            }
        st.session_state["adding_spending_df"] = self.spending_df

    def generate_temp_item_id(self):
        if len(self.spending_df)>0:
            return max(self.spending_df["temp_item_id"])+1
        return 0

    def refresh_display_df(self):
        df = st.session_state["adding_spending_df"].merge(
            self.db_manager.products.db_data,
            left_on="parent_product_id",
            right_on="product_id",
            how="left",
        ).rename({
            "temp_item_id": "ID",
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
        self.display_df = df[["ID", "Name", "Price Per", "Num Purchased"]]
        st.session_state["adding_spending_display_df"] = self.display_df

    def to_display_df(self):
        if self.display_df is None:
            self.refresh_display_df()
        return self.display_df

    def from_display_df(self, edited_df):
        renamed_df = edited_df.rename({
            "ID": "temp_item_id",
            "Num Purchased": "num_purchased"
        }, axis=1).reset_index()
        renamed_df = utils.force_int_ids(renamed_df)
        renamed_df[["spending_item_id", "parent_product_id"]] = renamed_df.merge(
            self.spending_df,
            left_on="temp_item_id",
            right_on="temp_item_id",
            how="left"
        )[["spending_item_id", "parent_product_id"]]


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
        return renamed_df[["temp_item_id", "parent_product_id", "spending_item_id", "new_item_name", "override_price", "num_purchased"]]

    def add_transaction_to_db(self):
        log("Saving transaction, with item df ->")
        log(self.spending_df)
        ## Add to vendors
        if self.vendor_name is None:
            vendor_id = None
        else:
            filtered_vendors = self.db_manager.vendors.db_data[
                self.db_manager.vendors.db_data["name"] == self.vendor_name]
            if len(filtered_vendors) > 0:
                vendor_id = filtered_vendors.iloc[0]["vendor_id"]
            else:
                vendor_id = self.db_manager.db.create_row(
                    self.db_manager.vendors.TABLE,
                    {
                        "name": self.vendor_name,
                    }
                )
                self.db_manager.vendors.db_data.loc[
                    len(self.db_manager.vendors.db_data)] = {
                    "vendor_id": vendor_id,
                    "name": self.vendor_name
                }

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
                shop_location_id = self.db_manager.db.create_row(
                    self.db_manager.shop_locations.TABLE,
                    {
                        "vendor_id": vendor_id,
                        "shop_location": self.shop_location,
                    }
                )
                self.db_manager.shop_locations.db_data.loc[
                    len(self.db_manager.shop_locations.db_data)] = {
                    "shop_location_id": shop_location_id,
                    "vendor_id": vendor_id,
                    "shop_location": self.shop_location,
                }

        ## Add to Transactions
        transaction_data = {
            "date": self.spending_date,
            "time": self.spending_time,
            "override_money": self.override_money,
            "is_income": self.is_income,
            "money_store_id": self.money_store_id,
            "vendor_id": vendor_id,
            "shop_location_id": shop_location_id,
            "category_id": self.category_id,
            "description": self.description
        }
        transaction_id = st.session_state.get("editing_transaction_id", -1)
        if transaction_id == -1:
            transaction_id = self.db_manager.db.create_row(
                self.db_manager.transactions.TABLE,
                transaction_data
            )
        else:
            differences = utils.get_row_differences(
                self.db_manager.transactions.get_db_row(transaction_id),
                transaction_data
            )
            self.db_manager.db.update_row(
                self.db_manager.transactions.TABLE,
                differences,
                "transaction_id",
                transaction_id
            )

        ## Add new Products
        new_products_df =  self.spending_df[
            self.spending_df["new_item_name"].apply(
                lambda var: not utils.isNone(var)
            )
        ]

        for i, row in new_products_df.iterrows():
            product_data = {
                "name": row["new_item_name"],
                "price": row["override_price"],
                "vendor_id": vendor_id,
                "category_id": self.category_id,
            }
            product_id = self.db_manager.db.create_row(
                self.db_manager.products.TABLE,
                product_data
            )
            self.spending_df.loc[i, "parent_product_id"] = product_id
            product_data["product_id"] = product_id
            self.db_manager.products.db_data.loc[
                len(self.db_manager.products.db_data)
            ] = product_data


        ## Add to Spending Items
        spending_items_df = self.spending_df[["override_price", "num_purchased", "spending_item_id"]].copy()
        spending_items_df["product_id"] = self.spending_df["parent_product_id"]
        spending_items_df["transaction_id"] = transaction_id
        spending_items_df["parent_price"] = self.spending_df.merge(
            self.db_manager.products.db_data,
            left_on="parent_product_id",
            right_on="product_id",
            how="left"
        )["price"]

        # delete items
        current_db_data = self.db_manager.spending_items.get_filtered_df("transaction_id", transaction_id)
        removed_ids = set(current_db_data["spending_item_id"])-set(spending_items_df["spending_item_id"])
        for to_remove_id in removed_ids:
            self.db_manager.db.delete(
                self.db_manager.spending_items.TABLE,
                "spending_item_id",
                to_remove_id
            )

        ## add/update items
        for i, row in spending_items_df.iterrows():
            if utils.isNone(row["spending_item_id"]):
                new_row = dict(row)
                new_row.pop("spending_item_id", None)
                self.db_manager.db.create_row(
                    self.db_manager.spending_items.TABLE,
                    new_row
                )
            else:
                original_row = self.db_manager.spending_items.get_db_row(row["spending_item_id"])
                differences = utils.get_row_differences(original_row, row)

                self.db_manager.db.update_row(
                    self.db_manager.spending_items.TABLE,
                    differences,
                    "spending_item_id",
                    row["spending_item_id"]
                )

        return transaction_id
