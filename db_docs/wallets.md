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
| `balance` | integer | 현재 잔액, default 0, `CHECK (balance >= 0)` |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `user_id` | `users.id` |
| `id` | `wallet_ledgers.wallet_id` |

## 동시성 규칙

| 항목 | 내용 |
| --- | --- |
| 신규 회원 | 회원가입 트랜잭션에서 0원 지갑 생성 |
| 레거시 회원 | 지갑이 없으면 savepoint와 `user_id` UNIQUE를 이용해 1건만 생성 |
| 잔액 변경 | 송금·출금·충전 승인·관리자 조정 시 `SELECT ... FOR UPDATE` 잠금 |
| 잠금 순서 | 복수 지갑은 `user_id` 오름차순으로 잠가 deadlock 위험 감소 |
