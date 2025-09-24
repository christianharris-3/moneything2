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
                if int(word["top"]) < current_y_pos-5 or int(word["top"]) > current_y_pos+5:
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

    return pd.DataFrame(df_data, columns = [col[0] for col in columns])

def extract_hsbc_statement(pages: list[list[list[dict]]]):
    transaction_rows = []
    initial_balance_text = None
    for page in pages:
        at_transactions = False
        for line in page:
            text = " ".join([word["text"] for word in line])

            if "BALANCECARRIEDFORWARD" in text:
                at_transactions = False
            if at_transactions:
                transaction_rows.append(line)
            if "BALANCEBROUGHTFORWARD" in text:
                at_transactions = True
                if initial_balance_text is None:
                    initial_balance_text = text

    table_df = extract_table(
        transaction_rows,
        [
            ("date", 0),
            ("type", 110),
            ("name", 135),
            ("paid_out", 350),
            ("paid_in", 440),
            ("balance", 510)
        ]
    )
    combined_df = pd.DataFrame(columns=list(table_df.columns)+["description", "money", "is_income"])
    for i, row in table_df.iterrows():
        if row["type"] != "":
            combined_df.loc[len(combined_df)] = row.copy()
        else:
            try:
                combined_df.loc[len(combined_df)-1, "description"] += " "+row["name"]
            except (KeyError, TypeError):
                combined_df.loc[len(combined_df) - 1, "description"] = row["name"]
            combined_df.loc[len(combined_df)-1,
                ["paid_out", "paid_in", "balance"]
            ] = row[
                ["paid_out", "paid_in", "balance"]
            ]


    combined_df["date"] = combined_df["date"].replace("", np.nan).ffill()
    combined_df["date"] = combined_df["date"].apply(utils.string_to_date)

    for i, row in combined_df.iterrows():
        if row["paid_in"] != "":
            combined_df.loc[i, "money"] = float(str(row["paid_in"]).replace(",", ""))
            combined_df.loc[i, "is_income"] = True
        elif row["paid_out"] != "":
            combined_df.loc[i, "money"] = float(str(row["paid_out"]).replace(",", ""))
            combined_df.loc[i, "is_income"] = False

    transaction_df = combined_df.rename({
        "name": "vendor",
    })[["date", "name", "description", "money", "is_income"]]

    snapshot_info = None
    if initial_balance_text is not None:
        split_text = initial_balance_text.split()
        try:
            date_str = split_text[0]+" "+split_text[1]+" "+split_text[2]
            balance_str = split_text[-1]
            snapshot_info = {
                "date": utils.string_to_date(date_str),
                "balance": float(balance_str.replace(",", ""))
            }
        except:
            pass

    return transaction_df, snapshot_info

def store_transactions_df(transactions_df, snapshot_info, db_manager=None, money_store=None):
    if db_manager is None:
        db_manager = DatabaseManager()
    for i, row in transactions_df.iterrows():
        adding = AddingTransaction({}, db_manager)
        adding.set_spending_date(row["date"])
        adding.set_vendor_name(row["name"])
        adding.set_description(row["description"])
        adding.set_override_money(row["money"])
        adding.set_is_income(row["is_income"])
        adding.set_money_store_used(money_store)

        same_transactions = db_manager.transactions.get_filtered_df(
            ["date", "vendor_name", "description", "override_money", "is_income"],
            [
                utils.date_to_string(row["date"]),
                row["name"],
                row["description"],
                row["money"],
                row["is_income"]
            ]
        )
        if len(same_transactions) == 0:
            adding.add_transaction_to_db()

    if snapshot_info is not None:
        adding = AddingTransaction({}, db_manager)
        adding.set_money_store_used(money_store)
        db_manager.db.create_row(
            db_manager.store_snapshots.TABLE,
            {
                "money_store_id": adding.money_store_id,
                "snapshot_date": utils.date_to_string(snapshot_info["date"]),
                "money_stored": snapshot_info["balance"]
            }
        )

def upload_pdf(file, db_manager, money_store=None):
    statement_pages = extract_pdf_text(file)
    transactions_df, initial_balance = extract_hsbc_statement(statement_pages)

    store_transactions_df(transactions_df, initial_balance, db_manager, money_store)



if __name__ == "__main__":
    test_path = "C:\\Users\\chris\\Downloads\\2025-06-20_Statement.pdf"
    test_path = "C:\\Users\\chris\\my stuff\\bank statements\\2025-07-20_Statement.pdf"
    pdf_pages = extract_pdf_text(test_path)
    df, initial_balance = extract_hsbc_statement(pdf_pages)

    store_transactions_df(df)