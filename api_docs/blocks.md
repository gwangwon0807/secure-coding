# Blocks Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/blocks` |
| 인증 | User |
| 설명 | 사용자 차단, 차단 목록, 차단 해제 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/` | User | 사용자 차단 | `blocked_user_id` |
| GET | `/` | User | 차단 목록 조회 | `page`, `size` |
| DELETE | `/{user_id}` | User | 차단 해제 | - |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 자기 차단 | 자기 자신 차단 불가 |
| 중복 제한 | 동일 사용자 중복 차단 불가 |
| 채팅 영향 | 차단 관계 시 채팅방 생성 / 메시지 전송 제한 |
| 해제 방식 | `deleted_at` 기반 soft delete |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /` | `id`, `blocked_user`, `created_at`, `pagination` |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `BLOCKED_USER_NOT_FOUND` | 차단 대상 없음 |
| `CANNOT_BLOCK_SELF` | 자기 자신 차단 불가 |
| `ALREADY_BLOCKED` | 이미 차단됨 |
| `BLOCK_NOT_FOUND` | 차단 기록 없음 |
