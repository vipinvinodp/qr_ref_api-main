from flask import Flask, request, send_file, jsonify, render_template_string
import qrcode
from PIL import Image
import io
import os
import json

app = Flask(__name__)

# Mapping dictionary for AV references
qr_data = {
    "AV1": {
        "title": "AV1",
        "location": "Please place in AV70, AV57 box in the master room",
        "use": "This item is used for creating mathematical objects",
        "category": "Tool used by whole family"
    },
    "AV2": {
        "title": "AV2",
        "location": "Please place in AV17, AV23 box in the bedroom",
        "use": "This item is used for repairing pipe",
        "category": "Tool used by Dada"
    },
    "AV3": {
        "title": "AV3",
        "location": "Love Please place in AV25 box in the kitchen",
        "use": "This item is used for cooking vegetables",
        "category": "Tool used by Mumma and Dada"
    }
    # Add up to AV50 as needed
}

@app.route("/view/<code>", methods=["GET"])
def view_code(code):
    entry = qr_data.get(code.upper())
    if not entry:
        return f"<h3>No entry found for {code}</h3>", 404

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h2 { color: #4CAF50; }
            .label { font-weight: bold; }
            .info { margin-top: 15px; }
        </style>
    </head>
    <body>
        <h2>{{ title }}</h2>
        <div class="info"><span class="label">Where to keep:</span> {{ location }}</div>
        <div class="info"><span class="label">Use:</span> {{ use }}</div>
        <div class="info"><span class="label">Category:</span> {{ category }}</div>
    </body>
    </html>
    """
    return render_template_string(html_template, **entry)

@app.route("/generate_sheet", methods=["POST"])
def generate_sheet():
    try:
        data_list = request.get_json().get("data", [])
        cols, rows = 5, 10
        qr_size = 200
        page_width = cols * qr_size
        page_height = rows * qr_size
        sheet = Image.new("RGB", (page_width, page_height), "white")

        logo = Image.open("doll.png")
        logo_size = 100
        logo.thumbnail((logo_size, logo_size))

        for idx, item in enumerate(data_list[:50]):
            code = item.get("X1", "AVX")
            qr_url = f"https://qr-ref-api-main.onrender.com/view/{code}"

            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=2,
                border=1
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            img_qr = img_qr.resize((qr_size, qr_size))

            # Add doll logo to center
            pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
            img_qr.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

            x = (idx % cols) * qr_size
            y = (idx // cols) * qr_size
            sheet.paste(img_qr, (x, y))

        output = io.BytesIO()
        sheet.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
