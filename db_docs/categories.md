# categories

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `categories` |
| 설명 | 상품 카테고리 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `name` | varchar(50) | UNIQUE |
| `sort_order` | integer | default 1 |
| `is_active` | boolean | default true |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `id` | `items.category_id` |

