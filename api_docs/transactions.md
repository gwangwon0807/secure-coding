# Transactions Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/transactions` |
| 인증 | User |
| 설명 | 거래 요청, 목록/상세 조회, 수락, 거절, 완료, 취소 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/` | User | 거래 요청 생성 | `item_id` |
| GET | `/` | User | 내 거래 목록 조회 | `role`, `page`, `size` |
| GET | `/{transaction_id}` | User | 거래 상세 조회 | - |
| PATCH | `/{transaction_id}/accept` | User | 판매자 수락 | - |
| PATCH | `/{transaction_id}/reject` | User | 판매자 거절 | `reason` |
| PATCH | `/{transaction_id}/complete` | User | 거래 완료 확인 | - |
| PATCH | `/{transaction_id}/cancel` | User | 거래 취소 | `reason` |

## 상태값

| 값 | 설명 |
| --- | --- |
| `REQUESTED` | 요청됨 |
| `ACCEPTED` | 수락됨 |
| `REJECTED` | 거절됨 |
| `CANCELED` | 취소됨 |
| `COMPLETED` | 거래완료 |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 요청 제한 | 자기 상품 거래 요청 불가 |
| 상품 상태 | 거래 불가 상태 상품은 요청 실패 |
| 완료 흐름 | 양측 완료 시 `COMPLETED`, 상품은 `SOLD` |
| 역할 필터 | `buyer`, `seller`, `all` 기준 목록 조회 |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /` | `id`, `item`, `buyer`, `seller`, `status`, `price`, `created_at` |
| `GET /{transaction_id}` | `item`, `buyer`, `seller`, `status`, `buyer_completed`, `seller_completed`, `accepted_at`, `completed_at` |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `CANNOT_REQUEST_OWN_ITEM` | 자기 상품 거래 요청 불가 |
| `ITEM_NOT_AVAILABLE` | 거래 불가 상품 |
| `USER_BLOCKED` | 차단 관계 |
| `TRANSACTION_NOT_FOUND` | 거래 없음 |
| `INVALID_ROLE_VALUE` | role 필터 오류 |
| `INVALID_TRANSACTION_STATUS` | 허용되지 않는 상태 변경 |
| `ITEM_STATUS_CONFLICT` | 상품 상태 충돌 |
| `BUYER_ALREADY_CONFIRMED` | 구매자 중복 완료 |
| `SELLER_ALREADY_CONFIRMED` | 판매자 중복 완료 |
