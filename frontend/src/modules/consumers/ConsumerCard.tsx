import { faPause, faPlay, faRotateRight, faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { IconButton } from "../../base/IconButton";
import { Pill } from "../../base/Pill";
import type { Tone } from "../../base/tone";
import { apiClient } from "../../share/apiClient";
import type { ConsumerOverview, ConsumerStatus } from "../../share/types";
import { DelayControl } from "./DelayControl";
import { MessageFeed } from "./MessageFeed";
import { PartitionProgressRow } from "./PartitionProgressRow";

const statusTone: Record<ConsumerStatus, Tone> = {
  running: "ok",
  paused: "warn",
  reconnecting: "warn",
  stopped: "neutral",
};

export function ConsumerCard({ consumer }: { consumer: ConsumerOverview }) {
  const { state, messages } = consumer;
  const paused = state.status === "paused";

  return (
    <article className="flex flex-col overflow-hidden rounded-lg border border-border bg-surface-raised">
      <header className="flex items-start gap-3 border-b border-border px-3 py-2.5">
        <span className="numeric flex size-10 shrink-0 items-center justify-center rounded-md border border-accent/35 bg-accent/10 text-lg font-bold text-accent">
          {state.consumer_id}
        </span>
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-[14px] font-semibold">Consumer {state.consumer_id}</span>
            <Pill tone={statusTone[state.status]}>
              {state.status === "reconnecting" && <FontAwesomeIcon icon={faRotateRight} spin />}
              {state.status}
            </Pill>
          </div>
          <div className="flex items-center gap-2">
            <span className="numeric truncate text-[12px] text-muted" title={state.group_id}>
              {state.group_id}
            </span>
            <DelayControl consumerId={state.consumer_id} delayMs={state.delay_ms} />
          </div>
        </div>
        <div className="flex gap-1.5">
          <IconButton
            icon={paused ? faPlay : faPause}
            label={paused ? "Resume" : "Pause"}
            onClick={() =>
              paused ? apiClient.resumeConsumer(state.consumer_id) : apiClient.pauseConsumer(state.consumer_id)
            }
          />
          <IconButton
            icon={faTrashCan}
            label="Remove consumer"
            tone="danger"
            onClick={() => apiClient.removeConsumer(state.consumer_id)}
          />
        </div>
      </header>
      <div className="divide-y divide-border border-b border-border">
        {state.partitions.map((progress) => (
          <PartitionProgressRow key={progress.partition} consumerId={state.consumer_id} progress={progress} />
        ))}
      </div>
      <MessageFeed messages={messages} />
    </article>
  );
}
