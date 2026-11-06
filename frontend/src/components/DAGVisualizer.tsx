"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  Position,
  MarkerType
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import { DAGNode, DAGEdge } from "@/types";

interface DAGVisualizerProps {
  nodes: DAGNode[];
  edges: DAGEdge[];
  onSelectCitation: (citationId: string) => void;
}

interface CustomNodeData extends Record<string, unknown> {
  citationId?: string;
  label: React.ReactNode;
}

const NODE_WIDTH = 190;
const NODE_HEIGHT = 65;

function getLayoutedElements(rawNodes: DAGNode[], rawEdges: DAGEdge[]) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: "TB", nodesep: 35, ranksep: 50 });

  rawNodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  rawEdges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes: Node[] = rawNodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id) || { x: 0, y: 0 };
    return {
      id: node.id,
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2
      },
      data: {
        citationId: node.citation_id,
        label: (
          <div className="p-2 text-left">
            <div className="flex items-center justify-between mb-1">
              <span
                className={`text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded ${
                  node.node_type === "commit"
                    ? "bg-slate-200 text-slate-800"
                    : node.node_type === "discussion"
                    ? "bg-purple-100 text-purple-700"
                    : node.node_type === "decision"
                    ? "bg-blue-100 text-blue-700 font-extrabold"
                    : "bg-emerald-100 text-emerald-800"
                }`}
              >
                {node.badge}
              </span>
              {node.grounding_score && (
                <span className="text-[8px] font-mono text-emerald-700 font-bold">
                  {(node.grounding_score * 100).toFixed(0)}% G(A)
                </span>
              )}
            </div>
            <p className="text-[10px] font-bold text-slate-900 leading-tight truncate">{node.label}</p>
            {node.author && <p className="text-[9px] text-slate-500 mt-0.5 truncate">{node.author}</p>}
          </div>
        )
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      style: {
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        background: node.has_contradiction ? "#FFFBEB" : "#FFFFFF",
        border: node.has_contradiction ? "2px solid #F59E0B" : "1px solid #CBD5E1",
        borderRadius: "8px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
        cursor: "pointer"
      }
    };
  });

  const layoutedEdges: Edge[] = rawEdges.map((e, idx) => ({
    id: `edge-${idx}`,
    source: e.source,
    target: e.target,
    animated: e.relation.includes("wasDerivedFrom"),
    label: e.relation.replace("prov:", ""),
    labelStyle: { fontSize: "8px", fill: "#64748B", fontWeight: 600 },
    style: { stroke: e.relation === "revertedBy" ? "#E11D48" : "#2563EB", strokeWidth: 1.5 },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: e.relation === "revertedBy" ? "#E11D48" : "#2563EB",
      width: 14,
      height: 14
    }
  }));

  return { layoutedNodes, layoutedEdges };
}

export function DAGVisualizer({ nodes, edges, onSelectCitation }: DAGVisualizerProps) {
  const { layoutedNodes, layoutedEdges } = useMemo(() => {
    return getLayoutedElements(nodes, edges);
  }, [nodes, edges]);

  const handleNodeClick = (_: React.MouseEvent | unknown, node: Node) => {
    const directCitationId = (node.data as CustomNodeData)?.citationId;
    if (directCitationId) {
      onSelectCitation(directCitationId);
      return;
    }
    if (node.id.startsWith("commit:")) {
      const sha = node.id.replace("commit:", "");
      onSelectCitation(`cit-commit-${sha}`);
    } else if (node.id.startsWith("disc:")) {
      const discId = node.id.replace("disc:", "");
      onSelectCitation(`cit-${discId}`);
    } else if (node.id.startsWith("dec:")) {
      const decId = node.id.replace("dec:", "");
      onSelectCitation(`cit-${decId}`);
    }
  };

  return (
    <div className="w-full h-[580px] bg-slate-50/50 rounded-lg border border-slate-200 overflow-hidden relative">
      <ReactFlow
        nodes={layoutedNodes}
        edges={layoutedEdges}
        onNodeClick={handleNodeClick}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.4}
        maxZoom={1.5}
      >
        <Background gap={12} size={1} color="#CBD5E1" />
        <Controls showInteractive={false} className="bg-white border border-slate-200 shadow-sm" />
      </ReactFlow>
    </div>
  );
}
