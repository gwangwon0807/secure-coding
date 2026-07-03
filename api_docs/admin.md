# Admin Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/admin` |
| Method 수 | 17 |
| 담당 기능 | 회원, 상품, 신고, 거래, 커뮤니티, 채팅, 지갑, 송금, 감사로그 관리 |
| 권한 | `ADMIN` |

## Endpoint 목록

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/users` | 회원 목록 조회 |
| PATCH | `/users/{user_id}/status` | 회원 상태 변경 |
| GET | `/items` | 상품 목록 조회 |
| PATCH | `/items/{item_id}/status` | 상품 상태 변경 |
| GET | `/reports` | 신고 목록 조회 |
| GET | `/reports/{report_id}` | 신고 상세 조회 |
| PATCH | `/reports/{report_id}` | 신고 처리 |
| GET | `/transactions` | 전체 거래 조회 |
| GET | `/community/posts` | 커뮤니티 글 목록 조회 |
| PATCH | `/community/posts/{post_id}/hide` | 커뮤니티 글 숨김/복구 |
| GET | `/community/comments` | 커뮤니티 댓글 목록 조회 |
| PATCH | `/community/comments/{comment_id}/hide` | 커뮤니티 댓글 숨김/복구 |
| GET | `/chat-rooms` | 채팅방 목록 조회 |
| GET | `/chat-rooms/{room_id}/messages` | 채팅 메시지 조회 |
| DELETE | `/chat-rooms/{room_id}` | 채팅방 삭제 |
| GET | `/wallets` | 사용자 지갑 목록 조회 |
| PATCH | `/wallets/{user_id}/adjust` | 사용자 지갑 잔액 조정 |
| GET | `/transfers` | 전체 송금 내역 조회 |
| GET | `/audit-logs` | 관리자 조치 로그 조회 |

## 관리 범위

- 사용자 조회 및 제재
- 상품 조회 및 상태 변경
- 신고 조회 및 처리
- 전체 거래 조회
- 커뮤니티 글/댓글 숨김 및 복구
- 채팅방 조회 및 삭제
- 사용자 지갑 잔액 조정
- 전체 송금 내역 조회
- 감사 로그 조회

## 주요 규칙

- 모든 상태 변경/관리 작업은 관리자 권한이 필요하다.
- 주요 변경 작업은 `audit_logs`에 기록된다.
- 진행 중 거래가 있는 사용자/상품은 일부 변경이 제한된다.
- 커뮤니티 글/댓글 숨김 API는 동일 엔드포인트를 다시 호출하면 복구된다.
- 지갑 조정은 양수/음수 모두 가능하지만 잔액이 음수가 되면 실패한다.

## 주요 에러 코드

| 코드 | 설명 |
| --- | --- |
| `ADMIN_REQUIRED` | 관리자 권한 필요 |
| `USER_NOT_FOUND` | 대상 사용자 없음 |
| `ITEM_NOT_FOUND` | 대상 상품 없음 |
| `REPORT_NOT_FOUND` | 신고 없음 |
| `CHAT_ROOM_NOT_FOUND` | 채팅방 없음 |
| `COMMUNITY_POST_NOT_FOUND` | 게시글 없음 |
| `COMMUNITY_COMMENT_NOT_FOUND` | 댓글 없음 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래 존재 |
| `CANNOT_UPDATE_SELF_STATUS` | 자기 계정 상태 변경 불가 |
| `INSUFFICIENT_BALANCE` | 잔액 조정 결과가 음수 |
