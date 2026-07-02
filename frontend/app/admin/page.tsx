"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type AdminUser = { id: number; email: string; nickname: string; status: string; role: string };
type AdminItem = { id: number; title: string; status: string; seller: { nickname: string }; report_count: number };
type AdminReport = { id: number; target_type: string; reason: string; status: string; target_summary: string | null };

export default function AdminPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [items, setItems] = useState<AdminItem[]>([]);
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [tab, setTab] = useState<"users" | "items" | "reports">("users");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch<{ users: AdminUser[] }>("/api/v1/admin/users"),
      apiFetch<{ items: AdminItem[] }>("/api/v1/admin/items"),
      apiFetch<{ reports: AdminReport[] }>("/api/v1/admin/reports"),
    ])
      .then(([userData, itemData, reportData]) => {
        setUsers(userData.users);
        setItems(itemData.items);
        setReports(reportData.reports);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "관리자 데이터를 불러오지 못했습니다."));
  }, []);

  return (
    <div className="admin-grid">
      <div className="section-title">
        <h1 className="page-title">관리자</h1>
        <div className="tabs">
          <button className={`tab ${tab === "users" ? "active" : ""}`} type="button" onClick={() => setTab("users")}>
            회원
          </button>
          <button className={`tab ${tab === "items" ? "active" : ""}`} type="button" onClick={() => setTab("items")}>
            상품
          </button>
          <button className={`tab ${tab === "reports" ? "active" : ""}`} type="button" onClick={() => setTab("reports")}>
            신고
          </button>
        </div>
      </div>
      {error ? <div className="error-box">{error}</div> : null}

      {tab === "users" ? (
        <section className="panel admin-section table-like">
          {users.map((user) => (
            <div className="table-row" key={user.id}>
              <strong>{user.nickname}</strong>
              <span>{user.email}</span>
              <span>{user.role}</span>
              <span>{user.status}</span>
            </div>
          ))}
        </section>
      ) : null}

      {tab === "items" ? (
        <section className="panel admin-section table-like">
          {items.map((item) => (
            <div className="table-row" key={item.id}>
              <strong>{item.title}</strong>
              <span>{item.seller.nickname}</span>
              <span>{item.status}</span>
              <span>신고 {item.report_count}건</span>
            </div>
          ))}
        </section>
      ) : null}

      {tab === "reports" ? (
        <section className="panel admin-section table-like">
          {reports.map((report) => (
            <div className="table-row" key={report.id}>
              <strong>{report.target_type}</strong>
              <span>{report.reason}</span>
              <span>{report.status}</span>
              <span>{report.target_summary || "-"}</span>
            </div>
          ))}
        </section>
      ) : null}
    </div>
  );
}
