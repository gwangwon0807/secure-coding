"use client";

import { useMemo, useState } from "react";

import { apiFetch } from "@/lib/api";

type ReportTargetType = "ITEM" | "USER" | "COMMUNITY_POST" | "COMMUNITY_COMMENT";

type ReportOption = {
  label: string;
  targetType: ReportTargetType;
  targetId: number;
};

type ReportFormProps = {
  buttonLabel?: string;
  options: ReportOption[];
};

const REPORT_OPTIONS = [
  { value: "SCAM_SUSPECTED", label: "사기 의심" },
  { value: "PROHIBITED_ITEM", label: "금지 품목" },
  { value: "FALSE_INFORMATION", label: "허위 정보" },
  { value: "ABUSIVE_LANGUAGE", label: "욕설/비방" },
  { value: "SPAM", label: "스팸/광고" },
  { value: "INAPPROPRIATE_CONTENT", label: "부적절한 내용" },
  { value: "ETC", label: "기타" },
];

export function ReportForm({ buttonLabel = "신고하기", options }: ReportFormProps) {
  const normalizedOptions = useMemo(() => options.filter((option) => option.targetId > 0), [options]);
  const [open, setOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [reason, setReason] = useState(REPORT_OPTIONS[0].value);
  const [detail, setDetail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const selectedOption = normalizedOptions[selectedIndex];

  async function handleSubmit() {
    if (!selectedOption) return;
    setError("");
    setMessage("");
    setIsSubmitting(true);
    try {
      await apiFetch("/api/v1/reports", {
        method: "POST",
        body: JSON.stringify({
          target_type: selectedOption.targetType,
          target_id: selectedOption.targetId,
          reason,
          detail: detail || null,
        }),
      });
      setMessage("신고가 접수되었습니다.");
      setOpen(false);
      setDetail("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "신고 접수에 실패했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (normalizedOptions.length === 0) return null;

  return (
    <div className="report-box">
      <button className="button subtle danger" type="button" onClick={() => setOpen((prev) => !prev)}>
        {buttonLabel}
      </button>
      {open ? (
        <div className="report-panel">
          {normalizedOptions.length > 1 ? (
            <div className="report-target-list">
              {normalizedOptions.map((option, index) => (
                <button
                  key={`${option.targetType}-${option.targetId}`}
                  className={`report-target-chip ${selectedIndex === index ? "active" : ""}`}
                  type="button"
                  onClick={() => setSelectedIndex(index)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          ) : (
            <div className="muted">{normalizedOptions[0].label}</div>
          )}
          <select value={reason} onChange={(event) => setReason(event.target.value)}>
            {REPORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <textarea value={detail} onChange={(event) => setDetail(event.target.value)} placeholder="신고 사유를 자세히 입력해 주세요." />
          {error ? <div className="error-box">{error}</div> : null}
          {message ? <div className="success-box">{message}</div> : null}
          <button className="button primary" disabled={isSubmitting} type="button" onClick={() => void handleSubmit()}>
            {isSubmitting ? "신고 중..." : "신고 접수"}
          </button>
        </div>
      ) : null}
      {!open && message ? <div className="success-box">{message}</div> : null}
    </div>
  );
}
