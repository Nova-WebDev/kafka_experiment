import { Panel } from "../../base/Panel";
import { useStore } from "../../share/store";
import { AddConsumerControl } from "./AddConsumerControl";
import { ConsumerCard } from "./ConsumerCard";

function compareConsumerIds(first: string, second: string): number {
  return first.length - second.length || first.localeCompare(second);
}

export function ConsumersPanel() {
  const { consumers } = useStore();
  const ordered = Object.values(consumers).sort((a, b) =>
    compareConsumerIds(a.state.consumer_id, b.state.consumer_id),
  );
  const groupIds = [...new Set(ordered.map((consumer) => consumer.state.group_id))];

  return (
    <Panel
      title="Consumers"
      actions={<AddConsumerControl groupIds={groupIds} />}
      className="min-h-0"
      bodyClassName="overflow-y-auto"
    >
      <div className="grid grid-cols-[repeat(auto-fill,minmax(380px,1fr))] content-start gap-3 p-3">
        {ordered.map((consumer) => (
          <ConsumerCard key={consumer.state.consumer_id} consumer={consumer} />
        ))}
      </div>
    </Panel>
  );
}
