# community_posts

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `community_posts` |
| 설명 | 커뮤니티 글 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `author_id` | integer | FK → `users.id`, INDEX |
| `title` | varchar(120) | 제목 |
| `content` | text | 본문 |
| `created_at` | datetime | 생성일 |
| `updated_at` | datetime | 수정일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `author_id` | `users.id` |
| `id` | `community_comments.post_id`, `community_post_images.post_id` |

