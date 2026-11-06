"""
NetworkX Temporal Decision Directed Acyclic Graph (DAG) Engine
Integrated with the official W3C PROV Python Library (trungdong/prov)
and Industry-Standard Architecture Decision Record (ADR) generators.
"""

from typing import List, Dict, Any
import networkx as nx
import json
from prov.model import ProvDocument
from ..models.schemas import DecisionNode, CommitEvent, DiscussionMessage, KanbanTask

class TemporalGraphEngine:
    """
    Constructs and serializes a time-aware Directed Acyclic Graph (DAG)
    and exports official W3C PROV-DM documents.
    """

    @staticmethod
    def build_graph(
        decisions: List[DecisionNode],
        commits: List[CommitEvent],
        discussions: List[DiscussionMessage],
        tasks: List[KanbanTask]
    ) -> Dict[str, Any]:
        """
        Builds a NetworkX DiGraph and exports nodes and edges formatted for frontend rendering.
        """
        graph = nx.DiGraph()

        # 1. Add Commit Nodes
        for c in commits:
            node_id = f"commit:{c.sha}"
            graph.add_node(
                node_id,
                label=f"Commit {c.sha[:7]}",
                full_title=c.message,
                author=c.author,
                timestamp=c.timestamp,
                node_type="commit",
                badge="Git Rollback" if "revert" in c.message.lower() else "Git Commit",
                citation_id=f"cit-commit-{c.sha}"
            )

        # 2. Add Discussion Nodes
        for d in discussions:
            node_id = f"disc:{d.id}"
            graph.add_node(
                node_id,
                label=f"Slack #{d.channel}",
                full_title=d.text,
                author=d.author,
                timestamp=d.timestamp,
                node_type="discussion",
                badge="Discussion",
                citation_id=f"cit-{d.id}"
            )

        # 3. Add Decision Nodes
        for dec in decisions:
            node_id = f"dec:{dec.id}"
            prim_citation_id = dec.citations[0].id if dec.citations else f"cit-dec-{dec.id}"
            graph.add_node(
                node_id,
                label=dec.title,
                full_title=dec.summary,
                status=dec.status,
                grounding_score=dec.grounding_score,
                has_contradiction=dec.has_contradiction,
                timestamp=dec.timestamp,
                node_type="decision",
                badge="Architecture Decision",
                citation_id=prim_citation_id
            )
            # Add derivation edges from supporting citations
            for cit in dec.citations:
                if cit.source_type == "commit":
                    target_id = f"commit:{cit.uri.split('/')[-1]}"
                    if graph.has_node(target_id):
                        graph.add_edge(target_id, node_id, relation="prov:wasDerivedFrom")
                elif cit.source_type == "discussion":
                    if "msg=" in cit.uri:
                        msg_id = cit.uri.split("msg=")[-1]
                        target_id = f"disc:{msg_id}"
                        if graph.has_node(target_id):
                            graph.add_edge(target_id, node_id, relation="prov:wasDerivedFrom")

        # 4. Add Kanban Task Nodes
        for t in tasks:
            node_id = f"task:{t.id}"
            graph.add_node(
                node_id,
                label=t.title,
                stage=t.stage,
                priority=t.priority,
                node_type="task",
                badge=f"Task ({t.stage})",
                citation_id=t.citation_id
            )
            if t.citation_id and "commit" in t.citation_id:
                sha = t.citation_id.split("-")[-1]
                target_id = f"commit:{sha}"
                if graph.has_node(target_id):
                    graph.add_edge(target_id, node_id, relation="verifiesTask")

        # Format output for frontend JSON
        nodes = []
        for n, data in graph.nodes(data=True):
            nodes.append({"id": n, **data})

        edges = []
        for u, v, data in graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "connectedTo")
            })

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "is_dag": nx.is_directed_acyclic_graph(graph),
            "nodes": nodes,
            "edges": edges
        }

    @staticmethod
    def export_w3c_prov_json(
        decisions: List[DecisionNode],
        commits: List[CommitEvent],
        discussions: List[DiscussionMessage]
    ) -> str:
        """
        Exports an official W3C PROV-DM Document using the trungdong/prov Python library.
        Returns serialized W3C PROV-JSON standard string.
        """
        doc = ProvDocument()
        doc.add_namespace("recon", "https://reconstruct.ai/ontology/prov#")
        doc.add_namespace("w3c", "http://www.w3.org/ns/prov#")

        # Agents
        agent_system = doc.agent("recon:software_agent_reconstruct_ai", {"prov:type": "prov:SoftwareAgent", "recon:name": "Reconstruct.ai Engine"})
        
        # Commits & Discussions as Entities
        for c in commits:
            entity_commit = doc.entity(f"recon:commit_{c.sha}", {
                "prov:type": "recon:GitCommit",
                "recon:message": c.message,
                "recon:author": c.author,
                "recon:timestamp": c.timestamp
            })
            author_agent = doc.agent(f"recon:author_{c.author.replace(' ', '_').lower()}")
            doc.wasAttributedTo(entity_commit, author_agent)

        # Decisions as Derived Entities
        for d in decisions:
            entity_dec = doc.entity(f"recon:decision_{d.id}", {
                "prov:type": "recon:ArchitectureDecision",
                "recon:title": d.title,
                "recon:grounding_score": d.grounding_score,
                "recon:status": d.status
            })
            doc.wasGeneratedBy(entity_dec, agent_system)

            for cit in d.citations:
                if cit.source_type == "commit":
                    sha = cit.uri.split("/")[-1]
                    doc.wasDerivedFrom(entity_dec, f"recon:commit_{sha}")

        return doc.serialize(format="json")

    @staticmethod
    def export_adr_markdown(decision: DecisionNode) -> str:
        """
        Exports an Architecture Decision Record (ADR) in Joel Parker Henderson standard format.
        """
        sources_list = "\n".join([f"- **{cit.title}**: `{cit.uri}` ({cit.author}, {cit.timestamp})" for cit in decision.citations])
        
        return f"""# ADR-{decision.id.upper()}: {decision.title}

## Status
**{decision.status}** (Epistemic Grounding Score G(A): {decision.grounding_score * 100:.1f}%)

## Context
{decision.summary}

## Decision & Rationale
{decision.rationale}

## Verifiable Sources (W3C PROV-DM wasDerivedFrom)
{sources_list}

## Consequences
- Primary maintainers: {', '.join(decision.authors)}
- Contradiction flagged: {'YES (Resolved via Leaver Review)' if not decision.quarantined_for_review and decision.has_contradiction else ('YES (Unresolved Risk)' if decision.has_contradiction else 'NO')}
- Date Recorded: {decision.timestamp}
"""
