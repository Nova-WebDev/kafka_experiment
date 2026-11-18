import { faCircleNodes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { StatusDot } from "../../base/StatusDot";
import { useStore } from "../../share/store";
import type { ClusterSnapshot } from "../../share/types";
import { ClusterPills } from "./ClusterPills";
import { ReconnectStatus } from "./ReconnectStatus";
import { ThemeToggle } from "./ThemeToggle";

function topicSummary(snapshot: ClusterSnapshot): string {
  const replicationFactor = snapshot.partitions[0]?.replicas.length ?? 0;
  return [
    snapshot.topic,
    `${snapshot.partitions.length} partitions`,
    `RF ${replicationFactor}`,
    `min ISR ${snapshot.min_insync_replicas}`,
  ].join(" · ");
}

export function Header() {
  const { snapshot, reconnects, streamConnected } = useStore();

  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-4 border-b border-border/70 bg-background/80 px-5 backdrop-blur-md">
      <span className="flex size-8 items-center justify-center rounded-lg bg-linear-to-br from-accent to-accent-secondary text-on-accent shadow-card">
        <FontAwesomeIcon icon={faCircleNodes} />
      </span>
      <div className="flex flex-col leading-tight">
        <h1 className="text-[15px] font-semibold tracking-tight">Kafka Lab</h1>
        {snapshot && <span className="numeric text-[12px] text-muted">{topicSummary(snapshot)}</span>}
      </div>
      <div className="ml-auto flex items-center gap-2">
        <ReconnectStatus reconnects={Object.values(reconnects)} />
        {snapshot && <ClusterPills snapshot={snapshot} />}
        <span className="mx-1 h-6 w-px bg-border" />
        <span
          className={`flex items-center gap-2 text-[13px] font-medium ${streamConnected ? "text-success" : "text-danger"}`}
        >
          <StatusDot tone={streamConnected ? "ok" : "danger"} pulse={streamConnected} />
          {streamConnected ? "Live" : "Offline"}
        </span>
        <ThemeToggle />
      </div>
    </header>
  );
}
