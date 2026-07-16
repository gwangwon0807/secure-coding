"use client";

import { FormEvent, useEffect, useState } from "react";
import type { ReactNode } from "react";
import Link from "next/link";

import { AuthGuard } from "@/components/auth-guard";
import { API_BASE_URL, apiFetch } from "@/lib/api";
import { formatItemStatus, formatTransactionStatus, getItemStatusClassName } from "@/lib/labels";

type AdminUser = { id: number; email: string; nickname: string; status: string; role: string; needs_review: boolean; report_count: number };
type AdminItem = { id: number; title: string; status: string; seller: { id?: number; nickname: string }; report_count: number };
type AdminReport = { id: number; target_type: string; target_id: number; reporter: { nickname: string }; reason: string; status: string; target_summary: string | null };
type AdminPost = { id: number; title: string; author: { nickname: string }; comment_count: number; report_count: number; deleted_at: string | null };
type AdminComment = { id: number; post_id: number; post_title: string | null; author: { nickname: string }; content: string; report_count: number; deleted_at: string | null };
type AdminChatRoom = { id: number; item: { title: string }; buyer: { nickname: string }; seller: { nickname: string }; message_count: number };
type Wallet = { user: { id: number; nickname: string }; balance: number };
type DepositRequest = { id: number; user: { id: number; nickname: string }; amount: number; status: string; created_at: string; reviewed_at: string | null; reviewed_by_admin: { id: number; nickname: string } | null };
type Transfer = { id: number; sender: { nickname: string }; recipient: { nickname: string }; amount: number; note: string | null; created_at: string };
type Tab = "users" | "items" | "community" | "chat" | "reports" | "wallets" | "depositRequests" | "transfers";
type DetailKind = "user" | "item" | "post" | "comment" | "chat" | "report" | "transfer" | "depositRequest";
type SelectedDetail = { kind: DetailKind; id: number; title: string } | null;

const DETAIL_ENDPOINTS: Record<DetailKind, (id: number) => string> = {
  user: (id) => `/api/v1/admin/users/${id}`,
  item: (id) => `/api/v1/admin/items/${id}`,
  post: (id) => `/api/v1/admin/community/posts/${id}`,
  comment: (id) => `/api/v1/admin/community/comments/${id}`,
  chat: (id) => `/api/v1/admin/chat-rooms/${id}`,
  report: (id) => `/api/v1/admin/reports/${id}`,
  transfer: (id) => `/api/v1/admin/transfers/${id}`,
  depositRequest: (id) => `/api/v1/admin/deposit-requests/${id}`,
};

function statusText(status: string) {
  const map: Record<string, string> = {
    ACTIVE: "정상",
    SUSPENDED: "정지",
    DELETED: "삭제",
    RECEIVED: "접수",
    REVIEWING: "검토중",
    RESOLVED: "처리됨",
    REJECTED: "반려",
    PENDING: "대기중",
    APPROVED: "승인됨",
    NONE: "조치 없음",
    ITEM_HIDDEN: "상품 숨김",
    ITEM_DELETED: "상품 삭제",
    USER_SUSPENDED: "사용자 정지",
    USER_DELETED: "사용자 삭제",
    COMMUNITY_POST_HIDDEN: "게시글 숨김",
    COMMUNITY_COMMENT_HIDDEN: "댓글 숨김",
    CHAT_ROOM_DELETED: "채팅방 삭제",
    MESSAGE_DELETED: "메시지 삭제",
    REPORT_REJECTED: "신고 반려",
    COMPLETED: "완료",
  };
  return map[status] || formatItemStatus(status);
}

function AdminContent() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [items, setItems] = useState<AdminItem[]>([]);
  const [posts, setPosts] = useState<AdminPost[]>([]);
  const [comments, setComments] = useState<AdminComment[]>([]);
  const [chatRooms, setChatRooms] = useState<AdminChatRoom[]>([]);
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [depositRequests, setDepositRequests] = useState<DepositRequest[]>([]);
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [tab, setTab] = useState<Tab>("users");
  const [selected, setSelected] = useState<SelectedDetail>(null);
  const [detail, setDetail] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [reason, setReason] = useState("");
  const [userStatus, setUserStatus] = useState("ACTIVE");
  const [itemStatus, setItemStatus] = useState("ON_SALE");
  const [walletAmount, setWalletAmount] = useState("");
  const [walletReason, setWalletReason] = useState("");
  const [depositDecisionReason, setDepositDecisionReason] = useState("");
  const [reportStatus, setReportStatus] = useState("REVIEWING");
  const [reportAction, setReportAction] = useState("NONE");

  async function loadAdminData() {
    const failures: string[] = [];
    async function load<T>(label: string, path: string, apply: (data: T) => void) {
      try {
        apply(await apiFetch<T>(path));
      } catch (err) {
        const message = err instanceof Error ? err.message : "데이터를 불러오지 못했습니다.";
        failures.push(`${label}: ${message}`);
      }
    }

    await Promise.all([
      load<{ users: AdminUser[] }>("회원", "/api/v1/admin/users", (data) => setUsers(data.users)),
      load<{ items: AdminItem[] }>("상품", "/api/v1/admin/items", (data) => setItems(data.items)),
      load<{ reports: AdminReport[] }>("신고", "/api/v1/admin/reports", (data) => setReports(data.reports.filter((report) => !["RESOLVED", "REJECTED"].includes(report.status)))),
      load<{ posts: AdminPost[] }>("커뮤니티 글", "/api/v1/admin/community/posts", (data) => setPosts(data.posts)),
      load<{ comments: AdminComment[] }>("커뮤니티 댓글", "/api/v1/admin/community/comments", (data) => setComments(data.comments)),
      load<{ chat_rooms: AdminChatRoom[] }>("채팅", "/api/v1/admin/chat-rooms", (data) => setChatRooms(data.chat_rooms)),
      load<{ wallets: Wallet[] }>("지갑", "/api/v1/admin/wallets", (data) => setWallets(data.wallets)),
      load<{ requests: DepositRequest[] }>("충전 요청", "/api/v1/admin/deposit-requests", (data) => setDepositRequests(data.requests)),
      load<{ transfers: Transfer[] }>("송금", "/api/v1/admin/transfers", (data) => setTransfers(data.transfers)),
    ]);

    setError(failures.join("\n"));
  }

  async function openDetail(next: NonNullable<SelectedDetail>) {
    setSelected(next);
    setDetail(null);
    setError("");
    setNotice("");
    const data = await apiFetch<any>(DETAIL_ENDPOINTS[next.kind](next.id));
    setDetail(data);
    setUserStatus(data?.user?.status || data?.status || "ACTIVE");
    setItemStatus(data?.status || "ON_SALE");
    setReportStatus(data?.status || "REVIEWING");
    setReportAction(data?.action_type || "NONE");
    setReason("");
    setWalletAmount("");
    setWalletReason("");
    setDepositDecisionReason("");
  }

  function handleTabChange(nextTab: Tab) {
    setTab(nextTab);
    setSelected(null);
    setDetail(null);
    setError("");
    setNotice("");
    setReason("");
    setWalletAmount("");
    setWalletReason("");
    setDepositDecisionReason("");
  }

  async function refreshSelected() {
    await loadAdminData();
    if (selected) {
      const data = await apiFetch<any>(DETAIL_ENDPOINTS[selected.kind](selected.id));
      setDetail(data);
    }
  }

  useEffect(() => {
    loadAdminData().catch((err) => setError(err instanceof Error ? err.message : "관리자 데이터를 불러오지 못했습니다."));
  }, []);

  async function handleUserStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || selected.kind !== "user" || !reason.trim()) return;
    await apiFetch(`/api/v1/admin/users/${selected.id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: userStatus, reason }),
    });
    setNotice("회원 상태가 변경되었습니다.");
    await refreshSelected();
  }

  async function handleItemStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || selected.kind !== "item" || !reason.trim()) return;
    await apiFetch(`/api/v1/admin/items/${selected.id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: itemStatus, reason }),
    });
    setNotice("상품 상태가 변경되었습니다.");
    await refreshSelected();
  }

  async function handleModeration(path: string, message: string) {
    if (!reason.trim()) return;
    await apiFetch(path, {
      method: "PATCH",
      body: JSON.stringify({ reason }),
    });
    setNotice(message);
    await refreshSelected();
  }

  async function handleDeleteChatRoom() {
    if (!selected || selected.kind !== "chat") return;
    await apiFetch(`/api/v1/admin/chat-rooms/${selected.id}`, { method: "DELETE" });
    setNotice("채팅방이 삭제되었습니다.");
    setSelected(null);
    setDetail(null);
    await loadAdminData();
  }

  async function handleWalletAdjust(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const userId = selected?.kind === "user" ? selected.id : detail?.user?.id;
    if (!userId || !walletAmount || !walletReason.trim()) return;
    await apiFetch(`/api/v1/admin/wallets/${userId}/adjust`, {
      method: "PATCH",
      body: JSON.stringify({ amount: Number(walletAmount), reason: walletReason }),
    });
    setNotice("지갑 잔액이 조정되었습니다.");
    setWalletAmount("");
    setWalletReason("");
    await refreshSelected();
  }

  async function handleReportUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || selected.kind !== "report") return;
    await apiFetch(`/api/v1/admin/reports/${selected.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        status: reportStatus,
        action_type: reportAction,
        admin_memo: reason || null,
        result_message: reason || null,
      }),
    });
    setNotice("신고가 처리되었습니다.");
    await refreshSelected();
  }

  async function handleDepositDecision(action: "approve" | "reject") {
    if (!selected || selected.kind !== "depositRequest") return;
    await apiFetch(`/api/v1/admin/deposit-requests/${selected.id}/${action}`, {
      method: "PATCH",
      body: JSON.stringify({ reason: depositDecisionReason || null }),
    });
    setNotice(action === "approve" ? "충전 요청을 승인했습니다." : "충전 요청을 거절했습니다.");
    setDepositDecisionReason("");
    await refreshSelected();
  }

  const reviewUsers = users.filter((user) => user.needs_review).slice(0, 8);

  return (
    <div className="admin-workspace">
      <div className="section-title">
        <h1 className="page-title">관리자</h1>
        <div className="tabs wrap-tabs">
          {[
            ["users", "회원"],
            ["items", "상품"],
            ["community", "커뮤니티"],
            ["chat", "채팅"],
            ["reports", "신고"],
            ["wallets", "지갑"],
            ["depositRequests", "충전요청"],
            ["transfers", "송금"],
          ].map(([value, label]) => (
            <button key={value} className={`tab ${tab === value ? "active" : ""}`} type="button" onClick={() => handleTabChange(value as Tab)}>
              {label}
            </button>
          ))}
        </div>
      </div>
      {error ? <div className="error-box">{error}</div> : null}
      {notice ? <div className="success-box">{notice}</div> : null}

      <section className="admin-review-strip">
        {reviewUsers.length === 0 ? <span className="muted">관리 필요 사용자가 없습니다.</span> : null}
        {reviewUsers.map((user) => (
          <button className="review-user-chip" key={user.id} type="button" onClick={() => void openDetail({ kind: "user", id: user.id, title: user.nickname })}>
            <strong>{user.nickname}</strong>
            <span>신고 {user.report_count}건</span>
          </button>
        ))}
      </section>

      <div className="admin-split">
        <section className="admin-list-panel">
          {tab === "users" ? renderUsers(users, openDetail) : null}
          {tab === "items" ? renderItems(items, openDetail) : null}
          {tab === "community" ? renderCommunity(posts, comments, openDetail) : null}
          {tab === "chat" ? renderChatRooms(chatRooms, openDetail) : null}
          {tab === "reports" ? renderReports(reports, openDetail) : null}
          {tab === "wallets" ? renderWallets(wallets, openDetail) : null}
          {tab === "depositRequests" ? renderDepositRequests(depositRequests, openDetail) : null}
          {tab === "transfers" ? renderTransfers(transfers, openDetail) : null}
        </section>

        <aside className="admin-detail-panel">
          {!selected ? <div className="muted">목록에서 대상을 선택하세요.</div> : null}
          {selected && !detail ? <div className="muted">상세 정보를 불러오는 중입니다.</div> : null}
          {selected && detail ? (
            <div className="admin-detail-content">
              <div className="section-title compact">
                <div>
                  <h2>{selected.title}</h2>
                  <div className="muted">{detailLabel(selected.kind)}</div>
                </div>
              </div>
              {renderDetailBody(selected, detail, openDetail)}
              {renderControls({
                selected,
                detail,
                reason,
                setReason,
                userStatus,
                setUserStatus,
                itemStatus,
                setItemStatus,
                walletAmount,
                setWalletAmount,
                walletReason,
                setWalletReason,
                depositDecisionReason,
                setDepositDecisionReason,
                reportStatus,
                setReportStatus,
                reportAction,
                setReportAction,
                handleUserStatus,
                handleItemStatus,
                handleWalletAdjust,
                handleReportUpdate,
                handleDepositDecision,
                handleModeration,
                handleDeleteChatRoom,
              })}
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

function renderUsers(users: AdminUser[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {users.map((user) => (
        <button className="admin-row-button" key={user.id} type="button" onClick={() => void openDetail({ kind: "user", id: user.id, title: user.nickname })}>
          <strong>{user.nickname}</strong>
          <span>{user.email}</span>
          <span>{user.needs_review ? `관리 필요 · 신고 ${user.report_count}건` : statusText(user.status)}</span>
        </button>
      ))}
    </div>
  );
}

function renderItems(items: AdminItem[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {items.map((item) => (
        <button className="admin-row-button" key={item.id} type="button" onClick={() => void openDetail({ kind: "item", id: item.id, title: item.title })}>
          <strong>{item.title}</strong>
          <span>{item.seller.nickname}</span>
          <span>신고 {item.report_count}건 · {formatItemStatus(item.status)}</span>
        </button>
      ))}
    </div>
  );
}

function renderCommunity(posts: AdminPost[], comments: AdminComment[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {posts.map((post) => (
        <button className="admin-row-button" key={`post-${post.id}`} type="button" onClick={() => void openDetail({ kind: "post", id: post.id, title: post.title })}>
          <strong>{post.title}</strong>
          <span>{post.author.nickname} · 댓글 {post.comment_count}개</span>
          <span>글 · 신고 {post.report_count}건 · {post.deleted_at ? "숨김" : "노출"}</span>
        </button>
      ))}
      {comments.map((comment) => (
        <button className="admin-row-button" key={`comment-${comment.id}`} type="button" onClick={() => void openDetail({ kind: "comment", id: comment.id, title: comment.post_title || "댓글" })}>
          <strong>{comment.content}</strong>
          <span>{comment.author.nickname} · {comment.post_title || "원글 없음"}</span>
          <span>댓글 · 신고 {comment.report_count}건 · {comment.deleted_at ? "숨김" : "노출"}</span>
        </button>
      ))}
    </div>
  );
}

function renderChatRooms(chatRooms: AdminChatRoom[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {chatRooms.map((room) => (
        <button className="admin-row-button" key={room.id} type="button" onClick={() => void openDetail({ kind: "chat", id: room.id, title: room.item.title })}>
          <strong>{room.item.title}</strong>
          <span>{room.buyer.nickname} · {room.seller.nickname}</span>
          <span>메시지 {room.message_count}개</span>
        </button>
      ))}
    </div>
  );
}

function renderReports(reports: AdminReport[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {reports.map((report) => (
        <button className="admin-row-button" key={report.id} type="button" onClick={() => void openDetail({ kind: "report", id: report.id, title: report.target_summary || report.target_type })}>
          <strong>{report.target_summary || report.target_type}</strong>
          <span>{report.reporter.nickname} · {report.reason}</span>
          <span>{statusText(report.status)} · {report.target_type}</span>
        </button>
      ))}
    </div>
  );
}

function renderWallets(wallets: Wallet[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {wallets.map((wallet) => (
        <button className="admin-row-button" key={wallet.user.id} type="button" onClick={() => void openDetail({ kind: "user", id: wallet.user.id, title: wallet.user.nickname })}>
          <strong>{wallet.user.nickname}</strong>
          <span>지갑 잔액</span>
          <span>{wallet.balance.toLocaleString()}원</span>
        </button>
      ))}
    </div>
  );
}

function renderDepositRequests(depositRequests: DepositRequest[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {depositRequests.map((request) => (
        <button className="admin-row-button" key={request.id} type="button" onClick={() => void openDetail({ kind: "depositRequest", id: request.id, title: `${request.user.nickname} 충전 요청` })}>
          <strong>{request.user.nickname}</strong>
          <span>{request.amount.toLocaleString()}원</span>
          <span>{request.status === "PENDING" ? "대기중" : request.status === "APPROVED" ? "승인됨" : "거절됨"}</span>
        </button>
      ))}
    </div>
  );
}

function renderTransfers(transfers: Transfer[], openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  return (
    <div className="table-like">
      {transfers.map((transfer) => (
        <button className="admin-row-button" key={transfer.id} type="button" onClick={() => void openDetail({ kind: "transfer", id: transfer.id, title: `${transfer.sender.nickname} → ${transfer.recipient.nickname}` })}>
          <strong>{transfer.sender.nickname} → {transfer.recipient.nickname}</strong>
          <span>{transfer.note || "메모 없음"}</span>
          <span>{transfer.amount.toLocaleString()}원</span>
        </button>
      ))}
    </div>
  );
}

function detailLabel(kind: DetailKind) {
  return {
    user: "회원 상세",
    item: "상품 상세",
    post: "커뮤니티 글 상세",
    comment: "커뮤니티 댓글 상세",
    chat: "채팅방 상세",
    report: "신고 상세",
    transfer: "송금 상세",
    depositRequest: "충전 요청 상세",
  }[kind];
}

function renderDetailBody(selected: NonNullable<SelectedDetail>, detail: any, openDetail: (target: NonNullable<SelectedDetail>) => Promise<void>) {
  if (selected.kind === "user") return <UserDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "item") return <ItemDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "post") return <PostDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "comment") return <CommentDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "chat") return <ChatDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "report") return <ReportDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "transfer") return <TransferDetail detail={detail} openDetail={openDetail} />;
  if (selected.kind === "depositRequest") return <DepositRequestDetail detail={detail} openDetail={openDetail} />;
  return null;
}

function UserDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  const [activity, setActivity] = useState("items");
  const activityTabs = [
    { key: "items", label: "상품", count: detail.items?.length || 0 },
    { key: "posts", label: "글", count: detail.posts?.length || 0 },
    { key: "comments", label: "댓글", count: detail.comments?.length || 0 },
    { key: "chat_rooms", label: "채팅", count: detail.chat_rooms?.length || 0 },
    { key: "transactions", label: "거래", count: detail.transactions?.length || 0 },
    { key: "transfers", label: "송금", count: detail.transfers?.length || 0 },
    { key: "deposit_requests", label: "충전요청", count: detail.deposit_requests?.length || 0 },
    { key: "reports", label: "신고", count: detail.reports?.length || 0 },
  ];

  return (
    <div className="admin-detail-stack">
      <div className="admin-kv"><span>이메일</span><strong>{detail.user.email}</strong></div>
      <div className="admin-kv"><span>상태</span><strong>{statusText(detail.user.status)}</strong></div>
      <div className="admin-kv"><span>신고</span><strong>{detail.report_count}건</strong></div>
      <div className="admin-kv"><span>지갑</span><strong>{detail.wallet.balance.toLocaleString()}원</strong></div>
      <div className="admin-activity-tabs">
        {activityTabs.map((entry) => (
          <button className={activity === entry.key ? "active" : ""} key={entry.key} type="button" onClick={() => setActivity(entry.key)}>
            {entry.label}
            <span>{entry.count}</span>
          </button>
        ))}
      </div>
      <div className="admin-activity-panel">
        {activity === "items" ? (
          <MiniList title="등록 상품" items={detail.items} render={(item: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "item", id: item.id, title: item.title })}>{item.title} · {formatItemStatus(item.status)}</button>
          )} />
        ) : null}
        {activity === "posts" ? (
          <MiniList title="커뮤니티 글" items={detail.posts} render={(post: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "post", id: post.id, title: post.title })}>{post.title}</button>
          )} />
        ) : null}
        {activity === "comments" ? (
          <MiniList title="댓글" items={detail.comments} render={(comment: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "comment", id: comment.id, title: "댓글" })}>{comment.content}</button>
          )} />
        ) : null}
        {activity === "chat_rooms" ? (
          <MiniList title="채팅방" items={detail.chat_rooms} render={(room: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "chat", id: room.id, title: room.item?.title || "채팅방" })}>{room.item?.title || "채팅방"}</button>
          )} />
        ) : null}
        {activity === "transactions" ? (
          <MiniList title="거래 내역" items={detail.transactions} render={(transaction: any) => (
            <span>{formatTransactionStatus(transaction.status)} · {transaction.price.toLocaleString()}원</span>
          )} />
        ) : null}
        {activity === "transfers" ? (
          <MiniList title="송금 내역" items={detail.transfers} render={(transfer: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "transfer", id: transfer.id, title: `${transfer.sender.nickname} → ${transfer.recipient.nickname}` })}>{transfer.sender.nickname} → {transfer.recipient.nickname} · {transfer.amount.toLocaleString()}원</button>
          )} />
        ) : null}
        {activity === "deposit_requests" ? (
          <MiniList title="충전 요청" items={detail.deposit_requests} render={(request: any) => (
            <button type="button" onClick={() => void openDetail({ kind: "depositRequest", id: request.id, title: `${request.user.nickname} 충전 요청` })}>{request.amount.toLocaleString()}원 · {request.status === "PENDING" ? "대기중" : request.status === "APPROVED" ? "승인됨" : "거절됨"}</button>
          )} />
        ) : null}
        {activity === "reports" ? <ReportList reports={detail.reports} openDetail={openDetail} /> : null}
      </div>
    </div>
  );
}

function ItemDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      {detail.images?.length ? (
        <div className="admin-image-grid">
          {detail.images.map((image: any) => <img key={image.id} alt={detail.title} src={`${API_BASE_URL}${image.image_url}`} />)}
        </div>
      ) : null}
      <div className={getItemStatusClassName(detail.status)}>{formatItemStatus(detail.status)}</div>
      <div className="price">{detail.price.toLocaleString()}원</div>
      <p className="admin-description">{detail.description}</p>
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.seller.id, title: detail.seller.nickname })}>판매자 {detail.seller.nickname}</button>
      <Link className="button subtle" href={`/items/${detail.id}`}>사용자 화면에서 보기</Link>
      <ReportList reports={detail.reports} openDetail={openDetail} />
      <MiniList title="연결 채팅방" items={detail.chat_rooms} render={(room: any) => (
        <button type="button" onClick={() => void openDetail({ kind: "chat", id: room.id, title: detail.title })}>{room.buyer?.nickname} · {room.seller?.nickname}</button>
      )} />
      <MiniList title="거래 내역" items={detail.transactions} render={(tx: any) => <span>{formatTransactionStatus(tx.status)} · {tx.price.toLocaleString()}원</span>} />
    </div>
  );
}

function PostDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.author.id, title: detail.author.nickname })}>작성자 {detail.author.nickname}</button>
      <p className="admin-description">{detail.content}</p>
      {detail.images?.length ? <div className="admin-image-grid">{detail.images.map((image: any) => <img key={image.id} alt={detail.title} src={`${API_BASE_URL}${image.image_url}`} />)}</div> : null}
      <Link className="button subtle" href={`/community/${detail.id}`}>사용자 화면에서 보기</Link>
      <ReportList reports={detail.reports} openDetail={openDetail} />
      <MiniList title="댓글" items={detail.comments} render={(comment: any) => (
        <button type="button" onClick={() => void openDetail({ kind: "comment", id: comment.id, title: "댓글" })}>{comment.author?.nickname} · {comment.content}</button>
      )} />
    </div>
  );
}

function CommentDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.author.id, title: detail.author.nickname })}>작성자 {detail.author.nickname}</button>
      <p className="admin-description">{detail.content}</p>
      {detail.post ? <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "post", id: detail.post.id, title: detail.post.title })}>원글 {detail.post.title}</button> : null}
      <ReportList reports={detail.reports} openDetail={openDetail} />
    </div>
  );
}

function ChatDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      {detail.item ? <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "item", id: detail.item.id, title: detail.item.title })}>상품 {detail.item.title}</button> : null}
      <div className="admin-chat-users">
        <button type="button" onClick={() => void openDetail({ kind: "user", id: detail.buyer.id, title: detail.buyer.nickname })}>{detail.buyer.nickname}</button>
        <button type="button" onClick={() => void openDetail({ kind: "user", id: detail.seller.id, title: detail.seller.nickname })}>{detail.seller.nickname}</button>
      </div>
      <div className="admin-message-list">
        {detail.messages.map((message: any) => (
          <div className="admin-message" key={message.id}>
            <strong>{message.sender?.nickname}</strong>
            <span>{message.content}</span>
          </div>
        ))}
      </div>
      <ReportList reports={detail.reports} openDetail={openDetail} />
    </div>
  );
}

function ReportDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      <div className="admin-kv"><span>신고자</span><strong>{detail.reporter.nickname}</strong></div>
      <div className="admin-kv"><span>사유</span><strong>{detail.reason}</strong></div>
      <div className="admin-kv"><span>상태</span><strong>{statusText(detail.status)}</strong></div>
      {detail.detail ? <p className="admin-description">{detail.detail}</p> : null}
      {detail.target_detail ? <TargetPreview targetType={detail.target_type} targetId={detail.target_id} detail={detail.target_detail} openDetail={openDetail} /> : null}
    </div>
  );
}

function TransferDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      <div className="admin-kv"><span>금액</span><strong>{detail.amount.toLocaleString()}원</strong></div>
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.sender.id, title: detail.sender.nickname })}>보낸 사람 {detail.sender.nickname}</button>
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.recipient.id, title: detail.recipient.nickname })}>받은 사람 {detail.recipient.nickname}</button>
      {detail.note ? <p className="admin-description">{detail.note}</p> : null}
    </div>
  );
}

function DepositRequestDetail({ detail, openDetail }: { detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return (
    <div className="admin-detail-stack">
      <div className="admin-kv"><span>신청 금액</span><strong>{detail.amount.toLocaleString()}원</strong></div>
      <div className="admin-kv"><span>상태</span><strong>{detail.status === "PENDING" ? "대기중" : detail.status === "APPROVED" ? "승인됨" : "거절됨"}</strong></div>
      <button className="admin-link-button" type="button" onClick={() => void openDetail({ kind: "user", id: detail.user.id, title: detail.user.nickname })}>요청 사용자 {detail.user.nickname}</button>
      {detail.reviewed_by_admin ? <div className="admin-kv"><span>처리 관리자</span><strong>{detail.reviewed_by_admin.nickname}</strong></div> : null}
    </div>
  );
}

function TargetPreview({ targetType, targetId, detail, openDetail }: { targetType: string; targetId: number; detail: any; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  const target = targetType === "USER" ? { kind: "user" as DetailKind, id: targetId, title: detail.user?.nickname || "회원" } :
    targetType === "ITEM" ? { kind: "item" as DetailKind, id: targetId, title: detail.title || "상품" } :
    targetType === "COMMUNITY_POST" ? { kind: "post" as DetailKind, id: targetId, title: detail.title || "게시글" } :
    targetType === "COMMUNITY_COMMENT" ? { kind: "comment" as DetailKind, id: targetId, title: "댓글" } :
    targetType === "CHAT_ROOM" ? { kind: "chat" as DetailKind, id: targetId, title: detail.item?.title || "채팅방" } : null;
  return (
    <div className="admin-target-preview">
      <strong>신고 대상</strong>
      <span>{detail.title || detail.user?.nickname || detail.content || detail.item?.title || targetType}</span>
      {target ? <button className="button subtle" type="button" onClick={() => void openDetail(target)}>대상 열기</button> : null}
    </div>
  );
}

function ReportList({ reports, openDetail }: { reports: any[]; openDetail: (target: NonNullable<SelectedDetail>) => Promise<void> }) {
  return <MiniList title="신고 내역" items={reports || []} render={(report: any) => (
    <button type="button" onClick={() => void openDetail({ kind: "report", id: report.id, title: report.reason })}>{report.reason} · {statusText(report.status)}</button>
  )} />;
}

function MiniList({ title, items, render }: { title: string; items: any[]; render: (item: any) => ReactNode }) {
  return (
    <div className="admin-mini-section">
      <strong>{title}</strong>
      <div className="admin-mini-list">
        {items?.length ? items.map((item) => <div key={item.id}>{render(item)}</div>) : <span className="muted">없습니다.</span>}
      </div>
    </div>
  );
}

function renderControls(props: {
  selected: NonNullable<SelectedDetail>;
  detail: any;
  reason: string;
  setReason: (value: string) => void;
  userStatus: string;
  setUserStatus: (value: string) => void;
  itemStatus: string;
  setItemStatus: (value: string) => void;
  walletAmount: string;
  setWalletAmount: (value: string) => void;
  walletReason: string;
  setWalletReason: (value: string) => void;
  depositDecisionReason: string;
  setDepositDecisionReason: (value: string) => void;
  reportStatus: string;
  setReportStatus: (value: string) => void;
  reportAction: string;
  setReportAction: (value: string) => void;
  handleUserStatus: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleItemStatus: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleWalletAdjust: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleReportUpdate: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  handleDepositDecision: (action: "approve" | "reject") => Promise<void>;
  handleModeration: (path: string, message: string) => Promise<void>;
  handleDeleteChatRoom: () => Promise<void>;
}) {
  const reasonInput = <input value={props.reason} onChange={(event) => props.setReason(event.target.value)} placeholder="조치 사유" />;
  const reportActionOptions: Record<string, Array<[string, string]>> = {
    ITEM: [["ITEM_HIDDEN", "상품 숨김"], ["ITEM_DELETED", "상품 삭제"]],
    USER: [["USER_SUSPENDED", "사용자 정지"], ["USER_DELETED", "사용자 삭제"]],
    COMMUNITY_POST: [["COMMUNITY_POST_HIDDEN", "게시글 숨김"]],
    COMMUNITY_COMMENT: [["COMMUNITY_COMMENT_HIDDEN", "댓글 숨김"]],
    CHAT_ROOM: [["CHAT_ROOM_DELETED", "채팅방 삭제"]],
    MESSAGE: [["MESSAGE_DELETED", "메시지 삭제"]],
  };
  if (props.selected.kind === "user") {
    return (
      <div className="admin-control-box">
        <form className="admin-control-form" onSubmit={props.handleUserStatus}>
          <select value={props.userStatus} onChange={(event) => props.setUserStatus(event.target.value)}>
            <option value="ACTIVE">정상</option>
            <option value="SUSPENDED">정지</option>
            <option value="DELETED">삭제</option>
          </select>
          {reasonInput}
          <button className="button primary" type="submit">회원 상태 변경</button>
        </form>
        <form className="admin-control-form" onSubmit={props.handleWalletAdjust}>
          <input inputMode="numeric" value={props.walletAmount} onChange={(event) => props.setWalletAmount(event.target.value)} placeholder="잔액 조정 금액" />
          <input value={props.walletReason} onChange={(event) => props.setWalletReason(event.target.value)} placeholder="지갑 조정 사유" />
          <button className="button subtle" type="submit">지갑 조정</button>
        </form>
      </div>
    );
  }
  if (props.selected.kind === "item") {
    return (
      <form className="admin-control-form admin-control-box" onSubmit={props.handleItemStatus}>
        <select value={props.itemStatus} onChange={(event) => props.setItemStatus(event.target.value)}>
          <option value="ON_SALE">판매중</option>
          <option value="RESERVED">예약중</option>
          <option value="SOLD">거래완료</option>
          <option value="HIDDEN">숨김</option>
        </select>
        {reasonInput}
        <button className="button primary" type="submit">상품 상태 변경</button>
      </form>
    );
  }
  if (props.selected.kind === "post") {
    return <div className="admin-control-box">{reasonInput}<button className="button primary" type="button" onClick={() => void props.handleModeration(`/api/v1/admin/community/posts/${props.selected.id}/hide`, "게시글 상태가 변경되었습니다.")}>{props.detail.deleted_at ? "게시글 복구" : "게시글 숨기기"}</button></div>;
  }
  if (props.selected.kind === "comment") {
    return <div className="admin-control-box">{reasonInput}<button className="button primary" type="button" onClick={() => void props.handleModeration(`/api/v1/admin/community/comments/${props.selected.id}/hide`, "댓글 상태가 변경되었습니다.")}>{props.detail.deleted_at ? "댓글 복구" : "댓글 숨기기"}</button></div>;
  }
  if (props.selected.kind === "chat") {
    return <div className="admin-control-box"><button className="button danger" type="button" onClick={() => void props.handleDeleteChatRoom()}>채팅방 삭제</button></div>;
  }
  if (props.selected.kind === "report") {
    return (
      <form className="admin-control-form admin-control-box" onSubmit={props.handleReportUpdate}>
        <select value={props.reportStatus} onChange={(event) => props.setReportStatus(event.target.value)}>
          <option value="RECEIVED">접수</option>
          <option value="REVIEWING">검토중</option>
          <option value="RESOLVED">처리됨</option>
          <option value="REJECTED">반려</option>
        </select>
        <select value={props.reportAction} onChange={(event) => props.setReportAction(event.target.value)}>
          <option value="NONE">조치 없음</option>
          {(reportActionOptions[props.detail.target_type] || []).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
          <option value="REPORT_REJECTED">신고 반려</option>
        </select>
        {reasonInput}
        <button className="button primary" type="submit">신고 처리</button>
      </form>
    );
  }
  if (props.selected.kind === "depositRequest") {
    return (
      <div className="admin-control-box">
        <input value={props.depositDecisionReason} onChange={(event) => props.setDepositDecisionReason(event.target.value)} placeholder="처리 메모" />
        {props.detail.status === "PENDING" ? (
          <>
            <button className="button primary" type="button" onClick={() => void props.handleDepositDecision("approve")}>충전 승인</button>
            <button className="button subtle" type="button" onClick={() => void props.handleDepositDecision("reject")}>충전 거절</button>
          </>
        ) : (
          <div className="muted">이미 처리된 요청입니다.</div>
        )}
      </div>
    );
  }
  return null;
}

export default function AdminPage() {
  return (
    <AuthGuard>
      <AdminContent />
    </AuthGuard>
  );
}
