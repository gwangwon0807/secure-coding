import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class ItemStatus(str, enum.Enum):
    ON_SALE = "ON_SALE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    HIDDEN = "HIDDEN"


class ImageStatus(str, enum.Enum):
    TEMP = "TEMP"
    ATTACHED = "ATTACHED"
    DELETED = "DELETED"


class MessageType(str, enum.Enum):
    TEXT = "TEXT"


class TransactionStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


class ReportStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    REVIEWING = "REVIEWING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class ReportTargetType(str, enum.Enum):
    ITEM = "ITEM"
    USER = "USER"
    CHAT_ROOM = "CHAT_ROOM"
    MESSAGE = "MESSAGE"


class ReportReason(str, enum.Enum):
    SCAM_SUSPECTED = "SCAM_SUSPECTED"
    PROHIBITED_ITEM = "PROHIBITED_ITEM"
    FALSE_INFORMATION = "FALSE_INFORMATION"
    ABUSIVE_LANGUAGE = "ABUSIVE_LANGUAGE"
    SPAM = "SPAM"
    INAPPROPRIATE_CONTENT = "INAPPROPRIATE_CONTENT"
    ETC = "ETC"


class AdminActionType(str, enum.Enum):
    NONE = "NONE"
    ITEM_HIDDEN = "ITEM_HIDDEN"
    ITEM_DELETED = "ITEM_DELETED"
    USER_SUSPENDED = "USER_SUSPENDED"
    REPORT_REJECTED = "REPORT_REJECTED"
