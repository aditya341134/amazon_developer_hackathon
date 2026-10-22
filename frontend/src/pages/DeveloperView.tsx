import React, { useEffect, useMemo, useState } from "react";
import RunSelector from "../components/RunSelector";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorToast from "../components/ErrorToast";
import TimelinePanel from "../components/TimelinePanel";
import EvidenceDrawer from "../components/EvidenceDrawer";
import ChatBox from "../components/ChatBox";
import WorkflowGraphView from "../graph/WorkflowGraphView";
import {
    DeviceSnapshot,
    Fix,
    ReplayResponse,
    RoutineSummary,
    ScenarioSummary,
    TimelineEvent,
    WorkflowGraph,
    ExplainResponse,
} from "../api/toolTypes";
import {
    applyFix,
    explain,
    getGraph,
    getSnapshots,
    getTimeline,
    listRoutines,
    listScenarios,
    proposeFixes,
    replay,
    runScenario,
} from "../api/client";

export default function DeveloperView() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [routines, setRoutines] = useState<RoutineSummary[]>([]);
    const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
    const [routineId, setRoutineId] = useState("r1");
    const [scenarioId, setScenarioId] = useState("s1_f1_unreachable");

    const [runId, setRunId] = useState<string | null>(null);
    const [runStatus, setRunStatus] = useState<"PASS" | "FAIL" | null>(null);
    const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
    const [snapshots, setSnapshots] = useState<DeviceSnapshot[]>([]);
    const [graph, setGraph] = useState<WorkflowGraph | null>(null);
    const [explainData, setExplainData] = useState<ExplainResponse | null>(null);
    const [fixes, setFixes] = useState<Fix[]>([]);
    const [replayDiff, setReplayDiff] = useState<ReplayResponse["diff_summary"] | null>(null);

    const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

    const selectedEvent = useMemo(() => {
        if (!selectedEventId) return null;
        return timeline.find((e) => e.event_id === selectedEventId) ?? null;
    }, [timeline, selectedEventId]);

    async function bootstrap() {
        setError(null);
        const r = await listRoutines();
        setRoutines(r.routines);
        const initialRoutine = r.routines.find((x) => x.routine_id === routineId)
            ? routineId
            : r.routines[0]?.routine_id ?? "r1";
        setRoutineId(initialRoutine);
        const s = await listScenarios(initialRoutine);
        setScenarios(s.scenarios);
        const initialScenario = s.scenarios.find((x) => x.scenario_id === scenarioId)
            ? scenarioId
            : s.scenarios[0]?.scenario_id ?? scenarioId;
        setScenarioId(initialScenario);
    }

    useEffect(() => {
        bootstrap().catch((e) => setError(String(e)));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function refreshScenarios(newRoutineId: string) {
        setError(null);
        setRoutineId(newRoutineId);
        const s = await listScenarios(newRoutineId);
        setScenarios(s.scenarios);
        setScenarioId(s.scenarios[0]?.scenario_id ?? "");
    }

    async function refreshRun(newRunId: string) {
        const t = await getTimeline(newRunId);
        setTimeline(t.events);
        setSelectedEventId(t.events[0]?.event_id ?? null);

        const g = await getGraph(newRunId);
        setGraph(g);

        try {
            const sn = await getSnapshots(newRunId);
            setSnapshots(sn.snapshots);
        } catch {
            // optional snapshots
        }

        const ex = await explain(newRunId);
        setExplainData(ex);

        const fx = await proposeFixes(newRunId);
        setFixes(fx.fixes);
    }

    async function handleRun() {
        setLoading(true);
        setError(null);
        setReplayDiff(null);
        try {
            const run = await runScenario({ routine_id: routineId, scenario_id: scenarioId });
            setRunId(run.run_id);
            setRunStatus(run.status);
            await refreshRun(run.run_id);
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }

    async function handleExplain() {
        if (!runId) return;
        setLoading(true);
        setError(null);
        try {
            setExplainData(await explain(runId));
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }

    async function handleProposeFixes() {
        if (!runId) return;
        setLoading(true);
        setError(null);
        try {
            setFixes((await proposeFixes(runId)).fixes);
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }

    async function handleApplyFix(fix_id: string) {
        if (!runId) return;
        setLoading(true);
        setError(null);
        try {
            await applyFix(runId, fix_id);
            setFixes((prev) =>
                prev.map((f) => (f.fix_id === fix_id ? { ...f, applied: true } : f))
            );
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }

    async function handleReplay() {
        if (!runId) return;
        setLoading(true);
        setError(null);
        try {
            const r = await replay(runId);
            setRunId(r.replay_run_id);
            setRunStatus(r.status);
            setReplayDiff(r.diff_summary);
            await refreshRun(r.replay_run_id);
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }

    function onSelectNode(nodeId: string) {
        if (!graph) return;
        const st = graph.execution?.node_status?.[nodeId];
        if (st?.event_id) setSelectedEventId(st.event_id);
    }

    return (
        <div style={{ display: "grid", gap: 20 }}>
            {/* Top Grid: Selector & Actions (Left), Workflow Graph & Fixes (Right) */}
            <div className="grid-2col-responsive">
                {/* Debug Controller Card */}
                <div className="card-glass" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 14, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                        <span>🛠️</span> Scenario Controller
                    </div>

                    <RunSelector
                        routines={routines}
                        scenarios={scenarios}
                        selectedRoutineId={routineId}
                        selectedScenarioId={scenarioId}
                        onRoutineChange={(id) =>
                            refreshScenarios(id).catch((e) => setError(String(e)))
                        }
                        onScenarioChange={(id) => setScenarioId(id)}
                    />

                    <button
                        onClick={handleRun}
                        disabled={loading || !routineId || !scenarioId}
                        style={{
                            width: "100%",
                            marginTop: 18,
                            padding: "12px 16px",
                            fontWeight: 700,
                            fontSize: 14.5
                        }}
                    >
                        {loading ? <LoadingSpinner size={20} /> : "⚡ Execute Scenario"}
                    </button>

                    <div style={{ marginTop: 14, fontSize: 12, color: "var(--text-secondary)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span>Run: <code>{runId ? runId.slice(0, 16) + "..." : "—"}</code></span>
                        {runStatus && (
                            <span className={`badge ${runStatus === "PASS" ? "badge-pass" : "badge-fail"}`}>
                                {runStatus}
                            </span>
                        )}
                    </div>

                    {error && <ErrorToast message={error} onClose={() => setError(null)} />}

                    {/* Developer Fix Actions Toolbar */}
                    <div style={{ marginTop: 18, borderTop: "1px solid var(--surface-border)", paddingTop: 14 }}>
                        <div style={{ fontWeight: 700, fontSize: 12.5, color: "var(--text-secondary)", marginBottom: 10 }}>
                            Direct Diagnostic Operations:
                        </div>
                        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                            <button
                                disabled={!runId || loading}
                                onClick={handleExplain}
                                style={{ padding: "8px 12px", background: "rgba(99, 102, 241, 0.2)", color: "#a5b4fc", fontSize: 12 }}
                            >
                                🔍 Explain Trace
                            </button>
                            <button
                                disabled={!runId || loading}
                                onClick={handleProposeFixes}
                                style={{ padding: "8px 12px", background: "rgba(16, 185, 129, 0.2)", color: "#6ee7b7", fontSize: 12 }}
                            >
                                💡 Propose Patches
                            </button>
                            <button
                                disabled={!runId || loading}
                                onClick={handleReplay}
                                style={{ padding: "8px 12px", background: "rgba(245, 158, 11, 0.2)", color: "#fcd34d", fontSize: 12 }}
                            >
                                🔄 Replay Run
                            </button>
                        </div>
                    </div>
                </div>

                {/* Workflow Graph & Classification Card */}
                <div style={{ display: "grid", gap: 16 }}>
                    <div className="card-glass" style={{ padding: 20 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                            <div style={{ fontWeight: 800, fontSize: 16, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                                <span>📊</span> DAG Workflow Execution Graph
                            </div>
                            {explainData?.classification && (
                                <span className={`badge ${runStatus === "PASS" ? "badge-pass" : "badge-fail"}`}>
                                    {explainData.classification}
                                </span>
                            )}
                        </div>

                        {/* Replay Diff Banner */}
                        {replayDiff && (
                            <div
                                style={{
                                    background: replayDiff.fixed ? "var(--success-bg)" : "var(--warning-bg)",
                                    border: `1px solid ${replayDiff.fixed ? "var(--success-border)" : "var(--warning-border)"}`,
                                    borderRadius: "var(--radius-md)",
                                    padding: "14px 16px",
                                    marginBottom: 16
                                }}
                            >
                                <div style={{ fontWeight: 800, color: replayDiff.fixed ? "var(--success-text)" : "var(--warning-text)", fontSize: 14, display: "flex", alignItems: "center", gap: 6 }}>
                                    <span>{replayDiff.fixed ? "🎉 Replay Validation: FAIL ➔ PASS" : "Replay Completed"}</span>
                                </div>
                                <div style={{ fontSize: 12.5, color: "#e2e8f0", marginTop: 4 }}>
                                    Failure Before: <b>{replayDiff.failure_before ?? "FAIL"}</b> | Failure After: <b>{replayDiff.failure_after ?? "PASS"}</b>
                                    {replayDiff.nodes_changed?.length > 0 && (
                                        <span style={{ marginLeft: 8, color: "var(--text-secondary)" }}>
                                            (Nodes changed: {replayDiff.nodes_changed.map((n) => `${n.node_id}: ${n.from}➔${n.to}`).join(", ")})
                                        </span>
                                    )}
                                </div>
                            </div>
                        )}

                        <WorkflowGraphView graph={graph} onSelectNode={onSelectNode} />

                        {explainData?.developer?.failed_node_id && (
                            <div style={{ marginTop: 12, fontSize: 13, color: "var(--danger-text)", background: "var(--danger-bg)", padding: "10px 14px", borderRadius: "var(--radius-md)", border: "1px solid var(--danger-border)" }}>
                                <b>Failed Node:</b> <code>{explainData.developer.failed_node_id}</code> — Click node in graph or event in timeline to inspect snapshot telemetry.
                            </div>
                        )}
                    </div>

                    {/* Developer Fixes Panel */}
                    <div className="card-glass" style={{ padding: 20 }}>
                        <div style={{ fontWeight: 800, fontSize: 15, color: "#f8fafc", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                            <span>🛠️</span> Code / Configuration Patches
                        </div>

                        {fixes.length === 0 ? (
                            <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
                                No fix patches required (the routine has either passed or not been executed).
                            </div>
                        ) : (
                            <div style={{ display: "grid", gap: 10 }}>
                                {fixes.map((f) => (
                                    <div
                                        key={f.fix_id}
                                        style={{
                                            background: "rgba(15, 23, 42, 0.7)",
                                            border: "1px solid var(--surface-border)",
                                            borderRadius: "var(--radius-md)",
                                            padding: 14
                                        }}
                                    >
                                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                                            <div style={{ fontWeight: 700, fontSize: 13.5, color: "#f8fafc" }}>
                                                <span className={`badge ${f.mode === "routine" ? "badge-info" : "badge-warn"}`} style={{ marginRight: 8, fontSize: 10 }}>
                                                    {f.mode.toUpperCase()}
                                                </span>
                                                {f.title}
                                            </div>
                                            <button
                                                disabled={!runId || loading || !f.safety.auto_apply_ok}
                                                onClick={() => handleApplyFix(f.fix_id)}
                                                className={f.applied ? "btn-success" : undefined}
                                                style={{
                                                    padding: "6px 14px",
                                                    fontSize: 12.5,
                                                    flexShrink: 0
                                                }}
                                            >
                                                {f.safety.auto_apply_ok ? (f.applied ? "✓ Applied" : "Apply Patch") : "Manual Guidance"}
                                            </button>
                                        </div>
                                        <div style={{ fontSize: 12.5, color: "var(--text-secondary)", marginTop: 6, lineHeight: 1.4 }}>
                                            {f.why_it_works}
                                        </div>

                                        <details style={{ marginTop: 10 }}>
                                            <summary style={{ cursor: "pointer", fontSize: 11.5, color: "#818cf8", fontWeight: 600 }}>
                                                Inspect Patch JSON
                                            </summary>
                                            <pre
                                                style={{
                                                    marginTop: 8,
                                                    background: "rgba(10, 15, 29, 0.95)",
                                                    color: "#38bdf8",
                                                    padding: 12,
                                                    borderRadius: "var(--radius-sm)",
                                                    fontSize: 11.5,
                                                    overflow: "auto",
                                                    border: "1px solid var(--surface-border)"
                                                }}
                                            >
                                                {JSON.stringify(f.patch, null, 2)}
                                            </pre>
                                        </details>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Timeline Panel and Trace Evidence Drawer */}
            <div className="grid-equal-responsive">
                <TimelinePanel
                    events={timeline}
                    selectedEventId={selectedEventId}
                    onSelectEvent={setSelectedEventId}
                />
                <EvidenceDrawer title="Directive & Device Evidence" event={selectedEvent} snapshots={snapshots} />
            </div>

            {/* Interactive Chat Assistant */}
            <ChatBox
                disabled={!runId || loading}
                onExplain={handleExplain}
                onProposeFixes={handleProposeFixes}
                onReplay={handleReplay}
            />
        </div>
    );
}
