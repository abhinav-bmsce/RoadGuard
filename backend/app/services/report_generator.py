"""
RoadGuard - PDF Report Generator
Produces formal civil engineering inspection reports using ReportLab.
Includes executive summary, high-resolution annotated image embedding, damage inventory tables, and maintenance directives.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as ReportLabImage,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from backend.app.core.config import settings
from backend.app.core.logging import logger


class ReportGenerator:
    @staticmethod
    def generate_pdf(
        report_id: str,
        detection_data: Dict[str, Any],
        inspector_name: str = "Civil Infrastructure Inspector",
        location_notes: str = "Unspecified Pavement Section",
        output_dir: str = None
    ) -> str:
        if output_dir is None:
            output_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        pdf_filename = f"RoadGuard_Report_{report_id}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            alignment=0
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )
        cell_style = ParagraphStyle(
            "CellNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b")
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a")
        )

        elements = []

        # 1. Header Banner
        header_table = Table(
            [
                [
                    Paragraph("ROADGUARD", ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=24, textColor=colors.HexColor("#f59e0b"))),
                    Paragraph("CIVIL INFRASTRUCTURE INSPECTION REPORT<br/><font color='#64748b'>Deep Learning Road Damage & Severity Audit</font>", ParagraphStyle("RightHead", fontName="Helvetica", fontSize=9, alignment=2, textColor=colors.HexColor("#334155")))
                ]
            ],
            colWidths=[200, 340]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#f59e0b"), spaceAfter=12))

        # 2. Inspection Metadata Box
        meta_data = [
            [
                Paragraph("<b>Report ID:</b>", cell_bold), Paragraph(str(report_id), cell_style),
                Paragraph("<b>Inspection Date:</b>", cell_bold), Paragraph(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), cell_style),
            ],
            [
                Paragraph("<b>Inspector:</b>", cell_bold), Paragraph(inspector_name, cell_style),
                Paragraph("<b>Location / Route:</b>", cell_bold), Paragraph(location_notes or "N/A", cell_style),
            ],
            [
                Paragraph("<b>Original Image:</b>", cell_bold), Paragraph(detection_data.get("original_filename", "road_scan.jpg"), cell_style),
                Paragraph("<b>AI Model:</b>", cell_bold), Paragraph("RoadGuard YOLOv8n (RDD2022)", cell_style),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[90, 180, 90, 180])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 10))

        # 3. Key Findings Scorecard
        severity_level = detection_data.get("severity_level", "Low")
        severity_score = detection_data.get("severity_score", 0.0)
        total_damages = detection_data.get("total_damages", 0)
        latency = detection_data.get("inference_time_ms", 0.0)

        sev_color = colors.HexColor("#10b981") if severity_level == "Low" else (
            colors.HexColor("#f59e0b") if severity_level == "Medium" else colors.HexColor("#ef4444")
        )

        scorecard = [
            [
                Paragraph("OVERALL SEVERITY", cell_bold),
                Paragraph("ROAD SEVERITY INDEX (RDSI)", cell_bold),
                Paragraph("TOTAL DEFECTS", cell_bold),
                Paragraph("AI LATENCY", cell_bold)
            ],
            [
                Paragraph(f"<font color='{sev_color.hexval()}'><b>{severity_level.upper()}</b></font>", ParagraphStyle("ScoreBig", fontName="Helvetica-Bold", fontSize=14, alignment=1)),
                Paragraph(f"<b>{severity_score:.1f} / 100</b>", ParagraphStyle("ScoreVal", fontName="Helvetica-Bold", fontSize=14, alignment=1)),
                Paragraph(f"<b>{total_damages}</b>", ParagraphStyle("ScoreVal", fontName="Helvetica-Bold", fontSize=14, alignment=1)),
                Paragraph(f"<b>{latency:.1f} ms</b>", ParagraphStyle("ScoreVal", fontName="Helvetica-Bold", fontSize=14, alignment=1))
            ]
        ]
        score_table = Table(scorecard, colWidths=[135, 135, 135, 135])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 8))

        # Explicit Experimental Assessment Disclaimer Box
        disclaimer_text = (
            "<b>EXPERIMENTAL ESTIMATE (Non-Certified Assessment):</b> Severity classifications and RDSI "
            "scores are automated AI screening metrics derived from 2D surface geometry. They do NOT replace "
            "certified ASTM D6433 structural pavement evaluations. On-site depth profiling and geotechnical "
            "engineer sign-off are required for certified civil maintenance intervention."
        )
        disclaimer_style = ParagraphStyle(
            "DisclaimerStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#475569")
        )
        disclaimer_box = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[540])
        disclaimer_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")), # Amber background
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#f59e0b")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(disclaimer_box)
        elements.append(Spacer(1, 10))

        # 4. Annotated Visual Image Section
        annotated_path = detection_data.get("annotated_image_path")
        if annotated_path and os.path.exists(annotated_path):
            elements.append(Paragraph("ANNOTATED DAMAGE LOCALIZATION", section_style))
            try:
                # Add image scaled proportionally
                img_flowable = ReportLabImage(annotated_path, width=6.5 * inch, height=3.6 * inch)
                elements.append(img_flowable)
                elements.append(Spacer(1, 10))
            except Exception as e:
                logger.error(f"Error embedding image in PDF: {e}")

        # 5. Damage Instance Inventory Table
        elements.append(Paragraph("DETAILED DAMAGE INVENTORY", section_style))
        damages = detection_data.get("damages", [])
        
        table_rows = [
            [
                Paragraph("<b>#</b>", cell_bold),
                Paragraph("<b>Distress Classification</b>", cell_bold),
                Paragraph("<b>Confidence</b>", cell_bold),
                Paragraph("<b>Area Ratio</b>", cell_bold),
                Paragraph("<b>Instance Score</b>", cell_bold),
                Paragraph("<b>Severity</b>", cell_bold)
            ]
        ]

        if not damages:
            table_rows.append([
                Paragraph("1", cell_style),
                Paragraph("No pavement distress detected", cell_style),
                Paragraph("N/A", cell_style),
                Paragraph("0.0%", cell_style),
                Paragraph("0.0", cell_style),
                Paragraph("Low", cell_style)
            ])
        else:
            for i, dmg in enumerate(damages):
                tag = dmg.get("severity_tag", "Low")
                tag_color = "#10b981" if tag == "Low" else ("#f59e0b" if tag == "Medium" else "#ef4444")
                table_rows.append([
                    Paragraph(str(i + 1), cell_style),
                    Paragraph(f"<b>{dmg.get('class_name', '')}</b>", cell_style),
                    Paragraph(f"{dmg.get('confidence', 0.0)*100:.1f}%", cell_style),
                    Paragraph(f"{dmg.get('area_ratio', 0.0)*100:.2f}%", cell_style),
                    Paragraph(f"{dmg.get('instance_severity', 0.0):.1f}", cell_style),
                    Paragraph(f"<font color='{tag_color}'><b>{tag}</b></font>", cell_style),
                ])

        dmg_table = Table(table_rows, colWidths=[30, 200, 75, 75, 80, 80])
        dmg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(dmg_table)
        elements.append(Spacer(1, 14))

        # 6. Actionable Engineering Directives
        elements.append(Paragraph("RECOMMENDED MAINTENANCE ACTION", section_style))
        if severity_level == "High":
            recommendation_text = (
                "<b>CRITICAL STRUCTURAL ATTENTION REQUIRED:</b> Deep pothole or advanced fatigue cracking detected. "
                "Immediate cold/hot-mix asphalt patching required to prevent vehicle rim failure and moisture sub-base erosion. "
                "Dispatch road maintenance crew within 24-48 hours."
            )
        elif severity_level == "Medium":
            recommendation_text = (
                "<b>SCHEDULED SURFACE RESTORATION:</b> Medium distress patterns identified. "
                "Schedule crack sealing and micro-surfacing within 30 days to halt oxidation and water penetration."
            )
        else:
            recommendation_text = (
                "<b>ACCEPTABLE PAVEMENT STATUS:</b> Negligible or hairline cracks observed. "
                "Continue standard semi-annual visual surveillance. No emergency civil intervention warranted."
            )

        rec_box = Table([[Paragraph(recommendation_text, cell_style)]], colWidths=[540])
        rec_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, sev_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(rec_box)
        elements.append(Spacer(1, 14))

        # 7. Engineer Sign-off Footer
        sign_table = Table([
            [
                Paragraph("<b>Audited By:</b> ___________________________", cell_style),
                Paragraph("<b>Authorized Signature:</b> ___________________________", cell_style),
                Paragraph("<b>Date:</b> ______________", cell_style)
            ]
        ], colWidths=[180, 240, 120])
        elements.append(sign_table)

        doc.build(elements)
        logger.info(f"Generated PDF inspection report at {pdf_path}")
        return pdf_path

