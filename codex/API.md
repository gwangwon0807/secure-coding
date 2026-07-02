기준: **MVP API 명세서 기준**, `method 수 = API Endpoint 개수`로 계산.

| 번호 | Router | Prefix | Method 수 | 역할 |
| --- | --- | --- | --- | --- |
| 1 | Auth Router | `/api/v1/auth` | 5 | 회원가입, 로그인, 로그아웃, 토큰 재발급, 내 정보 |
| 2 | User Router | `/api/v1/users` | 4 | 내 프로필, 공개 프로필, 회원 탈퇴 |
| 3 | Item Router | `/api/v1/items` | 6 | 상품 등록, 조회, 수정, 삭제, 상태 변경 |
| 4 | Image Router | `/api/v1/images` | 2 | 상품 이미지 업로드, 삭제 |
| 5 | Category Router | `/api/v1/categories` | 1 | 카테고리 목록 조회 |
| 6 | Chat Router | `/api/v1/chat-rooms` | 6 | 채팅방, 메시지, 읽음 처리 |
| 7 | Transaction Router | `/api/v1/transactions` | 7 | 거래 요청, 수락, 거절, 완료, 취소 |
| 8 | Report Router | `/api/v1/reports` | 3 | 신고 등록, 내 신고 조회 |
| 9 | Block Router | `/api/v1/blocks` | 3 | 사용자 차단, 차단 목록, 차단 해제 |
| 10 | Admin Router | `/api/v1/admin` | 9 | 회원, 상품, 신고, 거래, 로그 관리 |

| 총 Router 수 | 총 Method 수 |
| --- | --- |
| 10개 | 46개 |

다음은 **Auth Router부터** 하나씩 작성하면 됩니다.