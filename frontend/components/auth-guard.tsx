"use client";

import { ReactNode, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";

type AuthGuardProps = {
  children: ReactNode;
  fallback?: ReactNode;
};

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    apiFetch("/api/v1/auth/me")
      .then(() => setStatus("ready"))
      .catch(() => {
        const next = encodeURIComponent(pathname || "/");
        router.replace(`/login?next=${next}`);
      });
  }, [pathname, router]);

  if (status === "loading") {
    return fallback || <div className="panel empty-state muted">확인 중입니다.</div>;
  }

  return <>{children}</>;
}
