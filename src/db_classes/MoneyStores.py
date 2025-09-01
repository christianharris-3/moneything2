from src.DatabaseTable import DatabaseTable
import src.utils as utils

class MoneyStores(DatabaseTable):
    TABLE = "MoneyStores"
    COLUMNS = [
        "money_store_id",
        "name",
        "creation_date"
    ]
    DISPLAY_DF_RENAMED = {
        "money_store_id": "ID",
        "name": "Name",
        "creation_date": "Creation Date"
    }

    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)