import sqlite3 as sql
import math

class SQLDatabase:
    def __init__(self):
        self.connection = sql.connect("database.db")
        self.cursor = self.connection.cursor()

    def insert(self, table: str, data):
        """
        Inserts/Overwrites the values in a row with the given values

        :param table: the string representing the database table
        :param data: A row of a dataframe
        :return:
        """

        sql_statement = f"""
            INSERT INTO {table} ("{'", "'.join(data.keys())}")
            VALUES ({', '.join(map(self.stringify, data.values))})
            """
        set_statement = SQLDatabase.string_set(data)
        if set_statement != "":
            sql_statement += (
            f"""
            ON CONFLICT ({data.keys()[0]})
            DO UPDATE SET {SQLDatabase.string_set(data)}
            WHERE {data.keys()[0]}={data.values[0]}
            """)

        print(sql_statement)

        self.cursor.execute(
            sql_statement
        )
        self.connection.commit()

    @staticmethod
    def string_set(row):
        values = []
        for i in range(1, len(row.values)):
            if row.values[i] is not None:
                values.append(f"{row.keys()[i]}={SQLDatabase.stringify(row.values[i])}")
        return ", ".join(values)

    @staticmethod
    def stringify(var) -> str:
        if var is None or (isinstance(var, float) and math.isnan(var)):
            return "NULL"
        if isinstance(var, str):
            return f"\"{var}\""
        return str(var)

    def delete(self, table, variable, value):
        self.cursor.execute(
            f"""
            DELETE FROM {table} 
            WHERE {variable}="{value}"
            """
        )
        self.connection.commit()

    def update(self, table, id_name, id_, update_values: dict):
        self.cursor.execute(
            f"""
            UPDATE {table} 
            SET ({", ".join([f"{key}={SQLDatabase.stringify(update_values[key])}" for key in update_values])})
            WHERE {id_name}={id_}
            """
        )

    def load_table(self, obj, *args):
        return obj(
            self.execute_sql(
                f"SELECT * FROM {obj.TABLE}", False, False
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
                product_id INTEGER PRIMARY KEY,
                name TEXT,
                price DECIMAL,
                shop_id INTEGER,
                category_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Categories(
                category_id INTEGER PRIMARY KEY,
                name TEXT,
                importance DECIMAL,
                parent_category_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Shops(
                shop_id INTEGER PRIMARY KEY,
                brand TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ShopLocations(
                shop_location_id INTEGER PRIMARY KEY,
                shop_location TEXT,
                shop_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS SpendingEvents(
                spending_event_id INTEGER PRIMARY KEY,
                date TEXT,
                time TEXT,
                money_store_id INTEGER,
                shop_id INTEGER,
                shop_location_id INTEGER,
                category_id INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS SpendingItems(
                spending_item_id INTEGER PRIMARY KEY,
                spending_event_id INTEGER,
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
                money_store_id INTEGER PRIMARY KEY,
                name TEXT,
                creation_date TEXT
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS StoreSnapshots(
                snapshot_id INTEGER PRIMARY KEY,
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
                transfer_id INTEGER PRIMARY KEY,
                source_store_id INTEGER,
                target_store_id INTEGER,
                date TEXT,
                time TEXT,
                money_transferred DECIMAL
            );
            """
        )
        self.connection.commit()