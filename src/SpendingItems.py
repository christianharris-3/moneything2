from src.DatabaseTable import DatabaseTable
import src.utils as utils


class SpendingItems(DatabaseTable):
    TABLE = "SpendingItems"
    COLUMNS = [
        "spending_item_id",
        "spending_event_id",
        "product_id",
        "override_price",
        "parent_price",
        "num_purchased"
    ]

    def __init__(self, select_call, products):
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(self.db_data, products)

    def update_foreign_data(self, db_data, products):
        db_data["product_name"] = db_data.merge(
            products.db_data,
            left_on="product_id",
            right_on="product_id",
            how="left"
        )["name"]
        db_data["display_price"] = db_data["parent_price"].combine(
            db_data["override_price"],
            lambda parent, override: parent if utils.isNone(override) else override
        )

        return utils.force_int_ids(db_data)

    def to_display_df(self):
        df = self.db_data.rename({
            "spending_item_id": "ID",
            "spending_event_id": "Event ID",
            "product_name": "Name",
            "display_price": "Price",
            "num_purchased": "Num Purchased"
        }, axis=1)

        return df[["ID", "Event ID", "Name", "Price", "Num Purchased"]]

    def from_display_df(self, display_df, products):
        renamed_df = display_df.rename({
            "ID": "spending_item_id",
            "Event ID": "spending_event_id",
            "Name": "product_name",
            "Price": "display_price",
            "Num Purchased": "num_purchased"
        }, axis=1)

        renamed_df["product_id"] = renamed_df.merge(
            products.db_data,
            left_on="product_name",
            right_on="name",
            how="left"
        )["product_id"]

        renamed_df["override_price"] = renamed_df["display_price"].combine(
            self.db_data["parent_price"],
            lambda override, parent: parent if utils.isNone(override) else override
        )
        renamed_df["parent_price"] = self.db_data["parent_price"]

        return self.update_foreign_data(
            renamed_df[["spending_item_id", "spending_event_id", "product_id", "override_price", "parent_price", "num_purchased"]],
            products
        )