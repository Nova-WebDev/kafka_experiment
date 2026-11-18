import { Panel } from "../../base/Panel";
import { useStore } from "../../share/store";
import { PartitionRow } from "./PartitionRow";

export function PartitionsPanel() {
  const { snapshot } = useStore();

  if (!snapshot) {
    return null;
  }

  const brokerIds = snapshot.brokers.map((broker) => broker.broker_id);
  const reachable = new Set(snapshot.brokers.filter((broker) => broker.reachable).map((broker) => broker.broker_id));

  return (
    <Panel title="Partitions" className="shrink-0" bodyClassName={snapshot.metadata_available ? "" : "opacity-50"}>
      <ul className="divide-y divide-border">
        {snapshot.partitions.map((partition) => (
          <PartitionRow
            key={partition.partition}
            partition={partition}
            brokerIds={brokerIds}
            reachable={reachable}
            minInsyncReplicas={snapshot.min_insync_replicas}
          />
        ))}
      </ul>
    </Panel>
  );
}
