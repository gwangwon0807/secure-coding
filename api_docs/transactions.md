# Transaction Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/transactions` |
| Method 수 | 7 |
| 담당 기능 | 거래 요청, 목록/상세 조회, 수락, 거절, 완료, 취소 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `` | 거래 요청 생성 |
| GET | `` | 내 거래 목록 조회 |
| GET | `/{transaction_id}` | 거래 상세 조회 |
| PATCH | `/{transaction_id}/accept` | 판매자 완료 확인 |
| PATCH | `/{transaction_id}/reject` | 판매자 거절 |
| PATCH | `/{transaction_id}/complete` | 거래 완료 확인 |
| PATCH | `/{transaction_id}/cancel` | 거래 취소 |

## 현재 거래 모델 특징

- `REQUESTED`: 구매 의사/거래 요청
- `ACCEPTED`: 한쪽 또는 양쪽 완료 대기
- `COMPLETED`: 양측 완료
- `REJECTED`, `CANCELED`: 종료

## 상태 흐름

1. 구매자가 거래 요청 생성
2. 판매자가 상품 상태를 `RESERVED`로 변경
3. 구매자/판매자가 각각 완료 확인
4. 양측 완료 시 거래 `COMPLETED`, 상품 `SOLD`

## 주요 응답 필드

- `item`
- `buyer`
- `seller`
- `status`
- `buyer_completed`
- `seller_completed`
- `price`
- `created_at`, `accepted_at`, `rejected_at`, `canceled_at`, `completed_at`

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_REQUEST_OWN_ITEM` | 자기 상품 거래 요청 불가 |
| `ITEM_NOT_AVAILABLE` | 거래 불가 상품 |
| `USER_BLOCKED` | 차단 관계 |
| `TRANSACTION_NOT_FOUND` | 거래 없음 |
| `INVALID_ROLE_VALUE` | role 필터 오류 |
| `INVALID_TRANSACTION_STATUS` | 현재 상태에서 허용되지 않는 처리 |
| `ITEM_STATUS_CONFLICT` | 상품 상태 충돌 |
| `BUYER_ALREADY_CONFIRMED` | 구매자 중복 완료 |
| `SELLER_ALREADY_CONFIRMED` | 판매자 중복 완료 |
