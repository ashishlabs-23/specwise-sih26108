import { AnalysisRequest, AnalysisResponse, StandardRecord, Evidence } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Keep-alive timer reference for Render 15-minute inactivity spin-down
let keepAliveInterval: any = null;

/**
 * Pre-warm / Wake up Render backend instance on load
 */
export async function wakeUpBackend(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`, {
      method: "GET",
      cache: "no-store",
    });
    return res.ok;
  } catch {
    // If backend is sleeping, the first request will trigger Render to spin up
    return false;
  }
}

/**
 * Start periodic 14-minute ping to prevent Render free-tier from going to sleep
 */
export function startRenderKeepAlive(): void {
  if (typeof window === "undefined") return;
  if (keepAliveInterval) return;

  // Initial wake up
  wakeUpBackend();

  // 14 minutes = 14 * 60 * 1000 = 840,000 ms (under the 15-minute sleep threshold)
  const FOURTEEN_MINUTES_MS = 14 * 60 * 1000;
  keepAliveInterval = setInterval(() => {
    wakeUpBackend();
  }, FOURTEEN_MINUTES_MS);
}

export async function analyzeProduct(request: AnalysisRequest): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "API analysis request failed." }));
    throw new Error(err.detail || `Server returned error ${res.status}`);
  }

  return res.json();
}

export async function checkApiHealth(): Promise<{ status: string; standards_loaded: number }> {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return res.json();
}

export async function uploadPdf(file: File): Promise<AnalysisResponse> {
  const form = new FormData();
  form.append("file", file, file.name);

  const res = await fetch(`${API_BASE}/api/v1/upload-pdf`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `Upload failed with status ${res.status}` }));
    throw new Error(err.detail || `Server returned ${res.status}`);
  }

  return res.json();
}

export interface ResourcesResponse {
  summary: {
    standards_count: number;
    evidence_count: number;
    relationships_count: number;
    benchmark_cases_count: number;
    sources_count: number;
  };
  standards: StandardRecord[];
  evidence: Evidence[];
  relationships: Array<{
    from_standard: string;
    to_standard: string;
    relationship_type: string;
    evidence_ids: string[];
    verified: boolean;
  }>;
  sources: Array<{
    source_id: string;
    name: string;
    publisher: string;
    url: string;
    source_type: string;
    retrieved_at: string;
    notes: string;
  }>;
  benchmark_cases: Array<{
    id: string;
    query: string;
    expected_contains: string[];
    expected_decision: string | null;
    notes: string;
  }>;
}

export async function fetchStandardDetails(
  standardId: string
): Promise<{ standard: StandardRecord; evidence: Evidence[] }> {
  const encodedId = encodeURIComponent(standardId);
  const res = await fetch(`${API_BASE}/api/v1/standards/${encodedId}`);
  if (!res.ok) {
    throw new Error(`Failed to load details for ${standardId}`);
  }
  return res.json();
}

export async function fetchResources(): Promise<ResourcesResponse> {
  const res = await fetch(`${API_BASE}/api/v1/resources`);
  if (!res.ok) {
    throw new Error(`Failed to load resources (Status ${res.status})`);
  }
  return res.json();
}

