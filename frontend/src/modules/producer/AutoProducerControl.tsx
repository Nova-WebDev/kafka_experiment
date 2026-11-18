import { faBolt, faBoxOpen } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { Button } from "../../base/Button";
import { Switch } from "../../base/Switch";
import { TextInput } from "../../base/TextInput";
import { apiClient } from "../../share/apiClient";
import { AUTO_PRODUCER_RATE, isValidRate } from "../../share/limits";
import { useStore } from "../../share/store";
import { usePendingAction } from "../../share/usePendingAction";

export function AutoProducerControl() {
  const { autoProducer } = useStore();
  const [rate, setRate] = useState(String(AUTO_PRODUCER_RATE.initial));
  const [busy, run] = usePendingAction();

  const parsedRate = Number(rate);
  const rateValid = isValidRate(parsedRate);

  const toggle = (enabled: boolean) =>
    run(() => (enabled ? apiClient.startAutoProducer(parsedRate) : apiClient.stopAutoProducer()));

  const applyRate = () => {
    if (autoProducer.running && rateValid && parsedRate !== autoProducer.rate_per_sec) {
      void run(() => apiClient.startAutoProducer(parsedRate));
    }
  };

  return (
    <div className="flex shrink-0 items-center gap-2">
      <Button icon={faBoxOpen} onClick={() => run(apiClient.sendOrder)} title="Send a generated order">
        Order
      </Button>
      <FontAwesomeIcon
        icon={faBolt}
        title="Auto-producer"
        className={`ml-1 text-[13px] transition-colors duration-200 ${autoProducer.running ? "text-accent" : "text-muted"}`}
      />
      <Switch
        checked={autoProducer.running}
        label={autoProducer.running ? "Stop auto-producer" : "Start auto-producer"}
        disabled={busy || (!autoProducer.running && !rateValid)}
        onChange={toggle}
      />
      <TextInput
        compact
        type="number"
        min={AUTO_PRODUCER_RATE.min}
        max={AUTO_PRODUCER_RATE.max}
        step={AUTO_PRODUCER_RATE.step}
        value={rate}
        onChange={(event) => setRate(event.target.value)}
        onBlur={applyRate}
        onKeyDown={(event) => event.key === "Enter" && applyRate()}
        aria-label="Messages per second"
        className="numeric w-12 text-right"
      />
      <span className="text-[13px] text-muted">/s</span>
    </div>
  );
}
