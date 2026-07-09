"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";

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

const STATUS_OPTIONS = [
  { value: "", label: "전체 상태" },
  { value: "ON_SALE", label: "판매중" },
  { value: "RESERVED", label: "예약중" },
  { value: "SOLD", label: "거래완료" },
];

function formatPriceFilterLabel(minPrice: string, maxPrice: string) {
  if (minPrice && maxPrice) return `${Number(minPrice).toLocaleString()}원 ~ ${Number(maxPrice).toLocaleString()}원`;
  if (minPrice) return `${Number(minPrice).toLocaleString()}원 이상`;
  if (maxPrice) return `${Number(maxPrice).toLocaleString()}원 이하`;
  return "";
}

function HomePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialKeyword = searchParams.get("keyword") || "";
  const initialCategoryId = searchParams.get("category_id") || "";
  const initialMinPrice = searchParams.get("min_price") || "";
  const initialMaxPrice = searchParams.get("max_price") || "";
  const initialLocation = searchParams.get("location") || "";
  const initialStatus = searchParams.get("status") || "";
  const initialSort = searchParams.get("sort") || "latest";

  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [keyword, setKeyword] = useState(initialKeyword);
  const [submittedKeyword, setSubmittedKeyword] = useState(initialKeyword);
  const [categoryId, setCategoryId] = useState(initialCategoryId);
  const [minPrice, setMinPrice] = useState(initialMinPrice);
  const [maxPrice, setMaxPrice] = useState(initialMaxPrice);
  const [location, setLocation] = useState(initialLocation);
  const [statusFilter, setStatusFilter] = useState(initialStatus);
  const [sort, setSort] = useState(initialSort);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [lightboxImage, setLightboxImage] = useState<{ src: string; alt: string } | null>(null);
  const hasInvalidPriceRange = Boolean(minPrice && maxPrice && Number(minPrice) > Number(maxPrice));

  useEffect(() => {
    apiFetch<{ categories: Category[] }>("/api/v1/categories")
      .then((data) => setCategories(data.categories))
      .catch((err) => setError(err instanceof Error ? err.message : "카테고리를 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    if (hasInvalidPriceRange) {
      setItems([]);
      setTotalCount(0);
      setIsLoading(false);
      setError("최소 가격은 최대 가격보다 클 수 없습니다.");
      return;
    }
    const search = new URLSearchParams();
    if (submittedKeyword.trim()) search.set("keyword", submittedKeyword.trim());
    if (categoryId) search.set("category_id", categoryId);
    if (minPrice) search.set("min_price", minPrice);
    if (maxPrice) search.set("max_price", maxPrice);
    if (location.trim()) search.set("location", location.trim());
    if (statusFilter) search.set("status", statusFilter);
    if (sort) search.set("sort", sort);
    router.replace(search.toString() ? `/?${search.toString()}` : "/", { scroll: false });
    setIsLoading(true);
    setError("");
    apiFetch<ItemResponse>(`/api/v1/items?${search.toString()}`)
      .then((data) => {
        setItems(data.items);
        setTotalCount(data.pagination.total_count);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "상품 목록을 불러오지 못했습니다."))
      .finally(() => setIsLoading(false));
  }, [submittedKeyword, categoryId, minPrice, maxPrice, location, statusFilter, sort, router, hasInvalidPriceRange]);

  const activeCategoryName = useMemo(
    () => categories.find((category) => String(category.id) === categoryId)?.name,
    [categories, categoryId],
  );

  const activeFilters = useMemo(
    () => [
      submittedKeyword.trim() ? { key: "keyword", label: `검색어 ${submittedKeyword.trim()}` } : null,
      activeCategoryName ? { key: "category", label: activeCategoryName } : null,
      minPrice || maxPrice ? { key: "price", label: formatPriceFilterLabel(minPrice, maxPrice) } : null,
      location.trim() ? { key: "location", label: `지역 ${location.trim()}` } : null,
      statusFilter ? { key: "status", label: formatItemStatus(statusFilter) } : null,
    ].filter(Boolean) as Array<{ key: string; label: string }>,
    [submittedKeyword, activeCategoryName, minPrice, maxPrice, location, statusFilter],
  );

  function resetFilters() {
    setKeyword("");
    setSubmittedKeyword("");
    setCategoryId("");
    setMinPrice("");
    setMaxPrice("");
    setLocation("");
    setStatusFilter("");
    setSort("latest");
  }

  function clearFilter(key: string) {
    if (key === "keyword") {
      setKeyword("");
      setSubmittedKeyword("");
    }
    if (key === "category") setCategoryId("");
    if (key === "price") {
      setMinPrice("");
      setMaxPrice("");
    }
    if (key === "location") setLocation("");
    if (key === "status") setStatusFilter("");
  }

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
          <div className="search-row search-row-extended">
            <label className="sr-only" htmlFor="min-price">
              최소 가격
            </label>
            <input
              id="min-price"
              className="search-input"
              inputMode="numeric"
              value={minPrice}
              onChange={(event) => setMinPrice(event.target.value.replace(/[^0-9]/g, ""))}
              placeholder="최소 가격"
            />
            <label className="sr-only" htmlFor="max-price">
              최대 가격
            </label>
            <input
              id="max-price"
              className="search-input"
              inputMode="numeric"
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value.replace(/[^0-9]/g, ""))}
              placeholder="최대 가격"
            />
            <label className="sr-only" htmlFor="location">
              지역
            </label>
            <input
              id="location"
              className="search-input"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="지역으로 검색"
            />
            <label className="sr-only" htmlFor="status">
              판매 상태
            </label>
            <select id="status" className="search-select" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button className="button subtle" type="button" onClick={resetFilters}>
              초기화
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
        {activeFilters.length > 0 ? (
          <div className="active-filter-row">
            {activeFilters.map((filter) => (
              <button key={filter.key} className="active-filter-chip" type="button" onClick={() => clearFilter(filter.key)}>
                <span>{filter.label}</span>
                <strong>×</strong>
              </button>
            ))}
          </div>
        ) : null}
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
        ) : hasInvalidPriceRange ? (
          <div className="panel empty-state">
            <strong>가격 범위를 다시 확인해 주세요.</strong>
          </div>
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

export default function HomePage() {
  return (
    <Suspense fallback={<div className="panel empty-state muted">상품을 불러오는 중입니다.</div>}>
      <HomePageContent />
    </Suspense>
  );
}
