export const API_BASE_URL =
  process.env.NEXT_INTERNAL_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000";

function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("secure-coding-access-token");
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
    return payload.detail;
  }

  if (typeof payload.message === "string") {
    return payload.message;
  }

  return fallback;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = getStoredAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

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

export async function apiFormFetch<T>(path: string, formData: FormData, init?: RequestInit): Promise<T> {
  const accessToken = getStoredAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    method: init?.method || "POST",
    body: formData,
    credentials: "include",
    headers: {
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init?.headers || {}),
    },
  });

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
