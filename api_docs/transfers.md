# Transfers / Wallet Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/transfers` |
| 인증 | User + CSRF |
| 설명 | 지갑, 충전 요청, 출금, 사용자 간 송금 관리 |

## Endpoint

| Method | Endpoint | 설명 | 핵심 필드 |
| --- | --- | --- | --- |
| GET | `/wallet/me` | 내 지갑 잔액 조회 | - |
| GET | `/wallet/me/ledger` | 내 지갑 원장 조회 | `page`, `size` |
| GET | `/wallet/me/deposit-requests` | 내 충전 요청 내역 | `page`, `size` |
| POST | `/wallet/me/deposit-requests` | 관리자 확인용 충전 요청 | `amount` |
| POST | `/wallet/me/deposit` | 기존 직접 충전 경로 | 항상 `403` |
| POST | `/wallet/me/withdraw` | 내 지갑 출금 | `amount` |
| POST | `/` | 사용자 간 송금 | `recipient_id`, `amount`, `note`, `transaction_id`, `chat_room_id` |
| GET | `/` | 내 송금 내역 | `page`, `size` |
| GET | `/{transfer_id}` | 송금 상세 | - |

## 상태 / 원장 타입

| 구분 | 값 |
| --- | --- |
| 충전 요청 | `PENDING`, `APPROVED`, `REJECTED` |
| 송금 | `COMPLETED`, `CANCELED` |
| 현재 사용 원장 | `ADMIN_ADJUSTMENT`, `DEPOSIT_APPROVED`, `USER_WITHDRAWAL`, `TRANSFER_OUT`, `TRANSFER_IN` |
| 레거시 원장 enum | `INITIAL_CREDIT`, `USER_DEPOSIT` (신규 처리에서 사용하지 않음) |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 초기 잔액 | 회원가입 시 0원 지갑 생성 |
| 충전 | 요청 접수 후 관리자가 승인해야 잔액 반영 |
| 중복 요청 | 사용자별 `PENDING` 충전 요청은 1건만 허용 |
| 송금 대상 | 활성 상태 사용자만 가능 |
| 금액 | 1 이상의 정수 |
| 자기 송금 | 불가 |
| 차단 관계 | 차단 관계의 사용자는 송금 불가 |
| 거래 연결 | `transaction_id`, `chat_room_id`를 선택적으로 기록 |
| 잔액 부족 | 송금과 출금은 `409 INSUFFICIENT_BALANCE` |
| 동시성 | 지갑을 DB `FOR UPDATE`로 잠그고 잔액 검사부터 원장 생성까지 한 트랜잭션으로 처리 |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /wallet/me` | `user`, `balance` |
| `GET /wallet/me/ledger` | `transaction_type`, `amount`, `balance_after`, `description`, `counterparty_user_id` |
| `GET /wallet/me/deposit-requests` | `amount`, `status`, `reviewed_at`, `reviewed_by_admin` |
| `POST /` | `sender`, `recipient`, `amount`, `status`, `transaction_id`, `chat_room_id` |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `DIRECT_DEPOSIT_DISABLED_USE_REQUEST` | 직접 충전 금지, 충전 요청 API 사용 |
| `DEPOSIT_REQUEST_ALREADY_PENDING` | 이미 대기 중인 충전 요청 존재 |
| `CANNOT_TRANSFER_TO_SELF` | 자기 자신에게 송금 |
| `RECIPIENT_NOT_FOUND` | 수신자 없음 |
| `RECIPIENT_NOT_ACTIVE` | 수신자 비활성 |
| `USER_BLOCKED` | 차단 관계 |
| `INSUFFICIENT_BALANCE` | 잔액 부족 |
| `INVALID_TRANSACTION_CONTEXT` | 거래 당사자 불일치 |
| `INVALID_CHAT_ROOM_CONTEXT` | 채팅방 참여자 불일치 |
