import os
import matplotlib
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), '.mpl_cache')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagrams():
    out_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(out_dir, exist_ok=True)

    # =========================================================================
    # DIAGRAM 1: The 5-Step Core Workflow Pipeline
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 2.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    steps = [
        ("01", "CONNECT", "Authorized Sources", "GitHub, Slack, Jira\n+ 1-Click Demo", "#2563EB", "#EFF6FF"),
        ("02", "RECONSTRUCT", "Causal DAG & State", "Entity Extraction\nOrphan Blame (>75%)", "#0D9488", "#F0FDFA"),
        ("03", "VERIFY", "Epistemic Grounding", "NLI Contradiction\nPROV URI Pointers", "#D97706", "#FFFBEB"),
        ("04", "REVIEW", "Human Gatekeeper", "60-Sec Sign-Off\nCrypto Approval Seal", "#DC2626", "#FEF2F2"),
        ("05", "HANDOVER", "Living Continuation", "Day 1-30 Kanban\nGrounded Q&A Chat", "#7C3AED", "#F5F3FF")
    ]

    box_width = 1.6
    box_height = 1.7
    start_x = 0.3
    y_pos = 0.4

    for i, (num, title, subtitle, details, stroke_col, bg_col) in enumerate(steps):
        x = start_x + i * 1.95
        
        # Main Card Box
        rect = patches.FancyBboxPatch(
            (x, y_pos), box_width, box_height,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.2, edgecolor=stroke_col, facecolor=bg_col
        )
        ax.add_patch(rect)

        # Header Badge Pill
        badge_rect = patches.FancyBboxPatch(
            (x + 0.1, y_pos + box_height - 0.35), box_width - 0.2, 0.26,
            boxstyle="round,pad=0.03,rounding_size=0.04",
            linewidth=0, facecolor=stroke_col
        )
        ax.add_patch(badge_rect)

        # Badge text
        ax.text(x + box_width / 2, y_pos + box_height - 0.22, f"STEP {num} : {title}",
                ha='center', va='center', fontsize=7.5, fontweight='bold', color='#FFFFFF', family='sans-serif')

        # Subtitle
        ax.text(x + box_width / 2, y_pos + box_height - 0.55, subtitle,
                ha='center', va='center', fontsize=7.2, fontweight='bold', color='#0F172A', family='sans-serif')

        # Details
        ax.text(x + box_width / 2, y_pos + 0.5, details,
                ha='center', va='center', fontsize=6.5, color='#475569', family='sans-serif', linespacing=1.3)

        # Arrow to next step
        if i < len(steps) - 1:
            arrow_x = x + box_width + 0.05
            ax.annotate(
                '', xy=(arrow_x + 0.25, y_pos + box_height / 2),
                xytext=(arrow_x, y_pos + box_height / 2),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2, mutation_scale=12)
            )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.5)
    
    path1 = os.path.join(out_dir, "workflow_pipeline.png")
    plt.tight_layout()
    plt.savefig(path1, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Generated:", path1)

    # =========================================================================
    # DIAGRAM 2: Platform Web Interface & Screen Architecture Blueprint
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(10, 3.8), dpi=300)
    fig2.patch.set_facecolor('#FFFFFF')
    ax2.set_facecolor('#FFFFFF')
    ax2.axis('off')

    # Browser Outer Frame
    frame = patches.FancyBboxPatch(
        (0.2, 0.2), 9.6, 3.4,
        boxstyle="round,pad=0.05,rounding_size=0.1",
        linewidth=1.2, edgecolor='#334155', facecolor='#0F172A'
    )
    ax2.add_patch(frame)

    # Window Title Bar
    ax2.text(0.5, 3.35, "Reconstruct.ai  |  Living Continuation Workspace (Production UI)",
             fontsize=7.5, fontweight='bold', color='#94A3B8', family='sans-serif')
    
    # Top Control Bar (Pills & Role Toggle)
    nav_bar = patches.Rectangle((0.4, 2.9), 9.2, 0.35, linewidth=0, facecolor='#1E293B')
    ax2.add_patch(nav_bar)
    ax2.text(0.6, 3.07, "● GitHub: Connected  ● Slack: Synced  ● Jira: Active", fontsize=6.5, fontweight='bold', color='#10B981', family='sans-serif')
    ax2.text(4.8, 3.07, "[Role Switcher: Junior Successor ▾ (ABAC Redaction Active)]", fontsize=6.5, fontweight='bold', color='#F59E0B', family='sans-serif')
    ax2.text(8.0, 3.07, "[1-Click Demo Playground]", fontsize=6.5, fontweight='bold', color='#38BDF8', family='sans-serif')

    # 3-Column Layout inside Web App
    # Column 1: Causal DAG & Orphan Code Radar
    col1 = patches.Rectangle((0.4, 0.4), 2.5, 2.4, linewidth=0.8, edgecolor='#334155', facecolor='#F8FAFC')
    ax2.add_patch(col1)
    ax2.text(0.5, 2.6, "TEMPORAL DECISION DAG", fontsize=6.8, fontweight='bold', color='#0F172A', family='sans-serif')
    ax2.text(0.5, 2.35, "• Oct 12: Auth Migrated to JWT [PR #41]\n• Oct 18: DB Pool Resized [Slack #arch]\n• Nov 02: Stripe Webhook Redesigned",
             fontsize=6.0, color='#334155', family='sans-serif', linespacing=1.4)
    ax2.text(0.5, 1.4, "ORPHAN CODE RADAR", fontsize=6.8, fontweight='bold', color='#DC2626', family='sans-serif')
    ax2.text(0.5, 1.15, "• auth/jwt_rotate.py: 88% Blame (Alex)\n• billing/reconcile.ts: 92% Blame (Alex)\n[Bus Factor = 1 Warning]",
             fontsize=6.0, color='#991B1B', family='sans-serif', linespacing=1.3)
    ax2.text(0.5, 0.55, "[Launch 60-Sec Leaver Sign-Off]", fontsize=6.2, fontweight='bold', color='#2563EB', family='sans-serif')

    # Column 2: Grounded Handover Briefing & Citation Chips
    col2 = patches.Rectangle((3.0, 0.4), 4.0, 2.4, linewidth=0.8, edgecolor='#334155', facecolor='#FFFFFF')
    ax2.add_patch(col2)
    ax2.text(3.15, 2.6, "EXECUTIVE HANDOVER BRIEFING", fontsize=6.8, fontweight='bold', color='#0F172A', family='sans-serif')
    brief_text = (
        "Core service auth was overhauled to eliminate race conditions.\n"
        "Tokens expire after 15m. [Citation: PR #412] [Verified: 98%]\n\n"
        "CONTRADICTION DETECTED:\n"
        "Slack #dev claims Redis cache was dropped, but commit\n"
        "4f8a continues to ping it. [Conflict Badge: 84% NLI Score]\n\n"
        "REDACTED UNDER ABAC:\n"
        "[Private Salary & Infra Production Keys Masked for Junior Role]"
    )
    ax2.text(3.15, 2.3, brief_text, fontsize=6.0, color='#334155', family='sans-serif', linespacing=1.35)
    ax2.text(3.15, 0.55, "Ask Handover: 'How do I run tests locally?' -> Cites exact Makefile lines", fontsize=5.8, color='#64748B', style='italic', family='sans-serif')

    # Column 3: Day 1-30 Onboarding Kanban
    col3 = patches.Rectangle((7.1, 0.4), 2.5, 2.4, linewidth=0.8, edgecolor='#334155', facecolor='#F8FAFC')
    ax2.add_patch(col3)
    ax2.text(7.2, 2.6, "DAY 1-30 ACTIONABLE KANBAN", fontsize=6.8, fontweight='bold', color='#0F172A', family='sans-serif')
    kanban_text = (
        "DAY 1: IMMEDIATE\n"
        "[ ] Rotate Stripe Webhook Secret\n"
        "[ ] Review Unmerged PR #214\n\n"
        "WEEK 1: HIGH CONTEXT\n"
        "[ ] Meet Sarah (External Vendor)\n"
        "[ ] Audit Redis Orphan Module\n\n"
        "DAY 30: AUTONOMOUS\n"
        "[ ] Deploy v2 Pipeline to Prod"
    )
    ax2.text(7.2, 2.3, kanban_text, fontsize=6.0, color='#1E293B', family='sans-serif', linespacing=1.3)

    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 3.8)

    path2 = os.path.join(out_dir, "platform_ui_wireframe.png")
    plt.tight_layout()
    plt.savefig(path2, bbox_inches='tight', dpi=300, facecolor=fig2.get_facecolor(), edgecolor='none')
    plt.close()
    print("Generated:", path2)

    # =========================================================================
    # DIAGRAM 3: W3C PROV-DM & NLI Verification Data Flow
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(10, 2.7), dpi=300)
    fig3.patch.set_facecolor('#FFFFFF')
    ax3.set_facecolor('#FFFFFF')
    ax3.axis('off')

    nodes = [
        ("INCOMING STREAMS", "Multi-Source Feed\n• Git Commits & Blame\n• Slack/Discord RFCs\n• Linear/Jira Issues", 0.4, 0.4, 2.0, 1.9, "#3B82F6", "#EFF6FF"),
        ("W3C PROV-DM GRAPH", "Formal Provenance\n• prov:Entity (Decision)\n• prov:Activity (Merge)\n• prov:Agent (Departing Dev)\n• prov:wasDerivedFrom (URI)", 2.8, 0.4, 2.3, 1.9, "#10B981", "#ECFDF5"),
        ("EPISTEMIC RADAR", "DeBERTa-v3 NLI Engine\n• Pairwise Cross-Encoding\n• Contradiction Flag (>70%)\n• Recency Decay Formulation\n• Confidence Thresholding", 5.5, 0.4, 2.3, 1.9, "#F59E0B", "#FFFBEB"),
        ("OUTPUT WORKSPACE", "Grounded Handover\n• Role-Specific Projection\n• Clickable Evidence Chips\n• Redacted Private Tokens\n• Actionable Next Steps", 8.2, 0.4, 1.5, 1.9, "#8B5CF6", "#F5F3FF")
    ]

    for title, desc, x, y, w, h, stroke, bg in nodes:
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.06,rounding_size=0.06",
            linewidth=1.1, edgecolor=stroke, facecolor=bg
        )
        ax3.add_patch(rect)
        ax3.text(x + w/2, y + h - 0.25, title, ha='center', va='center', fontsize=7.2, fontweight='bold', color=stroke, family='sans-serif')
        ax3.text(x + 0.1, y + h - 0.5, desc, ha='left', va='top', fontsize=6.2, color='#1E293B', family='sans-serif', linespacing=1.35)

    # Arrows between nodes
    arrows = [(2.42, 2.78), (5.12, 5.48), (7.82, 8.18)]
    for x1, x2 in arrows:
        ax3.annotate(
            '', xy=(x2, 1.35), xytext=(x1, 1.35),
            arrowprops=dict(arrowstyle="->", color="#64748B", lw=2, mutation_scale=12)
        )

    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 2.7)

    path3 = os.path.join(out_dir, "prov_nli_architecture.png")
    plt.tight_layout()
    plt.savefig(path3, bbox_inches='tight', dpi=300, facecolor=fig3.get_facecolor(), edgecolor='none')
    plt.close()
    print("Generated:", path3)

if __name__ == "__main__":
    generate_diagrams()

