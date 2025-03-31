import pandas as pd
import segno
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the "amfont" font (make sure it's in the same directory or provide the full path)
pdfmetrics.registerFont(TTFont('AmharicFont', 'font.ttf'))  # Or 'amfont.otf' or whatever the extension is

# Excel file and output settings
EXCEL_FILE = "Locations.xlsx"
SHEET_NAME = "Sheet1"
OUTPUT_FOLDER = "qr_codes"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
PDF_FILE = f"qr_codes_{timestamp}.pdf"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def save_qr_to_excel(location_numbers):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["LocationNumber", "Compound"])

    new_rows = pd.DataFrame({"LocationNumber": location_numbers, "Compound": [""] * len(location_numbers)})
    df = pd.concat([df, new_rows], ignore_index=True)
    df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)
    messagebox.showinfo("Success", "QR Codes saved to Excel")

def generate_qr_codes():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Excel file '{EXCEL_FILE}' not found.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Error reading Excel file: {e}")
        return

    pdf = canvas.Canvas(PDF_FILE, pagesize=letter)
    x, y = 80, 580
    count = 0

    for _, row in df.iterrows():
        location_number = str(row["LocationNumber"]).strip()
        compound = str(row.get("Compound", "")).strip()
        if location_number:
            qr = segno.make(location_number, error="h")
            qr_filename = os.path.join(OUTPUT_FOLDER, f"location_{location_number}.png")
            qr.save(qr_filename, scale=8, border=2)

            border_padding = 15
            border_x = x - border_padding
            border_y = y - border_padding
            border_width = 210 + 2 * border_padding
            border_height = 180 + 50
            pdf.setStrokeColor(colors.black)
            pdf.rect(border_x, border_y - 40, border_width, border_height, stroke=1, fill=0)

            pdf.drawImage(qr_filename, x + 15, y - 40, width=173, height=173)

            pdf.setFont("AmharicFont", 10)  # Use the registered name
            pdf.drawCentredString(x + 100, y + 160, "የአርባ ምንጭ ስ/ህ/ጤ ልማት ምርምር ማዕከል")

            pdf.setFont("Helvetica", 10)
            pdf.drawCentredString(x + 100, y + 145, "Arba Minch HDSS")
            
            pdf.setFont("Helvetica", 12)
            pdf.drawCentredString(x + 100, y + 130, f"LN: {compound}-{location_number}")

            count += 1
            if count % 2 == 0:
                x = 80
                y -= 260
            else:
                x += 220
            if count % 6 == 0:
                pdf.showPage()
                x, y = 80, 580
    pdf.save()
    messagebox.showinfo("Success", f"QR Codes saved in: {PDF_FILE}")


def add_qr_codes():
    def save_input():
        location_numbers = text_input.get("1.0", tk.END).strip().split("\n")
        location_list = [num.strip() for num in location_numbers if num.strip()]
        save_qr_to_excel(location_list)
        input_window.destroy()

    input_window = tk.Toplevel()
    input_window.title("Enter QR Codes")

    tk.Label(input_window, text="Enter Location Numbers (one per line):", font=("Helvetica", 14)).pack()
    text_input = tk.Text(input_window, width=40, height=10, font=("Helvetica", 12))
    text_input.pack()

    tk.Button(input_window, text="Save", command=save_input, font=("Helvetica", 12)).pack()


def create_gui():
    root = tk.Tk()
    root.title("QR Code Generator")

    tk.Button(root, text="Add QR Codes", command=add_qr_codes, font=("Helvetica", 14)).pack(pady=10)
    tk.Button(root, text="Generate PDF", command=generate_qr_codes, font=("Helvetica", 14)).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
