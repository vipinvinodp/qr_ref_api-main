from flask import Flask, request, send_file, jsonify
import qrcode
from PIL import Image
import json
import io
import os

app = Flask(__name__)

@app.route("/generate_sheet", methods=["POST"])
def generate_sheet():
    try:
        # Read the JSON input
        data_list = request.get_json().get("data", [])

        # Define grid layout and QR size
        cols, rows = 5, 10
        qr_size = 200
        page_width = cols * qr_size
        page_height = rows * qr_size
        sheet = Image.new("RGB", (page_width, page_height), "white")

        # Load doll logo
        logo = Image.open("doll.png")
        logo_size = 100
        logo.thumbnail((logo_size, logo_size))

        # Generate QR codes and paste into sheet
        for idx, item in enumerate(data_list[:50]):  # limit to 50
            qr_content = json.dumps({
                "X1": item.get("X1", ""),
                "X2": item.get("X2", ""),
                "X3": item.get("X3", ""),
                "X4": item.get("X4", []),
                "X5": item.get("X5", "")
            }, separators=(',', ':'))

            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=2,
                border=1
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            img_qr = img_qr.resize((qr_size, qr_size))

            # Insert doll logo at center
            pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
            img_qr.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

            # Position on sheet
            x = (idx % cols) * qr_size
            y = (idx // cols) * qr_size
            sheet.paste(img_qr, (x, y))

        # Return as image
        img_bytes = io.BytesIO()
        sheet.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
