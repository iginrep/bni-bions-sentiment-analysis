import React, { useEffect, useState } from "react";
import Head from "next/head";
import dynamic from "next/dynamic";
import { CommentTable } from "../components/CommentTable";
import { ScheduleManager } from "../components/ScheduleManager";
import { fetchLabeledComments, fetchLabeledStats } from "../lib/api";
import type { LabeledComment, LabeledStats } from "../types/comment";

const SentimentChart = dynamic(
  () => import("../components/SentimentChart").then((mod) => mod.SentimentChart),
  { ssr: false }
);

export default function Home() {
  const [comments, setComments] = useState<LabeledComment[]>([]);
  const [stats, setStats] = useState<LabeledStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [extracting, setExtracting] = useState(false);
  const [labeling, setLabeling] = useState(false);
  const [actionMessage, setActionMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const loadDashboardData = () => {
    Promise.all([fetchLabeledComments(), fetchLabeledStats()])
      .then(([commentsData, statsData]) => {
        setComments(commentsData);
        setStats(statsData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Gagal memuat data dashboard.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleExtract = async () => {
    setExtracting(true);
    setActionMessage(null);
    try {
      const { triggerExtraction } = await import("../lib/api");
      const res = await triggerExtraction();
      setExtracting(false);
      if (res.status === "success") {
        setActionMessage({
          text: `Sukses menarik data baru! Ditemukan ${res.count} ulasan baru yang berhasil disimpan.`,
          type: "success",
        });
        loadDashboardData();
      } else {
        setActionMessage({
          text: `Gagal: ${res.message}`,
          type: "error",
        });
      }
    } catch (err) {
      setExtracting(false);
      setActionMessage({
        text: "Gagal memicu penarikan data baru ke backend.",
        type: "error",
      });
    }
  };

  const handleLabeling = async () => {
    setLabeling(true);
    setActionMessage(null);
    try {
      const { triggerLabeling } = await import("../lib/api");
      const res = await triggerLabeling();
      setLabeling(false);
      if (res.status === "success") {
        const s = res.stats;
        setActionMessage({
          text: `Sukses labeling Gemini! Diproses: ${s.success}, Dilewati: ${s.skipped}, Gagal: ${s.failed}.`,
          type: "success",
        });
        loadDashboardData();
      } else {
        setActionMessage({
          text: `Gagal: ${res.message}`,
          type: "error",
        });
      }
    } catch (err) {
      setLabeling(false);
      setActionMessage({
        text: "Gagal memicu pelabelan ulasan ke backend.",
        type: "error",
      });
    }
  };

  return (
    <>
      <Head>
        <title>BNI BIONS Sentiment Dashboard</title>
        <meta name="description" content="Dashboard visualisasi analisis sentimen real-time untuk BNI Sekuritas BIONS" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main style={{ padding: "40px 24px", maxWidth: "1280px", margin: "0 auto" }}>
        {/* Header Section */}
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "36px", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
              <div className="pulse-dot"></div>
              <span style={{ color: "#818CF8", fontSize: "0.8rem", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                Monitoring System Active
              </span>
            </div>
            <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>
              BNI Sekuritas BIONS <span style={{ background: "linear-gradient(90deg, #818cf8 0%, #c084fc 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Sentiment Analytics</span>
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginTop: "4px" }}>
              Dashboard hasil labeling sentimen data ulasan publik menggunakan Google GenAI (Gemini) SDK
            </p>
          </div>
        </header>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
            <p style={{ color: "var(--text-secondary)", fontSize: "1.1rem" }}>Memuat halaman dashboard...</p>
          </div>
        ) : error ? (
          <div className="glass-panel" style={{ padding: "40px", textAlign: "center", color: "var(--color-negative)" }}>
            <h3>Error Memuat Data</h3>
            <p>{error}</p>
          </div>
        ) : (
          <>
            {/* Metrik Ringkasan Utama (Summary Cards) */}
            <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px", marginBottom: "24px" }}>
              {/* Card Total */}
              <div className="glass-panel" style={{ padding: "20px 24px", position: "relative", overflow: "hidden" }}>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase" }}>Total Labeled</p>
                <h2 style={{ fontSize: "2.2rem", fontWeight: 800, margin: "8px 0 4px 0", color: "#F3F4F6" }}>{stats?.total || 0}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>ulasan publik masuk</p>
                <div style={{ position: "absolute", right: "-10px", bottom: "-20px", width: "80px", height: "80px", background: "rgba(99, 102, 241, 0.08)", borderRadius: "50%" }}></div>
              </div>

              {/* Card Positif */}
              <div className="glass-panel" style={{ padding: "20px 24px", position: "relative", overflow: "hidden" }}>
                <p style={{ color: "var(--color-positive)", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase" }}>Positif Sentimen</p>
                <h2 style={{ fontSize: "2.2rem", fontWeight: 800, margin: "8px 0 4px 0", color: "var(--color-positive)" }}>{stats?.labels.Positif || 0}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                  {stats?.total ? Math.round(((stats.labels.Positif || 0) / stats.total) * 100) : 0}% dari total ulasan
                </p>
                <div style={{ position: "absolute", right: "-10px", bottom: "-20px", width: "80px", height: "80px", background: "rgba(16, 185, 129, 0.08)", borderRadius: "50%" }}></div>
              </div>

              {/* Card Negatif */}
              <div className="glass-panel" style={{ padding: "20px 24px", position: "relative", overflow: "hidden" }}>
                <p style={{ color: "var(--color-negative)", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase" }}>Negatif Sentimen</p>
                <h2 style={{ fontSize: "2.2rem", fontWeight: 800, margin: "8px 0 4px 0", color: "var(--color-negative)" }}>{stats?.labels.Negatif || 0}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                  {stats?.total ? Math.round(((stats.labels.Negatif || 0) / stats.total) * 100) : 0}% perlu tindak lanjut
                </p>
                <div style={{ position: "absolute", right: "-10px", bottom: "-20px", width: "80px", height: "80px", background: "rgba(239, 68, 68, 0.08)", borderRadius: "50%" }}></div>
              </div>

              {/* Card Netral */}
              <div className="glass-panel" style={{ padding: "20px 24px", position: "relative", overflow: "hidden" }}>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase" }}>Netral Sentimen</p>
                <h2 style={{ fontSize: "2.2rem", fontWeight: 800, margin: "8px 0 4px 0", color: "#E2E8F0" }}>{stats?.labels.Netral || 0}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>
                  {stats?.total ? Math.round(((stats.labels.Netral || 0) / stats.total) * 100) : 0}% pertanyaan/informasi
                </p>
                <div style={{ position: "absolute", right: "-10px", bottom: "-20px", width: "80px", height: "80px", background: "rgba(107, 114, 128, 0.08)", borderRadius: "50%" }}></div>
              </div>
            </section>

            {/* Visualisasi Grafik Sentimen */}
            <SentimentChart />

            {/* Kontrol Manual & Otomatisasi */}
            <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "24px", marginBottom: "24px" }}>
              <ScheduleManager />
              
              {/* Manual Control Panel */}
              <div className="glass-panel" style={{ padding: "24px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <h3 style={{ fontSize: "1.10rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "16px" }}>
                    Aksi Pipeline Manual
                  </h3>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "20px", lineHeight: "1.4" }}>
                    Jalankan pipeline penarikan ulasan terbaru atau proses analisis sentimen (labeling) dengan Gemini AI secara instan.
                  </p>
                  
                  {actionMessage && (
                    <div style={{
                      padding: "10px 14px",
                      background: actionMessage.type === "success" ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
                      border: actionMessage.type === "success" ? "1px solid rgba(16, 185, 129, 0.2)" : "1px solid rgba(239, 68, 68, 0.2)",
                      color: actionMessage.type === "success" ? "var(--color-positive)" : "var(--color-negative)",
                      borderRadius: "8px",
                      fontSize: "0.85rem",
                      marginBottom: "16px"
                    }}>
                      {actionMessage.text}
                    </div>
                  )}
                </div>
                
                <div style={{ display: "flex", gap: "16px" }}>
                  <button
                    disabled={extracting || labeling}
                    onClick={handleExtract}
                    style={{
                      flex: 1,
                      padding: "12px",
                      background: "rgba(99, 102, 241, 0.1)",
                      color: "#A5B4FC",
                      border: "1px solid rgba(99, 102, 241, 0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontWeight: 600,
                      fontSize: "0.85rem",
                      transition: "all 0.2s ease"
                    }}
                    onMouseEnter={(e) => {
                      if (!extracting && !labeling) {
                        e.currentTarget.style.background = "rgba(99, 102, 241, 0.2)";
                        e.currentTarget.style.borderColor = "rgba(99, 102, 241, 0.4)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!extracting && !labeling) {
                        e.currentTarget.style.background = "rgba(99, 102, 241, 0.1)";
                        e.currentTarget.style.borderColor = "rgba(99, 102, 241, 0.2)";
                      }
                    }}
                  >
                    {extracting ? "Menarik..." : "Tarik Data Baru"}
                  </button>

                  <button
                    disabled={extracting || labeling}
                    onClick={handleLabeling}
                    style={{
                      flex: 1,
                      padding: "12px",
                      background: "rgba(16, 185, 129, 0.1)",
                      color: "var(--color-positive)",
                      border: "1px solid rgba(16, 185, 129, 0.2)",
                      borderRadius: "10px",
                      cursor: "pointer",
                      fontWeight: 600,
                      fontSize: "0.85rem",
                      transition: "all 0.2s ease"
                    }}
                    onMouseEnter={(e) => {
                      if (!extracting && !labeling) {
                        e.currentTarget.style.background = "rgba(16, 185, 129, 0.2)";
                        e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.4)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!extracting && !labeling) {
                        e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)";
                        e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.2)";
                      }
                    }}
                  >
                    {labeling ? "Menganalisis..." : "Labeling Sentimen"}
                  </button>
                </div>
              </div>
            </section>

            {/* Tabel Data Labeled */}
            <CommentTable comments={comments} />
          </>
        )}
      </main>
    </>
  );
}
