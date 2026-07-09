# blocks

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `blocks` |
| 설명 | 사용자 차단 관계 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `blocker_id` | integer | FK → `users.id`, INDEX |
| `blocked_user_id` | integer | FK → `users.id`, INDEX |
| `created_at` | datetime | 생성일 |
| `deleted_at` | datetime | nullable |

## 제약 / 관계

| 항목 | 내용 |
| --- | --- |
| UNIQUE | `blocker_id + blocked_user_id` |
| FK | `blocker_id → users.id` |
| FK | `blocked_user_id → users.id` |

