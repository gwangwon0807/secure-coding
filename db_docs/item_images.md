# item_images

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `item_images` |
| 설명 | 상품 이미지 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `item_id` | integer | FK → `items.id`, nullable, INDEX |
| `uploader_id` | integer | FK → `users.id`, INDEX |
| `image_url` | varchar(500) | 공개 URL |
| `storage_key` | varchar(500) | 저장 키 |
| `sort_order` | integer | default 1 |
| `status` | enum | `TEMP`, `ATTACHED`, `DELETED` |
| `created_at` | datetime | 생성일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `item_id` | `items.id` |
| `uploader_id` | `users.id` |

