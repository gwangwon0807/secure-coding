# Reports Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/reports` |
| 인증 | User |
| 설명 | 신고 등록, 내 신고 목록/상세 조회 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| POST | `/` | User | 신고 등록 | `target_type`, `target_id`, `reason`, `detail` |
| GET | `/me` | User | 내 신고 목록 조회 | `status_filter`, `target_type`, `page`, `size` |
| GET | `/{report_id}` | User | 내 신고 상세 조회 | - |

## 신고 대상 타입

| 값 | 설명 |
| --- | --- |
| `ITEM` | 상품 |
| `USER` | 사용자 |
| `COMMUNITY_POST` | 커뮤니티 글 |
| `COMMUNITY_COMMENT` | 커뮤니티 댓글 |
| `CHAT_ROOM` | 채팅방 |
| `MESSAGE` | 메시지 |

## 신고 상태값

| 값 | 설명 |
| --- | --- |
| `RECEIVED` | 접수 |
| `REVIEWING` | 검토중 |
| `RESOLVED` | 처리됨 |
| `REJECTED` | 반려 |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 중복 제한 | 같은 사용자가 같은 대상에 중복 신고 불가 |
| 자기 신고 | 자기 자신 / 자기 글 / 자기 댓글 / 자기 상품 신고 불가 |
| 상품 자동 처리 | 상품 신고 누적 시 자동 숨김 가능 |
| 사용자 누적 | 관리자 검토 대상 기준으로 활용 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `TARGET_NOT_FOUND` | 신고 대상 없음 |
| `DUPLICATE_REPORT` | 중복 신고 |
| `CANNOT_REPORT_SELF` | 자기 자신 신고 불가 |
| `CANNOT_REPORT_OWN_ITEM` | 자기 상품 신고 불가 |
| `CANNOT_REPORT_OWN_POST` | 자기 글 신고 불가 |
| `CANNOT_REPORT_OWN_COMMENT` | 자기 댓글 신고 불가 |
| `FORBIDDEN_CHAT_REPORT` | 채팅 참여자 아님 |
