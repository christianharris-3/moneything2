from src.sql_database import SQLDatabase

from src.db_classes.Categories import Categories
from src.db_classes.Products import Products
from src.db_classes.Vendors import Vendors
from src.db_classes.ShopLocations import ShopLocations
from src.db_classes.SpendingItems import SpendingItems
from src.db_classes.Transactions import Transactions
from src.db_classes.MoneyStores import MoneyStores
from src.db_classes.StoreSnapshots import StoreSnapshots
from src.db_classes.InternalTransfers import InternalTransfers


class DatabaseManager:
    def __init__(self):
        self.db = SQLDatabase()
        self.db.create_tables()


        self.money_stores = self.db.load_table(MoneyStores)
        self.store_snapshots = self.db.load_table(StoreSnapshots, self.money_stores)
        self.internal_transfers = self.db.load_table(InternalTransfers, self.money_stores)
        self.vendors = self.db.load_table(Vendors)
        self.shop_locations = self.db.load_table(ShopLocations, self.vendors)
        self.categories = self.db.load_table(Categories)
        self.products = self.db.load_table(Products, self.vendors, self.categories)
        self.transactions = self.db.load_table(Transactions,
            self.money_stores, self.vendors, self.shop_locations, self.categories)
        self.spending_items = self.db.load_table(SpendingItems, self.products)

    def reconnect_db(self):
        self.db = SQLDatabase()

    def save_df_changes(self, obj, edited_df) -> bool:
        return obj.save_changes(
            obj.from_display_df(edited_df),
            self.db
        )

    def get_products_display_df(self):
        return self.products.to_display_df()
    def save_products_df_changes(self, edited_df):
        return self.save_df_changes(self.products, edited_df)
    def get_all_products(self, shop):
        return self.products.list_products_from_shop(shop)

    def get_vendors_display_df(self):
        return self.vendors.to_display_df()
    def save_vendors_df_changes(self, edited_df):
        return self.save_df_changes(self.vendors, edited_df)
    def get_all_vendor_names(self) -> list[str]:
        return self.vendors.get_all_vendors()

    def get_categories_display_df(self):
        return self.categories.to_display_df()
    def save_categories_df_changes(self, edited_df):
        return self.save_df_changes(self.categories, edited_df)
    def get_all_category_strings(self):
        return self.categories.list_all_in_column("category_string")
    def get_all_categories(self):
        return self.categories.list_all_in_column("name")

    def get_locations_display_df(self):
        return self.shop_locations.to_display_df()
    def save_locations_df_changes(self, edited_df):
        return self.save_df_changes(self.shop_locations, edited_df)
    def get_shop_locations(self, shop_name):
        return self.shop_locations.get_shop_locations(shop_name)

    def get_transactions_display_df(self):
        return self.transactions.to_display_df()
    def save_transactions_df_changes(self, edited_df):
        return self.save_df_changes(self.transactions, edited_df)

    def get_spending_items_display_df(self):
        return self.spending_items.to_display_df()
    def save_spending_items_df_changes(self, edited_df):
        return self.save_df_changes(self.spending_items, edited_df)

    def get_money_stores_display_df(self):
        return self.money_stores.to_display_df()
    def save_money_stores_df_changes(self, edited_df):
        return self.save_df_changes(self.money_stores, edited_df)
    def get_all_money_stores(self):
        return self.money_stores.list_all_in_column("name")

    def get_store_snapshots_display_df(self):
        return self.store_snapshots.to_display_df()
    def save_store_snapshots_df_changes(self, edited_df):
        return self.save_df_changes(self.store_snapshots, edited_df)

    def get_internal_transfers_display_df(self):
        return self.internal_transfers.to_display_df()
    def save_internal_transfers_df_changes(self, edited_df):
        return self.save_df_changes(self.internal_transfers, edited_df)

