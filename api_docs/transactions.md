| 구분            | 내용                                                                                                         |
| ------------- | ---------------------------------------------------------------------------------------------------------- |
| Router        | Transaction Router                                                                                         |
| Prefix        | `/api/v1/transactions`                                                                                     |
| Method 수      | 7개                                                                                                         |
| 담당 기능         | 거래 요청, 내 거래 목록 조회, 거래 상세 조회, 거래 수락, 거래 거절, 거래 완료, 거래 취소                                                    |
| 인증 방식         | JWT + HttpOnly Cookie                                                                                      |
| 관련 테이블        | `transactions`, `items`, `users`                                                                           |
| 주요 Dependency | `get_current_user`, `require_active_user`, `require_transaction_participant`, `require_transaction_seller` |
| MVP 범위        | 실제 결제 없이 거래 상태만 관리                                                                                         |

| 번호 | Method | Endpoint                     | 기능         | 권한          | 설명                          |
| -- | ------ | ---------------------------- | ---------- | ----------- | --------------------------- |
| 1  | POST   | `/`                          | 거래 요청      | User        | 구매자가 특정 상품에 대해 거래 요청 생성     |
| 2  | GET    | `/`                          | 내 거래 목록 조회 | User        | 내가 구매자 또는 판매자로 참여한 거래 목록 조회 |
| 3  | GET    | `/{transaction_id}`          | 거래 상세 조회   | Participant | 특정 거래 상세 정보 조회              |
| 4  | PATCH  | `/{transaction_id}/accept`   | 거래 수락      | Seller      | 판매자가 거래 요청 수락               |
| 5  | PATCH  | `/{transaction_id}/reject`   | 거래 거절      | Seller      | 판매자가 거래 요청 거절               |
| 6  | PATCH  | `/{transaction_id}/complete` | 거래 완료      | Participant | 거래를 완료 처리                   |
| 7  | PATCH  | `/{transaction_id}/cancel`   | 거래 취소      | Participant | 진행 중 거래 취소                  |

---

| API       | POST `/api/v1/transactions`              |
| --------- | ---------------------------------------- |
| 기능        | 거래 요청                                    |
| 권한        | User                                     |
| 설명        | 구매자가 특정 상품에 대해 거래 요청을 생성한다.              |
| 성공 Status | `201 Created`                            |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422` |

| Request Body | Type    | Required | Validation | 설명        |
| ------------ | ------- | -------- | ---------- | --------- |
| item_id      | integer | Yes      | 존재하는 상품 ID | 거래 요청할 상품 |
| price        | integer | Yes      | 0 이상       | 요청 거래 금액  |

| 처리 규칙      | 설명                                  |
| ---------- | ----------------------------------- |
| 로그인 필수     | 비회원은 거래 요청 불가                       |
| 정지 회원 제한   | `SUSPENDED` 상태 사용자는 거래 요청 불가        |
| 본인 상품 제한   | 판매자는 자기 상품에 거래 요청 불가                |
| 상품 존재 확인   | 존재하지 않는 상품이면 요청 불가                  |
| 삭제 상품 제한   | 삭제된 상품은 거래 요청 불가                    |
| 숨김 상품 제한   | `HIDDEN` 상품은 거래 요청 불가               |
| 판매완료 상품 제한 | `SOLD` 상품은 거래 요청 불가                 |
| 중복 요청 제한   | 같은 구매자, 같은 상품에 대해 진행 중 거래 요청 중복 불가  |
| 판매자 자동 설정  | `seller_id`는 상품의 `seller_id`로 자동 저장 |
| 기본 상태      | 거래 생성 시 `REQUESTED` 상태              |

| Response Data | Type     | 설명          |
| ------------- | -------- | ----------- |
| id            | integer  | 거래 ID       |
| item_id       | integer  | 상품 ID       |
| buyer_id      | integer  | 구매자 ID      |
| seller_id     | integer  | 판매자 ID      |
| status        | string   | `REQUESTED` |
| price         | integer  | 거래 요청 금액    |
| created_at    | datetime | 거래 요청 시간    |

| Error Code                      | HTTP Status | 설명                |
| ------------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`                  | 401         | 로그인 필요            |
| `USER_NOT_ACTIVE`               | 403         | 정지 또는 탈퇴 사용자      |
| `ITEM_NOT_FOUND`                | 404         | 상품이 존재하지 않음       |
| `CANNOT_REQUEST_OWN_ITEM`       | 400         | 본인 상품에는 거래 요청 불가  |
| `ITEM_NOT_AVAILABLE`            | 409         | 거래 가능한 상품 상태가 아님  |
| `DUPLICATE_TRANSACTION_REQUEST` | 409         | 이미 진행 중인 거래 요청 존재 |
| `INVALID_PRICE`                 | 422         | 거래 금액 오류          |

---

| API       | GET `/api/v1/transactions`                |
| --------- | ----------------------------------------- |
| 기능        | 내 거래 목록 조회                                |
| 권한        | User                                      |
| 설명        | 현재 로그인한 사용자가 구매자 또는 판매자로 참여한 거래 목록을 조회한다. |
| 성공 Status | `200 OK`                                  |
| 실패 Status | `401`, `403`, `422`                       |

| Query Parameter | Type    | Required | Default | 설명                |
| --------------- | ------- | -------- | ------- | ----------------- |
| role            | string  | No       | null    | `buyer`, `seller` |
| status          | string  | No       | null    | 거래 상태             |
| page            | integer | No       | 1       | 페이지 번호            |
| size            | integer | No       | 20      | 페이지당 거래 수         |

| role 값   | 설명             |
| -------- | -------------- |
| `buyer`  | 내가 구매자인 거래만 조회 |
| `seller` | 내가 판매자인 거래만 조회 |
| null     | 구매/판매 거래 전체 조회 |

| Response Data                     | Type          | 설명        |
| --------------------------------- | ------------- | --------- |
| transactions                      | array         | 거래 목록     |
| transactions[].id                 | integer       | 거래 ID     |
| transactions[].item.id            | integer       | 상품 ID     |
| transactions[].item.title         | string        | 상품명       |
| transactions[].item.thumbnail_url | string/null   | 상품 대표 이미지 |
| transactions[].item.status        | string        | 상품 상태     |
| transactions[].buyer.id           | integer       | 구매자 ID    |
| transactions[].buyer.nickname     | string        | 구매자 닉네임   |
| transactions[].seller.id          | integer       | 판매자 ID    |
| transactions[].seller.nickname    | string        | 판매자 닉네임   |
| transactions[].status             | string        | 거래 상태     |
| transactions[].price              | integer       | 거래 금액     |
| transactions[].created_at         | datetime      | 거래 생성일    |
| transactions[].completed_at       | datetime/null | 거래 완료일    |
| pagination.page                   | integer       | 현재 페이지    |
| pagination.size                   | integer       | 페이지 크기    |
| pagination.total_count            | integer       | 전체 거래 수   |
| pagination.total_pages            | integer       | 전체 페이지 수  |

| Error Code                   | HTTP Status | 설명           |
| ---------------------------- | ----------- | ------------ |
| `UNAUTHORIZED`               | 401         | 로그인 필요       |
| `USER_NOT_ACTIVE`            | 403         | 정지 또는 탈퇴 사용자 |
| `INVALID_ROLE_VALUE`         | 422         | role 값 오류    |
| `INVALID_TRANSACTION_STATUS` | 422         | 거래 상태 값 오류   |
| `INVALID_PAGE_VALUE`         | 422         | 페이지 값 오류     |
| `INVALID_SIZE_VALUE`         | 422         | 페이지 크기 오류    |

---

| API       | GET `/api/v1/transactions/{transaction_id}` |
| --------- | ------------------------------------------- |
| 기능        | 거래 상세 조회                                    |
| 권한        | Participant                                 |
| 설명        | 특정 거래의 상품, 구매자, 판매자, 거래 상태 정보를 조회한다.        |
| 성공 Status | `200 OK`                                    |
| 실패 Status | `401`, `403`, `404`                         |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| transaction_id | integer | Yes      | 조회할 거래 ID |

| Response Data      | Type          | 설명        |
| ------------------ | ------------- | --------- |
| id                 | integer       | 거래 ID     |
| item.id            | integer       | 상품 ID     |
| item.title         | string        | 상품명       |
| item.price         | integer       | 상품 등록 가격  |
| item.thumbnail_url | string/null   | 상품 대표 이미지 |
| item.status        | string        | 상품 상태     |
| buyer.id           | integer       | 구매자 ID    |
| buyer.nickname     | string        | 구매자 닉네임   |
| seller.id          | integer       | 판매자 ID    |
| seller.nickname    | string        | 판매자 닉네임   |
| status             | string        | 거래 상태     |
| price              | integer       | 거래 요청 금액  |
| created_at         | datetime      | 거래 생성일    |
| accepted_at        | datetime/null | 거래 수락일    |
| rejected_at        | datetime/null | 거래 거절일    |
| canceled_at        | datetime/null | 거래 취소일    |
| completed_at       | datetime/null | 거래 완료일    |

| Error Code              | HTTP Status | 설명          |
| ----------------------- | ----------- | ----------- |
| `UNAUTHORIZED`          | 401         | 로그인 필요      |
| `TRANSACTION_NOT_FOUND` | 404         | 거래가 존재하지 않음 |
| `FORBIDDEN`             | 403         | 거래 참여자가 아님  |

---

| API       | PATCH `/api/v1/transactions/{transaction_id}/accept` |
| --------- | ---------------------------------------------------- |
| 기능        | 거래 수락                                                |
| 권한        | Seller                                               |
| 설명        | 판매자가 구매자의 거래 요청을 수락한다. 이때 거래 상태와 상품 상태를 함께 변경한다.     |
| 성공 Status | `200 OK`                                             |
| 실패 Status | `401`, `403`, `404`, `409`                           |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| transaction_id | integer | Yes      | 수락할 거래 ID |

| Request Body | Type | Required | 설명            |
| ------------ | ---- | -------- | ------------- |
| 없음           | -    | -        | 거래 ID 기준으로 처리 |

| 처리 규칙      | 설명                                          |
| ---------- | ------------------------------------------- |
| 판매자 확인     | 현재 사용자가 해당 거래의 판매자여야 함                      |
| 거래 상태 확인   | `REQUESTED` 상태만 수락 가능                       |
| 상품 상태 확인   | 상품이 `ON_SALE` 상태일 때만 수락 가능                  |
| DB 트랜잭션 필수 | 거래 상태와 상품 상태를 원자적으로 변경                      |
| 거래 상태 변경   | `REQUESTED` → `ACCEPTED`                    |
| 상품 상태 변경   | `ON_SALE` → `RESERVED`                      |
| 수락 시간 저장   | `accepted_at` 기록                            |
| 다른 요청 처리   | 같은 상품의 다른 `REQUESTED` 거래는 유지 또는 자동 거절 정책 선택 |

| Response Data | Type     | 설명         |
| ------------- | -------- | ---------- |
| id            | integer  | 거래 ID      |
| status        | string   | `ACCEPTED` |
| item_id       | integer  | 상품 ID      |
| item_status   | string   | `RESERVED` |
| accepted_at   | datetime | 거래 수락 시간   |

| Error Code                   | HTTP Status | 설명                 |
| ---------------------------- | ----------- | ------------------ |
| `UNAUTHORIZED`               | 401         | 로그인 필요             |
| `FORBIDDEN`                  | 403         | 판매자가 아님            |
| `TRANSACTION_NOT_FOUND`      | 404         | 거래가 존재하지 않음        |
| `INVALID_TRANSACTION_STATUS` | 409         | 수락 가능한 거래 상태가 아님   |
| `ITEM_NOT_AVAILABLE`         | 409         | 상품이 판매 가능한 상태가 아님  |
| `TRANSACTION_CONFLICT`       | 409         | 다른 거래로 인해 상태 충돌 발생 |

---

| API       | PATCH `/api/v1/transactions/{transaction_id}/reject` |
| --------- | ---------------------------------------------------- |
| 기능        | 거래 거절                                                |
| 권한        | Seller                                               |
| 설명        | 판매자가 구매자의 거래 요청을 거절한다.                               |
| 성공 Status | `200 OK`                                             |
| 실패 Status | `401`, `403`, `404`, `409`                           |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| transaction_id | integer | Yes      | 거절할 거래 ID |

| Request Body | Type   | Required | Validation | 설명       |
| ------------ | ------ | -------- | ---------- | -------- |
| reason       | string | No       | 최대 300자    | 거래 거절 사유 |

| 처리 규칙    | 설명                       |
| -------- | ------------------------ |
| 판매자 확인   | 현재 사용자가 해당 거래의 판매자여야 함   |
| 거래 상태 확인 | `REQUESTED` 상태만 거절 가능    |
| 거래 상태 변경 | `REQUESTED` → `REJECTED` |
| 상품 상태 유지 | 상품 상태는 변경하지 않음           |
| 거절 시간 저장 | `rejected_at` 기록         |

| Response Data | Type        | 설명         |
| ------------- | ----------- | ---------- |
| id            | integer     | 거래 ID      |
| status        | string      | `REJECTED` |
| rejected_at   | datetime    | 거래 거절 시간   |
| reason        | string/null | 거절 사유      |

| Error Code                   | HTTP Status | 설명               |
| ---------------------------- | ----------- | ---------------- |
| `UNAUTHORIZED`               | 401         | 로그인 필요           |
| `FORBIDDEN`                  | 403         | 판매자가 아님          |
| `TRANSACTION_NOT_FOUND`      | 404         | 거래가 존재하지 않음      |
| `INVALID_TRANSACTION_STATUS` | 409         | 거절 가능한 거래 상태가 아님 |
| `REJECT_REASON_TOO_LONG`     | 422         | 거절 사유 길이 초과      |

---

| API       | PATCH `/api/v1/transactions/{transaction_id}/complete` |
| --------- | ------------------------------------------------------ |
| 기능        | 거래 완료                                                  |
| 권한        | Participant                                            |
| 설명        | 수락된 거래를 완료 처리한다. 상품 상태도 판매완료로 변경한다.                    |
| 성공 Status | `200 OK`                                               |
| 실패 Status | `401`, `403`, `404`, `409`                             |

| Path Parameter | Type    | Required | 설명           |
| -------------- | ------- | -------- | ------------ |
| transaction_id | integer | Yes      | 완료 처리할 거래 ID |

| Request Body | Type | Required | 설명            |
| ------------ | ---- | -------- | ------------- |
| 없음           | -    | -        | 거래 ID 기준으로 처리 |

| 처리 규칙      | 설명                              |
| ---------- | ------------------------------- |
| 참여자 확인     | 구매자 또는 판매자만 완료 처리 가능            |
| 거래 상태 확인   | `ACCEPTED` 상태만 완료 가능            |
| 상품 상태 확인   | 상품이 `RESERVED` 상태여야 함           |
| DB 트랜잭션 필수 | 거래 상태와 상품 상태를 원자적으로 변경          |
| 거래 상태 변경   | `ACCEPTED` → `COMPLETED`        |
| 상품 상태 변경   | `RESERVED` → `SOLD`             |
| 완료 시간 저장   | `completed_at` 기록               |
| 신뢰도 반영     | MVP에서는 제외 가능, 2차에서 거래 횟수/후기와 연결 |

| Response Data | Type     | 설명          |
| ------------- | -------- | ----------- |
| id            | integer  | 거래 ID       |
| status        | string   | `COMPLETED` |
| item_id       | integer  | 상품 ID       |
| item_status   | string   | `SOLD`      |
| completed_at  | datetime | 거래 완료 시간    |

| Error Code                   | HTTP Status | 설명                  |
| ---------------------------- | ----------- | ------------------- |
| `UNAUTHORIZED`               | 401         | 로그인 필요              |
| `FORBIDDEN`                  | 403         | 거래 참여자가 아님          |
| `TRANSACTION_NOT_FOUND`      | 404         | 거래가 존재하지 않음         |
| `INVALID_TRANSACTION_STATUS` | 409         | 완료 가능한 거래 상태가 아님    |
| `ITEM_STATUS_CONFLICT`       | 409         | 상품 상태가 거래 상태와 맞지 않음 |

---

| API       | PATCH `/api/v1/transactions/{transaction_id}/cancel`   |
| --------- | ------------------------------------------------------ |
| 기능        | 거래 취소                                                  |
| 권한        | Participant                                            |
| 설명        | 진행 중인 거래를 취소한다. 수락된 거래를 취소하면 상품 상태를 다시 판매중으로 되돌릴 수 있다. |
| 성공 Status | `200 OK`                                               |
| 실패 Status | `401`, `403`, `404`, `409`, `422`                      |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| transaction_id | integer | Yes      | 취소할 거래 ID |

| Request Body | Type   | Required | Validation | 설명       |
| ------------ | ------ | -------- | ---------- | -------- |
| reason       | string | No       | 최대 300자    | 거래 취소 사유 |

| 처리 규칙          | 설명                                             |
| -------------- | ---------------------------------------------- |
| 참여자 확인         | 구매자 또는 판매자만 취소 가능                              |
| 취소 가능 상태       | `REQUESTED`, `ACCEPTED` 상태만 취소 가능              |
| `REQUESTED` 취소 | 거래 상태만 `CANCELED`로 변경                          |
| `ACCEPTED` 취소  | 거래 상태 `CANCELED`, 상품 상태 `RESERVED` → `ON_SALE` |
| 완료 거래 제한       | `COMPLETED` 거래는 취소 불가                          |
| 거절 거래 제한       | `REJECTED` 거래는 취소 불가                           |
| 취소 시간 저장       | `canceled_at` 기록                               |

| Response Data | Type        | 설명                 |
| ------------- | ----------- | ------------------ |
| id            | integer     | 거래 ID              |
| status        | string      | `CANCELED`         |
| item_id       | integer     | 상품 ID              |
| item_status   | string      | `ON_SALE` 또는 기존 상태 |
| canceled_at   | datetime    | 거래 취소 시간           |
| reason        | string/null | 취소 사유              |

| Error Code                   | HTTP Status | 설명               |
| ---------------------------- | ----------- | ---------------- |
| `UNAUTHORIZED`               | 401         | 로그인 필요           |
| `FORBIDDEN`                  | 403         | 거래 참여자가 아님       |
| `TRANSACTION_NOT_FOUND`      | 404         | 거래가 존재하지 않음      |
| `INVALID_TRANSACTION_STATUS` | 409         | 취소 가능한 거래 상태가 아님 |
| `ITEM_STATUS_CONFLICT`       | 409         | 상품 상태 충돌         |
| `CANCEL_REASON_TOO_LONG`     | 422         | 취소 사유 길이 초과      |

---

| Transaction Status Enum | 설명                 |
| ----------------------- | ------------------ |
| `REQUESTED`             | 구매자가 거래 요청한 상태     |
| `ACCEPTED`              | 판매자가 거래 요청을 수락한 상태 |
| `REJECTED`              | 판매자가 거래 요청을 거절한 상태 |
| `COMPLETED`             | 거래가 완료된 상태         |
| `CANCELED`              | 거래가 취소된 상태         |

| 권장 상태 전이                 | 가능 여부 | 설명                |
| ------------------------ | ----- | ----------------- |
| `REQUESTED` → `ACCEPTED` | 가능    | 판매자가 거래 수락        |
| `REQUESTED` → `REJECTED` | 가능    | 판매자가 거래 거절        |
| `REQUESTED` → `CANCELED` | 가능    | 구매자 또는 판매자가 요청 취소 |
| `ACCEPTED` → `COMPLETED` | 가능    | 거래 완료             |
| `ACCEPTED` → `CANCELED`  | 가능    | 예약 후 거래 취소        |
| `REJECTED` → 다른 상태       | 불가    | 종료 상태             |
| `COMPLETED` → 다른 상태      | 불가    | 종료 상태             |
| `CANCELED` → 다른 상태       | 불가    | 종료 상태             |

| 거래 상태와 상품 상태 연동 | 설명                        |
| --------------- | ------------------------- |
| 거래 생성           | 상품 상태 변경 없음               |
| 거래 수락           | 상품 `ON_SALE` → `RESERVED` |
| 거래 거절           | 상품 상태 변경 없음               |
| 거래 완료           | 상품 `RESERVED` → `SOLD`    |
| 거래 취소           | 수락 전이면 상품 상태 변경 없음        |
| 수락 후 거래 취소      | 상품 `RESERVED` → `ON_SALE` |

| Transaction 관련 Validation | 기준                                                           |
| ------------------------- | ------------------------------------------------------------ |
| transaction_id            | 1 이상의 정수                                                     |
| item_id                   | 존재하는 상품 ID                                                   |
| price                     | 0 이상                                                         |
| reason                    | 최대 300자                                                      |
| role                      | `buyer`, `seller`                                            |
| status                    | `REQUESTED`, `ACCEPTED`, `REJECTED`, `COMPLETED`, `CANCELED` |
| page                      | 1 이상                                                         |
| size                      | 1~100                                                        |

| Transaction Router 설계 근거 | 내용                                     |
| ------------------------ | -------------------------------------- |
| 실제 결제 제외                 | MVP에서는 보안, 환불, 정산 이슈를 줄이기 위해 상태 관리만 구현 |
| 거래 수락 시 DB 트랜잭션 필수       | 거래 상태와 상품 상태가 동시에 변경되어야 함              |
| 구매자/판매자 권한 분리            | 수락/거절은 판매자만 가능해야 함                     |
| 완료/취소는 참여자 기준            | 실제 거래 상황에서 양쪽 모두 완료/취소 요청 가능           |
| 거래 이력 보존                 | 분쟁, 신고, 관리자 확인을 위해 거래 기록 삭제 금지         |
| 상품 상태와 연동                | 사용자에게 판매중/예약중/판매완료 상태를 명확히 보여주기 위함     |
