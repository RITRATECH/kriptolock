import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont


# === Export ke HTML ===
def export_log_to_html(log_file="kriptolock.log", output_file="log_report.html"):
    with open(log_file, "r") as f:
        lines = f.readlines()

    html = """
    <html>
    <head>
        <title>Laporan KriptoLock</title>
        <style>
            body { font-family: monospace; background: #f5f5f5; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #999; padding: 8px; }
            th { background-color: #222; color: white; }
            td { background-color: white; }
        </style>
    </head>
    <body>
        <h2>Laporan Aktivitas KriptoLock</h2>
        <table>
            <tr><th>Waktu</th><th>Aksi</th><th>File</th><th>Status</th></tr>
    """

    for line in lines:
        try:
            ts, action_info = line.strip().split("] [", 1)
            timestamp = ts.replace("[", "")
            action, rest = action_info.split("] ", 1)
            filename, status = rest.split(" → ")
            html += f"<tr><td>{timestamp}</td><td>{action}</td><td>{filename}</td><td>{status}</td></tr>"
        except:
            continue

    html += """
        </table>
        <p>Exported at {}</p>
    </body></html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open(output_file, "w") as f:
        f.write(html)

    print(f"[📄] Log berhasil diekspor ke: {output_file}")

# ===  Export ke PDF  ===
def export_log_to_pdf(log_file="kriptolock.log", output_file="log_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)

    pdf.cell(200, 10, txt="Laporan KriptoLock", ln=1, align="C")
    pdf.ln(5)

    if not os.path.exists(log_file):
        pdf.cell(200, 10, txt="Log file tidak ditemukan.", ln=1)
    else:
        with open(log_file, "r") as f:
            for line in f:
                safe_line = line.strip().replace("→", "->")
                pdf.cell(200, 5, txt=safe_line, ln=1)

    pdf.output(output_file)
    print(f"[📄] Log berhasil diekspor ke PDF: {output_file}")

# === Export ke PNG  ===
def export_log_to_png(log_file="kriptolock.log", output_file="log_report.png"):
    lines = open(log_file).readlines()
    W, H = 1000, 20 * len(lines) + 50
    image = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    y = 10
    for line in lines:
        draw.text((10, y), line.strip(), fill="black", font=font)
        y += 20

    image.save(output_file)
    print(f"[🖼️] Log berhasil diekspor ke PNG: {output_file}")
    
# Panggil fungsi saat dijalankan
if __name__ == "__main__":
    export_log_to_html()
    export_log_to_pdf()
    export_log_to_png()
