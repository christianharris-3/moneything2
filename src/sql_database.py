import sqlite3 as sql
import math
import datetime

class SQLDatabase:
    def __init__(self):
        self.user_id = 501
        self.connection = sql.connect("database.db")
        self.cursor = self.connection.cursor()

    # def insert(self, table: str, data, exists=False) -> int:
    #     """
    #     Inserts/Overwrites the values in a row with the given values
    #
    #     :param table: the string representing the database table
    #     :param data: A row of a dataframe
    #     :return:
    #     """
    #
    #     if exists is None:
    #         exists = self.get_exists(table, data)
    #
    #     if not exists:
    #         self.create_row(table, data)
    #     else:
    #         set_statement = SQLDatabase.string_set(data)
    #         sql_statement = f"""
    #             UPDATE SET {set_statement}
    #             WHERE {data.keys()[0]}={data.values[0]}
    #             """
    #
    #         self.execute_sql(
    #             f"""
    #             UPDATE MetaData
    #             SET edited_timestamp = "{datetime.datetime.now().isoformat()}"
    #             WHERE meta_data_id = (
    #                 SELECT meta_data_id FROM {table}
    #                 WHERE {data.keys()[0]}={data.values[0]}
    #             );
    #             """
    #         )
    #     if sql_statement is not None:
    #         self.execute_sql(
    #             sql_statement
    #         )
    #     return self.cursor.lastrowid

    @staticmethod
    def string_set(row):
        items = list(row.items())
        values = []
        for key, val in items:
            if val is not None:
                values.append(f"{key}={SQLDatabase.stringify(val)}")
        return ", ".join(values)

    @staticmethod
    def stringify(var) -> str:
        if var is None or (isinstance(var, float) and math.isnan(var)):
            return "NULL"
        if isinstance(var, str):
            return f"\"{var}\""
        return str(var)

    def get_exists(self, table, data):
        value = self.execute_sql(
            f"""
            SELECT * FROM {table} WHERE {data.keys()[0]}={data.values[0]}
            """,
            False, False
        )
        return len(value.fetchall())>1

    def generate_meta_data(self) -> int:
        """
        adds meta data entry to the db
        :return: new meta data id
        """
        now = datetime.datetime.now().isoformat()
        self.execute_sql(
            f"""
            INSERT INTO MetaData
            (created_timestamp, edited_timestamp, row_deleted, user_id)
            VALUES
            ("{now}", "{now}", 0, {self.user_id})
            """
        )

        return self.cursor.lastrowid


    def delete(self, table, variable, value):
        self.execute_sql(
            f"""
            UPDATE MetaData
            SET row_deleted = 1
            WHERE meta_data_id IN (
                SELECT meta_data_id FROM {table}
                WHERE {variable}="{value}"
            );
            """
        )
    def create_row(self, table: str, data: dict) -> int:
        """
        :param table: name of the table
        :param data: dictionary of data to be saved, not including primary key of table
        :return: id of table
        """
        meta_data_id = self.generate_meta_data()
        sql_statement = f"""
            INSERT INTO {table} ("{'", "'.join(data.keys())}", "meta_data_id")
            VALUES ({', '.join(map(self.stringify, data.values()))}, {meta_data_id})
            """
        self.execute_sql(sql_statement)
        return self.cursor.lastrowid

    def update_row(self, table: str, data: dict, id_name: str, id_: int):
        """

        :param table: name of the table
        :param data: dictionary of data to update, not including primary key
        :param id_name: string column name of id, e.g. "product_id"
        :param id_: the id value for this row, e.g. 5
        :return: None
        """
        set_statement = SQLDatabase.string_set(data)
        if set_statement != "":
            self.execute_sql(
                f"""
                UPDATE {table} SET {set_statement}
                WHERE {id_name}={id_}
                """
            )
            self.execute_sql(
                f"""
                UPDATE MetaData
                SET edited_timestamp = "{datetime.datetime.now().isoformat()}"
                WHERE meta_data_id = (
                    SELECT meta_data_id FROM {table} 
                    WHERE {id_name}={id_}
                );
                """
            )

    def load_table(self, obj, *args):
        return obj(
            self.execute_sql(
                f"""
                SELECT {",".join([obj.TABLE+"."+col for col in obj.COLUMNS])}
                FROM {obj.TABLE}
                JOIN MetaData ON {obj.TABLE}.meta_data_id = MetaData.meta_data_id
                WHERE MetaData.user_id = {self.user_id} AND MetaData.row_deleted = 0;
                """,
                False, False
            ),
            *args
        )

    def execute_sql(self, sql_statement, commit=True, log=True):
        if log:
            print("Executing SQL statement")
            print(sql_statement)

        return_val = self.cursor.execute(sql_statement)
        if commit:
            self.connection.commit()

        return return_val

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Products(
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                name TEXT,
                price DECIMAL,
                vendor_id INTEGER,
                category_id INTEGER,
                description TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Categories(
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                name TEXT,
                importance DECIMAL,
                parent_category_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Vendors(
                vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                name TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ShopLocations(
                shop_location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                shop_location TEXT,
                vendor_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Transactions(
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                date TEXT,
                time TEXT,
                override_money DECIMAL,
                is_income BOOLEAN,
                money_store_id INTEGER,
                vendor_id INTEGER,
                shop_location_id INTEGER,
                category_id INTEGER,
                description TEXT
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS SpendingItems(
                spending_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                transaction_id INTEGER,
                product_id INTEGER,
                override_price DECIMAL,
                parent_price DECIMAL,
                num_purchased INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS MoneyStores(
                money_store_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                name TEXT,
                creation_date TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS StoreSnapshots(
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                money_store_id INTEGER,
                snapshot_date TEXT,
                snapshot_time TEXT,
                money_stored DECIMAL
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS InternalTransfers(
                transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_data_id INTEGER,
                source_store_id INTEGER,
                target_store_id INTEGER,
                date TEXT,
                time TEXT,
                money_transferred DECIMAL
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS MetaData(
                meta_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_timestamp TEXT,
                edited_timestamp TEXT,
                row_deleted BOOLEAN,
                user_id INTEGER
            );
            """
        )
        self.connection.commit()