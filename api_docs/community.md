# Community Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/community` |
| 인증 | Public / User 혼합 |
| 설명 | 커뮤니티 글/댓글 CRUD |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| GET | `/posts` | Public | 글 목록 조회 | `keyword`, `page`, `size` |
| POST | `/posts` | User | 글 등록 | `title`, `content`, `image_ids` |
| GET | `/posts/{post_id}` | Public | 글 상세 조회 | - |
| PATCH | `/posts/{post_id}` | User | 글 수정 | `title`, `content`, `image_ids` |
| DELETE | `/posts/{post_id}` | User | 글 삭제 | - |
| POST | `/posts/{post_id}/comments` | User | 댓글 등록 | `content` |
| PATCH | `/comments/{comment_id}` | User | 댓글 수정 | `content` |
| DELETE | `/comments/{comment_id}` | User | 댓글 삭제 | - |

## 응답 핵심

| API | 주요 응답 |
| --- | --- |
| `GET /posts` | `id`, `title`, `author`, `thumbnail_url`, `comment_count`, `created_at` |
| `GET /posts/{post_id}` | `title`, `content`, `author`, `images`, `comments`, `created_at` |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 이미지 연결 | 선업로드 후 `image_ids`로 연결 |
| 목록 검색 | 제목 + 본문 기준 `keyword` 검색 |
| 삭제 방식 | `deleted_at` 기반 soft delete |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `POST_NOT_FOUND` | 글 없음 |
| `COMMENT_NOT_FOUND` | 댓글 없음 |
| `INVALID_IMAGE_IDS` | 잘못된 이미지 ID |
| `FORBIDDEN` | 작성자 불일치 |
