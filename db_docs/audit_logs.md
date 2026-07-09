# audit_logs

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `audit_logs` |
| 설명 | 관리자 조치 로그 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `admin_id` | integer | FK → `users.id`, INDEX |
| `action` | varchar(100) | 관리자 액션 |
| `target_type` | varchar(50) | 대상 종류 |
| `target_id` | integer | 대상 ID |
| `reason` | text | 사유 |
| `created_at` | datetime | 생성일 |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `admin_id` | `users.id` |
