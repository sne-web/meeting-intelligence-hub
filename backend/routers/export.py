import csv
import io
import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

router = APIRouter(prefix="/api/export", tags=["export"])

STORAGE_DIR = "storage"
MEETINGS_FILE = os.path.join(STORAGE_DIR, "meetings_store.json")

def get_meeting(meeting_id: str):
    if not os.path.exists(MEETINGS_FILE):
        raise HTTPException(status_code=404, detail="No meetings found")
    with open(MEETINGS_FILE, "r") as f:
        meetings = json.load(f)
    meeting = next((m for m in meetings if m["id"] == meeting_id), None)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.get("/{meeting_id}/csv")
def export_csv(meeting_id: str):
    meeting = get_meeting(meeting_id)
    
    # Create an in-memory string buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write metadata
    writer.writerow(["Meeting File", meeting.get("filename", "Unknown")])
    writer.writerow(["Upload Date", meeting.get("upload_date", "")])
    writer.writerow(["Overall Sentiment", meeting.get("sentiment", {}).get("overall_sentiment", "")])
    writer.writerow([])
    
    # Write Decisions
    writer.writerow(["--- DECISIONS ---"])
    writer.writerow(["Decision", "Context"])
    for dec in meeting.get("decisions", []):
        writer.writerow([dec.get("description", ""), dec.get("context", "")])
    
    writer.writerow([])
    
    # Write Action Items
    writer.writerow(["--- ACTION ITEMS ---"])
    writer.writerow(["Who", "What", "By When", "Priority"])
    for item in meeting.get("action_items", []):
        writer.writerow([item.get("who", ""), item.get("what", ""), item.get("by_when", ""), item.get("priority", "")])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=analysis_{meeting_id}.csv"}
    )

@router.get("/{meeting_id}/pdf")
def export_pdf(meeting_id: str):
    meeting = get_meeting(meeting_id)
    
    # Create an in-memory bytes buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    h1 = styles['Heading1']
    h2 = styles['Heading2']
    normal = styles['Normal']
    
    # Title
    elements.append(Paragraph(f"Meeting Analysis: {meeting.get('filename', 'Unknown')}", h1))
    elements.append(Paragraph(f"Date: {meeting.get('upload_date', 'N/A')}", normal))
    elements.append(Spacer(1, 12))
    
    # Sentiment
    sentiment = meeting.get("sentiment", {})
    if sentiment:
        elements.append(Paragraph("Sentiment Overview", h2))
        elements.append(Paragraph(f"Overall: {sentiment.get('overall_sentiment', 'N/A')} (Score: {sentiment.get('overall_score', 0)})", normal))
        elements.append(Paragraph(f"Summary: {sentiment.get('summary', 'N/A')}", normal))
        elements.append(Spacer(1, 12))
        
    # Decisions Table
    decisions = meeting.get("decisions", [])
    if decisions:
        elements.append(Paragraph("Decisions", h2))
        data = [["Decision", "Context"]]
        for dec in decisions:
            data.append([
                Paragraph(dec.get("description", ""), normal),
                Paragraph(dec.get("context", ""), normal)
            ])
            
        table = Table(data, colWidths=[200, 250])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        
    # Action Items Table
    action_items = meeting.get("action_items", [])
    if action_items:
        elements.append(Paragraph("Action Items", h2))
        data = [["Who", "What", "By When", "Priority"]]
        for item in action_items:
            data.append([
                Paragraph(item.get("who", ""), normal),
                Paragraph(item.get("what", ""), normal),
                Paragraph(item.get("by_when", ""), normal),
                Paragraph(item.get("priority", ""), normal),
            ])
            
        table = Table(data, colWidths=[80, 200, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=analysis_{meeting_id}.pdf"}
    )
