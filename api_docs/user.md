| 구분            | 내용                                          |
| ------------- | ------------------------------------------- |
| Router        | User Router                                 |
| Prefix        | `/api/v1/users`                             |
| Method 수      | 4개                                          |
| 담당 기능         | 내 프로필 조회, 내 프로필 수정, 회원 탈퇴, 다른 사용자 공개 프로필 조회 |
| 인증 방식         | JWT + HttpOnly Cookie                       |
| 관련 테이블        | `users`                                     |
| 주요 Dependency | `get_current_user`, `require_active_user`   |

| 번호 | Method | Endpoint     | 기능        | 권한     | 설명                   |
| -- | ------ | ------------ | --------- | ------ | -------------------- |
| 1  | GET    | `/me`        | 내 프로필 조회  | User   | 로그인한 사용자의 상세 프로필 조회  |
| 2  | PATCH  | `/me`        | 내 프로필 수정  | User   | 닉네임, 프로필 이미지, 소개글 수정 |
| 3  | DELETE | `/me`        | 회원 탈퇴     | User   | 현재 로그인한 사용자 계정 탈퇴 처리 |
| 4  | GET    | `/{user_id}` | 공개 프로필 조회 | Public | 다른 사용자의 공개 정보 조회     |

---

| API       | GET `/api/v1/users/me`     |
| --------- | -------------------------- |
| 기능        | 내 프로필 조회                   |
| 권한        | User                       |
| 설명        | 현재 로그인한 사용자의 프로필 정보를 조회한다. |
| 성공 Status | `200 OK`                   |
| 실패 Status | `401`, `403`, `404`        |

| Request Body | Type | Required | 설명                     |
| ------------ | ---- | -------- | ---------------------- |
| 없음           | -    | -        | Access Token Cookie 사용 |

| Response Data     | Type        | 설명                               |
| ----------------- | ----------- | -------------------------------- |
| id                | integer     | 회원 ID                            |
| email             | string      | 이메일                              |
| nickname          | string      | 닉네임                              |
| profile_image_url | string/null | 프로필 이미지 URL                      |
| bio               | string/null | 자기소개                             |
| role              | string      | `USER` 또는 `ADMIN`                |
| status            | string      | `ACTIVE`, `SUSPENDED`, `DELETED` |
| trust_score       | integer     | 사용자 신뢰도                          |
| trade_count       | integer     | 거래 완료 횟수                         |
| report_count      | integer     | 신고 받은 횟수                         |
| created_at        | datetime    | 가입일                              |
| updated_at        | datetime    | 수정일                              |

| Error Code             | HTTP Status | 설명                   |
| ---------------------- | ----------- | -------------------- |
| `ACCESS_TOKEN_MISSING` | 401         | Access Token 없음      |
| `INVALID_ACCESS_TOKEN` | 401         | 유효하지 않은 Access Token |
| `USER_NOT_ACTIVE`      | 403         | 정상 상태가 아닌 사용자        |
| `USER_NOT_FOUND`       | 404         | 사용자 없음               |

---

| API       | PATCH `/api/v1/users/me`              |
| --------- | ------------------------------------- |
| 기능        | 내 프로필 수정                              |
| 권한        | User                                  |
| 설명        | 현재 로그인한 사용자의 닉네임, 프로필 이미지, 소개글을 수정한다. |
| 성공 Status | `200 OK`                              |
| 실패 Status | `400`, `401`, `403`, `409`, `422`     |

| Request Body      | Type        | Required | Validation            | 설명          |
| ----------------- | ----------- | -------- | --------------------- | ----------- |
| nickname          | string      | No       | 2~20자, 중복 가능 여부 정책 선택 | 닉네임         |
| profile_image_url | string/null | No       | URL 형식                | 프로필 이미지 URL |
| bio               | string/null | No       | 최대 300자               | 자기소개        |

| Response Data     | Type        | 설명              |
| ----------------- | ----------- | --------------- |
| id                | integer     | 회원 ID           |
| nickname          | string      | 수정된 닉네임         |
| profile_image_url | string/null | 수정된 프로필 이미지 URL |
| bio               | string/null | 수정된 자기소개        |
| updated_at        | datetime    | 수정일             |

| Error Code                  | HTTP Status | 설명                   |
| --------------------------- | ----------- | -------------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요               |
| `USER_NOT_ACTIVE`           | 403         | 정지 또는 탈퇴 사용자         |
| `NICKNAME_ALREADY_EXISTS`   | 409         | 닉네임 중복 정책 사용 시 중복 발생 |
| `INVALID_NICKNAME_FORMAT`   | 422         | 닉네임 형식 오류            |
| `INVALID_PROFILE_IMAGE_URL` | 422         | 프로필 이미지 URL 형식 오류    |
| `BIO_TOO_LONG`              | 422         | 자기소개 길이 초과           |

---

| API       | DELETE `/api/v1/users/me`                                    |
| --------- | ------------------------------------------------------------ |
| 기능        | 회원 탈퇴                                                        |
| 권한        | User                                                         |
| 설명        | 현재 로그인한 사용자의 계정을 탈퇴 처리한다. 실제 DB 삭제가 아니라 상태를 `DELETED`로 변경한다. |
| 성공 Status | `200 OK`                                                     |
| 실패 Status | `401`, `403`, `404`, `409`                                   |

| Request Body | Type | Required | 설명               |
| ------------ | ---- | -------- | ---------------- |
| 없음           | -    | -        | 현재 로그인 사용자 기준 처리 |

| 처리 규칙       | 설명                                |
| ----------- | --------------------------------- |
| Soft Delete | `users.status = DELETED` 처리       |
| 개인정보 처리     | 닉네임, 프로필 이미지, 소개글은 비공개 또는 익명화 가능  |
| 상품 처리       | 사용자의 판매중 상품은 숨김 또는 유지 정책 필요       |
| 채팅 처리       | 기존 채팅 기록은 신고/거래 이력 때문에 즉시 삭제하지 않음 |
| 거래 중 계정     | 진행 중 거래가 있으면 탈퇴 제한 가능             |

| Response Data | Type     | 설명           |
| ------------- | -------- | ------------ |
| id            | integer  | 탈퇴 처리된 회원 ID |
| status        | string   | `DELETED`    |
| deleted_at    | datetime | 탈퇴 처리 시간     |

| Error Code                  | HTTP Status | 설명                |
| --------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요            |
| `USER_NOT_FOUND`            | 404         | 사용자 없음            |
| `USER_ALREADY_DELETED`      | 409         | 이미 탈퇴 처리된 사용자     |
| `ACTIVE_TRANSACTION_EXISTS` | 409         | 진행 중 거래가 있어 탈퇴 불가 |

---

| API       | GET `/api/v1/users/{user_id}`                   |
| --------- | ----------------------------------------------- |
| 기능        | 공개 프로필 조회                                       |
| 권한        | Public                                          |
| 설명        | 다른 사용자의 공개 프로필 정보를 조회한다. 이메일 등 민감 정보는 반환하지 않는다. |
| 성공 Status | `200 OK`                                        |
| 실패 Status | `404`                                           |

| Path Parameter | Type    | Required | 설명         |
| -------------- | ------- | -------- | ---------- |
| user_id        | integer | Yes      | 조회할 사용자 ID |

| Response Data     | Type        | 설명          |
| ----------------- | ----------- | ----------- |
| id                | integer     | 회원 ID       |
| nickname          | string      | 닉네임         |
| profile_image_url | string/null | 프로필 이미지 URL |
| bio               | string/null | 자기소개        |
| trust_score       | integer     | 사용자 신뢰도     |
| trade_count       | integer     | 거래 완료 횟수    |
| created_at        | datetime    | 가입일         |

| 반환하지 않는 정보    | 이유              |
| ------------- | --------------- |
| email         | 개인정보            |
| password_hash | 보안 정보           |
| report_count  | 악용 가능성          |
| role          | 일반 사용자에게 불필요    |
| status        | 정지/탈퇴 상태 노출 최소화 |

| Error Code       | HTTP Status | 설명                |
| ---------------- | ----------- | ----------------- |
| `USER_NOT_FOUND` | 404         | 사용자 없음            |
| `USER_DELETED`   | 404         | 탈퇴한 사용자           |
| `USER_SUSPENDED` | 404         | 정지 사용자 공개 여부 제한 시 |

---

| 공통 Validation     | 기준                                 |
| ----------------- | ---------------------------------- |
| nickname          | 2~20자                              |
| profile_image_url | URL 형식 또는 null                     |
| bio               | 최대 300자                            |
| status 변경         | User Router에서는 직접 변경 불가            |
| email 변경          | MVP에서는 제외                          |
| password 변경       | Auth 또는 별도 Password Router에서 처리 권장 |

| User 관련 Enum | 값           | 설명    |
| ------------ | ----------- | ----- |
| UserRole     | `USER`      | 일반 회원 |
| UserRole     | `ADMIN`     | 관리자   |
| UserStatus   | `ACTIVE`    | 정상 회원 |
| UserStatus   | `SUSPENDED` | 정지 회원 |
| UserStatus   | `DELETED`   | 탈퇴 회원 |
