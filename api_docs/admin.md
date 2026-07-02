| 구분            | 내용                                                        |
| ------------- | --------------------------------------------------------- |
| Router        | Admin Router                                              |
| Prefix        | `/api/v1/admin`                                           |
| Method 수      | 9개                                                        |
| 담당 기능         | 회원 관리, 상품 관리, 신고 처리, 거래 조회, 관리자 조치 로그 조회                  |
| 인증 방식         | JWT + HttpOnly Cookie                                     |
| 권한            | Admin                                                     |
| 관련 테이블        | `users`, `items`, `reports`, `transactions`, `audit_logs` |
| 주요 Dependency | `get_current_user`, `require_admin`                       |
| 비고            | 관리자 API는 모든 변경 작업을 `audit_logs`에 기록하는 것을 권장               |

| 번호 | Method | Endpoint                  | 기능           | 권한    | 설명                       |
| -- | ------ | ------------------------- | ------------ | ----- | ------------------------ |
| 1  | GET    | `/users`                  | 회원 목록 조회     | Admin | 전체 회원 목록 조회, 검색, 상태 필터   |
| 2  | PATCH  | `/users/{user_id}/status` | 회원 상태 변경     | Admin | 회원 정지, 정지 해제, 탈퇴 처리      |
| 3  | GET    | `/items`                  | 상품 목록 조회     | Admin | 전체 상품 목록 조회, 신고/숨김 상품 확인 |
| 4  | PATCH  | `/items/{item_id}/status` | 상품 상태 변경     | Admin | 상품 숨김, 복구, 삭제 처리         |
| 5  | GET    | `/reports`                | 신고 목록 조회     | Admin | 접수된 신고 목록 조회             |
| 6  | GET    | `/reports/{report_id}`    | 신고 상세 조회     | Admin | 특정 신고의 상세 내용 조회          |
| 7  | PATCH  | `/reports/{report_id}`    | 신고 처리        | Admin | 신고 상태 변경 및 운영 조치         |
| 8  | GET    | `/transactions`           | 전체 거래 목록 조회  | Admin | 전체 거래 요청/완료/취소 내역 조회     |
| 9  | GET    | `/audit-logs`             | 관리자 조치 로그 조회 | Admin | 관리자 처리 이력 조회             |

---

| API       | GET `/api/v1/admin/users`                        |
| --------- | ------------------------------------------------ |
| 기능        | 회원 목록 조회                                         |
| 권한        | Admin                                            |
| 설명        | 관리자가 전체 회원 목록을 조회한다. 이메일, 닉네임, 상태 기준으로 검색할 수 있다. |
| 성공 Status | `200 OK`                                         |
| 실패 Status | `401`, `403`, `422`                              |

| Query Parameter | Type    | Required | Default | 설명              |
| --------------- | ------- | -------- | ------- | --------------- |
| keyword         | string  | No       | null    | 이메일 또는 닉네임 검색어  |
| status          | string  | No       | null    | 회원 상태 필터        |
| role            | string  | No       | null    | `USER`, `ADMIN` |
| page            | integer | No       | 1       | 페이지 번호          |
| size            | integer | No       | 20      | 페이지당 회원 수       |

| Response Data          | Type     | 설명       |
| ---------------------- | -------- | -------- |
| users                  | array    | 회원 목록    |
| users[].id             | integer  | 회원 ID    |
| users[].email          | string   | 이메일      |
| users[].nickname       | string   | 닉네임      |
| users[].role           | string   | 회원 권한    |
| users[].status         | string   | 회원 상태    |
| users[].trust_score    | integer  | 신뢰도 점수   |
| users[].trade_count    | integer  | 거래 완료 수  |
| users[].report_count   | integer  | 신고 받은 횟수 |
| users[].created_at     | datetime | 가입일      |
| pagination.page        | integer  | 현재 페이지   |
| pagination.size        | integer  | 페이지 크기   |
| pagination.total_count | integer  | 전체 회원 수  |
| pagination.total_pages | integer  | 전체 페이지 수 |

| Error Code            | HTTP Status | 설명         |
| --------------------- | ----------- | ---------- |
| `UNAUTHORIZED`        | 401         | 로그인 필요     |
| `ADMIN_REQUIRED`      | 403         | 관리자 권한 필요  |
| `INVALID_USER_STATUS` | 422         | 회원 상태 값 오류 |
| `INVALID_ROLE_VALUE`  | 422         | 권한 값 오류    |
| `INVALID_PAGE_VALUE`  | 422         | 페이지 값 오류   |
| `INVALID_SIZE_VALUE`  | 422         | 페이지 크기 오류  |

---

| API       | PATCH `/api/v1/admin/users/{user_id}/status` |
| --------- | -------------------------------------------- |
| 기능        | 회원 상태 변경                                     |
| 권한        | Admin                                        |
| 설명        | 관리자가 특정 회원의 상태를 정상, 정지, 탈퇴로 변경한다.            |
| 성공 Status | `200 OK`                                     |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422`     |

| Path Parameter | Type    | Required | 설명            |
| -------------- | ------- | -------- | ------------- |
| user_id        | integer | Yes      | 상태를 변경할 회원 ID |

| Request Body | Type   | Required | Validation                       | 설명        |
| ------------ | ------ | -------- | -------------------------------- | --------- |
| status       | string | Yes      | `ACTIVE`, `SUSPENDED`, `DELETED` | 변경할 회원 상태 |
| reason       | string | Yes      | 1~500자                           | 상태 변경 사유  |

| 처리 규칙       | 설명                                           |
| ----------- | -------------------------------------------- |
| 관리자 권한 필수   | 일반 사용자는 접근 불가                                |
| 자기 자신 제재 제한 | 관리자가 자기 계정을 정지/탈퇴 처리하지 못하게 제한 권장             |
| 탈퇴 회원 복구 제한 | `DELETED` → `ACTIVE` 복구는 정책적으로 제한 가능         |
| 진행 중 거래 확인  | 진행 중 거래가 있는 회원은 탈퇴 처리 제한 가능                  |
| 로그 기록       | 상태 변경 사유, 관리자 ID, 대상 회원 ID를 `audit_logs`에 저장 |

| Response Data   | Type     | 설명     |
| --------------- | -------- | ------ |
| id              | integer  | 회원 ID  |
| previous_status | string   | 이전 상태  |
| status          | string   | 변경된 상태 |
| reason          | string   | 변경 사유  |
| updated_at      | datetime | 변경 시간  |

| Error Code                  | HTTP Status | 설명                |
| --------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요            |
| `ADMIN_REQUIRED`            | 403         | 관리자 권한 필요         |
| `USER_NOT_FOUND`            | 404         | 회원이 존재하지 않음       |
| `CANNOT_UPDATE_SELF_STATUS` | 400         | 자기 자신의 상태 변경 불가   |
| `INVALID_USER_STATUS`       | 422         | 허용되지 않는 회원 상태     |
| `ACTIVE_TRANSACTION_EXISTS` | 409         | 진행 중 거래가 있어 처리 불가 |
| `REASON_REQUIRED`           | 422         | 상태 변경 사유 누락       |

---

| API       | GET `/api/v1/admin/items`                                |
| --------- | -------------------------------------------------------- |
| 기능        | 상품 목록 조회                                                 |
| 권한        | Admin                                                    |
| 설명        | 관리자가 전체 상품 목록을 조회한다. 일반 사용자에게 보이지 않는 숨김/삭제 상품도 조회할 수 있다. |
| 성공 Status | `200 OK`                                                 |
| 실패 Status | `401`, `403`, `422`                                      |

| Query Parameter | Type    | Required | Default | 설명           |
| --------------- | ------- | -------- | ------- | ------------ |
| keyword         | string  | No       | null    | 상품명 또는 설명 검색 |
| seller_id       | integer | No       | null    | 판매자 ID       |
| category_id     | integer | No       | null    | 카테고리 ID      |
| status          | string  | No       | null    | 상품 상태        |
| reported_only   | boolean | No       | false   | 신고된 상품만 조회   |
| page            | integer | No       | 1       | 페이지 번호       |
| size            | integer | No       | 20      | 페이지당 상품 수    |

| Response Data           | Type          | 설명       |
| ----------------------- | ------------- | -------- |
| items                   | array         | 상품 목록    |
| items[].id              | integer       | 상품 ID    |
| items[].title           | string        | 상품명      |
| items[].price           | integer       | 상품 가격    |
| items[].status          | string        | 상품 상태    |
| items[].seller.id       | integer       | 판매자 ID   |
| items[].seller.email    | string        | 판매자 이메일  |
| items[].seller.nickname | string        | 판매자 닉네임  |
| items[].report_count    | integer       | 신고 수     |
| items[].created_at      | datetime      | 등록일      |
| items[].updated_at      | datetime      | 수정일      |
| items[].deleted_at      | datetime/null | 삭제 처리 시간 |
| pagination.page         | integer       | 현재 페이지   |
| pagination.size         | integer       | 페이지 크기   |
| pagination.total_count  | integer       | 전체 상품 수  |
| pagination.total_pages  | integer       | 전체 페이지 수 |

| Error Code            | HTTP Status | 설명         |
| --------------------- | ----------- | ---------- |
| `UNAUTHORIZED`        | 401         | 로그인 필요     |
| `ADMIN_REQUIRED`      | 403         | 관리자 권한 필요  |
| `INVALID_ITEM_STATUS` | 422         | 상품 상태 값 오류 |
| `INVALID_PAGE_VALUE`  | 422         | 페이지 값 오류   |
| `INVALID_SIZE_VALUE`  | 422         | 페이지 크기 오류  |

---

| API       | PATCH `/api/v1/admin/items/{item_id}/status` |
| --------- | -------------------------------------------- |
| 기능        | 상품 상태 변경                                     |
| 권한        | Admin                                        |
| 설명        | 관리자가 상품을 숨김, 복구, 판매완료 등으로 상태 변경한다.           |
| 성공 Status | `200 OK`                                     |
| 실패 Status | `401`, `403`, `404`, `409`, `422`            |

| Path Parameter | Type    | Required | 설명            |
| -------------- | ------- | -------- | ------------- |
| item_id        | integer | Yes      | 상태를 변경할 상품 ID |

| Request Body | Type   | Required | Validation                              | 설명        |
| ------------ | ------ | -------- | --------------------------------------- | --------- |
| status       | string | Yes      | `ON_SALE`, `RESERVED`, `SOLD`, `HIDDEN` | 변경할 상품 상태 |
| reason       | string | Yes      | 1~500자                                  | 상태 변경 사유  |

| 처리 규칙     | 설명                                   |
| --------- | ------------------------------------ |
| 관리자 권한 필수 | 일반 사용자는 접근 불가                        |
| 신고 상품 숨김  | 금지 상품, 사기 의심 상품은 `HIDDEN` 처리         |
| 숨김 해제 가능  | 문제가 없다고 판단되면 `HIDDEN` → `ON_SALE` 가능 |
| 삭제 상품 제한  | Soft Delete된 상품은 상태 변경 제한 가능         |
| 거래 상태 확인  | 진행 중 거래가 있는 상품은 상태 변경 제한 가능          |
| 로그 기록     | 관리자 ID, 상품 ID, 이전 상태, 변경 상태, 사유 저장   |

| Response Data   | Type     | 설명        |
| --------------- | -------- | --------- |
| id              | integer  | 상품 ID     |
| previous_status | string   | 이전 상품 상태  |
| status          | string   | 변경된 상품 상태 |
| reason          | string   | 변경 사유     |
| updated_at      | datetime | 변경 시간     |

| Error Code                  | HTTP Status | 설명                |
| --------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요            |
| `ADMIN_REQUIRED`            | 403         | 관리자 권한 필요         |
| `ITEM_NOT_FOUND`            | 404         | 상품이 존재하지 않음       |
| `ITEM_ALREADY_DELETED`      | 409         | 이미 삭제 처리된 상품      |
| `ACTIVE_TRANSACTION_EXISTS` | 409         | 진행 중 거래가 있어 처리 불가 |
| `INVALID_ITEM_STATUS`       | 422         | 허용되지 않는 상품 상태     |
| `REASON_REQUIRED`           | 422         | 상태 변경 사유 누락       |

---

| API       | GET `/api/v1/admin/reports`                           |
| --------- | ----------------------------------------------------- |
| 기능        | 신고 목록 조회                                              |
| 권한        | Admin                                                 |
| 설명        | 관리자가 전체 신고 목록을 조회한다. 신고 상태, 대상 유형, 신고 사유별로 필터링할 수 있다. |
| 성공 Status | `200 OK`                                              |
| 실패 Status | `401`, `403`, `422`                                   |

| Query Parameter | Type    | Required | Default | 설명        |
| --------------- | ------- | -------- | ------- | --------- |
| status          | string  | No       | null    | 신고 처리 상태  |
| target_type     | string  | No       | null    | 신고 대상 유형  |
| reason          | string  | No       | null    | 신고 사유     |
| page            | integer | No       | 1       | 페이지 번호    |
| size            | integer | No       | 20      | 페이지당 신고 수 |

| Response Data               | Type          | 설명       |
| --------------------------- | ------------- | -------- |
| reports                     | array         | 신고 목록    |
| reports[].id                | integer       | 신고 ID    |
| reports[].reporter.id       | integer       | 신고자 ID   |
| reports[].reporter.nickname | string        | 신고자 닉네임  |
| reports[].target_type       | string        | 신고 대상 유형 |
| reports[].target_id         | integer       | 신고 대상 ID |
| reports[].target_summary    | string/null   | 신고 대상 요약 |
| reports[].reason            | string        | 신고 사유    |
| reports[].status            | string        | 신고 처리 상태 |
| reports[].created_at        | datetime      | 신고 접수 시간 |
| reports[].resolved_at       | datetime/null | 처리 완료 시간 |
| pagination.page             | integer       | 현재 페이지   |
| pagination.size             | integer       | 페이지 크기   |
| pagination.total_count      | integer       | 전체 신고 수  |
| pagination.total_pages      | integer       | 전체 페이지 수 |

| Error Code              | HTTP Status | 설명          |
| ----------------------- | ----------- | ----------- |
| `UNAUTHORIZED`          | 401         | 로그인 필요      |
| `ADMIN_REQUIRED`        | 403         | 관리자 권한 필요   |
| `INVALID_REPORT_STATUS` | 422         | 신고 상태 값 오류  |
| `INVALID_TARGET_TYPE`   | 422         | 신고 대상 유형 오류 |
| `INVALID_REPORT_REASON` | 422         | 신고 사유 오류    |
| `INVALID_PAGE_VALUE`    | 422         | 페이지 값 오류    |

---

| API       | GET `/api/v1/admin/reports/{report_id}` |
| --------- | --------------------------------------- |
| 기능        | 신고 상세 조회                                |
| 권한        | Admin                                   |
| 설명        | 관리자가 특정 신고의 상세 정보와 신고 대상 정보를 조회한다.      |
| 성공 Status | `200 OK`                                |
| 실패 Status | `401`, `403`, `404`                     |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| report_id      | integer | Yes      | 조회할 신고 ID |

| Response Data     | Type          | 설명          |
| ----------------- | ------------- | ----------- |
| id                | integer       | 신고 ID       |
| reporter.id       | integer       | 신고자 ID      |
| reporter.email    | string        | 신고자 이메일     |
| reporter.nickname | string        | 신고자 닉네임     |
| target_type       | string        | 신고 대상 유형    |
| target_id         | integer       | 신고 대상 ID    |
| target_detail     | object/null   | 신고 대상 상세 정보 |
| reason            | string        | 신고 사유       |
| detail            | string/null   | 신고 상세 내용    |
| status            | string        | 신고 처리 상태    |
| admin_id          | integer/null  | 처리 관리자 ID   |
| admin_memo        | string/null   | 관리자 내부 메모   |
| action_type       | string/null   | 처리 조치       |
| created_at        | datetime      | 신고 접수 시간    |
| resolved_at       | datetime/null | 신고 처리 시간    |

| Error Code         | HTTP Status | 설명          |
| ------------------ | ----------- | ----------- |
| `UNAUTHORIZED`     | 401         | 로그인 필요      |
| `ADMIN_REQUIRED`   | 403         | 관리자 권한 필요   |
| `REPORT_NOT_FOUND` | 404         | 신고가 존재하지 않음 |

---

| API       | PATCH `/api/v1/admin/reports/{report_id}`        |
| --------- | ------------------------------------------------ |
| 기능        | 신고 처리                                            |
| 권한        | Admin                                            |
| 설명        | 관리자가 신고 상태를 변경하고 필요 시 상품 숨김, 사용자 정지 등의 조치를 수행한다. |
| 성공 Status | `200 OK`                                         |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422`         |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| report_id      | integer | Yes      | 처리할 신고 ID |

| Request Body   | Type   | Required | Validation                          | 설명                 |
| -------------- | ------ | -------- | ----------------------------------- | ------------------ |
| status         | string | Yes      | `REVIEWING`, `RESOLVED`, `REJECTED` | 변경할 신고 상태          |
| action_type    | string | Yes      | 허용된 조치 유형                           | 운영 조치              |
| admin_memo     | string | No       | 최대 1000자                            | 관리자 내부 메모          |
| result_message | string | No       | 최대 500자                             | 사용자에게 공개 가능한 처리 결과 |

| Action Type       | 설명       |
| ----------------- | -------- |
| `NONE`            | 별도 조치 없음 |
| `ITEM_HIDDEN`     | 상품 숨김    |
| `ITEM_DELETED`    | 상품 삭제 처리 |
| `USER_SUSPENDED`  | 사용자 정지   |
| `REPORT_REJECTED` | 신고 반려    |

| 처리 규칙     | 설명                                             |
| --------- | ---------------------------------------------- |
| 관리자 권한 필수 | 일반 사용자는 접근 불가                                  |
| 신고 상태 변경  | 신고 상태를 `REVIEWING`, `RESOLVED`, `REJECTED`로 변경 |
| 조치 대상 확인  | 상품 숨김은 상품 신고, 사용자 정지는 사용자 신고와 연결               |
| 자동 제재 금지  | 관리자 요청에 의한 명시적 조치만 수행                          |
| 처리 시간 저장  | 완료 또는 반려 시 `resolved_at` 저장                    |
| 로그 기록     | 신고 ID, 관리자 ID, 조치 유형, 메모를 `audit_logs`에 저장     |

| Response Data | Type          | 설명        |
| ------------- | ------------- | --------- |
| id            | integer       | 신고 ID     |
| status        | string        | 변경된 신고 상태 |
| action_type   | string        | 수행된 조치    |
| admin_id      | integer       | 처리 관리자 ID |
| resolved_at   | datetime/null | 처리 완료 시간  |

| Error Code                | HTTP Status | 설명                  |
| ------------------------- | ----------- | ------------------- |
| `UNAUTHORIZED`            | 401         | 로그인 필요              |
| `ADMIN_REQUIRED`          | 403         | 관리자 권한 필요           |
| `REPORT_NOT_FOUND`        | 404         | 신고가 존재하지 않음         |
| `INVALID_REPORT_STATUS`   | 422         | 신고 상태 값 오류          |
| `INVALID_ACTION_TYPE`     | 422         | 조치 유형 오류            |
| `INVALID_ACTION_TARGET`   | 400         | 신고 대상과 조치 유형이 맞지 않음 |
| `REPORT_ALREADY_RESOLVED` | 409         | 이미 처리 완료된 신고        |
| `ADMIN_MEMO_TOO_LONG`     | 422         | 관리자 메모 길이 초과        |

---

| API       | GET `/api/v1/admin/transactions`    |
| --------- | ----------------------------------- |
| 기능        | 전체 거래 목록 조회                         |
| 권한        | Admin                               |
| 설명        | 관리자가 전체 거래 요청, 수락, 완료, 취소 내역을 조회한다. |
| 성공 Status | `200 OK`                            |
| 실패 Status | `401`, `403`, `422`                 |

| Query Parameter | Type    | Required | Default | 설명        |
| --------------- | ------- | -------- | ------- | --------- |
| status          | string  | No       | null    | 거래 상태     |
| buyer_id        | integer | No       | null    | 구매자 ID    |
| seller_id       | integer | No       | null    | 판매자 ID    |
| item_id         | integer | No       | null    | 상품 ID     |
| page            | integer | No       | 1       | 페이지 번호    |
| size            | integer | No       | 20      | 페이지당 거래 수 |

| Response Data                  | Type          | 설명       |
| ------------------------------ | ------------- | -------- |
| transactions                   | array         | 거래 목록    |
| transactions[].id              | integer       | 거래 ID    |
| transactions[].item.id         | integer       | 상품 ID    |
| transactions[].item.title      | string        | 상품명      |
| transactions[].buyer.id        | integer       | 구매자 ID   |
| transactions[].buyer.nickname  | string        | 구매자 닉네임  |
| transactions[].seller.id       | integer       | 판매자 ID   |
| transactions[].seller.nickname | string        | 판매자 닉네임  |
| transactions[].status          | string        | 거래 상태    |
| transactions[].price           | integer       | 거래 금액    |
| transactions[].created_at      | datetime      | 거래 생성일   |
| transactions[].completed_at    | datetime/null | 거래 완료일   |
| pagination.page                | integer       | 현재 페이지   |
| pagination.size                | integer       | 페이지 크기   |
| pagination.total_count         | integer       | 전체 거래 수  |
| pagination.total_pages         | integer       | 전체 페이지 수 |

| Error Code                   | HTTP Status | 설명         |
| ---------------------------- | ----------- | ---------- |
| `UNAUTHORIZED`               | 401         | 로그인 필요     |
| `ADMIN_REQUIRED`             | 403         | 관리자 권한 필요  |
| `INVALID_TRANSACTION_STATUS` | 422         | 거래 상태 값 오류 |
| `INVALID_PAGE_VALUE`         | 422         | 페이지 값 오류   |
| `INVALID_SIZE_VALUE`         | 422         | 페이지 크기 오류  |

---

| API       | GET `/api/v1/admin/audit-logs`                |
| --------- | --------------------------------------------- |
| 기능        | 관리자 조치 로그 조회                                  |
| 권한        | Admin                                         |
| 설명        | 관리자가 회원 정지, 상품 숨김, 신고 처리 등 주요 운영 조치 로그를 조회한다. |
| 성공 Status | `200 OK`                                      |
| 실패 Status | `401`, `403`, `422`                           |

| Query Parameter | Type    | Required | Default | 설명         |
| --------------- | ------- | -------- | ------- | ---------- |
| admin_id        | integer | No       | null    | 조치한 관리자 ID |
| action_type     | string  | No       | null    | 조치 유형      |
| target_type     | string  | No       | null    | 조치 대상 유형   |
| target_id       | integer | No       | null    | 조치 대상 ID   |
| page            | integer | No       | 1       | 페이지 번호     |
| size            | integer | No       | 20      | 페이지당 로그 수  |

| Response Data            | Type        | 설명           |
| ------------------------ | ----------- | ------------ |
| audit_logs               | array       | 관리자 조치 로그 목록 |
| audit_logs[].id          | integer     | 로그 ID        |
| audit_logs[].admin_id    | integer     | 관리자 ID       |
| audit_logs[].admin_email | string      | 관리자 이메일      |
| audit_logs[].action_type | string      | 조치 유형        |
| audit_logs[].target_type | string      | 조치 대상 유형     |
| audit_logs[].target_id   | integer     | 조치 대상 ID     |
| audit_logs[].reason      | string/null | 조치 사유        |
| audit_logs[].created_at  | datetime    | 조치 시간        |
| pagination.page          | integer     | 현재 페이지       |
| pagination.size          | integer     | 페이지 크기       |
| pagination.total_count   | integer     | 전체 로그 수      |
| pagination.total_pages   | integer     | 전체 페이지 수     |

| Error Code            | HTTP Status | 설명          |
| --------------------- | ----------- | ----------- |
| `UNAUTHORIZED`        | 401         | 로그인 필요      |
| `ADMIN_REQUIRED`      | 403         | 관리자 권한 필요   |
| `INVALID_ACTION_TYPE` | 422         | 조치 유형 오류    |
| `INVALID_TARGET_TYPE` | 422         | 조치 대상 유형 오류 |
| `INVALID_PAGE_VALUE`  | 422         | 페이지 값 오류    |

---

| Admin Action Type Enum  | 설명       |
| ----------------------- | -------- |
| `USER_STATUS_CHANGED`   | 회원 상태 변경 |
| `ITEM_STATUS_CHANGED`   | 상품 상태 변경 |
| `REPORT_STATUS_CHANGED` | 신고 상태 변경 |
| `ITEM_HIDDEN`           | 상품 숨김    |
| `ITEM_DELETED`          | 상품 삭제 처리 |
| `USER_SUSPENDED`        | 사용자 정지   |
| `REPORT_REJECTED`       | 신고 반려    |

| Admin Target Type Enum | 설명  |
| ---------------------- | --- |
| `USER`                 | 회원  |
| `ITEM`                 | 상품  |
| `REPORT`               | 신고  |
| `TRANSACTION`          | 거래  |
| `CHAT_ROOM`            | 채팅방 |
| `MESSAGE`              | 메시지 |

| Admin 관련 Validation | 기준            |
| ------------------- | ------------- |
| user_id             | 1 이상의 정수      |
| item_id             | 1 이상의 정수      |
| report_id           | 1 이상의 정수      |
| status              | 각 도메인의 허용 상태값 |
| reason              | 1~500자        |
| admin_memo          | 최대 1000자      |
| result_message      | 최대 500자       |
| page                | 1 이상          |
| size                | 1~100         |

| Admin Router 설계 근거    | 내용                                    |
| --------------------- | ------------------------------------- |
| 관리자 API는 Prefix 분리    | 일반 API와 운영 API를 명확히 분리                |
| 모든 API는 Admin 권한 필수   | 일반 사용자의 운영 기능 접근 차단                   |
| 변경 작업은 Audit Log 저장   | 운영 추적성과 책임 소재 확보                      |
| 신고 처리는 Admin에서 수행     | 사용자 신고와 관리자 조치를 분리                    |
| 자동 제재 제외              | 허위 신고 가능성 때문에 관리자 검토 후 조치             |
| 상품 삭제는 Soft Delete 권장 | 신고, 거래, 분쟁 이력 보존 필요                   |
| 회원 탈퇴/정지는 상태값 변경      | 기존 거래와 신고 이력을 유지해야 함                  |
| 거래는 조회 중심             | MVP에서는 관리자가 거래 상태를 직접 조작하지 않는 구조가 안전함 |
