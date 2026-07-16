// Browser requests stay on the frontend origin and Next.js proxies them to FastAPI.
export const API_BASE_URL = "";

const LEGACY_ACCESS_TOKEN_KEY = "secure-coding-access-token";
const CSRF_COOKIE_NAME = "csrf_token";
const REFRESH_EXCLUDED_PATHS = new Set([
  "/api/v1/auth/login",
  "/api/v1/auth/signup",
  "/api/v1/auth/refresh",
  "/api/v1/auth/logout",
]);
let refreshPromise: Promise<boolean> | null = null;

if (typeof window !== "undefined") {
  window.localStorage.removeItem(LEGACY_ACCESS_TOKEN_KEY);
}

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${encodeURIComponent(name)}=`;
  const entry = document.cookie.split("; ").find((cookie) => cookie.startsWith(prefix));
  return entry ? decodeURIComponent(entry.slice(prefix.length)) : null;
}

function buildHeaders(init?: RequestInit, isForm = false): HeadersInit {
  const method = (init?.method || "GET").toUpperCase();
  const csrfToken = getCookie(CSRF_COOKIE_NAME);
  return {
    ...(!isForm ? { "Content-Type": "application/json" } : {}),
    ...(csrfToken && !["GET", "HEAD", "OPTIONS"].includes(method) ? { "X-CSRF-Token": csrfToken } : {}),
    ...(init?.headers || {}),
  };
}

async function refreshSession(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const csrfToken = getCookie(CSRF_COOKIE_NAME);
      if (!csrfToken) return false;
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
        cache: "no-store",
      });
      return response.ok;
    })().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

type ApiErrorDetail = {
  loc?: Array<string | number>;
  msg?: string;
};

function formatApiError(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") {
    return fallback;
  }

  const payload = data as { detail?: string | ApiErrorDetail[]; message?: string };

  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item) => {
        const field = item.loc?.[item.loc.length - 1];
        if (field === "image_ids") {
          return "상품 이미지를 1장 이상 업로드해 주세요.";
        }
        if (field === "category_id") {
          return "카테고리를 선택해 주세요.";
        }
        if (field === "title") {
          return "제목을 입력해 주세요.";
        }
        if (field === "description") {
          return "상품 설명을 입력해 주세요.";
        }
        if (field === "price") {
          return "가격은 0원 이상으로 입력해 주세요.";
        }
        if (field === "location") {
          return "거래 지역을 입력해 주세요.";
        }
        if (field === "current_password") {
          return "현재 비밀번호를 확인해 주세요.";
        }
        if (field === "new_password") {
          return "새 비밀번호는 8자 이상으로 입력해 주세요.";
        }
        return item.msg || fallback;
      })
      .join("\n");
  }

  if (typeof payload.detail === "string") {
    if (payload.detail === "INVALID_CURRENT_PASSWORD") {
      return "현재 비밀번호가 올바르지 않습니다.";
    }
    if (payload.detail === "PASSWORD_SAME_AS_CURRENT") {
      return "새 비밀번호를 현재 비밀번호와 다르게 입력해 주세요.";
    }
    if (payload.detail === "DEPOSIT_REQUEST_ALREADY_PENDING") {
      return "처리 대기 중인 충전 요청이 이미 있습니다.";
    }
    if (payload.detail === "DIRECT_DEPOSIT_DISABLED_USE_REQUEST") {
      return "직접 입금은 비활성화되었습니다. 충전 요청을 이용해 주세요.";
    }
    return payload.detail;
  }

  if (typeof payload.message === "string") {
    return payload.message;
  }

  return fallback;
}

async function apiFetchInternal<T>(path: string, init: RequestInit | undefined, allowRefresh: boolean): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: buildHeaders(init),
    cache: "no-store",
  });

  if (response.status === 401 && allowRefresh && !REFRESH_EXCLUDED_PATHS.has(path)) {
    if (await refreshSession()) {
      return apiFetchInternal<T>(path, init, false);
    }
  }

  if (!response.ok) {
    let message = "요청에 실패했습니다.";
    try {
      const data = await response.json();
      message = formatApiError(data, message);
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  return apiFetchInternal<T>(path, init, true);
}

async function apiFormFetchInternal<T>(path: string, formData: FormData, init: RequestInit | undefined, allowRefresh: boolean): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    method: init?.method || "POST",
    body: formData,
    credentials: "include",
    headers: buildHeaders(init, true),
  });

  if (response.status === 401 && allowRefresh && !REFRESH_EXCLUDED_PATHS.has(path)) {
    if (await refreshSession()) {
      return apiFormFetchInternal<T>(path, formData, init, false);
    }
  }

  if (!response.ok) {
    let message = "업로드에 실패했습니다.";
    try {
      const data = await response.json();
      message = formatApiError(data, message);
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function apiFormFetch<T>(path: string, formData: FormData, init?: RequestInit): Promise<T> {
  return apiFormFetchInternal<T>(path, formData, init, true);
}
