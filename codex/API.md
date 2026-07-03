# 중고거래 플랫폼 API 요약

기준:
- 현재 저장소에 실제로 구현된 API 기준
- 송금/지갑 기능까지 반영한 최신 상태

## 1. 현재 구현 Router 요약

| 번호 | Router | Prefix | Method 수 | 역할 |
| --- | --- | --- | ---: | --- |
| 1 | Auth Router | `/api/v1/auth` | 5 | 회원가입, 로그인, 로그아웃, 토큰 재발급, 인증 사용자 조회 |
| 2 | User Router | `/api/v1/users` | 6 | 내 프로필, 내 상품 목록, 프로필 수정, 비밀번호 변경, 회원 탈퇴, 공개 프로필 |
| 3 | Item Router | `/api/v1/items` | 6 | 상품 등록, 목록/상세 조회, 수정, 삭제, 상태 변경 |
| 4 | Image Router | `/api/v1/images` | 3 | 상품/커뮤니티 이미지 업로드, 이미지 삭제 |
| 5 | Category Router | `/api/v1/categories` | 1 | 카테고리 목록 조회 |
| 6 | Community Router | `/api/v1/community` | 8 | 커뮤니티 글/댓글 조회, 등록, 수정, 삭제 |
| 7 | Chat Router | `/api/v1/chat-rooms` | 7 | 채팅방 생성, 목록/상세 조회, 메시지 조회/전송, 읽음 처리, 삭제 |
| 8 | Transaction Router | `/api/v1/transactions` | 7 | 거래 요청, 목록/상세 조회, 수락, 거절, 완료, 취소 |
| 9 | Transfer Router | `/api/v1/transfers` | 7 | 지갑 조회, 입금/출금, 원장 조회, 송금 생성, 송금 내역 조회 |
| 10 | Report Router | `/api/v1/reports` | 3 | 신고 등록, 내 신고 목록/상세 조회 |
| 11 | Block Router | `/api/v1/blocks` | 3 | 사용자 차단, 차단 목록, 차단 해제 |
| 12 | Admin Router | `/api/v1/admin` | 19 | 회원/상품/신고/거래/커뮤니티/채팅/지갑/송금/감사로그 관리 |

| 총 Router 수 | 총 Method 수 |
| --- | ---: |
| 12개 | 75개 |

## 2. 라우터별 문서 위치

| Router | 문서 |
| --- | --- |
| Auth | `api_docs/auth.md` |
| Users | `api_docs/user.md` |
| Items | `api_docs/item.md` |
| Images | `api_docs/images.md` |
| Categories | `api_docs/categories.md` |
| Community | `api_docs/community.md` |
| Chat Rooms | `api_docs/chat-rooms.md` |
| Transactions | `api_docs/transactions.md` |
| Transfers | `api_docs/transfers.md` |
| Reports | `api_docs/reports.md` |
| Blocks | `api_docs/blocks.md` |
| Admin | `api_docs/admin.md` |

## 3. 현재 구현 핵심 사항

- 인증은 `JWT + HttpOnly Cookie` 기반이며, 프론트 동기화를 위해 로그인 응답에 `access_token`도 반환한다.
- 상품 검색은 `keyword`, `category_id`, `min_price`, `max_price`, `location`, `status`, `sort`를 지원한다.
- 커뮤니티는 글/댓글 CRUD와 다중 이미지 업로드를 지원한다.
- 신고는 `ITEM`, `USER`, `COMMUNITY_POST`, `COMMUNITY_COMMENT`, `CHAT_ROOM`, `MESSAGE` 대상까지 확장 가능 구조다.
- 송금은 내부 지갑 기반으로 구현되어 있으며, 사용자 첫 접근 시 테스트 잔액이 자동 생성된다.
- 관리자 API는 사용자, 상품, 신고, 거래뿐 아니라 커뮤니티, 채팅, 지갑, 송금 조회/관리까지 확장되었다.

## 4. 변경 이력 요약

- `Transfer Router` 추가
- `Admin Router`에 커뮤니티/채팅/지갑/송금 관리 API 추가
- 프론트 상태 판별을 위해 토큰 기반 인증 동기화 로직 보완
- 지갑 원장(`wallet_ledgers`)과 사용자 송금(`transfers`) 도메인 추가
