import { faCircleCheck, faCircleXmark, faCrown, faServer } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Pill } from "../../base/Pill";
import type { Tone } from "../../base/tone";
import type { ClusterSnapshot } from "../../share/types";

function brokersTone(snapshot: ClusterSnapshot): Tone {
  if (!snapshot.quorum_ok) {
    return "danger";
  }
  return snapshot.reachable_brokers === snapshot.brokers.length ? "ok" : "warn";
}

function HealthPill({ label, healthy }: { label: string; healthy: boolean }) {
  return (
    <Pill tone={healthy ? "ok" : "danger"}>
      <FontAwesomeIcon icon={healthy ? faCircleCheck : faCircleXmark} />
      {label}
    </Pill>
  );
}

export function ClusterPills({ snapshot }: { snapshot: ClusterSnapshot }) {
  return (
    <>
      <Pill tone={brokersTone(snapshot)} title="Reachable brokers">
        <FontAwesomeIcon icon={faServer} />
        Brokers
        <span className="numeric font-semibold">
          {snapshot.reachable_brokers}/{snapshot.brokers.length}
        </span>
      </Pill>
      <HealthPill label="Quorum" healthy={snapshot.quorum_ok} />
      <HealthPill label="Writes" healthy={snapshot.writes_ok} />
      <Pill tone={snapshot.controller_id === null ? "danger" : "accent"} title="Active KRaft controller">
        <FontAwesomeIcon icon={faCrown} />
        Controller
        <span className="numeric font-semibold">
          {snapshot.controller_id === null ? "—" : `#${snapshot.controller_id}`}
        </span>
      </Pill>
    </>
  );
}
