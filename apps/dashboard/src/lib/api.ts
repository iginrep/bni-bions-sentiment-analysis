export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function fetchComments() {
  const res = await fetch(`${API_BASE}/comments`);
  if (!res.ok) throw new Error("failed to fetch comments");
  return res.json();
}

export async function fetchLabeledComments() {
  const res = await fetch(`${API_BASE}/comments/labeled?limit=150`);
  if (!res.ok) throw new Error("failed to fetch labeled comments");
  return res.json();
}

export async function fetchLabeledStats() {
  const res = await fetch(`${API_BASE}/comments/labeled/stats`);
  if (!res.ok) throw new Error("failed to fetch labeled stats");
  return res.json();
}

export async function triggerExtraction() {
  const res = await fetch(`${API_BASE}/comments/extract`, { method: "POST" });
  if (!res.ok) throw new Error("failed to trigger extraction");
  return res.json();
}

export async function triggerLabeling() {
  const res = await fetch(`${API_BASE}/comments/label`, { method: "POST" });
  if (!res.ok) throw new Error("failed to trigger labeling");
  return res.json();
}

export async function fetchSchedules() {
  const res = await fetch(`${API_BASE}/schedules`);
  if (!res.ok) throw new Error("failed to fetch schedules");
  return res.json();
}

export async function toggleScheduleStatus(scheduleId: string, isActive: boolean) {
  const res = await fetch(`${API_BASE}/schedules/${scheduleId}/toggle`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ isActive }),
  });
  if (!res.ok) throw new Error("failed to toggle schedule status");
  return res.json();
}
