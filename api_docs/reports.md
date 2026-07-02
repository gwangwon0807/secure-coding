| 구분            | 내용                                                                |
| ------------- | ----------------------------------------------------------------- |
| Router        | Report Router                                                     |
| Prefix        | `/api/v1/reports`                                                 |
| Method 수      | 3개                                                                |
| 담당 기능         | 신고 등록, 내가 신고한 목록 조회, 내가 신고한 상세 조회                                 |
| 인증 방식         | JWT + HttpOnly Cookie                                             |
| 관련 테이블        | `reports`, `users`, `items`, `chat_rooms`, `messages`             |
| 주요 Dependency | `get_current_user`, `require_active_user`, `require_report_owner` |
| 비고            | 신고 처리는 일반 Report Router가 아니라 Admin Router에서 처리                    |

| 번호 | Method | Endpoint       | 기능         | 권한   | 설명                    |
| -- | ------ | -------------- | ---------- | ---- | --------------------- |
| 1  | POST   | `/`            | 신고 등록      | User | 상품, 사용자, 채팅에 대한 신고 접수 |
| 2  | GET    | `/me`          | 내 신고 목록 조회 | User | 내가 접수한 신고 목록 조회       |
| 3  | GET    | `/{report_id}` | 내 신고 상세 조회 | User | 내가 접수한 특정 신고 상세 조회    |

---

| API       | POST `/api/v1/reports`                   |
| --------- | ---------------------------------------- |
| 기능        | 신고 등록                                    |
| 권한        | User                                     |
| 설명        | 로그인한 사용자가 상품, 사용자, 채팅방을 신고한다.            |
| 성공 Status | `201 Created`                            |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422` |

| Request Body | Type    | Required | Validation                             | 설명       |
| ------------ | ------- | -------- | -------------------------------------- | -------- |
| target_type  | string  | Yes      | `ITEM`, `USER`, `CHAT_ROOM`, `MESSAGE` | 신고 대상 유형 |
| target_id    | integer | Yes      | 존재하는 대상 ID                             | 신고 대상 ID |
| reason       | string  | Yes      | 허용된 신고 사유                              | 신고 사유    |
| detail       | string  | No       | 최대 1000자                               | 상세 신고 내용 |

| Target Type | 설명        |
| ----------- | --------- |
| `ITEM`      | 상품 신고     |
| `USER`      | 사용자 신고    |
| `CHAT_ROOM` | 채팅방 신고    |
| `MESSAGE`   | 특정 메시지 신고 |

| Reason Enum             | 설명      |
| ----------------------- | ------- |
| `SCAM_SUSPECTED`        | 사기 의심   |
| `PROHIBITED_ITEM`       | 금지 상품   |
| `FALSE_INFORMATION`     | 허위 정보   |
| `ABUSIVE_LANGUAGE`      | 욕설 / 비방 |
| `SPAM`                  | 스팸      |
| `INAPPROPRIATE_CONTENT` | 부적절한 내용 |
| `ETC`                   | 기타      |

| 처리 규칙       | 설명                                  |
| ----------- | ----------------------------------- |
| 로그인 필수      | 비회원은 신고 불가                          |
| 정지 회원 제한    | 정지 또는 탈퇴 사용자는 신고 불가                 |
| 대상 존재 확인    | 신고 대상이 실제로 존재해야 함                   |
| 자기 자신 신고 제한 | `USER` 신고 시 자기 자신 신고 불가             |
| 본인 상품 신고 제한 | 본인 상품 신고는 제한 가능                     |
| 채팅방 신고 권한   | 해당 채팅방 참여자만 신고 가능                   |
| 메시지 신고 권한   | 해당 메시지가 속한 채팅방 참여자만 신고 가능           |
| 중복 신고 제한    | 같은 사용자가 같은 대상에 대해 중복 신고하지 못하게 제한 가능 |
| 기본 상태       | 신고 생성 시 `RECEIVED` 상태               |
| 자동 제재 금지    | MVP에서는 신고 즉시 자동 차단하지 않고 관리자 검토      |

| Response Data | Type        | 설명         |
| ------------- | ----------- | ---------- |
| id            | integer     | 신고 ID      |
| reporter_id   | integer     | 신고자 ID     |
| target_type   | string      | 신고 대상 유형   |
| target_id     | integer     | 신고 대상 ID   |
| reason        | string      | 신고 사유      |
| detail        | string/null | 상세 내용      |
| status        | string      | `RECEIVED` |
| created_at    | datetime    | 신고 접수 시간   |

| Error Code               | HTTP Status | 설명             |
| ------------------------ | ----------- | -------------- |
| `UNAUTHORIZED`           | 401         | 로그인 필요         |
| `USER_NOT_ACTIVE`        | 403         | 정지 또는 탈퇴 사용자   |
| `INVALID_TARGET_TYPE`    | 422         | 신고 대상 유형 오류    |
| `INVALID_REPORT_REASON`  | 422         | 신고 사유 오류       |
| `TARGET_NOT_FOUND`       | 404         | 신고 대상이 존재하지 않음 |
| `CANNOT_REPORT_SELF`     | 400         | 자기 자신 신고 불가    |
| `CANNOT_REPORT_OWN_ITEM` | 400         | 본인 상품 신고 불가    |
| `FORBIDDEN_CHAT_REPORT`  | 403         | 채팅방 참여자가 아님    |
| `DUPLICATE_REPORT`       | 409         | 이미 신고한 대상      |
| `REPORT_DETAIL_TOO_LONG` | 422         | 상세 신고 내용 길이 초과 |

---

| API       | GET `/api/v1/reports/me`      |
| --------- | ----------------------------- |
| 기능        | 내 신고 목록 조회                    |
| 권한        | User                          |
| 설명        | 현재 로그인한 사용자가 접수한 신고 목록을 조회한다. |
| 성공 Status | `200 OK`                      |
| 실패 Status | `401`, `403`, `422`           |

| Query Parameter | Type    | Required | Default | 설명        |
| --------------- | ------- | -------- | ------- | --------- |
| status          | string  | No       | null    | 신고 처리 상태  |
| target_type     | string  | No       | null    | 신고 대상 유형  |
| page            | integer | No       | 1       | 페이지 번호    |
| size            | integer | No       | 20      | 페이지당 신고 수 |

| 정렬 기준 | 설명                   |
| ----- | -------------------- |
| 기본 정렬 | `created_at DESC`    |
| 목적    | 최근 신고 내역을 먼저 보여주기 위함 |

| Response Data            | Type          | 설명          |
| ------------------------ | ------------- | ----------- |
| reports                  | array         | 신고 목록       |
| reports[].id             | integer       | 신고 ID       |
| reports[].target_type    | string        | 신고 대상 유형    |
| reports[].target_id      | integer       | 신고 대상 ID    |
| reports[].target_summary | string/null   | 신고 대상 요약 정보 |
| reports[].reason         | string        | 신고 사유       |
| reports[].status         | string        | 신고 처리 상태    |
| reports[].created_at     | datetime      | 신고 접수 시간    |
| reports[].resolved_at    | datetime/null | 신고 처리 완료 시간 |
| pagination.page          | integer       | 현재 페이지      |
| pagination.size          | integer       | 페이지 크기      |
| pagination.total_count   | integer       | 전체 신고 수     |
| pagination.total_pages   | integer       | 전체 페이지 수    |

| target_summary 예시 | 설명                |
| ----------------- | ----------------- |
| 상품 신고             | 상품 제목             |
| 사용자 신고            | 사용자 닉네임           |
| 채팅방 신고            | 관련 상품명 또는 상대방 닉네임 |
| 메시지 신고            | 메시지 일부 내용         |

| Error Code              | HTTP Status | 설명           |
| ----------------------- | ----------- | ------------ |
| `UNAUTHORIZED`          | 401         | 로그인 필요       |
| `USER_NOT_ACTIVE`       | 403         | 정지 또는 탈퇴 사용자 |
| `INVALID_REPORT_STATUS` | 422         | 신고 상태 값 오류   |
| `INVALID_TARGET_TYPE`   | 422         | 신고 대상 유형 오류  |
| `INVALID_PAGE_VALUE`    | 422         | 페이지 값 오류     |
| `INVALID_SIZE_VALUE`    | 422         | 페이지 크기 오류    |

---

| API       | GET `/api/v1/reports/{report_id}`    |
| --------- | ------------------------------------ |
| 기능        | 내 신고 상세 조회                           |
| 권한        | User                                 |
| 설명        | 현재 로그인한 사용자가 접수한 특정 신고의 상세 정보를 조회한다. |
| 성공 Status | `200 OK`                             |
| 실패 Status | `401`, `403`, `404`                  |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| report_id      | integer | Yes      | 조회할 신고 ID |

| 처리 규칙       | 설명                                      |
| ----------- | --------------------------------------- |
| 본인 신고만 조회   | `report.reporter_id == current_user.id` |
| 관리자 메모 비공개  | 내부 운영 메모는 일반 사용자에게 반환하지 않음              |
| 처리 결과 일부 공개 | 신고 상태와 기본 처리 결과만 반환                     |
| 민감 정보 제한    | 신고 대상자의 이메일, 내부 제재 기준 등은 반환하지 않음        |

| Response Data  | Type          | 설명                 |
| -------------- | ------------- | ------------------ |
| id             | integer       | 신고 ID              |
| reporter_id    | integer       | 신고자 ID             |
| target_type    | string        | 신고 대상 유형           |
| target_id      | integer       | 신고 대상 ID           |
| target_summary | string/null   | 신고 대상 요약 정보        |
| reason         | string        | 신고 사유              |
| detail         | string/null   | 상세 신고 내용           |
| status         | string        | 신고 처리 상태           |
| result_message | string/null   | 사용자에게 공개 가능한 처리 결과 |
| created_at     | datetime      | 신고 접수 시간           |
| resolved_at    | datetime/null | 신고 처리 완료 시간        |

| 반환하지 않는 정보           | 이유           |
| -------------------- | ------------ |
| admin_id             | 내부 운영 정보     |
| admin_memo           | 관리자 내부 판단 내용 |
| internal_action_type | 제재 기준 악용 방지  |
| reported_user_email  | 개인정보         |
| 신고 대상자의 전체 신고 횟수     | 악용 가능성       |

| Error Code         | HTTP Status | 설명             |
| ------------------ | ----------- | -------------- |
| `UNAUTHORIZED`     | 401         | 로그인 필요         |
| `REPORT_NOT_FOUND` | 404         | 신고가 존재하지 않음    |
| `FORBIDDEN`        | 403         | 본인이 접수한 신고가 아님 |

---

| Report Status Enum | 설명       |
| ------------------ | -------- |
| `RECEIVED`         | 신고 접수    |
| `REVIEWING`        | 관리자 검토 중 |
| `RESOLVED`         | 처리 완료    |
| `REJECTED`         | 신고 반려    |

| Report Target Type Enum | 설명  |
| ----------------------- | --- |
| `ITEM`                  | 상품  |
| `USER`                  | 사용자 |
| `CHAT_ROOM`             | 채팅방 |
| `MESSAGE`               | 메시지 |

| Report Reason Enum      | 설명      |
| ----------------------- | ------- |
| `SCAM_SUSPECTED`        | 사기 의심   |
| `PROHIBITED_ITEM`       | 금지 상품   |
| `FALSE_INFORMATION`     | 허위 정보   |
| `ABUSIVE_LANGUAGE`      | 욕설 / 비방 |
| `SPAM`                  | 스팸      |
| `INAPPROPRIATE_CONTENT` | 부적절한 내용 |
| `ETC`                   | 기타      |

| Report 관련 Validation | 기준                                              |
| -------------------- | ----------------------------------------------- |
| report_id            | 1 이상의 정수                                        |
| target_id            | 1 이상의 정수                                        |
| target_type          | `ITEM`, `USER`, `CHAT_ROOM`, `MESSAGE`          |
| reason               | 허용된 신고 사유                                       |
| detail               | 최대 1000자                                        |
| status               | `RECEIVED`, `REVIEWING`, `RESOLVED`, `REJECTED` |
| page                 | 1 이상                                            |
| size                 | 1~100                                           |

| Report Router 설계 근거     | 내용                            |
| ----------------------- | ----------------------------- |
| 신고 등록은 User 권한          | 신고는 로그인 사용자만 가능해야 악용을 줄일 수 있음 |
| 신고 처리는 Admin Router로 분리 | 일반 사용자와 관리자 권한을 명확히 분리        |
| 자동 제재는 제외               | 허위 신고 가능성이 있으므로 관리자 검토 후 조치   |
| 중복 신고 제한                | 같은 사용자의 반복 신고 도배 방지           |
| 채팅/메시지 신고는 참여자만 가능      | 관계없는 사용자의 사적 대화 신고 방지         |
| 관리자 메모 비공개              | 내부 운영 기준과 개인정보 보호 필요          |
| 신고 이력 보존                | 분쟁, 사용자 제재, 운영 감사에 필요         |
