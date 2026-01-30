import pandas as pd
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

def generate_qr_code(BusNo, BusLicense, BusType, output_dir):
    qr_data = f"BusNo: {BusNo}, BusLicense: {BusLicense}, BusType: {BusType}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill="black", back_color="white").convert("RGB") 
    
    try:
        font = ImageFont.truetype("cmtt10.ttf",60) 
    except IOError:
        font = ImageFont.load_default()
    
    text = f"GMA BUS {BusNo}"
    
    draw = ImageDraw.Draw(img_qr)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    img_width, img_height = img_qr.size
    total_height = text_height + img_height + 10

    img = Image.new("RGB", (img_width, total_height), "white")
    draw = ImageDraw.Draw(img)
    draw.text(((img_width - text_width) / 2, 0), text, font=font, fill="black")
    
    img.paste(img_qr, (0, text_height + 10))
    
    img_path = os.path.join(output_dir, f"{BusNo}_QR.png")
    img.save(img_path)
    print(f"QR code saved for {BusNo} at {img_path}")

def generate_qr_codes_from_csv(csv_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    buses = pd.read_csv(csv_file)

    for index, row in buses.iterrows():
        BusNo = row['BusNo']
        BusLicense = row['BusLicense']
        BusType = row['BusType']

        generate_qr_code(BusNo=BusNo, BusLicense=BusLicense, BusType=BusType, output_dir=output_dir)

csv_file = 'buses.csv'
output_dir = 'qr_codes' 

generate_qr_codes_from_csv(csv_file, output_dir)
