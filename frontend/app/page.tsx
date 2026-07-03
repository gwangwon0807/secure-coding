"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { ImageLightbox } from "@/components/image-lightbox";
import { API_BASE_URL, apiFetch } from "@/lib/api";
import { formatItemStatus, getItemStatusClassName } from "@/lib/labels";

type Category = { id: number; name: string };
type Item = {
  id: number;
  title: string;
  price: number;
  location: string;
  status: string;
  thumbnail_url: string | null;
  seller: { nickname: string };
};

type ItemResponse = {
  items: Item[];
  pagination: { total_count: number };
};

const SORT_OPTIONS = [
  { value: "latest", label: "최신순" },
  { value: "price_asc", label: "낮은 가격순" },
  { value: "price_desc", label: "높은 가격순" },
];

export default function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [keyword, setKeyword] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [sort, setSort] = useState("latest");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [lightboxImage, setLightboxImage] = useState<{ src: string; alt: string } | null>(null);

  useEffect(() => {
    apiFetch<{ categories: Category[] }>("/api/v1/categories")
      .then((data) => setCategories(data.categories))
      .catch((err) => setError(err instanceof Error ? err.message : "카테고리를 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    const search = new URLSearchParams();
    if (submittedKeyword.trim()) search.set("keyword", submittedKeyword.trim());
    if (categoryId) search.set("category_id", categoryId);
    if (sort) search.set("sort", sort);
    setIsLoading(true);
    setError("");
    apiFetch<ItemResponse>(`/api/v1/items?${search.toString()}`)
      .then((data) => {
        setItems(data.items);
        setTotalCount(data.pagination.total_count);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "상품 목록을 불러오지 못했습니다."))
      .finally(() => setIsLoading(false));
  }, [submittedKeyword, categoryId, sort]);

  const activeCategoryName = useMemo(
    () => categories.find((category) => String(category.id) === categoryId)?.name,
    [categories, categoryId],
  );

  return (
    <div className="home-layout">
      <section className="panel search-panel">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setSubmittedKeyword(keyword);
          }}
        >
          <div className="search-row">
            <label className="sr-only" htmlFor="keyword">
              검색어
            </label>
            <input
              id="keyword"
              className="search-input"
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="상품명이나 설명으로 검색"
            />
            <label className="sr-only" htmlFor="category">
              카테고리
            </label>
            <select id="category" className="search-select" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
              <option value="">전체 카테고리</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <label className="sr-only" htmlFor="sort">
              정렬
            </label>
            <select id="sort" className="search-select" value={sort} onChange={(event) => setSort(event.target.value)}>
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button className="button primary" type="submit">
              검색
            </button>
          </div>
        </form>
        <div className="search-meta">
          <div className="chip-row">
            <button className={`chip ${categoryId === "" ? "active" : ""}`} type="button" onClick={() => setCategoryId("")}>
              전체
            </button>
            {categories.map((category) => (
              <button
                key={category.id}
                className={`chip ${String(category.id) === categoryId ? "active" : ""}`}
                type="button"
                onClick={() => setCategoryId(String(category.id))}
              >
                {category.name}
              </button>
            ))}
          </div>
          <div className="muted">
            {activeCategoryName ? `${activeCategoryName} · ` : ""}
            상품 {totalCount}개
          </div>
        </div>
      </section>

      {error ? <div className="error-box">{error}</div> : null}

      <section className="section">
        <div className="section-title">
          <h1 className="page-title">상품 목록</h1>
          <Link className="button subtle" href="/items/new">
            상품등록
          </Link>
        </div>

        {isLoading ? (
          <div className="panel empty-state muted">상품을 불러오는 중입니다.</div>
        ) : items.length === 0 ? (
          <div className="panel empty-state">
            <strong>조건에 맞는 상품이 없습니다.</strong>
          </div>
        ) : (
          <div className="product-grid">
            {items.map((item) => (
              <div className="panel product-card" key={item.id}>
                {item.thumbnail_url ? (
                  <button className="image-open-button" type="button" onClick={() => setLightboxImage({ src: item.thumbnail_url!, alt: item.title })}>
                    <img alt={item.title} className="product-thumb" src={`${API_BASE_URL}${item.thumbnail_url}`} />
                  </button>
                ) : (
                  <div className="product-thumb" />
                )}
                <Link className="product-card-link" href={`/items/${item.id}`}>
                  <div className="product-body">
                    <div className={getItemStatusClassName(item.status)}>{formatItemStatus(item.status)}</div>
                    <div className="product-title">{item.title}</div>
                    <div className="price">{item.price.toLocaleString()}원</div>
                    <div className="meta-line">
                      <span>{item.location}</span>
                      <span>{item.seller.nickname}</span>
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>
      {lightboxImage ? (
        <ImageLightbox images={[lightboxImage]} currentIndex={0} onClose={() => setLightboxImage(null)} />
      ) : null}
    </div>
  );
}
