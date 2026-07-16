"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { AUTH_CHANGED_EVENT, notifyAuthChanged } from "@/lib/auth";

type Me = {
  id: number;
  role: string;
};

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);

  useEffect(() => {
    const syncAuth = () => {
      apiFetch<Me>("/api/v1/auth/me")
        .then(setMe)
        .catch(() => setMe(null));
    };

    syncAuth();
    window.addEventListener(AUTH_CHANGED_EVENT, syncAuth);

    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, syncAuth);
    };
  }, [pathname]);

  async function handleLogout() {
    try {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
      setMe(null);
      notifyAuthChanged();
      router.push("/");
      router.refresh();
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link className="brand" href="/">
          <span className="brand-mark" />
          번개중고
        </Link>
        <div className="topbar-actions">
          <Link className="nav-link" href="/community">
            커뮤니티
          </Link>
          {me ? (
            <>
              <Link className="nav-link" href="/items/new">
                상품등록
              </Link>
              <Link className="nav-link" href="/transactions">
                거래내역
              </Link>
              <Link className="nav-link" href="/chat">
                채팅
              </Link>
              <Link className="nav-link" href="/mypage">
                마이
              </Link>
              {me.role === "ADMIN" ? (
                <Link className="nav-link" href="/admin">
                  관리자
                </Link>
              ) : null}
              <button className="nav-link" type="button" onClick={handleLogout}>
                로그아웃
              </button>
            </>
          ) : (
            <>
              <Link className="nav-link" href="/login">
                로그인
              </Link>
              <Link className="button primary" href="/signup">
                회원가입
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
