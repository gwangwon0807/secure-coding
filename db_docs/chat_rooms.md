# chat_rooms

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `chat_rooms` |
| 설명 | 상품 기반 채팅방 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `item_id` | integer | FK → `items.id`, INDEX |
| `buyer_id` | integer | FK → `users.id`, INDEX |
| `seller_id` | integer | FK → `users.id`, INDEX |
| `created_at` | datetime | 생성일 |
| `last_message_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `item_id` | `items.id` |
| `buyer_id` | `users.id` |
| `seller_id` | `users.id` |
| `id` | `messages.chat_room_id`, `transfers.chat_room_id` |

