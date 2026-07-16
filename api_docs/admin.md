# Admin Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/admin` |
| 인증 | Admin |
| 설명 | 회원, 상품, 신고, 거래, 커뮤니티, 채팅, 지갑, 송금, 감사로그 관리 |

## Endpoint

### 회원 / 상품 / 신고 / 거래

| Method | Endpoint | 설명 | 핵심 필드 |
| --- | --- | --- | --- |
| GET | `/users` | 회원 목록 조회 | `keyword`, `status`, `role`, `page`, `size` |
| PATCH | `/users/{user_id}/status` | 회원 상태 변경 | `status`, `reason` |
| GET | `/users/{user_id}` | 회원 상세 조회 | 활동 내역, 신고, 지갑, 채팅, 거래, 송금 |
| GET | `/items` | 상품 목록 조회 | `keyword`, `seller_id`, `category_id`, `status`, `reported_only`, `page`, `size` |
| PATCH | `/items/{item_id}/status` | 상품 상태 변경 | `status`, `reason` |
| GET | `/items/{item_id}` | 상품 상세 조회 | 이미지, 신고, 거래, 채팅 |
| GET | `/reports` | 신고 목록 조회 | `status`, `target_type`, `reason`, `include_resolved`, `page`, `size` |
| GET | `/reports/{report_id}` | 신고 상세 조회 | 신고자, 대상 상세, 처리 정보 |
| PATCH | `/reports/{report_id}` | 신고 처리 | `status`, `action_type`, `admin_memo`, `result_message` |
| GET | `/transactions` | 전체 거래 조회 | `page`, `size` |

### 커뮤니티 / 채팅

| Method | Endpoint | 설명 | 핵심 필드 |
| --- | --- | --- | --- |
| GET | `/community/posts` | 커뮤니티 글 목록 조회 | `keyword`, `reported_only`, `page`, `size` |
| PATCH | `/community/posts/{post_id}/hide` | 글 숨김 / 복구 | `reason` |
| GET | `/community/posts/{post_id}` | 글 상세 조회 | 작성자, 이미지, 댓글, 신고 |
| GET | `/community/comments` | 댓글 목록 조회 | `keyword`, `reported_only`, `page`, `size` |
| PATCH | `/community/comments/{comment_id}/hide` | 댓글 숨김 / 복구 | `reason` |
| GET | `/community/comments/{comment_id}` | 댓글 상세 조회 | 작성자, 원글, 신고 |
| GET | `/chat-rooms` | 채팅방 목록 조회 | `keyword`, `page`, `size` |
| GET | `/chat-rooms/{room_id}/messages` | 채팅 메시지 조회 | `page`, `size` |
| GET | `/chat-rooms/{room_id}` | 채팅방 상세 조회 | 상품, 구매자, 판매자, 메시지, 신고 |
| DELETE | `/chat-rooms/{room_id}` | 채팅방 삭제 | - |

### 지갑 / 송금 / 로그

| Method | Endpoint | 설명 | 핵심 필드 |
| --- | --- | --- | --- |
| GET | `/wallets` | 사용자 지갑 목록 조회 | `keyword`, `page`, `size` |
| PATCH | `/wallets/{user_id}/adjust` | 사용자 잔액 조정 | `amount`, `reason` |
| GET | `/deposit-requests` | 전체 충전 요청 목록 | `status`, `page`, `size` |
| GET | `/deposit-requests/{request_id}` | 충전 요청 상세 | - |
| PATCH | `/deposit-requests/{request_id}/approve` | 충전 승인 및 잔액 반영 | `reason` |
| PATCH | `/deposit-requests/{request_id}/reject` | 충전 거절 | `reason` |
| GET | `/transfers` | 전체 송금 조회 | `page`, `size` |
| GET | `/transfers/{transfer_id}` | 송금 상세 조회 | 송신자, 수신자, 금액, 메모, 상태 |
| GET | `/audit-logs` | 감사 로그 조회 | `page`, `size` |

## 관리자 조치 타입

| 값 | 설명 |
| --- | --- |
| `NONE` | 조치 없음 |
| `ITEM_HIDDEN` | 상품 숨김 |
| `ITEM_DELETED` | 상품 삭제 |
| `USER_SUSPENDED` | 사용자 정지 |
| `USER_DELETED` | 사용자 삭제 |
| `COMMUNITY_POST_HIDDEN` | 게시글 숨김 |
| `COMMUNITY_COMMENT_HIDDEN` | 댓글 숨김 |
| `CHAT_ROOM_DELETED` | 채팅방 삭제 |
| `MESSAGE_DELETED` | 메시지 삭제 |
| `REPORT_REJECTED` | 신고 반려 |

## 주요 규칙

| 항목 | 내용 |
| --- | --- |
| 권한 | 모든 API는 `ADMIN` 전용 |
| 감사 로그 | 주요 변경 작업은 `audit_logs` 기록 |
| 신고 처리 | 대상별 실제 숨김 / 삭제 / 정지 반영 |
| 잔액 조정 | 결과 잔액이 음수가 되면 실패 |
| 충전 승인 | `PENDING` 요청만 처리, 요청과 지갑을 DB 행 잠금으로 중복 승인 방지 |
| 지갑 정합성 | 승인·조정·송금은 잔액 변경과 원장 기록을 한 트랜잭션으로 처리 |

## 주요 에러

| 코드 | 설명 |
| --- | --- |
| `ADMIN_REQUIRED` | 관리자 권한 필요 |
| `USER_NOT_FOUND` | 사용자 없음 |
| `ITEM_NOT_FOUND` | 상품 없음 |
| `REPORT_NOT_FOUND` | 신고 없음 |
| `CHAT_ROOM_NOT_FOUND` | 채팅방 없음 |
| `COMMUNITY_POST_NOT_FOUND` | 게시글 없음 |
| `COMMUNITY_COMMENT_NOT_FOUND` | 댓글 없음 |
| `ACTIVE_TRANSACTION_EXISTS` | 진행 중 거래 존재 |
| `CANNOT_UPDATE_SELF_STATUS` | 자기 자신 상태 변경 불가 |
| `INSUFFICIENT_BALANCE` | 잔액 부족 |
| `DEPOSIT_REQUEST_NOT_FOUND` | 충전 요청 없음 |
| `DEPOSIT_REQUEST_ALREADY_PROCESSED` | 이미 승인되거나 거절된 요청 |
| `INVALID_REPORT_ACTION_FOR_TARGET` | 신고 대상과 조치 불일치 |
