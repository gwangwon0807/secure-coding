# users

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `users` |
| 설명 | 회원 정보 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK, INDEX |
| `email` | varchar(255) | UNIQUE, INDEX |
| `password_hash` | varchar(255) | 비밀번호 해시 |
| `nickname` | varchar(20) | UNIQUE, INDEX |
| `profile_image_url` | varchar(500) | nullable |
| `bio` | text | nullable |
| `role` | enum | `USER`, `ADMIN` |
| `status` | enum | `ACTIVE`, `SUSPENDED`, `DELETED` |
| `trust_score` | integer | default 0 |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `id` | `items.seller_id`, `community_posts.author_id`, `community_comments.author_id`, `chat_rooms.buyer_id`, `chat_rooms.seller_id`, `messages.sender_id`, `transactions.buyer_id`, `transactions.seller_id`, `wallets.user_id`, `transfers.sender_id`, `transfers.recipient_id`, `reports.reporter_id`, `reports.admin_id`, `blocks.blocker_id`, `blocks.blocked_user_id`, `audit_logs.admin_id` |

