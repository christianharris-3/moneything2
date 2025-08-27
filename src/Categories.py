import pandas as pd
from src.DatabaseTable import DatabaseTable
import src.utils as utils

class Categories(DatabaseTable):
    TABLE = "Categories"
    COLUMNS = [
        "category_id",
        "name",
        "importance",
        "parent_category"
    ]
    def __init__(self, select_call):
        super().__init__(select_call, self.COLUMNS)
        self.db_data = self.update_foreign_data(self.db_data)

    def update_foreign_data(self, db_data):
        db_data["category_string"] = db_data["category_id"].apply(
            self.get_category_string
        )
        db_data["parent_name"] = db_data.merge(
            db_data,
            left_on="parent_category",
            right_on="category_id",
            how="left"
        )["name_y"]
        return db_data

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
        if db_row["parent_category"] is not None:
            parent_string = self.get_category_string(
                db_row["parent_category"],
                checked_ids
            )
            if parent_string != "":
                output += "-"+parent_string
        return output

    def to_display_df(self):
        df = self.db_data.rename({
            "category_id": "ID",
            "name": "Name",
            "importance": "Importance",
            "parent_name": "Parent Category"
        }, axis=1)

        return df[["ID", "Name", "Importance", "Parent Category"]]

    def from_display_df(self, display_df):
        renamed_df = display_df.rename({
            "ID": "category_id",
            "Name": "name",
            "Importance": "importance",
            "Parent Category": "parent_name"
        }, axis=1)

        renamed_df["parent_category"] = renamed_df.merge(
            renamed_df,
            left_on="parent_name",
            right_on="name",
            how="left"
        )["category_id_y"]

        return self.update_foreign_data(
            renamed_df[["category_id", "name", "importance", "parent_category"]]
        )

