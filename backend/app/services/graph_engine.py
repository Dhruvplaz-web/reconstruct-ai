"""
NetworkX Temporal Decision Directed Acyclic Graph (DAG) Engine
Assembles chronological nodes (commits, discussions, decisions, tasks)
and derivation edges into a serialized graph for visualization.
"""

from typing import List, Dict, Any
import networkx as nx
from ..models.schemas import DecisionNode, CommitEvent, DiscussionMessage, KanbanTask

class TemporalGraphEngine:
    """
    Constructs and serializes a time-aware Directed Acyclic Graph (DAG)
    representing the organizational provenance of a project handover.
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
                badge="Git Commit"
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
                badge="Discussion"
            )

        # 3. Add Decision Nodes
        for dec in decisions:
            node_id = f"dec:{dec.id}"
            graph.add_node(
                node_id,
                label=dec.title,
                full_title=dec.summary,
                status=dec.status,
                grounding_score=dec.grounding_score,
                has_contradiction=dec.has_contradiction,
                timestamp=dec.timestamp,
                node_type="decision",
                badge="Architecture Decision"
            )
            # Add edges from supporting citations
            for cit in dec.citations:
                if cit.source_type == "commit":
                    target_id = f"commit:{cit.uri.split('/')[-1]}"
                    if graph.has_node(target_id):
                        graph.add_edge(target_id, node_id, relation="prov:wasDerivedFrom")
                elif cit.source_type == "discussion":
                    # Extract message id from uri e.g. msg=msg-slack-001
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
                badge=f"Task ({t.stage})"
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
