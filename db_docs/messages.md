# messages

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `messages` |
| 설명 | 채팅 메시지 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `chat_room_id` | integer | FK → `chat_rooms.id`, INDEX |
| `sender_id` | integer | FK → `users.id`, INDEX |
| `content` | text | 메시지 |
| `message_type` | enum | `TEXT` |
| `is_read` | boolean | default false |
| `created_at` | datetime | 생성일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `chat_room_id` | `chat_rooms.id` |
| `sender_id` | `users.id` |

