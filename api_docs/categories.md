# Categories Router

| 항목 | 내용 |
| --- | --- |
| Prefix | `/api/v1/categories` |
| 인증 | Public |
| 설명 | 카테고리 목록 조회 |

## Endpoint

| Method | Endpoint | Auth | 설명 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| GET | `/` | Public | 카테고리 목록 조회 | - |

## 응답 핵심

| 필드 | 설명 |
| --- | --- |
| `id` | 카테고리 ID |
| `name` | 카테고리명 |
| `sort_order` | 표시 순서 |
| `is_active` | 사용 여부 |

## 비고

| 항목 | 내용 |
| --- | --- |
| 관리 방식 | 현재는 Seed 기반 기본 카테고리 사용 |
| 관리자 CRUD | 별도 구현 없음 |
