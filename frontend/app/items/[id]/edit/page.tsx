"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { ItemForm } from "@/components/item-form";
import { apiFetch } from "@/lib/api";

type ItemDetail = {
  id: number;
  title: string;
  description: string;
  price: number;
  location: string;
  category: { id: number; name: string };
  images: Array<{ id: number; image_url: string }>;
};

export default function EditItemPage() {
  const params = useParams<{ id: string }>();
  const [item, setItem] = useState<ItemDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<ItemDetail>(`/api/v1/items/${params.id}`)
      .then(setItem)
      .catch((err) => setError(err instanceof Error ? err.message : "상품 정보를 불러오지 못했습니다."));
  }, [params.id]);

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  if (!item) {
    return <div className="panel empty-state muted">상품 정보를 불러오는 중입니다.</div>;
  }

  return (
    <AuthGuard>
      <ItemForm
        mode="edit"
        itemId={item.id}
        initialValues={{
          title: item.title,
          description: item.description,
          price: item.price,
          category_id: item.category.id,
          location: item.location,
          images: item.images.map((image) => ({ id: image.id, image_url: image.image_url })),
        }}
      />
    </AuthGuard>
  );
}
