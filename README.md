# 한국어 중고거래 웹서비스 MVP

문서 기준으로 구현한 FastAPI + Next.js + PostgreSQL 기반 중고거래 플랫폼 MVP입니다. `docker compose up --build` 한 번으로 프론트엔드, 백엔드, DB를 함께 실행할 수 있도록 구성했습니다.

## 구현한 범위

- JWT HttpOnly 쿠키 기반 인증
- 회원가입, 로그인, 로그아웃, 내 정보 조회/수정, 회원 탈퇴
- 카테고리 조회, 상품 이미지 업로드, 상품 등록/목록/상세/수정/삭제/상태 변경
- 채팅방 생성, 채팅 목록/상세, 메시지 조회/전송, 읽음 처리
- 거래 요청, 수락, 거절, 완료, 취소, 거래 목록/상세
- 내부 지갑, 입금/출금, 사용자 간 송금, 지갑 원장 조회
- 신고 등록, 내 신고 목록/상세
- 사용자 차단/해제, 차단 목록 조회
- 관리자 회원/상품/신고/거래/커뮤니티/채팅/지갑/송금/감사 로그 API
- 한국어 기반 주요 화면: 상품 목록, 로그인, 회원가입, 상품 등록, 상품 상세, 거래 목록, 채팅 목록, 지갑/송금, 관리자 화면

## 프로젝트 구조

```text
backend/    FastAPI 백엔드
frontend/   Next.js 프론트엔드
api_docs/   라우터별 API 명세
codex/      요구사항, API 요약, 아키텍처 문서
```

## 실행 방법

1. 환경변수 파일 생성

```bash
cp .env.example .env
```

2. 전체 서비스 실행

```bash
docker compose up --build
```

3. 접속 주소

- 프론트엔드: [http://localhost:3000](http://localhost:3000)
- 백엔드 Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- 헬스체크: [http://localhost:8000/health](http://localhost:8000/health)

## 기본 관리자 계정

- 이메일: `admin@example.com`
- 비밀번호: `admin1234`

앱 시작 시 관리자 계정과 기본 카테고리 7종이 자동으로 시드됩니다.

## 주요 환경변수

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL 설정
- `SECRET_KEY`: JWT 서명 키
- `BACKEND_CORS_ORIGINS`: 프론트엔드 출처 허용 목록. Chrome/Safari를 함께 테스트할 때는 `http://localhost:3000,http://127.0.0.1:3000`처럼 둘 다 넣는 것을 권장합니다.
- `NEXT_PUBLIC_API_BASE_URL`: 브라우저에서 호출할 백엔드 주소
- `NEXT_INTERNAL_API_BASE_URL`: Docker 내부에서 프론트엔드 서버가 사용할 백엔드 주소
- `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NICKNAME`: 초기 관리자 계정

## 검증 포인트

- `docker compose up --build`로 전체 컨테이너 기동
- `http://localhost:8000/docs`에서 Swagger 확인
- 회원가입 / 로그인 / 상품 등록 / 상품 목록 / 상품 상세 동작 확인
- 인증이 필요한 API에 대해 쿠키 없을 때 `401` 응답 확인
- 관리자 계정으로 `/api/v1/admin/*` 접근 가능
- 채팅 연동 송금 및 관리자 지갑/송금 조회 가능

## 구현상 단순화한 부분

- 이미지 저장은 문서의 Object Storage 대신 로컬 업로드 디렉터리(`backend/uploads`)를 사용했습니다.
- 실시간 WebSocket 채팅 대신 Polling 기반 메시지 조회 구조로 구현했습니다.
- 실제 외부 결제는 제외하고 내부 지갑/송금 방식으로 MVP를 구성했습니다.

## 빠른 수동 테스트 예시

1. 일반 사용자 회원가입
2. 로그인
3. 상품 이미지 업로드 후 상품 등록
4. 홈에서 상품 목록/상세 확인
5. 다른 계정으로 거래 요청 또는 채팅방 생성
6. 채팅 화면 또는 `/wallet`에서 상대방에게 송금
7. 관리자 계정 로그인 후 관리자 페이지와 `/docs`에서 관리 API 확인
