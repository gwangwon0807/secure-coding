"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { apiFetch } from "@/lib/api";
import { notifyAuthChanged } from "@/lib/auth";

type Me = {
  id: number;
  email: string;
  nickname: string;
  bio: string | null;
  trade_count: number;
  report_count: number;
  trust_score: number;
};

function MyPageContent() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Me>("/api/v1/users/me")
      .then((data) => setMe(data))
      .catch((err) => setError(err instanceof Error ? err.message : "내 정보를 불러오지 못했습니다."));
  }, []);

  async function handleLogout() {
    try {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
      notifyAuthChanged();
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그아웃에 실패했습니다.");
    }
  }

  return (
    <section className="panel profile-view-panel wide-panel">
        {error ? <div className="error-box">{error}</div> : null}
        <div className="profile-summary">
          <div className="profile-top">
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <div className="avatar" />
              <div>
                <h1 className="page-title">{me?.nickname || "마이페이지"}</h1>
                <div className="muted">{me?.email || ""}</div>
              </div>
            </div>
          </div>
          <div className="stats-inline">
            <div className="stat-pill">신뢰도 {me?.trust_score ?? 0}</div>
            <div className="stat-pill">거래 {me?.trade_count ?? 0}회</div>
            <div className="stat-pill">신고 {me?.report_count ?? 0}건</div>
          </div>
          <div className="info-row">{me?.bio || "소개글이 없습니다."}</div>
          <div className="mypage-action-grid">
            <Link className="mypage-action-card" href="/mypage/profile">
              <strong>프로필 수정</strong>
              <span>닉네임과 소개글 변경</span>
            </Link>
            <Link className="mypage-action-card" href="/mypage/password">
              <strong>비밀번호 변경</strong>
              <span>새 비밀번호로 업데이트</span>
            </Link>
            <Link className="mypage-action-card" href="/mypage/items">
              <strong>내가 올린 상품</strong>
              <span>등록 상품 확인, 수정, 삭제</span>
            </Link>
            <Link className="mypage-action-card" href="/wallet">
              <strong>지갑</strong>
              <span>잔액 확인, 입금, 출금</span>
            </Link>
            <button className="mypage-action-card danger-card" type="button" onClick={handleLogout}>
              <strong>로그아웃</strong>
              <span>현재 계정에서 로그아웃</span>
            </button>
          </div>
        </div>
    </section>
  );
}

export default function MyPage() {
  return (
    <AuthGuard>
      <MyPageContent />
    </AuthGuard>
  );
}
