import React from "react";

type Props = {
    message: string;
    onClose?: () => void;
};

export default function ErrorToast({ message, onClose }: Props) {
    if (!message) return null;

    return (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                background: "rgba(239, 68, 68, 0.12)",
                border: "1px solid rgba(239, 68, 68, 0.4)",
                color: "#b91c1c",
                padding: "10px 14px",
                borderRadius: 10,
                marginTop: 12,
                fontSize: 13,
                boxShadow: "0 2px 8px rgba(239, 68, 68, 0.15)",
                backdropFilter: "blur(4px)"
            }}
        >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>⚠️</span>
                <span>{message}</span>
            </div>
            {onClose && (
                <button
                    onClick={onClose}
                    style={{
                        background: "none",
                        border: "none",
                        color: "#b91c1c",
                        cursor: "pointer",
                        fontWeight: 700,
                        fontSize: 16,
                        padding: "0 4px"
                    }}
                >
                    ✕
                </button>
            )}
        </div>
    );
}
