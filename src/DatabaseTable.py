import math
import pandas as pd

class DatabaseTable:
    TABLE = "TABLE_NOT_ADDED"
    COLUMNS = ["COLUMNS_NOT_DEFINED"]
    def __init__(self, select_call, columns):
        data = []
        for db_row in select_call.fetchall():
            new_row = {}
            for i in range(len(columns)):
                new_row[columns[i]] = db_row[i]
            data.append(new_row)

        self.db_data = pd.DataFrame(
            data,
            columns=self.COLUMNS,
        )

    def save_changes(self, updated_df, db):
        primary_key = self.COLUMNS[0]

        for i, updated_row in updated_df.iterrows():
            if math.isnan(updated_row[primary_key]):
                self.save_row_added(updated_row, db)
            elif updated_row[primary_key] in self.db_data[primary_key].values:
                self.save_row_changes(
                    self.get_db_row(updated_row[primary_key]),
                    updated_row,
                    db
                )

        for i, original_row in self.db_data.iterrows():
            if original_row[primary_key] not in updated_df[primary_key].values:
                self.save_row_remove(original_row[primary_key], db)

    def generate_id(self) -> int:
        used_ids = set(self.db_data[self.COLUMNS[0]].values)

        return max(used_ids)+1

        # id_ = 1
        # while True:
        #     if id_ in used_ids:
        #         id_ += 1
        #     else:
        #         break
        # return id_

    def save_row_remove(self, id_, db):
        self.db_data = self.db_data.drop(
            self.db_data[self.db_data[self.COLUMNS[0]] == id_].index[0]
        )
        db.delete(self.TABLE, self.COLUMNS[0], id_)

    def save_row_added(self, updated_row, db):
        id_ = self.generate_id()
        updated_row[self.COLUMNS[0]] = id_
        self.save_row_changes(
            self.get_db_row(id_),
            updated_row,
            db
        )

    def get_db_row(self, id_):
        selected = self.db_data[self.db_data[self.COLUMNS[0]] == id_]
        if len(selected) == 0:
            return None
        return selected.iloc[0]

    def get_empty_row_data(self, id_):
        row_data = {
            column: None for column in self.COLUMNS
        }
        row_data[self.COLUMNS[0]] = id_
        return row_data

    def save_row_changes(self, original_row, updated_row, db):
        # print("2 rows ------->>>> are ","EQUAL" if DatabaseTable.row_equals(original_row, updated_row) else "NOT EQUAL")
        # print(original_row)
        # print(updated_row)
        if not DatabaseTable.row_equals(original_row, updated_row):
            db.insert(self.TABLE, updated_row)

    @staticmethod
    def row_equals(row1, row2) -> bool:
        if not isinstance(row1, pd.Series) or not isinstance(row2, pd.Series):
            return False
        if len(row1) != len(row2):
            return False

        for key in row1.keys():
            if key not in row2.keys():
                return False
            if row2[key] != row1[key]:
                if pd.isna(row2[key]) and pd.isna(row1[key]):
                    continue
                return False

        return True

    def to_display_df(self, *_):
        raise NotImplementedError()
    def from_display_df(self, *_):
        raise NotImplementedError()