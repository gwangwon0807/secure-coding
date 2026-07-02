export function formatItemStatus(status: string): string {
  switch (status) {
    case "ON_SALE":
      return "판매중";
    case "RESERVED":
      return "예약중";
    case "SOLD":
      return "거래완료";
    case "HIDDEN":
      return "숨김";
    default:
      return status;
  }
}

export function formatTransactionStatus(status: string): string {
  switch (status) {
    case "REQUESTED":
      return "구매의사";
    case "ACCEPTED":
      return "완료대기";
    case "REJECTED":
      return "거절됨";
    case "CANCELED":
      return "취소됨";
    case "COMPLETED":
      return "거래완료";
    default:
      return status;
  }
}

export function getItemStatusClassName(status: string): string {
  switch (status) {
    case "RESERVED":
      return "status status-reserved";
    case "SOLD":
      return "status status-sold";
    case "HIDDEN":
      return "status status-hidden";
    default:
      return "status status-on-sale";
  }
}
