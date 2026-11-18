import { createContext, useContext, useEffect, useMemo, useReducer, type Dispatch, type ReactNode } from "react";
import { apiClient } from "./apiClient";
import { connectEventStream } from "./sseClient";
import type {
  AutoProducerStatus,
  ClusterSnapshot,
  ConsumedMessageEvent,
  ConsumerOverview,
  ConsumerState,
  PartitionProgress,
  PendingReconnect,
  SendEvent,
  ServerEvent,
  ToastEvent,
} from "./types";

const SENDS_LIMIT = 30;
const CONSUMER_MESSAGES_LIMIT = 10;
const TOASTS_LIMIT = 3;

interface AppState {
  streamConnected: boolean;
  snapshot: ClusterSnapshot | null;
  sends: SendEvent[];
  autoProducer: AutoProducerStatus;
  consumers: Record<string, ConsumerOverview>;
  reconnects: Record<string, PendingReconnect>;
  toasts: ToastEvent[];
}

type Action =
  | { type: "stream.opened" }
  | { type: "stream.lost" }
  | { type: "event"; event: ServerEvent }
  | { type: "sends.history"; sends: SendEvent[] }
  | { type: "consumers.snapshot"; consumers: ConsumerOverview[] }
  | { type: "toast.dismissed"; id: string };

const initialState: AppState = {
  streamConnected: false,
  snapshot: null,
  sends: [],
  autoProducer: { running: false, rate_per_sec: 0 },
  consumers: {},
  reconnects: {},
  toasts: [],
};

function mergeNewestFirst<T extends { id: string; at: string }>(current: T[], incoming: T[], limit: number): T[] {
  const known = new Set(current.map((event) => event.id));
  const fresh = incoming.filter((event) => !known.has(event.id));
  if (fresh.length === 0) {
    return current;
  }
  return [...fresh, ...current].sort((a, b) => b.at.localeCompare(a.at)).slice(0, limit);
}

function without<T>(record: Record<string, T>, key: string): Record<string, T> {
  const { [key]: _removed, ...rest } = record;
  return rest;
}

function withConsumerState(consumers: Record<string, ConsumerOverview>, consumerState: ConsumerState) {
  const existing = consumers[consumerState.consumer_id];
  return { ...consumers, [consumerState.consumer_id]: { state: consumerState, messages: existing?.messages ?? [] } };
}

function withPartitionProgress(
  consumers: Record<string, ConsumerOverview>,
  consumerId: string,
  progress: PartitionProgress,
) {
  const existing = consumers[consumerId];
  if (!existing) {
    return consumers;
  }
  const partitions = existing.state.partitions.map((current) =>
    current.partition === progress.partition ? progress : current,
  );
  return { ...consumers, [consumerId]: { ...existing, state: { ...existing.state, partitions } } };
}

function withConsumedMessage(consumers: Record<string, ConsumerOverview>, message: ConsumedMessageEvent) {
  const existing = consumers[message.payload.consumer_id];
  if (!existing) {
    return consumers;
  }
  const messages = mergeNewestFirst(existing.messages, [message], CONSUMER_MESSAGES_LIMIT);
  return { ...consumers, [message.payload.consumer_id]: { ...existing, messages } };
}

function withToast(toasts: ToastEvent[], toast: ToastEvent): ToastEvent[] {
  return [...toasts, toast].slice(-TOASTS_LIMIT);
}

function applyEvent(state: AppState, event: ServerEvent): AppState {
  switch (event.type) {
    case "cluster.snapshot":
      return { ...state, snapshot: event.payload };
    case "broker.down":
    case "broker.up":
    case "leader.changed":
    case "controller.changed":
    case "writes.blocked":
    case "writes.restored":
      return { ...state, toasts: withToast(state.toasts, event) };
    case "connection.retry":
      return {
        ...state,
        reconnects: {
          ...state.reconnects,
          [event.payload.source]: {
            source: event.payload.source,
            attempt: event.payload.attempt,
            deadline: Date.now() + event.payload.delay_seconds * 1000,
          },
        },
      };
    case "connection.restored":
      return { ...state, reconnects: without(state.reconnects, event.payload.source) };
    case "producer.auto":
      return { ...state, autoProducer: event.payload };
    case "producer.sent":
    case "producer.failed":
      return { ...state, sends: mergeNewestFirst(state.sends, [event], SENDS_LIMIT) };
    case "consumer.created":
      return { ...state, consumers: withConsumerState(state.consumers, event.payload.state) };
    case "consumer.removed":
      return { ...state, consumers: without(state.consumers, event.payload.consumer_id) };
    case "consumer.state":
      return { ...state, consumers: withConsumerState(state.consumers, event.payload) };
    case "consumer.offset":
      return {
        ...state,
        consumers: withPartitionProgress(state.consumers, event.payload.consumer_id, event.payload.progress),
      };
    case "consumer.message":
      return { ...state, consumers: withConsumedMessage(state.consumers, event) };
  }
}

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "stream.opened":
      return { ...state, streamConnected: true, reconnects: {} };
    case "stream.lost":
      return { ...state, streamConnected: false };
    case "event":
      return applyEvent(state, action.event);
    case "sends.history":
      return { ...state, sends: mergeNewestFirst(state.sends, action.sends, SENDS_LIMIT) };
    case "consumers.snapshot":
      return {
        ...state,
        consumers: Object.fromEntries(
          action.consumers.map((consumer) => [
            consumer.state.consumer_id,
            { state: consumer.state, messages: mergeNewestFirst([], consumer.messages, CONSUMER_MESSAGES_LIMIT) },
          ]),
        ),
      };
    case "toast.dismissed":
      return { ...state, toasts: state.toasts.filter((toast) => toast.id !== action.id) };
  }
}

const StateContext = createContext<AppState>(initialState);
const DispatchContext = createContext<Dispatch<Action>>(() => undefined);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(
    () =>
      connectEventStream(apiClient.eventsUrl, {
        onOpen: () => dispatch({ type: "stream.opened" }),
        onDisconnect: () => dispatch({ type: "stream.lost" }),
        onEvent: (event) => dispatch({ type: "event", event }),
        onSendHistory: (sends) => dispatch({ type: "sends.history", sends }),
        onConsumersSnapshot: (consumers) => dispatch({ type: "consumers.snapshot", consumers }),
      }),
    [],
  );

  return (
    <DispatchContext.Provider value={dispatch}>
      <StateContext.Provider value={state}>{children}</StateContext.Provider>
    </DispatchContext.Provider>
  );
}

export function useStore(): AppState {
  return useContext(StateContext);
}

export function useToastDismissal(): (id: string) => void {
  const dispatch = useContext(DispatchContext);
  return useMemo(() => (id: string) => dispatch({ type: "toast.dismissed", id }), [dispatch]);
}
