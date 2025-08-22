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
print(text)

full_text = "\n".join(text)
print("Raw OCR output:\n", full_text)

# Step 4: Extract items + prices using regex
# Assumes format like "ItemName   12.99"
pattern = r"(.+?)\s+(\d+\.\d{2})"
items = re.findall(pattern, full_text)

print("\nExtracted items:")
for item, price in items:
    print(f"{item.strip()} → ${price}")