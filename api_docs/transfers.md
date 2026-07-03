# Transfers / Wallet Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/transfers` |
| Method 수 | 7 |
| 담당 기능 | 내 지갑 조회, 지갑 원장 조회, 사용자 송금, 송금 조회 |
| 권한 | 인증 필요 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/wallet/me` | 내 지갑 잔액 조회 |
| GET | `/wallet/me/ledger` | 내 지갑 원장 조회 |
| POST | `/wallet/me/deposit` | 내 지갑 입금 |
| POST | `/wallet/me/withdraw` | 내 지갑 출금 |
| POST | `/` | 송금 생성 |
| GET | `/` | 내 송금 내역 조회 |
| GET | `/{transfer_id}` | 송금 상세 조회 |

## 주요 규칙

- 각 사용자는 내부 지갑(`wallet`)을 가진다.
- 지갑이 없는 사용자는 첫 접근 시 테스트용 초기 잔액 `100,000원`이 자동 생성된다.
- 송금은 활성 사용자끼리만 가능하다.
- 자기 자신에게는 송금할 수 없다.
- 차단 관계가 있는 사용자끼리는 송금할 수 없다.
- 거래(`transaction_id`) 또는 채팅방(`chat_room_id`) 컨텍스트를 함께 기록할 수 있다.
- 입금/출금은 MVP 검증용 내부 지갑 잔액 조정 기능이다.

## 주요 요청 예시

### 1. 송금 생성

```json
{
  "recipient_id": 2,
  "amount": 5000,
  "note": "거래 테스트 송금",
  "transaction_id": 1,
  "chat_room_id": 2
}
```

### 2. 지갑 응답 예시

```json
{
  "user": {
    "id": 1,
    "nickname": "판매자"
  },
  "balance": 95000
}
```

## 관련 관리자 API

송금/지갑 관리용 관리자 API는 `api_docs/admin.md`의 아래 엔드포인트를 참고한다.

- `GET /api/v1/admin/wallets`
- `PATCH /api/v1/admin/wallets/{user_id}/adjust`
- `GET /api/v1/admin/transfers`

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `CANNOT_TRANSFER_TO_SELF` | 자기 자신에게 송금 불가 |
| `RECIPIENT_NOT_FOUND` | 수신 사용자 없음 |
| `RECIPIENT_NOT_ACTIVE` | 수신 사용자가 비활성 상태 |
| `USER_BLOCKED` | 차단 관계 사용자 |
| `INSUFFICIENT_BALANCE` | 잔액 부족 |
| `INVALID_TRANSACTION_CONTEXT` | 거래 컨텍스트가 유효하지 않음 |
| `INVALID_CHAT_ROOM_CONTEXT` | 채팅방 컨텍스트가 유효하지 않음 |
