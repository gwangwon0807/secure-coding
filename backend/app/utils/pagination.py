from math import ceil


def build_pagination(page: int, size: int, total_count: int) -> dict:
    return {
        "page": page,
        "size": size,
        "total_count": total_count,
        "total_pages": ceil(total_count / size) if total_count else 0,
    }
