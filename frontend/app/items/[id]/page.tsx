"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { API_BASE_URL, apiFetch } from "@/lib/api";
import { formatItemStatus, getItemStatusClassName } from "@/lib/labels";

type ItemDetail = {
  id: number;
  title: string;
  description: string;
  price: number;
  location: string;
  status: string;
  category: { name: string };
  seller: { id: number; nickname: string };
  images: Array<{ id: number; image_url: string }>;
};
type Me = { id: number };

export default function ItemDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<ItemDetail | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<ItemDetail>(`/api/v1/items/${params.id}`)
      .then(setItem)
      .catch((err) => setError(err instanceof Error ? err.message : "상품을 불러오지 못했습니다."));
    apiFetch<Me>("/api/v1/auth/me")
      .then(setMe)
      .catch(() => setMe(null));
  }, [params.id]);

  async function handleCreateChat() {
    try {
      const room = await apiFetch<{ id: number }>("/api/v1/chat-rooms", {
        method: "POST",
        body: JSON.stringify({ item_id: Number(params.id) }),
      });
      router.push(`/chat?room=${room.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "채팅방 생성에 실패했습니다.");
    }
  }

  const isOwner = me && item ? me.id === item.seller.id : false;

  if (error && !item) {
    return <div className="error-box">{error}</div>;
  }

  if (!item) {
    return <div className="panel empty-state muted">상품 정보를 불러오는 중입니다.</div>;
  }

  return (
    <div className="detail-layout">
      <section className="panel detail-panel">
        {item.images[0] ? <img alt={item.title} className="detail-hero-image" src={`${API_BASE_URL}${item.images[0].image_url}`} /> : <div className="detail-hero-image" />}
        {item.images.length > 1 ? (
          <div className="detail-thumb-row">
            {item.images.map((image) => (
              <img key={image.id} alt={item.title} className="mini-thumb" src={`${API_BASE_URL}${image.image_url}`} />
            ))}
          </div>
        ) : null}
      </section>
      <aside className="panel detail-side">
        <div className="detail-stack">
          <div className={getItemStatusClassName(item.status)}>{formatItemStatus(item.status)}</div>
          <h1 className="page-title">{item.title}</h1>
          <div className="price">{item.price.toLocaleString()}원</div>
        </div>
        <div className="info-row">카테고리 {item.category.name}</div>
        <div className="info-row">거래 지역 {item.location}</div>
        <div className="info-row">판매자 {item.seller.nickname}</div>
        <div className={`detail-actions ${isOwner ? "single" : ""}`}>
          {isOwner ? (
            <Link className="button primary" href={`/items/${item.id}/edit`}>
              상품 수정
            </Link>
          ) : (
            <>
              <button className="button primary" disabled={item.status === "SOLD"} type="button" onClick={handleCreateChat}>
                채팅하기
              </button>
              <Link className="button subtle" href="/transactions">
                거래내역
              </Link>
            </>
          )}
        </div>
        {error ? <div className="error-box">{error}</div> : null}
        <div className="detail-description">{item.description}</div>
      </aside>
    </div>
  );
}
