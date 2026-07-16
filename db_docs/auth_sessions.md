# auth_sessions

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `auth_sessions` |
| 설명 | 로그인 세션, Refresh Token 회전 및 강제 폐기 관리 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `user_id` | integer | FK → `users.id`, INDEX |
| `refresh_token_hash` | varchar(64) | UNIQUE, Refresh Token SHA-256 해시 |
| `csrf_token_hash` | varchar(64) | CSRF Token SHA-256 해시 |
| `expires_at` | datetime | 세션 만료 시각, INDEX |
| `revoked_at` | datetime | 로그아웃·강제 폐기 시각, nullable |
| `created_at` | datetime | 로그인 시각 |
| `last_used_at` | datetime | 마지막 토큰 재발급 시각 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `user_id` | `users.id` |
