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
    DISPLAY_DF_RENAMED = {
        "spending_item_id": "ID",
        "spending_event_id": "Event ID",
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
        # db_data["product_name"] = db_data.merge(
        #     products.db_data,
        #     left_on="product_id",
        #     right_on="product_id",
        #     how="left"
        # )["name"]
        db_data["display_price"] = db_data["parent_price"].combine(
            db_data["override_price"],
            lambda parent, override: parent if utils.isNone(override) else override
        )

        return utils.force_int_ids(db_data)

    # def to_display_df(self):
    #     df = self.db_data.rename({
    #         "spending_item_id": "ID",
    #         "spending_event_id": "Event ID",
    #         "product_name": "Name",
    #         "display_price": "Spent",
    #         "parent_price": "Base Price",
    #         "num_purchased": "Num Purchased"
    #     }, axis=1)
    #
    #     return df[["ID", "Event ID", "Name", "Spent", "Base Price", "Num Purchased"]]

    def from_display_df(self, display_df):
        display_df["override_price"] = display_df["Spent"].combine(
            display_df["Base Price"],
            lambda override, parent: parent if utils.isNone(override) else override
        )
        renamed_df = super().from_display_df(display_df)
        # renamed_df = display_df.rename({
        #     "ID": "spending_item_id",
        #     "Event ID": "spending_event_id",
        #     "Name": "product_name",
        #     "Spent": "display_price",
        #     "Base Price": "parent_price",
        #     "Num Purchased": "num_purchased"
        # }, axis=1)
        #
        # renamed_df["product_id"] = renamed_df.merge(
        #     products.db_data,
        #     left_on="product_name",
        #     right_on="name",
        #     how="left"
        # )["product_id"]

        return renamed_df