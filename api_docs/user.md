# User Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/users` |
| 인증 | User / Public 혼합 |
| 설명 | 내 프로필, 내 상품, 프로필 수정, 비밀번호 변경, 회원 탈퇴, 공개 프로필 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| GET | `/me` | User | 내 프로필 조회 | - |
| GET | `/me/items` | User | 내가 올린 상품 목록 | `page`, `size` |
| PATCH | `/me` | User | 프로필 수정 | `nickname`, `bio`, `profile_image_url` |
| PATCH | `/me/password` | User | 비밀번호 변경 | `current_password`, `new_password` |
| DELETE | `/me` | User | 회원 탈퇴 | - |
| GET | `/{user_id}` | Public | 공개 프로필 조회 | - |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /me` | `id`, `email`, `nickname`, `bio`, `profile_image_url`, `role`, `status`, `trust_score`, `trade_count`, `report_count` |
| `GET /me/items` | `id`, `title`, `price`, `status`, `location`, `thumbnail_url` |
| `GET /{user_id}` | `id`, `nickname`, `profile_image_url`, `bio`, `trade_count` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 공개 프로필 | `ACTIVE` 사용자만 조회 가능 |
| 프로필 수정 | 닉네임 중복 불가 |
| 회원 탈퇴 | 진행 중 거래가 있으면 실패 |
| 탈퇴 처리 | `status=DELETED`, 일부 프로필 정보 초기화 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `NICKNAME_ALREADY_EXISTS` | 닉네임 중복 |
| `INVALID_CURRENT_PASSWORD` | 현재 비밀번호 불일치 |
| `PASSWORD_SAME_AS_CURRENT` | 기존 비밀번호와 동일 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래 존재 |
| `USER_NOT_FOUND` | 사용자 없음 |
