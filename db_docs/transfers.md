# transfers

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `transfers` |
| 설명 | 사용자 간 송금 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `sender_id` | integer | FK → `users.id`, INDEX |
| `recipient_id` | integer | FK → `users.id`, INDEX |
| `amount` | integer | 송금 금액, `CHECK (amount > 0)` |
| `note` | varchar(200) | nullable |
| `status` | enum | `COMPLETED`, `CANCELED` |
| `transaction_id` | integer | FK → `transactions.id`, nullable, INDEX |
| `chat_room_id` | integer | FK → `chat_rooms.id`, nullable, INDEX |
| `created_at` | datetime | 생성일 |
| `canceled_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `sender_id` | `users.id` |
| `recipient_id` | `users.id` |
| `transaction_id` | `transactions.id` |
| `chat_room_id` | `chat_rooms.id` |
| `id` | `wallet_ledgers.transfer_id` |

## 정합성 규칙

| 항목 | 내용 |
| --- | --- |
| 원자성 | 발신 차감, 수신 증가, 송금 및 양쪽 원장 기록을 한 트랜잭션으로 처리 |
| 경쟁 조건 | 발신자·수신자 지갑을 `FOR UPDATE`로 잠그고 잠금 후 잔액 재검사 |
| 잔액 부족 | 전체 트랜잭션을 중단하고 송금·원장을 생성하지 않음 |
