# Image Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/images` |
| 인증 | User |
| 설명 | 상품/커뮤니티 이미지 업로드, 이미지 삭제 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/items` | User | 상품 이미지 업로드 | `files[]` |
| POST | `/community` | User | 커뮤니티 이미지 업로드 | `files[]` |
| DELETE | `/{image_id}` | User | 이미지 삭제 | - |

## 업로드 규칙

| 항목 | 내용 |
| --- | --- |
| 요청 형식 | `multipart/form-data` |
| 필드명 | `files` |
| 확장자 | `jpg`, `jpeg`, `png`, `webp` |
| MIME | `image/jpeg`, `image/png`, `image/webp` |
| 개수 제한 | 최대 10장 |

## 응답 핵심

| 필드 | 설명 |
| --- | --- |
| `id` | 이미지 ID |
| `image_url` | 공개 URL |
| `sort_order` | 정렬 순서 |
| `created_at` | 생성일 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `IMAGE_REQUIRED` | 업로드 파일 없음 |
| `TOO_MANY_IMAGES` | 파일 개수 초과 |
| `INVALID_IMAGE_EXTENSION` | 확장자 오류 |
| `INVALID_IMAGE_MIME_TYPE` | MIME 오류 |
| `IMAGE_NOT_FOUND` | 이미지 없음 |
| `CANNOT_DELETE_LAST_IMAGE` | 마지막 이미지 삭제 불가 |
| `IMAGE_ATTACHED_TO_LOCKED_ITEM` | 잠긴 상품 이미지 삭제 불가 |
