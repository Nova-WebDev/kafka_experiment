export interface BrokerState {
  broker_id: number;
  host: string;
  reachable: boolean;
  in_metadata: boolean;
  is_controller: boolean;
  leader_count: number;
}

export interface PartitionState {
  partition: number;
  leader: number | null;
  replicas: number[];
  isr: number[];
}

export interface ClusterSnapshot {
  topic: string;
  brokers: BrokerState[];
  partitions: PartitionState[];
  controller_id: number | null;
  metadata_available: boolean;
  reachable_brokers: number;
  quorum_voters: number;
  quorum_ok: boolean;
  writes_ok: boolean;
  min_insync_replicas: number;
  taken_at: string;
}

interface BrokerChange {
  broker_id: number;
}

interface ControllerChanged {
  previous_controller_id: number | null;
  controller_id: number | null;
}

interface LeaderChanged {
  partition: number;
  previous_leader: number | null;
  leader: number | null;
}

interface WritesBlocked {
  blocked_partitions: number[];
}

interface ConnectionRetry {
  source: string;
  attempt: number;
  delay_seconds: number;
  error: string;
}

interface ConnectionRestored {
  source: string;
  failed_attempts: number;
}

type SendSource = "manual" | "auto";

interface MessageSent {
  source: SendSource;
  key: string | null;
  value: string;
  partition: number;
  offset: number;
  latency_ms: number;
}

interface MessageFailed {
  source: SendSource;
  key: string | null;
  value: string;
  error: string;
  latency_ms: number;
}

export interface AutoProducerStatus {
  running: boolean;
  rate_per_sec: number;
}

export type ConsumerStatus = "running" | "paused" | "reconnecting" | "stopped";

export interface PartitionProgress {
  partition: number;
  position: number | null;
  committed: number | null;
  high_watermark: number | null;
  lag: number | null;
}

export interface ConsumerState {
  consumer_id: string;
  group_id: string;
  status: ConsumerStatus;
  delay_ms: number;
  partitions: PartitionProgress[];
}

interface ConsumerCreated {
  consumer_id: string;
  group_id: string;
  joined_existing_group: boolean;
  state: ConsumerState;
}

interface ConsumerRemoved {
  consumer_id: string;
  group_id: string;
}

interface ConsumedMessage {
  consumer_id: string;
  partition: number;
  offset: number;
  key: string | null;
  value: string;
  timestamp_ms: number;
  replayed: boolean;
}

interface OffsetCommitted {
  consumer_id: string;
  progress: PartitionProgress;
}

interface EventPayloads {
  "cluster.snapshot": ClusterSnapshot;
  "broker.down": BrokerChange;
  "broker.up": BrokerChange;
  "controller.changed": ControllerChanged;
  "leader.changed": LeaderChanged;
  "writes.blocked": WritesBlocked;
  "writes.restored": Record<string, never>;
  "connection.retry": ConnectionRetry;
  "connection.restored": ConnectionRestored;
  "producer.sent": MessageSent;
  "producer.failed": MessageFailed;
  "producer.auto": AutoProducerStatus;
  "consumer.created": ConsumerCreated;
  "consumer.removed": ConsumerRemoved;
  "consumer.state": ConsumerState;
  "consumer.message": ConsumedMessage;
  "consumer.offset": OffsetCommitted;
}

type EventType = keyof EventPayloads;

export type ServerEvent = {
  [K in EventType]: { id: string; type: K; at: string; payload: EventPayloads[K] };
}[EventType];

export type SendEvent = Extract<ServerEvent, { type: "producer.sent" | "producer.failed" }>;

export type ConsumedMessageEvent = Extract<ServerEvent, { type: "consumer.message" }>;

export type ToastEvent = Extract<
  ServerEvent,
  { type: "broker.down" | "broker.up" | "leader.changed" | "controller.changed" | "writes.blocked" | "writes.restored" }
>;

export interface ConsumerOverview {
  state: ConsumerState;
  messages: ConsumedMessageEvent[];
}

export interface PendingReconnect {
  source: string;
  attempt: number;
  deadline: number;
}

export const EVENT_TYPES: EventType[] = [
  "cluster.snapshot",
  "broker.down",
  "broker.up",
  "controller.changed",
  "leader.changed",
  "writes.blocked",
  "writes.restored",
  "connection.retry",
  "connection.restored",
  "producer.sent",
  "producer.failed",
  "producer.auto",
  "consumer.created",
  "consumer.removed",
  "consumer.state",
  "consumer.message",
  "consumer.offset",
];
