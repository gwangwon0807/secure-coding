# reports

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `reports` |
| 설명 | 신고 정보 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `reporter_id` | integer | FK → `users.id`, INDEX |
| `target_type` | enum | `ITEM`, `USER`, `COMMUNITY_POST`, `COMMUNITY_COMMENT`, `CHAT_ROOM`, `MESSAGE` |
| `target_id` | integer | INDEX |
| `reason` | enum | `SCAM_SUSPECTED`, `PROHIBITED_ITEM`, `FALSE_INFORMATION`, `ABUSIVE_LANGUAGE`, `SPAM`, `INAPPROPRIATE_CONTENT`, `ETC` |
| `detail` | text | nullable |
| `status` | enum | `RECEIVED`, `REVIEWING`, `RESOLVED`, `REJECTED` |
| `action_type` | enum | 관리자 조치 타입 |
| `admin_id` | integer | FK → `users.id`, nullable |
| `admin_memo` | text | nullable |
| `result_message` | varchar(500) | nullable |
| `created_at` | datetime | 생성일 |
| `resolved_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `reporter_id` | `users.id` |
| `admin_id` | `users.id` |

