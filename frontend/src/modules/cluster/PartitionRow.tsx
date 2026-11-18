import { faLock, faLockOpen } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { toneText, type Tone } from "../../base/tone";
import type { PartitionState } from "../../share/types";
import { ReplicaSquare, type ReplicaRole } from "./ReplicaSquare";

interface PartitionRowProps {
  partition: PartitionState;
  brokerIds: number[];
  reachable: Set<number>;
  minInsyncReplicas: number;
}

function replicaRole(partition: PartitionState, brokerId: number): ReplicaRole {
  if (!partition.replicas.includes(brokerId)) {
    return "none";
  }
  if (partition.leader === brokerId) {
    return "leader";
  }
  return partition.isr.includes(brokerId) ? "in-sync" : "out-of-sync";
}

function isrTone(liveIsr: number, minInsyncReplicas: number): Tone {
  if (liveIsr < minInsyncReplicas) {
    return "danger";
  }
  return liveIsr === minInsyncReplicas ? "warn" : "ok";
}

export function PartitionRow({ partition, brokerIds, reachable, minInsyncReplicas }: PartitionRowProps) {
  const liveIsr = partition.isr.filter((brokerId) => reachable.has(brokerId)).length;
  const leaderAlive = partition.leader !== null && reachable.has(partition.leader);
  const writable = leaderAlive && liveIsr >= minInsyncReplicas;

  return (
    <li className="flex h-12 items-center gap-4 px-4">
      <span className="numeric w-8 text-[15px] font-bold">P{partition.partition}</span>
      <div className="flex gap-1.5">
        {brokerIds.map((brokerId) => (
          <ReplicaSquare
            key={brokerId}
            brokerId={brokerId}
            role={replicaRole(partition, brokerId)}
            alive={reachable.has(brokerId)}
          />
        ))}
      </div>
      <span className="ml-auto text-[13px] text-muted">
        ISR{" "}
        <span className={`numeric text-[15px] font-semibold ${toneText[isrTone(liveIsr, minInsyncReplicas)]}`}>
          {liveIsr}/{partition.replicas.length}
        </span>
      </span>
      <span
        title={writable ? "Writable" : "Writes blocked"}
        className={`flex size-7 items-center justify-center rounded-md border transition-colors duration-200 ${writable ? "border-success/35 bg-success/10 text-success" : "border-danger/40 bg-danger/10 text-danger"}`}
      >
        <FontAwesomeIcon icon={writable ? faLockOpen : faLock} className="text-[12px]" />
      </span>
    </li>
  );
}
