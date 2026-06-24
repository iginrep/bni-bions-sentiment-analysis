import React, { useEffect, useState } from "react";
import { fetchSchedules, toggleScheduleStatus } from "../lib/api";

interface ScheduleDoc {
  id: string;
  name: string;
  cron: {
    hour: number;
    minute: number;
  };
  timezone: string;
  isActive: boolean;
}

export function ScheduleManager() {
  const [schedules, setSchedules] = useState<ScheduleDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadSchedules = () => {
    fetchSchedules()
      .then((data) => {
        setSchedules(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Gagal memuat jadwal otomatis.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadSchedules();
  }, []);

  const handleToggle = (id: string, currentStatus: boolean) => {
    setActionLoading(id);
    const newStatus = !currentStatus;
    toggleScheduleStatus(id, newStatus)
      .then(() => {
        setSchedules((prev) =>
          prev.map((s) => (s.id === id ? { ...s, isActive: newStatus } : s))
        );
        setActionLoading(null);
      })
      .catch((err) => {
        alert("Gagal mengubah status jadwal.");
        setActionLoading(null);
      });
  };

  if (loading) {
    return <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>Memuat jadwal...</div>;
  }

  return (
    <div className="glass-panel" style={{ padding: "24px" }}>
      <h3 style={{ fontSize: "1.10rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
        Pengaturan Auto Run Pipeline
      </h3>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "20px", lineHeight: "1.4" }}>
        Kelola jadwal otomatisasi penarikan dan analisis data. Sistem terintegrasi dengan zona waktu Asia/Jakarta (WIB).
      </p>

      {error ? (
        <p style={{ color: "var(--color-negative)", fontSize: "0.9rem" }}>{error}</p>
      ) : schedules.length === 0 ? (
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>Tidak ada jadwal otomatisasi terdaftar.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {schedules.map((s) => {
            const formatTime = (hour: number, minute: number) => {
              const h = hour.toString().padStart(2, "0");
              const m = minute.toString().padStart(2, "0");
              return `${h}:${m}`;
            };

            return (
              <div
                key={s.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "16px",
                  background: "rgba(255,255,255,0.02)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "12px",
                  flexWrap: "wrap",
                  gap: "12px",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <div
                      style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        background: s.isActive ? "var(--color-positive)" : "var(--color-neutral)",
                        boxShadow: s.isActive ? "0 0 6px var(--color-positive)" : "none",
                      }}
                    ></div>
                    <span style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--text-primary)" }}>
                      {s.name}
                    </span>
                  </div>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                    Berjalan setiap hari pukul <strong style={{ color: "#E2E8F0" }}>{formatTime(s.cron.hour, s.cron.minute)} WIB</strong> ({s.timezone})
                  </p>
                </div>

                <button
                  disabled={actionLoading === s.id}
                  onClick={() => handleToggle(s.id, s.isActive)}
                  style={{
                    padding: "8px 16px",
                    background: s.isActive ? "rgba(239, 68, 68, 0.1)" : "rgba(16, 185, 129, 0.1)",
                    color: s.isActive ? "var(--color-negative)" : "var(--color-positive)",
                    border: s.isActive
                      ? "1px solid rgba(239, 68, 68, 0.2)"
                      : "1px solid rgba(16, 185, 129, 0.2)",
                    borderRadius: "10px",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    transition: "all 0.2s ease",
                    minWidth: "100px",
                  }}
                  onMouseEnter={(e) => {
                    if (s.isActive) {
                      e.currentTarget.style.background = "rgba(239, 68, 68, 0.2)";
                    } else {
                      e.currentTarget.style.background = "rgba(16, 185, 129, 0.2)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (s.isActive) {
                      e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)";
                    } else {
                      e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)";
                    }
                  }}
                >
                  {actionLoading === s.id
                    ? "Memproses..."
                    : s.isActive
                    ? "Matikan"
                    : "Aktifkan"}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
