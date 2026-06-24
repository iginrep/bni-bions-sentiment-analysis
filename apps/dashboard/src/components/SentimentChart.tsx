import React, { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { fetchLabeledStats } from "../lib/api";
import type { LabeledStats } from "../types/comment";

export function SentimentChart() {
  const [stats, setStats] = useState<LabeledStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    fetchLabeledStats()
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Gagal memuat statistik analisis sentimen.");
        setLoading(false);
      });
  }, []);

  if (!isClient) return null;

  if (loading) {
    return (
      <div className="glass-panel flex-center" style={{ height: "350px", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <p style={{ color: "var(--text-secondary)" }}>Memuat grafik sentimen...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="glass-panel flex-center" style={{ height: "350px", display: "flex", justifyContent: "center", alignItems: "center", padding: "20px" }}>
        <p style={{ color: "var(--color-negative)", textAlign: "center" }}>{error || "Tidak ada data statistik ditemukan."}</p>
      </div>
    );
  }

  // 1. Data untuk Pie Chart (Total Sentimen)
  const pieData = [
    { name: "Positif", value: stats.labels.Positif || 0, color: "var(--color-positive)" },
    { name: "Negatif", value: stats.labels.Negatif || 0, color: "var(--color-negative)" },
    { name: "Netral", value: stats.labels.Netral || 0, color: "var(--color-neutral)" },
  ].filter(item => item.value > 0);

  // 2. Data untuk Bar Chart (Platform breakdown)
  const barData = Object.entries(stats.platforms).map(([platform, counts]) => ({
    name: platform === "google_play" ? "Google Play" : platform === "app_store" ? "App Store" : platform === "youtube" ? "YouTube" : platform,
    Positif: counts.Positif || 0,
    Negatif: counts.Negatif || 0,
    Netral: counts.Netral || 0,
  }));

  const totalReviews = stats.total;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px", margin: "24px 0" }}>
      {/* Panel Kiri: Pie Chart Ringkasan Sentimen */}
      <div className="glass-panel" style={{ padding: "24px", display: "flex", flexDirection: "column", height: "380px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-primary)" }}>Distribusi Sentimen</h3>
          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)", background: "rgba(255,255,255,0.05)", padding: "4px 10px", borderRadius: "12px" }}>
            Total: {totalReviews}
          </span>
        </div>
        {pieData.length === 0 ? (
          <div style={{ flex: 1, display: "flex", justifyContent: "center", alignItems: "center" }}>
            <p style={{ color: "var(--text-secondary)" }}>Belum ada data ulasan terlabeli.</p>
          </div>
        ) : (
          <div style={{ flex: 1, display: "flex", position: "relative" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="45%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "var(--bg-secondary)",
                    borderColor: "var(--border-color)",
                    borderRadius: "8px",
                    color: "var(--text-primary)",
                  }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
            {/* Tengah Donut Chart */}
            <div style={{
              position: "absolute",
              top: "45%",
              left: "50%",
              transform: "translate(-50%, -60%)",
              textAlign: "center",
              pointerEvents: "none"
            }}>
              <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--text-primary)" }}>
                {totalReviews}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Ulasan
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Panel Kanan: Stacked Bar Chart Distribusi Platform */}
      <div className="glass-panel" style={{ padding: "24px", display: "flex", flexDirection: "column", height: "380px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "20px" }}>
          Sentimen per Platform
        </h3>
        {barData.length === 0 ? (
          <div style={{ flex: 1, display: "flex", justifyContent: "center", alignItems: "center" }}>
            <p style={{ color: "var(--text-secondary)" }}>Belum ada data ulasan terlabeli.</p>
          </div>
        ) : (
          <div style={{ flex: 1 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={barData}
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <XAxis
                  dataKey="name"
                  stroke="var(--text-secondary)"
                  fontSize={11}
                  tickLine={false}
                />
                <YAxis
                  stroke="var(--text-secondary)"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--bg-secondary)",
                    borderColor: "var(--border-color)",
                    borderRadius: "8px",
                    color: "var(--text-primary)",
                  }}
                />
                <Legend iconType="circle" />
                <Bar dataKey="Positif" stackId="a" fill="var(--color-positive)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Netral" stackId="a" fill="var(--color-neutral)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Negatif" stackId="a" fill="var(--color-negative)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
