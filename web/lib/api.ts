const API = process.env.NEXT_PUBLIC_API_URL || "";

export type Issue = {
  id: number;
  title: string;
  description: string;
  latitude: number;
  longitude: number;
  mode: string;
  status: string;
  signature_count: number;
  signature_goal: number | null;
  public_status: string | null;
  external_case_number_masked: string | null;
  address_text: string;
};

function authHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

export async function login(email: string, password: string) {
  const data = await api<{ access_token: string }>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("token", data.access_token);
}

export async function register(email: string, password: string, display_name: string) {
  const data = await api<{ access_token: string }>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name }),
  });
  localStorage.setItem("token", data.access_token);
}

export async function fetchBoard() {
  return api<{ items: Issue[] }>("/api/v1/board?city=moscow");
}

export async function fetchIssue(id: string) {
  return api<Issue & { description: string }>(`/api/v1/issues/${id}`);
}

export async function createIssue(body: object) {
  return api<Issue>("/api/v1/issues", { method: "POST", body: JSON.stringify(body) });
}

export async function upgradeCollective(id: number) {
  return api(`/api/v1/issues/${id}/upgrade-to-collective?signature_goal=10`, { method: "POST" });
}

export async function fetchPetitionByIssue(issueId: number) {
  return api<{ id: number; signature_count: number; signature_goal: number }>(
    `/api/v1/petitions/by-issue/${issueId}`
  );
}

export async function signPetition(petitionId: number) {
  return api(`/api/v1/petitions/${petitionId}/sign`, { method: "POST" });
}

export async function mockSubmit(issueId: number) {
  return api<{ redirect_url: string }>(`/api/v1/issues/${issueId}/mock-submit`, { method: "POST" });
}

export async function linkCase(issueId: number, external_case_number: string) {
  return api(`/api/v1/tracking/link`, {
    method: "POST",
    body: JSON.stringify({ issue_id: issueId, external_case_number }),
  });
}
