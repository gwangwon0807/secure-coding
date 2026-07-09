# wallet_ledgers

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `wallet_ledgers` |
| 설명 | 지갑 원장 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `wallet_id` | integer | FK → `wallets.id`, INDEX |
| `transfer_id` | integer | FK → `transfers.id`, nullable, INDEX |
| `transaction_type` | enum | `INITIAL_CREDIT`, `ADMIN_ADJUSTMENT`, `USER_DEPOSIT`, `USER_WITHDRAWAL`, `TRANSFER_OUT`, `TRANSFER_IN` |
| `amount` | integer | 증감 금액 |
| `balance_after` | integer | 처리 후 잔액 |
| `description` | text | 설명 |
| `counterparty_user_id` | integer | FK → `users.id`, nullable, INDEX |
| `created_at` | datetime | 생성일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `wallet_id` | `wallets.id` |
| `transfer_id` | `transfers.id` |
| `counterparty_user_id` | `users.id` |

