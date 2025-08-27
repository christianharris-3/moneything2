# import pytesseract
#
# from PIL import Image
#
# img = Image.open("images/tesco1.jpg")
# text = pytesseract.image_to_string(img)
# print(text)

import easyocr
import re

reader = easyocr.Reader(['en'])
text = reader.readtext("images/tesco2.jpg", detail=0)

full_text = "\n".join(text)

# Step 4: Extract items + prices using regex
# Assumes format like "ItemName   12.99"
pattern = r"(.+?)\s+(\d+\.\d{2})"
items = re.findall(pattern, full_text)
