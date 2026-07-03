# 중고거래 플랫폼 시스템 아키텍처 요약

## 1. 전체 구성

| 영역 | 선택 기술 | 역할 |
| --- | --- | --- |
| Frontend | Next.js + TypeScript | 사용자 웹 UI |
| Backend | FastAPI + Python | REST API, 비즈니스 로직 |
| Database | PostgreSQL | 서비스 데이터 저장 |
| 실행 방식 | Docker Compose | 프론트/백엔드/DB 통합 실행 |
| 인증 방식 | JWT + HttpOnly Cookie |
| 프론트 인증 동기화 | 로그인 응답 `access_token` + localStorage |

## 2. 아키텍처 흐름

1. 사용자가 Next.js 프론트엔드에 접속한다.
2. 프론트엔드는 FastAPI 백엔드로 REST API 요청을 보낸다.
3. 백엔드는 인증, 상품, 커뮤니티, 채팅, 거래, 신고, 송금, 관리자 로직을 처리한다.
4. PostgreSQL에 저장된 데이터를 읽고 쓴다.
5. 업로드 이미지는 백엔드 정적 파일 경로(`/uploads`)로 제공된다.

## 3. Docker 실행 구조

| 컨테이너 | 역할 |
| --- | --- |
| `frontend` | Next.js 서버 |
| `backend` | FastAPI 서버 |
| `db` | PostgreSQL |

## 4. 현재 프로젝트 구성

| 경로 | 역할 |
| --- | --- |
| `frontend/app` | 페이지 라우팅 |
| `frontend/components` | 공통 UI 컴포넌트 |
| `frontend/lib` | API 호출, 인증 유틸 |
| `backend/app/api/v1/endpoints` | 라우터 |
| `backend/app/models` | ORM 모델 |
| `backend/app/schemas` | 요청/응답 스키마 |
| `api_docs` | 라우터별 API 문서 |
| `codex` | 요구사항, API 요약, 시스템 설계 문서 |

## 5. Backend Router 구성

| Router | Prefix | 역할 |
| --- | --- | --- |
| Auth | `/api/v1/auth` | 회원가입, 로그인, 토큰 재발급, 인증 사용자 조회 |
| Users | `/api/v1/users` | 프로필, 비밀번호, 내 상품, 회원 탈퇴 |
| Items | `/api/v1/items` | 상품 CRUD, 검색, 상태 변경 |
| Images | `/api/v1/images` | 상품/커뮤니티 이미지 업로드 및 삭제 |
| Categories | `/api/v1/categories` | 카테고리 조회 |
| Community | `/api/v1/community` | 커뮤니티 글/댓글 관리 |
| Chat Rooms | `/api/v1/chat-rooms` | 채팅방, 메시지, 읽음 처리 |
| Transactions | `/api/v1/transactions` | 거래 요청, 취소, 완료 |
| Transfers | `/api/v1/transfers` | 지갑, 송금, 원장 조회 |
| Reports | `/api/v1/reports` | 신고 등록, 내 신고 조회 |
| Blocks | `/api/v1/blocks` | 사용자 차단 |
| Admin | `/api/v1/admin` | 운영 관리 |

## 6. Database 구성

| 테이블 | 역할 |
| --- | --- |
| `users` | 회원 정보 |
| `categories` | 상품 카테고리 |
| `items` | 상품 정보 |
| `item_images` | 상품 이미지 |
| `community_posts` | 커뮤니티 글 |
| `community_comments` | 커뮤니티 댓글 |
| `community_post_images` | 커뮤니티 이미지 |
| `chat_rooms` | 채팅방 |
| `messages` | 채팅 메시지 |
| `transactions` | 거래 정보 |
| `wallets` | 사용자 지갑 |
| `wallet_ledgers` | 지갑 원장 |
| `transfers` | 사용자 간 송금 |
| `reports` | 신고 정보 |
| `blocks` | 사용자 차단 |
| `audit_logs` | 관리자 조치 로그 |

## 7. 핵심 도메인 흐름

| 기능 | 현재 흐름 |
| --- | --- |
| 회원 | 가입 → 로그인 → 내 정보/비밀번호 관리 |
| 상품 | 등록 → 목록/검색 → 상세 → 수정/삭제/상태 변경 |
| 커뮤니티 | 글 작성 → 댓글 작성 → 신고 처리 |
| 채팅 | 상품 기반 채팅방 생성 → 메시지 송수신 → 송금 진입 |
| 거래 | 구매 의사 → 예약중 전환 → 양측 완료 확인 → 거래완료 |
| 송금 | 지갑 생성 → 사용자 송금 → 원장 기록 |
| 신고 | 신고 접수 → 관리자 검토 → 상품 숨김 또는 사용자 제재 |
| 관리자 | 회원/상품/신고/거래/커뮤니티/채팅/지갑/송금/감사로그 관리 |

## 8. 설계 기준

| 기준 | 설명 |
| --- | --- |
| MVP 우선 | 핵심 거래 흐름을 먼저 안정화 |
| 명확한 분리 | Frontend / Backend / DB / Docs 분리 |
| 확장성 | 커뮤니티, 신고, 송금 등 기능 추가 가능 구조 |
| 운영성 | 관리자 기능과 감사로그 유지 |
| 보안 | JWT, Cookie, 권한 검증, 신고/차단/송금 제한 반영 |
