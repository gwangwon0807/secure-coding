# wallets

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `wallets` |
| 설명 | 사용자 지갑 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `user_id` | integer | FK → `users.id`, UNIQUE, INDEX |
| `balance` | integer | 현재 잔액 |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `user_id` | `users.id` |
| `id` | `wallet_ledgers.wallet_id` |

