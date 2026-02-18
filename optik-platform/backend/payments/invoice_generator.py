from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class InvoiceGenerator:
    def __init__(self, output_dir="invoices"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_pdf(self, invoice_data):
        invoice_id = invoice_data.get("invoice_id")
        if not invoice_id:
            raise ValueError("invoice_id is required to generate an invoice")
        file_path = os.path.join(self.output_dir, f"invoice_{invoice_id}.pdf")
        
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "OPTIK PLATFORM INVOICE")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Invoice ID: {invoice_id}")
        c.drawString(50, height - 100, f"Date: {invoice_data.get('date', 'N/A')}")
        
        # Customer Info
        c.drawString(50, height - 140, "To:")
        c.drawString(70, height - 160, f"Customer: {invoice_data.get('customer_name', 'N/A')}")
        c.drawString(70, height - 180, f"Email: {invoice_data.get('customer_email', 'N/A')}")

        # Items Table Header
        c.line(50, height - 210, width - 50, height - 210)
        c.drawString(50, height - 230, "Description")
        c.drawRightString(width - 50, height - 230, "Amount")
        c.line(50, height - 240, width - 50, height - 240)

        # Items
        y = height - 260
        for item in invoice_data.get("items", []):
            c.drawString(50, y, item['description'])
            c.drawRightString(width - 50, y, f"${item['amount']:.2f}")
            y -= 20

        # Total
        c.line(50, y, width - 50, y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 20, "Total")
        c.drawRightString(width - 50, y - 20, f"${invoice_data.get('total', 0):.2f}")

        c.showPage()
        c.save()
        
        return file_path
