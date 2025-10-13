from PIL import Image
import pytesseract
import re
import sys
from src.logger import log
import pandas as pd
import src.utils as utils
import streamlit as st
from src.adding_transaction import AddingTransaction

def init_pytesseract():
    if sys.platform == "win32":
        path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        log(f"Set Python to pytesseract to: {path}")
        pytesseract.pytesseract.tesseract_cmd = path


def extract_from_lidl_receipt(image_text):
    text = image_text.split("£100 of Lidl Vouchers.", 1)[1]
    text = text.split("*CUSTOMER COPY*", 1)[0]
    log("Processing Receipt Text As ->")
    log(image_text)
    log("------------------------------")
    items = []
    total = 0
    for text_row in text.split("\n"):
        log(f"load receipt item row: {text_row}")
        text_row = text_row.removesuffix(" A")
        text_row = text_row.removesuffix(" B")
        if text_row != "":
            split = text_row.rsplit(" ", 1)
            if len(split)!=2:
                continue
            name, price_str = split
            try:
                price = float(price_str)
            except:
                continue

            if price<0:
                items[-1][1] += price
            else:
                if name == "TOTAL":
                    total = price
                    break
                items.append([name.strip(), price])

    df = pd.DataFrame(items, columns=["Item", "Price"])
    log("Loaded dataframe from uploaded receipt image: ")
    log(df)

    date_time_match = re.findall(r"Date:\s\d+/\d+/\d+\sTime:\s\d+:\d+:\d+", image_text)

    if len(date_time_match)>0:
        date_vals = date_time_match[0].split()
        date = utils.string_to_date(date_vals[1])
        time = utils.string_to_time(date_vals[3])
    else:
        date = None
        time = None

    log(f"Total Price - £{total:.2f}")
    log(f"Date - {utils.date_to_string(date)}")
    log(f"Time - {utils.time_to_string(time)}")

    return df, total, date, time



def upload_lidl_receipt(image_path, db_manager, money_store):
    log(f"Uploading Receipt: {image_path} Into Money Store: {money_store}")
    init_pytesseract()
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    vendor = "Lidl"

    del st.session_state["adding_spending_df"]
    adding_receipt = AddingTransaction(db_manager)
    adding_receipt.set_vendor_name("Lidl")
    adding_receipt.set_is_income(False)
    adding_receipt.set_money_store_used(money_store)

    row = db_manager.vendors.get_filtered_df("name", vendor).iloc[0]
    category = db_manager.categories.get_db_row(row["default_category_id"]).get("name", None)
    location = db_manager.shop_locations.get_db_row(row["default_location_id"]).get("shop_location", None)

    adding_receipt.set_spending_category(category)
    adding_receipt.set_shop_location(location)

    item_data, override_money, date, time = extract_from_lidl_receipt(text)

    adding_receipt.set_override_money(override_money)
    adding_receipt.set_spending_date(date)
    adding_receipt.set_spending_time(time)

    for i, row in item_data.iterrows():
        adding_receipt.add_product(row["Item"], row["Price"])

    return adding_receipt.add_transaction_to_db()




