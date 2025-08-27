from src.sql_database import SQLDatabase


class DatabaseManager:
    def __init__(self):
        self.db = SQLDatabase()
        self.db.create_tables()

        self.shops = self.db.load_shops()
        self.shop_locations = self.db.load_locations(self.shops)
        self.categories = self.db.load_categories()
        self.products = self.db.load_products(self.shops, self.categories)
        self.spending_events = self.db.load_spending_events(self.shops, self.shop_locations)
        self.spending_items = self.db.load_spending_items(self.products)

    def get_products_display_df(self):
        return self.products.to_display_df(self.shops, self.categories)
    def save_products_df_changes(self, edited_df):
        self.products.save_changes(
            self.products.from_display_df(edited_df, self.shops, self.categories),
            self.db
        )
    def get_all_products(self, shop):
        return self.products.list_products_from_shop(shop)

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
        return self.categories.list_all_in_column("category_string")
    def get_all_categories(self):
        return self.categories.list_all_in_column("name")

    def get_locations_display_df(self):
        return self.shop_locations.to_display_df()
    def save_locations_df_changes(self, edited_df):
        self.shop_locations.save_changes(
            self.shop_locations.from_display_df(edited_df, self.shops),
            self.db
        )
    def get_shop_locations(self, shop_brand):
        return self.shop_locations.get_shop_locations(shop_brand)

    def get_spending_events_display_df(self):
        return self.spending_events.to_display_df()
    def save_spending_events_df_changes(self, edited_df):
        self.spending_events.save_changes(
            self.spending_events.from_display_df(edited_df, self.shops, self.shop_locations),
            self.db
        )

    def get_spending_items_display_df(self):
        return self.spending_items.to_display_df()
    def save_spending_items_df_changes(self, edited_df):
        self.spending_items.save_changes(
            self.spending_items.from_display_df(edited_df, self.products),
            self.db
        )

