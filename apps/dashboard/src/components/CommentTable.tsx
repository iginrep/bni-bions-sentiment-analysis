import React, { useState } from "react";
import type { LabeledComment, SentimentLabel } from "../types/comment";

export function CommentTable({ comments }: { comments: LabeledComment[] }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSentiment, setSelectedSentiment] = useState<string>("ALL");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("ALL");

  // Format tanggal lokalisasi
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "-";
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("id-ID", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  // Filter logika
  const filteredComments = comments.filter((c) => {
    const matchesSearch =
      c.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.authorDisplayName || "").toLowerCase().includes(searchTerm.toLowerCase());

    const matchesSentiment =
      selectedSentiment === "ALL" || c.labeling_review === selectedSentiment;

    const matchesPlatform =
      selectedPlatform === "ALL" || c.platform === selectedPlatform;

    return matchesSearch && matchesSentiment && matchesPlatform;
  });

  const getPlatformBadge = (platform: string) => {
    switch (platform) {
      case "google_play":
        return <span className="badge badge-platform">Google Play</span>;
      case "app_store":
        return <span className="badge badge-platform" style={{ background: "rgba(16, 185, 129, 0.05)", color: "#34D399", borderColor: "rgba(16, 185, 129, 0.15)" }}>App Store</span>;
      case "youtube":
        return <span className="badge badge-platform" style={{ background: "rgba(239, 68, 68, 0.05)", color: "#F87171", borderColor: "rgba(239, 68, 68, 0.15)" }}>YouTube</span>;
      default:
        return <span className="badge badge-platform">{platform}</span>;
    }
  };

  const getSentimentBadge = (label: SentimentLabel) => {
    switch (label) {
      case "Positif":
        return <span className="badge badge-positive">Positif</span>;
      case "Negatif":
        return <span className="badge badge-negative">Negatif</span>;
      case "Netral":
        return <span className="badge badge-neutral">Netral</span>;
      default:
        return <span className="badge badge-neutral">{label}</span>;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: "24px", marginTop: "24px" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "20px" }}>
        <h3 style={{ fontSize: "1.10rem", fontWeight: 600, color: "var(--text-primary)" }}>
          Feed Ulasan Terlabeli
        </h3>
        
        {/* Kontrol Filter */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", alignItems: "center" }}>
          <input
            type="text"
            placeholder="Cari ulasan atau nama..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              flex: 1,
              minWidth: "200px",
              padding: "8px 16px",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid var(--border-color)",
              borderRadius: "10px",
              color: "var(--text-primary)",
              fontSize: "0.9rem",
              outline: "none",
            }}
          />
          
          <select
            value={selectedSentiment}
            onChange={(e) => setSelectedSentiment(e.target.value)}
            style={{
              padding: "8px 16px",
              background: "#0F131E",
              border: "1px solid var(--border-color)",
              borderRadius: "10px",
              color: "var(--text-primary)",
              fontSize: "0.9rem",
              outline: "none",
            }}
          >
            <option value="ALL">Semua Sentimen</option>
            <option value="Positif">Positif</option>
            <option value="Negatif">Negatif</option>
            <option value="Netral">Netral</option>
          </select>

          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            style={{
              padding: "8px 16px",
              background: "#0F131E",
              border: "1px solid var(--border-color)",
              borderRadius: "10px",
              color: "var(--text-primary)",
              fontSize: "0.9rem",
              outline: "none",
            }}
          >
            <option value="ALL">Semua Platform</option>
            <option value="google_play">Google Play</option>
            <option value="app_store">App Store</option>
            <option value="youtube">YouTube</option>
          </select>
        </div>
      </div>

      {/* Tabel */}
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.9rem" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-secondary)" }}>
              <th style={{ padding: "12px 16px", fontWeight: 500 }}>Pengguna</th>
              <th style={{ padding: "12px 16px", fontWeight: 500 }}>Platform</th>
              <th style={{ padding: "12px 16px", fontWeight: 500, width: "45%" }}>Ulasan</th>
              <th style={{ padding: "12px 16px", fontWeight: 500 }}>Sentimen</th>
              <th style={{ padding: "12px 16px", fontWeight: 500 }}>Tanggal</th>
              <th style={{ padding: "12px 16px", fontWeight: 500, textAlign: "center" }}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {filteredComments.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
                  Tidak ada ulasan terlabeli yang cocok dengan filter.
                </td>
              </tr>
            ) : (
              filteredComments.map((c) => (
                <tr
                  key={c.id}
                  style={{
                    borderBottom: "1px solid rgba(255,255,255,0.03)",
                    transition: "background 0.2s ease",
                  }}
                  className="table-row-hover"
                >
                  <td style={{ padding: "14px 16px", fontWeight: 500, color: "var(--text-primary)" }}>
                    {c.authorDisplayName || "Anonim"}
                  </td>
                  <td style={{ padding: "14px 16px" }}>{getPlatformBadge(c.platform)}</td>
                  <td style={{ padding: "14px 16px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                    {c.text}
                  </td>
                  <td style={{ padding: "14px 16px" }}>{getSentimentBadge(c.labeling_review)}</td>
                  <td style={{ padding: "14px 16px", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                    {formatDate(c.postedAt)}
                  </td>
                  <td style={{ padding: "14px 16px", textAlign: "center" }}>
                    {c.sourceUrl ? (
                      <a
                        href={c.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          padding: "6px 12px",
                          background: "rgba(99, 102, 241, 0.1)",
                          color: "#A5B4FC",
                          border: "1px solid rgba(99, 102, 241, 0.2)",
                          borderRadius: "8px",
                          fontSize: "0.8rem",
                          textDecoration: "none",
                          fontWeight: 500,
                          transition: "all 0.2s ease",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = "rgba(99, 102, 241, 0.25)";
                          e.currentTarget.style.borderColor = "rgba(99, 102, 241, 0.4)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = "rgba(99, 102, 241, 0.1)";
                          e.currentTarget.style.borderColor = "rgba(99, 102, 241, 0.2)";
                        }}
                      >
                        Buka Link
                      </a>
                    ) : (
                      <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>-</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* Inline styles for row hover effect */}
      <style jsx>{`
        .table-row-hover:hover {
          background: rgba(255, 255, 255, 0.015);
        }
      `}</style>
    </div>
  );
}
