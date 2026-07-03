"use client";

import { useEffect } from "react";

import { API_BASE_URL } from "@/lib/api";

type LightboxImage = {
  src: string;
  alt: string;
};

type ImageLightboxProps = {
  images: LightboxImage[];
  currentIndex: number;
  onClose: () => void;
  onPrev?: () => void;
  onNext?: () => void;
};

export function ImageLightbox({ images, currentIndex, onClose, onPrev, onNext }: ImageLightboxProps) {
  const image = images[currentIndex];

  useEffect(() => {
    function handleKeydown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
      if (event.key === "ArrowLeft" && onPrev) onPrev();
      if (event.key === "ArrowRight" && onNext) onNext();
    }

    window.addEventListener("keydown", handleKeydown);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handleKeydown);
      document.body.style.overflow = "";
    };
  }, [onClose, onNext, onPrev]);

  if (!image) return null;

  return (
    <div className="lightbox-backdrop" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="lightbox-shell" onClick={(event) => event.stopPropagation()}>
        <button className="lightbox-close" type="button" onClick={onClose}>
          닫기
        </button>
        {images.length > 1 && onPrev ? (
          <button className="lightbox-nav prev" type="button" onClick={onPrev}>
            이전
          </button>
        ) : null}
        <img alt={image.alt} className="lightbox-image" src={image.src.startsWith("http") ? image.src : `${API_BASE_URL}${image.src}`} />
        {images.length > 1 && onNext ? (
          <button className="lightbox-nav next" type="button" onClick={onNext}>
            다음
          </button>
        ) : null}
        {images.length > 1 ? <div className="lightbox-count">{currentIndex + 1} / {images.length}</div> : null}
      </div>
    </div>
  );
}
