import os
import time
import unicodedata
from flask import Flask, request, render_template_string
from openai import OpenAI
import usb.core
import usb.util

# ======================
# CONFIGURATION
# ======================
# Replace these with your printer's USB IDs
VENDOR_ID = 0x0000   # placeholder
PRODUCT_ID = 0x0000  # placeholder

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
PRINTER_ENCODING = "cp437"

app = Flask(__name__)
client = OpenAI()

# ======================
# TEXT ENCODING
# ======================
def encode_for_printer(text: str) -> bytes:
    """
    Normalize Unicode text and encode it into a
    printer-compatible single-byte character set.
    """
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode(PRINTER_ENCODING, errors="replace")

# ======================
# ORACLE GENERATION
# ======================
def generate_oracle(topic: str) -> str:
    prompt = f"""
You are a dark-cute oracle.

Your voice is gentle, gothic, and comforting.
Think candlelight, lace, ink, moonlight, quiet shadows.
Soft darkness, never frightening.

Rules:
- Write in English
- 70 to 100 words
- Short poetic lines suitable for receipt printing
- No violence, curses, or fear
- No medical, legal, or financial advice
- Address the reader as "you"
- End with a single short mantra line

Topic:
{topic}
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt.strip(),
    )

    return response.output_text.strip()

# ======================
# USB PRINTING (RAW ESC/POS)
# ======================
def print_receipt(text: str):
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise RuntimeError("USB printer not found")

    try:
        # Detach kernel driver if necessary
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
    except usb.core.USBError:
        pass

    # Ensure a configuration is active
    try:
        dev.get_active_configuration()
    except usb.core.USBError:
        dev.set_configuration()

    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]

    # Locate the bulk OUT endpoint
    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT
    )

    if ep_out is None:
        raise RuntimeError("OUT endpoint not found")

    receipt = (
        b"\x1b@"  # Initialize printer
        + b"\n\n"
        + b"*** THE ORACLE ***\n"
        + b"whispers from the dark\n"
        + b"--------------------\n\n"
        + encode_for_printer(text)
        + b"\n\n--------------------\n"
        + b"carry this softly\n"
        + b"trust the quiet pull\n\n"
        + b"\x1dV\x01"  # Full cut
    )

    ep_out.write(receipt, timeout=5000)
    time.sleep(0.2)
    usb.util.dispose_resources(dev)

# ======================
# WEB UI
# ======================
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dark Oracle</title>
<style>
body {
  background: #0b0b0b;
  color: #eee;
  font-family: serif;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.box {
  background: #161616;
  padding: 28px;
  border-radius: 14px;
  width: 320px;
  box-shadow: 0 0 30px #000;
}
h1 {
  text-align: center;
  font-weight: normal;
  letter-spacing: 2px;
}
input {
  width: 100%;
  padding: 10px;
  background: #0f0f0f;
  color: #eee;
  border: 1px solid #333;
  border-radius: 6px;
}
button {
  width: 100%;
  margin-top: 14px;
  padding: 10px;
  background: #2a2a2a;
  color: #eee;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
button:hover {
  background: #444;
}
</style>
</head>

<body>
<div class="box">
  <h1>THE ORACLE</h1>
  <form method="POST">
    <input name="topic" placeholder="Love, career, fate..." required>
    <button type="submit">Receive Oracle</button>
  </form>
</div>
</body>
</html>
"""

# ======================
# ROUTE
# ======================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form["topic"]
        oracle = generate_oracle(topic)
        print_receipt(oracle)
    return render_template_string(HTML)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
