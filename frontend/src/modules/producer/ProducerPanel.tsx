import { Panel } from "../../base/Panel";
import { AutoProducerControl } from "./AutoProducerControl";
import { RecentSends } from "./RecentSends";
import { SendForm } from "./SendForm";

export function ProducerPanel() {
  return (
    <Panel title="Producer" className="min-h-0 flex-1" bodyClassName="flex flex-col">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <SendForm />
        <span className="h-6 w-px shrink-0 bg-border" />
        <AutoProducerControl />
      </div>
      <RecentSends />
    </Panel>
  );
}
