export type NodeColor = {
  background: string;
  border: string;
  text: string;
  glow?: string;
};

export function statusColor(status?: string): NodeColor {
  if (status === "FAILED") {
    return {
      background: "rgba(239, 68, 68, 0.2)",
      border: "#ef4444",
      text: "#fca5a5",
      glow: "0 0 16px rgba(239, 68, 68, 0.4)"
    };
  }
  if (status === "SUCCESS") {
    return {
      background: "rgba(16, 185, 129, 0.2)",
      border: "#10b981",
      text: "#6ee7b7",
      glow: "0 0 16px rgba(16, 185, 129, 0.4)"
    };
  }
  if (status === "SKIPPED") {
    return {
      background: "rgba(100, 116, 139, 0.2)",
      border: "#64748b",
      text: "#94a3b8",
      glow: "none"
    };
  }
  return {
    background: "rgba(30, 41, 59, 0.85)",
    border: "rgba(255, 255, 255, 0.15)",
    text: "#f8fafc",
    glow: "none"
  };
}