| 구분            | 내용                                                  |
| ------------- | --------------------------------------------------- |
| Router        | Category Router                                     |
| Prefix        | `/api/v1/categories`                                |
| Method 수      | 1개                                                  |
| 담당 기능         | 카테고리 목록 조회                                          |
| 인증 방식         | 없음                                                  |
| 관련 테이블        | `categories`                                        |
| 주요 Dependency | 없음                                                  |
| 비고            | 카테고리 생성/수정/삭제는 MVP에서는 관리자 기능으로 분리하거나 초기 DB Seed로 처리 |

| 번호 | Method | Endpoint | 기능         | 권한     | 설명                       |
| -- | ------ | -------- | ---------- | ------ | ------------------------ |
| 1  | GET    | `/`      | 카테고리 목록 조회 | Public | 상품 등록/검색에 사용할 카테고리 목록 조회 |

---

| API       | GET `/api/v1/categories`                   |
| --------- | ------------------------------------------ |
| 기능        | 카테고리 목록 조회                                 |
| 권한        | Public                                     |
| 설명        | 상품 등록, 상품 검색, 상품 목록 필터에 사용할 카테고리 목록을 조회한다. |
| 성공 Status | `200 OK`                                   |
| 실패 Status | `500`                                      |

| Request Body | Type | Required | 설명                        |
| ------------ | ---- | -------- | ------------------------- |
| 없음           | -    | -        | 조회 API이므로 Request Body 없음 |

| Query Parameter | Type    | Required | Default | 설명                  |
| --------------- | ------- | -------- | ------- | ------------------- |
| is_active       | boolean | No       | `true`  | 사용 중인 카테고리만 조회할지 여부 |

| Response Data           | Type     | 설명       |
| ----------------------- | -------- | -------- |
| categories              | array    | 카테고리 목록  |
| categories[].id         | integer  | 카테고리 ID  |
| categories[].name       | string   | 카테고리명    |
| categories[].sort_order | integer  | 화면 표시 순서 |
| categories[].is_active  | boolean  | 사용 여부    |
| categories[].created_at | datetime | 생성일      |

| Response 예시 구조  | Type    |
| --------------- | ------- |
| success         | boolean |
| data.categories | array   |
| message         | string  |

| Error Code              | HTTP Status | 설명            |
| ----------------------- | ----------- | ------------- |
| `CATEGORY_FETCH_FAILED` | 500         | 카테고리 목록 조회 실패 |

---

| Category 테이블 컬럼 | Type     | 설명      |
| --------------- | -------- | ------- |
| id              | integer  | 카테고리 ID |
| name            | string   | 카테고리명   |
| sort_order      | integer  | 정렬 순서   |
| is_active       | boolean  | 사용 여부   |
| created_at      | datetime | 생성일     |
| updated_at      | datetime | 수정일     |

| 기본 카테고리 예시 | 설명              |
| ---------- | --------------- |
| 전자기기       | 휴대폰, 노트북, 태블릿 등 |
| 의류         | 옷, 신발, 패션잡화 등   |
| 가구         | 책상, 의자, 침대 등    |
| 생활용품       | 주방용품, 생활잡화 등    |
| 도서         | 책, 참고서, 만화책 등   |
| 스포츠        | 운동용품, 캠핑용품 등    |
| 기타         | 분류가 애매한 상품      |

| Category 관련 Validation | 기준       |
| ---------------------- | -------- |
| id                     | 1 이상의 정수 |
| name                   | 1~50자    |
| sort_order             | 1 이상의 정수 |
| is_active              | boolean  |

| Category Router 설계 근거 | 내용                                |
| --------------------- | --------------------------------- |
| Public API로 제공        | 비회원도 상품 검색과 상품 목록 필터를 사용할 수 있어야 함 |
| Method는 조회 1개만 유지     | MVP에서는 카테고리 변경 빈도가 낮음             |
| 생성/수정/삭제는 Admin으로 분리  | 일반 사용자에게 카테고리 관리 권한을 주면 안 됨       |
| DB Seed 권장            | 초기 개발에서는 기본 카테고리를 미리 넣어두는 방식이 빠름  |
| `is_active` 사용        | 카테고리를 삭제하지 않고 비활성화할 수 있음          |
| `sort_order` 사용       | 프론트엔드에서 원하는 순서대로 표시 가능            |
