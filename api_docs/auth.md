# Auth Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/auth` |
| Method 수 | 5 |
| 담당 기능 | 회원가입, 로그인, 로그아웃, 토큰 재발급, 인증 사용자 조회 |
| 인증 방식 | JWT + HttpOnly Cookie |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/signup` | 회원가입 |
| POST | `/login` | 로그인 및 토큰 발급 |
| POST | `/logout` | 인증 쿠키 제거 |
| POST | `/refresh` | Refresh Token 기반 재발급 |
| GET | `/me` | 현재 로그인 사용자 조회 |

## 주요 규칙

- `signup`은 `email`, `nickname` 중복을 허용하지 않는다.
- `login` 응답은 쿠키 발급과 함께 `access_token`을 반환한다.
- `logout`은 인증 쿠키를 제거한다.
- `me`는 `ACTIVE` 사용자만 허용한다.

## 대표 요청/응답

### POST `/api/v1/auth/signup`

Request
```json
{
  "email": "user@example.com",
  "nickname": "사용자",
  "password": "password1234"
}
```

Response `201`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "사용자",
  "role": "USER",
  "status": "ACTIVE",
  "created_at": "2026-07-03T12:00:00"
}
```

### POST `/api/v1/auth/login`

Request
```json
{
  "email": "user@example.com",
  "password": "password1234"
}
```

Response `200`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "사용자",
    "role": "USER",
    "status": "ACTIVE"
  },
  "access_token": "jwt-token"
}
```

### GET `/api/v1/auth/me`

Response `200`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "사용자",
  "role": "USER",
  "status": "ACTIVE"
}
```

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `EMAIL_ALREADY_EXISTS` | 이미 가입된 이메일 |
| `NICKNAME_ALREADY_EXISTS` | 이미 사용 중인 닉네임 |
| `INVALID_CREDENTIALS` | 로그인 정보 불일치 |
| `REFRESH_TOKEN_MISSING` | Refresh Token 없음 |
| `INVALID_REFRESH_TOKEN` | Refresh Token 오류 |
| `USER_DELETED` | 탈퇴 사용자 |
| `USER_SUSPENDED` | 정지 사용자 |
