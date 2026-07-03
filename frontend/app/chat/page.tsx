"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ReportForm } from "@/components/report-form";
import { apiFetch } from "@/lib/api";
import { hasAccessToken } from "@/lib/auth";
import { formatItemStatus, getItemStatusClassName } from "@/lib/labels";

type ChatRoom = {
  id: number;
  item: { id: number; title: string; status: string };
  opponent: { nickname: string };
  unread_count: number;
  last_message?: { content: string };
};
type RoomDetail = {
  id: number;
  item: { id: number; title: string; status: string; price: number };
  buyer: { id: number; nickname: string };
  seller: { id: number; nickname: string };
  opponent: { id: number; nickname: string };
  transaction?: {
    id: number;
    status: string;
    buyer_completed: boolean;
    seller_completed: boolean;
  } | null;
};

type Message = {
  id: number;
  sender_id: number;
  content: string;
  created_at: string;
};
type Me = { id: number };

export default function ChatPage() {
  const router = useRouter();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [roomDetail, setRoomDetail] = useState<RoomDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");
  const [content, setContent] = useState("");

  async function loadRooms(preferredRoomId?: number | null) {
    const data = await apiFetch<{ chat_rooms: ChatRoom[] }>("/api/v1/chat-rooms");
    setRooms(data.chat_rooms);
    const nextSelected = preferredRoomId && data.chat_rooms.some((room) => room.id === preferredRoomId) ? preferredRoomId : data.chat_rooms[0]?.id ?? null;
    setSelectedRoomId(nextSelected);
  }

  useEffect(() => {
    const preferredRoomId = typeof window !== "undefined" ? Number(new URLSearchParams(window.location.search).get("room")) || null : null;
    if (hasAccessToken()) {
      apiFetch<Me>("/api/v1/auth/me")
        .then(setMe)
        .catch(() => setMe(null));
    } else {
      setMe(null);
    }
    loadRooms(preferredRoomId)
      .catch((err) => setError(err instanceof Error ? err.message : "채팅 목록을 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    if (!selectedRoomId) return;
    apiFetch<RoomDetail>(`/api/v1/chat-rooms/${selectedRoomId}`)
      .then(setRoomDetail)
      .catch((err) => setError(err instanceof Error ? err.message : "채팅 정보를 불러오지 못했습니다."));
    apiFetch<{ messages: Message[] }>(`/api/v1/chat-rooms/${selectedRoomId}/messages`)
      .then(async (data) => {
        setMessages(data.messages);
        const lastMessageId = data.messages[data.messages.length - 1]?.id;
        if (lastMessageId) {
          await apiFetch(`/api/v1/chat-rooms/${selectedRoomId}/read`, {
            method: "PATCH",
            body: JSON.stringify({ last_read_message_id: lastMessageId }),
          }).catch(() => undefined);
          await loadRooms(selectedRoomId).catch(() => undefined);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "메시지를 불러오지 못했습니다."));
  }, [selectedRoomId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedRoomId || !content.trim()) return;
    try {
      const created = await apiFetch<Message>(`/api/v1/chat-rooms/${selectedRoomId}/messages`, {
        method: "POST",
        body: JSON.stringify({ content, message_type: "TEXT" }),
      });
      setMessages((prev) => [...prev, created]);
      setContent("");
      await loadRooms(selectedRoomId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "메시지 전송에 실패했습니다.");
    }
  }

  async function handleDeleteRoom() {
    if (!selectedRoomId) return;
    setError("");
    try {
      await apiFetch(`/api/v1/chat-rooms/${selectedRoomId}`, { method: "DELETE" });
      setMessages([]);
      await loadRooms(null);
      router.replace("/chat");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "채팅 삭제에 실패했습니다.");
    }
  }

  async function handlePurchase() {
    if (!roomDetail) return;
    setError("");
    try {
      await apiFetch("/api/v1/transactions", {
        method: "POST",
        body: JSON.stringify({ item_id: roomDetail.item.id, price: roomDetail.item.price }),
      });
      const updated = await apiFetch<RoomDetail>(`/api/v1/chat-rooms/${roomDetail.id}`);
      setRoomDetail(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "구매 의사 전송에 실패했습니다.");
    }
  }

  async function handleItemStatus(status: "ON_SALE" | "RESERVED") {
    if (!roomDetail) return;
    setError("");
    try {
      await apiFetch(`/api/v1/items/${roomDetail.item.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      const updated = await apiFetch<RoomDetail>(`/api/v1/chat-rooms/${roomDetail.id}`);
      setRoomDetail(updated);
      await loadRooms(roomDetail.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "상품 상태 변경에 실패했습니다.");
    }
  }

  async function handleComplete(transactionId: number) {
    setError("");
    try {
      await apiFetch(`/api/v1/transactions/${transactionId}/complete`, {
        method: "PATCH",
      });
      const updated = await apiFetch<RoomDetail>(`/api/v1/chat-rooms/${selectedRoomId}`);
      setRoomDetail(updated);
      await loadRooms(selectedRoomId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "거래 완료 처리에 실패했습니다.");
    }
  }

  const selectedRoom = rooms.find((room) => room.id === selectedRoomId);
  const isSeller = roomDetail && me ? roomDetail.seller.id === me.id : false;
  const isBuyer = roomDetail && me ? roomDetail.buyer.id === me.id : false;
  const transaction = roomDetail?.transaction || null;
  const canBuyerPurchase = isBuyer && !transaction;
  const canComplete = transaction && roomDetail?.item.status === "RESERVED" && ((isBuyer && !transaction.buyer_completed) || (isSeller && !transaction.seller_completed));

  return (
    <div className="chat-layout">
      <section className="panel chat-room-list">
        <div className="section-title">
          <h1 className="page-title">채팅</h1>
        </div>
        <div className="stack-list">
          {rooms.map((room) => (
            <button className={`room-button ${selectedRoomId === room.id ? "active" : ""}`} key={room.id} type="button" onClick={() => setSelectedRoomId(room.id)}>
              <div className="list-card-head">
                <div>
                  <div className="card-title">{room.item.title}</div>
                  <div className="card-sub">{room.opponent.nickname}</div>
                </div>
                {room.unread_count > 0 ? <div className="status status-unread">{room.unread_count}</div> : null}
              </div>
              <div className="card-sub">{room.last_message?.content || "아직 메시지가 없습니다."}</div>
            </button>
          ))}
          {rooms.length === 0 ? <div className="muted">채팅방이 없습니다.</div> : null}
        </div>
      </section>
      <section className="panel chat-message-panel">
        <div className="section-title">
          <div>
            <h2>{selectedRoom ? selectedRoom.item.title : "대화 선택"}</h2>
            {selectedRoom ? <div className="muted">{selectedRoom.opponent.nickname}</div> : null}
          </div>
          {selectedRoom ? (
            <div className="detail-actions">
              <Link className="button subtle" href={`/items/${selectedRoom.item.id}`}>
                상품 보기
              </Link>
              {roomDetail?.opponent?.id ? (
                <Link
                  className="button subtle"
                  href={`/wallet?recipientId=${roomDetail.opponent.id}&chatRoomId=${selectedRoom.id}${transaction ? `&transactionId=${transaction.id}` : ""}`}
                >
                  송금
                </Link>
              ) : null}
              {roomDetail?.opponent?.id ? (
                <ReportForm
                  options={[
                    { label: "사용자 신고", targetType: "USER", targetId: roomDetail.opponent.id },
                  ]}
                />
              ) : null}
              <button className="button subtle danger" type="button" onClick={handleDeleteRoom}>
                채팅 삭제
              </button>
            </div>
          ) : null}
        </div>
        {selectedRoom ? (
          <div className="chat-room-meta">
            <div className={getItemStatusClassName(roomDetail?.item.status || selectedRoom.item.status)}>
              {formatItemStatus(roomDetail?.item.status || selectedRoom.item.status)}
            </div>
            {transaction ? <div className="status status-on-sale">{transaction.status === "REQUESTED" ? "구매 의사 있음" : transaction.status === "ACCEPTED" ? "거래완료 대기" : "거래완료"}</div> : null}
            {transaction ? (
              <div className="muted">
                구매자 완료 {transaction.buyer_completed ? "완료" : "대기"} · 판매자 완료 {transaction.seller_completed ? "완료" : "대기"}
              </div>
            ) : null}
          </div>
        ) : null}
        {selectedRoom ? (
          <div className="chat-action-bar">
            {canBuyerPurchase ? (
              <button className="button primary" type="button" onClick={() => void handlePurchase()}>
                구매하기
              </button>
            ) : null}
            {isSeller ? (
              <>
                <button className="button subtle" type="button" onClick={() => void handleItemStatus("ON_SALE")}>
                  판매중
                </button>
                <button className="button subtle" type="button" onClick={() => void handleItemStatus("RESERVED")}>
                  예약중
                </button>
              </>
            ) : null}
            {transaction && canComplete ? (
              <button className="button primary" type="button" onClick={() => void handleComplete(transaction.id)}>
                거래완료
              </button>
            ) : null}
          </div>
        ) : null}
        {error ? <div className="error-box">{error}</div> : null}
        <div className="message-stream">
          {messages.map((message) => (
            <div className={`message-row ${message.sender_id === me?.id ? "me" : "other"}`} key={message.id}>
              <div className={`message-bubble ${message.sender_id === me?.id ? "me" : ""}`}>{message.content}</div>
            </div>
          ))}
          {selectedRoomId && messages.length === 0 ? <div className="muted">아직 메시지가 없습니다.</div> : null}
        </div>
        <form className="message-form" onSubmit={handleSubmit}>
          <input className="chat-input" value={content} onChange={(event) => setContent(event.target.value)} placeholder="메시지를 입력하세요" />
          <button className="button primary" type="submit">
            보내기
          </button>
        </form>
      </section>
    </div>
  );
}
