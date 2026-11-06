import os
import sys
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas
import pypdf

class IndividualCanvas(canvas.Canvas):
    def __init__(self, *args, member_name="", role_title="", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.member_name = member_name
        self.role_title = role_title

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, letter[1] - 28, f"RECONSTRUCT.AI  |  {self.member_name} — {self.role_title}")
            self.drawRightString(letter[0] - 40, letter[1] - 28, "Individual Contributor Dossier")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, letter[1] - 33, letter[0] - 40, letter[1] - 33)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, letter[0] - 40, 36)

        self.drawString(40, 26, f"OFFICIAL SUBMISSION DOSSIER  —  {self.member_name.upper()} (JSPM RSCOE, PUNE)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 26, page_str)
        self.restoreState()


def create_canvas_class(name, role):
    class CustomCanvas(IndividualCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, member_name=name, role_title=role, **kwargs)
    return CustomCanvas


def build_member_pdf(member_info):
    filename = member_info["filename"]
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=38,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    brand_style = ParagraphStyle(
        'BrandStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=10,
        textColor=colors.HexColor('#2563EB'), spaceAfter=2
    )

    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=17, leading=20,
        textColor=colors.HexColor('#0F172A'), spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=12.5,
        textColor=colors.HexColor('#475569'), spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13.5,
        textColor=colors.HexColor('#0F172A'), spaceBefore=6, spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=12,
        textColor=colors.HexColor('#1E293B'), spaceBefore=4, spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#334155'), spaceAfter=3.5
    )

    bullet_style = ParagraphStyle(
        'BulletStyle', parent=body_style,
        leftIndent=12, firstLineIndent=-8, spaceAfter=2
    )

    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=9.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.2, leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    fig_caption_style = ParagraphStyle(
        'FigCaption', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7, leading=9,
        textColor=colors.HexColor('#2563EB'), alignment=1, spaceBefore=2, spaceAfter=4
    )

    story = []

    # =========================================================================
    # PAGE 1: Identity, Personal Mandate, Technical Ownership & Architecture
    # =========================================================================
    banner_left = [
        Paragraph(f"INDIVIDUAL CONTRIBUTOR DOSSIER  &bull;  {member_info['role'].upper()}", brand_style),
        Paragraph(f"{member_info['name']}", title_style),
        Paragraph(f"<b>Team:</b> Reconstruct.ai &nbsp;|&nbsp; <b>Institution:</b> JSPM RSCOE, Pune", subtitle_style),
    ]
    banner_right = [
        Paragraph(f"<b>Event:</b> We Code Coders Hackathon", body_style),
        Paragraph(f"<b>Domain:</b> {member_info['domain']}", body_style),
        Paragraph(f"<b>Email:</b> {member_info['email']}", body_style),
        Paragraph(f"<b>Repository:</b> <a href='https://github.com/Dhruvplaz-web/reconstruct-ai'><font color='#2563EB'><u>github.com/Dhruvplaz-web/reconstruct-ai</u></font></a>", body_style),
    ]

    banner_table = Table([[banner_left, banner_right]], colWidths=[4.2 * inch, 3.15 * inch])
    banner_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, 0), (-1, -1), 1.2, colors.HexColor('#0F172A')),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 4))

    # Personal Contribution Statement (Rule 14 Compliance)
    story.append(Paragraph("1. Personal Mandate & Individual Contribution Statement (Rule 14)", h1_style))
    story.append(Paragraph(member_info["mandate"], body_style))

    # Core Systems Owned
    story.append(Paragraph("2. Subsystem Ownership & Technical Architecture", h1_style))
    for bullet in member_info["subsystems"]:
        story.append(Paragraph(f"• {bullet}", bullet_style))
    story.append(Spacer(1, 4))

    # Relevant Diagram for their specific role
    diag_path = os.path.join(assets_dir, member_info["diagram"])
    if os.path.exists(diag_path):
        story.append(Image(diag_path, width=7.35 * inch, height=member_info["diag_height"] * inch))
        story.append(Paragraph(member_info["diag_caption"], fig_caption_style))

    story.append(Paragraph("3. Technical Deliverables Across All 3 Rounds", h1_style))
    deliv_data = [
        [Paragraph("Hackathon Round", table_header_style), Paragraph("Personal Responsibilities & Concrete Engineering Deliverables", table_header_style)],
        [
            Paragraph("<b>Round 1: The Plan</b><br/>(Current Phase)", table_cell_bold),
            Paragraph(member_info["round1_deliverables"], table_cell_style)
        ],
        [
            Paragraph("<b>Round 2: The Build</b><br/>(Working Functional MVP)", table_cell_bold),
            Paragraph(member_info["round2_deliverables"], table_cell_style)
        ],
        [
            Paragraph("<b>Round 3: The Finish</b><br/>(Production Polish & UAT)", table_cell_bold),
            Paragraph(member_info["round3_deliverables"], table_cell_style)
        ]
    ]
    deliv_table = Table(deliv_data, colWidths=[1.8 * inch, 5.55 * inch])
    deliv_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(deliv_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: Competitor Defense, Judge Interview Q&A (Rule 16) & Team Roster
    # =========================================================================
    story.append(Paragraph("4. Competitor Failure Analysis & Defense for this Domain", h1_style))
    story.append(Paragraph(member_info["competitor_analysis"], body_style))
    story.append(Spacer(1, 3))

    # Judge Viva / Interview Defense Cheat Sheet (Rule 16 Compliance)
    story.append(Paragraph("5. Judge Viva & Technical Decision Defense (Rule 16 Preparation)", h1_style))
    story.append(Paragraph(
        "<i>Per Rule 16 ('Judges may ask any team member to explain the product, demonstrate a feature, justify a technical decision or verify their contribution'), this section details the anticipated questions and defensible justifications:</i>",
        body_style
    ))

    qa_data = [
        [Paragraph("Anticipated Judge Question / Challenge", table_header_style), Paragraph("Defensible Technical Justification & Verification Evidence", table_header_style)],
        [
            Paragraph(f"<b>Q1: {member_info['q1']}</b>", table_cell_bold),
            Paragraph(member_info['a1'], table_cell_style)
        ],
        [
            Paragraph(f"<b>Q2: {member_info['q2']}</b>", table_cell_bold),
            Paragraph(member_info['a2'], table_cell_style)
        ],
        [
            Paragraph(f"<b>Q3: {member_info['q3']}</b>", table_cell_bold),
            Paragraph(member_info['a3'], table_cell_style)
        ]
    ]
    qa_table = Table(qa_data, colWidths=[2.5 * inch, 4.85 * inch])
    qa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(qa_table)
    story.append(Spacer(1, 4))

    # Complete Team Roster
    story.append(Paragraph("6. Full Project Team Roster & Peer Verification", h1_style))
    team_summary_data = [
        [Paragraph("Member Full Name", table_header_style), Paragraph("Assigned Role", table_header_style), Paragraph("Institution", table_header_style), Paragraph("Project Verification Status", table_header_style)],
        [Paragraph("<b>Khushi Patil</b>", table_cell_style), Paragraph("Team Lead & Head of Research", table_cell_style), Paragraph("JSPM RSCOE, Pune", table_cell_style), Paragraph("VERIFIED (Team Lead)", table_cell_bold)],
        [Paragraph("<b>Dhruv Patil</b>", table_cell_style), Paragraph("AI Development & Core Engineering Lead", table_cell_style), Paragraph("JSPM RSCOE, Pune", table_cell_style), Paragraph("VERIFIED (AI Core Lead)", table_cell_bold)],
        [Paragraph("<b>Yuvraj Kadam</b>", table_cell_style), Paragraph("Lead Full-Stack Frontend & UI/UX", table_cell_style), Paragraph("JSPM RSCOE, Pune", table_cell_style), Paragraph("VERIFIED (Frontend Lead)", table_cell_bold)],
        [Paragraph("<b>Nimisha Joshi</b>", table_cell_style), Paragraph("Systems Backend, Ingestion & Security", table_cell_style), Paragraph("JSPM RSCOE, Pune", table_cell_style), Paragraph("VERIFIED (Backend Lead)", table_cell_bold)]
    ]
    team_table = Table(team_summary_data, colWidths=[1.7 * inch, 2.5 * inch, 1.7 * inch, 1.45 * inch])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(team_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Primary Project Repository:</b> <a href='https://github.com/Dhruvplaz-web/reconstruct-ai'><font color='#2563EB'><u>https://github.com/Dhruvplaz-web/reconstruct-ai</u></font></a> &bull; <b>Target Event:</b> We Code Coders Three-Round Hackathon", body_style))

    CustomCanvas = create_canvas_class(member_info["name"], member_info["role"])
    doc.build(story, canvasmaker=CustomCanvas)
    print(f"Successfully generated Individual PDF: {pdf_path}")


def generate_all_individual_pdfs():
    members = [
        # =====================================================================
        # 1. KHUSHI PATIL — Team Lead & Head of Research & Product Strategy
        # =====================================================================
        {
            "name": "Khushi Patil",
            "role": "Team Lead & Head of Research & Product Strategy",
            "domain": "Product Strategy, Cognitive Problem Taxonomy & Milestone Management",
            "email": "khushi@reconstruct.ai",
            "filename": "Reconstruct_AI_Khushi_Patil.pdf",
            "mandate": (
                "As the Team Lead and Head of Research, I am responsible for overall project orchestration, sprint prioritization, "
                "problem validation, and ensuring 100% adherence to the hackathon's 11 mandatory submission items and 100-point judging rubric. "
                "I spearheaded the qualitative audit of developer turnover dynamics across Reddit r/ExperiencedDevs and Hacker News, "
                "formulated the theoretical foundation around Nonaka's SECI model (tacit vs. explicit knowledge breakdown), and established "
                "the multi-domain problem taxonomy spanning Enterprise Tech, Academic Research Labs, Student Clubs, and Open-Source Communities."
            ),
            "subsystems": [
                "<b>SECI & Agile Paradox Research Framework:</b> Theoretical formulation explaining why agile sprint speed directly accelerates organizational forgetting.",
                "<b>Competitor Teardown Matrix:</b> Competitive benchmarking against Glean, Atlassian Rovo, Swimm, and NotebookLM to isolate market gaps.",
                "<b>Sprint Planning & Milestone Governance:</b> Tracking task breakdown across all 4 team members for Rounds 1, 2, and 3.",
                "<b>User Acceptance Criteria & Success Rubric:</b> Defining measurable KPIs (80% ramp-up reduction, 15x leaver documentation friction cut)."
            ],
            "diagram": "workflow_pipeline.png",
            "diag_height": 1.7,
            "diag_caption": "Figure 1: End-to-End Operational Lifecycle Managed Under Khushi Patil's Product Roadmap",
            "round1_deliverables": (
                "Authored problem understanding dossier, SECI taxonomy, competitor autopsy matrix, team responsibility breakdown, "
                "and ensured full compliance with all 11 hackathon brief requirements."
            ),
            "round2_deliverables": (
                "Lead User Acceptance Testing (UAT), coordinate between frontend and backend leads, curate real-world test scenarios, "
                "and ensure working MVP runs end-to-end for judge evaluations."
            ),
            "round3_deliverables": (
                "Direct the final 3-minute product walkthrough video, author the comprehensive security and accessibility audit documentation, "
                "and manage the delivery of the 3 major promised Round 3 product improvements."
            ),
            "competitor_analysis": (
                "Traditional tools fail because they treat handover as a documentation task rather than an organizational sociology challenge. "
                "Confluence fails due to the 'Graveyard Effect' (wikis rot in 30 days). Glean fails due to the 'Passive Search Gap' (new hires don't know what to ask). "
                "Reconstruct.ai overcomes these structural market failures by shifting from manual push-based wikis to automated pull-based graph synthesis."
            ),
            "q1": "Why focus on student clubs and research labs in addition to enterprise software teams?",
            "a1": (
                "Because institutional knowledge loss is actually more severe in non-corporate environments: student clubs face a 100% leadership reset every 1-4 years, "
                "and academic labs suffer from post-doc rotation reproducibility crises. Reconstruct.ai's architecture is domain-agnostic."
            ),
            "q2": "How did you ensure the team's plan is feasible within the hackathon time constraints?",
            "a2": (
                "We explicitly separated our Round 2 Scoped MVP (GitHub + Slack ingestion, DAG extraction, and 60-second review) from Round 3 enhancements "
                "(advanced NLI contradiction radar and ABAC toggle). We also added the 1-Click Synthetic Playground so judges can evaluate the app in 30 seconds."
            ),
            "q3": "How do you measure whether Reconstruct.ai actually solves the knowledge handover problem?",
            "a3": (
                "Through three quantitative KPIs: 1) Successor time-to-first-commit reduced from 4 weeks to under 4 days; 2) Bus Factor = 1 orphan code eliminated; "
                "3) Leaver offboarding burden cut from 20 hours to under 60 seconds."
            )
        },

        # =====================================================================
        # 2. DHRUV PATIL — AI Development & Core Engineering Lead
        # =====================================================================
        {
            "name": "Dhruv Patil",
            "role": "AI Development & Core Engineering Lead",
            "domain": "AI Pipelines, LLM Orchestration, Epistemic NLI Verification & Rapid AI Coding",
            "email": "dhruvpatil4555@gmail.com",
            "filename": "Reconstruct_AI_Dhruv_Patil.pdf",
            "mandate": (
                "As the AI Development Lead, I own the machine intelligence, reasoning, and automated code implementation engine of Reconstruct.ai. "
                "I design the multi-stage LLM orchestration pipelines (leveraging Gemini 1.5 Pro and Claude 3.5 Sonnet) that autonomously extract architectural "
                "decisions, unresolved blockers, and operational dependencies from raw Git commit histories and unstructured chat threads. "
                "Furthermore, I engineered the mathematical formulation for Epistemic Confidence Scoring G(A) and the pairwise Natural Language Inference (NLI) "
                "Contradiction Radar using HuggingFace DeBERTa-v3 to resolve conflicting project assertions without ungrounded hallucinations."
            ),
            "subsystems": [
                "<b>Dual-Stage LLM Extraction Chains:</b> High-recall structured prompt architecture converting PR reviews, commits, and Slack threads into temporal facts.",
                "<b>Epistemic Contradiction Radar:</b> Pairwise NLI cross-encoder (DeBERTa-v3-small) identifying cross-source factual conflicts with >70% contradiction probability.",
                "<b>Mathematical Grounding Score Formula:</b> Implementation of G(A) = λ·S_evidence + (1-λ)·e^(-γΔt)·(1-P(Contradiction)) to quarantine uncertain assertions.",
                "<b>AI-Augmented Core Codebase Development:</b> Driving rapid full-stack scaffolding and algorithmic logic using state-of-the-art agentic engineering workflows."
            ],
            "diagram": "prov_nli_architecture.png",
            "diag_height": 1.9,
            "diag_caption": "Figure 1: W3C PROV-DM & DeBERTa-v3 NLI Verification Engine Engineered by Dhruv Patil",
            "round1_deliverables": (
                "Formulated the epistemic verification architecture, prompt schemas, mathematical confidence decay models, "
                "and engineered the synthetic benchmark evaluation dataset (Acme Payments microservice)."
            ),
            "round2_deliverables": (
                "Implement the core LLM decision extraction pipeline, citation grounding linker, and local DeBERTa-v3 NLI cross-encoder "
                "scripts integrated into the FastAPI backend."
            ),
            "round3_deliverables": (
                "Deliver real-time Contradiction Radar badge triggers in the UI, fine-tune the epistemic confidence thresholds, "
                "and deploy automated hallucination prevention guardrails."
            ),
            "competitor_analysis": (
                "Existing RAG tools (like NotebookLM or Atlassian Rovo) fail catastrophically when sources contradict each other—they hallucinate an ungrounded compromise. "
                "Reconstruct.ai refuses to invent consensus. Our pairwise NLI engine detects contradictions explicitly and surfaces them side-by-side with confidence scores."
            ),
            "q1": "Why use DeBERTa-v3 for contradiction detection instead of asking an LLM directly?",
            "a1": (
                "Cross-encoder NLI models like DeBERTa-v3-small are deterministic, computationally lightweight, run locally in milliseconds with zero API costs, "
                "and are mathematically trained specifically on Natural Language Inference (premise vs. hypothesis entailment/contradiction)."
            ),
            "q2": "How does your architecture solve cross-source entity disambiguation (e.g. Slack chat vs PR commit)?",
            "a2": (
                "We implement a 48-hour sliding temporal co-occurrence window combined with semantic embedding cosine similarity. If a Slack thread discussions "
                "coincide temporally with a Git PR merge and exhibit cosine similarity > 0.78, we bind them under a formal W3C prov:wasDerivedFrom relationship."
            ),
            "q3": "How do you guarantee that generated handovers contain zero hallucinations?",
            "a3": (
                "Through strict W3C PROV-DM cryptographic URI grounding. Every single claim is bound to an exact commit diff or chat thread URI. "
                "Assertions with grounding scores G(A) < 0.65 are quarantined into the human review queue and never presented as verified organizational truth."
            )
        },

        # =====================================================================
        # 3. YUVRAJ KADAM — Lead Full-Stack Frontend & UI/UX Engineer
        # =====================================================================
        {
            "name": "Yuvraj Kadam",
            "role": "Lead Full-Stack Frontend & UI/UX Engineer",
            "domain": "Next.js 14 Application, Continuation Workspace Kanban & NotebookLM Citation Drawer",
            "email": "yuvraj@reconstruct.ai",
            "filename": "Reconstruct_AI_Yuvraj_Kadam.pdf",
            "mandate": (
                "As the Lead Full-Stack Frontend and UI/UX Engineer, I own the user-facing web application of Reconstruct.ai. "
                "My mission is to eliminate the 'Wiki Graveyard' by replacing static reading pages with an interactive, living continuation hub. "
                "I architect the responsive frontend using Next.js 14 (App Router), Tailwind CSS, and Radix UI primitives, strictly adhering to an 8-point spatial grid. "
                "I specifically engineered the NotebookLM-style Citation Sidecar Drawer (which smoothly reveals exact source diffs upon clicking citation chips), "
                "the Day 1–30 Actionable Onboarding Kanban, and the 60-Second Leaver Review Modal."
            ),
            "subsystems": [
                "<b>Next.js 14 App Architecture:</b> Server-side rendered speed, client-side state caching, and URL-first shareable filters.",
                "<b>Interactive Continuation Workspace:</b> 3-column layout featuring Temporal Decision DAG, Executive Briefing, and Actionable Kanban.",
                "<b>NotebookLM-Style Citation Sidecar Drawer:</b> Slide-out drawer displaying code diffs and Slack transcripts side-by-side with the active claim.",
                "<b>60-Second Leaver Review Modal:</b> Frictionless 3-question prompt interface with cryptographic approval stamp for departing developers."
            ],
            "diagram": "platform_ui_wireframe.png",
            "diag_height": 2.2,
            "diag_caption": "Figure 1: Reconstruct.ai Production Web Architecture Engineered by Yuvraj Kadam",
            "round1_deliverables": (
                "Designed the component blueprints, UX wireframes, 8pt spatial design tokens, and defined the 5 core web module interface architectures."
            ),
            "round2_deliverables": (
                "Build and deploy the functional Next.js 14 web client, implement the 1-Click Demo Playground interface, "
                "and connect live REST endpoints from the FastAPI backend."
            ),
            "round3_deliverables": (
                "Implement interactive Temporal DAG graph visualization, keyboard accessibility (WCAG AA), active focus rings, "
                "and responsive layouts stress-tested across mobile (375px) and desktop (1440px)."
            ),
            "competitor_analysis": (
                "Swimm provides code walkthroughs but is a code-only silo. Confluence provides documents that nobody reads. "
                "Reconstruct.ai combines the document readability of Confluence with the live code-coupling of Swimm and the citation trust of NotebookLM."
            ),
            "q1": "How does your UI design solve the 'Two-Week Notice Paradox' for a departing employee?",
            "a1": (
                "We designed the '60-Second Leaver Review Gate'. Rather than asking the leaver to fill out a blank wiki, our system mines Git Blame for orphan code "
                "and presents only 3 targeted micro-questions with 1-click dropdowns. They approve the handover in under 1 minute."
            ),
            "q2": "Why did you choose Next.js 14 and Tailwind over heavy UI component libraries?",
            "a2": (
                "Next.js 14 App Router provides instantaneous server-side rendering and zero client-side JavaScript bloat. Radix UI headless primitives give us "
                "full ownership of accessibility (focus trapping, keyboard navigation, aria labels) without the monolithic baggage of heavy design libraries."
            ),
            "q3": "How does the UI handle permission-based redactions for incoming junior developers?",
            "a3": (
                "The UI features a live Role Switcher dropdown. In 'Junior Successor' view, restricted tokens (salaries, AWS keys) are rendered as blurred "
                "[REDACTED BY PERMISSION POLICY] badges with tooltips explaining required access tiers, strictly proving trust-awareness to judges."
            )
        },

        # =====================================================================
        # 4. NIMISHA JOSHI — Systems Backend, Data Ingestion & Security Architect
        # =====================================================================
        {
            "name": "Nimisha Joshi",
            "role": "Systems Backend, Data Ingestion & Security Architect",
            "domain": "FastAPI Services, Git Blame Orphan Code Miner, Ingestion Pipelines & ABAC Redaction",
            "email": "nimisha@reconstruct.ai",
            "filename": "Reconstruct_AI_Nimisha_Joshi.pdf",
            "mandate": (
                "As the Systems Backend, Data Ingestion, and Security Architect, I own the data intake infrastructure, Git repository analysis, "
                "and permission-aware security boundaries of Reconstruct.ai. I architect the asynchronous Python FastAPI REST service, "
                "implement the Git Blame Orphan Code Miner to detect Bus Factor = 1 vulnerabilities across repositories, and build the "
                "multi-source ingestion connectors for GitHub, Slack, and Jira. Additionally, I enforce the hackathon's strict Trust Requirements "
                "through an Attribute-Based Access Control (ABAC) engine that dynamically redacts confidential records before data serialization."
            ),
            "subsystems": [
                "<b>Python FastAPI Backend Engine:</b> High-throughput async REST endpoints with auto-generated OpenAPI documentation and Pydantic v2 schemas.",
                "<b>Git Blame Orphan Code Miner:</b> AST-level Git tree parser using GitPython that calculates commit ownership and flags files with >75% single-author blame.",
                "<b>Multi-Source Ingestion Pipeline:</b> Parsers for GitHub GraphQL/REST commits and PRs, Slack/Discord JSON message exports, and Markdown docs.",
                "<b>Attribute-Based Access Control (ABAC) Redaction Engine:</b> Pre-serialization security inspection that masks confidential HR, salary, and credential tokens."
            ],
            "diagram": "workflow_pipeline.png",
            "diag_height": 1.7,
            "diag_caption": "Figure 1: Ingestion & Verification Data Pipeline Architecture Managed by Nimisha Joshi",
            "round1_deliverables": (
                "Engineered the multi-source data ingestion schema, W3C PROV database models, Git blame analysis logic, "
                "and defined the ABAC security policy classification rules."
            ),
            "round2_deliverables": (
                "Deploy the working FastAPI backend, build the Git repository cloner and Slack message thread extractor, "
                "and implement the 1-Click Synthetic Benchmark dataset loader."
            ),
            "round3_deliverables": (
                "Implement cryptographic digital signature verification for handover approvals, execute the automated PyTest/Jest test suite, "
                "and conduct the formal security and data privacy audit."
            ),
            "competitor_analysis": (
                "Commercial search tools like Glean require complex enterprise OAuth installations that create an 'OAuth Wall' during hackathon evaluations. "
                "I engineered a Dual-Mode Ingestion Engine: live production connectors alongside a 1-click Synthetic Demo Playground that ingests sample repos in 2 seconds."
            ),
            "q1": "How does the Git Blame Orphan Code Miner calculate single-author risk?",
            "a1": (
                "The miner walks the Git commit history and computes line-by-line blame ratios per file. If a single contributor authored >75% of lines in a critical "
                "module and no other contributor has touched the file in 90 days, it is classified as 'Bus Factor = 1' and queued for leaver micro-interviewing."
            ),
            "q2": "How does your backend prevent confidential information leakage (Trust Requirement)?",
            "a2": (
                "Every ingested chunk is tagged with security classifications (e.g. CONFIDENTIAL_HR, INFRA_KEYS). Our ABAC filter inspects the requester's role "
                "before serializing JSON responses, guaranteeing restricted fields are permanently stripped before reaching the client-side."
            ),
            "q3": "Why choose FastAPI and SQLite/PostgreSQL over a complex distributed graph database like Neo4j for the hackathon?",
            "a3": (
                "Feasibility and zero setup friction! NetworkX in-memory DAGs combined with SQLite and PostgreSQL (pgvector) run instantaneously, require zero external "
                "daemon configuration, and allow judges to clone and run our entire repository with a single docker-compose or python main.py command."
            )
        }
    ]

    for member in members:
        build_member_pdf(member)

if __name__ == "__main__":
    generate_all_individual_pdfs()

