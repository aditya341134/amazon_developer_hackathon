import React, { useState } from "react";
import { DeviceSnapshot, TimelineEvent } from "../api/toolTypes";

type Props = {
    title: string;
    event: TimelineEvent | null;
    snapshots?: DeviceSnapshot[];
};

export default function EvidenceDrawer({ title, event, snapshots = [] }: Props) {
    const [activeTab, setActiveTab] = useState<"snapshot" | "payload">("snapshot");
    const [copied, setCopied] = useState(false);

    // Find relevant device snapshot if device_id is in event payload
    const eventDeviceId = (event?.payload?.device_id ?? event?.payload?.endpointId) as string | undefined;
    const matchingSnapshot = eventDeviceId ? snapshots.find((s) => s.device_id === eventDeviceId) : snapshots[0];

    const errorType = event?.payload?.errorType as string | undefined;
    const errMessage = event?.payload?.message as string | undefined;

    function handleCopyJson() {
        const payloadToCopy = event?.payload ?? matchingSnapshot;
        if (!payloadToCopy) return;
        navigator.clipboard.writeText(JSON.stringify(payloadToCopy, null, 2));
        setCopied(true);
        setTimeout(() => setCopied(false), 1800);
    }

    return (
        <div className="card-glass" style={{ padding: 18, display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <div style={{ fontWeight: 800, fontSize: 15, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                    <span>🔬</span>
                    <span>{title}</span>
                </div>
                {event && (
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <button
                            onClick={handleCopyJson}
                            style={{
                                padding: "3px 8px",
                                fontSize: 11,
                                background: copied ? "var(--success-bg)" : "rgba(15, 23, 42, 0.6)",
                                border: `1px solid ${copied ? "var(--success-border)" : "var(--surface-border)"}`,
                                color: copied ? "var(--success-text)" : "var(--text-secondary)"
                            }}
                        >
                            {copied ? "✓ Copied" : "📋 Copy JSON"}
                        </button>
                        <span className="badge badge-info">{event.kind}</span>
                    </div>
                )}
            </div>

            {!event ? (
                <div style={{ color: "var(--text-muted)", fontSize: 13, padding: "32px 0", textAlign: "center" }}>
                    Select an execution event or click a graph node to inspect live evidence.
                </div>
            ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                    {/* Event Timestamp and ID header */}
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>🕒 {event.ts}</span>
                        <code style={{ background: "rgba(15, 23, 42, 0.8)", padding: "2px 6px", borderRadius: "var(--radius-xs)" }}>
                            {event.event_id}
                        </code>
                    </div>

                    {/* Summary Header */}
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", lineHeight: 1.4 }}>
                        {event.summary}
                    </div>

                    {/* Error Banner if ErrorResponse */}
                    {errorType && (
                        <div
                            style={{
                                background: "var(--danger-bg)",
                                border: "1px solid var(--danger-border)",
                                borderRadius: "var(--radius-md)",
                                padding: "12px 14px"
                            }}
                        >
                            <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 700, color: "var(--danger-text)", fontSize: 13 }}>
                                <span>🚨 ErrorResponse:</span>
                                <span>{errorType}</span>
                            </div>
                            {errMessage && (
                                <div style={{ fontSize: 12, color: "#fca5a5", marginTop: 4, lineHeight: 1.4 }}>
                                    {errMessage}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Evidence Tab Buttons */}
                    <div style={{ display: "flex", gap: 8, borderBottom: "1px solid var(--surface-border)", paddingBottom: 8 }}>
                        <button
                            onClick={() => setActiveTab("snapshot")}
                            style={{
                                padding: "5px 12px",
                                fontSize: 12,
                                background: activeTab === "snapshot" ? "rgba(99, 102, 241, 0.25)" : "transparent",
                                border: activeTab === "snapshot" ? "1px solid rgba(99, 102, 241, 0.6)" : "1px solid transparent",
                                color: activeTab === "snapshot" ? "#fff" : "var(--text-secondary)"
                            }}
                        >
                            📡 Device Snapshot {matchingSnapshot ? `(${matchingSnapshot.device_id})` : ""}
                        </button>
                        <button
                            onClick={() => setActiveTab("payload")}
                            style={{
                                padding: "5px 12px",
                                fontSize: 12,
                                background: activeTab === "payload" ? "rgba(99, 102, 241, 0.25)" : "transparent",
                                border: activeTab === "payload" ? "1px solid rgba(99, 102, 241, 0.6)" : "1px solid transparent",
                                color: activeTab === "payload" ? "#fff" : "var(--text-secondary)"
                            }}
                        >
                            📦 Event Payload JSON
                        </button>
                    </div>

                    {/* Tab 1: Device Snapshot */}
                    {activeTab === "snapshot" && (
                        <div>
                            {matchingSnapshot ? (
                                <div
                                    style={{
                                        background: "rgba(15, 23, 42, 0.7)",
                                        border: "1px solid var(--surface-border)",
                                        borderRadius: "var(--radius-md)",
                                        padding: 14
                                    }}
                                >
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                                        <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-secondary)" }}>
                                            Device: <code style={{ color: "#e2e8f0" }}>{matchingSnapshot.device_id}</code>
                                        </span>
                                        <span
                                            className={`badge ${matchingSnapshot.endpoint_health === "OK" ? "badge-pass" : "badge-fail"}`}
                                        >
                                            {matchingSnapshot.endpoint_health}
                                        </span>
                                    </div>

                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, fontSize: 12 }}>
                                        <div style={{ background: "rgba(0,0,0,0.3)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--surface-border)" }}>
                                            <div style={{ color: "var(--text-secondary)", fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
                                                Actual Physical State
                                            </div>
                                            <pre style={{ margin: 0, color: "#38bdf8", fontSize: 11.5, overflow: "auto" }}>
                                                {JSON.stringify(matchingSnapshot.actual_state, null, 2)}
                                            </pre>
                                        </div>
                                        <div style={{ background: "rgba(0,0,0,0.3)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--surface-border)" }}>
                                            <div style={{ color: "var(--text-secondary)", fontSize: 11, fontWeight: 700, marginBottom: 4 }}>
                                                Reported Cloud State
                                            </div>
                                            <pre style={{ margin: 0, color: "#fbbf24", fontSize: 11.5, overflow: "auto" }}>
                                                {JSON.stringify(matchingSnapshot.reported_state, null, 2)}
                                            </pre>
                                        </div>
                                    </div>

                                    {matchingSnapshot.time_of_sample && (
                                        <div style={{ marginTop: 10, fontSize: 11.5, color: "var(--text-muted)" }}>
                                            Sample Timestamp: <code style={{ color: "#e2e8f0" }}>{matchingSnapshot.time_of_sample}</code>
                                        </div>
                                    )}

                                    {matchingSnapshot.declared_capabilities?.length > 0 && (
                                        <div style={{ marginTop: 10 }}>
                                            <div style={{ color: "var(--text-secondary)", fontSize: 11.5, fontWeight: 600 }}>
                                                Capabilities Validation:
                                            </div>
                                            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6 }}>
                                                {matchingSnapshot.declared_capabilities.map((c) => {
                                                    const supported = matchingSnapshot.actual_capabilities.includes(c);
                                                    return (
                                                        <span
                                                            key={c}
                                                            style={{
                                                                fontSize: 10.5,
                                                                padding: "3px 8px",
                                                                borderRadius: "var(--radius-xs)",
                                                                background: supported ? "var(--success-bg)" : "var(--danger-bg)",
                                                                color: supported ? "var(--success-text)" : "var(--danger-text)",
                                                                border: `1px solid ${supported ? "var(--success-border)" : "var(--danger-border)"}`,
                                                                fontWeight: 600
                                                            }}
                                                        >
                                                            {supported ? "✓" : "✗"} {c.replace("Alexa.", "")}
                                                        </span>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "16px 0" }}>
                                    No hardware snapshot linked to this event.
                                </div>
                            )}
                        </div>
                    )}

                    {/* Tab 2: Raw Event Payload */}
                    {activeTab === "payload" && (
                        <pre
                            style={{
                                background: "rgba(10, 15, 29, 0.95)",
                                color: "#e2e8f0",
                                padding: 14,
                                borderRadius: "var(--radius-md)",
                                overflow: "auto",
                                maxHeight: 320,
                                fontSize: 11.5,
                                margin: 0,
                                border: "1px solid var(--surface-border)",
                                lineHeight: 1.45
                            }}
                        >
                            {JSON.stringify(event.payload, null, 2)}
                        </pre>
                    )}
                </div>
            )}
        </div>
    );
}