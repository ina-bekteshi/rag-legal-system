from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.colors import HexColor

# ── Colour palette ────────────────────────────────────────────────────────────
NAVY    = HexColor("#1B2A4A")
TEAL    = HexColor("#1E7F8E")
LIGHT   = HexColor("#EAF4F6")
ACCENT  = HexColor("#C0392B")
MID     = HexColor("#4A6FA5")
LGREY   = HexColor("#F5F5F5")
DGREY   = HexColor("#555555")
WHITE   = colors.white
GREY_CH = HexColor("#CCCCCC")

# ── Document setup ─────────────────────────────────────────────────────────────
OUTPUT = "Week2_Report_Neurological_Severity_Scores.pdf"
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.5*cm,  bottomMargin=2.5*cm,
)
W, H = A4
CONTENT_W = W - 4.4*cm

# ── Styles (Clean Slate) ──────────────────────────────────────────────────────
styles = StyleSheet1()
def S(name, **kw): return ParagraphStyle(name, **kw)

styles.add(S("title", fontName="Helvetica-Bold", fontSize=20, textColor=WHITE, leading=26))
styles.add(S("subtitle", fontName="Helvetica", fontSize=10.5, textColor=HexColor("#D0E8EE"), leading=16))
styles.add(S("meta", fontName="Helvetica", fontSize=9, textColor=HexColor("#BDD8E0"), leading=13))
styles.add(S("section", fontName="Helvetica-Bold", fontSize=13, textColor=NAVY, leading=18, spaceBefore=18, spaceAfter=4))
styles.add(S("subsection", fontName="Helvetica-Bold", fontSize=10.5, textColor=TEAL, leading=15, spaceBefore=10, spaceAfter=2))
styles.add(S("body", fontName="Helvetica", fontSize=9.5, textColor=DGREY, leading=14.5, alignment=TA_JUSTIFY))
styles.add(S("caption", fontName="Helvetica-Oblique", fontSize=8.5, textColor=MID, leading=12, alignment=TA_CENTER))
styles.add(S("table_hdr", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, leading=12, alignment=TA_CENTER))
styles.add(S("table_cell", fontName="Helvetica", fontSize=9, textColor=DGREY, leading=13))
styles.add(S("table_cell_c", fontName="Helvetica", fontSize=9, textColor=DGREY, leading=13, alignment=TA_CENTER))

def p(text, style="body"): return Paragraph(text, styles[style])
def sp(h=6): return Spacer(1, h)
def hr(color=TEAL, w=1): return HRFlowable(width="100%", thickness=w, color=color, spaceAfter=4)

# ── Header banner ──────────────────────────────────────────────────────────────
def make_header():
    title_cell = [
        p("Week 2 Report", "title"),
        sp(3),
        p("Analysis of Neurological Severity Scores", "subtitle"),
        sp(6),
        p("Project: A Methodological Framework for Causal AI in the Analysis of Clinical<br/>"
          "Determinants of Treatment Outcomes in Cerebral Aneurysms", "meta"),
    ]
    info_cell = [
        Paragraph("<b><font color='#D0E8EE'>Submitted:</font></b>  March 17, 2026",
                  S("i1", fontName="Helvetica", fontSize=9, textColor=WHITE, leading=14)),
        Paragraph("<b><font color='#D0E8EE'>Deadline:</font></b>   March 20, 2026 — 14:00",
                  S("i2", fontName="Helvetica", fontSize=9, textColor=WHITE, leading=14)),
    ]
    tbl = Table([[title_cell, info_cell]], colWidths=[CONTENT_W*0.66, CONTENT_W*0.34])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (0,0), 22),
        ("RIGHTPADDING", (1,0), (1,0), 22),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return tbl

# ── Objective box (FIXED Tuple for LINEBEFORE) ─────────────────────────────────
def make_objective():
    text = (
        "<b>Objective:</b>  Understand the clinical indicators used in aneurysm treatment research — "
        "specifically the neurological severity scoring systems that quantify patient condition, "
        "guide clinical decision-making, and serve as key variables in causal and predictive analyses."
    )
    cell = Paragraph(text, S("obj", fontName="Helvetica", fontSize=9.5, textColor=NAVY, leading=14.5, alignment=TA_JUSTIFY))
    tbl = Table([[cell]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LINEBEFORE", (0,0), (0,-1), 4, TEAL), # Correct: Thickness 4, then Color TEAL
    ]))
    return tbl

# ── Tables ─────────────────────────────────────────────────────────────────────
def make_summary_table():
    headers = ["Score", "Domain Assessed", "Scale / Range", "Primary Use"]
    rows = [
        ["Glasgow Coma Scale\n(GCS)", "Level of consciousness\n& neurological function", "3 – 15\n(3 = deepest coma)", "Triage, ICU monitoring,\noutcome prediction"],
        ["WFNS Scale", "SAH clinical severity\n(combines GCS + motor)", "Grades I – V\n(I = best, V = worst)", "SAH grading,\nsurgical timing"],
        ["Hunt–Hess Scale", "SAH severity based on\nclinical presentation", "Grades 0 – V\n(0 = unruptured, V = worst)", "Pre-op risk stratification,\nmanagement planning"],
        ["Fisher Score", "CT-based SAH blood\ndistribution & volume", "Grades 1 – 4\n(1 = no blood, 4 = diffuse)", "Vasospasm risk,\nneurological deficit prediction"],
    ]
    data = [[p(h,"table_hdr") for h in headers]]
    for r in rows:
        data.append([p(r[0], "table_cell"), p(r[1], "table_cell"), p(r[2], "table_cell_c"), p(r[3], "table_cell_c")])
    tbl = Table(data, colWidths=[CONTENT_W*0.22, CONTENT_W*0.28, CONTENT_W*0.24, CONTENT_W*0.26])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGREY]),
        ("GRID", (0,0), (-1,-1), 0.4, GREY_CH),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW", (0,0), (-1,0), 1.5, TEAL),
    ]))
    return tbl

def make_causal_table():
    headers = ["Score", "Predictor?", "Confounder?", "Mediator?", "Causal Role Notes"]
    rows = [
        ["GCS", "Yes — strong", "Yes", "Possible", "May mediate path from bleed severity to outcome; often used as baseline covariate"],
        ["WFNS", "Yes — strong", "Yes", "Possible", "Incorporates GCS; captures neuro deficit; timing of measurement critical"],
        ["Hunt–Hess", "Yes", "Yes", "Less common", "Subjective element limits causal precision; useful for stratification"],
        ["Fisher", "Yes", "Partial", "Unlikely", "Radiological, not clinical; strong predictor of (downstream) vasospasm"],
    ]
    data = [[p(h,"table_hdr") for h in headers]]
    for r in rows:
        data.append([p(r[0], "table_cell"), p(r[1], "table_cell_c"), p(r[2], "table_cell_c"), p(r[3], "table_cell_c"), p(r[4], "table_cell")])
    tbl = Table(data, colWidths=[CONTENT_W*0.13, CONTENT_W*0.12, CONTENT_W*0.13, CONTENT_W*0.11, CONTENT_W*0.51])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGREY]),
        ("GRID", (0,0), (-1,-1), 0.4, GREY_CH),
        ("LINEBELOW", (0,0), (-1,0), 1.5, TEAL),
    ]))
    return tbl

def score_card(title, content_rows):
    title_p = Paragraph(title, S("ct", fontName="Helvetica-Bold", fontSize=10.5, textColor=WHITE, leading=15))
    card_data = [[title_p]]
    for label, text in content_rows:
        card_data.append([Paragraph(f"<b><font color='#1E7F8E'>{label}</font></b>  {text}",
                                    S("cd", fontName="Helvetica", fontSize=9.2, textColor=DGREY, leading=14, alignment=TA_JUSTIFY))])
    tbl = Table(card_data, colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), MID),
        ("BACKGROUND", (0,1), (0,-1), WHITE),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("BOX", (0,0), (-1,-1), 0.8, MID),
        ("LINEBEFORE", (0,1), (0,-1), 3, TEAL),
    ]))
    return tbl

def make_conclusion():
    text = (
        "All four scoring systems are essential variables in causal AI frameworks for cerebral aneurysm research. "
        "GCS and WFNS, capturing acute neurological status, function simultaneously as <b>baseline predictors</b>, "
        "<b>confounders</b>, and potential <b>mediators</b> on the causal path from aneurysm rupture to outcome. "
        "Hunt–Hess provides complementary clinical grading for risk stratification, while the Fisher Score "
        "introduces an independent radiological dimension. Together, they form a rich feature set for causal "
        "directed acyclic graphs (DAGs) and outcome-prediction models."
    )
    cell = Paragraph(text, S("conc", fontName="Helvetica", fontSize=9.5, textColor=NAVY, leading=14.5, alignment=TA_JUSTIFY))
    tbl = Table([[cell]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOX", (0,0), (-1,-1), 1, TEAL),
    ]))
    return tbl

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, 1.2*cm, fill=1, stroke=0)
    canvas.restoreState()

# ── BUILD STORY ────────────────────────────────────────────────────────────────
story = [make_header(), sp(14), make_objective(), sp(18)]

# 1. Intro
story.append(hr())
story.append(p("1.  Introduction", "section"))
story.append(p("Cerebral aneurysm management is guided substantially by the neurological condition of the patient at presentation. Standardised severity scores translate complex clinical pictures into variables that can be incorporated into statistical models. This report examines four instruments: the Glasgow Coma Scale (GCS), the WFNS Scale, the Hunt–Hess Scale, and the Fisher Score."))

# 2. Overview
story.append(sp(10))
story.append(hr())
story.append(p("2.  Comparative Overview", "section"))
story.append(make_summary_table())
story.append(p("Table 1. Summary of neurological severity scores.", "caption"))

# 3. Details
story.append(sp(14))
story.append(hr())
story.append(p("3.  Detailed Analysis of Each Score", "section"))

# GCS
story.append(KeepTogether([
    p("3.1  Glasgow Coma Scale (GCS)", "subsection"),
    score_card("GCS — Teasdale & Jennett, 1974", [
        ("What it measures:", "Consciousness level via Eye, Verbal, and Motor response. Range 3 to 15."),
        ("Clinical use:", "Triage and monitoring. Informing timing of intervention."),
        ("Role in research:", "Predictor of functional outcome; confounder and potential mediator."),
    ])
]))

# WFNS
story.append(sp(10))
story.append(KeepTogether([
    p("3.2  WFNS Subarachnoid Haemorrhage Scale", "subsection"),
    score_card("WFNS Scale — WFNS Committee, 1988", [
        ("What it measures:", "Clinical severity based on GCS and motor deficit. Grades I-V."),
        ("Clinical use:", "Guides management decisions for ruptured aneurysms."),
        ("Role in research:", "Strong predictor of mortality. Shared variance with GCS requires careful DAG handling."),
    ])
]))

# Hunt-Hess
story.append(sp(10))
story.append(KeepTogether([
    p("3.3  Hunt–Hess Scale", "subsection"),
    score_card("Hunt–Hess Scale — Hunt & Hess, 1968", [
        ("What it measures:", "Severity based on symptoms like headache, nuchal rigidity, and consciousness."),
        ("Clinical use:", "Pre-operative risk assessment and stratification."),
        ("Role in research:", "Predictor of post-op outcomes. Subjectivity may introduce inter-rater variability."),
    ])
]))

# Fisher
story.append(sp(10))
story.append(KeepTogether([
    p("3.4  Fisher Score (CT Grading Scale)", "subsection"),
    score_card("Fisher Score — Fisher et al., 1980", [
        ("What it measures:", "Pattern and volume of blood on CT imaging. Grades 1-4."),
        ("Clinical use:", "Predicting delayed cerebral ischaemia (DCI) and vasospasm."),
        ("Role in research:", "Radiological predictor capturing haemorrhage burden independent of clinical scores."),
    ])
]))

story.append(sp(14))
story.append(hr())
story.append(p("4.  Causal Analysis", "section"))
story.append(make_causal_table())

story.append(sp(14))
story.append(hr())
story.append(p("5.  Conclusion", "section"))
story.append(make_conclusion())

# References
story.append(sp(14))
story.append(p("6.  References", "section"))
for r in [
    "Teasdale G, Jennett B. Assessment of coma and impaired consciousness: a practical scale. <i>Lancet.</i> 1974;304(7872):81–84.",
    "World Federation of Neurological Surgeons Committee. Report of World Federation of Neurological Surgeons Committee on a universal subarachnoid hemorrhage grading scale. <i>J Neurosurg.</i> 1988;68(6):985–986.",
    "Hunt WE, Hess RM. Surgical risk as related to time of intervention in the repair of intracranial aneurysms. <i>J Neurosurg.</i> 1968;28(1):14–20.",
    "Fisher CM, Kistler JP, Davis JM. Relation of cerebral vasospasm to subarachnoid hemorrhage visualized by CT scanning. <i>Neurosurgery.</i> 1980;6(1):1–9.",
]:
    story.append(p(r))
    story.append(sp(2))

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Success: {OUTPUT}")