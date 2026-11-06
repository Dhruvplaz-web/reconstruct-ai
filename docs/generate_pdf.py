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

# Ensure diagram assets exist
import generate_diagrams
generate_diagrams.generate_diagrams()

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

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
            self.drawString(40, letter[1] - 28, "RECONSTRUCT.AI  |  WE CODE CODERS  |  ROUND 1 PLAN")
            self.drawRightString(letter[0] - 40, letter[1] - 28, f"Page {self._pageNumber}")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, letter[1] - 32, letter[0] - 40, letter[1] - 32)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, letter[0] - 40, 36)

        self.drawString(40, 26, "RECONSTRUCT.AI  |  WE CODE CODERS  |  ROUND 1 PLAN")
        page_str = f"Page {self._pageNumber}"
        self.drawRightString(letter[0] - 40, 26, page_str)
        self.restoreState()


def build_pdf(filename="Reconstruct_AI_Deep_Research_Dossier.pdf"):
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Typography Styles matching Grounded Edition
    brand_style = ParagraphStyle(
        'BrandStyle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.HexColor('#64748B'), spaceAfter=4,
        textTransform='uppercase'
    )

    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor('#0F172A'), spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=16,
        textColor=colors.HexColor('#2563EB'), spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13,
        textColor=colors.HexColor('#0F172A'), spaceBefore=6, spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155'), spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletStyle', parent=body_style,
        leftIndent=12, firstLineIndent=-8, spaceAfter=2.5
    )

    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=9.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    fig_caption_style = ParagraphStyle(
        'FigCaption', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.2, leading=9.5,
        textColor=colors.HexColor('#2563EB'), alignment=1, spaceBefore=3, spaceAfter=5
    )

    note_box_style = ParagraphStyle(
        'NoteBox', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=11.5,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # =========================================================================
    # PAGE 1: Cover Page, Project Purpose & Consolidated Metadata
    # =========================================================================
    story.append(Paragraph("WE CODE CODERS HACKATHON &bull; ROUND 1 SUBMISSION", brand_style))
    story.append(Paragraph("RECONSTRUCT.AI", title_style))
    story.append(Paragraph("Converting Scattered Project Activity into Verifiable Handover Intelligence", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=14))

    story.append(Paragraph("Project purpose", h2_style))
    story.append(Paragraph(
        "Reconstruct.ai is a proposed handover-intelligence platform that gathers authorized project activity from code "
        "repositories, team discussions, issue trackers and project documents. It organizes that evidence into a "
        "time-aware, source-linked view of project decisions, unresolved work, ownership risks and next steps—so a "
        "successor can continue work with less guesswork.",
        body_style
    ))
    story.append(Spacer(1, 10))

    meta_data = [
        [Paragraph("<b>Team</b>", table_cell_bold), Paragraph("Reconstruct.ai", table_cell_style)],
        [Paragraph("<b>Institution</b>", table_cell_bold), Paragraph("JSPM’s Rajarshi Shahu College of Engineering (RSCOE), Pune", table_cell_style)],
        [Paragraph("<b>Team members</b>", table_cell_bold), Paragraph("Khushi Patil &bull; Dhruv Patil &bull; Yuvraj Kadam &bull; Nimisha Joshi", table_cell_style)],
        [Paragraph("<b>Repository</b>", table_cell_bold), Paragraph("<a href='https://github.com/Dhruvplaz-web/reconstruct-ai'><font color='#2563EB'><u>github.com/Dhruvplaz-web/reconstruct-ai</u></font></a>", table_cell_style)],
        [Paragraph("<b>Submission stage</b>", table_cell_bold), Paragraph("Round 1 — Plan and proposal", table_cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[1.8 * inch, 5.55 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # Clean Official Endorsement (replacing draft note)
    endorsement_text = (
        "<b>Official Submission Endorsement:</b> This consolidated proposal is prepared and submitted by Team Reconstruct.ai "
        "(JSPM RSCOE, Pune) for Round 1 of the We Code Coders Three-Round Challenge. All proposed workflows, data models, "
        "and milestone commitments have been aligned directly with the hackathon's required core workflow and evaluation criteria."
    )
    endorsement_table = Table([[Paragraph(endorsement_text, note_box_style)]], colWidths=[7.35 * inch])
    endorsement_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(endorsement_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: Section 1 (Understanding of the Problem) & Section 2 (Affected Users)
    # =========================================================================
    story.append(Paragraph("1. Understanding of the Problem", h1_style))
    story.append(Paragraph(
        "Project teams accumulate knowledge across many places: source-code commits, pull requests, issue trackers, "
        "chat discussions, design notes and individual working practices. A project handover becomes difficult when a "
        "key contributor leaves, graduates, changes responsibilities or becomes unavailable. The next person may "
        "inherit the code and task list but not the reasoning behind decisions, hidden dependencies, debugging steps, "
        "operational warnings or the history of unresolved issues.",
        body_style
    ))
    story.append(Paragraph(
        "The core problem is therefore not simply a lack of documentation. It is the fragmentation of project context and "
        "the difficulty of identifying which information is current, reliable, relevant and safe to share. Traditional "
        "handover notes are often manually prepared and can become stale; search tools can retrieve information but "
        "may not connect related events or clearly expose conflicting evidence.",
        body_style
    ))
    story.append(Paragraph(
        "Reconstruct.ai addresses this gap by converting authorized project traces into a structured, evidence-linked "
        "handover workspace. It is designed to assist human handover—not to replace contributor judgement or "
        "automatically declare every extracted statement true.",
        body_style
    ))

    story.append(Paragraph("Problem dimensions", h2_style))
    story.append(Paragraph("• <b>Scattered context:</b> important decisions and blockers are distributed across tools and conversations.", bullet_style))
    story.append(Paragraph("• <b>Knowledge concentration:</b> critical files or workflows may depend heavily on one contributor.", bullet_style))
    story.append(Paragraph("• <b>Unclear project state:</b> old discussions, current code and open tickets may not agree.", bullet_style))
    story.append(Paragraph("• <b>Successor uncertainty:</b> incoming contributors may not know what to inspect or whom to ask.", bullet_style))
    story.append(Paragraph("• <b>Trust and privacy:</b> handover material can contain confidential information that should not be visible to every role.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Scope boundary", h2_style))
    story.append(Paragraph(
        "The initial product focuses on software and project-team handovers, with GitHub/Git history and Slack-style "
        "exported discussions as the first practical sources. Jira/Linear and document connectors are planned "
        "extensions or optional inputs depending on time and access. The same approach may later support research "
        "labs, student organizations and open-source communities, but these are expansion contexts rather than "
        "separate MVP builds.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Affected Users", h1_style))
    user_data = [
        [Paragraph("USER GROUP", table_header_style), Paragraph("NEED / PAIN POINT", table_header_style), Paragraph("VALUE FROM RECONSTRUCT.AI", table_header_style)],
        [
            Paragraph("<b>Departing contributor</b>", table_cell_bold),
            Paragraph("Needs a focused way to transfer critical context without writing a long manual handover.", table_cell_style),
            Paragraph("Targeted questions based on detected ownership gaps and unresolved work; human review before sign-off.", table_cell_style)
        ],
        [
            Paragraph("<b>Incoming successor</b>", table_cell_bold),
            Paragraph("Needs to understand current architecture, decisions, risks and next actions.", table_cell_style),
            Paragraph("Source-linked briefing, timeline, unresolved items and Day 1–30 task list.", table_cell_style)
        ],
        [
            Paragraph("<b>Team lead / project manager</b>", table_cell_bold),
            Paragraph("Needs visibility into handover completeness, dependencies and knowledge concentration.", table_cell_style),
            Paragraph("Risk indicators, review status and a structured view of project continuity.", table_cell_style)
        ],
        [
            Paragraph("<b>Security / repository owner</b>", table_cell_bold),
            Paragraph("Needs to control which records and sensitive fields can be accessed.", table_cell_style),
            Paragraph("Permission-aware ingestion and server-side access filtering, subject to policy configuration.", table_cell_style)
        ]
    ]
    user_table = Table(user_data, colWidths=[1.55 * inch, 2.75 * inch, 3.05 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(user_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: Section 3 (Proposed Solution) & Section 4 (Complete Product Workflow)
    # =========================================================================
    story.append(Paragraph("3. Proposed Solution", h1_style))
    story.append(Paragraph(
        "Reconstruct.ai is a multi-source handover reconstruction system. It collects project evidence that the team is "
        "authorized to use, normalizes events into a common structure, links related decisions and artifacts over time, "
        "highlights ownership concentration and unresolved questions, and presents the result as an interactive "
        "continuation workspace.",
        body_style
    ))
    story.append(Paragraph("The platform is designed around five principles:", body_style))
    story.append(Paragraph("• <b>Evidence before assertion:</b> every generated handover claim should link back to one or more source records.", bullet_style))
    story.append(Paragraph("• <b>Time-aware context:</b> the system should show when information was created or updated and avoid treating old notes as current without review.", bullet_style))
    story.append(Paragraph("• <b>Uncertainty is visible:</b> missing support and possible contradictions should be flagged for human inspection.", bullet_style))
    story.append(Paragraph("• <b>Human confirmation:</b> departing contributors and project leads can correct or approve important handover details.", bullet_style))
    story.append(Paragraph("• <b>Least-privilege access:</b> sensitive content is filtered on the server according to the viewer’s permissions.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Differentiation", h2_style))
    story.append(Paragraph(
        "The proposed distinction is the combination of repository ownership analysis, cross-source timeline "
        "reconstruction, explicit evidence citations, uncertainty/contradiction review and successor-oriented tasks in "
        "one workflow. Existing documentation, search and code-guide tools can each address parts of this problem; "
        "Reconstruct.ai aims to connect those parts into a handover process. This is a product-positioning statement, "
        "not a claim that other products lack all of these capabilities.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. Complete Product Workflow", h1_style))

    # EMBED DIAGRAM: 5-Step Workflow Pipeline
    wf_img_path = os.path.join(assets_dir, "workflow_pipeline.png")
    if os.path.exists(wf_img_path):
        story.append(Image(wf_img_path, width=7.35 * inch, height=1.75 * inch))
        story.append(Paragraph("Figure 1: Complete 5-Step Operational Handover Workflow", fig_caption_style))

    story.append(Paragraph(
        "<b>1 — Connect:</b> A manager selects the project and departing contributor, authorizes the data sources and "
        "chooses either connected sources or a prepared synthetic demo dataset.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2 — Reconstruct:</b> The ingestion service parses commits, pull requests, issue records and permitted discussion "
        "exports. It extracts candidate decisions, dependencies, blockers and ownership patterns. Git blame "
        "concentration is treated as a risk signal, not proof that a person is the only one who understands a module.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3 — Verify:</b> The system links each candidate statement to its supporting source and timestamp. Where two "
        "statements appear inconsistent, an NLI model may flag a possible conflict; the interface presents the original "
        "evidence for review rather than deciding factual truth automatically.",
        body_style
    ))
    story.append(Paragraph(
        "<b>4 — Review:</b> The departing contributor or project lead reviews high-risk gaps and answers a small set of "
        "targeted questions. Corrections and approvals are recorded with their author and time.",
        body_style
    ))
    story.append(Paragraph(
        "<b>5 — Hand over:</b> The platform applies role-based/attribute-based access rules and generates a continuation "
        "workspace with a project summary, evidence timeline, unresolved tasks and suggested first-month actions.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: Section 5 (Main Planned Features & UI Wireframe Blueprint)
    # =========================================================================
    story.append(Paragraph("5. Main Planned Features", h1_style))
    feat_data = [
        [Paragraph("FEATURE", table_header_style), Paragraph("PLANNED CAPABILITY", table_header_style), Paragraph("USER BENEFIT", table_header_style)],
        [
            Paragraph("<b>Multi-source ingestion</b>", table_cell_bold),
            Paragraph("Import repository history and authorized discussion/ticket exports; provide a synthetic demo path for evaluation.", table_cell_style),
            Paragraph("Reduces manual collection and avoids requiring judges to connect personal accounts.", table_cell_style)
        ],
        [
            Paragraph("<b>Ownership concentration scan</b>", table_cell_bold),
            Paragraph("Analyze Git blame / commit history and flag files with high single-author contribution for review.", table_cell_style),
            Paragraph("Helps teams identify modules that may need knowledge transfer.", table_cell_style)
        ],
        [
            Paragraph("<b>Temporal evidence graph</b>", table_cell_bold),
            Paragraph("Represent people, files, decisions, issues and events with timestamped, traceable relationships.", table_cell_style),
            Paragraph("Shows how project context evolved and where a claim came from.", table_cell_style)
        ],
        [
            Paragraph("<b>Evidence-linked handover brief</b>", table_cell_bold),
            Paragraph("Generate structured summaries with source references and timestamps.", table_cell_style),
            Paragraph("Lets successors inspect the original evidence instead of relying only on generated text.", table_cell_style)
        ],
        [
            Paragraph("<b>Uncertainty / conflict review</b>", table_cell_bold),
            Paragraph("Use NLI as a signal to identify potentially inconsistent statements; route uncertain items to review.", table_cell_style),
            Paragraph("Makes disagreement visible and reduces silent merging of conflicting claims.", table_cell_style)
        ],
        [
            Paragraph("<b>Targeted leaver questions</b>", table_cell_bold),
            Paragraph("Generate a short set of questions from detected gaps, ownership concentration and unresolved items.", table_cell_style),
            Paragraph("Focuses contributor effort on the most important missing context.", table_cell_style)
        ],
        [
            Paragraph("<b>Continuation workspace</b>", table_cell_bold),
            Paragraph("Show a project overview, timeline/graph, citations, unresolved work and Day 1–30 tasks.", table_cell_style),
            Paragraph("Turns handover information into actionable next steps.", table_cell_style)
        ],
        [
            Paragraph("<b>Permission-aware view</b>", table_cell_bold),
            Paragraph("Apply server-side access policies and redact restricted fields before returning data.", table_cell_style),
            Paragraph("Supports safer sharing across roles; requires security testing and policy review.", table_cell_style)
        ]
    ]
    feat_table = Table(feat_data, colWidths=[1.65 * inch, 3.2 * inch, 2.5 * inch])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(feat_table)
    story.append(Spacer(1, 4))

    # EMBED DIAGRAM: Platform UI Blueprint & Wireframe
    ui_img_path = os.path.join(assets_dir, "platform_ui_wireframe.png")
    if os.path.exists(ui_img_path):
        story.append(Image(ui_img_path, width=7.35 * inch, height=2.6 * inch))
        story.append(Paragraph("Figure 2: Reconstruct.ai Production Web Interface: 3-Column Continuation Hub, Role Switcher & Grounded Citations", fig_caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: Section 6 (Proposed Technology Stack) & Section 7 (Team Responsibilities)
    # =========================================================================
    story.append(Paragraph("6. Proposed Technology Stack", h1_style))
    stack_data = [
        [Paragraph("LAYER", table_header_style), Paragraph("PROPOSED TECHNOLOGY", table_header_style), Paragraph("WHY IT FITS / IMPLEMENTATION NOTE", table_header_style)],
        [
            Paragraph("<b>Frontend</b>", table_cell_bold),
            Paragraph("Next.js 14, TypeScript, Tailwind CSS, Radix UI", table_cell_style),
            Paragraph("Responsive dashboard, accessible dialogs/drawers and reusable UI. Version should be aligned with the actual project setup before implementation.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend API</b>", table_cell_bold),
            Paragraph("Python, FastAPI, Pydantic, Uvicorn", table_cell_style),
            Paragraph("Python ecosystem supports repository parsing, NLP and graph processing; typed request/response schemas simplify API integration.", table_cell_style)
        ],
        [
            Paragraph("<b>Ingestion</b>", table_cell_bold),
            Paragraph("GitPython; GitHub API/PyGithub; JSON/Markdown parsers", table_cell_style),
            Paragraph("Start with repository cloning/history and local exported files. Live OAuth connectors are optional extensions, not a Round 2 dependency.", table_cell_style)
        ],
        [
            Paragraph("<b>Graph / storage</b>", table_cell_bold),
            Paragraph("NetworkX; SQLite for MVP; PostgreSQL for later deployment", table_cell_style),
            Paragraph("NetworkX is sufficient for a prototype graph. Start with a simple relational schema; add vector search only if required by tested workflows.", table_cell_style)
        ],
        [
            Paragraph("<b>AI / verification</b>", table_cell_bold),
            Paragraph("LLM-based structured extraction; Hugging Face DeBERTa-v3 NLI", table_cell_style),
            Paragraph("LLM output must be schema-validated and citation-grounded. NLI is a possible-conflict classifier, not a truth detector. Model/provider choice depends on availability and evaluation.", table_cell_style)
        ],
        [
            Paragraph("<b>Security / testing</b>", table_cell_bold),
            Paragraph("Server-side ABAC policy checks; PyTest; frontend tests", table_cell_style),
            Paragraph("Enforce least privilege before serialization; test access denial, redaction, secret handling and audit logging.", table_cell_style)
        ]
    ]
    stack_table = Table(stack_data, colWidths=[1.45 * inch, 2.25 * inch, 3.65 * inch])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("7. Team Responsibilities", h1_style))
    story.append(Paragraph(
        "The responsibilities below consolidate the four individual contributor dossiers. Each member owns a primary "
        "area while integration and review remain shared responsibilities.",
        body_style
    ))

    resp_data = [
        [Paragraph("MEMBER / ROLE", table_header_style), Paragraph("PRIMARY RESPONSIBILITIES", table_header_style), Paragraph("ROUND DELIVERABLES", table_header_style)],
        [
            Paragraph("<b>Khushi Patil</b><br/>Team Lead & Head of Research / Product Strategy", table_cell_bold),
            Paragraph("Problem validation, user taxonomy, research framing, competitor review, sprint planning, acceptance criteria, team coordination and submission compliance.", table_cell_style),
            Paragraph("R1: problem dossier, scope, evaluation plan and role coordination.<br/>R2: UAT scenarios, integration coordination and user feedback.<br/>R3: final walkthrough, product review and accessibility/security coordination.", table_cell_style)
        ],
        [
            Paragraph("<b>Dhruv Patil</b><br/>AI Development & Core Engineering Lead", table_cell_bold),
            Paragraph("Structured extraction design, prompt schemas, decision/dependency extraction, grounding and NLI conflict-signalling pipeline, synthetic benchmark design.", table_cell_style),
            Paragraph("R1: AI architecture, prompt/schema plan and benchmark specification.<br/>R2: extraction, citation linker and NLI prototype.<br/>R3: threshold evaluation, UI integration and hallucination guardrails.", table_cell_style)
        ],
        [
            Paragraph("<b>Yuvraj Kadam</b><br/>Lead Full-Stack Frontend & UI/UX Engineer", table_cell_bold),
            Paragraph("Next.js application, responsive layouts, continuation workspace, onboarding Kanban, citation sidecar, leaver review interface and accessibility.", table_cell_style),
            Paragraph("R1: wireframes, component plan and design tokens.<br/>R2: functional web client, demo interface and API integration.<br/>R3: graph visualization, responsive polish and keyboard accessibility.", table_cell_style)
        ],
        [
            Paragraph("<b>Nimisha Joshi</b><br/>Systems Backend, Data Ingestion & Security Architect", table_cell_bold),
            Paragraph("FastAPI services, repository parsing, Git ownership analysis, multi-source ingestion schemas, provenance records and server-side ABAC/redaction.", table_cell_style),
            Paragraph("R1: schemas, provenance model, ownership logic and policy design.<br/>R2: backend, repo ingestion, discussion export parser and demo loader.<br/>R3: automated tests, security review and approval-verification enhancement if feasible.", table_cell_style)
        ]
    ]
    resp_table = Table(resp_data, colWidths=[1.8 * inch, 2.75 * inch, 2.8 * inch])
    resp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(resp_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Shared responsibilities", h2_style))
    story.append(Paragraph("• All members participate in code review, integration testing, documentation and judge preparation.", bullet_style))
    story.append(Paragraph("• The team lead coordinates scope and milestones; technical leads remain accountable for their owned subsystems.", bullet_style))
    story.append(Paragraph("• The team will not describe planned features as completed until a working implementation and supporting evidence exist.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: Section 8 (Three-Round Plan) & Section 9 (Expected Impact & Metrics)
    # =========================================================================
    story.append(Paragraph("8. Three-Round Development Plan", h1_style))
    plan_data = [
        [Paragraph("ROUND", table_header_style), Paragraph("FOCUS", table_header_style), Paragraph("PLANNED DELIVERABLES", table_header_style), Paragraph("EXIT CHECK", table_header_style)],
        [
            Paragraph("<b>Round 1 — Plan</b>", table_cell_bold),
            Paragraph("Validate the problem, define MVP scope and design the architecture.", table_cell_style),
            Paragraph("Consolidated proposal; workflow and architecture; initial data schema; wireframes; synthetic test scenario; team responsibilities.", table_cell_style),
            Paragraph("All required proposal sections reviewed; scope and assumptions approved by team.", table_cell_style)
        ],
        [
            Paragraph("<b>Round 2 — Build</b>", table_cell_bold),
            Paragraph("Deliver a working end-to-end MVP using a controlled dataset.", table_cell_style),
            Paragraph("Repo ingestion; ownership scan; structured extraction; evidence citations; basic timeline/workspace; targeted review questions; demo dataset.", table_cell_style),
            Paragraph("A judge can load demo data and complete one handover flow end-to-end.", table_cell_style)
        ],
        [
            Paragraph("<b>Round 3 — Finish</b>", table_cell_bold),
            Paragraph("Improve reliability, usability, privacy and explainability.", table_cell_style),
            Paragraph("Conflict/uncertainty indicators; role-aware access controls; tests; responsive/accessibility improvements; walkthrough video and limitation notes.", table_cell_style),
            Paragraph("Demonstration is repeatable; core flows and access rules pass documented tests.", table_cell_style)
        ]
    ]
    plan_table = Table(plan_data, colWidths=[1.25 * inch, 1.8 * inch, 2.75 * inch, 1.55 * inch])
    plan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(plan_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("9. Expected Impact and Evaluation Metrics", h1_style))
    story.append(Paragraph(
        "The project’s impact will be evaluated through a small pilot rather than presented as a guaranteed percentage "
        "improvement. The team will compare a baseline handover process with a Reconstruct.ai-assisted handover "
        "using the same sample project and successor tasks.",
        body_style
    ))

    metric_data = [
        [Paragraph("METRIC", table_header_style), Paragraph("HOW TO MEASURE", table_header_style), Paragraph("SUCCESS SIGNAL", table_header_style)],
        [
            Paragraph("<b>Time to first meaningful task</b>", table_cell_bold),
            Paragraph("Measure elapsed time for a new contributor to identify and begin a predefined task using the baseline and the generated handover.", table_cell_style),
            Paragraph("Lower time with no loss in task correctness.", table_cell_style)
        ],
        [
            Paragraph("<b>Handover completeness</b>", table_cell_bold),
            Paragraph("Use a checklist of required decisions, dependencies, open issues, ownership and operational notes; count items supported by evidence.", table_cell_style),
            Paragraph("More checklist items are discoverable and source-linked.", table_cell_style)
        ],
        [
            Paragraph("<b>Ownership-risk coverage</b>", table_cell_bold),
            Paragraph("Compare manually identified critical files with files flagged by the ownership scan; inspect false positives and false negatives.", table_cell_style),
            Paragraph("Useful risk flags with explainable ownership evidence.", table_cell_style)
        ],
        [
            Paragraph("<b>Evidence traceability</b>", table_cell_bold),
            Paragraph("Audit a sample of generated claims and verify that each opens the correct source record and timestamp.", table_cell_style),
            Paragraph("Claims are reviewable and unsupported claims are clearly marked.", table_cell_style)
        ],
        [
            Paragraph("<b>Review effort</b>", table_cell_bold),
            Paragraph("Record time spent by the departing contributor reviewing and answering system-generated questions.", table_cell_style),
            Paragraph("Less effort than preparing a full manual handover, without overstating a fixed time target.", table_cell_style)
        ],
        [
            Paragraph("<b>Privacy / access control</b>", table_cell_bold),
            Paragraph("Run role-based test cases for allowed and denied records; inspect logs and API responses for restricted fields.", table_cell_style),
            Paragraph("No unauthorized disclosure in the defined test suite.", table_cell_style)
        ]
    ]
    metric_table = Table(metric_data, colWidths=[1.8 * inch, 3.25 * inch, 2.3 * inch])
    metric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 3))

    story.append(Paragraph("Impact statement", h2_style))
    story.append(Paragraph(
        "<b>Expected impact:</b> reduce avoidable context-search effort, make critical project knowledge easier to locate, "
        "surface ownership and continuity risks earlier, and provide successors with an actionable, evidence-linked "
        "starting point. The pilot will establish measured baselines before the team reports numerical improvement.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: Section 10 (Future Scope) & Section 11 (Team & Participant Details)
    # =========================================================================
    story.append(Paragraph("10. Future Scope", h1_style))
    story.append(Paragraph("• <b>Additional integrations:</b> GitLab, Jira/Linear, Discord and approved document repositories after the core GitHub/export workflow is stable.", bullet_style))
    story.append(Paragraph("• <b>Continuous decision capture:</b> optional bots or integrations that capture approved decisions as they occur, with explicit workspace consent and retention controls.", bullet_style))
    story.append(Paragraph("• <b>Enterprise identity and policy:</b> SSO, organization-managed roles, audit export and configurable retention policies.", bullet_style))
    story.append(Paragraph("• <b>Private deployment:</b> self-hosted inference and storage options for organizations with strict data residency requirements.", bullet_style))
    story.append(Paragraph("• <b>Research and education workflows:</b> adapt the evidence model for laboratory protocols, datasets, student clubs and open-source maintainer transitions.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("11. Complete Team and Participant Details", h1_style))
    team_full_data = [
        [Paragraph("NAME", table_header_style), Paragraph("ROLE", table_header_style), Paragraph("INSTITUTION", table_header_style), Paragraph("EMAIL AS REGISTERED", table_header_style)],
        [
            Paragraph("<b>Khushi Patil</b>", table_cell_bold),
            Paragraph("Team Lead & Head of Research / Product Strategy", table_cell_style),
            Paragraph("JSPM RSCOE, Pune", table_cell_style),
            Paragraph("khushi@reconstruct.ai", table_cell_style)
        ],
        [
            Paragraph("<b>Dhruv Patil</b>", table_cell_bold),
            Paragraph("AI Development & Core Engineering Lead", table_cell_style),
            Paragraph("JSPM RSCOE, Pune", table_cell_style),
            Paragraph("dhruvpatil4555@gmail.com", table_cell_style)
        ],
        [
            Paragraph("<b>Yuvraj Kadam</b>", table_cell_bold),
            Paragraph("Lead Full-Stack Frontend & UI/UX Engineer", table_cell_style),
            Paragraph("JSPM RSCOE, Pune", table_cell_style),
            Paragraph("yuvraj@reconstruct.ai", table_cell_style)
        ],
        [
            Paragraph("<b>Nimisha Joshi</b>", table_cell_bold),
            Paragraph("Systems Backend, Data Ingestion & Security Architect", table_cell_style),
            Paragraph("JSPM RSCOE, Pune", table_cell_style),
            Paragraph("nimisha@reconstruct.ai", table_cell_style)
        ]
    ]
    team_full_table = Table(team_full_data, colWidths=[1.3 * inch, 2.35 * inch, 1.7 * inch, 2.0 * inch])
    team_full_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(team_full_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Project repository:</b> <a href='https://github.com/Dhruvplaz-web/reconstruct-ai'><font color='#2563EB'><u>https://github.com/Dhruvplaz-web/reconstruct-ai</u></font></a>", body_style))
    story.append(Spacer(1, 10))

    # Formal Verification Sign-off Box (Cleaned, professional)
    signoff_text = (
        "<b>Submission Verification:</b> All participant identities, institution affiliations (JSPM RSCOE, Pune), "
        "and primary roles have been verified and confirmed across all project records. The official code repository is "
        "publicly accessible to the judges, and development will proceed strictly during the permitted hackathon build window."
    )
    signoff_table = Table([[Paragraph(signoff_text, note_box_style)]], colWidths=[7.35 * inch])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(signoff_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: Implementation Assumptions and Responsible-Use Notes & References
    # =========================================================================
    story.append(Paragraph("Implementation Assumptions and Responsible-Use Notes", h1_style))
    story.append(Paragraph(
        "To keep the proposal technically defensible, the following constraints apply to the design and evaluation:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Git blame concentration</b> (for example, a high single-author share) is a heuristic risk indicator. It does not prove "
        "that the contributor is the only person with relevant knowledge or that the file is operationally critical.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>A temporal relationship</b> between a chat message and a commit does not by itself prove causality. The graph "
        "should distinguish observed links from inferred links and show the evidence behind each inference.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Natural Language Inference</b> can classify pairs of text as potentially entailing, contradicting or being unrelated. It "
        "cannot establish which statement is factually correct; timestamps, source authority and human review remain "
        "necessary.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>A provenance model</b> such as W3C PROV-DM records entities, activities, agents and derivation relationships. It "
        "does not, by itself, make records immutable or cryptographically tamper-proof.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Access control</b> must be enforced on the backend before data is serialized or returned. UI masking alone is not a "
        "security boundary. The implementation requires negative tests for restricted access and secret leakage.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>All AI-generated claims</b> should include source references, be schema-validated and be marked uncertain when "
        "evidence is missing. The system must not invent missing handover details.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>The synthetic demo dataset</b> must contain fictional project data and secrets, not real employee or organizational "
        "information.",
        bullet_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Selected technical references", h2_style))
    story.append(Paragraph("• <b>W3C, PROV-DM: The PROV Data Model:</b> <a href='https://www.w3.org/TR/prov-dm/'><font color='#2563EB'><u>https://www.w3.org/TR/prov-dm/</u></font></a>", bullet_style))
    story.append(Paragraph("• <b>Nonaka, I. & Takeuchi, H., The Knowledge-Creating Company:</b> Foundational reference for the SECI knowledge-creation model.", bullet_style))
    story.append(Paragraph("• <b>Hugging Face model documentation for DeBERTa / NLI:</b> Model selection and evaluation should be confirmed against the chosen checkpoint and task.", bullet_style))
    story.append(Paragraph("• <b>IEEE Software / ACM Digital Library:</b> Empirical studies on turnover vulnerabilities, knowledge concentration, and documentation maintenance in agile teams.", bullet_style))
    story.append(Spacer(1, 14))

    # Formal Ending
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    story.append(Paragraph("<font color='#64748B'><b>End of Round 1 proposal &bull; Team Reconstruct.ai &bull; We Code Coders Three-Round Challenge</b></font>", ParagraphStyle('EndNote', parent=styles['Normal'], alignment=1, fontSize=8)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {pdf_path}")

    ok_path = os.path.join(os.path.dirname(__file__), "ok.pdf")
    shutil.copyfile(pdf_path, ok_path)
    print(f"Successfully copied perfected PDF to: {ok_path}")

if __name__ == "__main__":
    build_pdf()
