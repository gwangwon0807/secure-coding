| 구분            | 내용                                        |
| ------------- | ----------------------------------------- |
| Router        | Block Router                              |
| Prefix        | `/api/v1/blocks`                          |
| Method 수      | 3개                                        |
| 담당 기능         | 사용자 차단, 차단 목록 조회, 차단 해제                   |
| 인증 방식         | JWT + HttpOnly Cookie                     |
| 관련 테이블        | `blocks`, `users`                         |
| 주요 Dependency | `get_current_user`, `require_active_user` |
| 비고            | 차단 관계는 채팅방 생성, 메시지 전송 시 검증에 사용            |

| 번호 | Method | Endpoint     | 기능       | 권한   | 설명                   |
| -- | ------ | ------------ | -------- | ---- | -------------------- |
| 1  | POST   | `/`          | 사용자 차단   | User | 특정 사용자를 차단한다.        |
| 2  | GET    | `/`          | 차단 목록 조회 | User | 내가 차단한 사용자 목록을 조회한다. |
| 3  | DELETE | `/{user_id}` | 차단 해제    | User | 특정 사용자에 대한 차단을 해제한다. |

---

| API       | POST `/api/v1/blocks`                    |
| --------- | ---------------------------------------- |
| 기능        | 사용자 차단                                   |
| 권한        | User                                     |
| 설명        | 현재 로그인한 사용자가 특정 사용자를 차단한다.               |
| 성공 Status | `201 Created`                            |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422` |

| Request Body    | Type    | Required | Validation  | 설명         |
| --------------- | ------- | -------- | ----------- | ---------- |
| blocked_user_id | integer | Yes      | 존재하는 사용자 ID | 차단할 사용자 ID |

| 처리 규칙       | 설명                                   |
| ----------- | ------------------------------------ |
| 로그인 필수      | 비회원은 사용자 차단 불가                       |
| 정지 회원 제한    | 정지 또는 탈퇴 사용자는 차단 기능 제한 가능            |
| 대상 사용자 확인   | 존재하는 사용자만 차단 가능                      |
| 자기 자신 차단 불가 | `current_user.id != blocked_user_id` |
| 중복 차단 방지    | 이미 차단한 사용자는 다시 차단하지 않음               |
| 채팅 제한       | 차단 관계가 있으면 채팅방 생성 및 메시지 전송 제한        |
| 기존 채팅방 처리   | 기존 채팅방은 유지하되 메시지 전송 제한 권장            |

| Response Data   | Type     | 설명         |
| --------------- | -------- | ---------- |
| id              | integer  | 차단 ID      |
| blocker_id      | integer  | 차단한 사용자 ID |
| blocked_user_id | integer  | 차단된 사용자 ID |
| created_at      | datetime | 차단한 시간     |

| Error Code               | HTTP Status | 설명                 |
| ------------------------ | ----------- | ------------------ |
| `UNAUTHORIZED`           | 401         | 로그인 필요             |
| `USER_NOT_ACTIVE`        | 403         | 정지 또는 탈퇴 사용자       |
| `BLOCKED_USER_NOT_FOUND` | 404         | 차단 대상 사용자가 존재하지 않음 |
| `CANNOT_BLOCK_SELF`      | 400         | 자기 자신 차단 불가        |
| `ALREADY_BLOCKED`        | 409         | 이미 차단한 사용자         |
| `INVALID_USER_ID`        | 422         | 사용자 ID 형식 오류       |

---

| API       | GET `/api/v1/blocks`           |
| --------- | ------------------------------ |
| 기능        | 차단 목록 조회                       |
| 권한        | User                           |
| 설명        | 현재 로그인한 사용자가 차단한 사용자 목록을 조회한다. |
| 성공 Status | `200 OK`                       |
| 실패 Status | `401`, `403`, `422`            |

| Query Parameter | Type    | Required | Default | 설명            |
| --------------- | ------- | -------- | ------- | ------------- |
| page            | integer | No       | 1       | 페이지 번호        |
| size            | integer | No       | 20      | 페이지당 차단 사용자 수 |

| 정렬 기준 | 설명                     |
| ----- | ---------------------- |
| 기본 정렬 | `created_at DESC`      |
| 목적    | 최근 차단한 사용자를 먼저 보여주기 위함 |

| Response Data                           | Type        | 설명              |
| --------------------------------------- | ----------- | --------------- |
| blocks                                  | array       | 차단 목록           |
| blocks[].id                             | integer     | 차단 ID           |
| blocks[].blocked_user.id                | integer     | 차단된 사용자 ID      |
| blocks[].blocked_user.nickname          | string      | 차단된 사용자 닉네임     |
| blocks[].blocked_user.profile_image_url | string/null | 차단된 사용자 프로필 이미지 |
| blocks[].created_at                     | datetime    | 차단한 시간          |
| pagination.page                         | integer     | 현재 페이지          |
| pagination.size                         | integer     | 페이지 크기          |
| pagination.total_count                  | integer     | 전체 차단 수         |
| pagination.total_pages                  | integer     | 전체 페이지 수        |

| 반환하지 않는 정보                | 이유           |
| ------------------------- | ------------ |
| blocked_user.email        | 개인정보         |
| blocked_user.report_count | 악용 가능성       |
| blocked_user.role         | 일반 사용자에게 불필요 |
| blocked_user.status       | 노출 최소화       |

| Error Code           | HTTP Status | 설명           |
| -------------------- | ----------- | ------------ |
| `UNAUTHORIZED`       | 401         | 로그인 필요       |
| `USER_NOT_ACTIVE`    | 403         | 정지 또는 탈퇴 사용자 |
| `INVALID_PAGE_VALUE` | 422         | 페이지 값 오류     |
| `INVALID_SIZE_VALUE` | 422         | 페이지 크기 오류    |

---

| API       | DELETE `/api/v1/blocks/{user_id}` |
| --------- | --------------------------------- |
| 기능        | 차단 해제                             |
| 권한        | User                              |
| 설명        | 현재 로그인한 사용자가 특정 사용자에 대한 차단을 해제한다. |
| 성공 Status | `200 OK`                          |
| 실패 Status | `401`, `403`, `404`, `422`        |

| Path Parameter | Type    | Required | 설명            |
| -------------- | ------- | -------- | ------------- |
| user_id        | integer | Yes      | 차단 해제할 사용자 ID |

| 처리 규칙          | 설명                                |
| -------------- | --------------------------------- |
| 로그인 필수         | 비회원은 차단 해제 불가                     |
| 차단 관계 확인       | 현재 사용자가 해당 사용자를 차단한 기록이 있어야 함     |
| Soft Delete 여부 | 단순 삭제 또는 `deleted_at` 기록 방식 선택 가능 |
| 채팅 제한 해제       | 차단 해제 후 채팅방 생성 및 메시지 전송 가능        |
| 상대방 차단은 별도     | 내가 차단 해제해도 상대방이 나를 차단했으면 채팅 불가    |

| Response Data   | Type     | 설명            |
| --------------- | -------- | ------------- |
| blocked_user_id | integer  | 차단 해제된 사용자 ID |
| unblocked_at    | datetime | 차단 해제 시간      |

| Error Code        | HTTP Status | 설명             |
| ----------------- | ----------- | -------------- |
| `UNAUTHORIZED`    | 401         | 로그인 필요         |
| `USER_NOT_ACTIVE` | 403         | 정지 또는 탈퇴 사용자   |
| `BLOCK_NOT_FOUND` | 404         | 차단 기록이 존재하지 않음 |
| `INVALID_USER_ID` | 422         | 사용자 ID 형식 오류   |

---

| Block 테이블 컬럼    | Type          | 설명                       |
| --------------- | ------------- | ------------------------ |
| id              | integer       | 차단 ID                    |
| blocker_id      | integer       | 차단한 사용자 ID               |
| blocked_user_id | integer       | 차단된 사용자 ID               |
| created_at      | datetime      | 차단 생성일                   |
| deleted_at      | datetime/null | 차단 해제일, Soft Delete 사용 시 |

| Block 관련 Validation | 기준            |
| ------------------- | ------------- |
| blocker_id          | 현재 로그인 사용자 ID |
| blocked_user_id     | 존재하는 사용자 ID   |
| user_id             | 1 이상의 정수      |
| page                | 1 이상          |
| size                | 1~100         |

| 권장 DB 제약조건                            | 설명          |
| ------------------------------------- | ----------- |
| `blocker_id != blocked_user_id`       | 자기 자신 차단 방지 |
| `UNIQUE(blocker_id, blocked_user_id)` | 중복 차단 방지    |
| `blocker_id FK users.id`              | 차단한 사용자 참조  |
| `blocked_user_id FK users.id`         | 차단된 사용자 참조  |

| 차단 관계 적용 위치 | 처리                            |
| ----------- | ----------------------------- |
| 채팅방 생성      | 구매자와 판매자 사이에 차단 관계가 있으면 생성 불가 |
| 메시지 전송      | 채팅 참여자 사이에 차단 관계가 있으면 전송 불가   |
| 상품 조회       | MVP에서는 제한하지 않음                |
| 공개 프로필 조회   | MVP에서는 제한하지 않음                |
| 거래 요청       | 필요 시 차단 관계가 있으면 거래 요청 제한 가능   |

| Block Router 설계 근거 | 내용                                |
| ------------------ | --------------------------------- |
| 차단은 User 권한        | 로그인 사용자만 악성 사용자를 차단할 수 있어야 함      |
| 중복 차단 방지           | 같은 대상에 대한 불필요한 데이터 중복 방지          |
| 양방향 검증 필요          | 내가 차단했거나 상대방이 나를 차단했으면 채팅 제한      |
| 기존 채팅방은 유지         | 신고, 분쟁, 거래 이력 확인을 위해 대화 기록 보존     |
| 메시지 전송만 제한         | 기존 데이터 삭제보다 운영상 안전함               |
| Soft Delete 선택 가능  | 차단/해제 이력 추적이 필요하면 `deleted_at` 사용 |
