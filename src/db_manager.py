from src.sql_database import SQLDatabase


class DatabaseManager:
    def __init__(self):
        self.db = SQLDatabase()
        self.db.create_tables()

        self.shops = self.db.load_shops()
        self.shop_locations = self.db.load_locations(self.shops)
        self.categories = self.db.load_categories()
        self.products = self.db.load_products(self.shops, self.categories)

    def get_products_display_df(self):
        return self.products.to_display_df(self.shops, self.categories)
    def save_products_df_changes(self, edited_df):
        self.products.save_changes(
            self.products.from_display_df(edited_df, self.shops, self.categories),
            self.db
        )
    def get_shops_display_df(self):
        return self.shops.to_display_df()
    def save_shops_df_changes(self, edited_df):
        self.shops.save_changes(
            self.shops.from_display_df(edited_df),
            self.db
        )
    def get_all_shop_brands(self) -> list[str]:
        return self.shops.get_all_shops()

    def get_categories_display_df(self):
        return self.categories.to_display_df()
    def save_categories_df_changes(self, edited_df):
        self.categories.save_changes(
            self.categories.from_display_df(edited_df),
            self.db
        )
    def get_all_category_strings(self):
        return self.categories.list_category_strings()
    def get_all_categories(self):
        return self.categories.list_category_names()

    def get_locations_display_df(self):
        return self.shop_locations.to_display_df()
    def save_locations_df_changes(self, edited_df):
        self.shop_locations.save_changes(
            self.shop_locations.from_display_df(edited_df, self.shops),
            self.db
        )

