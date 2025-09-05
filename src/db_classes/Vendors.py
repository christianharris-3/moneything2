from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Vendors(DatabaseTable):
    TABLE = "Vendors"
    COLUMNS = [
        "vendor_id",
        "name"
    ]
    DISPLAY_DF_RENAMED = {
        "vendor_id": "ID",
        "name": "Name",
    }

    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)

    def get_all_vendors(self) -> list[str]:
        return sorted(filter(
            lambda val: not utils.isNone(val),
            set([
                self.get_db_row(id_)["name"]
                for id_ in self.db_data["vendor_id"]
            ])
        ))