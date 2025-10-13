import pandas as pd
import src.utils as utils
from src.logger import log

class DatabaseTable:
    TABLE = "TABLE_NOT_ADDED"
    COLUMNS = ["COLUMNS_NOT_DEFINED"]
    DISPLAY_DF_RENAMED = {"RENAME_MAPPER_NOT_DEFINED":"FIX_THIS"}
    DISPLAY_DF_COLUMNS = None
    display_inner_joins = []

    def __init__(self, select_call, columns):
        data = []
        for db_row in select_call.fetchall():
            new_row = {}
            for i in range(len(columns)):
                new_row[columns[i]] = db_row[i]
            data.append(new_row)

        self.db_data = utils.force_int_ids(
            pd.DataFrame(
                data,
                columns=self.COLUMNS,
            )
        )
        self.INVERSE_DISPLAY_DF_RENAMED = {
            val: key
            for key, val in self.DISPLAY_DF_RENAMED.items()
        }
        if self.DISPLAY_DF_COLUMNS is None:
            self.DISPLAY_DF_COLUMNS = list(
                self.DISPLAY_DF_RENAMED.values()
            )

        self.created_ids = set()
        self.db_data = self.update_foreign_data(self.db_data)

    def save_changes(self, updated_df, db):
        updated_df = updated_df[self.COLUMNS]
        primary_key = self.COLUMNS[0]
        table_edited = False

        for i, updated_row in updated_df.iterrows():
            if utils.isNone(updated_row[primary_key]):
                self.save_row_added(updated_row, db)
                table_edited = True
            elif updated_row[primary_key] in self.db_data[self.COLUMNS][primary_key].values:
                table_edited = self.save_row_changes(
                    self.get_db_row(updated_row[primary_key])[self.COLUMNS],
                    updated_row,
                    db
                ) or table_edited

        for i, original_row in self.db_data[self.COLUMNS].iterrows():
            if original_row[primary_key] not in updated_df[primary_key].values:
                self.save_row_remove(original_row[primary_key], db)
                table_edited = True

        return table_edited

    def save_row_remove(self, id_, db):
        removed_rows = self.db_data[self.db_data[self.COLUMNS[0]] == id_]
        if len(removed_rows) > 0:
            log(f"Deleting row from {self.TABLE}: {dict(removed_rows.iloc[0])}")
        self.db_data = self.db_data.drop(
            removed_rows.index[0]
        )
        db.delete(self.TABLE, self.COLUMNS[0], id_)

    def save_row_added(self, updated_row, db):
        row_data = dict(updated_row)
        row_data.pop(self.COLUMNS[0], None)
        log(f"Storing data to {self.TABLE}: {row_data}")
        db.create_row(
            self.TABLE,
            row_data
        )

    def get_db_row(self, id_):
        selected = self.db_data[self.db_data[self.COLUMNS[0]] == id_]
        if len(selected) == 0:
            return None
        return selected.iloc[0]

    def get_id_from_value(self, column, value):
        filtered = self.get_filtered_df(column, value)
        if len(filtered) < 1:
            return None
        else:
            return filtered.iloc[0][self.COLUMNS[0]]

    def get_filtered_df(self, column, value):
        return utils.filter_df(self.db_data, column, value)

    def save_row_changes(self, original_row, updated_row, db) -> bool:
        if not DatabaseTable.row_equals(original_row, updated_row):
            log(f"Updating Row on {self.TABLE} = {dict(original_row)} -> {dict(updated_row)}")
            db.update_row(
                self.TABLE,
                utils.get_row_differences(original_row, updated_row),
                self.COLUMNS[0],
                updated_row[self.COLUMNS[0]]
            )
            return True
        return False

    def list_all_in_column(self, column):
        return sorted(filter(
            lambda name: not utils.isNone(name),
            set(self.db_data[column])
        ))


    @staticmethod
    def df_equals(df1, df2) -> bool:
        if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
            return False
        if len(df1) != len(df2):
            return False
        for i, row in df1.iterrows():
            if not DatabaseTable.row_equals(row, df2.iloc[i]):
                return False
        return True

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

    def update_foreign_data(self, db_data):
        db_data = db_data.copy()

        for inner_join in self.display_inner_joins:
            merged_df = db_data.merge(
                inner_join["object"].db_data.drop_duplicates(
                    subset=[inner_join["right_on"]]
                ),
                left_on=inner_join["left_on"],
                right_on=inner_join["right_on"],
                how="left"
            )

            if inner_join["source_column"] in merged_df.columns:
                db_data[inner_join["new_column"]] = merged_df[
                    inner_join["source_column"]
                ]
            else:
                db_data[inner_join["new_column"]] = merged_df[
                    inner_join["source_column"]+"_y"
                ]

        return utils.force_int_ids(db_data)

    def to_display_df(self, db_data=None):
        if db_data is None:
            db_data = self.db_data
        df = db_data.rename(
            self.DISPLAY_DF_RENAMED,
            axis=1
        )
        return df[self.DISPLAY_DF_COLUMNS]
    def from_display_df(self, display_df):
        renamed_df = display_df.rename(
            self.INVERSE_DISPLAY_DF_RENAMED,
            axis=1
        ).reset_index(drop=True)

        for inner_join in self.display_inner_joins:
            merged_df = renamed_df.merge(
                inner_join["object"].db_data.drop_duplicates(
                    subset=[inner_join["source_column"]]
                ),
                left_on=inner_join["new_column"],
                right_on=inner_join["source_column"],
                how="left"
            )

            if inner_join["right_on"] in merged_df.columns:
                renamed_df[inner_join["left_on"]] = merged_df[
                    inner_join["right_on"]
                ]
            else:
                renamed_df[inner_join["left_on"]] = merged_df[
                    inner_join["right_on"]+"_y"
                ]

        return self.update_foreign_data(
            renamed_df[self.COLUMNS],
        )