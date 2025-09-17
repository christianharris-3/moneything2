from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Products(DatabaseTable):
    TABLE = "Products"
    COLUMNS = [
        "product_id",
        "name",
        "price",
        "vendor_id",
        "category_id",
        "description"
    ]
    DISPLAY_DF_RENAMED = {
        "product_id": "ID",
        "name": "Name",
        "price": "Price",
        "category_string": "Category",
        "shop_name": "Shop",
        "description": "Description"
    }

    def __init__(self, select_call, vendors, categories):
        self.display_inner_joins = utils.make_display_inner_joins(
            (categories, "category_id", "category_string"),
            (vendors, "vendor_id", "name", "shop_name")
        )
        super().__init__(select_call, self.COLUMNS)

    def list_products_from_shop(self, shop_name):
        return sorted([
            self.get_product_string(row)
            for i, row in self.db_data.iterrows()
            if (row["shop_name"] == shop_name or utils.isNone(row["shop_name"])) and not utils.isNone(row["name"])
        ])

    def get_product_string(self, row):
        return f"{row['name']} - £{row['price']:.2f}"

    def get_product_id_from_product_string(self, string):
        for i, row in self.db_data.iterrows():
            if self.get_product_string(row) == string:
                return row["product_id"]
        return None

    def to_display_df(self):
        return super().to_display_df(
            self.update_foreign_data(
                utils.force_int_ids(self.db_data)
            )
        )
