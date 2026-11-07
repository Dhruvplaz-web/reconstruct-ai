# Reconstruct.ai — Handover Intelligence Platform

> **CodersInPune Hackathon (We Code Coders) — Round 2: The Build**  
> **Team:** TEAM DOMINATOR  
> **Institution:** JSPM’s Rajarshi Shahu College of Engineering (RSCOE), Pune  
> **Repository:** [https://github.com/Dhruvplaz-web/reconstruct-ai](https://github.com/Dhruvplaz-web/reconstruct-ai)  
> **Live Demo:** *(Deployed on Vercel — Zero sign-in required, opens directly in Incognito)*  

---

## Executive Summary

When core developers or student team members leave a project, critical context disappears with them. Traditional wikis decay within 30 days, while departing engineers facing a two-week notice have zero incentive to draft 30-page documents.

**Reconstruct.ai** is an automated handover-intelligence platform that ingests project traces (Git commit histories, pull requests, and chat discussions), reconstructs a temporal provenance DAG, detects architectural contradictions using local NLI cross-encoders, calculates bus-factor ownership risks, and facilitates a 60-second micro-review for the departing contributor before cryptographically signing the handover dossier.

```
       [ Git Commits + Pull Requests + Chat Traces ]
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │           RECONSTRUCT.AI PIPELINE            │
     ├──────────────────────────────────────────────┤
     │  1. ICSE DOA Ownership & Bus Factor = 1      │
     │  2. W3C PROV-DM Temporal Decision DAG        │
     │  3. HuggingFace NLI Pairwise Contradiction   │
     │  4. NIST SP 800-162 ABAC Secret Scrubber     │
     │  5. RFC 8032 Ed25519 Digital Signature       │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │            INTERACTIVE WORKSPACE             │
     ├──────────────────────┬───────────────────────┤
     │ 60s Leaver Modal     │ Actionable Day 1-30   │
     │ Resolves 2-week      │ Onboarding Kanban &   │
     │ notice paradox       │ Citation Sidecar      │
     └──────────────────────┴───────────────────────┘
```

---

## Team Dominator

| Name | Role | Responsibilities |
| :--- | :--- | :--- |
| **Dhruv Patil** *(Team Leader)* | Full-Stack Systems Architect | End-to-end integration, FastAPI services, Next.js UI, deployment |
| **Khushi Patil** | Product Strategy & UX Lead | Handover workflow, 60s micro-review UX, Day 1–30 Kanban design |
| **Yuvraj Kadam** | Backend & Graph Engineer | Git mining, ICSE DOA Bus Factor, W3C PROV-DM DAG topology |
| **Nimisha Joshi** | AI & Security Specialist | HuggingFace NLI Radar, RFC 8032 Ed25519 crypto, NIST ABAC filters |

---

## Key Features Implemented in Round 2

### 1. ICSE Degree of Authorship (DOA) & Bus Factor = 1 Analysis
* Implements academic Degree of Authorship ($DOA = 3.293 + 1.098 \cdot FA + 0.164 \cdot DL - 0.321 \cdot \ln(1 + AC)$) to calculate true code ownership.
* Filters out whitespace/formatting noise (Prettier, Black, mass renames) so cosmetic editors are never misclassified as architecture owners.
* Automatically flags critical files with single-developer ownership ($>75\%$) as high-risk orphans.

### 2. W3C PROV-DM Temporal Decision DAG
* Reconstructs project decisions into a directed acyclic graph adhering to the **W3C PROV-DM** provenance specification.
* Explicitly tracks `prov:wasGeneratedBy`, `prov:wasDerivedFrom`, and `prov:wasInformedBy` relationships.
* Visualized via an interactive `@xyflow/react` (React Flow) canvas with layout-preserving node positioning and dynamic citation anchoring.

### 3. HuggingFace NLI Contradiction Radar Engine
* Runs local cross-encoder / semantic embedding models (`sentence-transformers/all-MiniLM-L6-v2`) in under 50ms on CPU with zero external API calls and zero rate limits.
* Evaluates pairwise semantic contradictions across commit diffs and chat debates using a 35+ category architectural conflict taxonomy (e.g., JWT vs. Redis sessions, PostgreSQL vs. DynamoDB, REST vs. gRPC).
* Formulates a mathematically grounded confidence score factoring semantic conflict probability, temporal recency decay ($\Delta t$), and multi-source corroboration.

### 4. RFC 8032 Ed25519 Cryptographic Signatures
* Generates an immutable, tamper-proof SHA-256 fingerprint of the entire handover workspace state.
* Signs the digest using asymmetric **RFC 8032 Ed25519** public/private key pairs.
* Provides a 1-click verification badge allowing auditors to mathematically confirm zero post-handover state tampering.

### 5. NIST SP 800-162 Attribute-Based Access Control (ABAC)
* Enforces strict server-side redaction before JSON serialization (never relies on cosmetic CSS or DOM masking).
* Evaluates requester attributes (Role, Clearance Level, Department) against target resource sensitivity (`CONFIDENTIAL_ARCH`, `RESTRICTED_AUTH`).
* Deeply scrubs API keys (`sk_test_*`, Stripe, AWS, JWT secrets) from contradiction claims, commit messages, and chat excerpts for `JUNIOR_SUCCESSOR` views.

### 6. The 60-Second Leaver Micro-Review
* Resolves the "Two-Week Notice Paradox" by presenting departing developers with 3 targeted, high-impact confirmation prompts instead of demanding long documentation.
* Saves responses directly to the atomic JSON session store (`StateStore`).

### 7. Actionable Day 1–30 Onboarding Kanban & Citation Sidecar
* Successors receive pre-computed, role-tailored action cards categorized into Day 1 (Setup & Auth), Day 7 (Architecture & High-Risk Files), and Day 30 (Feature Ownership).
* NotebookLM-style slide-out sidecar displays verified source diffs, timestamps, and commit hashes on click.

---

## Tech Stack & Architecture

- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, `@xyflow/react` (React Flow), Lucide Icons, Radix UI.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2 schemas, NetworkX (graph topology), PyCryptodome / cryptography (Ed25519).
- **AI / NLP:** HuggingFace Sentence-Transformers (`all-MiniLM-L6-v2`), local PyTorch CPU inference.
- **Data & Security:** Atomic session persistence (`StateStore` with atomic file swap), NIST SP 800-162 ABAC filtering engine.
- **Testing & Tooling:** PyTest (21/21 passing automated tests), pnpm build (100% strict TypeScript compliance).

---

## Quickstart & Local Installation

### Prerequisites
* Python 3.11+
* Node.js 18+ and pnpm

### 1-Command Startup
```bash
# Clone the repository
git clone https://github.com/Dhruvplaz-web/reconstruct-ai.git
cd reconstruct-ai

# Launch both FastAPI backend (port 8000) and Next.js frontend (port 3000)
python run_app.py
```
`run_app.py` automatically checks and reclaims ports 8000 and 3000 from stale background processes, installs dependencies if missing, and gracefully terminates both process trees upon exit (`Ctrl+C`).

### Running Backend Unit & Integration Tests
```bash
pytest backend/tests/test_backend.py -v
# Output: 21 passed in ~85s (100% green)
```

### Running Frontend Production Build
```bash
cd frontend
pnpm install
pnpm run build
# Output: Compiled successfully, zero lint warnings, 5/5 static routes prerendered
```

---

## Round 3 Roadmap (Planned Major Improvements)

1. **Continuous GitHub Action & PR Review Handover Bot:** Real-time truck factor monitoring on every pull request, warning maintainers before code silos form.
2. **Automated LLM Code Synthesis & Test Scaffolding for Orphan Files:** Automated generation of regression test suites and type docstrings for high-risk files left with Bus Factor = 1.
3. **Enterprise Multi-Tenant & HSM-Backed Audit Vault:** AWS KMS / HashiCorp Vault hardware-backed key signing with Sigstore/Cosign append-only transparency log.

---

## License
MIT License. Developed for CodersInPune Hackathon 2026.
