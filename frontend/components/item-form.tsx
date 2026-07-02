"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { API_BASE_URL, apiFetch, apiFormFetch } from "@/lib/api";

type Category = { id: number; name: string };
type UploadedImage = { id: number; image_url: string };
type ItemPayload = {
  title: string;
  description: string;
  price: number;
  category_id: number;
  location: string;
  image_ids: number[];
};

type ItemFormProps = {
  mode: "create" | "edit";
  itemId?: number;
  initialValues?: {
    title: string;
    description: string;
    price: number;
    category_id: number;
    location: string;
    images: UploadedImage[];
  };
};

export function ItemForm({ mode, itemId, initialValues }: ItemFormProps) {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>(initialValues?.images ?? []);
  const [title, setTitle] = useState(initialValues?.title ?? "");
  const [description, setDescription] = useState(initialValues?.description ?? "");
  const [price, setPrice] = useState(initialValues?.price ? String(initialValues.price) : "");
  const [categoryId, setCategoryId] = useState(initialValues?.category_id ? String(initialValues.category_id) : "");
  const [location, setLocation] = useState(initialValues?.location ?? "");
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    apiFetch<{ categories: Category[] }>("/api/v1/categories")
      .then((data) => setCategories(data.categories))
      .catch((err) => setError(err instanceof Error ? err.message : "카테고리를 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    if (!initialValues) return;
    setUploadedImages(initialValues.images);
    setTitle(initialValues.title);
    setDescription(initialValues.description);
    setPrice(String(initialValues.price));
    setCategoryId(String(initialValues.category_id));
    setLocation(initialValues.location);
  }, [initialValues]);

  async function handleImages(files: FileList | null) {
    if (!files || files.length === 0) return;
    setError("");
    setIsUploading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append("files", file));
      const result = await apiFormFetch<{ images: UploadedImage[] }>("/api/v1/images/items", formData);
      setUploadedImages((prev) => [...prev, ...result.images]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "이미지 업로드에 실패했습니다.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (uploadedImages.length === 0) {
      setError("상품 이미지를 1장 이상 업로드해 주세요.");
      return;
    }
    setError("");
    setIsSubmitting(true);

    const payload: ItemPayload = {
      title,
      description,
      price: Number(price),
      category_id: Number(categoryId),
      location,
      image_ids: uploadedImages.map((image) => image.id),
    };

    try {
      if (mode === "create") {
        const created = await apiFetch<{ id: number }>("/api/v1/items", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        router.push(`/items/${created.id}`);
      } else {
        await apiFetch(`/api/v1/items/${itemId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
        router.push(`/items/${itemId}`);
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : mode === "create" ? "상품 등록에 실패했습니다." : "상품 수정에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel single-form-panel item-create-panel">
      <div className="section-title compact">
        <h1 className="page-title">{mode === "create" ? "상품 등록" : "상품 수정"}</h1>
      </div>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="title">
            상품명
          </label>
          <input id="title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="예: 아이폰 13 미드나이트 128GB" />
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="description">
            설명
          </label>
          <textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="상태, 사용감, 구성품을 적어 주세요." />
        </div>
        <div className="split-fields">
          <div className="field-group">
            <label className="field-label" htmlFor="price">
              가격
            </label>
            <input id="price" min="0" type="number" value={price} onChange={(event) => setPrice(event.target.value)} />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="category_id">
              카테고리
            </label>
            <select id="category_id" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
              <option value="">선택</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="location">
            거래 지역
          </label>
          <input id="location" value={location} onChange={(event) => setLocation(event.target.value)} placeholder="예: 서울 성수동" />
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
                <img alt="업로드 이미지" className="product-thumb" src={`${API_BASE_URL}${image.image_url}`} />
                <button className="button subtle" type="button" onClick={() => setUploadedImages((prev) => prev.filter((value) => value.id !== image.id))}>
                  제거
                </button>
              </div>
            ))}
          </div>
        ) : null}
        {error ? <div className="error-box">{error}</div> : null}
        <button className="button primary form-submit-button" disabled={isUploading || isSubmitting} type="submit">
          {isSubmitting ? (mode === "create" ? "등록 중..." : "저장 중...") : mode === "create" ? "등록하기" : "저장하기"}
        </button>
      </form>
    </section>
  );
}
