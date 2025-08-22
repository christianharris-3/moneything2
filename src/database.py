import sqlite3 as sql
from src.Categories import Categories
from src.Products import Products
from src.Shops import Shops
import math

class Database:
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

        print(f"""
            INSERT INTO {table} ("{'", "'.join(data.keys())}")
            VALUES ({', '.join(map(self.stringify, data.values))})
            ON CONFLICT ({data.keys()[0]})
            DO UPDATE SET {Database.string_set(data)}
            WHERE {data.keys()[0]}={data.values[0]}
            """)

        self.cursor.execute(
            f"""
            INSERT INTO {table} ("{'", "'.join(data.keys())}")
            VALUES ({', '.join(map(self.stringify, data.values))})
            ON CONFLICT ({data.keys()[0]})
            DO UPDATE SET {Database.string_set(data)}
            WHERE {data.keys()[0]}={data.values[0]}
            """
        )
        self.connection.commit()

    @staticmethod
    def string_set(row):
        values = []
        for i in range(1, len(row.values)):
            if row.values[i] is not None:
                values.append(f"{row.keys()[i]}={Database.stringify(row.values[i])}")
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
            SET ({", ".join([f"{key}={Database.stringify(update_values[key])}" for key in update_values])})
            WHERE {id_name}={id_}
            """
        )

    def load_products(self):
        products = self.cursor.execute(
            """
            SELECT * FROM Products
            """
        )
        return Products(
            products,
        )

    def load_shops(self):
        shops = self.cursor.execute(
            """
            SELECT * FROM Shops
            """
        )
        return Shops(shops)

    def load_categories(self):
        categories = self.cursor.execute(
            "SELECT * FROM Categories"
        )
        return Categories(categories)


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
                parent_category INTEGER
            );
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Shops(
                shop_id INTEGER PRIMARY KEY,
                brand TEXT,
                location TEXT
            );
            """
        )

        # self.cursor.execute(
        #     """
        #     INSERT INTO Products (name, price, shop_id)
        #                 VALUES ("Apples", 1.29, 1)
        #     """
        # )
        # self.cursor.execute(
        #     """
        #     INSERT INTO Shops (brand, location)
        #                 VALUES ("Lidl", "Oxford Road")
        #     """
        # )
        # self.connection.commit()