import type { AutoProducerStatus, ConsumerState } from "./types";

const API_BASE = "/api";
const HTTP_BAD_GATEWAY = 502;
const HTTP_NO_CONTENT = 204;

interface SendResult {
  status: "sent" | "failed";
  key: string | null;
  partition: number | null;
  offset: number | null;
  latency_ms: number;
  error: string | null;
}

type HttpMethod = "POST" | "PATCH" | "DELETE";

async function request<T>(method: HttpMethod, path: string, body?: unknown, acceptedStatuses: number[] = []): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok && !acceptedStatuses.includes(response.status)) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  if (response.status === HTTP_NO_CONTENT) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

const consumerPath = (consumerId: string) => `/consumers/${encodeURIComponent(consumerId)}`;

export const apiClient = {
  eventsUrl: `${API_BASE}/events`,
  retryNow: () => request<{ skipped_waits: number }>("POST", "/connection/retry-now"),
  sendMessage: (key: string | null, value: string) =>
    request<SendResult>("POST", "/producer/messages", { key, value }, [HTTP_BAD_GATEWAY]),
  sendOrder: () => request<SendResult>("POST", "/producer/orders", undefined, [HTTP_BAD_GATEWAY]),
  startAutoProducer: (ratePerSec: number) =>
    request<AutoProducerStatus>("POST", "/producer/auto/start", { rate_per_sec: ratePerSec }),
  stopAutoProducer: () => request<AutoProducerStatus>("POST", "/producer/auto/stop"),
  createConsumer: (groupId: string | null, delayMs: number) =>
    request<ConsumerState>("POST", "/consumers", { group_id: groupId, delay_ms: delayMs }),
  removeConsumer: (consumerId: string) => request<void>("DELETE", consumerPath(consumerId)),
  pauseConsumer: (consumerId: string) => request<unknown>("POST", `${consumerPath(consumerId)}/pause`),
  resumeConsumer: (consumerId: string) => request<unknown>("POST", `${consumerPath(consumerId)}/resume`),
  setConsumerDelay: (consumerId: string, delayMs: number) =>
    request<unknown>("PATCH", consumerPath(consumerId), { delay_ms: delayMs }),
  seekConsumer: (consumerId: string, partition: number, offset: number) =>
    request<unknown>("POST", `${consumerPath(consumerId)}/seek`, { partition, offset }),
};
