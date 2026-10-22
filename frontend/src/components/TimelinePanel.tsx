import React, { useState } from "react";
import { TimelineEvent } from "../api/toolTypes";

type Props = {
    events: TimelineEvent[];
    selectedEventId: string | null;
    onSelectEvent: (eventId: string) => void;
};

function getKindIcon(kind: string): string {
    switch (kind) {
        case "SENSOR_EVENT": return "📡";
        case "DIRECTIVE": return "⚡";
        case "RESPONSE": return "📬";
        case "DECISION": return "⚖️";
        case "ASSERT": return "🎯";
        case "INFO": return "ℹ️";
        default: return "📝";
    }
}

function getKindBadge(kind: string): string {
    switch (kind) {
        case "DIRECTIVE": return "badge-info";
        case "RESPONSE": return "badge-warn";
        case "DECISION": return "badge-info";
        case "ASSERT": return "badge-pass";
        default: return "badge-info";
    }
}

export default function TimelinePanel({
    events,
    selectedEventId,
    onSelectEvent
}: Props) {
    const [filter, setFilter] = useState<string>("ALL");

    const filteredEvents = events.filter((e) => {
        if (filter === "ALL") return true;
        if (filter === "ERRORS") {
            return e.payload?.name === "ErrorResponse" || e.payload?.result === "FAIL";
        }
        return e.kind === filter;
    });

    return (
        <div className="card-glass" style={{ padding: 18, display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <div style={{ fontWeight: 800, fontSize: 15, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                    <span>⏱️</span>
                    <span>Execution Sequence</span>
                </div>
                <span className="badge badge-info" style={{ fontSize: 10 }}>{events.length} Events</span>
            </div>

            {/* Quick Kind Filter Pills */}
            <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
                {[
                    { id: "ALL", label: "All" },
                    { id: "ERRORS", label: "🚨 Errors" },
                    { id: "DIRECTIVE", label: "⚡ Directives" },
                    { id: "RESPONSE", label: "📬 Responses" },
                    { id: "ASSERT", label: "🎯 Assertions" }
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setFilter(tab.id)}
                        style={{
                            padding: "4px 10px",
                            fontSize: 11,
                            borderRadius: "var(--radius-full)",
                            background: filter === tab.id ? "var(--accent-primary)" : "rgba(15, 23, 42, 0.6)",
                            border: filter === tab.id ? "1px solid var(--accent-primary)" : "1px solid var(--surface-border)",
                            color: filter === tab.id ? "#fff" : "var(--text-secondary)",
                            boxShadow: filter === tab.id ? "0 0 10px rgba(99, 102, 241, 0.35)" : "none"
                        }}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Event List */}
            <div style={{ display: "grid", gap: 8, maxHeight: 440, overflowY: "auto", paddingRight: 4 }}>
                {filteredEvents.map((e, index) => {
                    const active = selectedEventId === e.event_id;
                    const isError = e.payload?.name === "ErrorResponse" || e.payload?.result === "FAIL";

                    return (
                        <div
                            key={e.event_id}
                            role="button"
                            tabIndex={0}
                            aria-pressed={active}
                            onClick={() => onSelectEvent(e.event_id)}
                            onKeyDown={(evt) => {
                                if (evt.key === "Enter" || evt.key === " ") {
                                    evt.preventDefault();
                                    onSelectEvent(e.event_id);
                                }
                            }}
                            style={{
                                textAlign: "left",
                                padding: "10px 14px",
                                borderRadius: "var(--radius-md)",
                                border: active
                                    ? "2px solid var(--accent-primary)"
                                    : isError
                                    ? "1px solid var(--danger-border)"
                                    : "1px solid var(--surface-border)",
                                background: active
                                    ? "rgba(99, 102, 241, 0.22)"
                                    : isError
                                    ? "rgba(239, 68, 68, 0.12)"
                                    : "rgba(15, 23, 42, 0.65)",
                                cursor: "pointer",
                                transition: "all 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
                                boxShadow: active ? "0 0 16px rgba(99, 102, 241, 0.35)" : "none",
                                position: "relative"
                            }}
                        >
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                                <span style={{ fontSize: 11, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 5 }}>
                                    <span style={{ fontWeight: 700, color: "var(--text-secondary)" }}>#{index + 1}</span>
                                    <span>{getKindIcon(e.kind)}</span>
                                    <span>{e.ts.split("T")[1]?.replace("Z", "") ?? e.ts}</span>
                                </span>
                                <span className={`badge ${isError ? "badge-fail" : getKindBadge(e.kind)}`} style={{ fontSize: 9.5 }}>
                                    {isError ? "FAILURE" : e.kind}
                                </span>
                            </div>
                            <div style={{ fontWeight: 600, fontSize: 13, color: isError ? "var(--danger-text)" : "#f1f5f9", lineHeight: 1.35 }}>
                                {e.summary}
                            </div>
                        </div>
                    );
                })}

                {filteredEvents.length === 0 && events.length > 0 && (
                    <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "28px 0" }}>
                        No events match the selected filter ({filter}).
                    </div>
                )}

                {events.length === 0 && (
                    <div style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", padding: "28px 0" }}>
                        No events recorded yet. Run a routine scenario above.
                    </div>
                )}
            </div>
        </div>
    );
}