export type CallRecord = {
  id: string;
  agent: "inbound" | "outbound";
  startedAt: string;
  endedAt?: string;
  durationSec?: number;
  status: "completed" | "failed" | "in-progress";
  summary?: string;
};

const STORAGE_KEY = "inbound_agent_call_history";
const HISTORY_EVENT = "inbound_agent_call_history_updated";

function notifyHistoryChange() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(HISTORY_EVENT));
  }
}

export function subscribeCallHistory(listener: () => void) {
  if (typeof window === "undefined") return () => {};
  const onStorage = () => listener();
  const onCustom = () => listener();
  window.addEventListener("storage", onStorage);
  window.addEventListener(HISTORY_EVENT, onCustom);
  return () => {
    window.removeEventListener("storage", onStorage);
    window.removeEventListener(HISTORY_EVENT, onCustom);
  };
}

export function getCallHistory(): CallRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as CallRecord[]) : [];
  } catch {
    return [];
  }
}

export function saveCallHistory(records: CallRecord[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(0, 100)));
  notifyHistoryChange();
}

export function addCallRecord(record: CallRecord) {
  const history = getCallHistory();
  saveCallHistory([record, ...history]);
}

export function updateCallRecord(id: string, patch: Partial<CallRecord>) {
  const history = getCallHistory();
  saveCallHistory(
    history.map((r) => (r.id === id ? { ...r, ...patch } : r)),
  );
}

export function formatDuration(sec: number) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function formatCallTime(iso: string) {
  return new Date(iso).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
