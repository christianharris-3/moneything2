import pandas as pd
from src.DatabaseTable import DatabaseTable
import math

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
        if category_id is None or (isinstance(category_id, float) and math.isnan(category_id)):
            return ""

        output = self.db_data[category_id]["name"]
        if self.db_data[category_id]["parent_category"] is not None:
            output += "-"+self.get_category_string(
                self.db_data[category_id]["parent_category"]
            )
        return output

    def get_category_id(self, category_string):
        if category_string is None or category_string == "":
            return None

        for category_id in self.db_data["category_id"]:
            if self.get_category_string(category_id) == category_string:
                return category_id

        return None

    def dataframe(self):
        df = pd.DataFrame(
            self.db_data.values(),
        ).rename({
            "category_id": "ID",
            "name": "Name",
            "importance": "Importance"
        }, axis=1
        )#.drop("id", axis=1)

        return df

