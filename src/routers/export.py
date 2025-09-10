
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Any, Dict
import io, json

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

router = APIRouter()

@router.post("/export/pdf")
async def export_pdf(payload: Dict[str, Any] = Body(...)):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Reporte PGx", styles["Title"]))
    story.append(Spacer(1, 12))
    patient = payload.get("patient", {})
    result = payload.get("result", {})
    story.append(Paragraph(f"Paciente: {patient.get('pseudonym','-')}", styles["Normal"]))
    story.append(Paragraph(f"Tumor: {patient.get('tumor_type','-')}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Resumen", styles["Heading2"]))
    story.append(Paragraph(result.get("summary","-"), styles["Normal"]))
    story.append(Spacer(1, 12))
    details = result.get("details") or []
    data = [["Acción","Fármaco","Variante","Nivel","Año"]]
    for d in details:
        meta = d.get("study_meta",{})
        var = d.get("variant",{})
        data.append([d.get("action",""), d.get("drug",""), f"{var.get('gene','')} {var.get('protein_change','')}", meta.get("level","-"), str(meta.get("year","-"))])
    if len(data) > 1:
        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.lightgrey), ('GRID',(0,0),(-1,-1), 0.5, colors.grey)]))
        story.append(table)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=report.pdf"})

@router.post("/export/json")
async def export_json(payload: Dict[str, Any] = Body(...)):
    blob = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return StreamingResponse(io.BytesIO(blob), media_type="application/json", headers={"Content-Disposition":"attachment; filename=report.json"})
