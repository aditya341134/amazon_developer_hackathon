import React from "react";
import { RoutineSummary, ScenarioSummary } from "../api/toolTypes";

type Props = {
    routines: RoutineSummary[];
    scenarios: ScenarioSummary[];
    selectedRoutineId: string;
    selectedScenarioId: string;
    onRoutineChange: (routine_id: string) => void;
    onScenarioChange: (scenario_id: string) => void;
};

function getRoutineIcon(id: string): string {
    switch (id) {
        case "r1": return "🌙";
        case "r2": return "☀️";
        case "r3": return "🎬";
        case "r4": return "🛡️";
        default: return "⚡";
    }
}

export default function RunSelector({
    routines,
    scenarios,
    selectedRoutineId,
    selectedScenarioId,
    onRoutineChange,
    onScenarioChange
}: Props) {
    const selectedRoutine = routines.find((r) => r.routine_id === selectedRoutineId);
    const selectedScenario = scenarios.find((s) => s.scenario_id === selectedScenarioId);

    return (
        <div style={{ display: "grid", gap: 14 }}>
            <div>
                <label htmlFor="routine-select" style={{ fontSize: 12.5, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 6, display: "block" }}>
                    Select Smart Home Routine
                </label>
                <div style={{ position: "relative" }}>
                    <select
                        id="routine-select"
                        value={selectedRoutineId}
                        onChange={(e) => onRoutineChange(e.target.value)}
                        style={{
                            width: "100%",
                            paddingLeft: 34,
                            fontWeight: 600
                        }}
                    >
                        {routines.map((r) => (
                            <option key={r.routine_id} value={r.routine_id}>
                                {r.name} ({r.routine_id.toUpperCase()})
                            </option>
                        ))}
                    </select>
                    <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", fontSize: 15 }}>
                        {getRoutineIcon(selectedRoutineId)}
                    </span>
                </div>
                {selectedRoutine && (
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6, lineHeight: 1.4 }}>
                        {selectedRoutine.description}
                    </div>
                )}
            </div>

            <div>
                <label htmlFor="scenario-select" style={{ fontSize: 12.5, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 6, display: "block" }}>
                    Test Failure Scenario
                </label>
                <div style={{ position: "relative" }}>
                    <select
                        id="scenario-select"
                        value={selectedScenarioId}
                        onChange={(e) => onScenarioChange(e.target.value)}
                        style={{
                            width: "100%",
                            paddingLeft: 34,
                            fontWeight: 600
                        }}
                    >
                        {scenarios.map((s) => (
                            <option key={s.scenario_id} value={s.scenario_id}>
                                {s.name} ({s.scenario_id})
                            </option>
                        ))}
                    </select>
                    <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", fontSize: 14 }}>
                        🧪
                    </span>
                </div>
                {selectedScenario && (
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6, lineHeight: 1.4 }}>
                        {selectedScenario.description}
                    </div>
                )}
            </div>
        </div>
    );
}
