# Auth Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/auth` |
| 인증 | Public / Cookie + JWT |
| 설명 | 회원가입, 로그인, 로그아웃, 토큰 재발급, 인증 사용자 조회 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/signup` | Public | 회원가입 | `email`, `nickname`, `password` |
| POST | `/login` | Public | 로그인 | `email`, `password` |
| POST | `/logout` | User | 로그아웃 | - |
| POST | `/refresh` | User | Access Token 재발급 | - |
| GET | `/me` | User | 현재 로그인 사용자 조회 | - |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `POST /signup` | `id`, `email`, `nickname`, `role`, `status`, `created_at` |
| `POST /login` | `user`, `access_token` |
| `GET /me` | `id`, `email`, `nickname`, `role`, `status` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 중복 제한 | `email`, `nickname` 중복 불가 |
| 로그인 응답 | `HttpOnly Cookie` + `access_token` 반환 |
| 인증 상태 | `SUSPENDED`, `DELETED` 사용자는 제한 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `EMAIL_ALREADY_EXISTS` | 이메일 중복 |
| `NICKNAME_ALREADY_EXISTS` | 닉네임 중복 |
| `INVALID_CREDENTIALS` | 로그인 실패 |
| `REFRESH_TOKEN_MISSING` | Refresh Token 없음 |
| `INVALID_REFRESH_TOKEN` | Refresh Token 오류 |
| `USER_SUSPENDED` | 정지 사용자 |
| `USER_DELETED` | 삭제 사용자 |
