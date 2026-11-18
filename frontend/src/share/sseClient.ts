import { EVENT_TYPES, type ConsumerOverview, type SendEvent, type ServerEvent } from "./types";

const SEND_HISTORY_EVENT = "producer.history";
const CONSUMERS_SNAPSHOT_EVENT = "consumers.snapshot";

interface EventStreamHandlers {
  onOpen: () => void;
  onDisconnect: () => void;
  onEvent: (event: ServerEvent) => void;
  onSendHistory: (sends: SendEvent[]) => void;
  onConsumersSnapshot: (consumers: ConsumerOverview[]) => void;
}

function parse<T>(message: Event): T {
  return JSON.parse((message as MessageEvent<string>).data) as T;
}

export function connectEventStream(url: string, handlers: EventStreamHandlers): () => void {
  const source = new EventSource(url);

  source.onopen = handlers.onOpen;
  source.onerror = handlers.onDisconnect;

  for (const type of EVENT_TYPES) {
    source.addEventListener(type, (message) => handlers.onEvent(parse<ServerEvent>(message)));
  }
  source.addEventListener(SEND_HISTORY_EVENT, (message) =>
    handlers.onSendHistory(parse<{ events: SendEvent[] }>(message).events),
  );
  source.addEventListener(CONSUMERS_SNAPSHOT_EVENT, (message) =>
    handlers.onConsumersSnapshot(parse<{ consumers: ConsumerOverview[] }>(message).consumers),
  );

  return () => source.close();
}
