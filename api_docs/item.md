| 구분            | 내용                                                              |
| ------------- | --------------------------------------------------------------- |
| Router        | Item Router                                                     |
| Prefix        | `/api/v1/items`                                                 |
| Method 수      | 6개                                                              |
| 담당 기능         | 상품 목록 조회, 상품 상세 조회, 상품 등록, 상품 수정, 상품 삭제, 상품 상태 변경               |
| 인증 방식         | JWT + HttpOnly Cookie                                           |
| 관련 테이블        | `items`, `item_images`, `categories`, `users`                   |
| 주요 Dependency | `get_current_user`, `require_active_user`, `require_item_owner` |

| 번호 | Method | Endpoint            | 기능       | 권한     | 설명                        |
| -- | ------ | ------------------- | -------- | ------ | ------------------------- |
| 1  | GET    | `/`                 | 상품 목록 조회 | Public | 상품 목록, 검색, 필터, 정렬, 페이지네이션 |
| 2  | GET    | `/{item_id}`        | 상품 상세 조회 | Public | 특정 상품의 상세 정보 조회           |
| 3  | POST   | `/`                 | 상품 등록    | User   | 로그인한 사용자가 상품 등록           |
| 4  | PATCH  | `/{item_id}`        | 상품 수정    | Owner  | 판매자가 본인 상품 정보 수정          |
| 5  | DELETE | `/{item_id}`        | 상품 삭제    | Owner  | 판매자가 본인 상품 삭제 처리          |
| 6  | PATCH  | `/{item_id}/status` | 상품 상태 변경 | Owner  | 판매중, 예약중, 판매완료 상태 변경      |

---

| API       | GET `/api/v1/items`                                      |
| --------- | -------------------------------------------------------- |
| 기능        | 상품 목록 조회 / 검색                                            |
| 권한        | Public                                                   |
| 설명        | 등록된 상품 목록을 조회한다. 키워드, 카테고리, 가격, 지역, 상태, 정렬 조건을 사용할 수 있다. |
| 성공 Status | `200 OK`                                                 |
| 실패 Status | `400`, `422`                                             |

| Query Parameter | Type    | Required | Default   | 설명               |
| --------------- | ------- | -------- | --------- | ---------------- |
| keyword         | string  | No       | null      | 상품명 또는 상품 설명 검색어 |
| category_id     | integer | No       | null      | 카테고리 ID          |
| min_price       | integer | No       | null      | 최소 가격            |
| max_price       | integer | No       | null      | 최대 가격            |
| location        | string  | No       | null      | 거래 지역            |
| status          | string  | No       | `ON_SALE` | 상품 상태            |
| sort            | string  | No       | `latest`  | 정렬 기준            |
| page            | integer | No       | 1         | 페이지 번호           |
| size            | integer | No       | 20        | 페이지당 상품 수        |

| Sort 값       | 설명     |
| ------------ | ------ |
| `latest`     | 최신순    |
| `price_asc`  | 낮은 가격순 |
| `price_desc` | 높은 가격순 |

| Response Data              | Type        | 설명         |
| -------------------------- | ----------- | ---------- |
| items                      | array       | 상품 목록      |
| items[].id                 | integer     | 상품 ID      |
| items[].title              | string      | 상품명        |
| items[].price              | integer     | 상품 가격      |
| items[].location           | string      | 거래 지역      |
| items[].status             | string      | 상품 상태      |
| items[].thumbnail_url      | string/null | 대표 이미지 URL |
| items[].seller.id          | integer     | 판매자 ID     |
| items[].seller.nickname    | string      | 판매자 닉네임    |
| items[].seller.trust_score | integer     | 판매자 신뢰도    |
| items[].created_at         | datetime    | 상품 등록일     |
| pagination.page            | integer     | 현재 페이지     |
| pagination.size            | integer     | 페이지 크기     |
| pagination.total_count     | integer     | 전체 상품 수    |
| pagination.total_pages     | integer     | 전체 페이지 수   |

| Error Code             | HTTP Status | 설명                  |
| ---------------------- | ----------- | ------------------- |
| `INVALID_PRICE_RANGE`  | 400         | 최소 가격이 최대 가격보다 큰 경우 |
| `INVALID_SORT_VALUE`   | 422         | 지원하지 않는 정렬 값        |
| `INVALID_STATUS_VALUE` | 422         | 지원하지 않는 상품 상태       |
| `INVALID_PAGE_VALUE`   | 422         | 페이지 값이 올바르지 않음      |

---

| API       | GET `/api/v1/items/{item_id}`    |
| --------- | -------------------------------- |
| 기능        | 상품 상세 조회                         |
| 권한        | Public                           |
| 설명        | 특정 상품의 상세 정보, 이미지, 판매자 정보를 조회한다. |
| 성공 Status | `200 OK`                         |
| 실패 Status | `404`                            |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| item_id        | integer | Yes      | 조회할 상품 ID |

| Response Data            | Type        | 설명          |
| ------------------------ | ----------- | ----------- |
| id                       | integer     | 상품 ID       |
| title                    | string      | 상품명         |
| description              | string      | 상품 설명       |
| price                    | integer     | 상품 가격       |
| category.id              | integer     | 카테고리 ID     |
| category.name            | string      | 카테고리명       |
| location                 | string      | 거래 지역       |
| status                   | string      | 상품 상태       |
| images                   | array       | 상품 이미지 목록   |
| images[].id              | integer     | 이미지 ID      |
| images[].image_url       | string      | 이미지 URL     |
| images[].sort_order      | integer     | 이미지 순서      |
| seller.id                | integer     | 판매자 ID      |
| seller.nickname          | string      | 판매자 닉네임     |
| seller.profile_image_url | string/null | 판매자 프로필 이미지 |
| seller.trust_score       | integer     | 판매자 신뢰도     |
| view_count               | integer     | 조회수         |
| created_at               | datetime    | 등록일         |
| updated_at               | datetime    | 수정일         |

| Error Code       | HTTP Status | 설명          |
| ---------------- | ----------- | ----------- |
| `ITEM_NOT_FOUND` | 404         | 상품이 존재하지 않음 |
| `ITEM_DELETED`   | 404         | 삭제된 상품      |
| `ITEM_HIDDEN`    | 404         | 숨김 처리된 상품   |

---

| API       | POST `/api/v1/items`              |
| --------- | --------------------------------- |
| 기능        | 상품 등록                             |
| 권한        | User                              |
| 설명        | 로그인한 사용자가 판매할 상품을 등록한다.           |
| 성공 Status | `201 Created`                     |
| 실패 Status | `400`, `401`, `403`, `404`, `422` |

| Request Body | Type      | Required | Validation    | 설명             |
| ------------ | --------- | -------- | ------------- | -------------- |
| title        | string    | Yes      | 2~100자        | 상품명            |
| description  | string    | Yes      | 1~3000자       | 상품 설명          |
| price        | integer   | Yes      | 0 이상          | 상품 가격          |
| category_id  | integer   | Yes      | 존재하는 카테고리     | 카테고리 ID        |
| location     | string    | Yes      | 1~100자        | 거래 지역          |
| image_ids    | integer[] | Yes      | 최소 1개, 최대 10개 | 업로드된 이미지 ID 목록 |

| 처리 규칙     | 설명                          |
| --------- | --------------------------- |
| 로그인 필수    | 비회원은 상품 등록 불가               |
| 정지 회원 제한  | `SUSPENDED` 상태 회원은 상품 등록 불가 |
| 카테고리 검증   | 존재하는 카테고리만 등록 가능            |
| 이미지 검증    | 현재 사용자가 업로드한 이미지인지 확인       |
| 기본 상태     | 상품 등록 시 `ON_SALE` 상태로 생성    |
| 가격 검증     | 음수 가격 불가                    |
| 이미지 개수 제한 | MVP 기준 최대 10개               |

| Response Data | Type     | 설명            |
| ------------- | -------- | ------------- |
| id            | integer  | 생성된 상품 ID     |
| seller_id     | integer  | 판매자 ID        |
| title         | string   | 상품명           |
| price         | integer  | 가격            |
| status        | string   | 기본값 `ON_SALE` |
| created_at    | datetime | 등록일           |

| Error Code                   | HTTP Status | 설명               |
| ---------------------------- | ----------- | ---------------- |
| `UNAUTHORIZED`               | 401         | 로그인 필요           |
| `USER_NOT_ACTIVE`            | 403         | 정지 또는 탈퇴 사용자     |
| `CATEGORY_NOT_FOUND`         | 404         | 카테고리 없음          |
| `IMAGE_NOT_FOUND`            | 404         | 이미지 없음           |
| `IMAGE_OWNER_MISMATCH`       | 403         | 본인이 업로드한 이미지가 아님 |
| `INVALID_TITLE_FORMAT`       | 422         | 상품명 형식 오류        |
| `INVALID_DESCRIPTION_FORMAT` | 422         | 상품 설명 형식 오류      |
| `INVALID_PRICE`              | 422         | 가격 값 오류          |
| `IMAGE_REQUIRED`             | 422         | 이미지가 없음          |
| `TOO_MANY_IMAGES`            | 422         | 이미지 개수 초과        |

---

| API       | PATCH `/api/v1/items/{item_id}`          |
| --------- | ---------------------------------------- |
| 기능        | 상품 수정                                    |
| 권한        | Owner                                    |
| 설명        | 판매자가 본인이 등록한 상품 정보를 수정한다.                |
| 성공 Status | `200 OK`                                 |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422` |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| item_id        | integer | Yes      | 수정할 상품 ID |

| Request Body | Type      | Required | Validation    | 설명        |
| ------------ | --------- | -------- | ------------- | --------- |
| title        | string    | No       | 2~100자        | 상품명       |
| description  | string    | No       | 1~3000자       | 상품 설명     |
| price        | integer   | No       | 0 이상          | 상품 가격     |
| category_id  | integer   | No       | 존재하는 카테고리     | 카테고리 ID   |
| location     | string    | No       | 1~100자        | 거래 지역     |
| image_ids    | integer[] | No       | 최소 1개, 최대 10개 | 상품 이미지 목록 |

| 처리 규칙      | 설명                                  |
| ---------- | ----------------------------------- |
| 소유자 확인     | `item.seller_id == current_user.id` |
| 판매완료 상품 제한 | `SOLD` 상품은 수정 제한 가능                 |
| 숨김 상품 제한   | `HIDDEN` 상품은 관리자 조치 상태이므로 수정 제한 가능  |
| 이미지 교체     | 전달된 `image_ids` 기준으로 이미지 목록 갱신      |
| 부분 수정      | 전달된 필드만 수정                          |

| Response Data | Type     | 설명          |
| ------------- | -------- | ----------- |
| id            | integer  | 상품 ID       |
| title         | string   | 수정된 상품명     |
| description   | string   | 수정된 상품 설명   |
| price         | integer  | 수정된 가격      |
| category_id   | integer  | 수정된 카테고리 ID |
| location      | string   | 수정된 거래 지역   |
| updated_at    | datetime | 수정일         |

| Error Code                | HTTP Status | 설명            |
| ------------------------- | ----------- | ------------- |
| `UNAUTHORIZED`            | 401         | 로그인 필요        |
| `FORBIDDEN`               | 403         | 상품 소유자가 아님    |
| `ITEM_NOT_FOUND`          | 404         | 상품 없음         |
| `CATEGORY_NOT_FOUND`      | 404         | 카테고리 없음       |
| `CANNOT_EDIT_SOLD_ITEM`   | 409         | 판매완료 상품 수정 불가 |
| `CANNOT_EDIT_HIDDEN_ITEM` | 409         | 숨김 상품 수정 불가   |
| `INVALID_PRICE`           | 422         | 가격 값 오류       |
| `TOO_MANY_IMAGES`         | 422         | 이미지 개수 초과     |

---

| API       | DELETE `/api/v1/items/{item_id}`                                            |
| --------- | --------------------------------------------------------------------------- |
| 기능        | 상품 삭제                                                                       |
| 권한        | Owner                                                                       |
| 설명        | 판매자가 본인이 등록한 상품을 삭제한다. 실제 삭제가 아니라 `deleted_at`을 기록하는 Soft Delete 방식으로 처리한다. |
| 성공 Status | `200 OK`                                                                    |
| 실패 Status | `401`, `403`, `404`, `409`                                                  |

| Path Parameter | Type    | Required | 설명        |
| -------------- | ------- | -------- | --------- |
| item_id        | integer | Yes      | 삭제할 상품 ID |

| 처리 규칙       | 설명                              |
| ----------- | ------------------------------- |
| 소유자 확인      | 판매자 본인만 삭제 가능                   |
| Soft Delete | DB에서 즉시 삭제하지 않고 `deleted_at` 기록 |
| 목록 제외       | 삭제된 상품은 일반 목록 조회에서 제외           |
| 상세 제외       | 삭제된 상품은 일반 사용자에게 조회되지 않음        |
| 거래 이력 보존    | 신고, 거래, 관리자 확인을 위해 데이터 보존       |
| 진행 중 거래 확인  | 진행 중 거래가 있으면 삭제 제한 가능           |

| Response Data | Type     | 설명           |
| ------------- | -------- | ------------ |
| id            | integer  | 삭제 처리된 상품 ID |
| deleted_at    | datetime | 삭제 처리 시간     |

| Error Code                  | HTTP Status | 설명                |
| --------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요            |
| `FORBIDDEN`                 | 403         | 상품 소유자가 아님        |
| `ITEM_NOT_FOUND`            | 404         | 상품 없음             |
| `ITEM_ALREADY_DELETED`      | 409         | 이미 삭제된 상품         |
| `ACTIVE_TRANSACTION_EXISTS` | 409         | 진행 중 거래가 있어 삭제 불가 |

---

| API       | PATCH `/api/v1/items/{item_id}/status`   |
| --------- | ---------------------------------------- |
| 기능        | 상품 상태 변경                                 |
| 권한        | Owner                                    |
| 설명        | 판매자가 상품 상태를 판매중, 예약중, 판매완료로 변경한다.        |
| 성공 Status | `200 OK`                                 |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422` |

| Path Parameter | Type    | Required | 설명            |
| -------------- | ------- | -------- | ------------- |
| item_id        | integer | Yes      | 상태를 변경할 상품 ID |

| Request Body | Type   | Required | Validation | 설명        |
| ------------ | ------ | -------- | ---------- | --------- |
| status       | string | Yes      | 허용된 상태값    | 변경할 상품 상태 |

| 허용 Status  | 설명   | 변경 가능 주체 |
| ---------- | ---- | -------- |
| `ON_SALE`  | 판매중  | 판매자      |
| `RESERVED` | 예약중  | 판매자      |
| `SOLD`     | 판매완료 | 판매자      |
| `HIDDEN`   | 숨김   | 관리자 전용   |

| 처리 규칙          | 설명                              |
| -------------- | ------------------------------- |
| 소유자 확인         | 판매자 본인만 상태 변경 가능                |
| `HIDDEN` 변경 제한 | 일반 판매자는 `HIDDEN`으로 변경 불가        |
| 삭제 상품 제한       | 삭제된 상품은 상태 변경 불가                |
| 거래 상태 연동       | 거래 수락/완료 API에서도 상품 상태가 변경될 수 있음 |
| 상태 변경 로그       | 필요 시 상품 상태 변경 이력 저장             |

| Response Data   | Type     | 설명     |
| --------------- | -------- | ------ |
| id              | integer  | 상품 ID  |
| previous_status | string   | 이전 상태  |
| status          | string   | 변경된 상태 |
| updated_at      | datetime | 수정일    |

| Error Code                  | HTTP Status | 설명                  |
| --------------------------- | ----------- | ------------------- |
| `UNAUTHORIZED`              | 401         | 로그인 필요              |
| `FORBIDDEN`                 | 403         | 상품 소유자가 아님          |
| `ITEM_NOT_FOUND`            | 404         | 상품 없음               |
| `ITEM_DELETED`              | 409         | 삭제된 상품              |
| `INVALID_ITEM_STATUS`       | 422         | 허용되지 않는 상품 상태       |
| `CANNOT_SET_HIDDEN_STATUS`  | 403         | 일반 사용자는 숨김 상태 변경 불가 |
| `INVALID_STATUS_TRANSITION` | 409         | 허용되지 않는 상태 변경       |

---

| Item Status Enum | 설명   |
| ---------------- | ---- |
| `ON_SALE`        | 판매중  |
| `RESERVED`       | 예약중  |
| `SOLD`           | 판매완료 |
| `HIDDEN`         | 숨김   |

| 권장 상태 전이               | 가능 여부   | 설명                   |
| ---------------------- | ------- | -------------------- |
| `ON_SALE` → `RESERVED` | 가능      | 거래 예약                |
| `RESERVED` → `ON_SALE` | 가능      | 예약 취소                |
| `RESERVED` → `SOLD`    | 가능      | 거래 완료                |
| `ON_SALE` → `SOLD`     | 가능      | 직접 판매완료 처리           |
| `SOLD` → `ON_SALE`     | 제한      | 실수 복구용으로 허용 여부 정책 필요 |
| `ANY` → `HIDDEN`       | 관리자만 가능 | 신고/운영 조치             |
| `HIDDEN` → `ON_SALE`   | 관리자만 가능 | 숨김 해제                |

| 공통 Validation | 기준                                      |
| ------------- | --------------------------------------- |
| title         | 2~100자                                  |
| description   | 1~3000자                                 |
| price         | 0 이상                                    |
| category_id   | 존재하는 카테고리 ID                            |
| location      | 1~100자                                  |
| image_ids     | 최소 1개, 최대 10개                           |
| page          | 1 이상                                    |
| size          | 1~100                                   |
| sort          | `latest`, `price_asc`, `price_desc`     |
| status        | `ON_SALE`, `RESERVED`, `SOLD`, `HIDDEN` |

| Item Router 설계 근거   | 내용                               |
| ------------------- | -------------------------------- |
| 상품 삭제는 Soft Delete  | 신고, 거래, 관리자 확인 이력 보존 필요          |
| 상품 목록은 Public       | 비회원도 상품 탐색 가능해야 함                |
| 상품 등록은 User         | 거래 기능은 로그인 사용자에게만 허용             |
| 상품 수정/삭제는 Owner     | 다른 사용자의 상품 조작 방지                 |
| 검색은 Item Router에 포함 | MVP에서는 별도 Search Router 분리보다 단순함 |
| `HIDDEN`은 관리자 전용    | 신고 처리와 운영 제재를 일반 상품 상태와 구분       |
