import pandas as pd
from src.DatabaseTable import DatabaseTable
import math
import src.utils as utils

class Shops(DatabaseTable):
    TABLE = "Shops"
    COLUMNS = [
        "shop_id",
        "brand",
        "location"
    ]
    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

    def get_shop_string(self, shop_id, location=True) -> str:
        if utils.isNone(shop_id):
            return ""

        shop = self.db_data[self.db_data["shop_id"] == shop_id].iloc[0]

        output = shop["brand"]
        if output is None:
            return ""

        if location and (shop["location"] is not None):
            output += " - "+shop["location"]

        return output
    
    def get_shop_id(self, shop_string):
        if shop_string is None or shop_string == "":
            return None

        for shop_id in self.db_data["shop_id"]:
            if (
                self.get_shop_string(shop_id, True) == shop_string
                or self.get_shop_string(shop_id, False) == shop_string
            ):
                return shop_id

        return None
    
    def get_all_shops(self, location=True):
        return sorted(list(set([
            self.get_shop_string(id_, location)
            for id_ in self.db_data["shop_id"]
        ])))

    def to_display_df(self):
        df = self.db_data.rename({
            "shop_id": "ID",
            "brand": "Brand",
            "location": "Location"
        }, axis=1
        )
        return df

    def from_display_df(self, display_df):
        return display_df.rename({
            "ID": "shop_id",
            "Brand": "brand",
            "Location": "location"
        }, axis=1)

