from PIL import Image
import pytesseract
import re
import sys
from src.logger import log
import pandas as pd
import src.utils as utils
from src.adding_transaction import AddingTransaction

def init_pytesseract():
    if sys.platform == "win32":
        path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        log(f"Set Python to pytesseract to: {path}")
        pytesseract.pytesseract.tesseract_cmd = path


def extract_from_lidl_receipt(image_text):
    text = image_text.split("£\n", 1)[1]
    text = text.split("*CUSTOMER COPY*", 1)[0]

    purchase_items = re.compile(r"([A-Za-z0-9&\s]+)\s+(\d+\.\d{2})\s+([A-Z])")
    items = purchase_items.findall(text)

    date_time_match = re.findall(r"Date:\s\d+/\d+/\d+\sTime:\s\d+:\d+:\d+", image_text)

    if len(date_time_match)>0:
        date_vals = date_time_match[0].split()
        date = utils.string_to_date(date_vals[1])
        time = utils.string_to_time(date_vals[3])
    else:
        date = None
        time = None

    df = pd.DataFrame(items, columns=["Item", "Price", "VAT"])[["Item", "Price"]]
    df["Item"] = df["Item"].str.strip()

    last_row = df.iloc[-1]
    df = df.iloc[:-1]

    return df, last_row["Price"], date, time



def upload_lidl_receipt(image_path, db_manager, money_store):
    init_pytesseract()
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    vendor = "Lidl"

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




