import { BrokersRow } from "./modules/cluster/BrokersRow";
import { PartitionsPanel } from "./modules/cluster/PartitionsPanel";
import { ConsumersPanel } from "./modules/consumers/ConsumersPanel";
import { Header } from "./modules/header/Header";
import { ProducerPanel } from "./modules/producer/ProducerPanel";
import { ToastStack } from "./modules/toasts/ToastStack";
import { StoreProvider } from "./share/store";

export function App() {
  return (
    <StoreProvider>
      <div className="flex h-full flex-col">
        <Header />
        <main className="flex min-h-0 flex-1 flex-col gap-3 p-3">
          <BrokersRow />
          <div className="grid min-h-0 flex-1 grid-cols-[600px_minmax(0,1fr)] gap-3">
            <div className="flex min-h-0 flex-col gap-3">
              <PartitionsPanel />
              <ProducerPanel />
            </div>
            <ConsumersPanel />
          </div>
        </main>
        <ToastStack />
      </div>
    </StoreProvider>
  );
}
