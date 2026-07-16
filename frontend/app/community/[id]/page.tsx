"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { ImageLightbox } from "@/components/image-lightbox";
import { ReportForm } from "@/components/report-form";
import { API_BASE_URL, apiFetch } from "@/lib/api";

type PostDetail = {
  id: number;
  title: string;
  content: string;
  author: { id: number; nickname: string };
  images: Array<{ id: number; image_url: string }>;
  comments: Array<{
    id: number;
    author: { id: number; nickname: string };
    content: string;
    created_at: string;
  }>;
};

type Me = { id: number };

function CommunityDetailContent() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [post, setPost] = useState<PostDetail | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const commentRef = useRef<HTMLTextAreaElement | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  async function loadPost() {
    const data = await apiFetch<PostDetail>(`/api/v1/community/posts/${params.id}`);
    setPost(data);
  }

  useEffect(() => {
    loadPost().catch((err) => setError(err instanceof Error ? err.message : "게시글을 불러오지 못했습니다."));
    apiFetch<Me>("/api/v1/auth/me")
      .then(setMe)
      .catch(() => setMe(null));
  }, [params.id]);

  useEffect(() => {
    const textarea = commentRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 220)}px`;
  }, [comment]);

  async function handleComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!comment.trim()) return;
    setError("");
    try {
      await apiFetch(`/api/v1/community/posts/${params.id}/comments`, {
        method: "POST",
        body: JSON.stringify({ content: comment }),
      });
      setComment("");
      await loadPost();
    } catch (err) {
      setError(err instanceof Error ? err.message : "댓글 작성에 실패했습니다.");
    }
  }

  async function handleDeletePost() {
    const confirmed = window.confirm("게시글을 삭제하시겠습니까?");
    if (!confirmed) return;
    await apiFetch(`/api/v1/community/posts/${params.id}`, { method: "DELETE" });
    router.push("/community");
    router.refresh();
  }

  async function handleDeleteComment(commentId: number) {
    await apiFetch(`/api/v1/community/comments/${commentId}`, { method: "DELETE" });
    await loadPost();
  }

  if (!post) {
    return <div className="panel empty-state muted">게시글을 불러오는 중입니다.</div>;
  }

  const lightboxImages = post.images.map((image) => ({ src: image.image_url, alt: post.title }));

  return (
    <>
    <div className="section">
      <section className="panel community-post-panel">
        <div className="section-title">
          <div>
            <h1 className="page-title">{post.title}</h1>
            <div className="muted">{post.author.nickname}</div>
          </div>
          <div className="detail-actions">
            <Link className="button subtle" href="/community">
              목록
            </Link>
            {me?.id === post.author.id ? (
              <button className="button subtle danger" type="button" onClick={() => void handleDeletePost()}>
                삭제
              </button>
            ) : (
              <div className="report-action-grid">
                <ReportForm
                  options={[
                    { label: "글 신고", targetType: "COMMUNITY_POST", targetId: post.id },
                    { label: "작성자 신고", targetType: "USER", targetId: post.author.id },
                  ]}
                />
              </div>
            )}
          </div>
        </div>
        <div className="detail-description">{post.content}</div>
        {post.images.length > 0 ? (
          <div className="community-image-grid">
            {post.images.map((image, index) => (
              <button className="community-image-card image-open-button" key={image.id} type="button" onClick={() => {
                setSelectedImageIndex(index);
                setLightboxOpen(true);
              }}>
                <img alt={post.title} className="community-image" src={`${API_BASE_URL}${image.image_url}`} />
              </button>
            ))}
          </div>
        ) : null}
      </section>

      <section className="panel community-comment-panel">
        <div className="section-title compact">
          <h2>댓글</h2>
        </div>
        <form className="form" onSubmit={handleComment}>
          <textarea
            ref={commentRef}
            className="comment-textarea"
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="댓글을 입력하세요."
          />
          <button className="button primary form-submit-button" type="submit">
            댓글 등록
          </button>
        </form>
        {error ? <div className="error-box">{error}</div> : null}
        <div className="stack-list">
          {post.comments.map((entry) => (
            <div className="list-card" key={entry.id}>
              <div className="list-card-head">
                <strong>{entry.author.nickname}</strong>
                <div className="inline-action-row">
                  {me?.id === entry.author.id ? (
                    <button className="button subtle danger" type="button" onClick={() => void handleDeleteComment(entry.id)}>
                      삭제
                    </button>
                  ) : null}
                  {me?.id !== entry.author.id ? (
                    <ReportForm
                      options={[
                        { label: "댓글 신고", targetType: "COMMUNITY_COMMENT", targetId: entry.id },
                        { label: "작성자 신고", targetType: "USER", targetId: entry.author.id },
                      ]}
                    />
                  ) : null}
                </div>
              </div>
              <div>{entry.content}</div>
            </div>
          ))}
          {post.comments.length === 0 ? <div className="muted">댓글이 없습니다.</div> : null}
        </div>
      </section>
    </div>
    {lightboxOpen ? (
      <ImageLightbox
        images={lightboxImages}
        currentIndex={selectedImageIndex}
        onClose={() => setLightboxOpen(false)}
        onPrev={() => setSelectedImageIndex((prev) => (prev - 1 + post.images.length) % post.images.length)}
        onNext={() => setSelectedImageIndex((prev) => (prev + 1) % post.images.length)}
      />
    ) : null}
    </>
  );
}

export default CommunityDetailContent;
