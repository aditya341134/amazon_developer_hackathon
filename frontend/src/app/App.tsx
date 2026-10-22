import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

export default function App() {
    const loc = useLocation();
    const isHome = loc.pathname === "/";
    const isDev = loc.pathname === "/developer";

    return (
        <div style={{ maxWidth: 1360, margin: "0 auto", padding: "20px 24px", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            {/* Top Navigation Bar */}
            <header
                role="banner"
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 16,
                    padding: "16px 22px",
                    background: "rgba(17, 24, 39, 0.78)",
                    backdropFilter: "blur(16px)",
                    WebkitBackdropFilter: "blur(16px)",
                    borderRadius: "var(--radius-lg)",
                    border: "1px solid var(--surface-border)",
                    boxShadow: "var(--shadow-md)"
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div
                        style={{
                            width: 42,
                            height: 42,
                            borderRadius: "var(--radius-md)",
                            background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 22,
                            boxShadow: "0 0 20px rgba(99, 102, 241, 0.45)",
                            userSelect: "none"
                        }}
                    >
                        🩺
                    </div>
                    <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <span style={{ fontSize: 19, fontWeight: 800, letterSpacing: "-0.025em", color: "#f8fafc" }}>
                                Routine Doctor
                            </span>
                            <span className="badge badge-info" style={{ fontSize: 10, padding: "2px 8px" }}>
                                Alexa+ MCP
                            </span>
                        </div>
                        <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                            Smart Home Automation Failure Diagnosis • Fix Guidance • Deterministic Replay
                        </div>
                    </div>
                </div>

                <nav role="navigation" aria-label="Main Navigation" style={{ display: "flex", gap: 10 }}>
                    <Link
                        to="/"
                        aria-current={isHome ? "page" : undefined}
                        style={{
                            textDecoration: "none",
                            color: isHome ? "#ffffff" : "var(--text-secondary)",
                            padding: "9px 18px",
                            borderRadius: "var(--radius-md)",
                            fontSize: 13.5,
                            fontWeight: 600,
                            background: isHome ? "rgba(99, 102, 241, 0.22)" : "transparent",
                            border: isHome ? "1px solid rgba(99, 102, 241, 0.55)" : "1px solid transparent",
                            boxShadow: isHome ? "0 0 14px rgba(99, 102, 241, 0.25)" : "none",
                            transition: "all 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 8
                        }}
                    >
                        <span>🏡</span> Homeowner View
                    </Link>
                    <Link
                        to="/developer"
                        aria-current={isDev ? "page" : undefined}
                        style={{
                            textDecoration: "none",
                            color: isDev ? "#ffffff" : "var(--text-secondary)",
                            padding: "9px 18px",
                            borderRadius: "var(--radius-md)",
                            fontSize: 13.5,
                            fontWeight: 600,
                            background: isDev ? "rgba(99, 102, 241, 0.22)" : "transparent",
                            border: isDev ? "1px solid rgba(99, 102, 241, 0.55)" : "1px solid transparent",
                            boxShadow: isDev ? "0 0 14px rgba(99, 102, 241, 0.25)" : "none",
                            transition: "all 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 8
                        }}
                    >
                        <span>🛠️</span> Developer Debugger
                    </Link>
                </nav>
            </header>

            {/* Main Content Area */}
            <main role="main" style={{ marginTop: 22, flex: 1 }}>
                <Outlet />
            </main>

            {/* Accessible Footer */}
            <footer
                role="contentinfo"
                style={{
                    marginTop: 36,
                    padding: "18px 4px",
                    borderTop: "1px solid var(--surface-border)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 12,
                    fontSize: 12,
                    color: "var(--text-muted)"
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span>Backend Status:</span>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--success-text)", fontWeight: 600 }}>
                        <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--success)", display: "inline-block" }}></span>
                        Connected
                    </span>
                    <code style={{ background: "rgba(15, 23, 42, 0.85)", padding: "3px 8px", borderRadius: "var(--radius-xs)", color: "#cbd5e1" }}>
                        {import.meta.env.VITE_BACKEND_BASE_URL ?? "http://localhost:8000"}
                    </code>
                </div>
                <div style={{ display: "flex", gap: 14, color: "var(--text-secondary)" }}>
                    <span>JSON-RPC 2.0</span>
                    <span>•</span>
                    <span>OAuth 2.1 PKCE</span>
                    <span>•</span>
                    <span>RFC 9728 PRM</span>
                    <span>•</span>
                    <span>WCAG AA</span>
                </div>
            </footer>
        </div>
    );
}