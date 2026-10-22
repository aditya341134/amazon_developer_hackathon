import React, { useState, useRef, useEffect } from "react";

type Props = {
    disabled?: boolean;
    onExplain: () => Promise<void>;
    onProposeFixes: () => Promise<void>;
    onReplay: () => Promise<void>;
};

type ChatMessage = {
    id: string;
    sender: "user" | "doctor";
    text: string;
};

export default function ChatBox({
    disabled,
    onExplain,
    onProposeFixes,
    onReplay
}: Props) {
    const [text, setText] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: "msg_init",
            sender: "doctor",
            text: "Hello! I am your Routine Doctor assistant. You can ask me why an automation failed, request auto-fixes, or ask me to replay the scenario."
        }
    ]);
    const [busy, setBusy] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, busy]);

    async function executeAction(query: string, actionType: "explain" | "fix" | "replay") {
        if (disabled || busy) return;
        setBusy(true);

        const userMsg: ChatMessage = {
            id: `usr_${Date.now()}`,
            sender: "user",
            text: query
        };
        setMessages((prev) => [...prev, userMsg]);

        try {
            if (actionType === "explain") {
                await onExplain();
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `doc_${Date.now()}`,
                        sender: "doctor",
                        text: "Diagnosis updated! Review the explanation card and device evidence drawer for exact root cause details."
                    }
                ]);
            } else if (actionType === "fix") {
                await onProposeFixes();
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `doc_${Date.now()}`,
                        sender: "doctor",
                        text: "Fix proposals generated! Review the patches above. You can apply them with 1-click."
                    }
                ]);
            } else if (actionType === "replay") {
                await onReplay();
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `doc_${Date.now()}`,
                        sender: "doctor",
                        text: "Deterministic replay completed! Check the replay validation banner for before/after diff verification."
                    }
                ]);
            }
        } catch (e) {
            setMessages((prev) => [
                ...prev,
                {
                    id: `doc_${Date.now()}`,
                    sender: "doctor",
                    text: `Error executing command: ${String(e)}`
                }
            ]);
        } finally {
            setBusy(false);
        }
    }

    function handleSend() {
        if (!text.trim() || disabled || busy) return;
        const query = text.trim();
        setText("");

        const lower = query.toLowerCase();
        if (lower.includes("why") || lower.includes("explain") || lower.includes("fail") || lower.includes("reason")) {
            executeAction(query, "explain");
        } else if (lower.includes("fix") || lower.includes("repair") || lower.includes("patch") || lower.includes("suggest") || lower.includes("solve")) {
            executeAction(query, "fix");
        } else if (lower.includes("replay") || lower.includes("retry") || lower.includes("again") || lower.includes("run") || lower.includes("verify")) {
            executeAction(query, "replay");
        } else {
            executeAction(query, "explain");
        }
    }

    return (
        <div className="card-glass" style={{ padding: 18, display: "flex", flexDirection: "column", height: 400 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <div style={{ fontWeight: 800, fontSize: 15, color: "#f8fafc", display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 18 }}>💬</span>
                    <span>Interactive Routine Doctor Assistant</span>
                </div>
                <span className="badge badge-info" style={{ fontSize: 10 }}>Deterministic MCP</span>
            </div>

            {/* Conversation Log */}
            <div
                ref={scrollRef}
                style={{
                    flex: 1,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: 10,
                    padding: "8px 4px",
                    marginBottom: 12
                }}
            >
                {messages.map((m) => {
                    const isUser = m.sender === "user";
                    return (
                        <div
                            key={m.id}
                            style={{
                                alignSelf: isUser ? "flex-end" : "flex-start",
                                maxWidth: "86%",
                                background: isUser
                                    ? "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)"
                                    : "rgba(15, 23, 42, 0.8)",
                                color: isUser ? "#ffffff" : "#f1f5f9",
                                padding: "10px 14px",
                                borderRadius: isUser ? "14px 14px 2px 14px" : "14px 14px 14px 2px",
                                fontSize: 13,
                                lineHeight: 1.45,
                                border: isUser ? "none" : "1px solid var(--surface-border)",
                                boxShadow: "var(--shadow-sm)"
                            }}
                        >
                            {!isUser && (
                                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 4, display: "flex", alignItems: "center", gap: 5 }}>
                                    <span>🩺</span> Routine Doctor AI
                                </div>
                            )}
                            {m.text}
                        </div>
                    );
                })}
                {busy && (
                    <div
                        style={{
                            alignSelf: "flex-start",
                            color: "var(--text-secondary)",
                            fontSize: 12,
                            fontStyle: "italic",
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "6px 12px",
                            background: "rgba(15, 23, 42, 0.6)",
                            borderRadius: "var(--radius-md)",
                            border: "1px solid var(--surface-border)"
                        }}
                    >
                        <span style={{ animation: "spin 1s linear infinite" }}>⚙️</span> Routine Doctor is analyzing telemetry...
                    </div>
                )}
            </div>

            {/* Quick Prompt Chips */}
            <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
                <button
                    disabled={disabled || busy}
                    onClick={() => executeAction("Why did this routine fail?", "explain")}
                    className="btn-ghost"
                    style={{ fontSize: 11.5, padding: "5px 10px", borderRadius: "var(--radius-full)" }}
                >
                    🔍 Why did it fail?
                </button>
                <button
                    disabled={disabled || busy}
                    onClick={() => executeAction("Propose fixes for this failure", "fix")}
                    className="btn-ghost"
                    style={{ fontSize: 11.5, padding: "5px 10px", borderRadius: "var(--radius-full)" }}
                >
                    💡 Propose fixes
                </button>
                <button
                    disabled={disabled || busy}
                    onClick={() => executeAction("Replay scenario with patches", "replay")}
                    className="btn-ghost"
                    style={{ fontSize: 11.5, padding: "5px 10px", borderRadius: "var(--radius-full)" }}
                >
                    🔄 Replay run
                </button>
            </div>

            {/* Input Bar */}
            <div style={{ display: "flex", gap: 8 }}>
                <input
                    aria-label="Ask Routine Doctor a question"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder='Ask: "Why did it fail?", "Fix this", or "Replay"...'
                    style={{ flex: 1, fontSize: 13 }}
                    disabled={disabled || busy}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleSend();
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={disabled || busy || !text.trim()}
                    style={{ padding: "9px 18px", fontWeight: 700 }}
                >
                    Send
                </button>
            </div>
        </div>
    );
}