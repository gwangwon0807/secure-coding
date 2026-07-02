| 구분            | 내용                                                               |
| ------------- | ---------------------------------------------------------------- |
| Router        | Image Router                                                     |
| Prefix        | `/api/v1/images`                                                 |
| Method 수      | 2개                                                               |
| 담당 기능         | 상품 이미지 업로드, 이미지 삭제                                               |
| 인증 방식         | JWT + HttpOnly Cookie                                            |
| 관련 테이블        | `item_images`, `users`                                           |
| 저장소           | Object Storage                                                   |
| 주요 Dependency | `get_current_user`, `require_active_user`, `require_image_owner` |

| 번호 | Method | Endpoint      | 기능         | 권한    | 설명                          |
| -- | ------ | ------------- | ---------- | ----- | --------------------------- |
| 1  | POST   | `/items`      | 상품 이미지 업로드 | User  | 상품 등록 전 또는 수정 시 사용할 이미지 업로드 |
| 2  | DELETE | `/{image_id}` | 이미지 삭제     | Owner | 본인이 업로드한 이미지 삭제             |

---

| API          | POST `/api/v1/images/items`                     |
| ------------ | ----------------------------------------------- |
| 기능           | 상품 이미지 업로드                                      |
| 권한           | User                                            |
| Content-Type | `multipart/form-data`                           |
| 설명           | 사용자가 상품 등록 또는 수정에 사용할 이미지를 업로드한다.               |
| 성공 Status    | `201 Created`                                   |
| 실패 Status    | `400`, `401`, `403`, `413`, `415`, `422`, `500` |

| Form Data | Type   | Required | Validation    | 설명             |
| --------- | ------ | -------- | ------------- | -------------- |
| files     | File[] | Yes      | 최소 1개, 최대 10개 | 업로드할 상품 이미지 목록 |

| 처리 규칙        | 설명                                          |
| ------------ | ------------------------------------------- |
| 로그인 필수       | 비회원은 이미지 업로드 불가                             |
| 정지 회원 제한     | `SUSPENDED` 상태 사용자는 이미지 업로드 불가              |
| 파일 개수 제한     | 한 번에 최대 10개까지만 업로드                          |
| 파일 크기 제한     | 파일당 최대 5MB 권장                               |
| 확장자 제한       | `jpg`, `jpeg`, `png`, `webp`만 허용            |
| MIME Type 검증 | `image/jpeg`, `image/png`, `image/webp`만 허용 |
| 저장 방식        | 파일은 Object Storage에 저장                      |
| DB 저장        | DB에는 이미지 URL, 저장 key, 업로더 ID만 저장            |
| 상품 연결        | 상품 등록 시 `image_ids`로 상품과 연결                 |
| 기본 상태        | 업로드 직후에는 `TEMP` 상태로 저장 가능                   |

| Response Data       | Type     | 설명                   |
| ------------------- | -------- | -------------------- |
| images              | array    | 업로드된 이미지 목록          |
| images[].id         | integer  | 이미지 ID               |
| images[].image_url  | string   | 이미지 접근 URL           |
| images[].sort_order | integer  | 이미지 순서               |
| images[].status     | string   | `TEMP` 또는 `ATTACHED` |
| images[].created_at | datetime | 업로드 시간               |

| Error Code                | HTTP Status | 설명                |
| ------------------------- | ----------- | ----------------- |
| `UNAUTHORIZED`            | 401         | 로그인 필요            |
| `USER_NOT_ACTIVE`         | 403         | 정지 또는 탈퇴 사용자      |
| `IMAGE_REQUIRED`          | 422         | 이미지 파일이 없음        |
| `TOO_MANY_IMAGES`         | 422         | 이미지 개수 초과         |
| `IMAGE_FILE_TOO_LARGE`    | 413         | 이미지 용량 초과         |
| `INVALID_IMAGE_EXTENSION` | 415         | 허용되지 않는 확장자       |
| `INVALID_IMAGE_MIME_TYPE` | 415         | 허용되지 않는 MIME Type |
| `IMAGE_UPLOAD_FAILED`     | 500         | 이미지 저장소 업로드 실패    |

---

| API       | DELETE `/api/v1/images/{image_id}` |
| --------- | ---------------------------------- |
| 기능        | 이미지 삭제                             |
| 권한        | Owner                              |
| 설명        | 사용자가 본인이 업로드한 이미지를 삭제한다.           |
| 성공 Status | `200 OK`                           |
| 실패 Status | `401`, `403`, `404`, `409`, `500`  |

| Path Parameter | Type    | Required | 설명         |
| -------------- | ------- | -------- | ---------- |
| image_id       | integer | Yes      | 삭제할 이미지 ID |

| 처리 규칙             | 설명                                     |
| ----------------- | -------------------------------------- |
| 로그인 필수            | 비회원은 이미지 삭제 불가                         |
| 소유자 확인            | `image.uploader_id == current_user.id` |
| TEMP 이미지 삭제 가능    | 아직 상품에 연결되지 않은 이미지는 삭제 가능              |
| ATTACHED 이미지 제한   | 상품에 연결된 이미지는 상품 소유자만 삭제 가능             |
| 최소 이미지 개수 확인      | 상품에 이미지가 1개뿐이면 삭제 제한 가능                |
| Object Storage 삭제 | 저장소에서 실제 파일 삭제                         |
| DB 처리             | DB에서는 삭제 처리 또는 `deleted_at` 기록         |
| 실패 대응             | Storage 삭제 실패 시 DB 삭제도 함께 중단           |

| Response Data | Type     | 설명         |
| ------------- | -------- | ---------- |
| id            | integer  | 삭제된 이미지 ID |
| deleted_at    | datetime | 삭제 처리 시간   |

| Error Code                      | HTTP Status | 설명                       |
| ------------------------------- | ----------- | ------------------------ |
| `UNAUTHORIZED`                  | 401         | 로그인 필요                   |
| `FORBIDDEN`                     | 403         | 이미지 소유자가 아님              |
| `IMAGE_NOT_FOUND`               | 404         | 이미지가 존재하지 않음             |
| `IMAGE_ALREADY_DELETED`         | 409         | 이미 삭제된 이미지               |
| `CANNOT_DELETE_LAST_IMAGE`      | 409         | 상품의 마지막 이미지는 삭제 불가       |
| `IMAGE_ATTACHED_TO_LOCKED_ITEM` | 409         | 판매완료 또는 숨김 상품의 이미지 삭제 제한 |
| `IMAGE_DELETE_FAILED`           | 500         | 이미지 저장소 삭제 실패            |

---

| Image Status Enum | 설명                         |
| ----------------- | -------------------------- |
| `TEMP`            | 업로드되었지만 아직 상품에 연결되지 않은 이미지 |
| `ATTACHED`        | 상품에 연결된 이미지                |
| `DELETED`         | 삭제 처리된 이미지                 |

| Image 관련 Validation | 기준                                      |
| ------------------- | --------------------------------------- |
| 파일 개수               | 최소 1개, 최대 10개                           |
| 파일 크기               | 파일당 최대 5MB                              |
| 허용 확장자              | `jpg`, `jpeg`, `png`, `webp`            |
| 허용 MIME Type        | `image/jpeg`, `image/png`, `image/webp` |
| 이미지 URL             | Object Storage URL                      |
| sort_order          | 1 이상 정수                                 |
| uploader_id         | 현재 로그인 사용자 ID                           |

| Image Router 설계 근거  | 내용                                 |
| ------------------- | ---------------------------------- |
| 이미지는 DB에 직접 저장하지 않음 | DB 용량 증가와 조회 성능 저하 방지              |
| DB에는 URL과 key만 저장   | 파일 관리와 데이터 관리 분리                   |
| 상품 등록 전 이미지 업로드 허용  | 프론트엔드에서 이미지 미리보기와 등록 흐름 구현이 쉬움     |
| `TEMP` 상태 사용        | 업로드 후 상품 등록 전 상태를 구분 가능            |
| Object Storage 사용   | 이미지 트래픽 증가 시 API 서버 부하 감소          |
| MIME Type 검증 필요     | 확장자 위장 파일 업로드 방지                   |
| 마지막 이미지 삭제 제한       | 상품은 최소 1개 이상의 이미지를 가져야 한다는 요구사항 유지 |
