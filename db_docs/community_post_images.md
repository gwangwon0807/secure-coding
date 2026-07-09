# community_post_images

| 항목 | 내용 |
| --- | --- |
| 테이블명 | `community_post_images` |
| 설명 | 커뮤니티 글 이미지 |
| PK | `id` |

## 컬럼

| 컬럼명 | 타입 | 제약 / 설명 |
| --- | --- | --- |
| `id` | integer | PK |
| `post_id` | integer | FK → `community_posts.id`, nullable, INDEX |
| `uploader_id` | integer | FK → `users.id`, INDEX |
| `image_url` | varchar(500) | 공개 URL |
| `storage_key` | varchar(500) | 저장 키 |
| `sort_order` | integer | default 1 |
| `created_at` | datetime | 생성일 |
| `deleted_at` | datetime | nullable |

## 관계

| 컬럼 | 연결 |
| --- | --- |
| `post_id` | `community_posts.id` |
| `uploader_id` | `users.id` |

