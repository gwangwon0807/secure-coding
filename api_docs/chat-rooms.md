# Chat Rooms Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/chat-rooms` |
| 인증 | User |
| 설명 | 채팅방 생성, 목록/상세 조회, 메시지 조회/전송, 읽음 처리, 삭제 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/` | User | 채팅방 생성 | `item_id` |
| GET | `/` | User | 내 채팅방 목록 조회 | `page`, `size` |
| GET | `/{room_id}` | User | 채팅방 상세 조회 | - |
| GET | `/{room_id}/messages` | User | 메시지 목록 조회 | `page`, `size` |
| POST | `/{room_id}/messages` | User | 메시지 전송 | `content`, `message_type` |
| PATCH | `/{room_id}/read` | User | 읽음 처리 | `last_read_message_id` |
| DELETE | `/{room_id}` | User | 채팅방 삭제 | - |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 생성 제한 | 자기 상품 채팅 불가 |
| 상품 상태 | `HIDDEN`, `SOLD` 상품 채팅 불가 |
| 차단 관계 | 차단 관계가 있으면 생성/메시지 전송 불가 |
| 중복 방지 | 동일 상품/구매자/판매자 조합은 기존 채팅방 재사용 |
| 메시지 타입 | 현재 `TEXT`만 지원 |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /` | `id`, `item`, `buyer`, `seller`, `last_message`, `unread_count`, `last_message_at` |
| `GET /{room_id}` | `item`, `buyer`, `seller`, `opponent`, `transaction`, `buyer_completed`, `seller_completed` |
| `GET /{room_id}/messages` | `id`, `sender`, `content`, `message_type`, `is_read`, `created_at` |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_CHAT_OWN_ITEM` | 자기 상품 채팅 불가 |
| `ITEM_NOT_AVAILABLE` | 채팅 불가 상품 |
| `USER_BLOCKED` | 차단 관계 |
| `CHAT_ROOM_NOT_FOUND` | 채팅방 없음 |
| `FORBIDDEN` | 참여자 아님 |
| `INVALID_MESSAGE_TYPE` | 메시지 타입 오류 |
| `EMPTY_MESSAGE` | 빈 메시지 |
