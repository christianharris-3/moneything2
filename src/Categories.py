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

    def get_category_string(self, category_id) -> str:
        if utils.isNone(category_id):
            return ""

        db_row = self.get_db_row(category_id)
        if db_row is None:
            return ""
        output = db_row["name"]
        if output is None:
            return ""
        if db_row["parent_category"] is not None:
            parent_string = self.get_category_string(
                db_row["parent_category"]
            )
            if parent_string != "":
                output += "-"+parent_string
        return output

    def get_category_id_from_string(self, category_string):
        if category_string is None or category_string == "":
            return None

        for category_id in self.db_data["category_id"]:
            if self.get_category_string(category_id) == category_string:
                return category_id

        return None

    def get_category_name(self, category_id):
        row = self.get_db_row(category_id)
        if row is not None:
            return row["name"]
        return ""

    def get_category_id_from_name(self, category_name):
        if category_name is None:
            return None
        for i,row in self.db_data.iterrows():
            if row["name"] == category_name:
                return row["category_id"]

        return None

    def list_category_strings(self):
        category_strings = set()
        for id_ in self.db_data["category_id"]:
            category_strings.add(self.get_category_string(id_))
        return sorted(list(category_strings))

    def list_category_names(self):
        return sorted(list(set(
            name for name in self.db_data["name"] if not utils.isNone(name)
        )))

    def to_display_df(self):
        df = self.db_data.rename({
            "category_id": "ID",
            "name": "Name",
            "importance": "Importance"
        }, axis=1)

        df["Parent Category"] = self.db_data["parent_category"].apply(
            self.get_category_name
        )
        print(df)
        return df[["ID", "Name", "Importance", "Parent Category"]]

    def from_display_df(self, display_df):
        renamed_df = display_df.rename({
            "ID": "category_id",
            "Name": "name",
            "Importance": "importance"
        }, axis=1)

        renamed_df["parent_category"] = display_df["Parent Category"].apply(self.get_category_id_from_name)

        return renamed_df[["category_id", "name", "importance", "parent_category"]]

