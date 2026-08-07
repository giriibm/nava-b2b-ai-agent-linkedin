const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${path} failed (${res.status}): ${text}`);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string; llm_providers_available: string[] }>("/health"),

  listICPs: () => request<import("./types").ICP[]>("/api/icp"),
  createICP: (payload: Record<string, unknown>) =>
    request<import("./types").ICP>("/api/icp", { method: "POST", body: JSON.stringify(payload) }),

  listProspects: (params?: { icp_id?: string; stage?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return request<import("./types").ProspectCompany[]>(`/api/prospects${qs ? `?${qs}` : ""}`);
  },
  getProspect: (id: string) => request<import("./types").ProspectCompany>(`/api/prospects/${id}`),
  getContact: (id: string) =>
    request<import("./types").ProspectContactDetail>(`/api/prospects/contacts/${id}`),
  importProspect: (payload: Record<string, unknown>) =>
    request<import("./types").ProspectCompany>("/api/prospects/import", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  triggerResearch: (companyId: string) =>
    request<{ job_id: string }>(`/api/prospects/${companyId}/research`, { method: "POST" }),
  triggerScoring: (contactId: string) =>
    request<{ job_id: string }>(`/api/prospects/contacts/${contactId}/score`, { method: "POST" }),
  triggerPersonalization: (contactId: string, channel = "linkedin") =>
    request<{ job_id: string }>(
      `/api/prospects/contacts/${contactId}/generate-message?channel=${channel}`,
      { method: "POST" }
    ),
  getJob: (jobId: string) => request<import("./types").Job>(`/api/jobs/${jobId}`),

  approvalQueue: () => request<import("./types").GeneratedMessage[]>("/api/approvals/queue"),
  approveMessage: (id: string, reviewer: string) =>
    request(`/api/approvals/${id}/approve`, { method: "POST", body: JSON.stringify({ reviewer }) }),
  editMessage: (id: string, reviewer: string, edited_content: string) =>
    request(`/api/approvals/${id}/edit`, {
      method: "POST",
      body: JSON.stringify({ reviewer, edited_content }),
    }),
  rejectMessage: (id: string, reviewer: string, reason: string) =>
    request(`/api/approvals/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reviewer, reason }),
    }),

  salesforceStatus: () => request<{ configured: boolean }>("/api/integrations/salesforce/status"),
  heyreachStatus: () => request<{ configured: boolean }>("/api/integrations/heyreach/status"),
};
