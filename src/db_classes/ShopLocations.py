from src.DatabaseTable import DatabaseTable
import src.utils as utils

class ShopLocations(DatabaseTable):
    TABLE = "ShopLocations"
    COLUMNS = [
        "shop_location_id",
        "shop_location",
        "shop_id"
    ]
    DISPLAY_DF_RENAMED = {
            "shop_location_id": "ID",
            "shop_location": "Location",
            "brand": "Brand"
        }

    def __init__(self, select_call, shops):
        self.display_inner_joins = utils.make_display_inner_joins(
            (shops, "shop_id", "brand")
        )
        super().__init__(select_call, self.COLUMNS)

    def get_shop_locations(self, shop_brand):
        if shop_brand is None:
            filtered = self.db_data
        else:
            filtered = self.db_data[self.db_data["brand"] == shop_brand]

        return sorted(set(
            filtered["shop_location"]
        ))

