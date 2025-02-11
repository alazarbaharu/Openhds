import sqlite3
import segno
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Database file
DB_FILE = "bingo_cards.db"
OUTPUT_FOLDER = "qr_codes"

# Generate timestamp for the filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
PDF_FILE = f"qr_codes_{timestamp}.pdf"

# Ensure output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Page size and QR code size
PAGE_WIDTH, PAGE_HEIGHT = letter  # (612x792 points)
QR_SIZE = 180  # QR code size in pixels
MARGIN_X, MARGIN_Y = 80, 580  # Starting position (higher y)
GAP_X, GAP_Y = 220, 260  # Spacing between QR codes


# Connect to SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Fetch data from table
cursor.execute("SELECT LocationNumber FROM locqrcode")
rows = cursor.fetchall()

# Create a new PDF
pdf = canvas.Canvas(PDF_FILE, pagesize=letter)

# Initial position for placing QR codes
x, y = MARGIN_X, MARGIN_Y
count = 0  # Count QR codes per page

for row in rows:
    location_number = str(row[0]).strip()  # Ensure it's a string

    if location_number:
        # Generate QR Code
        qr = segno.make(location_number, error="h")
        qr_filename = os.path.join(OUTPUT_FOLDER, f"location_{location_number}.png")
        qr.save(qr_filename, scale=8, border=2)  # Save as PNG

        # Define border size
        border_padding = 20  # Space around QR
        border_x = x - border_padding
        border_y = y - border_padding
        border_size = QR_SIZE + 2 * border_padding

        # Draw a border around the QR code (with space for text inside)
        pdf.setStrokeColor(colors.black)
        pdf.rect(border_x, border_y - 30, border_size, border_size + 30, stroke=1, fill=0)

        # Add Header Text (Centered INSIDE border) "ARBA MINCH HDSS"
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(x + QR_SIZE / 2, y + QR_SIZE + 3, "ARBA MINCH HDSS")  

        # Add Location Number (Centered INSIDE border below "ARBA MINCH HDSS")
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(x + QR_SIZE / 2, y + QR_SIZE - 10, f"LN: {location_number}")

        # Draw QR Code inside the border
        pdf.drawImage(qr_filename, x, y - 12, width=QR_SIZE, height=QR_SIZE)  

        # Move to next position
        count += 1
        if count % 2 == 0:  # Two QR codes per row
            x = MARGIN_X  # Reset X
            y -= GAP_Y  # Move down to next row

           

        else:
            x += GAP_X  # Move right for next QR code

        # Move to a new page after 6 QR codes
        if count % 6 == 0:
            pdf.showPage()
            x, y = MARGIN_X, MARGIN_Y  # Reset position for new page

# Save the final PDF with timestamped filename
pdf.save()
print(f"QR Codes saved in: {PDF_FILE}")

# Close database connection
conn.close()
