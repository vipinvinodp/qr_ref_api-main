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
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Mapping dictionary
qr_lookup = {
    "AV1": {
        "title": "AV1",
        "location": "Please place in AV70, AV57 box in the master room",
        "use": "This item is used for creating mathematical objects",
        "category": "Category is tool used by whole family"
    },
    "AV2": {
        "title": "AV2",
        "location": "Please place in AV17, AV23 box in the bedroom",
        "use": "This item is used for repairing pipe",
        "category": "Category is tool used by Dada"
    },
    "AV3": {
        "title": "AV3",
        "location": "Please place in AV25 box in the kitchen",
        "use": "This item is used for cooking vegetables",
        "category": "Category is tool used by Mumma"
    }
    # Add up to AV50...
}

# View endpoint
@app.route("/view/<code>", methods=["GET"])
def view_code(code):
    entry = qr_lookup.get(code.upper())
    if not entry:
        return f"<h3>No entry found for {code}</h3>", 404

    html_template = """
    <html>
    <head><title>{{ title }}</title></head>
    <body style="font-family:sans-serif;">
        <h2>{{ title }}</h2>
        <p><strong>Where to Keep:</strong> {{ location }}</p>
        <p><strong>Item Use:</strong> {{ use }}</p>
        <p><strong>Category:</strong> {{ category }}</p>
    </body>
    </html>
    """
    return render_template_string(html_template, **entry)
