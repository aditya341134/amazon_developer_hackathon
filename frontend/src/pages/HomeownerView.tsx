import React, { useEffect, useMemo, useState } from "react";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorToast from "../components/ErrorToast";
import RunSelector from "../components/RunSelector";
import TimelinePanel from "../components/TimelinePanel";
import EvidenceDrawer from "../components/EvidenceDrawer";
import ChatBox from "../components/ChatBox";
import {
    DeviceSnapshot,
    ExplainResponse,
    Fix,
    ReplayResponse,
    RoutineSummary,
    ScenarioSummary,
    TimelineEvent
} from "../api/toolTypes";
import {
    applyFix,
    explain,
    getSnapshots,
    getTimeline,
    listRoutines,
    listScenarios,
    proposeFixes,
    replay,
    runScenario
} from "../api/client";

export default function HomeownerView() {
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
    const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

    const [explainData, setExplainData] = useState<ExplainResponse | null>(null);
    const [fixes, setFixes] = useState<Fix[]>([]);
    const [replayDiff, setReplayDiff] = useState<ReplayResponse["diff_summary"] | null>(null);

    const selectedEvent = useMemo(() => {
        if (!selectedEventId) return null;
        return timeline.find((e) => e.event_id === selectedEventId) ?? null;
    }, [timeline, selectedEventId]);

    // Derived Stepper status
    const step1Done = Boolean(runId);
    const step2Done = Boolean(explainData);
    const step3Done = Boolean(fixes.some((f) => f.applied));
    const step4Done = Boolean(replayDiff?.fixed);

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

        try {
            const sn = await getSnapshots(newRunId);
            setSnapshots(sn.snapshots);
        } catch {
            // snapshots optional
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
            const fx = await proposeFixes(runId);
            setFixes(fx.fixes);
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
            setFixes((prev) => prev.map((f) => (f.fix_id === fix_id ? { ...f, applied: true } : f)));
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

    return (
        <div style={{ display: "grid", gap: 20 }}>
            {/* Resolution Progress Stepper */}
            <div
                className="card-glass"
                style={{
                    padding: "14px 20px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 12
                }}
            >
                {[
                    { step: 1, title: "1. Run Automation", active: true, done: step1Done },
                    { step: 2, title: "2. Diagnose Cause", active: step1Done, done: step2Done },
                    { step: 3, title: "3. Apply Solution", active: step2Done, done: step3Done },
                    { step: 4, title: "4. Verify & Replay", active: step3Done, done: step4Done }
                ].map((s, idx, arr) => (
                    <React.Fragment key={s.step}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                            <div
                                style={{
                                    width: 28,
                                    height: 28,
                                    borderRadius: "50%",
                                    background: s.done
                                        ? "var(--success)"
                                        : s.active
                                        ? "var(--accent-primary)"
                                        : "rgba(255, 255, 255, 0.1)",
                                    color: "#fff",
                                    fontSize: 12,
                                    fontWeight: 800,
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    boxShadow: s.done || s.active ? "0 0 12px rgba(99, 102, 241, 0.35)" : "none"
                                }}
                            >
                                {s.done ? "✓" : s.step}
                            </div>
                            <span
                                style={{
                                    fontSize: 13,
                                    fontWeight: 600,
                                    color: s.done
                                        ? "var(--success-text)"
                                        : s.active
                                        ? "var(--text-primary)"
                                        : "var(--text-muted)"
                                }}
                            >
                                {s.title}
                            </span>
                        </div>
                        {idx < arr.length - 1 && (
                            <span style={{ color: "rgba(255, 255, 255, 0.15)", fontSize: 16 }}>➔</span>
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Top Control Grid */}
            <div className="grid-2col-responsive">
                {/* Scenario Launcher Card */}
                <div className="card-glass" style={{ padding: 20 }}>
                    <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 14, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                        <span>▶️</span> Run Routine Scenario
                    </div>

                    <RunSelector
                        routines={routines}
                        scenarios={scenarios}
                        selectedRoutineId={routineId}
                        selectedScenarioId={scenarioId}
                        onRoutineChange={(id) => refreshScenarios(id).catch((e) => setError(String(e)))}
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
                        {loading ? <LoadingSpinner size={20} /> : "⚡ Run Automation Scenario"}
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
                </div>

                {/* Homeowner Plain Explanation Card */}
                <div className="card-glass" style={{ padding: 20 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                        <div style={{ fontWeight: 800, fontSize: 16, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                            <span>💡</span> Homeowner Diagnosis
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
                            <div style={{ fontWeight: 800, color: replayDiff.fixed ? "var(--success-text)" : "var(--warning-text)", fontSize: 14.5, display: "flex", alignItems: "center", gap: 8 }}>
                                <span>{replayDiff.fixed ? "🎉 Problem Solved!" : "Replay Completed"}</span>
                            </div>
                            <div style={{ fontSize: 12.5, color: "#e2e8f0", marginTop: 4 }}>
                                Status: <b>{replayDiff.failure_before ?? "FAIL"}</b> ➔ <b>{replayDiff.failure_after ?? "PASS"}</b>. All smart home devices responded successfully.
                            </div>
                        </div>
                    )}

                    {!explainData ? (
                        <div style={{ color: "var(--text-muted)", fontSize: 13.5, padding: "36px 0", textAlign: "center", lineHeight: 1.5 }}>
                            Select a scenario on the left and click <b>Run Automation Scenario</b> to see a friendly diagnosis of what went wrong and how to fix it.
                        </div>
                    ) : (
                        <div style={{ display: "grid", gap: 14 }}>
                            {/* What happened card */}
                            <div style={{ background: "rgba(15, 23, 42, 0.7)", padding: 14, borderRadius: "var(--radius-md)", border: "1px solid var(--surface-border)" }}>
                                <div style={{ fontSize: 11.5, color: "var(--text-secondary)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 4 }}>
                                    What Happened:
                                </div>
                                <div style={{ fontWeight: 700, color: "#f8fafc", fontSize: 14.5, lineHeight: 1.4 }}>
                                    {explainData.homeowner.what}
                                </div>
                            </div>

                            {/* When and Why */}
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 12 }}>
                                <div style={{ background: "rgba(15, 23, 42, 0.7)", padding: 12, borderRadius: "var(--radius-md)", border: "1px solid var(--surface-border)" }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase" }}>When:</div>
                                    <div style={{ fontWeight: 600, color: "#e2e8f0", fontSize: 13, marginTop: 2 }}>{explainData.homeowner.when}</div>
                                </div>
                                <div style={{ background: "rgba(15, 23, 42, 0.7)", padding: 12, borderRadius: "var(--radius-md)", border: "1px solid var(--surface-border)" }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase" }}>Why It Failed:</div>
                                    <div style={{ fontWeight: 600, color: "#cbd5e1", fontSize: 13, marginTop: 2 }}>{explainData.homeowner.why}</div>
                                </div>
                            </div>

                            {/* Next Steps */}
                            <div style={{ background: "rgba(15, 23, 42, 0.7)", padding: 14, borderRadius: "var(--radius-md)", border: "1px solid var(--surface-border)" }}>
                                <div style={{ fontSize: 12, fontWeight: 700, color: "#cbd5e1", marginBottom: 6 }}>Recommended Next Steps:</div>
                                <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: "var(--text-secondary)", display: "grid", gap: 4 }}>
                                    {explainData.homeowner.next_steps.map((s, i) => (
                                        <li key={i}>{s}</li>
                                    ))}
                                </ul>
                            </div>

                            {/* Recommended Fixes */}
                            {fixes.length > 0 && (
                                <div style={{ borderTop: "1px solid var(--surface-border)", paddingTop: 14 }}>
                                    <div style={{ fontWeight: 700, fontSize: 13, color: "#cbd5e1", marginBottom: 10 }}>
                                        Recommended Auto-Fixes:
                                    </div>
                                    <div style={{ display: "grid", gap: 10 }}>
                                        {fixes.map((f) => (
                                            <div
                                                key={f.fix_id}
                                                style={{
                                                    background: "rgba(15, 23, 42, 0.7)",
                                                    border: f.applied ? "1px solid var(--success-border)" : "1px solid var(--surface-border)",
                                                    borderRadius: "var(--radius-md)",
                                                    padding: "12px 14px",
                                                    display: "flex",
                                                    justifyContent: "space-between",
                                                    alignItems: "center",
                                                    gap: 12
                                                }}
                                            >
                                                <div>
                                                    <div style={{ fontWeight: 700, fontSize: 13.5, color: "#f8fafc" }}>
                                                        <span className="badge badge-info" style={{ marginRight: 8, fontSize: 9.5 }}>
                                                            {f.mode.toUpperCase()}
                                                        </span>
                                                        {f.title}
                                                    </div>
                                                    <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4, lineHeight: 1.35 }}>
                                                        {f.why_it_works}
                                                    </div>
                                                </div>
                                                <button
                                                    disabled={!runId || loading || !f.safety.auto_apply_ok}
                                                    onClick={() => handleApplyFix(f.fix_id)}
                                                    className={f.applied ? "btn-success" : undefined}
                                                    style={{
                                                        padding: "7px 14px",
                                                        fontSize: 12.5,
                                                        flexShrink: 0
                                                    }}
                                                >
                                                    {f.safety.auto_apply_ok ? (f.applied ? "✓ Applied" : "✨ Apply Fix") : "Manual Fix"}
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Action Bar */}
                            <div style={{ display: "flex", gap: 10, marginTop: 6 }}>
                                <button
                                    disabled={!runId || loading}
                                    onClick={handleReplay}
                                    className="btn-success"
                                    style={{
                                        padding: "10px 18px",
                                        fontWeight: 700,
                                        fontSize: 13.5
                                    }}
                                >
                                    🔄 Replay to Validate Fix
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Timeline and Evidence Inspector */}
            <div className="grid-equal-responsive">
                <TimelinePanel
                    events={timeline}
                    selectedEventId={selectedEventId}
                    onSelectEvent={setSelectedEventId}
                />
                <EvidenceDrawer title="Event & Device Evidence" event={selectedEvent} snapshots={snapshots} />
            </div>

            {/* Interactive Chat Box Assistant */}
            <ChatBox
                disabled={!runId || loading}
                onExplain={handleExplain}
                onProposeFixes={handleProposeFixes}
                onReplay={handleReplay}
            />
        </div>
    );
}