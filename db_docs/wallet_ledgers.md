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
| `transaction_type` | enum | `INITIAL_CREDIT`, `ADMIN_ADJUSTMENT`, `USER_DEPOSIT`, `DEPOSIT_APPROVED`, `USER_WITHDRAWAL`, `TRANSFER_OUT`, `TRANSFER_IN` |
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

## 원장 규칙

| 항목 | 내용 |
| --- | --- |
| 충전 승인 | `DEPOSIT_APPROVED`로 기록 |
| 송금 | 발신 지갑에 `TRANSFER_OUT`, 수신 지갑에 `TRANSFER_IN` 생성 |
| `balance_after` | 지갑 행 잠금 후 계산된 처리 직후 잔액 |
| 레거시 타입 | `INITIAL_CREDIT`, `USER_DEPOSIT`은 enum 호환성을 위해 유지하지만 신규 처리에서 사용하지 않음 |
