from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF
import io


# ─── COLOUR PALETTE ───────────────────────────────────────
C_DARK    = colors.HexColor('#0f0f1a')
C_NAVY    = colors.HexColor('#1a1a2e')
C_BLUE    = colors.HexColor('#667eea')
C_PURPLE  = colors.HexColor('#764ba2')
C_GREEN   = colors.HexColor('#68d391')
C_ORANGE  = colors.HexColor('#f6ad55')
C_RED     = colors.HexColor('#fc8181')
C_WHITE   = colors.HexColor('#ffffff')
C_LIGHT   = colors.HexColor('#e2e8f0')
C_MUTED   = colors.HexColor('#718096')
C_SUCCESS = colors.HexColor('#276749')
C_WARN    = colors.HexColor('#744210')
C_DANGER  = colors.HexColor('#742a2a')
C_INFO_BG = colors.HexColor('#ebf8ff')
C_GRAD1   = colors.HexColor('#667eea')
C_GRAD2   = colors.HexColor('#764ba2')


def _score_color(score: int):
    if score >= 7:
        return C_GREEN
    elif score >= 5:
        return C_ORANGE
    else:
        return C_RED


def _score_bg(score: int):
    if score >= 7:
        return colors.HexColor('#f0fff4')
    elif score >= 5:
        return colors.HexColor('#fffaf0')
    else:
        return colors.HexColor('#fff5f5')


def _readiness_verdict(score: int):
    if score >= 70:
        return ("Strong Candidate", C_GREEN, colors.HexColor('#f0fff4'))
    elif score >= 50:
        return ("Needs Some Work", C_ORANGE, colors.HexColor('#fffaf0'))
    else:
        return ("Significant Gaps", C_RED, colors.HexColor('#fff5f5'))


def _mini_bar(score: int, max_val: int = 10, width: int = 180, height: int = 10) -> Drawing:
    d = Drawing(width, height)
    # background
    d.add(Rect(0, 0, width, height, rx=4, ry=4,
               fillColor=colors.HexColor('#e2e8f0'), strokeColor=None))
    # fill
    fill_w = int((score / max_val) * width)
    fill_c = _score_color(score)
    if fill_w > 0:
        d.add(Rect(0, 0, fill_w, height, rx=4, ry=4,
                   fillColor=fill_c, strokeColor=None))
    return d


def generate_pdf_report(
    job_role: str,
    readiness_score: int,
    skill_scores: dict,
    skill_reasoning: dict,
    gap_analysis: dict,
    learning_plan: dict,
    youtube_results: dict
) -> bytes:

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    W = A4[0] - 3.6 * cm  # usable width

    # ─── STYLES ──────────────────────────────────────────
    styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    title_style = S('T', fontName='Helvetica-Bold', fontSize=26,
                    textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=2)
    subtitle_style = S('Sub', fontName='Helvetica', fontSize=11,
                       textColor=colors.HexColor('#a0aec0'),
                       alignment=TA_CENTER, spaceAfter=4)
    role_style = S('Role', fontName='Helvetica-Bold', fontSize=13,
                   textColor=colors.HexColor('#63b3ed'),
                   alignment=TA_CENTER, spaceAfter=0)
    section_style = S('Sec', fontName='Helvetica-Bold', fontSize=14,
                      textColor=C_BLUE, spaceBefore=14, spaceAfter=6)
    body_style = S('Bod', fontName='Helvetica', fontSize=10,
                   textColor=colors.HexColor('#2d3748'),
                   spaceAfter=4, leading=15)
    small_style = S('Sm', fontName='Helvetica', fontSize=9,
                    textColor=C_MUTED, spaceAfter=3, leading=13)
    bold_small = S('BS', fontName='Helvetica-Bold', fontSize=9,
                   textColor=colors.HexColor('#2d3748'))
    skill_name_s = S('SN', fontName='Helvetica-Bold', fontSize=10,
                     textColor=colors.HexColor('#1a202c'))
    white_bold = S('WB', fontName='Helvetica-Bold', fontSize=11,
                   textColor=C_WHITE, alignment=TA_CENTER)
    white_sm = S('WSm', fontName='Helvetica', fontSize=9,
                 textColor=colors.HexColor('#cbd5e0'), alignment=TA_CENTER)
    footer_s = S('Ft', fontName='Helvetica', fontSize=8,
                 textColor=C_MUTED, alignment=TA_CENTER)

    elems = []

    # ─── HERO HEADER ─────────────────────────────────────
    header_data = [[
        Paragraph("◈ CATALYST", title_style),
    ]]
    header_tbl = Table(header_data, colWidths=[W])
    header_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_NAVY),
        ('ROUNDEDCORNERS', [12], ),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    elems.append(header_tbl)

    sub_data = [[
        Paragraph("AI Skill Assessment Report", subtitle_style),
    ], [
        Paragraph(f"Role: {job_role}", role_style),
    ]]
    sub_tbl = Table(sub_data, colWidths=[W])
    sub_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_NAVY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('LINEBELOW', (0, -1), (-1, -1), 3, C_BLUE),
    ]))
    elems.append(sub_tbl)
    elems.append(Spacer(1, 14))

    # ─── READINESS OVERVIEW ──────────────────────────────
    elems.append(Paragraph("Overall Readiness", section_style))

    verdict_text, verdict_color, verdict_bg = _readiness_verdict(readiness_score)

    overview_data = [
        [
            Paragraph("Readiness Score", white_bold),
            Paragraph("Skills Assessed", white_bold),
            Paragraph("Verdict", white_bold),
        ],
        [
            Paragraph(f"{readiness_score}%", S('RS', fontName='Helvetica-Bold',
                      fontSize=28, textColor=C_BLUE, alignment=TA_CENTER)),
            Paragraph(str(len(skill_scores)), S('SA', fontName='Helvetica-Bold',
                      fontSize=28, textColor=C_GREEN, alignment=TA_CENTER)),
            Paragraph(verdict_text, S('V', fontName='Helvetica-Bold',
                      fontSize=14, textColor=verdict_color, alignment=TA_CENTER)),
        ]
    ]
    ov_tbl = Table(overview_data, colWidths=[W/3]*3)
    ov_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [8]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elems.append(ov_tbl)
    elems.append(Spacer(1, 14))

    # ─── SKILL SCORES ────────────────────────────────────
    elems.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor('#e2e8f0')))
    elems.append(Paragraph("Skill Assessment Scores", section_style))

    skill_rows = [[
        Paragraph("Skill", S('SH', fontName='Helvetica-Bold', fontSize=10,
                  textColor=C_WHITE)),
        Paragraph("Score", S('SH2', fontName='Helvetica-Bold', fontSize=10,
                  textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Level", S('SH3', fontName='Helvetica-Bold', fontSize=10,
                  textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Progress", S('SH4', fontName='Helvetica-Bold', fontSize=10,
                  textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Feedback", S('SH5', fontName='Helvetica-Bold', fontSize=10,
                  textColor=C_WHITE)),
    ]]

    for skill, score in skill_scores.items():
        if score >= 8:
            level_label = "Expert"
        elif score >= 6:
            level_label = "Proficient"
        elif score >= 4:
            level_label = "Basic"
        else:
            level_label = "Beginner"

        reasoning = skill_reasoning.get(skill, "")[:70]
        sc = _score_color(score)

        skill_rows.append([
            Paragraph(skill, skill_name_s),
            Paragraph(f"{score}/10", S('Sc', fontName='Helvetica-Bold',
                      fontSize=12, textColor=sc, alignment=TA_CENTER)),
            Paragraph(level_label, S('Lv', fontName='Helvetica', fontSize=9,
                      textColor=sc, alignment=TA_CENTER)),
            _mini_bar(score),
            Paragraph(reasoning, small_style),
        ])

    skill_tbl = Table(skill_rows,
                      colWidths=[W*0.22, W*0.1, W*0.12, W*0.25, W*0.31])
    skill_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#ffffff'), colors.HexColor('#f7fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 2, C_BLUE),
    ]))
    elems.append(skill_tbl)
    elems.append(Spacer(1, 14))

    # ─── GAP ANALYSIS ────────────────────────────────────
    if gap_analysis:
        elems.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor('#e2e8f0')))
        elems.append(Paragraph("Gap Analysis", section_style))

        strong = gap_analysis.get("strong_skills", [])
        gaps   = gap_analysis.get("gap_skills", [])
        adj    = gap_analysis.get("adjacent_skills", [])

        gap_cols = []

        def _gap_col(items, label, bg, tc, icon):
            rows = [[Paragraph(f"{icon}  {label}", S('GL',
                     fontName='Helvetica-Bold', fontSize=10,
                     textColor=tc))]]
            for item in items:
                rows.append([Paragraph(f"• {item}", S('GI',
                             fontName='Helvetica', fontSize=9,
                             textColor=colors.HexColor('#2d3748'),
                             leading=13))])
            if not items:
                rows.append([Paragraph("None identified", S('GN',
                             fontName='Helvetica-Oblique', fontSize=9,
                             textColor=C_MUTED))])
            t = Table(rows, colWidths=[(W/3) - 6])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), bg),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fafafa')),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            return t

        t1 = _gap_col(strong, "Strong Skills",
                      colors.HexColor('#f0fff4'), C_SUCCESS, "✓")
        t2 = _gap_col(gaps, "Skill Gaps",
                      colors.HexColor('#fff5f5'), C_DANGER, "✗")
        t3 = _gap_col(adj, "Adjacent Skills",
                      colors.HexColor('#ebf8ff'),
                      colors.HexColor('#2b6cb0'), "→")

        gap_row = Table([[t1, t2, t3]], colWidths=[W/3]*3,
                        hAlign='LEFT')
        gap_row.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elems.append(gap_row)
        elems.append(Spacer(1, 14))

    # ─── LEARNING PLAN ───────────────────────────────────
    if learning_plan and learning_plan.get("learning_plan"):
        elems.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor('#e2e8f0')))
        elems.append(Paragraph("Personalised Learning Plan", section_style))

        total_time = learning_plan.get("total_time_estimate", "")
        order = learning_plan.get("recommended_order", [])

        if total_time or order:
            meta_items = []
            if total_time:
                meta_items.append(f"⏱  Total time: {total_time}")
            if order:
                meta_items.append(f"📋  Recommended order: {' → '.join(order)}")

            meta_tbl = Table(
                [[Paragraph(item, S('MI', fontName='Helvetica', fontSize=9,
                            textColor=colors.HexColor('#2c5282')))
                  for item in meta_items]],
                colWidths=[W / len(meta_items)] * len(meta_items)
                if meta_items else [W]
            )
            meta_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1),
                 colors.HexColor('#ebf8ff')),
                ('GRID', (0, 0), (-1, -1), 0.3,
                 colors.HexColor('#bee3f8')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elems.append(meta_tbl)
            elems.append(Spacer(1, 10))

        priority_colors = {
            'HIGH':   (colors.HexColor('#fff5f5'), C_DANGER,
                       colors.HexColor('#feb2b2')),
            'MEDIUM': (colors.HexColor('#fffaf0'), C_WARN,
                       colors.HexColor('#fbd38d')),
            'LOW':    (colors.HexColor('#f0fff4'), C_SUCCESS,
                       colors.HexColor('#9ae6b4')),
        }

        for item in learning_plan.get("learning_plan", []):
            skill     = item.get("skill", "")
            priority  = item.get("priority", "MEDIUM")
            time_est  = item.get("time_estimate", "")
            mini_proj = item.get("mini_project", "")

            p_bg, p_tc, p_border = priority_colors.get(
                priority, priority_colors['MEDIUM']
            )

            header_row = [[
                Paragraph(skill, S('PLH', fontName='Helvetica-Bold',
                          fontSize=11, textColor=colors.HexColor('#1a202c'))),
                Paragraph(priority, S('PLP', fontName='Helvetica-Bold',
                          fontSize=9, textColor=p_tc, alignment=TA_CENTER)),
                Paragraph(f"⏱  {time_est}", S('PLT', fontName='Helvetica',
                          fontSize=9, textColor=C_MUTED, alignment=TA_RIGHT)),
            ]]
            h_tbl = Table(header_row, colWidths=[W*0.5, W*0.2, W*0.3])
            h_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), p_bg),
                ('LINEBELOW', (0, 0), (-1, -1), 1.5, p_border),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, 0), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elems.append(h_tbl)

            if mini_proj:
                mp_tbl = Table(
                    [[Paragraph(f"🛠  Mini project: {mini_proj}",
                                S('MP', fontName='Helvetica-Oblique',
                                  fontSize=9,
                                  textColor=colors.HexColor('#4a5568'),
                                  leading=13))]],
                    colWidths=[W]
                )
                mp_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1),
                     colors.HexColor('#fafafa')),
                    ('LINEBELOW', (0, 0), (-1, -1), 0.3,
                     colors.HexColor('#e2e8f0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ]))
                elems.append(mp_tbl)

            videos = youtube_results.get(skill, [])
            if videos:
                vid_rows = [[
                    Paragraph("Resource", S('VH', fontName='Helvetica-Bold',
                              fontSize=9, textColor=C_MUTED)),
                    Paragraph("Channel", S('VH2', fontName='Helvetica-Bold',
                              fontSize=9, textColor=C_MUTED)),
                    Paragraph("Views", S('VH3', fontName='Helvetica-Bold',
                              fontSize=9, textColor=C_MUTED,
                              alignment=TA_CENTER)),
                    Paragraph("Link", S('VH4', fontName='Helvetica-Bold',
                              fontSize=9, textColor=C_MUTED)),
                ]]
                for v in videos:
                    title = v.get('title', '')[:50]
                    vid_rows.append([
                        Paragraph(title, S('VT', fontName='Helvetica',
                                  fontSize=8, leading=12,
                                  textColor=colors.HexColor('#2d3748'))),
                        Paragraph(v.get('channel', ''),
                                  S('VC', fontName='Helvetica', fontSize=8,
                                    textColor=C_MUTED)),
                        Paragraph(v.get('view_count_display', 'N/A'),
                                  S('VV', fontName='Helvetica', fontSize=8,
                                    textColor=C_MUTED, alignment=TA_CENTER)),
                        Paragraph(v.get('url', ''),
                                  S('VU', fontName='Helvetica', fontSize=7,
                                    textColor=C_BLUE, leading=10)),
                    ])
                v_tbl = Table(vid_rows,
                              colWidths=[W*0.38, W*0.2, W*0.1, W*0.32])
                v_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0),
                     colors.HexColor('#f7fafc')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                     [C_WHITE, colors.HexColor('#f7fafc')]),
                    ('GRID', (0, 0), (-1, -1), 0.2,
                     colors.HexColor('#e2e8f0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elems.append(v_tbl)

            elems.append(Spacer(1, 8))

    # ─── FOOTER ──────────────────────────────────────────
    elems.append(Spacer(1, 10))
    elems.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor('#e2e8f0')))
    elems.append(Spacer(1, 6))

    footer_tbl = Table(
        [[Paragraph(
            "Generated by ◈ Catalyst — AI Skill Assessment Platform  |  "
            "Powered by Agentic AI + Groq + YouTube API",
            footer_s
        )]],
        colWidths=[W]
    )
    footer_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elems.append(footer_tbl)

    doc.build(elems)
    buffer.seek(0)
    return buffer.getvalue()