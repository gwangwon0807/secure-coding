"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";

type Me = {
  nickname: string;
  bio: string | null;
};

export default function MyProfileEditPage() {
  const router = useRouter();
  const [form, setForm] = useState({ nickname: "", bio: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    apiFetch<Me>("/api/v1/users/me")
      .then((data) => setForm({ nickname: data.nickname, bio: data.bio || "" }))
      .catch((err) => setError(err instanceof Error ? err.message : "내 정보를 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setIsSubmitting(true);
    try {
      await apiFetch("/api/v1/users/me", {
        method: "PATCH",
        body: JSON.stringify({
          nickname: form.nickname,
          bio: form.bio,
        }),
      });
      setSuccess("프로필이 저장되었습니다.");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "프로필 수정에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel single-form-panel">
      <div className="section-title compact">
        <h1 className="page-title">프로필 수정</h1>
        <Link className="button subtle" href="/mypage">
          돌아가기
        </Link>
      </div>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="nickname">
            닉네임
          </label>
          <input id="nickname" value={form.nickname} onChange={(event) => setForm((prev) => ({ ...prev, nickname: event.target.value }))} />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="bio">
            소개글
          </label>
          <textarea id="bio" value={form.bio} onChange={(event) => setForm((prev) => ({ ...prev, bio: event.target.value }))} />
        </div>
        {error ? <div className="error-box">{error}</div> : null}
        {success ? <div className="success-box">{success}</div> : null}
        <button className="button primary" disabled={isSubmitting} type="submit">
          {isSubmitting ? "저장 중..." : "저장"}
        </button>
      </form>
    </section>
  );
}
