from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Categories(DatabaseTable):
    TABLE = "Categories"
    COLUMNS = [
        "category_id",
        "name",
        "importance",
        "parent_category_id"
    ]
    DISPLAY_DF_RENAMED = {
        "category_id": "ID",
        "name": "Name",
        "importance": "Importance",
        "parent_name": "Parent Category"
    }

    def __init__(self, select_call):
        self.display_inner_joins = utils.make_display_inner_joins(
            (self, "parent_category_id", "name", "parent_name", "category_id")
        )
        super().__init__(select_call, self.COLUMNS)

    def update_foreign_data(self, db_data):
        db_data["category_string"] = db_data["category_id"].apply(
            self.get_category_string
        )
        return super().update_foreign_data(db_data)

    def get_category_string(self, category_id, checked_ids=None) -> str:
        if utils.isNone(category_id):
            return ""
        if checked_ids is None:
            checked_ids = {category_id}
        elif category_id in checked_ids:
            return ""
        else:
            checked_ids.add(category_id)

        db_row = self.get_db_row(category_id)
        if db_row is None:
            return ""
        output = db_row["name"]
        if output is None:
            return ""
        if db_row["parent_category_id"] is not None:
            parent_string = self.get_category_string(
                db_row["parent_category_id"],
                checked_ids
            )
            if parent_string != "":
                output += "-"+parent_string
        return output


