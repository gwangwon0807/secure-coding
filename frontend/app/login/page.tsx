"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    const form = new FormData(event.currentTarget);
    try {
      await apiFetch("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      const next = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") || "/" : "/";
      router.push(next);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel single-form-panel">
      <div className="section-title compact">
        <h1 className="page-title">로그인</h1>
      </div>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="email">
            이메일
          </label>
          <input id="email" name="email" type="email" />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="password">
            비밀번호
          </label>
          <input id="password" name="password" type="password" />
        </div>
        {error ? <div className="error-box">{error}</div> : null}
        <button className="button primary" disabled={isSubmitting} type="submit">
          {isSubmitting ? "로그인 중..." : "로그인"}
        </button>
      </form>
    </section>
  );
}
