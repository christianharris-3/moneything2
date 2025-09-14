from src.DatabaseTable import DatabaseTable
import src.utils as utils


class SpendingItems(DatabaseTable):
    TABLE = "SpendingItems"
    COLUMNS = [
        "spending_item_id",
        "transaction_id",
        "product_id",
        "override_price",
        "parent_price",
        "num_purchased"
    ]
    DISPLAY_DF_RENAMED = {
        "spending_item_id": "ID",
        "transaction_id": "Transaction ID",
        "product_name": "Name",
        "display_price": "Spent",
        "parent_price": "Base Price",
        "num_purchased": "Num Purchased"
    }

    def __init__(self, select_call, products):
        self.display_inner_joins = utils.make_display_inner_joins(
            (products, "product_id", "name", "product_name")
        )
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(self.db_data)

    def update_foreign_data(self, db_data):
        db_data = super().update_foreign_data(db_data)
        db_data["display_price"] = db_data["parent_price"].combine(
            db_data["override_price"],
            lambda parent, override: parent if utils.isNone(override) else override
        )

        return utils.force_int_ids(db_data)

    def from_display_df(self, display_df):
        display_df["override_price"] = display_df["Spent"].combine(
            display_df["Base Price"],
            lambda override, parent: parent if utils.isNone(override) else override
        )
        renamed_df = super().from_display_df(display_df)

        return renamed_df