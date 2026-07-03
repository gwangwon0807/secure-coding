"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ImageLightbox } from "@/components/image-lightbox";
import { API_BASE_URL, apiFetch } from "@/lib/api";

type Post = {
  id: number;
  title: string;
  author: { nickname: string };
  comment_count: number;
  thumbnail_url: string | null;
  created_at: string;
};

export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [keyword, setKeyword] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");
  const [error, setError] = useState("");
  const [lightboxImage, setLightboxImage] = useState<{ src: string; alt: string } | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (submittedKeyword.trim()) params.set("keyword", submittedKeyword.trim());
    apiFetch<{ posts: Post[] }>(`/api/v1/community/posts?${params.toString()}`)
      .then((data) => setPosts(data.posts))
      .catch((err) => setError(err instanceof Error ? err.message : "커뮤니티 글을 불러오지 못했습니다."));
  }, [submittedKeyword]);

  return (
    <div className="section">
      <section className="panel search-panel">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setSubmittedKeyword(keyword);
          }}
        >
          <div className="search-row two-wide">
            <input className="search-input" value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="제목이나 내용으로 검색" />
            <button className="button primary" type="submit">
              검색
            </button>
          </div>
        </form>
      </section>
      <section className="section">
        <div className="section-title">
          <h1 className="page-title">커뮤니티</h1>
          <Link className="button primary" href="/community/new">
            글쓰기
          </Link>
        </div>
        {error ? <div className="error-box">{error}</div> : null}
        <div className="stack-list">
          {posts.map((post) => (
            <div className="list-card" key={post.id}>
              <div className="community-list-card">
                {post.thumbnail_url ? (
                  <button className="image-open-button community-thumb-button" type="button" onClick={() => setLightboxImage({ src: post.thumbnail_url!, alt: post.title })}>
                    <img alt={post.title} className="community-list-thumb" src={`${API_BASE_URL}${post.thumbnail_url}`} />
                  </button>
                ) : <div className="community-list-thumb empty" />}
                <Link className="community-list-body" href={`/community/${post.id}`}>
                  <div className="list-card-head">
                    <strong className="card-title">{post.title}</strong>
                    <span className="muted">{post.comment_count}개 댓글</span>
                  </div>
                  <div className="meta-line">
                    <span>{post.author.nickname}</span>
                    <span>{new Date(post.created_at).toLocaleDateString("ko-KR")}</span>
                  </div>
                </Link>
              </div>
            </div>
          ))}
          {posts.length === 0 ? <div className="panel empty-state muted">등록된 글이 없습니다.</div> : null}
        </div>
      </section>
      {lightboxImage ? (
        <ImageLightbox images={[lightboxImage]} currentIndex={0} onClose={() => setLightboxImage(null)} />
      ) : null}
    </div>
  );
}
