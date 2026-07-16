from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.transfer import Wallet


def get_or_create_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.scalar(select(Wallet).where(Wallet.user_id == user_id))
    if wallet:
        return wallet

    try:
        # The savepoint keeps the outer transaction usable if another request
        # creates this user's unique wallet at the same time.
        with db.begin_nested():
            wallet = Wallet(user_id=user_id, balance=0)
            db.add(wallet)
            db.flush()
        return wallet
    except IntegrityError:
        wallet = db.scalar(select(Wallet).where(Wallet.user_id == user_id))
        if wallet is None:
            raise
        return wallet


def lock_wallets(db: Session, user_ids: Iterable[int]) -> dict[int, Wallet]:
    ordered_user_ids = sorted(set(user_ids))
    if not ordered_user_ids:
        return {}

    for user_id in ordered_user_ids:
        get_or_create_wallet(db, user_id)
    db.flush()

    # A stable lock order prevents A->B and B->A transfers from deadlocking.
    wallets = db.scalars(
        select(Wallet)
        .where(Wallet.user_id.in_(ordered_user_ids))
        .order_by(Wallet.user_id.asc())
        .with_for_update()
        .execution_options(populate_existing=True)
    ).all()
    if len(wallets) != len(ordered_user_ids):
        raise RuntimeError("WALLET_LOCK_FAILED")
    return {wallet.user_id: wallet for wallet in wallets}
