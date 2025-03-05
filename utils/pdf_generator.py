from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

def generate_quote_pdf(quote_data, output_path):
    """Generate a PDF document for the quote"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Set up initial coordinates
    y = height - inch
    left_margin = inch
    
    # Add header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(left_margin, y, "Travel Quote")
    y -= inch/2
    
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y, f"Generated on: {datetime.now().strftime('%B %d, %Y')}")
    y -= inch/2
    
    # Add group information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, "Group Information")
    y -= inch/2
    
    c.setFont("Helvetica", 12)
    group = quote_data['group']
    c.drawString(left_margin, y, f"Group Name: {group['name']}")
    y -= inch/4
    c.drawString(left_margin, y, f"Paying Participants: {group['num_paying']}")
    y -= inch/4
    c.drawString(left_margin, y, f"Free Chaperones: {group['num_chaperones']}")
    y -= inch/4
    c.drawString(left_margin, y, f"Total Participants: {group['num_paying'] + group['num_chaperones']}")
    y -= inch/2
    
    # Add costs breakdown
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, "Cost Breakdown")
    y -= inch/2
    
    c.setFont("Helvetica", 12)
    quote = quote_data['quote']
    
    # Transportation costs
    c.drawString(left_margin, y, "Transportation Costs:")
    y -= inch/4
    if quote['bus_cost']:
        c.drawString(left_margin + inch/2, y, f"Bus: ${quote['bus_cost']:,.2f}")
        y -= inch/4
    if quote['metro_cost']:
        c.drawString(left_margin + inch/2, y, f"Metro: ${quote['metro_cost']:,.2f}")
        y -= inch/4
    if quote['airline_cost']:
        c.drawString(left_margin + inch/2, y, f"Airline: ${quote['airline_cost']:,.2f}")
        y -= inch/4
    if quote['train_cost']:
        c.drawString(left_margin + inch/2, y, f"Train: ${quote['train_cost']:,.2f}")
        y -= inch/4
    
    # Guide costs
    y -= inch/4
    c.drawString(left_margin, y, "Guide Information:")
    y -= inch/4
    c.drawString(left_margin + inch/2, y, f"Daily Rate: ${quote['guide_rate']:,.2f}")
    y -= inch/4
    c.drawString(left_margin + inch/2, y, f"Number of Days: {quote['guide_days']}")
    y -= inch/4
    c.drawString(left_margin + inch/2, y, f"Guide Tip (per day): ${quote['guide_tip']:,.2f}")
    y -= inch/4
    c.drawString(left_margin + inch/2, y, f"Driver Tip (per day): ${quote['driver_tip']:,.2f}")
    
    # Entry tickets
    if quote['entry_tickets']:
        y -= inch/2
        c.drawString(left_margin, y, "Entry Tickets:")
        y -= inch/4
        for ticket in quote['entry_tickets']:
            if ticket['name'] and ticket['cost']:
                c.drawString(left_margin + inch/2, y, f"{ticket['name']}: ${ticket['cost']:,.2f}")
                y -= inch/4
    
    # Hotels
    if quote['hotels']:
        y -= inch/4
        c.drawString(left_margin, y, "Hotels:")
        y -= inch/4
        for hotel in quote['hotels']:
            if hotel['name'] and hotel['cost_per_room']:
                c.drawString(left_margin + inch/2, y, f"{hotel['name']}")
                y -= inch/4
                c.drawString(left_margin + inch, y, f"Standard Rate: ${hotel['cost_per_room']:,.2f}")
                y -= inch/4
                if hotel['has_high_occupancy'] and hotel['high_occupancy_cost']:
                    c.drawString(left_margin + inch, y, f"High Occupancy Rate: ${hotel['high_occupancy_cost']:,.2f}")
                    y -= inch/4
    
    # Profit amount
    y -= inch/2
    c.drawString(left_margin, y, f"Profit Amount (per person): ${quote['profit_amount']:,.2f}")
    
    # Add signature lines
    y -= inch * 1.5
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, "Agreement")
    y -= inch/2
    
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y, "Travel Company Representative:")
    y -= inch
    c.line(left_margin, y, left_margin + 4*inch, y)
    y -= inch/4
    c.drawString(left_margin, y, "Date:")
    c.line(left_margin + inch, y, left_margin + 3*inch, y)
    
    y -= inch
    c.drawString(left_margin, y, "Client Representative:")
    y -= inch
    c.line(left_margin, y, left_margin + 4*inch, y)
    y -= inch/4
    c.drawString(left_margin, y, "Date:")
    c.line(left_margin + inch, y, left_margin + 3*inch, y)
    
    # Save the PDF
    c.save()
