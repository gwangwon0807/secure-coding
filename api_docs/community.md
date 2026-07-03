# Community Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/community` |
| Method 수 | 8 |
| 담당 기능 | 커뮤니티 글/댓글 목록 조회, 등록, 수정, 삭제 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/posts` | 글 목록 조회 |
| POST | `/posts` | 글 등록 |
| GET | `/posts/{post_id}` | 글 상세 조회 |
| PATCH | `/posts/{post_id}` | 글 수정 |
| DELETE | `/posts/{post_id}` | 글 삭제 |
| POST | `/posts/{post_id}/comments` | 댓글 등록 |
| PATCH | `/comments/{comment_id}` | 댓글 수정 |
| DELETE | `/comments/{comment_id}` | 댓글 삭제 |

## 글 목록 조회

- `keyword`, `page`, `size` 지원
- 목록에는 `thumbnail_url`, `comment_count` 포함

## 글 등록/수정

```json
{
  "title": "제목 없음",
  "content": "본문",
  "image_ids": [10, 11]
}
```

- 커뮤니티 이미지는 별도 업로드 후 `image_ids`로 연결
- 최대 10장 권장

## 상세 응답 특징

- 작성자 정보 포함
- 이미지 배열 포함
- 댓글 배열 포함

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `POST_NOT_FOUND` | 글 없음 |
| `COMMENT_NOT_FOUND` | 댓글 없음 |
| `INVALID_IMAGE_IDS` | 잘못된 이미지 ID |
| `FORBIDDEN` | 작성자/권한 불일치 |
