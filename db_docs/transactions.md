# transactions

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `transactions` |
| 설명 | 거래 정보 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `item_id` | integer | FK → `items.id`, INDEX |
| `buyer_id` | integer | FK → `users.id`, INDEX |
| `seller_id` | integer | FK → `users.id`, INDEX |
| `status` | enum | `REQUESTED`, `ACCEPTED`, `REJECTED`, `CANCELED`, `COMPLETED` |
| `price` | integer | 거래 금액 |
| `reject_reason` | varchar(300) | nullable |
| `cancel_reason` | varchar(300) | nullable |
| `created_at` | datetime | 생성일 |
| `accepted_at` | datetime | nullable |
| `rejected_at` | datetime | nullable |
| `canceled_at` | datetime | nullable |
| `completed_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `item_id` | `items.id` |
| `buyer_id` | `users.id` |
| `seller_id` | `users.id` |
| `id` | `transfers.transaction_id` |

