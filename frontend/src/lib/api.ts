const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type User = {
  id: number;
  name: string;
  email: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function formatErrorDetail(detail: unknown): string {
  if (typeof detail === "string") {
    try {
      const parsed = JSON.parse(detail) as { error?: { message?: string } };
      if (parsed.error?.message) return parsed.error.message;
    } catch {
      /* plain string */
    }
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "object" && d && "msg" in d ? String(d.msg) : String(d)))
      .join(", ");
  }
  return "Request failed";
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new ApiError(
      `Cannot reach the API at ${API_URL}. Start the backend with: uvicorn app.main:app --reload`,
      0,
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(formatErrorDetail(data.detail), response.status);
  }

  return data as T;
}

export const api = {
  register: (name: string, email: string, password: string) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) =>
    request<User>("/api/auth/me", { method: "GET" }, token),

  checkAvailability: (
    token: string,
    date: string,
    preferredTime?: string | null,
  ) =>
    request<Record<string, unknown>>(
      "/api/tools/check-availability",
      {
        method: "POST",
        body: JSON.stringify({ date, preferred_time: preferredTime ?? null }),
      },
      token,
    ),

  searchProperties: (
    token: string,
    filters: {
      location?: string;
      bhk?: string;
      property_type?: string;
      max_budget_lakhs?: number;
      budget?: string;
      query?: string;
    },
  ) =>
    request<Record<string, unknown>>(
      "/api/tools/search-properties",
      { method: "POST", body: JSON.stringify(filters) },
      token,
    ),

  getInventoryOverview: (token: string) =>
    request<Record<string, unknown>>(
      "/api/tools/inventory-overview",
      { method: "POST", body: "{}" },
      token,
    ),

  getPropertyDetails: (token: string, propertyId: string) =>
    request<Record<string, unknown>>(
      "/api/tools/get-property-details",
      { method: "POST", body: JSON.stringify({ property_id: propertyId }) },
      token,
    ),

  bookMeeting: (
    token: string,
    payload: {
      name: string;
      email: string;
      date: string;
      time: string;
      property_id?: string;
      property_name?: string;
    },
  ) =>
    request<Record<string, unknown>>(
      "/api/tools/book-meeting",
      { method: "POST", body: JSON.stringify(payload) },
      token,
    ),

  validateEmail: (token: string, email: string) =>
    request<Record<string, unknown>>(
      "/api/tools/validate-email",
      { method: "POST", body: JSON.stringify({ email }) },
      token,
    ),

  createVoiceSession: async (offerSdp: string, token: string) => {
    let response: Response;
    try {
      response = await fetch(`${API_URL}/api/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/sdp",
          Authorization: `Bearer ${token}`,
        },
        body: offerSdp,
      });
    } catch {
      throw new ApiError(
        `Cannot reach the API at ${API_URL}. Start the backend with: uvicorn app.main:app --reload`,
        0,
      );
    }

    const text = await response.text();
    if (!response.ok) {
      let message = text;
      try {
        const data = JSON.parse(text) as { detail?: unknown };
        message = formatErrorDetail(data.detail);
      } catch {
        /* plain text error from upstream */
      }
      throw new ApiError(message || "Voice session failed", response.status);
    }

    return text;
  },
};

export { API_URL, ApiError };
