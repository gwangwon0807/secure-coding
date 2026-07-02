| 구분            | 내용                                        |
| ------------- | ----------------------------------------- |
| Router        | Auth Router                               |
| Prefix        | `/api/v1/auth`                            |
| Method 수      | 5개                                        |
| 담당 기능         | 회원가입, 로그인, 로그아웃, 토큰 재발급, 현재 로그인 사용자 조회    |
| 인증 방식         | JWT + HttpOnly Cookie                     |
| 관련 테이블        | `users`                                   |
| 주요 Dependency | `get_current_user`, `require_active_user` |

| 번호 | Method | Endpoint   | 기능        | 권한     | 설명                                  |
| -- | ------ | ---------- | --------- | ------ | ----------------------------------- |
| 1  | POST   | `/signup`  | 회원가입      | Pub    lic | 이메일, 비밀번호, 닉네임으로 회원 생성              |
| 2  | POST   | `/login`   | 로그인       | Public | 이메일과 비밀번호 검증 후 토큰 발급                |
| 3  | POST   | `/logout`  | 로그아웃      | User   | 인증 쿠키 제거                            |
| 4  | POST   | `/refresh` | 토큰 재발급    | Public | Refresh Token 검증 후 Access Token 재발급 |
| 5  | GET    | `/me`      | 현재 사용자 조회 | User   | 현재 로그인한 사용자 정보 반환                   |

---

| API       | POST `/api/v1/auth/signup`    |
| --------- | ----------------------------- |
| 기능        | 회원가입                          |
| 권한        | Public                        |
| 설명        | 사용자가 이메일, 비밀번호, 닉네임으로 회원가입한다. |
| 성공 Status | `201 Created`                 |
| 실패 Status | `400`, `409`, `422`           |

| Request Body | Type   | Required | Validation    | 설명          |
| ------------ | ------ | -------- | ------------- | ----------- |
| email        | string | Yes      | 이메일 형식, 중복 불가 | 로그인 이메일     |
| password     | string | Yes      | 최소 8자 이상      | 로그인 비밀번호    |
| nickname     | string | Yes      | 2~20자         | 서비스 내 표시 이름 |

| Response Data | Type     | 설명       |
| ------------- | -------- | -------- |
| id            | integer  | 회원 ID    |
| email         | string   | 이메일      |
| nickname      | string   | 닉네임      |
| role          | string   | `USER`   |
| status        | string   | `ACTIVE` |
| created_at    | datetime | 가입일      |

| Error Code                | HTTP Status | 설명           |
| ------------------------- | ----------- | ------------ |
| `EMAIL_ALREADY_EXISTS`    | 409         | 이미 사용 중인 이메일 |
| `INVALID_PASSWORD_FORMAT` | 422         | 비밀번호 형식 오류   |
| `INVALID_NICKNAME_FORMAT` | 422         | 닉네임 형식 오류    |

---

| API       | POST `/api/v1/auth/login`                          |
| --------- | -------------------------------------------------- |
| 기능        | 로그인                                                |
| 권한        | Public                                             |
| 설명        | 이메일과 비밀번호를 검증하고 Access Token, Refresh Token을 발급한다. |
| 성공 Status | `200 OK`                                           |
| 실패 Status | `400`, `401`, `403`, `422`                         |

| Request Body | Type   | Required | Validation | 설명       |
| ------------ | ------ | -------- | ---------- | -------- |
| email        | string | Yes      | 이메일 형식     | 로그인 이메일  |
| password     | string | Yes      | 최소 1자 이상   | 로그인 비밀번호 |

| Response Data | Type    | 설명                               |
| ------------- | ------- | -------------------------------- |
| user.id       | integer | 회원 ID                            |
| user.email    | string  | 이메일                              |
| user.nickname | string  | 닉네임                              |
| user.role     | string  | `USER` 또는 `ADMIN`                |
| user.status   | string  | `ACTIVE`, `SUSPENDED`, `DELETED` |

| Cookie        | 설정                         | 설명                   |
| ------------- | -------------------------- | -------------------- |
| access_token  | HttpOnly, Secure, SameSite | API 인증용 토큰           |
| refresh_token | HttpOnly, Secure, SameSite | Access Token 재발급용 토큰 |

| Error Code            | HTTP Status | 설명              |
| --------------------- | ----------- | --------------- |
| `INVALID_CREDENTIALS` | 401         | 이메일 또는 비밀번호 불일치 |
| `USER_DELETED`        | 403         | 탈퇴 처리된 회원       |
| `USER_SUSPENDED`      | 403         | 정지된 회원          |

---

| API       | POST `/api/v1/auth/logout`            |
| --------- | ------------------------------------- |
| 기능        | 로그아웃                                  |
| 권한        | User                                  |
| 설명        | Access Token, Refresh Token 쿠키를 제거한다. |
| 성공 Status | `200 OK`                              |
| 실패 Status | `401`                                 |

| Request Body | Type | Required | 설명             |
| ------------ | ---- | -------- | -------------- |
| 없음           | -    | -        | 쿠키 기반 인증 정보 사용 |

| Response Data | Type | 설명        |
| ------------- | ---- | --------- |
| null          | null | 별도 데이터 없음 |

| Cookie 처리        | 설명        |
| ---------------- | --------- |
| access_token 삭제  | 인증 쿠키 제거  |
| refresh_token 삭제 | 재발급 쿠키 제거 |

| Error Code     | HTTP Status | 설명           |
| -------------- | ----------- | ------------ |
| `UNAUTHORIZED` | 401         | 로그인되지 않은 사용자 |

---

| API       | POST `/api/v1/auth/refresh`                  |
| --------- | -------------------------------------------- |
| 기능        | Access Token 재발급                             |
| 권한        | Public                                       |
| 설명        | Refresh Token을 검증한 뒤 새로운 Access Token을 발급한다. |
| 성공 Status | `200 OK`                                     |
| 실패 Status | `401`, `403`                                 |

| Request Body | Type | Required | 설명                  |
| ------------ | ---- | -------- | ------------------- |
| 없음           | -    | -        | Refresh Token 쿠키 사용 |

| Response Data | Type | 설명          |
| ------------- | ---- | ----------- |
| null          | null | 토큰은 쿠키로 재설정 |

| Cookie        | 설정                         | 설명             |
| ------------- | -------------------------- | -------------- |
| access_token  | HttpOnly, Secure, SameSite | 새 Access Token |
| refresh_token | HttpOnly, Secure, SameSite | 필요 시 갱신 가능     |

| Error Code              | HTTP Status | 설명                    |
| ----------------------- | ----------- | --------------------- |
| `REFRESH_TOKEN_MISSING` | 401         | Refresh Token 없음      |
| `REFRESH_TOKEN_EXPIRED` | 401         | Refresh Token 만료      |
| `INVALID_REFRESH_TOKEN` | 401         | 유효하지 않은 Refresh Token |
| `USER_NOT_ACTIVE`       | 403         | 정상 상태가 아닌 사용자         |

---

| API       | GET `/api/v1/auth/me`     |
| --------- | ------------------------- |
| 기능        | 현재 로그인 사용자 조회             |
| 권한        | User                      |
| 설명        | 현재 로그인한 사용자의 기본 정보를 반환한다. |
| 성공 Status | `200 OK`                  |
| 실패 Status | `401`, `403`, `404`       |

| Request Body | Type | Required | 설명                 |
| ------------ | ---- | -------- | ------------------ |
| 없음           | -    | -        | Access Token 쿠키 사용 |

| Response Data     | Type        | 설명                |
| ----------------- | ----------- | ----------------- |
| id                | integer     | 회원 ID             |
| email             | string      | 이메일               |
| nickname          | string      | 닉네임               |
| profile_image_url | string/null | 프로필 이미지 URL       |
| role              | string      | `USER` 또는 `ADMIN` |
| status            | string      | 회원 상태             |
| trust_score       | integer     | 사용자 신뢰도           |
| created_at        | datetime    | 가입일               |

| Error Code             | HTTP Status | 설명                   |
| ---------------------- | ----------- | -------------------- |
| `ACCESS_TOKEN_MISSING` | 401         | Access Token 없음      |
| `ACCESS_TOKEN_EXPIRED` | 401         | Access Token 만료      |
| `INVALID_ACCESS_TOKEN` | 401         | 유효하지 않은 Access Token |
| `USER_NOT_FOUND`       | 404         | 사용자 없음               |
| `USER_NOT_ACTIVE`      | 403         | 정상 상태가 아닌 사용자        |

---

| 공통 Validation  | 기준                           |
| -------------- | ---------------------------- |
| email          | RFC 이메일 형식                   |
| password       | 최소 8자 이상, MVP에서는 복잡도 검사는 선택  |
| nickname       | 2~20자                        |
| role 기본값       | `USER`                       |
| status 기본값     | `ACTIVE`                     |
| password 저장 방식 | 평문 저장 금지, `password_hash` 저장 |
| 비밀번호 해시        | `bcrypt` 또는 `argon2`         |
| Token 저장 위치    | HttpOnly Cookie              |
| 응답 형식          | JSON                         |

| Auth 관련 Enum | 값           | 설명    |
| ------------ | ----------- | ----- |
| UserRole     | `USER`      | 일반 회원 |
| UserRole     | `ADMIN`     | 관리자   |
| UserStatus   | `ACTIVE`    | 정상 회원 |
| UserStatus   | `SUSPENDED` | 정지 회원 |
| UserStatus   | `DELETED`   | 탈퇴 회원 |
