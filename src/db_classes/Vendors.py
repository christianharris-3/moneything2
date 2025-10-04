from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Vendors(DatabaseTable):
    TABLE = "Vendors"
    COLUMNS = [
        "vendor_id",
        "name",
        "default_category_id",
        "default_location_id"
    ]
    DISPLAY_DF_RENAMED = {
        "vendor_id": "ID",
        "name": "Name",
        "default_category_id": "Category ID",
        "default_location_id": "Location ID"
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

    def rename_vendors(self, db, current_id, new_name):
        if current_id is not None:
            db.update_row(
                self.TABLE,
                {"name": new_name},
                "vendor_id",
                current_id
            )