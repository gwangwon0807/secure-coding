# items

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `items` |
| 설명 | 상품 정보 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `seller_id` | integer | FK → `users.id`, INDEX |
| `category_id` | integer | FK → `categories.id`, INDEX |
| `title` | varchar(100) | 상품명 |
| `description` | text | 설명 |
| `price` | integer | 가격 |
| `location` | varchar(100) | 지역 |
| `status` | enum | `ON_SALE`, `RESERVED`, `SOLD`, `HIDDEN` |
| `view_count` | integer | default 0 |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `seller_id` | `users.id` |
| `category_id` | `categories.id` |
| `id` | `item_images.item_id`, `chat_rooms.item_id`, `transactions.item_id` |

