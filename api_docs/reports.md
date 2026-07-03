# Report Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/reports` |
| Method 수 | 3 |
| 담당 기능 | 신고 등록, 내 신고 목록/상세 조회 |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `` | 신고 등록 |
| GET | `/me` | 내 신고 목록 조회 |
| GET | `/{report_id}` | 내 신고 상세 조회 |

## 지원 신고 대상

| 대상 타입 | 설명 |
| --- | --- |
| `ITEM` | 상품 신고 |
| `USER` | 사용자 신고 |
| `COMMUNITY_POST` | 커뮤니티 글 신고 |
| `COMMUNITY_COMMENT` | 커뮤니티 댓글 신고 |
| `CHAT_ROOM` | 채팅방 신고 |
| `MESSAGE` | 메시지 신고 |

## 신고 생성 예시

```json
{
  "target_type": "COMMUNITY_COMMENT",
  "target_id": 15,
  "reason": "ABUSIVE_LANGUAGE",
  "detail": "욕설이 포함되어 있습니다."
}
```

## 자동 처리 규칙

- 같은 사용자는 같은 대상에 중복 신고할 수 없다.
- 상품 신고가 누적되면 일정 횟수 이상에서 자동 숨김 처리될 수 있다.
- 사용자 신고 누적은 관리자 검토 대상 표시 기준으로 활용된다.

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `TARGET_NOT_FOUND` | 신고 대상 없음 |
| `DUPLICATE_REPORT` | 중복 신고 |
| `CANNOT_REPORT_SELF` | 자기 자신 신고 불가 |
| `CANNOT_REPORT_OWN_ITEM` | 자기 상품 신고 불가 |
| `CANNOT_REPORT_OWN_POST` | 자기 글 신고 불가 |
| `CANNOT_REPORT_OWN_COMMENT` | 자기 댓글 신고 불가 |
| `FORBIDDEN_CHAT_REPORT` | 채팅 참여자가 아님 |
