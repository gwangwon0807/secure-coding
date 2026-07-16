# 번개중고

## 주요 기능

| 영역 | 기능 |
| --- | --- |
| 회원 | 회원가입, 로그인, 로그아웃, 프로필·소개글·비밀번호 변경, 회원 탈퇴 |
| 상품 | 다중 이미지 업로드, 등록·조회·수정·삭제, 판매중·예약중·거래완료 상태 |
| 검색 | 상품명·설명, 카테고리, 가격, 지역, 판매 상태 필터와 가격·최신순 정렬 |
| 채팅 | 상품 기반 1:1 채팅방, 메시지, 읽음 처리, 채팅방 삭제 |
| 거래 | 구매 요청, 수락·거절·취소, 구매자·판매자 양쪽 완료 확인 |
| 커뮤니티 | 게시글·댓글 CRUD, 다중 이미지, 게시글 검색 |
| 신고·차단 | 상품·사용자·글·댓글·채팅방·메시지 신고, 사용자 차단·해제 |
| 지갑 | 0원 지갑, 관리자 승인형 충전, 출금, 사용자 간 송금, 잔액 원장 |
| 관리자 | 회원·상품·신고·커뮤니티·채팅·거래·지갑·송금·충전 요청 조회와 제어 |

## 기술 스택

| 구분 | 기술 |
| --- | --- |
| Frontend | Next.js 15.5, React 19.1, TypeScript |
| Backend | FastAPI, SQLAlchemy 2, Pydantic |
| Database | PostgreSQL 16 |
| Authentication | HttpOnly JWT Cookie, Refresh Token Rotation, Server Session, CSRF Token |
| File | Docker Volume에 로컬 이미지 저장 |
| Runtime | Docker, Docker Compose |

## 시스템 구조

```text
브라우저
   │ http://localhost:3000
   ▼
Next.js Frontend
   │ /api/*, /uploads/* reverse proxy
   ▼
FastAPI Backend
   │ SQLAlchemy / psycopg
   ▼
PostgreSQL
```

브라우저는 Next.js와 같은 origin으로 API를 호출합니다. Next.js 서버가 Docker 내부 주소 `http://backend:8000`으로 API와 업로드 파일을 프록시합니다.

## 프로젝트 구조

```text
.
├── backend/
│   ├── app/api/v1/endpoints/   FastAPI 라우터
│   ├── app/models/             SQLAlchemy DB 모델
│   ├── app/schemas/            요청·응답 스키마
│   ├── app/services/           지갑 등 공통 도메인 로직
│   └── requirements.txt
├── frontend/
│   ├── app/                    Next.js App Router 페이지
│   ├── components/             공통 UI 컴포넌트
│   └── lib/                    API·인증 유틸리티
├── api_docs/                         라우터별 API 명세
├── db_docs/                          테이블별 DB 명세
├── security_tests/                   로컬 보안 재현·회귀 스크립트
├── docker-compose.yml
└── .env.example
```

## 빠른 시작

### 1. 준비물

| 항목 | 필수 여부 | 확인 명령 |
| --- | --- | --- |
| Docker Desktop | 필수 | `docker --version` |
| Docker Compose | 필수 | `docker compose version` |
| Python 3 | 보안 PoC 실행 시만 | `python3 --version` |

Docker Desktop을 실행한 상태에서 아래 명령을 실행합니다.

### 2. 환경변수 생성

```bash
cp .env.example .env
```

`.env.example`의 값은 로컬 실습용입니다. 필요하면 `.env`의 DB 비밀번호, `SECRET_KEY`, 관리자 계정을 변경합니다.

```bash
openssl rand -hex 32
```

위 명령으로 난수를 만든 후 `SECRET_KEY`에 넣을 수 있습니다.

### 3. 전체 서비스 실행

```bash
docker compose up --build
```

백그라운드로 실행하려면 다음을 사용합니다.

```bash
docker compose up -d --build
docker compose ps
```

### 4. 접속 주소

| 서비스 | URL | 용도 |
| --- | --- | --- |
| 프론트엔드 | [http://localhost:3000](http://localhost:3000) | 일반 사용자·관리자 웹 화면 |
| Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) | API 명세 및 수동 호출 |
| OpenAPI JSON | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | OpenAPI 스키마 |

## 초기 데이터

서버가 처음 시작될 때 `.env`의 `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NICKNAME`으로 관리자를 생성합니다. 이미 같은 이메일이 존재하면 다시 생성하지 않습니다.

기본 카테고리는 전자기기, 의류, 가구, 생활용품, 도서, 스포츠, 기타 7종입니다. 신규 회원의 지갑 잔액은 0원입니다.

## 사용 흐름

### 회원가입과 프로필 관리

1. `회원가입`에서 중복되지 않는 이메일과 닉네임, 비밀번호를 입력합니다.
2. 가입이 완료되면 로그인 화면으로 이동하며, 등록한 계정으로 로그인합니다.
3. 로그인 후 `마이`에서 내 프로필, 소개글, 거래·신고 정보를 확인합니다.
4. `프로필 수정`에서 닉네임과 소개글을 변경하고, 비밀번호는 별도 화면에서 변경합니다.
5. 로그아웃하면 인증 쿠키와 서버 세션이 폐기되고 공개 상품·커뮤니티만 이용할 수 있습니다.

### 상품 조회와 검색

1. 홈에서는 로그인 여부와 관계없이 판매중·예약중·거래완료 상품을 확인할 수 있습니다.
2. 검색어를 입력하면 상품명과 설명을 기준으로 상품을 찾습니다.
3. 카테고리, 최소·최대 가격, 지역, 판매 상태를 조합해 결과를 필터링합니다.
4. 최신순, 낮은 가격순, 높은 가격순으로 검색 결과를 정렬합니다.
5. 상품 카드를 선택하면 가격, 판매자, 설명, 상태와 여러 장의 사진을 상세 화면에서 확인합니다.

### 상품 등록과 관리

1. 로그인한 사용자는 `상품등록`에서 상품명, 가격, 카테고리, 지역, 설명과 여러 장의 사진을 등록합니다.
2. 로그인하지 않은 상태에서 상품등록을 누르면 로그인 화면으로 이동합니다.
3. `마이 > 내가 올린 상품`에서 등록한 상품 목록을 확인합니다.
4. 상품 상세에서 작성자 본인만 내용을 수정하거나 상품을 삭제할 수 있습니다.
5. 판매자는 상품 상태를 판매중 또는 예약중으로 변경하며, 거래 완료 후에는 거래완료 상태로 보존합니다.

### 채팅과 거래

1. 구매 희망자는 상품 상세에서 판매자와 1:1 채팅방을 생성합니다.
2. 채팅방에서 메시지를 주고받으며 상품 상태와 거래 조건을 협의합니다.
3. 구매자가 구매 요청을 보내면 판매자가 상품을 예약중으로 변경할 수 있습니다. 예약중이어도 다른 사용자의 문의는 허용됩니다.
4. 거래가 성사되면 구매자와 판매자가 각각 거래완료를 확인합니다.
5. 양쪽 확인이 모두 끝나면 거래와 상품이 거래완료로 변경되고 거래내역에 유지됩니다.

### 커뮤니티

1. 로그인한 사용자는 `커뮤니티`에서 전체 사용자가 볼 수 있는 게시글을 작성합니다.
2. 게시글에는 여러 장의 이미지를 첨부할 수 있으며 제목이나 내용으로 검색할 수 있습니다.
3. 다른 사용자는 게시글 상세에서 댓글을 작성해 공개적으로 소통합니다.
4. 작성자는 자신의 게시글과 댓글을 수정하거나 삭제할 수 있습니다.

### 신고와 차단

1. 상품, 사용자, 커뮤니티 글·댓글, 채팅방·메시지에서 `신고하기`를 선택합니다.
2. 신고 사유를 입력하면 신고가 접수되며 동일한 대상에 대한 중복 신고는 제한됩니다.
3. 상품은 미처리 신고가 3건 이상 누적되면 자동으로 숨김 처리됩니다.
4. 사용자는 신고가 1건 이상 접수되면 관리자 화면의 `관리대상`에 표시되며, 신고가 많은 순서로 우선 노출됩니다.
5. 관리자가 신고 내용과 활동 내역을 확인한 후 신고를 기각하거나 대상 숨김·삭제, 회원 정지 등의 조치를 결정합니다.
6. 사용자는 원하지 않는 상대를 직접 차단하거나 차단을 해제할 수 있습니다.

### 지갑 충전과 송금

1. `지갑` 화면에서 충전 금액을 입력해 충전 요청을 접수합니다.
2. 요청 직후에는 잔액이 변하지 않고 `PENDING`으로 표시됩니다.
3. 관리자가 `관리자 > 충전요청`에서 승인하면 잔액과 원장에 반영됩니다.
4. 거래 당사자는 채팅방에서 상대방을 선택하고 금액을 입력해 송금합니다.
5. `지갑`에서 현재 잔액, 충전 요청 상태, 최근 송금 내역과 잔액 원장을 확인합니다.
6. 잔액 변경과 송금 원장은 한 DB 트랜잭션으로 저장되며 잔액이 부족하면 송금되지 않습니다.

### 관리자

1. `.env`에 설정한 관리자 계정으로 로그인합니다.
2. 헤더의 `관리자`를 누릅니다.
3. 회원, 상품, 커뮤니티, 채팅, 신고, 거래, 지갑, 충전요청, 송금 탭에서 전체 데이터를 조회합니다.
4. 회원을 선택하면 프로필과 상품·게시글·댓글·채팅·신고 등 활동 카테고리를 확인하고 각 목록으로 이동합니다.
5. 상품, 게시글, 댓글, 채팅방과 신고를 선택하면 실제 내용과 관련 사용자를 상세 화면에서 확인합니다.
6. 회원 상태 변경, 상품·커뮤니티 숨김, 채팅방 삭제와 신고 승인·기각을 처리합니다.
7. 충전 요청을 승인·거절하고 송금 내역을 확인하며, 정정이 필요하면 사유를 남기고 지갑 잔액을 조정합니다.

## 인증과 요청 보호

| 항목 | 동작 |
| --- | --- |
| Access Token | JavaScript로 읽을 수 없는 HttpOnly Cookie에 저장 |
| Refresh Token | DB에 SHA-256 해시로만 저장하고 재발급 시 회전 |
| Server Session | 만료·로그아웃된 `auth_sessions`을 확인 |
| CSRF | GET 이외의 인증 요청에 `csrf_token` Cookie와 `X-CSRF-Token` 헤더 요구 |
| 지갑 동시성 | PostgreSQL `SELECT ... FOR UPDATE`로 지갑 잠금, DB 체크 제약으로 음수 잔액 차단 |

## 환경변수

| 변수 | 설명 | 로컬 기본값 |
| --- | --- | --- |
| `POSTGRES_DB` | DB명 | `secure_coding` |
| `POSTGRES_USER` | DB 사용자 | `postgres` |
| `POSTGRES_PASSWORD` | DB 비밀번호 | `postgres` |
| `POSTGRES_PORT` | 호스트 DB 포트 | `5432` |
| `BACKEND_PORT` | FastAPI 호스트 포트 | `8000` |
| `FRONTEND_PORT` | Next.js 호스트 포트 | `3000` |
| `SECRET_KEY` | JWT 서명 키 | 로컬 예제값 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 | `15` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh Token/세션 만료 | `10080` |
| `BACKEND_CORS_ORIGINS` | 허용 origin | localhost, 127.0.0.1 |
| `NEXT_INTERNAL_API_BASE_URL` | Next.js 서버의 Docker 내부 API 주소 | `http://backend:8000` |
| `COOKIE_SECURE` | HTTPS 전용 Cookie | 로컬은 `false` |
| `COOKIE_SAMESITE` | Cookie SameSite | `lax` |
| `ADMIN_EMAIL` | 초기 관리자 이메일 | `admin@example.com` |
| `ADMIN_PASSWORD` | 초기 관리자 비밀번호 | `admin1234` |

## 문서

| 문서 | 위치 |
| --- | --- |
| API 목차 | [api_docs/README.md](api_docs/README.md) |
| 인증 API | [api_docs/auth.md](api_docs/auth.md) |
| 상품 API | [api_docs/item.md](api_docs/item.md) |
| 지갑·송금 API | [api_docs/transfers.md](api_docs/transfers.md) |
| 관리자 API | [api_docs/admin.md](api_docs/admin.md) |
| DB 목차 | [db_docs/README.md](db_docs/README.md) |
| Swagger | [http://localhost:8000/docs](http://localhost:8000/docs) |

## 검증

### 기본 동작 확인

```bash
docker compose ps
curl http://localhost:8000/health
curl http://localhost:3000/api/v1/categories
docker compose logs --tail=100 backend frontend
```

정상 기동 시 `db` 상태는 `healthy`, `backend`와 `frontend`는 `Up`으로 표시됩니다.

## Docker 운영 명령

| 목적 | 명령 |
| --- | --- |
| 백그라운드 실행 | `docker compose up -d --build` |
| 상태 확인 | `docker compose ps` |
| 전체 로그 | `docker compose logs -f` |
| 백엔드 로그 | `docker compose logs -f backend` |
| 프론트엔드 재빌드 | `docker compose up -d --build frontend` |
| 백엔드 재빌드 | `docker compose up -d --build backend` |
| 서비스 종료 | `docker compose down` |
| DB·업로드 포함 초기화 | `docker compose down -v` |

`docker compose down -v`는 회원, 상품, 채팅, 지갑, 업로드 이미지를 삭제하므로 필요할 때만 사용합니다.

## 문제 해결

### `port is already allocated`

로컬에서 이미 사용 중인 포트를 `.env`에서 변경합니다. PostgreSQL만 충돌한다면 `POSTGRES_PORT=5433`으로 변경해도 Docker 내부 DB 주소는 그대로입니다.

### Chrome과 Safari로 두 사용자 동시 테스트

두 브라우저 모두 `http://localhost:3000`으로 접속하고 서로 다른 계정으로 로그인합니다. 브라우저별 Cookie 저장소가 분리되므로 판매자와 구매자 흐름을 동시에 확인할 수 있습니다.

### 변경한 `.env`가 반영되지 않는 경우

```bash
docker compose up -d --force-recreate backend frontend
```

DB 사용자·DB명을 이미 생성된 볼륨에서 변경한 경우에는 DB 볼륨 초기화가 필요할 수 있습니다.

## MVP 범위와 제한

| 항목 | 현재 구현 |
| --- | --- |
| 채팅 | WebSocket 대신 주기적 API 조회 |
| 이미지 | S3 등 Object Storage 대신 Docker Volume |
| 지갑 | 실제 은행·PG 연동 없는 내부 포인트 |
| 충전 | 실제 입금 자동 확인 대신 관리자 수동 승인 |
| 알림 | Push, 이메일, SMS 알림 미연동 |
| 배포 | 로컬 Docker Compose 실습 환경 기준 |
