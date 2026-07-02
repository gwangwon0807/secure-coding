"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { API_BASE_URL, apiFetch } from "@/lib/api";
import { formatItemStatus, getItemStatusClassName } from "@/lib/labels";

type MyItem = {
  id: number;
  title: string;
  price: number;
  location: string;
  status: string;
  thumbnail_url: string | null;
};

function MyItemsContent() {
  const [items, setItems] = useState<MyItem[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadItems() {
    const data = await apiFetch<{ items: MyItem[] }>("/api/v1/users/me/items");
    setItems(data.items);
  }

  useEffect(() => {
    loadItems().catch((err) => setError(err instanceof Error ? err.message : "내 상품을 불러오지 못했습니다."));
  }, []);

  async function handleDelete(itemId: number) {
    const confirmed = window.confirm("이 상품을 삭제하시겠습니까?");
    if (!confirmed) return;
    setError("");
    setMessage("");
    try {
      await apiFetch(`/api/v1/items/${itemId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((item) => item.id !== itemId));
      setMessage("상품이 삭제되었습니다.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "상품 삭제에 실패했습니다.");
    }
  }

  return (
    <section className="panel wide-panel">
      <div className="section-title">
        <h1 className="page-title">내가 올린 상품</h1>
        <Link className="button subtle" href="/mypage">
          마이페이지
        </Link>
      </div>
      {error ? <div className="error-box">{error}</div> : null}
      {message ? <div className="success-box">{message}</div> : null}
      <div className="stack-list">
        {items.map((item) => (
          <div className="list-card my-item-manage-card" key={item.id}>
            {item.thumbnail_url ? <img alt={item.title} className="manage-thumb" src={`${API_BASE_URL}${item.thumbnail_url}`} /> : <div className="manage-thumb" />}
            <div className="manage-item-body">
              <div className="list-card-head">
                <div>
                  <div className="card-title">{item.title}</div>
                  <div className="card-sub">{item.location}</div>
                </div>
                <div className={getItemStatusClassName(item.status)}>{formatItemStatus(item.status)}</div>
              </div>
              <div className="price">{item.price.toLocaleString()}원</div>
              <div className="manage-action-row">
                <Link className="button subtle" href={`/items/${item.id}`}>
                  상세
                </Link>
                <Link className="button subtle" href={`/items/${item.id}/edit`}>
                  수정
                </Link>
                <button className="button subtle danger" type="button" onClick={() => void handleDelete(item.id)}>
                  삭제
                </button>
              </div>
            </div>
          </div>
        ))}
        {items.length === 0 ? <div className="panel empty-state muted">등록한 상품이 없습니다.</div> : null}
      </div>
    </section>
  );
}

export default function MyItemsPage() {
  return (
    <AuthGuard>
      <MyItemsContent />
    </AuthGuard>
  );
}
