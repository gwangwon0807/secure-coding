# deposit_requests

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `deposit_requests` |
| 설명 | 사용자가 신청하고 관리자가 승인·거절하는 지갑 충전 요청 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `user_id` | integer | FK → `users.id`, INDEX |
| `amount` | integer | 충전 요청 금액, `CHECK (amount > 0)` |
| `status` | enum | `PENDING`, `APPROVED`, `REJECTED`, INDEX |
| `reviewed_by_admin_id` | integer | FK → `users.id`, nullable, INDEX |
| `created_at` | datetime | 요청 시각 |
| `reviewed_at` | datetime | 승인·거절 시각, nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `user_id` | `users.id` |
| `reviewed_by_admin_id` | `users.id` |

## 정합성 규칙

| 항목 | 내용 |
| --- | --- |
| 승인 조건 | `PENDING` 요청만 승인·거절 가능 |
| 중복 승인 | 관리자 처리 시 해당 요청을 `FOR UPDATE`로 잠금 |
| 잔액 반영 | 승인 상태, `wallets.balance`, `wallet_ledgers`를 하나의 DB 트랜잭션으로 처리 |
