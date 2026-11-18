import { faCrown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { StatusDot } from "../../base/StatusDot";
import type { Tone } from "../../base/tone";
import type { BrokerState } from "../../share/types";

function brokerTone(broker: BrokerState, metadataAvailable: boolean): Tone {
  if (!broker.reachable) {
    return "danger";
  }
  return metadataAvailable && !broker.in_metadata ? "warn" : "ok";
}

export function BrokerCard({
  broker,
  metadataAvailable,
}: {
  broker: BrokerState;
  metadataAvailable: boolean;
}) {
  const tone = brokerTone(broker, metadataAvailable);
  const down = tone === "danger";

  return (
    <article
      className={`flex h-[72px] flex-col justify-between rounded-xl border  px-4 py-2.5 shadow-card transition-[border-color,opacity] duration-200 ${down ? "border-danger/70 opacity-55 bg-red-200 dark:bg-red-950" : "border-border bg-surface"}`}
    >
      <div className="flex items-center gap-2">
        <StatusDot tone={tone} />
        <span className="text-[14px] font-semibold">
          Broker <span className="numeric">{broker.broker_id}</span>
        </span>
        {broker.is_controller && (
          <span className="ml-auto inline-flex items-center gap-1 rounded-full border border-accent/35 bg-accent/10 px-2 py-0.5 text-[12px] font-medium text-accent">
            <FontAwesomeIcon icon={faCrown} className="text-[10px]" />
            controller
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="numeric text-xl leading-none font-semibold">
          {metadataAvailable ? broker.leader_count : "—"}
        </span>
        <span className="text-[13px] text-muted">
          {broker.leader_count === 1 && metadataAvailable
            ? "leader"
            : "leaders"}
        </span>
      </div>
    </article>
  );
}
