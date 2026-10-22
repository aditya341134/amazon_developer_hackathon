import React, { useMemo } from "react";
import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";
import { WorkflowGraph } from "../api/toolTypes";
import { statusColor } from "./graphTypes";

type Props = {
  graph: WorkflowGraph | null;
  onSelectNode: (nodeId: string) => void;
};

export default function WorkflowGraphView({ graph, onSelectNode }: Props) {
  const nodes: Node[] = useMemo(() => {
    if (!graph) return [];
    return graph.nodes.map((n, idx) => {
      const st = graph.execution?.node_status?.[n.id]?.status;
      const c = statusColor(st);
      const isFailed = st === "FAILED";

      return {
        id: n.id,
        position: { x: (idx % 2) * 330 + 30, y: Math.floor(idx / 2) * 140 + 30 },
        data: {
          label: (
            <div style={{ textAlign: "left" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-secondary)" }}>
                  {n.kind}
                </span>
                {st && (
                  <span
                    style={{
                      fontSize: 9.5,
                      fontWeight: 800,
                      padding: "2px 7px",
                      borderRadius: "var(--radius-xs)",
                      background: c.border,
                      color: "#fff",
                      letterSpacing: "0.04em"
                    }}
                  >
                    {st}
                  </span>
                )}
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, color: c.text, lineHeight: 1.35 }}>
                {n.label}
              </div>
            </div>
          )
        },
        style: {
          background: c.background,
          border: `2px solid ${c.border}`,
          color: c.text,
          boxShadow: isFailed ? "0 0 20px rgba(239, 68, 68, 0.45)" : c.glow,
          width: 280,
          padding: "12px 16px",
          borderRadius: "var(--radius-md)",
          cursor: "pointer",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          transition: "transform 0.15s, box-shadow 0.15s"
        }
      };
    });
  }, [graph]);

  const edges: Edge[] = useMemo(() => {
    if (!graph) return [];
    return graph.edges.map((e, i) => {
      const label = e.when ? `when ${e.when}` : undefined;
      return {
        id: `e_${i}`,
        source: e.from,
        target: e.to,
        label,
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2.5 },
        labelStyle: { fill: "#cbd5e1", fontSize: 11, fontWeight: 700 }
      };
    });
  }, [graph]);

  if (!graph) {
    return (
      <div className="card-glass" style={{ padding: 36, textAlign: "center", color: "var(--text-muted)", fontSize: 13.5 }}>
        No DAG execution graph compiled yet. Run a routine scenario above to compile and execute the automation graph.
      </div>
    );
  }

  return (
    <div className="card-glass" style={{ height: 500, position: "relative", overflow: "hidden" }}>
      {/* Legend overlay */}
      <div
        style={{
          position: "absolute",
          top: 14,
          right: 14,
          zIndex: 10,
          display: "flex",
          gap: 10,
          background: "rgba(15, 23, 42, 0.88)",
          backdropFilter: "blur(8px)",
          padding: "6px 14px",
          borderRadius: "var(--radius-full)",
          border: "1px solid var(--surface-border)",
          fontSize: 11,
          fontWeight: 600
        }}
      >
        <span style={{ display: "flex", alignItems: "center", gap: 5, color: "var(--success-text)" }}>
          ● Success
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 5, color: "var(--danger-text)" }}>
          ● Failed
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 5, color: "var(--text-muted)" }}>
          ● Skipped
        </span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        onNodeClick={(_, node) => onSelectNode(node.id)}
      >
        <Background color="#1e293b" gap={18} />
        <Controls style={{ background: "rgba(15, 23, 42, 0.9)", border: "1px solid var(--surface-border)", borderRadius: "var(--radius-sm)" }} />
      </ReactFlow>
    </div>
  );
}