import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import datetime

def generate_report(detection_nodes, simulation_result, out_dir="reports"):
    os.makedirs(out_dir, exist_ok=True)
    fname = f"deepshield_report_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.pdf"
    path = os.path.join(out_dir, fname)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "DeepShield Analysis Report")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated: {datetime.datetime.utcnow().isoformat()}Z")
    y -= 20

    c.drawString(margin, y, "Detections:")
    y -= 15
    for n in detection_nodes:
        line = f"- {n['id']} | type: {n.get('type','?')} | score: {n.get('score','?')}"
        c.drawString(margin+10, y, line[:100])
        y -= 12
        if y < margin:
            c.showPage(); y = height - margin

    y -= 10
    c.drawString(margin, y, f"Simulation reach: {simulation_result.get('reach')}")
    y -= 20

    c.drawString(margin, y, "Legal-awareness summary:")
    y -= 12
    legal_text = [
        "1. Preserve originals and metadata for chain-of-custody.",
        "2. Prepare takedown / DMCA requests where applicable.",
        "3. Document impacted stakeholders and communications.",
        "4. Consult legal counsel before public statements."
    ]
    for t in legal_text:
        c.drawString(margin+10, y, t)
        y -= 12
        if y < margin:
            c.showPage(); y = height - margin

    c.save()
    return path
