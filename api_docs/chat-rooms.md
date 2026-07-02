| 구분            | 내용                                                                    |
| ------------- | --------------------------------------------------------------------- |
| Router        | Chat Room Router                                                      |
| Prefix        | `/api/v1/chat-rooms`                                                  |
| Method 수      | 6개                                                                    |
| 담당 기능         | 채팅방 생성, 채팅방 목록 조회, 채팅방 상세 조회, 메시지 조회, 메시지 전송, 읽음 처리                   |
| 인증 방식         | JWT + HttpOnly Cookie                                                 |
| 관련 테이블        | `chat_rooms`, `messages`, `items`, `users`, `blocks`                  |
| 주요 Dependency | `get_current_user`, `require_active_user`, `require_chat_participant` |
| MVP 방식        | 실시간 WebSocket이 아닌 Polling 기반 메시지 조회                                   |

| 번호 | Method | Endpoint              | 기능          | 권한          | 설명                        |
| -- | ------ | --------------------- | ----------- | ----------- | ------------------------- |
| 1  | POST   | `/`                   | 채팅방 생성      | User        | 상품 상세 페이지에서 판매자와 채팅방 생성   |
| 2  | GET    | `/`                   | 내 채팅방 목록 조회 | User        | 내가 참여 중인 채팅방 목록 조회        |
| 3  | GET    | `/{room_id}`          | 채팅방 상세 조회   | Participant | 특정 채팅방의 상품, 상대방, 상태 정보 조회 |
| 4  | GET    | `/{room_id}/messages` | 메시지 목록 조회   | Participant | 특정 채팅방의 메시지 내역 조회         |
| 5  | POST   | `/{room_id}/messages` | 메시지 전송      | Participant | 채팅방에 텍스트 메시지 전송           |
| 6  | PATCH  | `/{room_id}/read`     | 메시지 읽음 처리   | Participant | 상대방이 보낸 메시지를 읽음 처리        |

| API       | POST `/api/v1/chat-rooms`                                            |
| --------- | -------------------------------------------------------------------- |
| 기능        | 채팅방 생성 또는 기존 채팅방 반환                                                  |
| 권한        | User                                                                 |
| 설명        | 구매자가 상품 상세 페이지에서 판매자에게 채팅을 시작한다. 이미 같은 상품에 대한 채팅방이 있으면 기존 채팅방을 반환한다. |
| 성공 Status | `200 OK`, `201 Created`                                              |
| 실패 Status | `400`, `401`, `403`, `404`, `409`                                    |

| Request Body | Type    | Required | Validation | 설명            |
| ------------ | ------- | -------- | ---------- | ------------- |
| item_id      | integer | Yes      | 존재하는 상품 ID | 채팅을 시작할 상품 ID |

| 처리 규칙     | 설명                                               |
| --------- | ------------------------------------------------ |
| 로그인 필수    | 비회원은 채팅방 생성 불가                                   |
| 정지 회원 제한  | `SUSPENDED` 상태 사용자는 채팅방 생성 불가                    |
| 상품 존재 확인  | 존재하지 않는 상품이면 생성 불가                               |
| 판매자 본인 제한 | 판매자는 자기 상품에 구매자처럼 채팅방 생성 불가                      |
| 삭제 상품 제한  | 삭제된 상품은 채팅방 생성 불가                                |
| 숨김 상품 제한  | `HIDDEN` 상품은 채팅방 생성 불가                           |
| 차단 관계 확인  | 구매자와 판매자 중 한 명이라도 차단한 관계면 생성 불가                  |
| 중복 방지     | `buyer_id + seller_id + item_id` 조합이 같으면 기존 방 반환 |

| Response Data | Type     | 설명            |
| ------------- | -------- | ------------- |
| id            | integer  | 채팅방 ID        |
| item_id       | integer  | 상품 ID         |
| buyer_id      | integer  | 구매자 ID        |
| seller_id     | integer  | 판매자 ID        |
| created_at    | datetime | 채팅방 생성일       |
| is_new        | boolean  | 새로 생성된 채팅방 여부 |

| Error Code             | HTTP Status | 설명              |
| ---------------------- | ----------- | --------------- |
| `UNAUTHORIZED`         | 401         | 로그인 필요          |
| `USER_NOT_ACTIVE`      | 403         | 정지 또는 탈퇴 사용자    |
| `ITEM_NOT_FOUND`       | 404         | 상품이 존재하지 않음     |
| `CANNOT_CHAT_OWN_ITEM` | 400         | 본인 상품에는 채팅 불가   |
| `ITEM_NOT_AVAILABLE`   | 409         | 삭제, 숨김, 판매완료 상품 |
| `USER_BLOCKED`         | 403         | 차단 관계로 채팅 불가    |

| API       | GET `/api/v1/chat-rooms`         |
| --------- | -------------------------------- |
| 기능        | 내 채팅방 목록 조회                      |
| 권한        | User                             |
| 설명        | 현재 로그인한 사용자가 참여 중인 채팅방 목록을 조회한다. |
| 성공 Status | `200 OK`                         |
| 실패 Status | `401`, `403`, `422`              |

| Query Parameter | Type    | Required | Default | 설명         |
| --------------- | ------- | -------- | ------- | ---------- |
| page            | integer | No       | 1       | 페이지 번호     |
| size            | integer | No       | 20      | 페이지당 채팅방 수 |

| 정렬 기준    | 설명                         |
| -------- | -------------------------- |
| 기본 정렬    | `last_message_at DESC`     |
| 메시지 없는 방 | `created_at DESC` 기준 보조 정렬 |

| Response Data                        | Type          | 설명          |
| ------------------------------------ | ------------- | ----------- |
| chat_rooms                           | array         | 채팅방 목록      |
| chat_rooms[].id                      | integer       | 채팅방 ID      |
| chat_rooms[].item.id                 | integer       | 상품 ID       |
| chat_rooms[].item.title              | string        | 상품명         |
| chat_rooms[].item.thumbnail_url      | string/null   | 상품 대표 이미지   |
| chat_rooms[].item.status             | string        | 상품 상태       |
| chat_rooms[].opponent.id             | integer       | 상대방 ID      |
| chat_rooms[].opponent.nickname       | string        | 상대방 닉네임     |
| chat_rooms[].last_message.content    | string/null   | 마지막 메시지 내용  |
| chat_rooms[].last_message.created_at | datetime/null | 마지막 메시지 시간  |
| chat_rooms[].unread_count            | integer       | 읽지 않은 메시지 수 |
| pagination.page                      | integer       | 현재 페이지      |
| pagination.size                      | integer       | 페이지 크기      |
| pagination.total_count               | integer       | 전체 채팅방 수    |
| pagination.total_pages               | integer       | 전체 페이지 수    |

| Error Code           | HTTP Status | 설명           |
| -------------------- | ----------- | ------------ |
| `UNAUTHORIZED`       | 401         | 로그인 필요       |
| `USER_NOT_ACTIVE`    | 403         | 정지 또는 탈퇴 사용자 |
| `INVALID_PAGE_VALUE` | 422         | 페이지 값 오류     |
| `INVALID_SIZE_VALUE` | 422         | 페이지 크기 오류    |

| API       | GET `/api/v1/chat-rooms/{room_id}`     |
| --------- | -------------------------------------- |
| 기능        | 채팅방 상세 조회                              |
| 권한        | Participant                            |
| 설명        | 특정 채팅방의 상품 정보, 구매자, 판매자, 상대방 정보를 조회한다. |
| 성공 Status | `200 OK`                               |
| 실패 Status | `401`, `403`, `404`                    |

| Path Parameter | Type    | Required | 설명         |
| -------------- | ------- | -------- | ---------- |
| room_id        | integer | Yes      | 조회할 채팅방 ID |

| Response Data      | Type          | 설명                |
| ------------------ | ------------- | ----------------- |
| id                 | integer       | 채팅방 ID            |
| item.id            | integer       | 상품 ID             |
| item.title         | string        | 상품명               |
| item.price         | integer       | 상품 가격             |
| item.thumbnail_url | string/null   | 상품 대표 이미지         |
| item.status        | string        | 상품 상태             |
| buyer.id           | integer       | 구매자 ID            |
| buyer.nickname     | string        | 구매자 닉네임           |
| seller.id          | integer       | 판매자 ID            |
| seller.nickname    | string        | 판매자 닉네임           |
| opponent.id        | integer       | 현재 사용자 기준 상대방 ID  |
| opponent.nickname  | string        | 현재 사용자 기준 상대방 닉네임 |
| created_at         | datetime      | 채팅방 생성일           |
| last_message_at    | datetime/null | 마지막 메시지 시간        |

| Error Code            | HTTP Status | 설명           |
| --------------------- | ----------- | ------------ |
| `UNAUTHORIZED`        | 401         | 로그인 필요       |
| `CHAT_ROOM_NOT_FOUND` | 404         | 채팅방 없음       |
| `FORBIDDEN`           | 403         | 채팅방 참여자가 아님  |
| `USER_BLOCKED`        | 403         | 차단 관계로 접근 제한 |

| API       | GET `/api/v1/chat-rooms/{room_id}/messages`           |
| --------- | ----------------------------------------------------- |
| 기능        | 메시지 목록 조회                                             |
| 권한        | Participant                                           |
| 설명        | 특정 채팅방의 메시지 내역을 조회한다. MVP에서는 Polling 방식으로 주기적으로 호출한다. |
| 성공 Status | `200 OK`                                              |
| 실패 Status | `401`, `403`, `404`, `422`                            |

| Path Parameter | Type    | Required | 설명              |
| -------------- | ------- | -------- | --------------- |
| room_id        | integer | Yes      | 메시지를 조회할 채팅방 ID |

| Query Parameter | Type    | Required | Default | 설명               |
| --------------- | ------- | -------- | ------- | ---------------- |
| cursor          | integer | No       | null    | 마지막으로 조회한 메시지 ID |
| size            | integer | No       | 30      | 가져올 메시지 개수       |

| Cursor 기준 | 설명                             |
| --------- | ------------------------------ |
| cursor 없음 | 최신 메시지 기준으로 조회                 |
| cursor 있음 | 해당 메시지 이전 또는 이후 메시지 조회 정책 선택   |
| MVP 권장    | 최신 메시지부터 가져오고, 스크롤 시 이전 메시지 조회 |

| Response Data           | Type         | 설명                |
| ----------------------- | ------------ | ----------------- |
| messages                | array        | 메시지 목록            |
| messages[].id           | integer      | 메시지 ID            |
| messages[].chat_room_id | integer      | 채팅방 ID            |
| messages[].sender_id    | integer      | 보낸 사용자 ID         |
| messages[].content      | string       | 메시지 내용            |
| messages[].message_type | string       | 메시지 타입            |
| messages[].is_read      | boolean      | 읽음 여부             |
| messages[].created_at   | datetime     | 메시지 전송 시간         |
| next_cursor             | integer/null | 다음 조회에 사용할 cursor |
| has_next                | boolean      | 추가 메시지 존재 여부      |

| Error Code            | HTTP Status | 설명          |
| --------------------- | ----------- | ----------- |
| `UNAUTHORIZED`        | 401         | 로그인 필요      |
| `CHAT_ROOM_NOT_FOUND` | 404         | 채팅방 없음      |
| `FORBIDDEN`           | 403         | 채팅방 참여자가 아님 |
| `INVALID_CURSOR`      | 422         | cursor 값 오류 |
| `INVALID_SIZE_VALUE`  | 422         | size 값 오류   |

| API       | POST `/api/v1/chat-rooms/{room_id}/messages`                |
| --------- | ----------------------------------------------------------- |
| 기능        | 메시지 전송                                                      |
| 권한        | Participant                                                 |
| 설명        | 채팅방 참여자가 텍스트 메시지를 전송한다. MVP에서는 이미지 메시지는 제외하거나 2차 기능으로 분리한다. |
| 성공 Status | `201 Created`                                               |
| 실패 Status | `400`, `401`, `403`, `404`, `409`, `422`                    |

| Path Parameter | Type    | Required | 설명              |
| -------------- | ------- | -------- | --------------- |
| room_id        | integer | Yes      | 메시지를 전송할 채팅방 ID |

| Request Body | Type   | Required | Validation      | 설명     |
| ------------ | ------ | -------- | --------------- | ------ |
| content      | string | Yes      | 1~1000자         | 메시지 내용 |
| message_type | string | Yes      | MVP는 `TEXT`만 허용 | 메시지 타입 |

| 처리 규칙    | 설명                             |
| -------- | ------------------------------ |
| 로그인 필수   | 비회원은 메시지 전송 불가                 |
| 참여자 확인   | 구매자 또는 판매자만 전송 가능              |
| 정지 회원 제한 | 정지 회원은 메시지 전송 불가               |
| 차단 관계 확인 | 차단 관계가 있으면 전송 불가               |
| 빈 메시지 제한 | 공백만 있는 메시지 전송 불가               |
| 길이 제한    | 메시지는 최대 1000자                  |
| 채팅방 갱신   | 메시지 저장 후 `last_message_at` 갱신  |
| 읽음 기본값   | 보낸 직후 상대방 기준 `is_read = false` |

| Response Data | Type     | 설명        |
| ------------- | -------- | --------- |
| id            | integer  | 메시지 ID    |
| chat_room_id  | integer  | 채팅방 ID    |
| sender_id     | integer  | 보낸 사용자 ID |
| content       | string   | 메시지 내용    |
| message_type  | string   | `TEXT`    |
| is_read       | boolean  | 읽음 여부     |
| created_at    | datetime | 메시지 전송 시간 |

| Error Code             | HTTP Status | 설명               |
| ---------------------- | ----------- | ---------------- |
| `UNAUTHORIZED`         | 401         | 로그인 필요           |
| `USER_NOT_ACTIVE`      | 403         | 정지 또는 탈퇴 사용자     |
| `CHAT_ROOM_NOT_FOUND`  | 404         | 채팅방 없음           |
| `FORBIDDEN`            | 403         | 채팅방 참여자가 아님      |
| `USER_BLOCKED`         | 403         | 차단 관계로 메시지 전송 불가 |
| `EMPTY_MESSAGE`        | 422         | 빈 메시지            |
| `MESSAGE_TOO_LONG`     | 422         | 메시지 길이 초과        |
| `INVALID_MESSAGE_TYPE` | 422         | 허용되지 않는 메시지 타입   |
| `CHAT_ROOM_CLOSED`     | 409         | 채팅방이 종료된 경우      |

| API       | PATCH `/api/v1/chat-rooms/{room_id}/read` |
| --------- | ----------------------------------------- |
| 기능        | 메시지 읽음 처리                                 |
| 권한        | Participant                               |
| 설명        | 현재 사용자가 해당 채팅방에서 상대방이 보낸 메시지를 읽음 처리한다.    |
| 성공 Status | `200 OK`                                  |
| 실패 Status | `401`, `403`, `404`                       |

| Path Parameter | Type    | Required | 설명            |
| -------------- | ------- | -------- | ------------- |
| room_id        | integer | Yes      | 읽음 처리할 채팅방 ID |

| Request Body         | Type    | Required | Validation  | 설명                   |
| -------------------- | ------- | -------- | ----------- | -------------------- |
| last_read_message_id | integer | No       | 존재하는 메시지 ID | 특정 메시지까지 읽음 처리할 때 사용 |

| 처리 규칙           | 설명                                                      |
| --------------- | ------------------------------------------------------- |
| 참여자 확인          | 채팅방 구매자 또는 판매자만 가능                                      |
| 본인 메시지 제외       | 본인이 보낸 메시지는 읽음 처리 대상 아님                                 |
| 상대방 메시지만 처리     | 상대방이 보낸 메시지만 `is_read = true`                           |
| 전체 읽음 처리        | `last_read_message_id`가 없으면 현재 조회 가능한 상대방 메시지를 모두 읽음 처리 |
| unread_count 감소 | 채팅방 목록의 읽지 않은 메시지 수에 반영                                 |

| Response Data        | Type         | 설명                  |
| -------------------- | ------------ | ------------------- |
| room_id              | integer      | 채팅방 ID              |
| read_count           | integer      | 읽음 처리된 메시지 수        |
| last_read_message_id | integer/null | 마지막으로 읽음 처리된 메시지 ID |
| updated_at           | datetime     | 읽음 처리 시간            |

| Error Code            | HTTP Status | 설명          |
| --------------------- | ----------- | ----------- |
| `UNAUTHORIZED`        | 401         | 로그인 필요      |
| `CHAT_ROOM_NOT_FOUND` | 404         | 채팅방 없음      |
| `FORBIDDEN`           | 403         | 채팅방 참여자가 아님 |
| `MESSAGE_NOT_FOUND`   | 404         | 기준 메시지 없음   |

| Message Type Enum | 설명                    |
| ----------------- | --------------------- |
| `TEXT`            | 텍스트 메시지               |
| `IMAGE`           | 이미지 메시지, MVP에서는 제외 가능 |

| Chat Room 관련 상태 | 설명                            |
| --------------- | ----------------------------- |
| `ACTIVE`        | 정상 채팅방                        |
| `CLOSED`        | 거래 완료, 차단, 관리자 조치 등으로 제한된 채팅방 |
| `BLOCKED`       | 차단 관계로 메시지 전송 제한              |

| Chat 관련 Validation   | 기준            |
| -------------------- | ------------- |
| room_id              | 1 이상의 정수      |
| item_id              | 존재하는 상품 ID    |
| content              | 1~1000자       |
| message_type         | MVP 기준 `TEXT` |
| page                 | 1 이상          |
| size                 | 1~100         |
| cursor               | 1 이상의 정수      |
| last_read_message_id | 존재하는 메시지 ID   |

| Chat Router 설계 근거 | 내용                               |
| ----------------- | -------------------------------- |
| 채팅방 생성은 상품 기준     | 중고거래는 특정 상품을 중심으로 대화가 발생함        |
| 중복 채팅방 방지         | 같은 구매자, 판매자, 상품 조합의 채팅방 중복 생성 방지 |
| Participant 권한 필수 | 채팅 내용은 민감 정보이므로 참여자만 접근 가능       |
| MVP는 Polling 방식   | WebSocket보다 구현이 빠르고 안정적          |
| 메시지는 DB 저장        | 거래 분쟁, 신고 처리, 관리자 확인에 필요         |
| 차단 관계 확인          | 악성 사용자와의 추가 소통 방지                |
| 읽음 처리는 별도 API     | 채팅방 목록의 unread_count 계산에 필요      |
