"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { formatItemStatus, formatTransactionStatus, getItemStatusClassName } from "@/lib/labels";

type Transaction = {
  id: number;
  status: string;
  price: number;
  item: { id: number; title: string; status: string };
  buyer: { id: number; nickname: string };
  seller: { id: number; nickname: string };
  created_at: string;
  buyer_completed?: boolean;
  seller_completed?: boolean;
  accepted_at?: string | null;
  completed_at?: string | null;
};

export default function TransactionsPage() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [role, setRole] = useState("");
  const [error, setError] = useState("");

  async function loadTransactions(nextRole: string) {
    const search = new URLSearchParams();
    if (nextRole) search.set("role", nextRole);
    const data = await apiFetch<{ transactions: Transaction[] }>(`/api/v1/transactions?${search.toString()}`);
    setTransactions(data.transactions);
  }

  useEffect(() => {
    loadTransactions(role)
      .catch((err) => setError(err instanceof Error ? err.message : "거래 내역을 불러오지 못했습니다."));
  }, [role]);

  const roleLabel = useMemo(() => {
    if (role === "buyer") return "구매";
    if (role === "seller") return "판매";
    return "전체";
  }, [role]);

  return (
    <div className="section">
      <div className="section-title">
        <h1 className="page-title">거래내역</h1>
        <div className="tabs">
          <button className={`tab ${role === "" ? "active" : ""}`} type="button" onClick={() => setRole("")}>
            전체
          </button>
          <button className={`tab ${role === "buyer" ? "active" : ""}`} type="button" onClick={() => setRole("buyer")}>
            구매
          </button>
          <button className={`tab ${role === "seller" ? "active" : ""}`} type="button" onClick={() => setRole("seller")}>
            판매
          </button>
        </div>
      </div>
      {error ? <div className="error-box">{error}</div> : null}
      <div className="stack-list">
        {transactions.map((transaction) => (
          <div className="list-card clickable-card" key={transaction.id} onClick={() => router.push(`/items/${transaction.item.id}`)} role="button" tabIndex={0}>
            <div className="list-card-head">
              <div>
                <h3 className="card-title">{transaction.item.title}</h3>
                <div className="card-sub">
                  구매자 {transaction.buyer.nickname} · 판매자 {transaction.seller.nickname}
                </div>
              </div>
              <div className={getItemStatusClassName(transaction.item.status)}>{formatItemStatus(transaction.item.status)}</div>
            </div>
            <div className="meta-line">
              <span>
                {roleLabel} · {transaction.price.toLocaleString()}원
              </span>
              <span>{formatTransactionStatus(transaction.status)}</span>
            </div>
            <div className="card-sub">
              구매자 완료 {transaction.buyer_completed ? "완료" : "대기"} · 판매자 완료 {transaction.seller_completed ? "완료" : "대기"}
            </div>
            <div className="transaction-action-row" onClick={(event) => event.stopPropagation()}>
              <button className="button subtle" type="button" onClick={() => router.push(`/items/${transaction.item.id}`)}>
                상품 보기
              </button>
            </div>
          </div>
        ))}
        {transactions.length === 0 ? <div className="panel empty-state muted">거래 내역이 없습니다.</div> : null}
      </div>
    </div>
  );
}
