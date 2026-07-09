"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { API_BASE_URL, apiFetch, apiFormFetch } from "@/lib/api";

type UploadedImage = { id: number; image_url: string };

function CommunityNewContent() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleImages(files: FileList | null) {
    if (!files || files.length === 0) return;
    setError("");
    setIsUploading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append("files", file));
      const result = await apiFormFetch<{ images: UploadedImage[] }>("/api/v1/images/community", formData);
      setUploadedImages((prev) => [...prev, ...result.images].slice(0, 10));
    } catch (err) {
      setError(err instanceof Error ? err.message : "이미지 업로드에 실패했습니다.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const created = await apiFetch<{ id: number }>("/api/v1/community/posts", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim() || "제목 없음",
          content,
          image_ids: uploadedImages.map((image) => image.id),
        }),
      });
      router.push(`/community/${created.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "글 작성에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel single-form-panel item-create-panel">
      <div className="section-title">
        <h1 className="page-title">글쓰기</h1>
      </div>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="title">
            제목
          </label>
          <input id="title" value={title} onChange={(event) => setTitle(event.target.value)} />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="content">
            내용
          </label>
          <textarea id="content" value={content} onChange={(event) => setContent(event.target.value)} />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="images">
            이미지
          </label>
          <div className="upload-box compact-upload-box">
            <input id="images" accept="image/png,image/jpeg,image/webp" multiple type="file" onChange={(event) => void handleImages(event.target.files)} />
            <div className="muted">{isUploading ? "업로드 중..." : `${uploadedImages.length}장 업로드됨`}</div>
          </div>
        </div>
        {uploadedImages.length > 0 ? (
          <div className="upload-preview-grid">
            {uploadedImages.map((image) => (
              <div className="preview-card" key={image.id}>
                <img alt="커뮤니티 이미지" className="product-thumb" src={`${API_BASE_URL}${image.image_url}`} />
                <button className="button subtle" type="button" onClick={() => setUploadedImages((prev) => prev.filter((value) => value.id !== image.id))}>
                  제거
                </button>
              </div>
            ))}
          </div>
        ) : null}
        {error ? <div className="error-box">{error}</div> : null}
        <button className="button primary form-submit-button" disabled={isUploading || isSubmitting} type="submit">
          {isSubmitting ? "작성 중..." : "등록하기"}
        </button>
      </form>
    </section>
  );
}

export default function CommunityNewPage() {
  return (
    <AuthGuard>
      <CommunityNewContent />
    </AuthGuard>
  );
}
