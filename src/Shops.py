import pandas as pd
from src.DatabaseTable import DatabaseTable
import math
import src.utils as utils

class Shops(DatabaseTable):
    TABLE = "Shops"
    COLUMNS = [
        "shop_id",
        "brand"
    ]
    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

    def get_all_shops(self) -> list[str]:
        return sorted(list(set([
            self.get_db_row(id_)["brand"]
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

