"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Position,
  MarkerType
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import { DAGNode, DAGEdge } from "@/types";
import { MousePointerClick } from "lucide-react";

interface DAGVisualizerProps {
  nodes: DAGNode[];
  edges: DAGEdge[];
  onSelectCitation: (citationId: string) => void;
  heightClass?: string;
}

interface CustomNodeData extends Record<string, unknown> {
  citationId?: string;
  label: React.ReactNode;
}

const NODE_WIDTH = 210;
const NODE_HEIGHT = 72;

function getLayoutedElements(rawNodes: DAGNode[], rawEdges: DAGEdge[]) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: "TB", nodesep: 45, ranksep: 55 });

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
          <div className="p-2.5 text-left flex flex-col justify-between h-full select-none">
            <div className="flex items-center justify-between mb-1">
              <span
                className={`text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                  node.node_type === "commit"
                    ? "bg-slate-200 text-slate-800"
                    : node.node_type === "discussion"
                    ? "bg-purple-100 text-purple-700"
                    : node.node_type === "decision"
                    ? "bg-blue-100 text-blue-800 font-extrabold"
                    : "bg-emerald-100 text-emerald-800"
                }`}
              >
                {node.badge}
              </span>
              {node.grounding_score && (
                <span className="text-[8px] font-mono text-emerald-700 font-bold bg-emerald-50 px-1 py-0.5 rounded border border-emerald-200">
                  {(node.grounding_score * 100).toFixed(0)}% G(A)
                </span>
              )}
            </div>
            <p className="text-[11px] font-bold text-slate-900 leading-snug line-clamp-2">
              {node.label}
            </p>
            <div className="flex items-center justify-between mt-1 text-[9px] text-slate-500">
              <span className="truncate max-w-[120px]">{node.author || "Acme Contributor"}</span>
              <span className="text-blue-600 font-semibold hover:underline">Inspect &rarr;</span>
            </div>
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
        borderRadius: "10px",
        boxShadow: "0 2px 4px rgba(0,0,0,0.06)",
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
    labelStyle: { fontSize: "9px", fill: "#64748B", fontWeight: 600 },
    style: { stroke: e.relation === "revertedBy" ? "#E11D48" : "#2563EB", strokeWidth: 1.75 },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: e.relation === "revertedBy" ? "#E11D48" : "#2563EB",
      width: 14,
      height: 14
    }
  }));

  return { layoutedNodes, layoutedEdges };
}

export function DAGVisualizer({
  nodes,
  edges,
  onSelectCitation,
  heightClass = "h-[620px]"
}: DAGVisualizerProps) {
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
    <div className={`w-full ${heightClass} bg-slate-50/70 rounded-xl border border-slate-200 overflow-hidden relative shadow-inner`}>
      {/* Top Helper Banner */}
      <div className="absolute top-3 left-3 z-10 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-slate-200/80 shadow-xs flex items-center gap-2 text-xs text-slate-700 pointer-events-none">
        <MousePointerClick className="w-3.5 h-3.5 text-blue-600" />
        <span className="font-medium text-[11px]">
          Click any node to view grounded Git diff & chat discussion in NotebookLM drawer
        </span>
      </div>

      {/* W3C PROV Legend in bottom-right */}
      <div className="absolute bottom-3 right-3 z-10 bg-white/95 backdrop-blur-sm p-2 rounded-lg border border-slate-200 text-[10px] space-y-1 shadow-xs pointer-events-none">
        <span className="font-bold text-slate-700 block uppercase tracking-wider text-[9px]">
          W3C PROV-DM Relations
        </span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-blue-600 inline-block" />
          <span className="text-slate-600 font-mono">wasGeneratedBy</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-blue-600 border-b border-dashed inline-block" />
          <span className="text-slate-600 font-mono">wasDerivedFrom</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-rose-600 inline-block" />
          <span className="text-rose-700 font-mono">revertedBy (conflict)</span>
        </div>
      </div>

      <ReactFlow
        nodes={layoutedNodes}
        edges={layoutedEdges}
        onNodeClick={handleNodeClick}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.3}
        maxZoom={1.6}
      >
        <Background gap={14} size={1} color="#CBD5E1" />
        <Controls
          showInteractive={false}
          className="bg-white border border-slate-200 shadow-sm rounded-lg"
        />
        <MiniMap
          nodeStrokeWidth={2}
          zoomable
          pannable
          className="bg-white border border-slate-200 rounded-lg shadow-sm"
          style={{ width: 120, height: 80 }}
        />
      </ReactFlow>
    </div>
  );
}
