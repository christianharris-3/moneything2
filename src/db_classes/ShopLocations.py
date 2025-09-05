from src.DatabaseTable import DatabaseTable
import src.utils as utils

class ShopLocations(DatabaseTable):
    TABLE = "ShopLocations"
    COLUMNS = [
        "shop_location_id",
        "shop_location",
        "vendor_id"
    ]
    DISPLAY_DF_RENAMED = {
            "shop_location_id": "ID",
            "shop_location": "Location",
            "name": "Brand"
        }

    def __init__(self, select_call, vendors):
        self.display_inner_joins = utils.make_display_inner_joins(
            (vendors, "vendor_id", "name")
        )
        super().__init__(select_call, self.COLUMNS)

    def get_shop_locations(self, shop_name):
        if shop_name is None:
            filtered = self.db_data
        else:
            filtered = self.db_data[self.db_data["name"] == shop_name]

        return sorted(set(
            filtered["shop_location"]
        ))

