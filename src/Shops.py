from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Shops(DatabaseTable):
    TABLE = "Shops"
    COLUMNS = [
        "shop_id",
        "brand"
    ]
    DISPLAY_DF_RENAMED = {
        "shop_id": "ID",
        "brand": "Brand",
    }

    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

    def get_all_shops(self) -> list[str]:
        return sorted(filter(
            lambda val: not utils.isNone(val),
            set([
                self.get_db_row(id_)["brand"]
                for id_ in self.db_data["shop_id"]
            ])
        ))