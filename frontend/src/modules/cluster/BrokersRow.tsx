import { useStore } from "../../share/store";
import { BrokerCard } from "./BrokerCard";

export function BrokersRow() {
  const { snapshot } = useStore();

  if (!snapshot) {
    return null;
  }

  return (
    <div className="grid shrink-0 grid-cols-5 gap-3">
      {snapshot.brokers.map((broker) => (
        <BrokerCard key={broker.broker_id} broker={broker} metadataAvailable={snapshot.metadata_available} />
      ))}
    </div>
  );
}
