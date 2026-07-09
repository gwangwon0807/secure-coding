"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { AuthGuard } from "@/components/auth-guard";
import { apiFetch } from "@/lib/api";

type Wallet = { user: { id: number; nickname: string }; balance: number };
type LedgerEntry = { id: number; transaction_type: string; amount: number; balance_after: number; description: string; created_at: string };
type Transfer = { id: number; sender: { id: number; nickname: string }; recipient: { id: number; nickname: string }; amount: number; note: string | null; created_at: string };
type UserSummary = { id: number; nickname: string };
type WalletMode = "deposit" | "withdraw" | "transfer";

function WalletContent() {
  const searchParams = useSearchParams();
  const initialRecipientId = searchParams.get("recipientId") || "";
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [recipientId] = useState(initialRecipientId);
  const [recipient, setRecipient] = useState<UserSummary | null>(null);
  const [mode, setMode] = useState<WalletMode>(initialRecipientId ? "transfer" : "deposit");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadWallet() {
    const [walletData, ledgerData, transferData] = await Promise.all([
      apiFetch<Wallet>("/api/v1/transfers/wallet/me"),
      apiFetch<{ ledger: LedgerEntry[] }>("/api/v1/transfers/wallet/me/ledger"),
      apiFetch<{ transfers: Transfer[] }>("/api/v1/transfers"),
    ]);
    setWallet(walletData);
    setLedger(ledgerData.ledger);
    setTransfers(transferData.transfers);
  }

  useEffect(() => {
    loadWallet().catch((err) => setError(err instanceof Error ? err.message : "지갑 정보를 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    if (!recipientId) {
      setRecipient(null);
      return;
    }
    apiFetch<UserSummary>(`/api/v1/users/${recipientId}`)
      .then(setRecipient)
      .catch(() => setRecipient(null));
  }, [recipientId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    const numericAmount = Number(amount);
    try {
      if (mode === "deposit") {
        await apiFetch("/api/v1/transfers/wallet/me/deposit", {
          method: "POST",
          body: JSON.stringify({ amount: numericAmount }),
        });
        setSuccess("입금이 완료되었습니다.");
      }
      if (mode === "withdraw") {
        await apiFetch("/api/v1/transfers/wallet/me/withdraw", {
          method: "POST",
          body: JSON.stringify({ amount: numericAmount }),
        });
        setSuccess("출금이 완료되었습니다.");
      }
      if (mode === "transfer") {
        if (!recipientId) {
          setError("송금할 상대를 먼저 선택해 주세요.");
          return;
        }
        await apiFetch("/api/v1/transfers", {
          method: "POST",
          body: JSON.stringify({
            recipient_id: Number(recipientId),
            amount: numericAmount,
            note: note || null,
            transaction_id: searchParams.get("transactionId") ? Number(searchParams.get("transactionId")) : null,
            chat_room_id: searchParams.get("chatRoomId") ? Number(searchParams.get("chatRoomId")) : null,
          }),
        });
        setSuccess("송금이 완료되었습니다.");
      }
      setAmount("");
      setNote("");
      await loadWallet();
    } catch (err) {
      setError(err instanceof Error ? err.message : "처리에 실패했습니다.");
    }
  }

  const actionLabel = mode === "deposit" ? "입금하기" : mode === "withdraw" ? "출금하기" : "송금하기";

  return (
    <div className="section">
      <section className="panel wide-panel">
        <div className="section-title">
          <h1 className="page-title">지갑</h1>
          <div className="tabs wallet-tabs">
            <button className={`tab ${mode === "deposit" ? "active" : ""}`} type="button" onClick={() => setMode("deposit")}>
              입금
            </button>
            <button className={`tab ${mode === "withdraw" ? "active" : ""}`} type="button" onClick={() => setMode("withdraw")}>
              출금
            </button>
            {recipientId ? (
              <button className={`tab ${mode === "transfer" ? "active" : ""}`} type="button" onClick={() => setMode("transfer")}>
                송금
              </button>
            ) : null}
          </div>
        </div>
        <div className="wallet-balance-card">
          <span className="muted">현재 잔액</span>
          <strong>{(wallet?.balance || 0).toLocaleString()}원</strong>
        </div>
        <form className="form two-column-form" onSubmit={handleSubmit}>
          {mode === "transfer" ? (
            <div className="field-group field-span-2">
              <label className="field-label">받는 사람</label>
              <div className="recipient-display">{recipient?.nickname || "상대 정보를 불러오는 중입니다."}</div>
            </div>
          ) : null}
          <div className="field-group field-span-2">
            <label className="field-label" htmlFor="amount">
              금액
            </label>
            <input id="amount" inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} />
          </div>
          {mode === "transfer" ? (
            <div className="field-group field-span-2">
              <label className="field-label" htmlFor="note">
                메모
              </label>
              <input id="note" value={note} onChange={(event) => setNote(event.target.value)} placeholder="선택 입력" />
            </div>
          ) : null}
          {error ? <div className="error-box field-span-2">{error}</div> : null}
          {success ? <div className="success-box field-span-2">{success}</div> : null}
          <button className="button primary form-submit-button field-span-2" type="submit">
            {actionLabel}
          </button>
        </form>
      </section>

      <section className="panel wide-panel">
        <div className="section-title compact">
          <h2>최근 송금 내역</h2>
        </div>
        <div className="stack-list">
          {transfers.map((transfer) => (
            <div className="list-card" key={transfer.id}>
              <div className="list-card-head">
                <strong>{transfer.sender.nickname} → {transfer.recipient.nickname}</strong>
                <div className="price small-price">{transfer.amount.toLocaleString()}원</div>
              </div>
              <div className="card-sub">{transfer.note || "메모 없음"}</div>
            </div>
          ))}
          {transfers.length === 0 ? <div className="muted">송금 내역이 없습니다.</div> : null}
        </div>
      </section>

      <section className="panel wide-panel">
        <div className="section-title compact">
          <h2>잔액 기록</h2>
        </div>
        <div className="stack-list">
          {ledger.map((entry) => (
            <div className="list-card" key={entry.id}>
              <div className="list-card-head">
                <strong>{entry.description}</strong>
                <div className={entry.amount >= 0 ? "price small-price" : "status status-hidden"}>{entry.amount >= 0 ? `+${entry.amount.toLocaleString()}원` : `${entry.amount.toLocaleString()}원`}</div>
              </div>
              <div className="card-sub">잔액 {entry.balance_after.toLocaleString()}원</div>
            </div>
          ))}
          {ledger.length === 0 ? <div className="muted">기록이 없습니다.</div> : null}
        </div>
      </section>
    </div>
  );
}

export default function WalletPage() {
  return (
    <AuthGuard>
      <WalletContent />
    </AuthGuard>
  );
}
