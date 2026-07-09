# Item Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/items` |
| 인증 | Public / User 혼합 |
| 설명 | 상품 CRUD, 검색, 상태 변경 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| GET | `/` | Public | 상품 목록 조회 / 검색 | `keyword`, `category_id`, `min_price`, `max_price`, `location`, `status`, `sort`, `page`, `size` |
| GET | `/{item_id}` | Public | 상품 상세 조회 | - |
| POST | `/` | User | 상품 등록 | `title`, `description`, `price`, `category_id`, `location`, `image_ids` |
| PATCH | `/{item_id}` | User | 상품 수정 | `title`, `description`, `price`, `category_id`, `location`, `image_ids` |
| DELETE | `/{item_id}` | User | 상품 삭제 | - |
| PATCH | `/{item_id}/status` | User | 상품 상태 변경 | `status` |

## 정렬 / 상태값

| 구분 | 값 |
| --- | --- |
| 정렬 | `latest`, `price_asc`, `price_desc` |
| 상품 상태 | `ON_SALE`, `RESERVED`, `SOLD`, `HIDDEN` |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /` | `id`, `title`, `price`, `location`, `status`, `thumbnail_url`, `seller`, `created_at` |
| `GET /{item_id}` | `title`, `description`, `price`, `category`, `location`, `status`, `images`, `seller`, `view_count` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 수정 제한 | `SOLD`, `HIDDEN` 상품 수정 불가 |
| 상태 변경 | 판매자는 `ON_SALE`, `RESERVED`만 직접 변경 |
| 완료 처리 | `SOLD`는 거래 완료 흐름에서만 반영 |
| 목록 노출 | `deleted_at` 또는 `HIDDEN` 상품 제외 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `CATEGORY_NOT_FOUND` | 카테고리 없음 |
| `IMAGE_NOT_FOUND` | 이미지 없음 |
| `IMAGE_OWNER_MISMATCH` | 이미지 소유자 불일치 |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_EDIT_SOLD_ITEM` | 판매완료 수정 불가 |
| `CANNOT_EDIT_HIDDEN_ITEM` | 숨김 상품 수정 불가 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래 존재 |
| `CANNOT_SET_SOLD_DIRECTLY` | 판매완료 직접 설정 불가 |
| `INVALID_PRICE_RANGE` | 가격 범위 오류 |
| `INVALID_SORT_VALUE` | 정렬 값 오류 |
