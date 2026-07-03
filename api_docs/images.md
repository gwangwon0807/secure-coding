# Image Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/images` |
| Method 수 | 3 |
| 담당 기능 | 상품/커뮤니티 이미지 업로드, 이미지 삭제 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/items` | 상품 이미지 업로드 |
| POST | `/community` | 커뮤니티 이미지 업로드 |
| DELETE | `/{image_id}` | 업로드 이미지 삭제 |

## 업로드 규칙

- `multipart/form-data`
- 필드명: `files`
- 확장자: `jpg`, `jpeg`, `png`, `webp`
- MIME: `image/jpeg`, `image/png`, `image/webp`
- 최대 10장

## 삭제 규칙

- 본인 업로드 이미지여야 한다.
- 상품/커뮤니티에 이미 연결된 마지막 이미지는 삭제 불가할 수 있다.
- 판매완료/숨김 상품에 연결된 이미지는 삭제가 제한된다.

## 대표 응답

```json
{
  "images": [
    {
      "id": 1,
      "image_url": "/uploads/abc.jpg",
      "sort_order": 1,
      "created_at": "2026-07-03T12:00:00"
    }
  ]
}
```

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `IMAGE_REQUIRED` | 업로드 파일 없음 |
| `TOO_MANY_IMAGES` | 업로드 개수 초과 |
| `INVALID_IMAGE_EXTENSION` | 허용되지 않는 확장자 |
| `INVALID_IMAGE_MIME_TYPE` | 허용되지 않는 MIME |
| `IMAGE_NOT_FOUND` | 이미지 없음 |
| `CANNOT_DELETE_LAST_IMAGE` | 마지막 이미지 삭제 불가 |
| `IMAGE_ATTACHED_TO_LOCKED_ITEM` | 잠긴 상품에 연결된 이미지 |
