# Chat Rooms Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/chat-rooms` |
| Method 수 | 7 |
| 담당 기능 | 채팅방 생성, 목록/상세 조회, 메시지 조회/전송, 읽음 처리, 채팅 삭제 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `` | 채팅방 생성 |
| GET | `` | 채팅방 목록 조회 |
| GET | `/{room_id}` | 채팅방 상세 조회 |
| GET | `/{room_id}/messages` | 메시지 목록 조회 |
| POST | `/{room_id}/messages` | 메시지 전송 |
| PATCH | `/{room_id}/read` | 읽음 처리 |
| DELETE | `/{room_id}` | 채팅방 삭제 |

## 채팅방 생성 규칙

- 판매자는 자신의 상품으로 채팅방을 만들 수 없다.
- `HIDDEN`, `SOLD` 상품에는 채팅방 생성 불가
- 차단 관계가 있으면 생성 불가
- 동일 상품/구매자/판매자 조합은 기존 채팅방 재사용

## 채팅방 상세 특징

- `item`, `buyer`, `seller`, `opponent` 정보 포함
- 연관 거래가 있으면 `transaction` 요약 포함
- `buyer_completed`, `seller_completed` 상태 확인 가능

## 메시지 규칙

- 현재는 `TEXT` 타입만 지원
- 공백 메시지는 허용되지 않는다
- 읽음 처리는 `last_read_message_id` 기준 부분 처리 가능

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_CHAT_OWN_ITEM` | 자기 상품 채팅 불가 |
| `ITEM_NOT_AVAILABLE` | 채팅 가능한 상품 상태 아님 |
| `USER_BLOCKED` | 차단 관계 |
| `CHAT_ROOM_NOT_FOUND` | 채팅방 없음 |
| `FORBIDDEN` | 참여자가 아님 |
| `INVALID_MESSAGE_TYPE` | 지원하지 않는 메시지 타입 |
| `EMPTY_MESSAGE` | 빈 메시지 |
