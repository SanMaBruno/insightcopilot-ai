const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api";

interface ApiErrorPayload {
  detail?: string;
  code?: string;
  category?: string;
  service?: string;
  provider?: string;
  retryable?: boolean;
}

class ApiError extends Error {
  status: number;
  code?: string;
  category?: string;
  service?: string;
  provider?: string;
  retryable?: boolean;

  constructor(status: number, payload: ApiErrorPayload) {
    const message = payload.detail ?? "Error de API";
    super(message);
    this.status = status;
    this.code = payload.code;
    this.category = payload.category;
    this.service = payload.service;
    this.provider = payload.provider;
    this.retryable = payload.retryable;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({} as ApiErrorPayload));
    throw new ApiError(response.status, {
      detail: body.detail ?? response.statusText,
      code: body.code,
      category: body.category,
      service: body.service,
      provider: body.provider,
      retryable: body.retryable,
    });
  }

  return response.json() as Promise<T>;
}

async function uploadFile<T>(path: string, file: File): Promise<T> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({} as ApiErrorPayload));
    throw new ApiError(response.status, {
      detail: body.detail ?? response.statusText,
      code: body.code,
      category: body.category,
      service: body.service,
      provider: body.provider,
      retryable: body.retryable,
    });
  }

  return response.json() as Promise<T>;
}

export { request, uploadFile, ApiError };
