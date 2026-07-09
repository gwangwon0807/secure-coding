# community_comments

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `community_comments` |
| 설명 | 커뮤니티 댓글 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `post_id` | integer | FK → `community_posts.id`, INDEX |
| `author_id` | integer | FK → `users.id`, INDEX |
| `content` | text | 댓글 내용 |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `post_id` | `community_posts.id` |
| `author_id` | `users.id` |

