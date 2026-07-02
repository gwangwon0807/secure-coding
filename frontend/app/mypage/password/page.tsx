"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

import { apiFetch } from "@/lib/api";

export default function MyPasswordPage() {
  const [form, setForm] = useState({ currentPassword: "", newPassword: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (form.newPassword !== form.confirmPassword) {
      setError("새 비밀번호 확인이 일치하지 않습니다.");
      return;
    }
    setIsSubmitting(true);
    try {
      await apiFetch("/api/v1/users/me/password", {
        method: "PATCH",
        body: JSON.stringify({
          current_password: form.currentPassword,
          new_password: form.newPassword,
        }),
      });
      setSuccess("비밀번호가 변경되었습니다.");
      setForm({ currentPassword: "", newPassword: "", confirmPassword: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "비밀번호 변경에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel single-form-panel">
      <div className="section-title compact">
        <h1 className="page-title">비밀번호 변경</h1>
        <Link className="button subtle" href="/mypage">
          돌아가기
        </Link>
      </div>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="currentPassword">
            현재 비밀번호
          </label>
          <input
            id="currentPassword"
            type="password"
            value={form.currentPassword}
            onChange={(event) => setForm((prev) => ({ ...prev, currentPassword: event.target.value }))}
          />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="newPassword">
            새 비밀번호
          </label>
          <input id="newPassword" type="password" value={form.newPassword} onChange={(event) => setForm((prev) => ({ ...prev, newPassword: event.target.value }))} />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="confirmPassword">
            새 비밀번호 확인
          </label>
          <input
            id="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={(event) => setForm((prev) => ({ ...prev, confirmPassword: event.target.value }))}
          />
        </div>
        {error ? <div className="error-box">{error}</div> : null}
        {success ? <div className="success-box">{success}</div> : null}
        <button className="button primary" disabled={isSubmitting} type="submit">
          {isSubmitting ? "변경 중..." : "비밀번호 변경"}
        </button>
      </form>
    </section>
  );
}
