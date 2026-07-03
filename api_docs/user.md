# User Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/users` |
| Method 수 | 6 |
| 담당 기능 | 내 프로필, 내가 올린 상품, 프로필 수정, 비밀번호 변경, 회원 탈퇴, 공개 프로필 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/me` | 내 프로필 조회 |
| GET | `/me/items` | 내가 올린 상품 목록 조회 |
| PATCH | `/me` | 프로필 수정 |
| PATCH | `/me/password` | 비밀번호 변경 |
| DELETE | `/me` | 회원 탈퇴 |
| GET | `/{user_id}` | 공개 프로필 조회 |

## 대표 응답 필드

### GET `/api/v1/users/me`
- `id`, `email`, `nickname`
- `profile_image_url`, `bio`
- `role`, `status`
- `trust_score`, `trade_count`, `report_count`
- `created_at`, `updated_at`

### GET `/api/v1/users/me/items`
- 내가 등록한 판매 상품 목록
- 각 상품에 `thumbnail_url`, `status`, `price`, `location` 포함

### PATCH `/api/v1/users/me/password`
Request
```json
{
  "current_password": "old-password",
  "new_password": "new-password1234"
}
```

## 주요 규칙

- 공개 프로필은 `ACTIVE` 사용자만 조회 가능하다.
- 프로필 수정 시 닉네임 중복은 허용되지 않는다.
- 탈퇴 시 진행 중 거래가 있으면 실패한다.
- 탈퇴 시 `status=DELETED`, `bio/profile_image_url`는 초기화된다.

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `NICKNAME_ALREADY_EXISTS` | 닉네임 중복 |
| `INVALID_CURRENT_PASSWORD` | 현재 비밀번호 불일치 |
| `PASSWORD_SAME_AS_CURRENT` | 현재 비밀번호와 동일 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래 존재 |
| `USER_NOT_FOUND` | 사용자 없음 |
