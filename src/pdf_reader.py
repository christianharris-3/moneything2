import pdfplumber
import pandas as pd
import numpy as np
import src.utils as utils
from src.db_manager import DatabaseManager
from src.adding_transaction import AddingTransaction
pd.set_option('display.max_columns', None)

def extract_pdf_text(path) -> list[list[list[dict]]]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            word_dict = page.extract_words()
            page_info = []
            current_y_pos = -1
            for word in word_dict:
                if int(word["top"]) != current_y_pos:
                    page_info.append([])
                    current_y_pos = int(word["top"])
                page_info[-1].append({
                    "text": word["text"],
                    "x_pos": int(word["x0"])
                })
            pages.append(page_info)

    return pages

def extract_table(data: list[list[dict]], columns: list[tuple[str, int]]) -> pd.DataFrame:
    """

    :param data:
    :param columns: list of column info, each item is [column title, x pos of far left of column]
    :return: dataframe storing the table
    """
    df_data = []
    for line in data:
        new_row = {column: [] for column, cutoff in columns}
        for word in line:
            column_index = len(columns)-1
            while word["x_pos"] < columns[column_index][1] and column_index>0:
                column_index-=1
            new_row[columns[column_index][0]].append(word["text"])
        df_data.append({
            column: " ".join(words)
            for column, words in new_row.items()
        })

    return pd.DataFrame(df_data)

def extract_hsbc_statement(pages: list[list[list[dict]]]):
    transaction_rows = []
    for page in pages:
        # print(" ------------------ NEW PAGE")
        at_transactions = False
        for line in page:
            text = " ".join([word["text"] for word in line])

            if "BALANCECARRIEDFORWARD" in text:
                at_transactions = False
            if at_transactions:
                transaction_rows.append(line)
                # print(text, line)
            if "BALANCEBROUGHTFORWARD" in text:
                at_transactions = True

    table_df = extract_table(
        transaction_rows,
        [
            ("date", 0),
            ("idk", 110),
            ("name", 135),
            ("paid_out", 350),
            ("paid_in", 440),
            ("balance", 510)
        ]
    )
    table_df = table_df[table_df["name"] != "INTERNET TRANSFER"].reset_index(drop=True)
    top_rows = table_df.iloc[::2].reset_index(drop=True)
    bottom_rows = table_df.iloc[1::2].reset_index(drop=True)
    top_rows["description"] = bottom_rows["name"]
    top_rows[["paid_out", "paid_in", "balance"]] = bottom_rows[
        ["paid_out", "paid_in", "balance"]
    ]
    top_rows["date"] = top_rows["date"].replace("", np.nan).ffill()
    top_rows["date"] = top_rows["date"].apply(utils.string_to_date)

    for i, row in top_rows.iterrows():
        if row["paid_out"] == "":
            top_rows.loc[i, "money"] = float(row["paid_in"])
            top_rows.loc[i, "is_income"] = True
        else:
            top_rows.loc[i, "money"] = float(row["paid_out"])
            top_rows.loc[i, "is_income"] = False

    transaction_df = top_rows.rename({
        "name": "vendor",
    })[["date", "name", "description", "money", "is_income"]]

    return transaction_df

def store_transactions_df(transactions_df, money_store=None):
    db_manager = DatabaseManager()
    for i, row in transactions_df.iterrows():
        adding = AddingTransaction({}, db_manager)
        adding.set_spending_date(row["date"])
        adding.set_vendor_name(row["name"])
        adding.set_description(row["description"])
        adding.set_override_money(row["money"])
        adding.set_is_income(row["is_income"])
        adding.set_money_store_used(money_store)
        adding.add_transaction_to_db()


if __name__ == "__main__":
    test_path = "C:\\Users\\chris\\Downloads\\2025-06-20_Statement.pdf"
    pdf_pages = extract_pdf_text(test_path)
    df = extract_hsbc_statement(pdf_pages)
    store_transactions_df(df)