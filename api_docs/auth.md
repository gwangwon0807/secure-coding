# Auth Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/auth` |
| 인증 | Public / HttpOnly Cookie + Server Session |
| 설명 | 회원가입, 로그인, 로그아웃, 토큰 재발급, 인증 사용자 조회 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/signup` | Public | 회원가입 | `email`, `nickname`, `password` |
| POST | `/login` | Public | 로그인 | `email`, `password` |
| POST | `/logout` | Cookie + CSRF | 세션 폐기 및 쿠키 삭제 | `X-CSRF-Token` |
| POST | `/refresh` | Refresh Cookie + CSRF | 토큰 회전 및 Access Token 재발급 | `X-CSRF-Token` |
| GET | `/me` | User | 현재 로그인 사용자 조회 | - |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `POST /signup` | `id`, `email`, `nickname`, `role`, `status`, `created_at` |
| `POST /login` | `user` + HttpOnly 인증 쿠키 |
| `GET /me` | `id`, `email`, `nickname`, `role`, `status` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 중복 제한 | `email`, `nickname` 중복 불가 |
| 지갑 생성 | 회원가입 트랜잭션에서 초기 잔액 0원의 지갑을 함께 생성 |
| 토큰 노출 | 응답 본문과 `localStorage`에 인증 토큰을 저장하지 않음 |
| Access Token | HttpOnly 쿠키, 기본 15분 |
| Refresh Token | HttpOnly 쿠키, 서버에는 해시만 저장, 재발급 시 회전 |
| CSRF | 변경 요청은 `csrf_token` 쿠키와 `X-CSRF-Token` 헤더 검증 |
| 로그아웃 | `auth_sessions.revoked_at` 기록 후 쿠키 삭제 |
| 인증 상태 | `SUSPENDED`, `DELETED` 사용자는 제한 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `EMAIL_ALREADY_EXISTS` | 이메일 중복 |
| `NICKNAME_ALREADY_EXISTS` | 닉네임 중복 |
| `INVALID_CREDENTIALS` | 로그인 실패 |
| `REFRESH_TOKEN_MISSING` | Refresh Token 없음 |
| `INVALID_REFRESH_TOKEN` | Refresh Token 오류 |
| `CSRF_TOKEN_INVALID` | CSRF 쿠키 또는 헤더 오류 |
| `SESSION_EXPIRED` | 만료되거나 폐기된 서버 세션 |
| `USER_SUSPENDED` | 정지 사용자 |
| `USER_DELETED` | 삭제 사용자 |
