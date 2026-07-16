from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.category import Category
from app.models.enums import UserRole
from app.models.user import User


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.backend_cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount(settings.public_upload_prefix, StaticFiles(directory=settings.upload_dir), name="uploads")
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}


def seed_data() -> None:
    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.email == settings.admin_email)):
            admin = User(
                email=settings.admin_email,
                password_hash=get_password_hash(settings.admin_password),
                nickname=settings.admin_nickname,
                role=UserRole.ADMIN,
            )
            db.add(admin)
        category_names = ["전자기기", "의류", "가구", "생활용품", "도서", "스포츠", "기타"]
        for idx, name in enumerate(category_names, start=1):
            existing = db.scalar(select(Category).where(Category.name == name))
            if not existing:
                db.add(Category(name=name, sort_order=idx))
        db.commit()
    finally:
        db.close()


def ensure_postgres_enums() -> None:
    if engine.dialect.name != "postgresql":
        return
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1
                            FROM pg_type
                            WHERE typname = 'reporttargettype'
                        ) THEN
                            ALTER TYPE reporttargettype ADD VALUE IF NOT EXISTS 'COMMUNITY_POST';
                            ALTER TYPE reporttargettype ADD VALUE IF NOT EXISTS 'COMMUNITY_COMMENT';
                        END IF;
                        IF EXISTS (
                            SELECT 1
                            FROM pg_type
                            WHERE typname = 'wallettransactiontype'
                        ) THEN
                            ALTER TYPE wallettransactiontype ADD VALUE IF NOT EXISTS 'USER_DEPOSIT';
                            ALTER TYPE wallettransactiontype ADD VALUE IF NOT EXISTS 'DEPOSIT_APPROVED';
                            ALTER TYPE wallettransactiontype ADD VALUE IF NOT EXISTS 'USER_WITHDRAWAL';
                        END IF;
                        IF EXISTS (
                            SELECT 1
                            FROM pg_type
                            WHERE typname = 'depositrequeststatus'
                        ) THEN
                            ALTER TYPE depositrequeststatus ADD VALUE IF NOT EXISTS 'APPROVED';
                            ALTER TYPE depositrequeststatus ADD VALUE IF NOT EXISTS 'REJECTED';
                        END IF;
                        IF EXISTS (
                            SELECT 1
                            FROM pg_type
                            WHERE typname = 'adminactiontype'
                        ) THEN
                            ALTER TYPE adminactiontype ADD VALUE IF NOT EXISTS 'USER_DELETED';
                            ALTER TYPE adminactiontype ADD VALUE IF NOT EXISTS 'COMMUNITY_POST_HIDDEN';
                            ALTER TYPE adminactiontype ADD VALUE IF NOT EXISTS 'COMMUNITY_COMMENT_HIDDEN';
                            ALTER TYPE adminactiontype ADD VALUE IF NOT EXISTS 'CHAT_ROOM_DELETED';
                            ALTER TYPE adminactiontype ADD VALUE IF NOT EXISTS 'MESSAGE_DELETED';
                        END IF;
                    END
                    $$;
                    """
                )
            )
    except SQLAlchemyError:
        # Fresh databases or partially initialized schemas should not fail startup here.
        return


def ensure_postgres_wallet_constraints() -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_wallets_balance_nonnegative') THEN
                        ALTER TABLE wallets
                        ADD CONSTRAINT ck_wallets_balance_nonnegative CHECK (balance >= 0);
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_transfers_amount_positive') THEN
                        ALTER TABLE transfers
                        ADD CONSTRAINT ck_transfers_amount_positive CHECK (amount > 0);
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_deposit_requests_amount_positive') THEN
                        ALTER TABLE deposit_requests
                        ADD CONSTRAINT ck_deposit_requests_amount_positive CHECK (amount > 0);
                    END IF;
                END
                $$;
                """
            )
        )


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_postgres_enums()
    ensure_postgres_wallet_constraints()
    seed_data()
