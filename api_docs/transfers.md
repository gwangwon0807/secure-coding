# Transfers / Wallet Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/transfers` |
| 인증 | User |
| 설명 | 지갑 조회, 원장 조회, 입금/출금, 사용자 송금 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| GET | `/wallet/me` | User | 내 지갑 잔액 조회 | - |
| GET | `/wallet/me/ledger` | User | 내 지갑 원장 조회 | `page`, `size` |
| POST | `/wallet/me/deposit` | User | 내 지갑 입금 | `amount` |
| POST | `/wallet/me/withdraw` | User | 내 지갑 출금 | `amount` |
| POST | `/` | User | 송금 생성 | `recipient_id`, `amount`, `note`, `transaction_id`, `chat_room_id` |
| GET | `/` | User | 내 송금 내역 조회 | `page`, `size` |
| GET | `/{transfer_id}` | User | 송금 상세 조회 | - |

## 상태값

| 구분 | 값 |
| --- | --- |
| 송금 상태 | `COMPLETED`, `CANCELED` |
| 원장 타입 | `INITIAL_CREDIT`, `ADMIN_ADJUSTMENT`, `USER_DEPOSIT`, `USER_WITHDRAWAL`, `TRANSFER_OUT`, `TRANSFER_IN` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 지갑 생성 | 첫 접근 시 초기 잔액 `100000` 자동 생성 |
| 송금 제한 | 활성 사용자끼리만 가능 |
| 자기 송금 | 자기 자신에게 송금 불가 |
| 차단 관계 | 차단 관계 사용자는 송금 불가 |
| 문맥 연결 | `transaction_id`, `chat_room_id` 기록 가능 |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /wallet/me` | `user`, `balance` |
| `GET /wallet/me/ledger` | `id`, `transaction_type`, `amount`, `balance_after`, `description`, `created_at` |
| `GET /` | `id`, `sender`, `recipient`, `amount`, `note`, `status`, `created_at` |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `CANNOT_TRANSFER_TO_SELF` | 자기 자신 송금 불가 |
| `RECIPIENT_NOT_FOUND` | 수신자 없음 |
| `RECIPIENT_NOT_ACTIVE` | 수신자 비활성 |
| `USER_BLOCKED` | 차단 관계 |
| `INSUFFICIENT_BALANCE` | 잔액 부족 |
| `INVALID_TRANSACTION_CONTEXT` | 거래 문맥 오류 |
| `INVALID_CHAT_ROOM_CONTEXT` | 채팅방 문맥 오류 |
