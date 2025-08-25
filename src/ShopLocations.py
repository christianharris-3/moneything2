from src.DatabaseTable import DatabaseTable
import src.utils as utils

class ShopLocations(DatabaseTable):
    TABLE = "ShopLocations"
    COLUMNS = [
        "shop_location_id",
        "shop_location",
        "shop_id"
    ]
    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

