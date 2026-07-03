# Item Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/items` |
| Method 수 | 6 |
| 담당 기능 | 상품 CRUD, 검색, 상태 변경 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `` | 상품 목록 조회 및 검색 |
| GET | `/{item_id}` | 상품 상세 조회 |
| POST | `` | 상품 등록 |
| PATCH | `/{item_id}` | 상품 수정 |
| DELETE | `/{item_id}` | 상품 삭제 |
| PATCH | `/{item_id}/status` | 상품 상태 변경 |

## 검색 파라미터

| 파라미터 | 설명 |
| --- | --- |
| `keyword` | 상품명/설명 검색 |
| `category_id` | 카테고리 필터 |
| `min_price` | 최소 가격 |
| `max_price` | 최대 가격 |
| `location` | 지역 필터 |
| `status` | 판매 상태 필터 |
| `sort` | `latest`, `price_asc`, `price_desc` |
| `page`, `size` | 페이지네이션 |

## 상품 등록/수정 필드

```json
{
  "title": "아이폰 13",
  "description": "상태 좋음",
  "price": 450000,
  "category_id": 1,
  "location": "서울 성수동",
  "image_ids": [1, 2]
}
```

## 상태 변경 규칙

- 판매자는 `ON_SALE`, `RESERVED`로만 직접 변경 가능
- `SOLD`는 거래 완료 흐름을 통해서만 변경
- 숨김(`HIDDEN`) 상태 상품은 일반 목록에서 제외

## 주요 응답 필드

### 목록
- `id`, `title`, `price`, `location`
- `status`
- `thumbnail_url`
- `seller`

### 상세
- `category`
- `images`
- `seller`
- `view_count`

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `CATEGORY_NOT_FOUND` | 카테고리 없음 |
| `IMAGE_NOT_FOUND` | 이미지 없음 |
| `IMAGE_OWNER_MISMATCH` | 업로드 사용자 불일치 |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_EDIT_SOLD_ITEM` | 판매완료 상품 수정 불가 |
| `CANNOT_EDIT_HIDDEN_ITEM` | 숨김 상품 수정 불가 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래로 삭제 불가 |
| `CANNOT_SET_SOLD_DIRECTLY` | 판매완료 직접 변경 불가 |
| `INVALID_PRICE_RANGE` | 가격 범위 오류 |
| `INVALID_SORT_VALUE` | 정렬 값 오류 |
